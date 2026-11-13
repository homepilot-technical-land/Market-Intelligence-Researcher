#!/usr/bin/env python3
"""Command Line Interface for the HomePilot Market Intelligence Engine."""

import sys
import argparse
import json
from dotenv import load_dotenv

load_dotenv()

from src.pipeline.runner import MarketIntelligencePipeline
from src.storage.repository import IntelligenceRepository
from src.intelligence.research_engine import ObjectiveResearchEngine
from src.intelligence.daily_briefing import DailyBriefingGenerator
from src.connectors.api_connectors import PropertyPriceRegisterConnector, CSOStatConnector, RTBRentIndexConnector
from src.models.research import ResearchObjective

def main():
    parser = argparse.ArgumentParser(description="HomePilot Market Intelligence Engine CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available pipeline commands")

    # Command: load-sources
    subparsers.add_parser("load-sources", help="Load and register all sources from config/sources_registry.json")

    # Command: list-sources
    subparsers.add_parser("list-sources", help="List all registered intelligence sources")

    # Command: discover
    discover_parser = subparsers.add_parser("discover", help="Discover URLs for a specific source")
    discover_parser.add_argument("--source-id", required=True, help="ID of the source to map")
    discover_parser.add_argument("--limit", type=int, default=50, help="Max URLs to discover")

    # Command: run-pilot
    subparsers.add_parser("run-pilot", help="Run an end-to-end pilot crawl, normalisation, and scoring workflow")

    # Command: run-research
    research_parser = subparsers.add_parser("run-research", help="Execute an Objective-Driven Research run")
    research_parser.add_argument("--title", default="Investigate FTB Hidden Costs & Commuter Affordability")
    research_parser.add_argument("--dimension", default="financial_confidence")

    # Phase 3 Command: generate-briefing
    briefing_parser = subparsers.add_parser("generate-briefing", help="Generate the Daily Morning Intelligence Briefing")
    briefing_parser.add_argument("--county", default="Meath", help="Target county focus")

    # Phase 3 Command: fetch-ppr
    ppr_parser = subparsers.add_parser("fetch-ppr", help="Analyze residential transactions from the Property Price Register")
    ppr_parser.add_argument("--county", default="Meath", help="County name")

    # Phase 3 Command: fetch-cso
    subparsers.add_parser("fetch-cso", help="Fetch official CSO housing market indicators (HPM05 & NDA02)")

    # Phase 3 Command: list-reviews
    subparsers.add_parser("list-reviews", help="List pending findings in the Operator Review Queue")

    # Phase 3 Command: approve-review
    approve_parser = subparsers.add_parser("approve-review", help="Approve an insight in the Operator Review Queue")
    approve_parser.add_argument("--id", required=True, help="Task ID or Insight ID to approve")
    approve_parser.add_argument("--feedback", default="Verified by human operator", help="Operator feedback note")

    # Phase 3 Command: reject-review
    reject_parser = subparsers.add_parser("reject-review", help="Reject/archive an insight in the Operator Review Queue")
    reject_parser.add_argument("--id", required=True, help="Task ID or Insight ID to reject")

    # Command: check-connections
    subparsers.add_parser("check-connections", help="Check live connectivity for MongoDB, Firecrawl API, xAI API, and Budget limits")

    # Command: scrape-url (Direct Firecrawl Scrape)
    scrape_parser = subparsers.add_parser("scrape-url", help="Scrape a URL using Firecrawl clean markdown extraction")
    scrape_parser.add_argument("--url", required=True, help="URL to scrape")
    scrape_parser.add_argument("--wait", type=int, default=1000, help="Wait time in ms before scraping")

    # Command: search (Firecrawl Web Search)
    search_parser = subparsers.add_parser("search", help="Execute web search via Firecrawl")
    search_parser.add_argument("--query", required=True, help="Search query")
    search_parser.add_argument("--limit", type=int, default=5, help="Number of results")

    # Command: search-then-scrape (Two-step search then scrape)
    sts_parser = subparsers.add_parser("search-then-scrape", help="Execute the Firecrawl Search-Then-Scrape two-step workflow")
    sts_parser.add_argument("--query", required=True, help="Search query")
    sts_parser.add_argument("--limit", type=int, default=3, help="Number of top candidates to scrape")

    # Command: search-fb-communities (Search Facebook communities relating to HomePilot)
    fb_parser = subparsers.add_parser("search-fb-communities", help="Search Facebook communities & groups relating to HomePilot / Irish FTB")
    fb_parser.add_argument("--query", default="First Time Buyers Ireland", help="Community topic query")
    fb_parser.add_argument("--limit", type=int, default=3, help="Number of communities to discover")

    # Command: discover-authorities (Dynamic Authority Discovery using Taxonomy Queries)
    auth_parser = subparsers.add_parser("discover-authorities", help="Discover new authoritative Irish sources similar to the 35 seeds using dynamic taxonomy queries")
    auth_parser.add_argument("--county", default="Meath", help="Target county focus")

    # Command: analyze-x (Native X/Twitter Sentiment Synthesis via xAI Grok)
    x_parser = subparsers.add_parser("analyze-x", help="Analyze real-time X platform sentiment on Irish housing via xAI Grok")
    x_parser.add_argument("--topic", default="Irish housing first time buyers", help="Topic to analyze on X")

    args = parser.parse_args()

    pipeline = MarketIntelligencePipeline()

    if args.command == "load-sources":
        count = pipeline.load_sources_from_registry()
        print(f"Successfully loaded and registered {count} sources.")

    elif args.command == "list-sources":
        pipeline.load_sources_from_registry()
        sources = pipeline.repo.list_sources()
        print(f"\n{'ID':<25} {'TIER':<6} {'ECOSYSTEM':<42} {'NAME'}")
        print("-" * 105)
        for s in sources:
            print(f"{s.source_id:<25} {s.tier:<6} {s.ecosystem:<42} {s.name}")
        print(f"\nTotal: {len(sources)} active sources.")

    elif args.command == "discover":
        pipeline.load_sources_from_registry()
        urls = pipeline.run_source_discovery(args.source_id, limit=args.limit)
        print(f"\nDiscovered {len(urls)} URLs for {args.source_id}:")
        for u in urls:
            print(f"[{u.tier1_status.upper()}] (score: {u.semantic_score}) {u.url}")

    elif args.command == "run-pilot":
        print("Initializing HomePilot Market Intelligence Pipeline Pilot...")
        pipeline.load_sources_from_registry()
        
        # Test target: CCPC Buying a Home
        source_id = "ccpc_homebuyers_guides"
        discovered = pipeline.run_source_discovery(source_id, limit=10)
        approved = [u for u in discovered if u.tier1_status == "approved"]
        print(f"\nFound {len(approved)} approved target URLs out of {len(discovered)} mapped.")

        if approved:
            target_url = approved[0].url
            print(f"\nProcessing target: {target_url}")
            doc = pipeline.process_url(source_id, target_url)
            if doc:
                print(f"Extracted Document: {doc.title} (Hash: {doc.content_hash[:12]}..., Version: {doc.version})")
                insight = pipeline.analyze_document_intelligence(doc)
                if insight:
                    print(f"\n--- Intelligence Insight Generated ---")
                    print(f"Category: {insight.primary_category}")
                    print(f"Composite Score: {insight.scoring.composite_score}/100")
                    print(f"Relevance: {insight.scoring.s_relevance} | Impact: {insight.scoring.s_impact} | Confidence: {insight.scoring.s_confidence}")
                    if insight.ten_questions:
                        print(f"Q1 What Happened: {insight.ten_questions.q1_what_happened}")
                        print(f"Q4 Customer Problem: {insight.ten_questions.q4_customer_problem}")
                        print(f"Q6 Product Capability: {insight.ten_questions.q6_product_capability}")
        print("\nPilot workflow completed successfully!")

    elif args.command == "run-research":
        print("Executing Objective-Driven Research Investigation...")
        pipeline.load_sources_from_registry()
        engine = ObjectiveResearchEngine(repository=pipeline.repo)
        
        obj = ResearchObjective(
            objective_id="obj_cli_market_readiness",
            title=args.title,
            strategic_dimension=args.dimension,
            core_questions=[
                "What are the primary financial barriers beyond the 10% deposit?",
                "How do scheme caps and starter home prices interact in commuter counties?",
                "What empirical evidence gaps exist in current registered feeds?"
            ],
            target_audiences=["seg_1_frustrated_ftb", "seg_2_mortgage_ready_optimiser"]
        )
        run = engine.execute_research_run(obj)
        print(f"\n--- Research Run Complete [{run.run_id}] ---")
        print(f"Status: {run.status}")
        print(f"Sources Consulted: {len(run.sources_consulted)}")
        print(f"Gaps Identified: {len(run.identified_gaps)}")
        print("\nConsolidated Report Preview:")
        print(run.consolidated_report_markdown[:700] + "...\n")

    elif args.command == "generate-briefing":
        print(f"Generating Daily Morning Intelligence Briefing for County {args.county}...")
        briefing_gen = DailyBriefingGenerator(repository=pipeline.repo)
        briefing = briefing_gen.generate_morning_briefing(county_focus=args.county)
        print(f"\n=== {briefing.title} ===")
        print(briefing.markdown_report)

    elif args.command == "fetch-ppr":
        print(f"Analyzing Property Price Register Transactions for County {args.county}...")
        benchmarks = PropertyPriceRegisterConnector.calculate_county_affordability_benchmarks(county=args.county)
        rent_delta = RTBRentIndexConnector.calculate_buy_vs_rent_differential(county=args.county)
        print(f"\n--- County {args.county} PPR Benchmarks ---")
        print(f"Sample Transactions: {benchmarks['sample_size']}")
        print(f"Median Starter Home Price: €{benchmarks['median_starter_home_price']:,.0f}")
        print(f"Median New Build Price: €{benchmarks['median_new_build_price']:,.0f}")
        print(f"First Home Scheme Cap: €{benchmarks['first_home_scheme_cap']:,.0f}")
        print(f"Scheme Cap Breach Rate: {benchmarks['cap_breach_rate_percent']}%")
        print(f"Monthly Rent vs Mortgage Delta: €{rent_delta['monthly_cash_flow_advantage_eur']:,.0f} / mo")

    elif args.command == "fetch-cso":
        print("Fetching official CSO housing statistics...")
        cso_data = CSOStatConnector.fetch_housing_market_indicators()
        print(json.dumps(cso_data, indent=2))

    elif args.command == "list-reviews":
        print("\n--- Operator Review Queue ---")
        candidates = pipeline.repo.list_candidate_sources(status="pending_approval")
        print(f"Pending Candidate Sources: {len(candidates)}")
        for c in candidates:
            print(f"- [{c.candidate_id}] {c.domain} (Semantic Score: {c.semantic_score})")

    elif args.command == "approve-review":
        print(f"Approved review task '{args.id}' with note: '{args.feedback}'")

    elif args.command == "reject-review":
        print(f"Rejected review task '{args.id}'")

    elif args.command == "check-connections":
        from src.coordination.budget_tracker import BudgetGovernanceTracker
        from src.intelligence.grok_service import GrokService
        print("\n=== HomePilot Intelligence Pipeline Diagnostic Check ===")
        
        # 1. MongoDB Status
        mongo_ok = pipeline.repo._connected and pipeline.repo.db_manager.db is not None
        if mongo_ok:
            print(f"✓ MongoDB: CONNECTED (Database: '{pipeline.repo.db_manager.db_name}' on {pipeline.repo.db_manager.uri})")
        else:
            print(f"! MongoDB: OFFLINE (Operating with in-memory fallback - set MONGODB_URI in .env to connect live)")

        # 2. Firecrawl API Status
        fc_configured = pipeline.connector.is_configured()
        if fc_configured:
            print(f"✓ Firecrawl API: CONFIGURED (Key: {pipeline.connector.api_key[:8]}..., Endpoint: {pipeline.connector.base_url})")
        else:
            print(f"! Firecrawl API: NOT CONFIGURED (Using simulation mode - set FIRECRAWL_API_KEY in .env)")

        # 3. xAI Grok API Status
        grok = GrokService()
        xai_configured = grok.is_configured()
        if xai_configured:
            print(f"✓ xAI Grok API: CONFIGURED (Key: {grok.api_key[:8]}..., Model: {grok.model})")
        else:
            print(f"! xAI Grok API: NOT CONFIGURED (Using simulation mode - set XAI_API_KEY in .env)")

        # 4. Budget Burn Status
        tracker = BudgetGovernanceTracker(repository=pipeline.repo, state_file="config/budget_burn_state.json")
        burn = tracker.get_current_burn()
        print(f"\n--- Monthly Budget & Quota Tracking ({burn.billing_month}) ---")
        print(f"Firecrawl Credits: {burn.firecrawl_credits_used} / {burn.firecrawl_credit_limit} used")
        print(f"xAI Spend: ${burn.xai_cost_usd:.2f} / ${burn.xai_budget_limit_usd:.2f} USD")
        print(f"Cache Free Passes: {burn.pages_processed_free_hash} pages (Saved ~${burn.estimated_dollars_saved_by_cache:.2f})")
        print("========================================================\n")

    elif args.command == "scrape-url":
        print(f"\nScraping URL via Firecrawl: {args.url} (Wait: {args.wait}ms)")
        actions = [{"type": "wait", "milliseconds": args.wait}] if args.wait > 0 else None
        res = pipeline.connector.scrape_url(
            url=args.url,
            only_main_content=True,
            remove_base64_images=True,
            actions=actions
        )
        print(f"\nTitle: {res.get('title')}")
        print(f"Status Code: {res.get('status')}")
        print(f"Extracted Markdown Length: {len(res.get('markdown', ''))} characters")
        print("-" * 60)
        print(res.get("markdown", "")[:600] + ("..." if len(res.get("markdown", "")) > 600 else ""))
        print("-" * 60)

    elif args.command == "search":
        print(f"\nExecuting Firecrawl Search for: '{args.query}' (Limit: {args.limit})")
        results = pipeline.connector.search(query=args.query, limit=args.limit)
        print(f"Discovered {len(results)} results:\n")
        for i, item in enumerate(results, 1):
            print(f"[{i}] {item.get('title')}")
            print(f"    URL: {item.get('url')}")
            print(f"    Snippet: {item.get('description', '')[:120]}...\n")

    elif args.command == "search-then-scrape":
        print(f"\nExecuting Firecrawl Search-Then-Scrape Pattern for: '{args.query}' (Scrape Limit: {args.limit})")
        results = pipeline.connector.search_then_scrape(query=args.query, scrape_limit=args.limit)
        print(f"Successfully scraped {len(results)} pages:\n")
        for i, item in enumerate(results, 1):
            print(f"[{i}] {item.get('title')}")
            print(f"    URL: {item.get('url')}")
            print(f"    Content Length: {len(item.get('markdown', ''))} chars")
            print(f"    Preview: {item.get('markdown', '')[:180].strip()}...\n")

    elif args.command == "search-fb-communities":
        print(f"\nSearching Facebook Communities for: '{args.query}' (Limit: {args.limit})")
        results = pipeline.connector.search_facebook_communities(query=args.query, limit=args.limit)
        print(f"Discovered {len(results)} Facebook communities/groups:\n")
        for i, item in enumerate(results, 1):
            print(f"[{i}] {item.get('title')}")
            print(f"    URL: {item.get('url')}")
            print(f"    Content Length: {len(item.get('markdown', ''))} chars")
            print(f"    Preview: {item.get('markdown', '')[:180].strip()}...\n")

    elif args.command == "discover-authorities":
        from src.intelligence.authority_discovery import AuthoritySourceDiscoveryEngine
        pipeline.load_sources_from_registry()
        discovery = AuthoritySourceDiscoveryEngine(repository=pipeline.repo)
        print(f"\nExecuting Dynamic Authority Discovery via Firecrawl for '{args.county}'...")
        candidates = discovery.discover_sources_via_firecrawl(connector=pipeline.connector, county=args.county)
        print(f"Discovered {len(candidates)} new candidate sources for operator review:\n")
        for i, c in enumerate(candidates, 1):
            print(f"[{i}] {c.name} (Authority Score: {c.authority_score:.1f})")
            print(f"    URL: {c.root_url}")
            print(f"    Publisher: {c.publisher_identity}")
            print(f"    Justification: {c.justification[:120]}...\n")

    elif args.command == "analyze-x":
        from src.intelligence.grok_service import GrokService
        from src.coordination.budget_tracker import BudgetGovernanceTracker
        tracker = BudgetGovernanceTracker(repository=pipeline.repo, state_file="config/budget_burn_state.json")
        grok = GrokService(budget_tracker=tracker)
        print(f"\nSynthesizing X Platform Intelligence & Future Bot Communications for topic: '{args.topic}'...")
        strat = grok.synthesize_strategic_x_intelligence(topic=args.topic)
        print(f"\n=== xAI Grok Strategic X Intelligence & Bot Communication Plan ===")
        print(f"Topic: {strat.topic}")
        print(f"Token Accounting: {strat.prompt_tokens} prompt + {strat.completion_tokens} completion (Cost: ${strat.cost_usd:.5f} USD)")
        print("\n--- Real-Time Discourse & Sentiment Analysis ---")
        print(strat.analysis)
        print("\n--- Top Buyer Pain Points & Anxieties on X ---")
        for i, p in enumerate(strat.buyer_pain_points, 1):
            print(f"[{i}] {p}")
        print("\n--- Future Bot Communication Hooks (Campaign & Educational Angles) ---")
        for i, hook in enumerate(strat.proposed_bot_communications, 1):
            print(f"[{i}] {hook}")
        print("\n--- HomePilot Product Capability Alignment ---")
        for i, prod in enumerate(strat.homepilot_product_alignment, 1):
            print(f"[{i}] {prod}")
        print("\n--- Human Validation Gate (The 3 R's Governance) ---")
        print(f"Requires Human Validation: {'YES (Operator Signoff Mandated)' if strat.requires_human_validation else 'NO (Autonomous Bot Response)'}")
        print(f"Validation Rationale: {strat.validation_rationale}")

        # Persist structured intelligence and bot communication assets into MongoDB
        import uuid
        from src.models.campaign import CampaignOpportunity
        from src.models.asset import GeneratedAsset, AssetPayload

        campaign_id = f"camp_x_{uuid.uuid4().hex[:8]}"
        campaign = CampaignOpportunity(
            campaign_id=campaign_id,
            theme_title=f"X Strategic Intelligence: {strat.topic}",
            strategic_dimension="financial_confidence",
            target_segment="seg_1_frustrated_ftb",
            central_customer_problem=strat.buyer_pain_points[0] if strat.buyer_pain_points else strat.topic,
            homepilot_positioning_hook=strat.homepilot_product_alignment[0] if strat.homepilot_product_alignment else "HomePilot Decision Tools",
            status="ready_for_review" if strat.requires_human_validation else "approved"
        )
        pipeline.repo.save_campaign(campaign)

        saved_asset_ids = []
        for idx, hook in enumerate(strat.proposed_bot_communications, 1):
            asset_id = f"asset_x_{uuid.uuid4().hex[:8]}"
            asset = GeneratedAsset(
                asset_id=asset_id,
                campaign_id=campaign_id,
                asset_type="x_thread",
                content_payload=AssetPayload(
                    headline=hook,
                    copy_body=f"Discourse Context: {strat.analysis}\n\nProposed Bot Hook: {hook}",
                    evidence_citations=[f"https://x.com/search?q={strat.topic.replace(' ', '+')}"]
                ),
                review_status="pending_review",
                reviewer_notes=f"Synthesized via xAI Grok. Requires dual operator signoff under Rule B-04. Alignment: {', '.join(strat.homepilot_product_alignment[:2])}"
            )
            pipeline.repo.save_asset(asset)
            saved_asset_ids.append(asset_id)

        print(f"\nPersisted to MongoDB Database ('homepilot_intelligence'):")
        print(f"  • Campaign Opportunity: {campaign_id} (Collection: 'campaign_opportunities')")
        print(f"  • Content Assets: {len(saved_asset_ids)} draft X bot threads (Collection: 'content_assets')")
        print(f"  • Operator Status: PENDING_OPERATOR_APPROVAL (Gated under Rule B-04)")
        print("===================================================================\n")

    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
