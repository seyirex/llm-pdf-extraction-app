"""Celery application instance configured with Redis broker/backend."""

from celery import Celery

from src.config import settings

celery_app = Celery(
    "llm_pdf_extraction",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_expires=3600,

    # Task execution settings
    task_track_started=True,
    task_time_limit=settings.celery_task_time_limit,
    task_soft_time_limit=settings.celery_task_soft_time_limit,
    task_acks_late=True,
    task_reject_on_worker_lost=True,

    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    worker_pool_restarts=True,
    worker_send_task_events=True,

    # Broker settings
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,

    # Result backend settings
    result_backend_always_retry=True,
    result_backend_max_retries=10,

    # Queue routing — isolate document processing from future lightweight tasks
    task_routes={
        "process_pdf": {"queue": "documents"},
    },
    task_default_queue="default",
)

celery_app.autodiscover_tasks(["src.tasks.process_pdf"])
