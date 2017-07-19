from __future__ import absolute_import
from celery import Celery

worker = Celery('iwant_bot_celery_worker',
                broker='redis://redis:6379/0',
                backend='redis://redis:6379/0'
               )

worker.conf.update(
                    enable_utc=True,
                    broker_use_ssl=False,
                    timezone='Europe/Prague',
                    worker_concurrency=6,
                    imports=['bot_worker.tasks', 'iwant_bot.pool'],
                  )
worker.conf.beat_schedule = {
    # 'check_every_30_seconds': {
    #    'task': 'iwant_bot.pool.make_groups',
    #    'schedule': 30.0,
    # }
}
