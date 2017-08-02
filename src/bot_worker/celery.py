from __future__ import absolute_import
from celery import Celery
# from iwant_bot.start import _check_storage_interval


worker = Celery('iwant_bot_celery_worker',
                broker='redis://redis:6379/0',
                backend='redis://redis:6379/0'
                )

worker.conf.update(
    enable_utc=True,
    broker_use_ssl=False,
    worker_concurrency=6,
    timezone='Europe/Prague',
    imports=['bot_worker.tasks', 'iwant_bot.pool', 'iwant_bot.start']
)

worker.conf.beat_schedule = {
    'check_every_30_seconds': {
       'task': 'iwant_bot.start.storage_checker',
       'schedule': 30.0
       # 'schedule': _check_storage_interval,
    }
}
