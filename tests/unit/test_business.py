import time

from iwant_bot import business


def test_create_request():
    request = business.IWantRequest("john", "coffee", 1)
    assert request.is_active_now()
    assert not request.is_active_by(time.time() + 65)


def test_storage_saves_and_restores():
    storage = business.MemoryRequestsStorage()
    request = business.IWantRequest("john", "coffee", 0)
    storage.store_request(request)
    recovered_request = storage.get_activity_requests()[0]
    assert request == recovered_request


def make_filled_request_pool():
    storage = business.MemoryRequestsStorage()
    storage.store_request(business.IWantRequest("john", "coffee", 5))
    storage.store_request(business.IWantRequest("jane", "coffee", 5))
    storage.store_request(business.IWantRequest("olivia", "picnic", 5))
    storage.store_request(business.IWantRequest("jerry", "coffee", 0))
    pool = business.RequestsPool(storage)
    pool.update_requests_from_storage()
    return pool


def test_requests_pool_filters_relevant():
    pool = make_filled_request_pool()
    active_requests = pool.current_activities_requests
    assert len(active_requests) == 3


def test_requests_partitioning():
    pool = make_filled_request_pool()
    partitions = business.partition_requests(pool.current_activities_requests)
    assert len(partitions) == 2
    assert len(partitions["coffee"]) == 2
    assert partitions["picnic"][0].person_id == "olivia"


def test_request_cancel():
    pool = make_filled_request_pool()
    storage = pool._requests_storage

    cancel_picnic = business.ICancelRequest("olivia", "picnic", 2)
    storage.store_request(cancel_picnic)
    pool.update_requests_from_storage()
    active_requests = pool.current_activities_requests
    assert len(active_requests) == 2

    cancel_coffee_late = business.ICancelRequest("john", "coffee", 6)
    storage.store_request(cancel_coffee_late)
    pool.update_requests_from_storage()
    active_requests = pool.current_activities_requests
    assert len(active_requests) == 2
