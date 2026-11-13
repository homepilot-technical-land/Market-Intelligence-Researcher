# Market Intelligence Researcher — Project Kickoff & Blueprint

## Executive Overview
**Market Intelligence Researcher** is a purpose-built intelligence engine for **HomePilot** (the Irish Homeownership Operating System). Its goal is to continuously discover, monitor, extract, and interpret high-signal developments across the Irish housing, mortgage, regulatory, and property landscape.

Rather than acting as a generic web crawler or aggregator, it filters for high-impact intelligence that directly empowers:
- **Customer Education & Confidence**: Demystifying schemes (HTB, First Home Scheme), rate moves, policy shifts, and buyer readiness.
- **Product & Feature Strategy**: Informing mortgage calculator parameters, affordability thresholds, and journey tooling.
- **Brand Authority & Marketing**: Providing verifiable, timely source material for social media, carousels, founder commentary, and campaign briefs.

---

## System Architecture

```mermaid
flowchart TD
    subgraph Discovery ["1. Source Discovery & Monitoring"]
        SR[Approved Source Registry] --> Crawler[Sitemap & URL Mapper]
        Crawler --> ChangeDet[Semantic Change Detection]
    end

    subgraph Processing ["2. Extraction & Assessment"]
        ChangeDet --> Extractor[Structured Information Extraction]
        Extractor --> Scorer[HomePilot Relevance Scorer (0-100)]
        Scorer --> CatClass[12 Intelligence Categories]
    end

    subgraph Intelligence ["3. Strategic Value & Output"]
        CatClass --> StratInterp[10 Strategic Questions Engine]
        StratInterp --> ContentGen[Content & Campaign Proposals]
        ContentGen --> Review[Human-in-the-Loop Review Queue]
    end
```

---

## Core Pillars & Functional Modules

### 1. Source Discovery & Approved Registry
* **Scope**: Controlled list of authorized Irish institutions and industry bodies.
* **Mechanism**: Sitemap discovery, RSS/Atom feeds where available, recursive internal link mapping (restricted strictly to approved root domains).
* **Initial Target Source Registry**:
  - **Statutory / Regulatory / Government**:
    - Central Bank of Ireland (`centralbank.ie`)
    - Department of Housing, Local Government and Heritage (`gov.ie/housing`)
    - Residential Tenancies Board (`rtb.ie`)
    - Property Services Regulatory Authority (`psr.ie`)
    - Central Statistics Office (`cso.ie` - Residential Property Price Index, Planning Permissions)
    - Property Price Register (`propertypriceregister.ie`)
    - Housing Agency (`housingagency.ie`)
  - **First-Time Buyer & Support Schemes**:
    - First Home Scheme (`firsthomescheme.ie`)
    - Revenue Commissioners (`revenue.ie` - Help to Buy Scheme guidelines)
    - Local Authority Home Loan (`localauthorityhomeloan.ie`)
    - Citizens Information (`citizensinformation.ie` - Housing & Mortgages)
  - **Banking & Lending Landscape**:
    - Banking & Payments Federation Ireland (`bpfi.ie` - Mortgage approvals, drawdowns, market monitors)
    - Key pillar banks & non-bank lenders (AIB, Bank of Ireland, PTSB, Avant Money, Haven, ICS)
  - **Market & Research Reports**:
    - Daft.ie Rental & Sales Reports (`daft.ie/report`)
    - MyHome.ie Property Reports
    - Society of Chartered Surveyors Ireland (`scsi.ie`)
    - ESRI (`esri.ie`)

### 2. Information Extraction Schema
Each indexed document must strictly capture:
| Field | Description |
| :--- | :--- |
| `url` & `source_org` | Origin URL and authoritative entity |
| `publication_date` | Official publication/update timestamp |
| `retrieval_date` | Timestamp when captured |
| `category` | One of the 12 defined intelligence domains |
| `key_facts` & `statistics` | Verified numeric and factual points (no synthetic data) |
| `geographic_relevance` | National, Dublin, commuter counties, regional |
| `target_audience` | First-time buyers, movers, switchers, investors, policy makers |
| `version_delta` | Granular diff from previous crawl (ignoring styling/nav changes) |

### 3. HomePilot Strategic Assessment (0–100 Scoring)
Score weighted against the 5 strategic pillars:
1. **Uncertainty Reduction** (Clearing confusion around policy, fees, or timeline).
2. **Financial Confidence** (Clarity on deposits, borrowing limits, stress tests).
3. **Decision Making** (Actionable timing, location, or scheme selection).
4. **Financial Outcomes** (Saving money, avoiding penalties, maximizing grants).
5. **Journey Support** (Solving friction points between saving, approval, and closing).

### 4. Strategic Interpretation & Content Translation
For findings scoring above threshold (e.g., $\ge 70$):
* Automatically answers the **10 Strategic Questions**:
  1. What happened?
  2. Why does it matter?
  3. Who is affected?
  4. What customer problem does it address?
  5. How does it link to HomePilot?
  6. Which product feature/calculator solves this?
  7. Does it bolster an existing campaign?
  8. Does it create a new opportunity?
  9. What is the urgency / time sensitivity?
  10. What extra corroborating evidence is needed?
* Formats content outputs (X/Twitter insights, educational carousels, campaign briefs, founder talking points) held for human sign-off.

---

## Recommended Next Steps

1. **Source Registry Definition**: Formalize `sources.json` or `sources.yaml` with crawl frequencies, seed URLs, and parser types.
2. **Tooling & Tech Stack Setup**: Select the execution framework (e.g., Python crawler with BeautifulSoup/Playwright/Scrapy, SQLite/PostgreSQL/JSON metadata store, and LLM extraction pipelines).
3. **Pilot Crawl & Extraction**: Run an initial extraction test on high-priority sources (e.g., BPFI monthly mortgage report and Central Bank macroprudential rules) to validate the extraction & scoring schema.
