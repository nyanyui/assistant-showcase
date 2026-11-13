# Reasoning, state and action have different jobs

This conceptual diagram shows the private email/order workflow without deployment
addresses, account details or operational records.

```mermaid
flowchart TD
    Mail[Periodic inbox discovery] --> Interpret[Model interpretation]
    Context[Relevant plans and preferences] --> Interpret
    Interpret --> Alert[Email relevance decision]
    Interpret --> Validate[Validate order observations against evidence]
    Validate --> Outbox[Durable observation outbox]
    Outbox --> Orders[Order and shipment state]
    Orders --> Due[Due carrier checks]
    Due --> Evidence[Supported source observations]
    Evidence --> Orders
    Orders --> Ledger[Readable inventory]
    Orders --> Policy[Notification policy]
    Alert --> Policy
    History[Quiet hours and delivery history] --> Policy
    Policy --> Send[Telegram delivery]
    Send --> Receipts[Confirmed or uncertain outcome]
    Receipts --> History
```

A model interprets meaning. Code validates the declared facts, associates known
references and maintains state. The transport records what happened when sending.
These responsibilities prevent a persuasive sentence from being the only record
that something happened.

The email pipeline maintains its own operational store and readable ledger.
Travel uses typed Markdown records and checked updates. They do not share a
fictional universal database, and this diagram does not imply that every private
integration has been unified into one writer.

## Travel preferences and the trust work

```mermaid
flowchart LR
    User[User updates and corrections] --> Reason[Agent interpretation]
    Preferences[Scoped travel preferences] --> Reason
    Records[Current trips and shared knowledge] --> Reason
    Reason --> Proposal[Proposed answer or update]
    Proposal --> Checks[Version and relationship checks]
    Checks --> Saved[Saved records and readback]
    Research[Ongoing trust work] -.-> Boundaries[Delegation and confirmation rules]
    Boundaries -.-> Proposal
```

The dotted links describe the complementary trust direction, not a claim that
every travel action already passes through a complete trust layer. The
[travel case](TRAVEL_CASE_STUDY.md) distinguishes current behavior from that work.

## Public demo boundary

```mermaid
flowchart LR
    Fixture[Fictional structured observations] --> Validate[Validate the demo contract]
    Validate --> State[Local order and shipment state]
    State --> Policy[Milestone and repeat policy]
    Policy --> Simulation[Print a simulated update]
    Simulation --> Receipts[Local delivery receipts]
    Receipts --> Policy
```

The public fixture replaces both email interpretation and courier retrieval.
SQLite stores synthetic operational state. There is no model, inbox reader,
browser, Telegram adapter, real knowledge base or trust engine in the demo.
Its tests exercise the stated local contract, not the quality of upstream
interpretation or the behavior of external services.
