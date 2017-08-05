from __future__ import absolute_import
from celery import Celery
import iwant_bot.pipeline

_check_storage_interval = 30.0      # seconds
store = iwant_bot.pipeline.choose_correct_store()

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
    f'check_every_{_check_storage_interval}_seconds': {
        'task': 'iwant_bot.start.storage_checker',
        'schedule': _check_storage_interval,
        'args': (store, )
    }
}
