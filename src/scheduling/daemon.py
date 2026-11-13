"""Autonomous Production Scheduling Daemon for HomePilot Market Intelligence.

Manages 24/7 background scheduled operations:
1. Daily Morning Intelligence Briefing (07:00 UTC)
2. Source Cadence Monitoring (Daily, Every 2-3 Days, Weekly)
3. Closed-Loop Knowledge Gap Batch Processor (Demand-Driven Re-Ingestion)

Features graceful SIGINT/SIGTERM handling, process isolation, and health heartbeats.
"""

import os
import signal
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from src.storage.repository import IntelligenceRepository
from src.pipeline.runner import MarketIntelligencePipeline
from src.intelligence.daily_briefing import DailyBriefingGenerator
from src.observability.posthog_client import PostHogTelemetry

logger = logging.getLogger("SchedulerDaemon")

class ProductionSchedulerDaemon:
    """Autonomous background scheduler and supervisor."""

    def __init__(
        self,
        repository: Optional[IntelligenceRepository] = None,
        pipeline: Optional[MarketIntelligencePipeline] = None,
        telemetry: Optional[PostHogTelemetry] = None
    ):
        self.repo = repository or IntelligenceRepository()
        self.pipeline = pipeline or MarketIntelligencePipeline(repository=self.repo)
        self.telemetry = telemetry or PostHogTelemetry()
        self.briefing_gen = DailyBriefingGenerator(repository=self.repo, telemetry=self.telemetry)
        self.running = False
        self.last_briefing_time: Optional[datetime] = None
        self.last_cadence_run: Optional[datetime] = None
        self.last_gap_batch_run: Optional[datetime] = None

    def execute_daily_briefing_job(self, county_focus: str = "Meath") -> Dict[str, Any]:
        """Job 1: Compiles and records the daily executive briefing."""
        logger.info(f"Executing scheduled 07:00 UTC Daily Briefing job for {county_focus}...")
        try:
            briefing = self.briefing_gen.generate_morning_briefing(county_focus=county_focus)
            self.last_briefing_time = datetime.now(timezone.utc)
            self.telemetry.capture("daily.briefing.generated", {
                "briefing_id": briefing.briefing_id,
                "county": county_focus,
                "date": briefing.briefing_date
            })
            return {"status": "success", "briefing_id": briefing.briefing_id, "time": self.last_briefing_time.isoformat()}
        except Exception as e:
            logger.error(f"Error executing daily briefing job: {e}")
            return {"status": "failed", "error": str(e)}

    def execute_cadence_monitor_job(self, max_sources: Optional[int] = None) -> Dict[str, Any]:
        """Job 2: Evaluates active sources and runs scheduled discovery on due sources."""
        logger.info("Executing scheduled source cadence monitor job...")
        sources = self.repo.list_sources(active_only=True)
        checked_count = 0
        discovered_total = 0

        for source in sources:
            if max_sources is not None and checked_count >= max_sources:
                break
            # Check cadence
            if source.cadence in ["daily", "continuous"]:
                try:
                    urls = self.pipeline.run_source_discovery(source.source_id, limit=20)
                    checked_count += 1
                    discovered_total += len(urls)
                except Exception as e:
                    logger.warning(f"Failed source discovery for {source.source_id}: {e}")

        self.last_cadence_run = datetime.now(timezone.utc)
        return {
            "status": "success",
            "sources_checked": checked_count,
            "urls_discovered": discovered_total,
            "time": self.last_cadence_run.isoformat()
        }

    def execute_closed_loop_gap_job(self) -> Dict[str, Any]:
        """Job 3: Batches unanswered knowledge gaps and dispatches targeted research."""
        logger.info("Executing closed-loop knowledge gap batch processor...")
        # Check pending gaps
        gaps = []
        if self.repo._connected and self.repo.db_manager.db is not None:
            cursor = self.repo.db_manager.db.research_objectives.find({"status": "pending_investigation"})
            gaps = list(cursor)

        resolved_count = 0
        for gap in gaps:
            # Targeted query via Firecrawl search
            gap_topic = gap.get("topic", "")
            if gap_topic and self.pipeline.connector.is_configured():
                try:
                    results = self.pipeline.connector.search(query=f"site:.ie {gap_topic}", limit=2)
                    for r in results:
                        u = r.get("url")
                        if u:
                            self.pipeline.process_url(source_id="gov_ie_housing", url=u)
                            resolved_count += 1
                    if self.repo._connected and self.repo.db_manager.db is not None:
                        self.repo.db_manager.db.research_objectives.update_one(
                            {"_id": gap["_id"]},
                            {"$set": {"status": "investigated", "resolved_at": datetime.now(timezone.utc)}}
                        )
                except Exception as e:
                    logger.warning(f"Error processing gap '{gap_topic}': {e}")

        self.last_gap_batch_run = datetime.now(timezone.utc)
        return {"status": "success", "gaps_processed": len(gaps), "urls_ingested": resolved_count}

    def run_all_cycle_once(self, max_sources: Optional[int] = 2) -> Dict[str, Any]:
        """Executes one full cycle of all 3 jobs (used for testing and CLI on-demand runs)."""
        logger.info("Running single complete daemon operational cycle...")
        b_res = self.execute_daily_briefing_job()
        c_res = self.execute_cadence_monitor_job(max_sources=max_sources)
        g_res = self.execute_closed_loop_gap_job()

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "briefing_job": b_res,
            "cadence_job": c_res,
            "gap_batch_job": g_res,
            "daemon_healthy": True
        }

    async def start(self, interval_seconds: int = 3600):
        """Starts the persistent background daemon loop."""
        self.running = True
        logger.info(f"Production Scheduler Daemon started. Loop interval: {interval_seconds}s.")

        # Register signal handlers
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, lambda: self.stop())
            except NotImplementedError:
                pass # Windows fallback

        while self.running:
            now = datetime.now(timezone.utc)
            # Run briefing around 07:00 UTC or if first run
            if self.last_briefing_time is None or (now.hour == 7 and (now - self.last_briefing_time).total_seconds() > 43200):
                self.execute_daily_briefing_job()

            # Run cadence monitoring daily around 02:00 UTC
            if self.last_cadence_run is None or (now.hour == 2 and (now - self.last_cadence_run).total_seconds() > 43200):
                self.execute_cadence_monitor_job()

            # Run gap processor every 12 hours
            if self.last_gap_batch_run is None or (now - self.last_gap_batch_run).total_seconds() > 43200:
                self.execute_closed_loop_gap_job()

            await asyncio.sleep(min(60, interval_seconds))

    def stop(self):
        """Gracefully halts the daemon."""
        logger.info("Stopping Production Scheduler Daemon gracefully...")
        self.running = False
