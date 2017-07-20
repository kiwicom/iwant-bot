from __future__ import absolute_import
from .celery import worker
import time


# this is a working off-topic example of celery task
@worker.task()
def longtime_add(x, y):
    print('long time task begins')
    time.sleep(5)
    print('long time task finished')
    return x + y


for _ in range(3):
    result = longtime_add.delay(1, 2)
    print(f"Task finished? {result.ready()}")
    print(f"Task result: {result.result}")
    time.sleep(1)
    print(f"Task finished {result.ready()}")
    print(f"Task result: {result.result}")
