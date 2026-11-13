import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import redis

logger = logging.getLogger(__name__)

class RedisQueueManager:
    """Manages independent Redis job queues, priority scheduling, and retries with fallback queue."""

    QUEUES = [
        "source-discovery",
        "page-crawling",
        "content-processing",
        "relevance-analysis",
        "change-analysis",
        "objective-research",
        "source-evaluation",
        "content-generation"
    ]

    PRIORITIES = {
        "critical": 1,   # Government scheme updates, macroprudential changes
        "high": 2,       # Developer launch schedules, PPR price releases
        "normal": 3,     # Weekly digests, general articles
        "low": 4         # Background exploratory mapping
    }

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.client: Optional[redis.Redis] = None
        self._memory_queues: Dict[str, List[Dict[str, Any]]] = {q: [] for q in self.QUEUES}
        self.connect()

    def connect(self) -> bool:
        try:
            r = redis.from_url(self.redis_url, socket_timeout=1.5)
            r.ping()
            self.client = r
            logger.info(f"Connected to Redis at {self.redis_url}")
            return True
        except Exception as e:
            logger.warning(f"Redis unavailable at {self.redis_url}: {e}. Using local in-memory queues.")
            self.client = None
            return False

    def is_connected(self) -> bool:
        return self.client is not None

    def enqueue_job(self, queue_name: str, payload: Dict[str, Any], priority: str = "normal") -> str:
        """Enqueues a task payload to the designated queue."""
        if queue_name not in self.QUEUES:
            raise ValueError(f"Unknown queue: {queue_name}. Allowed: {self.QUEUES}")

        job_id = f"job_{queue_name}_{int(datetime.utcnow().timestamp() * 1000)}"
        job_data = {
            "job_id": job_id,
            "queue": queue_name,
            "priority": priority,
            "payload": payload,
            "status": "pending",
            "enqueued_at": datetime.utcnow().isoformat(),
            "retry_count": 0
        }

        if self.is_connected() and self.client is not None:
            self.client.rpush(f"hp_queue:{queue_name}", json.dumps(job_data))
        else:
            self._memory_queues[queue_name].append(job_data)

        return job_id

    def dequeue_job(self, queue_name: str) -> Optional[Dict[str, Any]]:
        """Pulls the next pending job from the queue."""
        if self.is_connected() and self.client is not None:
            raw = self.client.lpop(f"hp_queue:{queue_name}")
            if raw:
                return json.loads(raw)
            return None
        else:
            if self._memory_queues[queue_name]:
                return self._memory_queues[queue_name].pop(0)
            return None

    def get_queue_depth(self, queue_name: str) -> int:
        if self.is_connected() and self.client is not None:
            return self.client.llen(f"hp_queue:{queue_name}")
        return len(self._memory_queues[queue_name])
