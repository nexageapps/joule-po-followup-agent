# Specification: po-followup-assistant-agent

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [guidelines.md](../guidelines.md) — Universal execution rules
> - [guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Basic Setup

- [ ] Read `product-requirements-document.md` and `intent.md` at the solution root before writing any code
- [ ] Bootstrap agent code in `assets/po-followup-assistant-agent/` using the `sap-agent-bootstrap` skill (invoke from inside `assets/po-followup-assistant-agent/`, use copy commands — do NOT create files manually)
- [ ] Install dependencies: `pip install -r requirements.txt` from `assets/po-followup-assistant-agent/`
- [ ] Validate the agent starts and responds at `/.well-known/agent.json`

---

## Mock PO Data Module

> The agent uses no live APIs. All PO data comes from an internal mock dataset shaped exactly like the SAP S/4HANA `API_PURCHASEORDER_PROCESS_SRV` OData schema (entities: `A_PurchaseOrder`, `A_PurchaseOrderItem`). The mock data layer must be isolated behind a tool interface so a future replacement with a live API call requires only updating that module.

- [ ] Create `assets/po-followup-assistant-agent/app/mock_po_data.py` with an in-memory list of realistic purchase order records. Each record must include at minimum:
  - `PurchaseOrder` (string, e.g. `"4500001234"`)
  - `Supplier` (string, e.g. `"Acme Supplies GmbH"`)
  - `SupplierName` (string)
  - `PurchasingOrganization` (string)
  - `DocumentDate` (ISO date string)
  - `items` (list of dicts), each item containing:
    - `PurchaseOrderItem` (string, e.g. `"00010"`)
    - `Material` (string)
    - `ShortText` (string description)
    - `OrderQuantity` (number)
    - `NetPriceAmount` (float)
    - `NetPriceQuantity` (float)
    - `Currency` (string, e.g. `"EUR"`)
    - `NetAmount` (float — total line value)
    - `ScheduleDeliveryDate` (ISO date string)
    - `ConfirmationDeliveryDate` (ISO date string or null)
    - `OrderAcknowledgmentNumber` (string or null — null = no acknowledgement)
    - `GoodsReceiptStatus` (string: `"OPEN"` or `"RECEIVED"`)
    - `PurchaseOrderQuantity` (float)
- [ ] Include at least 10 realistic mock PO records covering all flag scenarios:
  - At least 2 POs with `ScheduleDeliveryDate` in the past and no GR (overdue + missing GR)
  - At least 2 POs with `ScheduleDeliveryDate` within 3 calendar days from today
  - At least 2 POs with `OrderAcknowledgmentNumber` as null (missing ACK)
  - At least 2 POs that are fully on-track (no flags) — to verify the agent does not flag clean POs
  - Mix of different suppliers and varying `NetAmount` values
- [ ] Use Python's `datetime.date.today()` to compute relative dates dynamically so mock data does not become stale. Never hardcode dates as static strings that will expire.
- [ ] Expose a single function: `def get_open_purchase_orders() -> list[dict]` that returns the full list of mock PO records

---

## Agent Tools

> Each tool below is a standalone Python function decorated with `@tool` (LangChain) and registered in the agent's tool list. Tools are pure read-only — no writes, no sends. All tool functions go in `assets/po-followup-assistant-agent/app/tools/`.

### Tool 1: get_open_purchase_orders

- [ ] Create `assets/po-followup-assistant-agent/app/tools/get_open_purchase_orders.py`
- [ ] The tool calls `mock_po_data.get_open_purchase_orders()` and returns the full list of open PO records as a JSON-serialisable list of dicts
- [ ] Tool description (for the LLM): "Retrieve all open purchase orders from the data source. Returns a list of PO records including header and line item details."
- [ ] No input parameters required

### Tool 2: flag_purchase_orders

- [ ] Create `assets/po-followup-assistant-agent/app/tools/flag_purchase_orders.py`
- [ ] Accept one input: `purchase_orders: list[dict]` — the full list from `get_open_purchase_orders`
- [ ] Apply the four flagging rules to each PO item:
  1. **OVERDUE**: `ScheduleDeliveryDate` < today
  2. **DUE_SOON**: `ScheduleDeliveryDate` >= today AND `ScheduleDeliveryDate` <= today + 3 calendar days
  3. **MISSING_ACK**: `OrderAcknowledgmentNumber` is null or empty string
  4. **MISSING_GR**: `ScheduleDeliveryDate` < today AND `GoodsReceiptStatus` == `"OPEN"`
- [ ] A single PO item may carry multiple flags simultaneously
- [ ] Return only PO items that have at least one flag; each result dict must include the original PO fields plus a `flags` list (e.g. `["OVERDUE", "MISSING_GR"]`)
- [ ] POs with no flags must NOT appear in the output
- [ ] Tool description: "Apply follow-up rules to a list of purchase orders and return only those that require action. Each flagged item includes a 'flags' list explaining why it needs follow-up."

### Tool 3: rank_purchase_orders

- [ ] Create `assets/po-followup-assistant-agent/app/tools/rank_purchase_orders.py`
- [ ] Accept one input: `flagged_purchase_orders: list[dict]` — output from `flag_purchase_orders`
- [ ] Sort the list:
  - Primary sort: days overdue descending (most overdue first). For DUE_SOON items (not yet overdue), days overdue = 0
  - Secondary sort: `NetAmount` descending (highest value first)
- [ ] Add a `days_overdue` field to each result dict (integer, 0 if not yet overdue)
- [ ] Add a `rank` field (1-based integer position in the sorted list)
- [ ] Return the sorted list with `rank` and `days_overdue` fields added
- [ ] Tool description: "Sort flagged purchase orders by urgency (days overdue, descending) and monetary value (net amount, descending). Returns the ranked list with 'rank' and 'days_overdue' fields."

### Tool 4: draft_supplier_email

- [ ] Create `assets/po-followup-assistant-agent/app/tools/draft_supplier_email.py`
- [ ] Accept inputs:
  - `purchase_order_number: str`
  - `purchase_order_item: str`
  - `supplier_name: str`
  - `short_text: str` (item description)
  - `net_amount: float`
  - `currency: str`
  - `schedule_delivery_date: str`
  - `days_overdue: int`
  - `flags: list[str]`
- [ ] Do NOT call an LLM inside the tool function. The tool constructs a structured dict with all PO context fields and returns it. The agent's LLM uses this structured dict to generate the email text in its response.
- [ ] Return a dict with:
  - `po_number`, `item`, `supplier`, `description`, `amount`, `currency`, `delivery_date`, `days_overdue`, `flags`
  - `draft_instruction`: a string such as `"Draft a short, polite email to the supplier requesting an update on this purchase order. Reference the PO number, item, delivery date, and the specific issue(s) listed in flags. Tone: professional and collaborative, not threatening. Mark this as a DRAFT for buyer review — do not send."`
- [ ] Tool description: "Prepare the context needed to draft a follow-up email for a flagged purchase order. Returns structured PO data and a drafting instruction for the agent to use when composing the email."

---

## System Prompt

- [ ] Open `assets/po-followup-assistant-agent/app/agent.py` and update the `@prompt_section` / `get_system_prompt()` body with the following instructions:

  ```
  You are a read-only purchasing assistant for procurement buyers. 
  You help buyers identify open purchase orders that need follow-up and prepare draft supplier communications.

  ## Your capabilities
  - Retrieve open purchase orders using the get_open_purchase_orders tool
  - Flag POs that need follow-up using the flag_purchase_orders tool
  - Rank flagged POs by urgency and value using the rank_purchase_orders tool
  - Prepare email draft context using the draft_supplier_email tool and then write the draft email text yourself

  ## Rules you must ALWAYS follow
  1. You are STRICTLY READ-ONLY. You MUST NEVER modify, approve, cancel, create, or send any purchase order, document, or message.
  2. If a user asks you to perform any write action (edit a PO, send an email, approve an order), politely decline and explain that you are a read-only assistant.
  3. Never fabricate, guess, or invent PO data. Always call tools to retrieve data.
  4. When presenting flagged POs, always state the reason(s) for each flag explicitly.
  5. Draft emails are always marked as DRAFT and are for buyer review only — make this clear in every drafted email.
  6. When drafting emails, use a professional and collaborative tone. Never use accusatory or threatening language.
  7. If PO data cannot be loaded, report the error clearly. Do not return an empty list silently.

  ## Flag codes and their meaning
  - OVERDUE: Delivery date has passed
  - DUE_SOON: Delivery is due within 3 calendar days
  - MISSING_ACK: Supplier has not sent an order acknowledgement
  - MISSING_GR: Delivery date has passed but no goods receipt has been recorded

  ## Ranking logic
  Flagged POs are ranked by: (1) days overdue descending, then (2) net PO value descending.
  Always present the ranked list in order, explaining the ranking to the buyer.
  ```

- [ ] Verify the system prompt is correctly wired into the agent and returned by `get_system_prompt()`

---

## Runtime Skills

- [ ] Assess whether a runtime skill is needed for email drafting. The email drafting instructions are concise enough to live in the system prompt (no branching logic or reference material required) — do NOT create a runtime skill for email drafting
- [ ] No runtime skills are required for this agent

---

## Project-Specific Tasks

### R1 — Retrieve and display open purchase orders

- [ ] Wire `get_open_purchase_orders` tool into the agent's tool list in `agent.py`
- [ ] Verify the agent can respond to: "Show me all open purchase orders" by calling `get_open_purchase_orders` and presenting results

### R2 — Flag POs that require follow-up

- [ ] Wire `flag_purchase_orders` tool into the agent's tool list
- [ ] Verify the agent correctly responds to: "Which POs need follow-up?" by calling `get_open_purchase_orders` then `flag_purchase_orders` and presenting only flagged POs with their flag reasons
- [ ] Verify clean (non-flagged) POs are excluded from the follow-up response

### R3 — Rank flagged POs by urgency and value

- [ ] Wire `rank_purchase_orders` tool into the agent's tool list
- [ ] Verify the agent calls `rank_purchase_orders` after `flag_purchase_orders` and presents results in ranked order (most overdue first, then by value)
- [ ] Verify the agent explains the ranking logic to the buyer in its response

### R4 — Present a structured per-PO summary

- [ ] Verify each flagged PO in the agent response includes: supplier name, PO number, item description, net amount + currency, scheduled delivery date, days overdue, and all flag reasons
- [ ] Verify the response is readable and business-friendly (not raw JSON)

### R5 — Draft a supplier follow-up email

- [ ] Wire `draft_supplier_email` tool into the agent's tool list
- [ ] Verify the agent responds to: "Draft a follow-up email for PO 4500001234" by calling `draft_supplier_email` with the correct PO details and then composing a professional draft email
- [ ] Verify every drafted email: references the PO number and issue, is professional and collaborative in tone, is explicitly marked as DRAFT for buyer review

### R6 — Enforce strict read-only operation

- [ ] Verify the agent refuses any write-action request (e.g. "Cancel PO 4500001234", "Send the follow-up email", "Approve this order") with a polite refusal explaining the read-only constraint
- [ ] Verify no tool in the agent performs any write, update, delete, or send operation

### R7 (High-want) — Natural language query interface

- [ ] Verify the agent correctly handles varied phrasings:
  - "Which POs are overdue this week?"
  - "Show me POs missing goods receipt"
  - "Draft an email for PO 4500001235"
  - "What are my top 3 most urgent POs right now?"

### R8 (High-want) — Filter by supplier or date range

- [ ] Implement basic filter support: when the user asks for POs from a specific supplier (e.g. "Show overdue POs for Acme Supplies GmbH"), the agent filters results client-side after loading all POs
- [ ] Verify filtering works for both supplier name and delivery date range

---

## Business Instrumentation

- [ ] Implement structured logging and OpenTelemetry spans for all five PRD milestones:

  **M1 — PO Data Loaded**
  - Log on achievement: `M1.achieved: PO data loaded successfully — {count} records available`
  - Log on miss: `M1.missed: PO data could not be loaded — {error_detail}`
  - Instrument in the `get_open_purchase_orders` tool execution path

  **M2 — Flagging Logic Applied**
  - Log on achievement: `M2.achieved: Flagging logic applied — {flagged_count} POs flagged out of {total_count}`
  - Log on miss: `M2.missed: Flagging logic did not complete — {error_detail}`
  - Instrument in the `flag_purchase_orders` tool execution path

  **M3 — Ranked Results Returned**
  - Log on achievement: `M3.achieved: Ranked results ready — {flagged_count} flagged POs presented to buyer`
  - Log on miss: `M3.missed: Ranking did not complete — {error_detail}`
  - Instrument in the `rank_purchase_orders` tool execution path

  **M4 — Email Drafted**
  - Log on achievement: `M4.achieved: Draft email generated for PO {po_number} — reason: {flag_reason}`
  - Log on miss: `M4.missed: Email draft could not be generated for PO {po_number} — {error_detail}`
  - Instrument in the `draft_supplier_email` tool execution path

  **M5 — Buyer Review Confirmed (Read-Only Constraint)**
  - Log on achievement: `M5.achieved: Session completed — read-only constraint maintained throughout`
  - Log on miss: `M5.missed: Unexpected write attempt detected — {action_detail}; operation blocked`
  - Instrument in the agent's main response path (session end / refusal handler)

- [ ] Verify `bootstrap(app)` is called after `app = server.build()` in `main.py`
- [ ] Run validation: `grep -r "M[0-9]\.achieved" assets/po-followup-assistant-agent/app/` — must return at least 5 results

---

## MCP Tool Integration

> This agent has no SAP API MCP servers. Mock data is fully self-contained. No MCP servers are required. No `mcp-translation-file` skill invocation is needed. No `mcp-mock.json` generation is needed (there are no MCP tools to mock).

- [ ] Confirm `asset.yaml` has no `requires` entries for MCP servers (the agent needs none for this build)
- [ ] Confirm no direct HTTP clients (`requests`, `httpx`, etc.) are used anywhere in the agent code for SAP API access

---

## Testing

- [ ] Install test dependencies: `pip install -r requirements-test.txt` from `assets/po-followup-assistant-agent/`
- [ ] Write unit test for `get_open_purchase_orders` tool in `assets/po-followup-assistant-agent/tests/test_get_open_purchase_orders.py`:
  - Verify the tool returns a non-empty list
  - Verify each record contains the required fields (`PurchaseOrder`, `Supplier`, `items`, etc.)
  - Run the test immediately after writing
- [ ] Write unit test for `flag_purchase_orders` tool in `assets/po-followup-assistant-agent/tests/test_flag_purchase_orders.py`:
  - Verify OVERDUE flag is applied when `ScheduleDeliveryDate` < today
  - Verify DUE_SOON flag is applied when delivery is 1–3 days away
  - Verify MISSING_ACK flag is applied when `OrderAcknowledgmentNumber` is null
  - Verify MISSING_GR flag is applied when delivery date passed and `GoodsReceiptStatus` == "OPEN"
  - Verify a PO with no flags does NOT appear in the output
  - Verify a PO can carry multiple flags simultaneously
  - Run the test immediately after writing
- [ ] Write unit test for `rank_purchase_orders` tool in `assets/po-followup-assistant-agent/tests/test_rank_purchase_orders.py`:
  - Verify most overdue PO is ranked first
  - Verify among equally overdue POs, highest `NetAmount` is ranked first
  - Verify `rank` and `days_overdue` fields are added to each result
  - Run the test immediately after writing
- [ ] Write unit test for `draft_supplier_email` tool in `assets/po-followup-assistant-agent/tests/test_draft_supplier_email.py`:
  - Verify the tool returns a dict with all required fields
  - Verify `draft_instruction` is a non-empty string
  - Verify the tool does NOT make any LLM or HTTP calls
  - Run the test immediately after writing
- [ ] Write one integration test in `assets/po-followup-assistant-agent/tests/test_integration.py`:
  - Mock the LLM (ChatLiteLLM) to return a canned response
  - Call the agent's `invoke` function with: "Which POs need follow-up today?"
  - Verify the response references at least one flagged PO
  - Verify the full tool chain fires: `get_open_purchase_orders` → `flag_purchase_orders` → `rank_purchase_orders`
  - All mocks must be offline — no real AI Core or network calls
- [ ] Run `pytest` from `assets/po-followup-assistant-agent/` (no args) — coverage must be ≥ 70%
- [ ] If coverage < 70%, add targeted tests until threshold is met
- [ ] Run `pytest` again from `assets/po-followup-assistant-agent/` (no args) to generate final `test_report.json`
- [ ] Verify `test_report.json` exists in `assets/po-followup-assistant-agent/`
