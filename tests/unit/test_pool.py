import time

from iwant_bot import requests
from iwant_bot.storage import MemoryRequestsStorage
from iwant_bot.pool import RequestsPool


NOW = time.time()


def make_filled_request_pool():
    storage = MemoryRequestsStorage()
    storage.store_request(requests.IWantRequest("john", "coffee", NOW + 50, 0, 0))
    storage.store_request(requests.IWantRequest("jane", "coffee", NOW + 50, 0, 0))
    storage.store_request(requests.IWantRequest("oliver", "coffee", NOW + 50, 0, 0))
    storage.store_request(requests.IWantRequest("peter", "coffee", NOW + 70, 0, 0))
    storage.store_request(requests.IWantRequest("olivia", "picnic", NOW + 50, 0, 0))
    storage.store_request(requests.IWantRequest("martin", "picnic", NOW + 70, 0, 0))
    storage.store_request(requests.IWantRequest("christopher", "picnic", NOW + 100, 0, 0))
    storage.store_request(requests.IWantRequest("jerry", "coffee", NOW + 0, 0, 0))
    pool = RequestsPool(storage)
    pool.update_requests_from_storage()
    return pool


def test_requests_pool_filters_relevant():
    pool = make_filled_request_pool()
    active_requests = pool.current_activities_requests
    assert len(active_requests) == 7


def test_pairing_activities():
    pool = make_filled_request_pool()
    for activity in pool.activity_list:
        pool.make_pairs(activity)
    assert len(pool.pairs['picnic']) == 1
    assert len(pool.pairs['coffee']) == 2


def test_number_of_activities():
    pool = make_filled_request_pool()
    assert len(pool.activity_list) == 2


def test_pool_ignores_duplicates():
    pool = make_filled_request_pool()
    storage = pool._requests_storage
    storage.store_request(requests.IWantRequest("john", "coffee", NOW + 50, 0, 0))
    storage.store_request(requests.IWantRequest("james", "coffee", NOW + 50, 0, 0))
    pool.update_requests_from_storage()
    active_requests = pool.current_activities_requests
    assert len(active_requests) == 8
