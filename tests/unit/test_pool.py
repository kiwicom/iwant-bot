from iwant_bot import requests
from iwant_bot.storage import MemoryRequestsStorage
from iwant_bot.pool import RequestsPool


def make_filled_request_pool():
    storage = MemoryRequestsStorage()
    storage.store_request(requests.IWantRequest("john", "coffee", 5))
    storage.store_request(requests.IWantRequest("jane", "coffee", 5))
    storage.store_request(requests.IWantRequest("olivia", "picnic", 5))
    storage.store_request(requests.IWantRequest("jerry", "coffee", 0))
    pool = RequestsPool(storage)
    pool.update_requests_from_storage()
    return pool


def test_requests_pool_filters_relevant():
    pool = make_filled_request_pool()
    active_requests = pool.current_activities_requests
    assert len(active_requests) == 3


def test_pool_ignores_duplicates():
    pool = make_filled_request_pool()
    storage = pool._requests_storage
    storage.store_request(requests.IWantRequest("john", "coffee", 5))
    storage.store_request(requests.IWantRequest("james", "coffee", 5))
    pool.update_requests_from_storage()
    active_requests = pool.current_activities_requests
    assert len(active_requests) == 4
