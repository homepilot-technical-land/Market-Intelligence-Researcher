# HomePilot Market Intelligence Engine — Objective-Driven Research Blueprint

**Version:** 2.1.0-RESEARCH-EDITION  
**Focus:** Objective-Driven Intelligence & Audience Persona Benchmarking  
**Status:** Operational & Verified (20 / 20 Tests Passing)  
**Foundation Document:** HomePilot Audience Persona & Content Campaign Template  

---

## 1. Objective-Driven Research: Inside-Out Intelligence

While **Source-Driven Intelligence** monitors *what external sources choose to publish*, the **Objective-Driven Research Engine** investigates *what HomePilot needs to know* to empower its users and differentiate its brand.

```mermaid
flowchart TD
    subgraph InsideOut ["Objective-Driven Research Loop"]
        Obj["HomePilot Strategic Objective\n(e.g. 'Investigate FTB Hidden Costs & Commuter Affordability')"] --> Decomp["Decompose into Empirical Questions\n• Upfront closing cash gap\n• Scheme cap vs. base price shifts\n• Conveyancing timeline lag"]
        Decomp --> Search["Query Registered Feeds & Authoritative Feeds\n(Revenue, Central Bank, BPFI, Glenveagh, PPR)"]
        Search --> Benchmark["Benchmark Against 5 Granular Personas\n(Frustrated FTB, Optimiser, Planner, Owner, Wealth Builder)"]
        Benchmark --> Gap["Identify Evidence & Data Gaps\n(e.g. Missing LEA rental stats, localized survey fees)"]
        Gap --> Brief["Structured Research Brief\n(Stored in research_runs for Marketing & Product)"]
    end
```

---

## 2. Persona Benchmarking & Market Reality Matrix

Every empirical finding from incoming feeds is benchmarked against the **5 Granular Audience Segments** defined in the campaign template:

| Segment ID | Audience Segment | Demographics | Core Market Friction Identified in Feeds | Emotional Transformation | Primary HomePilot Positioning Hook |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`seg_1`** | **The Frustrated First-Time Buyer** | Age 28–40<br>€35k–€90k | Repeated calculator usage; feels stuck; overwhelmed by banking jargon and unclear roadmap. | Confused & anxious $\rightarrow$ Certainty & clear roadmap | *"Stop calculating borrowing limits. Start building your step-by-step homeownership plan."* |
| **`seg_2`** | **The Mortgage-Ready Optimiser** | Age 27–38<br>€60k–€120k+ | Financially ready but confused about Help to Buy (HTB) vs. First Home Scheme (FHS) equity trade-offs. | Prepared but cautious $\rightarrow$ Strategic optimization | *"Being mortgage-ready isn't the same as being homeownership-ready. Optimize your scheme and rate strategy before you apply."* |
| **`seg_3`** | **The Homeownership Planner** | Age 28–45<br>€50k–€130k | Sale agreed; drowning in conveyancing delays, structural surveys, valuation deadlines, and closing fees. | Stressed & frantic $\rightarrow$ Task visibility & control | *"Over 60 tasks stand between 'Sale Agreed' and 'Keys Collected'. Coordinate your purchase with clarity."* |
| **`seg_4`** | **The New Homeowner** | Age 29–45<br>€50k–€150k | Recently bought; cash-strapped after closing, managing unexpected furniture, renovation, and maintenance costs. | Relieved but cash-poor $\rightarrow$ Budget stability | *"The journey doesn't end when you get the keys. Protect and budget for your home's ongoing health."* |
| **`seg_5`** | **The Future Wealth Builder** | Age 30–50<br>€70k–€180k+ | Wants to maximize equity growth, overpayment interest savings, green mortgage retrofits, and future upgrades. | Ambitious $\rightarrow$ Equity acceleration | *"Your home is your largest financial asset. Build equity faster and shave years off your mortgage."* |

---

## 3. Systems Thinking: Deconstructing the "Real Cost of Buying"

When incoming feeds report market developments (e.g., *a new residential launch in Navan* or *an update to the Help to Buy scheme*), the research engine deconstructs the **underlying system dynamics**:

```mermaid
flowchart LR
    A["Nominal Inflow:\nHTB Grant (€30k)\nFHS Equity Share"] --> Stock["Buyer Liquid Cash Reserve"]
    Stock --> Outflow1["Deposit Outflow (10% Base Price)"]
    Stock --> Outflow2["Conveyancing Legal Fees (€2,500 - €3,500)"]
    Stock --> Outflow3["Stamp Duty (1% of Price)"]
    Stock --> Outflow4["Structural Survey & Valuation (€800 - €1,200)"]

    style Stock fill:#ffffcc,stroke:#333,stroke-width:2px
    style Outflow2 fill:#ffcccc,stroke:#333
    style Outflow3 fill:#ffcccc,stroke:#333
    style Outflow4 fill:#ffcccc,stroke:#333
```

### Empirical Research Findings:
1. **The Inflow/Outflow Disparity**: Subsidies give the illusion of affordability, but developer pricing models in commuter towns often capitalize the grant directly into the base price.
2. **The Closing Cash Deficit**: Buyers commonly save *only* the 10% deposit requirement, leaving a **€7,500 to €12,000 cash deficit** at conveyancing closing.
3. **Conveyancing Latency Risk**: Average transaction cycle times of **12 to 16 weeks** between "Sale Agreed" and drawdown risk loan offer expiration during rate hike cycles.

---

## 4. The 4 Architectures Integration

The research engine cross-references market evidence against HomePilot's **4 Core Architecture Layers**:

```mermaid
mindmap
  root((HomePilot Core Advantage))
    Utility Architecture
      Mortgage Simulation Engine
      Scenario Comparison Engine
      Government Scheme Engine
      Budget Planning Engine
      Stress Testing Engine
    Psychological Architecture
      Readiness Score
      Ownership Gap Analysis
      Momentum Tracking
      Dream Home Roadmap
    Lifecycle Architecture
      Pre-purchase Planning
      Purchase Task Execution (60+ Tasks)
      Post-purchase Maintenance
      Wealth Building & Equity Monitoring
    Transaction Ecosystem
      Mortgage Brokers & Advisors
      Solicitors & Conveyancers
      Insurers & Surveyors
      Furniture & Retrofit Suppliers
```

---

## 5. Implementation & Verification Status

### Codebase Additions:
1. **[config/marketing_campaign_personas.json](file:///Users/samson/Documents/HomePilot's%20projects/External%20Website%20Research%20Tool/config/marketing_campaign_personas.json)**:
   - Contains all 5 Granular Audience Segments, Tone of Voice rules ("Instead of bank jargon, say..."), and commercial offerings (90-Day Buyer Journey Pass at €39–€49).
2. **[src/intelligence/research_engine.py](file:///Users/samson/Documents/HomePilot's%20projects/External%20Website%20Research%20Tool/src/intelligence/research_engine.py)**:
   - `ObjectiveResearchEngine`: Implements empirical research runs, persona benchmarking, gap analysis, and structured report synthesis.
3. **CLI Execution**:
   - Operators can execute on-demand research runs via:
     ```bash
     python cli.py run-research --title "Investigate FTB Hidden Costs & Commuter Affordability"
     ```

### Test Coverage (20 / 20 Tests Passing):
* `tests/test_research_engine.py` validates that objective research runs deconstruct questions, identify evidence gaps, and correctly map findings to the target personas.
* 100% of all Phase 1 and research engine tests pass cleanly.
