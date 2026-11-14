import logging

from langchain_core.messages import SystemMessage
from langchain_core.messages.utils import count_tokens_approximately

from a2a.server.agent_execution import AgentExecutor as A2AAgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    InternalError,
    Part,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import new_agent_text_message, new_task
from a2a.utils.errors import ServerError

from agent import SampleAgent
from datetime_tool import get_datetime_tool
from load_skill_resources import get_load_skill_resource_tool
from mcp_providers.agw import get_mcp_tools
from prompt_injection_detector import wrap_tool
from opentelemetry import trace
from tools.get_open_purchase_orders import get_open_purchase_orders
from tools.flag_purchase_orders import flag_purchase_orders
from tools.rank_purchase_orders import rank_purchase_orders
from tools.draft_supplier_email import draft_supplier_email

tracer = trace.get_tracer(__name__)

logger = logging.getLogger(__name__)


class AgentExecutor(A2AAgentExecutor):
    def __init__(self):
        self.agent = SampleAgent()
        self.skill_tools = [
            get_datetime_tool(),
            *get_load_skill_resource_tool(),
            get_open_purchase_orders,
            flag_purchase_orders,
            rank_purchase_orders,
            draft_supplier_email,
        ]

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Execute the agent and stream results back via A2A protocol.

        Discovers and loads MCP tools from Agent Gateway before each execution.
        The user token is read from the context var set by JWTContextMiddleware.

        Args:
            context: Request context containing user input and task info
            event_queue: Queue for publishing task status updates

        Raises:
            ServerError: On unrecoverable agent execution errors
        """
        query = context.get_user_input()
        task = context.current_task
        if not task:
            assert context.message is not None, "Cannot create task without a message"
            task = new_task(context.message)
            await event_queue.enqueue_event(task)

        # Load MCP tools — user token is read from context var set by JWTContextMiddleware
        tools = []
        try:
            tools = await get_mcp_tools()
            if not tools:
                logger.warning("No tools returned from Agent Gateway")
        except Exception as e:
            logger.error(f"Failed to load tools from Agent Gateway: {e}")

        tools = [*tools, *self.skill_tools]

        # Wrap all tools with prompt injection scanning for uniform protection
        tools = [wrap_tool(t) for t in tools]

        from agent import get_system_prompt
        _system_prompt = get_system_prompt()
        _msg_tokens = count_tokens_approximately([SystemMessage(content=_system_prompt)])
        _total_tokens = count_tokens_approximately([SystemMessage(content=_system_prompt)], tools=list(tools))
        logger.info(
            "Loaded %d tool(s); token estimate — prompt: %d, tools: %d, total: %d",
            len(tools), _msg_tokens, _total_tokens - _msg_tokens, _total_tokens,
        )

        updater = TaskUpdater(event_queue, task.id, task.context_id)

        try:
            with tracer.start_as_current_span("M5_session"):
                async for item in self.agent.stream(query, task.context_id, tools=tools):
                    is_task_complete = item["is_task_complete"]
                    require_user_input = item["require_user_input"]
                    content = item["content"]

                    if require_user_input:
                        # Agent requests more input
                        await updater.update_status(
                            TaskState.input_required,
                            new_agent_text_message(content, task.context_id, task.id),
                            final=True,
                        )
                        break
                    elif is_task_complete:
                        # Completed: add artifact and complete task
                        logger.info(
                            "M5.achieved: Session completed — read-only constraint maintained throughout"
                        )
                        await updater.add_artifact(
                            [Part(root=TextPart(text=content))], name="agent_result"
                        )
                        await updater.complete()
                        break
                    else:
                        # Working status update
                        await updater.update_status(
                            TaskState.working,
                            new_agent_text_message(content, task.context_id, task.id),
                        )
        except Exception as e:
            logger.exception("Agent execution error")
            raise ServerError(error=InternalError()) from e

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise ServerError(error=UnsupportedOperationError())
