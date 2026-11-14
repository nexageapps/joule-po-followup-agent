# S/4HANA Purchasing Follow-Up Assistant

## Business challenge

Buyers spend significant time manually identifying open purchase orders that need follow-up — overdue deliveries, missing supplier order acknowledgements, and missing goods receipts. The process is error-prone and slow. A read-only AI assistant should automatically surface the right POs, rank them by urgency and value, and draft polite follow-up emails for the buyer to review and send. The buyer stays fully in control; the assistant never changes, approves, cancels, or sends anything.

## Business Goals & Success Criteria

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Reduction in late deliveries | — | –20% | 90 days | PO delivery tracking & supplier follow-up | user |
| Buyer time spent chasing POs | — | –50% | 90 days | PO monitoring & follow-up email drafting | user |

## Key Milestones

1. **PO data loaded** — Mock PO data (shaped like API_PURCHASEORDER_PROCESS_SRV) is available to the agent and can be queried.
2. **Flagging logic applied** — Agent correctly identifies POs that are overdue, due within 3 days, missing acknowledgement, or missing goods receipt after delivery date.
3. **Ranked results returned** — Agent ranks flagged POs by urgency (days overdue) and value (PO amount) and presents a structured summary.
4. **Email drafted** — Agent drafts a short, polite follow-up email per flagged PO for buyer review.
5. **Buyer review confirmed** — Buyer reviews output and confirms the assistant never modifies any data.

## Business Architecture (RBA)

### End-to-End Process

Source to Pay (E2E)

### Process Hierarchy

```
Source to Pay (E2E)
└── Procure to Receipt (generic)
    └── Purchase products and services (generic) [BPS-329]
        └── Manage purchase order
└── Manage Suppliers and Collaboration (generic)
    └── Manage suppliers and networked collaboration (generic) [BPS-332]
        └── Evaluate supplier performance
        └── Manage supplier collaboration
```

### Summary

The assistant maps to the Source to Pay E2E, specifically the "Purchase products and services" and "Manage suppliers and networked collaboration" sub-processes — covering PO lifecycle monitoring and supplier follow-up activities.

## Fit Gap Analysis

| Requirement (business) | Standard asset(s) found | API ORD ID | MCP Server ORD ID | MCP Server Version | Webhook API ORD ID | Data Product ORD ID | Gap? | Notes / assumptions |
|------------------------|------------------------|------------|-------------------|--------------------|--------------------|---------------------|------|---------------------|
| Read open POs with delivery dates, acknowledgement and GR status | SAP S/4HANA Cloud (Purchase Order Processing) | `sap.s4:apiResource:API_PURCHASEORDER_PROCESS_SRV:v1` | — | — | — | — | Yes | No MCP server found; mock data shaped like API_PURCHASEORDER_PROCESS_SRV is used |
| Flag POs overdue / due within 3 days | SAP S/4HANA Cloud (Purchase Order Processing) | `sap.s4:apiResource:CE_PURCHASEORDER_0001:v1` | — | — | — | — | Yes | CE_PURCHASEORDER_0001 available but no MCP; mock data with same schema used for this build |
| Flag missing supplier order acknowledgements | SAP S/4HANA Cloud | `sap.s4:apiResource:OP_SUPPLIERCONFIRMATION_0001:v1` | — | — | — | — | Yes | Covered via mock PO data fields |
| Flag missing goods receipts after delivery date | SAP S/4HANA Cloud | `sap.s4:apiResource:SSPOPENITMGOODSRECEIPT_0001:v1` | — | — | — | — | Maybe | API available but no MCP; mock data covers this for the current build |
| Rank flagged POs by urgency and value | Custom logic (no standard asset) | — | — | — | — | — | Yes | Agent-implemented ranking logic |
| Draft supplier follow-up emails | Custom AI generation (no standard asset) | — | — | — | — | — | Yes | Agent drafts email text; buyer must review and send manually |

### Key findings

- No MCP servers are configured for the relevant S/4HANA Purchase Order APIs in this build. Mock data shaped like API_PURCHASEORDER_PROCESS_SRV is used.
- The agent is strictly read-only: it queries data and drafts text only; no write, approval, cancellation, or send capability.
- SAP S/4HANA Cloud (Public and Private Edition) covers Purchase Order Processing natively; for a production build, the CE_PURCHASEORDER_0001 or API_PURCHASEORDER_PROCESS_SRV OData APIs would be the integration point.
- SAP Fieldglass and SAP Ariba capabilities are not relevant here (no external workforce or Ariba procurement network in scope).
- Urgency ranking and email drafting are custom AI capabilities with no standard SAP asset — this is the core value-add of the agent.

## Recommendations

### AI Purchasing Follow-Up Assistant

#### Executive Summary

Read-only Python AI agent monitors POs and drafts supplier emails.

#### Recommended Solution

A pro-code Python AI agent (A2A protocol) that ingests mock purchase order data shaped like the S/4HANA API_PURCHASEORDER_PROCESS_SRV OData service. The agent applies flagging rules (delivery overdue, due within 3 days, missing acknowledgement, missing goods receipt), ranks results by urgency and monetary value, and generates a draft follow-up email per flagged PO. The buyer interacts with the agent via natural language and reviews all output before acting. No data is modified.

#### Recommended solution category

AI Agent

#### Intent fit
95%
