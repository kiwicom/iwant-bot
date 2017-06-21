from iwant_bot import requests
from iwant_bot.storage import MemoryRequestsStorage
from iwant_bot.pool import RequestsPool


def make_filled_request_pool():
    storage = MemoryRequestsStorage()
    storage.store_request(requests.IWantRequest("john", "coffee", 5))
    storage.store_request(requests.IWantRequest("jane", "coffee", 5))
    storage.store_request(requests.IWantRequest("oliver", "coffee", 5))
    storage.store_request(requests.IWantRequest("peter", "coffee", 7))
    storage.store_request(requests.IWantRequest("olivia", "picnic", 5))
    storage.store_request(requests.IWantRequest("andrew", "picnic", 5))
    storage.store_request(requests.IWantRequest("martin", "picnic", 7))
    storage.store_request(requests.IWantRequest("christopher", "picnic", 10))
    storage.store_request(requests.IWantRequest("jerry", "coffee", 0))
    pool = RequestsPool(storage)
    pool.update_requests_from_storage()
    return pool


def test_requests_pool_filters_relevant():
    pool = make_filled_request_pool()
    active_requests = pool.current_activities_requests
    assert len(active_requests) == 8


def test_pairing_activities():
    pool = make_filled_request_pool()
    for activity in pool.activity_list:
        pool.make_pairs(activity)
    assert len(pool.pairs['picnic']) == 2
    assert len(pool.pairs['coffee']) == 2


def test_ignored_pairs():
    pool = make_filled_request_pool()
    pool.users.ignore('christopher', 'olivia')
    pool.users.ignore('christopher', 'martin')
    pool.users.ignore('christopher', 'andrew')
    pool.users.ignore('olivia', 'andrew')
    pool.users.ignore('olivia', 'martin')
    for activity in pool.activity_list:
        pool.make_pairs(activity)
    assert len(pool.pairs['picnic']) == 1
    assert len(pool.pairs['coffee']) == 2


def test_number_of_activities():
    pool = make_filled_request_pool()
    storage = pool._requests_storage
    assert len(pool.activity_list) == 2
    storage.store_request(requests.IWantRequest("jack", "running", 45))
    pool.update_requests_from_storage()
    assert len(pool.activity_list) == 3


def test_pool_ignores_duplicates():
    pool = make_filled_request_pool()
    storage = pool._requests_storage
    storage.store_request(requests.IWantRequest("john", "coffee", 5))
    storage.store_request(requests.IWantRequest("james", "coffee", 5))
    pool.update_requests_from_storage()
    active_requests = pool.current_activities_requests
    assert len(active_requests) == 9
