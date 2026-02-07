"""Celery configuration for Synch-Manager async tasks."""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('synch_manager')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Periodic task schedule for polling and resilience checks
app.conf.beat_schedule = {
    'poll-all-network-elements': {
        'task': 'apps.inventory.tasks.poll_all_nes',
        'schedule': 60.0,  # every 60 seconds
    },
    'collect-performance-metrics': {
        'task': 'apps.performance.tasks.collect_metrics',
        'schedule': 30.0,  # every 30 seconds
    },
    'gnss-resilience-check': {
        'task': 'core.gnss_resilience.check_gnss_health',
        'schedule': 10.0,  # every 10 seconds for fast failover
    },
    'compute-sync-mesh-score': {
        'task': 'core.sync_mesh_score.compute_mesh_score',
        'schedule': 30.0,
    },
    'cleanup-old-performance-data': {
        'task': 'apps.performance.tasks.cleanup_old_data',
        'schedule': crontab(hour=2, minute=0),  # daily at 2 AM
    },
}
