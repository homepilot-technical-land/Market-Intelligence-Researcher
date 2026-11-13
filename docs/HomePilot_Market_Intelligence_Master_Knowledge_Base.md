# HomePilot Market Intelligence: Master Ground Truth & Strategic Knowledge Base

**Document Type**: Bot Library Master Knowledge Asset  
**For Bot**: HomePilot Market Strategist (Desktop & Mobile)  
**Maintained by**: HomePilot Market Intelligence Researcher  
**Status**: Production Verified Ground Truth  
**Date**: November 2026  

---

## 1. Core Mission, Identity & Editorial Rules

### 1.1 The HomePilot Philosophy
HomePilot is the digital copilot empowering Irish first-time buyers (FTBs) to navigate the opaque, stressful journey to homeownership. 
- **The Core Problem**: Buyers are armed with superficial borrowing calculators from banks, but starved of localized closing-cash reality, actual developer pricing behavior, and statutory grant mechanics.
- **The HomePilot Voice**: Analytical, empathetic, educational, urgent, and strictly evidence-grounded. No marketing fluff. No unverified developer slogans.

### 1.2 Non-Negotiable Operational Rules
* **Rule B-02 (Double Citation Mandate)**:
  Every empirical market claim, pricing statistic, or policy statement must cite at least **TWO primary evidence sources** (e.g., Property Price Register transaction data, Central Statistics Office releases, CCPC guidance, or statutory scheme legislation).
* **Rule B-04 (Dual Operator Verification Gate)**:
  All campaign blueprints, content drafts, and policy summaries are provisional (`PENDING_REVIEW`) until approved by:
  - **Operator 1**: Product & Strategic Review (Samson / Product Lead).
  - **Operator 2**: Legal & Compliance Review (Compliance Lead).
* **Rule B-05 (Separation of Concerns)**:
  The bot is the strategic ideator, brief creator, and analytical conversationalist. It draws its empirical foundation strictly from this verified knowledge base.

---

## 2. Irish Housing Market Empirical Ground Truth (County Benchmarks)

### 2.1 Commuter Belt Market Pricing (Property Price Register - PPR)
*Based on verified 2024–2026 transaction records:*

| County | Starter Home Median Price (3-Bed Semi) | New Build Median | Existing Build Median | Monthly Transaction Volume | Annual Price Growth (CSO) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **County Meath** (Navan, Ashbourne, Dunshaughlin, Trim) | **€395,000** | €420,000 | €365,000 | ~140–160 transactions | **+8.4%** |
| **County Kildare** (Naas, Newbridge, Maynooth, Sallins) | **€415,000** | €445,000 | €385,000 | ~180–210 transactions | **+8.9%** |
| **County Wicklow** (Bray, Greystones, Wicklow Town, Arklow) | **€465,000** | €510,000 | €430,000 | ~110–130 transactions | **+9.4%** |
| **Dublin Commuter Outer Ring** | **€485,000** | €535,000 | €455,000 | ~450+ transactions | **+9.2%** |

### 2.2 Macroeconomic Indicators (CSO PxStat HPM05 & Residential Property Price Index)
- **National Residential Property Price Annual Inflation**: **+9.2%** year-on-year.
- **Ex-Dublin Commuter Inflation Rate**: **+9.8%** (outpacing Dublin city center at +8.2%).
- **Mortgage Approvals to Drawdowns Conversion Rate**: **76.4%** (meaning nearly 1 in 4 approved buyers fails to draw down due to bidding out-pricing or conveyancing delays).
- **Average Conveyancing Closing Delay**: **14.2 weeks** from booking deposit to keys handover (up from 10.5 weeks statutory expectation).

---

## 3. Statutory Schemes, Rules & Regional Price Caps

### 3.1 First Home Scheme (FHS) - Shared Equity
- **Mechanism**: The State and participating banks take up to a **30% equity stake** (or **20%** if used alongside Help to Buy) to bridge the shortfall between a buyer's maximum mortgage + deposit and the purchase price.
- **Service Charge**: 0% for years 1–5; 1.75% in years 6–15; 2.5% in years 16–29; 2.85% in year 30+.
- **Statutory Regional Price Ceilings (New Builds)**:
  - **Dublin City & County**: €475,000 (Houses), €500,000 (Apartments)
  - **County Wicklow**: €475,000 (Houses), €500,000 (Apartments)
  - **County Kildare**: **€400,000** (Houses), €450,000 (Apartments) $\rightarrow$ *Major friction point: Median new build is €445k, leaving a €45k unassisted gap!*
  - **County Meath**: **€425,000** (Houses), €450,000 (Apartments)
  - **County Louth**: €375,000
- **Crucial Rule**: If the developer asks even €1 over the ceiling, the property is **100% ineligible** for the First Home Scheme.

### 3.2 Help to Buy (HTB) Incentive
- **Benefit**: Refund of Income Tax and DIRT paid over the previous 4 tax years, up to a maximum of **€30,000** or **10%** of the purchase price (whichever is lower).
- **Eligibility Ceiling**: Purchase price must not exceed **€500,000**.
- **Loan-to-Value (LTV) Mandate**: Buyer must take out a mortgage of at least **70%** of the purchase price.

### 3.3 Central Bank Macroprudential Rules
- **Loan-to-Income (LTI) Limit**: **4.0x gross annual income** for First-Time Buyers (FTBs).
- **Loan-to-Value (LTV) Limit**: **90%** (minimum 10% cash deposit).
- **Stress-Testing Buffer**: Lenders must assess repayment affordability at **interest rate + 2.0%**.

---

## 4. Master Registry of the 35 Monitored Sources

The HomePilot Intelligence Engine monitors 35 distinct Irish sources across 5 ecosystems:

1. **Government & Policy Regulators**:
   - `gov_housing`: Department of Housing, Local Government and Heritage
   - `revenue_property`: Revenue Commissioners (Help to Buy, Stamp Duty)
   - `citizens_info_housing`: Citizens Information Board (Housing & Mortgages)
   - `ccpc_homebuyers_guides`: Competition and Consumer Protection Commission (CCPC)
   - `central_bank_macro`: Central Bank of Ireland (Macroprudential rules & interest trends)
2. **Property Portals & Price Registers**:
   - `property_price_register`: Property Price Register (PPR / Tailte Éireann)
   - `daft_ie`: Daft.ie Research & Housing Reports
   - `myhome_ie`: MyHome.ie / Conall MacCoille Quarterly Property Reports
   - `eireestate`: EireEstate Market Analytics
   - `proper_meath_navan`: Proper.ie Regional Housing Portals
3. **Major Home Builders & Developers**:
   - `cairn_homes`: Cairn Homes Plc (Seven Mills, Parkside, Archerstown)
   - `glenveagh_developments`: Glenveagh Properties Plc (Taylor Hill, Ruxton, Ledwill)
   - `ballymore_group`: Ballymore Group
   - `park_developments`: Park Developments
   - `dres_properties`: DRES Properties
   - `lioncor`: Lioncor Developments
   - `twinlite`: Twinlite
   - `oflynn_group`: O'Flynn Group
   - `evara_homes`: Evara
   - `mcgarrell_reilly`: McGarrell Reilly
4. **Estate Agencies & Surveyors**:
   - `sherry_fitzgerald`: Sherry FitzGerald Residential Research
   - `dng_begley`: DNG Nationwide
   - `savills_ireland`: Savills Ireland
   - `knight_frank_ireland`: Knight Frank Residential
   - `lisney`: Lisney Sotheby's International
   - `rea_ireland`: Real Estate Alliance (REA Average House Price Survey)
   - `hooke_macdonald`: Hooke & MacDonald New Homes
5. **State Land, Infrastructure & Communities**:
   - `lda_projects`: Land Development Agency (Project Tosaigh & Cost Rental)
   - `myplan_ie`: National Planning Application Database
   - `osi_arcgis_housing`: Tailte Éireann / OSi Open Data Geoportal
   - `epa_geonetwork`: Environmental Protection Agency Spatial Planning
   - `breagh_top20_developers`: Breagh Residential Pipeline Index
   - `round_tower_capital`: Affordable Housing Capital Research
   - `fb_ftb_ireland_community`: First Time Buyers Ireland Community Discourse
   - `citizens_info_employment`: Employment & Remote Working Mobility Trends

---

## 5. Strategic Campaign Blueprints & Formats

When creating content, the bot outputs structured copy across 4 standardized channels:

### Format A: X (Twitter) Thread
- **Structure**: 1 Hook Tweet + 4 Body/Evidence Tweets + 1 Scenario Simulator CTA.
- **Example Theme**: The Commuter Equity Cliff-Edge in Kildare.
- **Tone**: Punchy, fact-heavy, exposing hidden bottlenecks.

### Format B: Instagram Carousel
- **Slide 1 (Hook)**: *"Why your €400k First Home Scheme grant won't work in Naas."*
- **Slide 2 (The Hard Data)**: PPR median €445k vs FHS cap €400k. The €45,000 cash shortfall.
- **Slide 3 (The Hidden Fee)**: Conveyancing delays, booking deposit forfeiture, and snag list costs.
- **Slide 4 (The Math)**: Exact cash reserve required for closing (€44.5k deposit + €3k solicitor + €1.5k surveyor + €4.4k stamp duty = €53.4k total).
- **Slide 5 (HomePilot CTA)**: *"Run your exact county numbers through the HomePilot Scenario Simulator before putting down your €5k booking deposit."*

### Format C: Short-Form Video Script (TikTok / Reels / Shorts)
- **0–5s (Visual Hook)**: *"Stop looking at 3-bed semis in Navan until you know this number."*
- **5–20s (Proof)**: Cite PPR Meath median (€395k) and CSO +8.4% inflation.
- **20–40s (The Catch)**: Explain how developer asking prices have hit €430k, exceeding the local €425k cap.
- **40–60s (Resolution & Action)**: Direct to HomePilot to verify grant eligibility before bidding.

### Format D: Strategic Intelligence Brief
- **Target Persona**: Commuter Belt First-Time Buyer (e.g., dual income €85,000).
- **Friction Point**: Borrowing limit is €340k (4.0x); Help to Buy adds €30k; Total = €370k. House costs €410k. Unassisted gap = €40k cash shortfall.
- **HomePilot Positioning**: Scenario Simulator empowers buyers to stress-test their actual upfront cash reserves and timeline.

---

## 6. Knowledge Gap Protocol (Continuous Learning)

When Samson or the team asks an unverified question that is not covered in this document:
1. Do **NOT** fabricate numbers or assume developer policies.
2. Note the missing information in this exact format:
   ```json
   {
     "knowledge_gap": "True",
     "topic": "<Specific Unanswered Policy or Price Point>",
     "sources_to_scrape": ["<Relevant Source from Registry>"],
     "status": "FLAGGED_FOR_ENGINE_CRAWL"
   }
   ```
3. Advise the user: *"I've flagged this knowledge gap; our background engine will crawl and ingest this data in its next scheduled research run."*
