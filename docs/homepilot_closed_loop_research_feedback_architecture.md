# HomePilot Closed-Loop Dynamic Research & Ideation Feedback Architecture

## 1. Executive Summary & Concept

This architectural specification formalizes the **closed-loop bilateral feedback mechanism** between the **Market Intelligence Research Engine** (the continuous explorer, evaluator, and data pool) and **xAI / GrokBot** (the ideation, consumer discourse analyst, and campaign drafter).

Rather than treating data ingestion as a static, one-way conveyor belt, this architecture establishes a **self-evolving, demand-driven research cycle**:
1. **Continuous Assessment & Expansion**: The research engine continuously analyzes authoritative Irish housing data, maps county benchmarks, and identifies emerging patterns.
2. **Knowledge Pool Cache Check**: When GrokBot conceptualizes new campaign angles or investigates viral buyer friction from X, it first queries the internal MongoDB knowledge pool for verified facts and statutory rules.
3. **Knowledge Gap & Cold-Spot Flagging**: If GrokBot identifies questions, buyer confusion, or regional blind spots lacking empirical answers in the pool, it tags them as **Unanswered Knowledge Gaps** in a dedicated investigation backlog.
4. **Batched Demand-Driven Re-Ingestion**: Periodically, the research engine batches these gaps and triggers targeted Firecrawl deep scrapes, dynamic authority discovery, or official API queries (PPR, CSO) to resolve the exact missing facts.
5. **Pool Enrichment & Final Verification**: The newly ingested data enriches the knowledge pool, allowing GrokBot to synthesize fully cited, compliant content blueprints ready for dual operator sign-off (Rule B-04).

---

## 2. The Closed-Loop Feedback Cycle

```mermaid
flowchart TD
    subgraph Ideation_Layer["1. Ideation & Real-Time Discourse (xAI / GrokBot)"]
        X["Public X (Twitter) Discussions & Buyer Friction"] --> GrokIdea["GrokBot Formulates Campaign Angle / Question"]
    end

    subgraph Pool_Layer["2. Knowledge Pool Query (MongoDB Source of Truth)"]
        GrokIdea --> CacheCheck{"Is verified evidence in MongoDB Pool?"}
        MongoPool[("MongoDB Knowledge Pool\n• documents\n• evidence_records\n• change_events")]
        MongoPool <--> CacheCheck
    end

    subgraph Hit_Path["3A. Cache Hit (Verified Evidence Present)"]
        CacheCheck -->|YES: Evidence >= 2 (Rule B-02)| BlueprintGen["Campaign Asset Blueprint Generator\n(X Threads, Carousels, Scripts)"]
        BlueprintGen --> OpReview["The 3 R's Operator Signoff (Rule B-04)\nOperator 1 + Operator 2"]
    end

    subgraph Miss_Path["3B. Cache Miss (Knowledge Gap Detected)"]
        CacheCheck -->|NO: Evidence Missing / Unverified| GapBacklog[("Unanswered Gap Backlog\nMongoDB: research_objectives\nstatus: pending_investigation")]
        GapBacklog --> Batcher["Periodic Batch Scheduler\n(e.g., Daily 07:00 UTC or N >= 5 gaps)"]
    end

    subgraph Ingestion_Trigger["4. Targeted Deep-Dive Ingestion"]
        Batcher --> TargetScrape["Targeted Ingestion Dispatcher"]
        TargetScrape --> FC["Firecrawl Targeted Scrape / Search"]
        TargetScrape --> PPR["Property Price Register Query"]
        TargetScrape --> CSO["CSO PxStat Open Data"]
    end

    FC --> MongoPool
    PPR --> MongoPool
    CSO --> MongoPool

    MongoPool -.->|Re-evaluates with fresh evidence| BlueprintGen
```

---

## 3. Structural Mechanics: How the Cycle Operates

### Step 1: The Knowledge Pool as Ground Truth
- The MongoDB collections (`documents`, `evidence_records`, `change_events`, `sources`) form the **Ground Truth Knowledge Pool**.
- It is dynamically refreshed through scheduled source monitoring (35 authoritative Irish sites, PPR, CSO).

### Step 2: GrokBot Ideation & Pool Interrogation
- When GrokBot analyzes real-time discourse on X (e.g. *“Why are Naas new-build booking deposits being forfeited?”*), it does not hallucinate an unverified answer.
- GrokBot performs a semantic search against the MongoDB pool:
  - Query: `booking deposit refundability qualification criteria qualifying contractor`.
  - Check: Does an official Revenue Help to Buy circular or Law Society of Ireland conveyancing condition exist in `evidence_records`?

### Step 3: Branching: Blueprint Generation vs. Gap Backlog
- **Path A (Evidence Exists $\ge 2$ sources)**: GrokBot generates the blueprint (X thread, carousel, video script), attaches verifiable citations (Rule B-02), and stages it for operator approval.
- **Path B (Evidence Missing or Incomplete)**: GrokBot generates an `UnansweredKnowledgeGap` record:
  ```json
  {
    "gap_id": "gap_2026_htb_booking_deposit_forfeit",
    "topic": "Help to Buy booking deposit forfeiture rules in new-build contracts",
    "trigger_source": "X Platform buyer complaint thread in Kildare",
    "missing_evidence": "Statutory terms under which a qualifying contractor can retain a booking deposit before contract exchange",
    "suggested_targets": [
      "https://www.revenue.ie/en/property/help-to-buy-incentive/contractors.aspx",
      "https://www.lawsociety.ie/solicitors/standard-contracts-of-sale"
    ],
    "priority": "HIGH",
    "status": "pending_investigation"
  }
  ```

### Step 4: Periodic Batching & Targeted Ingestion
- Gaps are queued into MongoDB collection `research_objectives`.
- Once batched (e.g. during the morning 07:00 UTC cycle or when 5 gaps accumulate):
  - The pipeline converts the gap into targeted search-and-scrape operations using Firecrawl.
  - Documents are ingested, normalized, scored, and added to the pool.

### Step 5: Pool Re-evaluation & Complete Resolution
- The pipeline re-notifies GrokBot that the missing evidence has landed.
- GrokBot resumes the draft, populates the verified citations, and presents a complete, compliant asset to the human operators.

---

## 4. Key Strategic Advantages of this Design

1. **Zero Hallucination in Public Communications**: Bots never speculate or extrapolate beyond what is certified in the internal pool.
2. **Demand-Driven Budget Efficiency**: Instead of blindly scraping thousands of random web pages (burning Firecrawl credits), scraping is laser-targeted on the exact questions consumers are asking right now.
3. **Compound Intelligence Growth**: Every gap resolved permanently enriches the pool. A question researched once is answered forever for all future bot campaigns.
4. **Autonomous Adaptation**: As market conditions shift (e.g. new government budget announcements, new Central Bank exemption quotas), consumer friction on X immediately highlights what new data HomePilot needs to ingest.
