#!/usr/bin/env python3
"""Command Line Interface for the HomePilot Market Intelligence Engine."""

import sys
import argparse
import json
from src.pipeline.runner import MarketIntelligencePipeline
from src.storage.repository import IntelligenceRepository
from src.intelligence.research_engine import ObjectiveResearchEngine
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
        print(run.consolidated_report_markdown[:600] + "...\n")

    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
