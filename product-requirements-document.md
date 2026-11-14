# Product Requirements Document (PRD)

**Title:** S/4HANA Purchasing Follow-Up Assistant  
**Date:** 2026-11-14  
**Owner:** Procurement Product Owner  
**Solution Category:** AI Agent

---

## Product Purpose & Value Proposition

**Elevator Pitch:**  
Buyers waste time each day manually hunting through open purchase orders to identify which ones are at risk — overdue, unacknowledged, or without goods receipt. This AI assistant does that hunting automatically, surfaces the right POs ranked by urgency and value, and puts a draft supplier email in the buyer's hands ready to review. No data is ever changed; the buyer stays in control.

**Business Need:**  
Procurement teams lack a fast, reliable way to identify open POs that need urgent attention. Manual review is slow and error-prone, causing late supplier escalations and missed delivery follow-ups. An intelligent, read-only assistant that flags and ranks the right POs — and drafts communications — removes the burden while keeping the buyer in the decision seat.

**Expected Value:**

- Reduce late deliveries by 20% within 90 days through faster, consistent supplier follow-up
- Cut buyer time spent chasing POs by 50% within 90 days by eliminating manual PO review

**Product Objectives (Prioritized):**

1. Accurately flag every open PO that meets one or more follow-up criteria (overdue, due within 3 days, missing acknowledgement, missing goods receipt)
2. Rank flagged POs by urgency and monetary value so buyers act on the highest-impact items first
3. Generate a ready-to-review supplier follow-up email for each flagged PO, reducing drafting effort to zero
4. Guarantee strict read-only operation — no PO data is ever modified, approved, cancelled, or transmitted

---

## Business Metrics

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Reduction in late deliveries | — | –20% | 90 days | PO delivery tracking & supplier follow-up | user |
| Buyer time spent chasing POs | — | –50% | 90 days | PO monitoring & follow-up email drafting | user |

---

## User Profiles & Personas

### Primary Persona: Alex — Procurement Buyer

Alex is a 34-year-old procurement buyer at a mid-sized manufacturing company, managing 80–120 open purchase orders at any time across multiple suppliers. Every morning, Alex spends 30–45 minutes scrolling through spreadsheet exports and S/4HANA screens trying to identify which POs are at risk. By the time Alex writes follow-up emails to suppliers, half the morning is gone. Alex is comfortable with SAP and business tools but frustrated by repetitive, manual investigation work. Success for Alex means being able to start the day knowing exactly which POs need attention — and having the first-draft email ready to go.

**Pain points:**
- No consolidated view of at-risk POs; has to check multiple fields manually
- Writing follow-up emails to suppliers takes 10–15 minutes per PO
- Risk of missing a critical delivery because it got buried in the list

### Secondary Persona: Maria — Procurement Manager

Maria is a 45-year-old procurement manager overseeing a team of five buyers. She needs visibility into which suppliers consistently have delivery or acknowledgement issues, and she wants her team spending time on decisions, not data gathering. She interacts with the assistant less frequently but values the ranked, structured output for team briefings.

**Pain points:**
- Difficulty getting a quick picture of which suppliers are most problematic
- Team spends too much time on administrative follow-up rather than strategic sourcing

### Other User Types

- **IT / Platform Administrator** — deploys and maintains the agent; responsible for mock data updates and future API connectivity.

---

## User Goals & Tasks

### For Alex (Procurement Buyer):

**Goals:**
- Know every at-risk PO within 2 minutes of starting the day
- Have a draft follow-up email ready for each flagged PO without writing it from scratch

**Key Tasks:**
- Ask the agent: "Which POs need follow-up today?"
- Review the ranked list and prioritise by urgency or value
- Review and optionally edit the drafted email, then send it themselves

### For Maria (Procurement Manager):

**Goals:**
- Get a quick summary of the highest-priority overdue POs for team briefings

**Key Tasks:**
- Ask the agent: "Show me the top 5 most urgent overdue POs"
- Use the structured summary to identify repeat offenders among suppliers

---

## Product Principles

1. **Buyer in control**: The agent proposes; the buyer decides. Nothing is sent, changed, or approved without explicit buyer action.
2. **Urgency first**: Output is always ordered by what matters most — days overdue and monetary value — so buyers never have to re-sort.
3. **Zero noise**: Only flag POs that genuinely need action. False positives erode trust faster than missed POs.
4. **Transparent reasoning**: For every flagged PO, the agent states exactly why it was flagged (overdue / due soon / no ACK / no GR), so the buyer understands the situation instantly.
5. **Future-ready**: The mock data layer is designed to be swapped for live S/4HANA API calls without changing agent logic.

---

## Business Context

**Current State:**  
Buyers manually review open PO lists exported from S/4HANA, cross-reference delivery dates, check acknowledgement status, and look for missing goods receipts — all across separate screens and exports. Follow-up emails are written from scratch per supplier. The process takes 30–45 minutes daily per buyer and is inconsistently applied across the team.

**Strategic Alignment:**  
Improving supplier follow-up speed directly supports on-time delivery KPIs and working capital targets. This assistant is the first step toward a broader AI-augmented procurement function.

**Success Criteria:**  
See the Business Metrics section above.

---

## Goals and Non-Goals

### Goals (In Scope)

- Flag all open POs where: delivery date has passed, delivery is due within 3 calendar days, supplier order acknowledgement is missing, or goods receipt is missing after the delivery date
- Rank flagged POs by urgency (days overdue) and PO value (descending)
- Present a structured summary per flagged PO: supplier name, PO number, line item, net value, delivery date, and flag reason(s)
- Draft a short, polite supplier follow-up email per flagged PO for buyer review
- Operate exclusively on mock PO data shaped like the S/4HANA API_PURCHASEORDER_PROCESS_SRV OData service

### Non-Goals (Out of Scope)

- Sending, posting, or transmitting emails or messages to suppliers
- Creating, updating, approving, or cancelling any purchase order or related document
- Connecting to a live S/4HANA system or any external API in this build
- Supplier performance analytics or trend reporting beyond the current flagged PO list
- Multi-language email drafting (English only in this build)

---

## Requirements

### Must-Have Requirements

**R1**: Retrieve and display open purchase orders

- **Problem to Solve**: Buyers cannot quickly see all open POs in one consolidated view without manual export and cross-referencing.
- **User Story**: As a buyer, I need the agent to load and present all open purchase orders so that I have a complete, current picture without manual data gathering.
- **Acceptance Criteria**:
  - Given the agent is invoked, when the buyer asks for open POs, then the agent returns a list of all open POs from the mock data source including supplier, PO number, item description, net value, and scheduled delivery date.
- **Maps to Objective**: Objective 1
- **Priority Rank**: 1

---

**R2**: Flag POs that require follow-up

- **Problem to Solve**: Buyers must manually check four different conditions across each PO to determine whether action is needed; this is slow and inconsistent.
- **User Story**: As a buyer, I need the agent to automatically flag any PO that is overdue, due within 3 days, missing supplier acknowledgement, or missing goods receipt after its delivery date — so I focus only on POs that actually need action.
- **Acceptance Criteria**:
  - Given a PO with a delivery date in the past, when the agent runs flagging logic, then the PO is flagged as "Overdue".
  - Given a PO with a delivery date within 3 calendar days from today, when the agent runs flagging logic, then the PO is flagged as "Due soon".
  - Given a PO with no supplier order acknowledgement recorded, when the agent runs flagging logic, then the PO is flagged as "Missing acknowledgement".
  - Given a PO whose delivery date has passed and no goods receipt is recorded, when the agent runs flagging logic, then the PO is flagged as "Missing goods receipt".
  - A PO may carry multiple flags simultaneously.
- **Maps to Objective**: Objective 1
- **Priority Rank**: 2

---

**R3**: Rank flagged POs by urgency and value

- **Problem to Solve**: When multiple POs are flagged, buyers have no structured way to decide which to act on first.
- **User Story**: As a buyer, I need flagged POs ranked by urgency (days overdue) and monetary value so that I address the highest-impact items first.
- **Acceptance Criteria**:
  - Given a list of flagged POs, when the agent returns ranked results, then POs are sorted primarily by days overdue (most overdue first) and secondarily by net PO value (highest first).
  - The ranking logic is explained to the buyer in the response.
- **Maps to Objective**: Objective 2
- **Priority Rank**: 3

---

**R4**: Present a structured per-PO summary

- **Problem to Solve**: Buyers need key facts about each flagged PO at a glance to understand the situation before contacting a supplier.
- **User Story**: As a buyer, I need a concise summary for each flagged PO — supplier, PO number, item, value, delivery date, and flag reason — so I can assess the situation without navigating to S/4HANA.
- **Acceptance Criteria**:
  - Given a flagged PO, when the agent presents it, then the response includes: supplier name, PO number, line item description, net value, scheduled delivery date, days overdue (if applicable), and all flag reasons.
- **Maps to Objective**: Objective 2
- **Priority Rank**: 4

---

**R5**: Draft a supplier follow-up email per flagged PO

- **Problem to Solve**: Writing individual follow-up emails to suppliers is repetitive and time-consuming, taking 10–15 minutes per PO.
- **User Story**: As a buyer, I need the agent to draft a short, polite follow-up email for each flagged PO so that I can review, adjust if needed, and send — without writing from scratch.
- **Acceptance Criteria**:
  - Given a flagged PO, when the buyer requests an email draft, then the agent produces a professional, polite email referencing the PO number, item, delivery date, and the specific issue (overdue / no ACK / no GR).
  - The email is explicitly marked as a draft for buyer review; the agent does not send it.
  - The tone is professional and collaborative, not threatening.
- **Maps to Objective**: Objective 3
- **Priority Rank**: 5

---

**R6**: Enforce strict read-only operation

- **Problem to Solve**: Buyers must trust that using the assistant carries zero risk of inadvertent data changes.
- **User Story**: As a buyer, I need assurance that the agent never modifies, approves, cancels, or sends anything, so that I can use it confidently without fear of unintended consequences.
- **Acceptance Criteria**:
  - Given any user input, when the agent processes a request, then it performs no write, update, delete, approval, cancellation, or message-transmission operation.
  - If a user asks the agent to perform a write action, it politely declines and explains its read-only scope.
- **Maps to Objective**: Objective 4
- **Priority Rank**: 1

---

### High-Want Requirements

**R7**: Natural language query interface

- **Problem to Solve**: Buyers want to interact with the assistant conversationally rather than through fixed commands.
- **User Story**: As a buyer, I need to ask the agent questions in plain language (e.g. "Which POs are overdue this week?", "Draft an email for PO 4500001234") so that the experience feels natural.
- **Priority Rank**: 1

---

**R8**: Filter and focus by supplier or date range

- **Problem to Solve**: Buyers sometimes need to focus on a specific supplier or time window rather than the full PO list.
- **User Story**: As a buyer, I need to ask the agent to show flagged POs for a specific supplier or delivery window so that I can prepare for a supplier call.
- **Priority Rank**: 2

---

## Non-Functional Requirements

### Performance
- **Latency**: Agent should return a ranked list of flagged POs within 10 seconds of a buyer request (mock data, no live API latency).
- **Throughput**: Designed for single-user interactive sessions; no high-concurrency requirement in this build.

### Reliability
- **Availability**: Runs as a deployed cloud service; standard platform availability applies.
- **Fallback**: If mock data cannot be loaded, the agent returns a clear error message and does not silently return an empty list.

### Explainability
- **Traceability**: Each flagged PO response states the exact reason(s) for flagging, referencing the data fields that triggered it.
- **Decision Logging**: All milestone events are logged with structured messages (see Milestones section).
- **Uncertainty Communication**: If a PO's status fields are null or ambiguous in the mock data, the agent notes the uncertainty rather than making assumptions.

---

## Solution Architecture

**Architecture Overview:**  
A single Python AI agent (A2A protocol) deployed on SAP BTP. The agent uses an internal mock data module as its data source, applies rule-based flagging and ranking logic, and uses an LLM (via SAP Generative AI Hub) for natural language interaction and email drafting. No external system calls are made in this build.

**Key Components:**

- **Python AI Agent (A2A)**: Core agent runtime; handles natural language understanding, tool orchestration, and response generation
- **Mock PO Data Module**: In-memory or file-based dataset of purchase orders shaped exactly like the S/4HANA API_PURCHASEORDER_PROCESS_SRV OData schema
- **PO Flagging Tool**: Rule-based tool that evaluates each PO against the four follow-up criteria and returns a list of flagged POs with reasons
- **Ranking Tool**: Sorts flagged POs by days overdue (primary) and net PO value (secondary)
- **Email Drafting Tool**: Uses the LLM to generate a professional supplier follow-up email from structured PO data

**Integration Points:**

- Mock data module: read-only internal; no network call; serves as a stand-in for the S/4HANA API_PURCHASEORDER_PROCESS_SRV OData endpoint
- SAP Generative AI Hub: LLM calls for response generation and email drafting

**Deployment Environments:**

- Development / Test: mock data only
- Production (future): Replace mock data module with live S/4HANA API_PURCHASEORDER_PROCESS_SRV OData calls; no agent logic changes required

---

### Agent Extensibility & Instrumentation

**Agent Extensibility:**
- The mock data layer is isolated behind a tool interface; swapping it for a live API call requires only updating that tool — no changes to agent logic, prompts, or ranking/flagging code.
- Additional flagging criteria (e.g. price deviation, partial delivery) can be added as new rules within the flagging tool without modifying other components.
- Email drafting tone and template can be customised via system prompt configuration without code changes.

**Business Step Instrumentation:**
- Each milestone listed below corresponds to a named business step that must emit a structured log on achievement and on miss.
- Log format: `[MILESTONE_ID].[achieved|missed]: [description]`
- These logs are the basis for production observability, debugging, and future OpenTelemetry span instrumentation.

---

### Automation & Agent Behaviour

**Automation Level:** Hybrid — rule-based flagging and ranking + LLM-assisted natural language and email drafting

**Actions the system performs without human approval:**
- Load and filter open PO data from the mock data source
- Apply flagging rules and determine which POs need follow-up
- Rank flagged POs by urgency and value
- Generate draft email text for buyer review

**Actions that require human review or approval:**
- Sending any email or communication to a supplier (buyer must copy, edit, and send manually)
- Any interpretation of ambiguous PO status data

**Model or engine used:** SAP Generative AI Hub (GPT-4o or equivalent) for natural language understanding and email drafting

**Knowledge & data sources accessed:**
- Mock PO dataset (read-only): purchase order headers and items shaped like API_PURCHASEORDER_PROCESS_SRV; includes delivery date, acknowledgement flag, goods receipt flag, supplier, item, and net value fields

**Tools or connectors invoked:**
- `get_open_purchase_orders` (read-only): loads all open POs from the mock data source
- `flag_purchase_orders` (read-only): applies follow-up criteria rules and returns flagged POs with reasons
- `rank_purchase_orders` (read-only): sorts flagged POs by urgency and value
- `draft_supplier_email` (read-only): generates a draft follow-up email for a given flagged PO

**Guardrails & fail-safes:**
- The agent must never execute any write, update, delete, approval, or message-transmission operation under any circumstances
- If the user requests a write action, the agent declines and states its read-only scope
- If PO data cannot be loaded, the agent surfaces a clear error rather than returning an empty or misleading result
- The agent does not speculate about supplier intent or use accusatory language in drafted emails

---

### Configuration & Data

**Configuration Scope:**  
Mock PO data file location and format; LLM model endpoint and credentials via SAP AI Core binding.

**Organisational & Master Data:**
- Mock PO dataset must include realistic supplier names, PO numbers, item descriptions, net values, delivery dates, acknowledgement flags, and goods receipt flags.

---

## Milestones

### M1: PO Data Loaded

- **Description**: The agent has successfully loaded the mock PO dataset and it is available for processing.
- **Achieved when**: The mock data source returns one or more purchase order records without error.
- **Log on achievement**: `M1.achieved: PO data loaded successfully — {count} records available`
- **Log on miss**: `M1.missed: PO data could not be loaded — {error_detail}`

### M2: Flagging Logic Applied

- **Description**: The agent has evaluated all open POs against the four follow-up criteria.
- **Achieved when**: The flagging tool completes execution and returns a list of zero or more flagged POs with their reasons.
- **Log on achievement**: `M2.achieved: Flagging logic applied — {flagged_count} POs flagged out of {total_count}`
- **Log on miss**: `M2.missed: Flagging logic did not complete — {error_detail}`

### M3: Ranked Results Returned

- **Description**: The flagged PO list has been sorted by urgency and value and is ready to present to the buyer.
- **Achieved when**: The ranking tool returns a sorted list with at least one entry, or returns an empty list when no POs are flagged.
- **Log on achievement**: `M3.achieved: Ranked results ready — {flagged_count} flagged POs presented to buyer`
- **Log on miss**: `M3.missed: Ranking did not complete — {error_detail}`

### M4: Email Drafted

- **Description**: The agent has generated a draft supplier follow-up email for a specific flagged PO.
- **Achieved when**: The email drafting tool returns a non-empty email text referencing the correct PO number and issue.
- **Log on achievement**: `M4.achieved: Draft email generated for PO {po_number} — reason: {flag_reason}`
- **Log on miss**: `M4.missed: Email draft could not be generated for PO {po_number} — {error_detail}`

### M5: Buyer Review Confirmed (Read-Only Constraint)

- **Description**: The buyer has reviewed the agent output; no data modification was attempted by the agent.
- **Achieved when**: The agent session concludes without any write, update, or send operation having been executed.
- **Log on achievement**: `M5.achieved: Session completed — read-only constraint maintained throughout`
- **Log on miss**: `M5.missed: Unexpected write attempt detected — {action_detail}; operation blocked`

---

## Risks, Assumptions, and Dependencies

### Risks

- **Mock data quality**: If the mock dataset does not faithfully reflect the API_PURCHASEORDER_PROCESS_SRV schema, flagging logic may need rework when connecting to a live system.
- **LLM email tone**: Generated emails may occasionally require buyer editing for tone or specificity; the agent cannot guarantee perfectly tailored language for every supplier relationship.

### Assumptions (Validate These)

- The mock PO dataset will include all fields needed for flagging: delivery date, acknowledgement flag, goods receipt indicator, supplier name, item description, and net value.
- Buyers will operate in English; no multi-language requirement in this build.
- The mock data approach is used for this build phase.

### Dependencies

- SAP Generative AI Hub: LLM endpoint available and accessible from the BTP deployment
- SAP BTP: deployment platform for the agent runtime

---

## Open Questions

- When a production connection to S/4HANA is established, which authentication method will be used (OAuth2, basic auth, principal propagation)?
- Should the email drafting take into account any existing supplier communication history, or always draft from scratch?
- Is there a preference for how the buyer accesses the agent — web UI, SAP Build Work Zone integration, or Joule chat?
