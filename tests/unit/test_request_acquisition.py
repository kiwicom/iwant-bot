import pytest

from iwant_bot import request_acquisition
from iwant_bot import storage


@pytest.fixture
def pipeline():
    pipeline = request_acquisition.RequestPreprocessingPipeline()
    return pipeline


def add_notifier(pipeline, list_container):
    block = request_acquisition.Notifier()
    block.append_callback(lambda req: list_container.append(req))
    pipeline.add_block('activity', block)


def add_breaker(pipeline):
    block = request_acquisition.Breaker()
    pipeline.add_block('activity', block)


def add_noop(pipeline):
    block = request_acquisition.PassThrough()
    pipeline.add_block('activity', block)


def add_uid_assigner(pipeline):
    block = request_acquisition.UIDAssigner()
    pipeline.add_block('activity', block)


def add_requests_saver(pipeline, req_storage):
    block = request_acquisition.Saver(req_storage)
    pipeline.add_block('activity', block)


def add_requests_canceller(pipeline, req_storage):
    block = request_acquisition.Canceller(req_storage)
    pipeline.add_block('cancel', block)


def test_notifier(pipeline):
    requests = []
    add_notifier(pipeline, requests)
    pipeline.add_activity_request('john', 'coffee', 5)
    assert len(requests) == 1
    assert requests[0].person_id == 'john'


def test_breaker(pipeline):
    requests = []
    add_noop(pipeline)
    add_breaker(pipeline)
    add_notifier(pipeline, requests)
    pipeline.add_activity_request('john', 'coffee', 5)
    assert len(requests) == 0


def test_uid_assigner(pipeline):
    requests = []
    add_uid_assigner(pipeline)
    add_notifier(pipeline, requests)
    pipeline.add_activity_request('john', 'coffee', 5)
    pipeline.add_activity_request('john', 'coffee', 5)
    assert requests[0].id != requests[1].id


def test_saver(pipeline):
    req_storage = storage.MemoryRequestsStorage()
    add_requests_saver(pipeline, req_storage)
    pipeline.add_activity_request('john', 'coffee', 5)
    assert req_storage.get_activity_requests()[0].person_id == 'john'


def test_canceller(pipeline):
    req_storage = storage.MemoryRequestsStorage()
    add_uid_assigner(pipeline)

    add_requests_saver(pipeline, req_storage)
    add_requests_canceller(pipeline, req_storage)

    requests_cancelled = []
    add_cancelled_requests_notifier(pipeline, requests_cancelled)

    requests_not_cancelled = []
    add_not_cancelled_requests_notifier(pipeline, requests_not_cancelled)

    pipeline.add_activity_request('john', 'coffee', 5)
    assert len(req_storage.get_activity_requests()) == 1

    id_to_cancel = req_storage.get_activity_requests()[0].id
    pipeline.add_cancellation_request('john', id_to_cancel)

    assert len(req_storage.get_activity_requests()) == 0
    assert len(requests_cancelled) == 1
    assert len(requests_not_cancelled) == 0

    pipeline.add_cancellation_request('john', id_to_cancel)

    assert len(req_storage.get_activity_requests()) == 0
    assert len(requests_cancelled) == 1
    assert len(requests_not_cancelled) == 1
