import pytest
from src.coordination.queue_manager import RedisQueueManager

def test_redis_queue_manager_enqueues_and_dequeues():
    qm = RedisQueueManager()
    
    # Verify independent queues
    assert len(qm.QUEUES) == 8
    assert "source-discovery" in qm.QUEUES
    assert "relevance-analysis" in qm.QUEUES
    assert "objective-research" in qm.QUEUES
    assert "source-evaluation" in qm.QUEUES

    # Enqueue critical task
    job_id = qm.enqueue_job("source-discovery", {"source_id": "cso_housing"}, priority="critical")
    assert job_id.startswith("job_source-discovery_")
    assert qm.get_queue_depth("source-discovery") >= 1

    # Dequeue task
    job = qm.dequeue_job("source-discovery")
    assert job is not None
    assert job["payload"]["source_id"] == "cso_housing"
    assert job["priority"] == "critical"
    assert qm.get_queue_depth("source-discovery") == 0
