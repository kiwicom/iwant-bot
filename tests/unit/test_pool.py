import datetime

from iwant_bot import requests
from iwant_bot.storage import MemoryRequestsStorage
from iwant_bot.pool import RequestsPool


NOW = datetime.datetime.today()
DELAY_10S = datetime.timedelta(seconds=10)
START_TIME = NOW + 60 * DELAY_10S


def make_request_stacker(store):

    def stack_request(person, activity, deadline):
        request = requests.IWantRequest(person, activity, deadline, START_TIME, 0)
        request.id = "generic ID"
        request = store.store_request(request)
        return request
    return stack_request


def make_filled_request_pool():
    storage = MemoryRequestsStorage()
    stacker = make_request_stacker(storage)
    stacker("john", "coffee", NOW + 5 * DELAY_10S)
    stacker("jane", "coffee", NOW + 5 * DELAY_10S)
    stacker("oliver", "coffee", NOW + 5 * DELAY_10S)
    stacker("peter", "coffee", NOW + 7 * DELAY_10S)
    stacker("olivia", "picnic", NOW + 5 * DELAY_10S)
    stacker("martin", "picnic", NOW + 7 * DELAY_10S)
    stacker("christopher", "picnic", NOW + 10 * DELAY_10S)
    stacker("jerry", "coffee", NOW)
    stacker("tyler", "coffee", NOW + 7 * DELAY_10S)
    stacker("carolina", "coffee", NOW + 7 * DELAY_10S)
    stacker("emilia", "coffee", NOW + 7 * DELAY_10S)
    stacker("josh", "coffee", NOW + 7 * DELAY_10S)
    stacker("alex", "coffee", NOW + 7 * DELAY_10S)
    stacker("bryan", "coffee", NOW + 7 * DELAY_10S)
    stacker("kate", "coffee", NOW + 7 * DELAY_10S)
    stacker("morgan", "coffee", NOW + 7 * DELAY_10S)
    stacker("celine", "coffee", NOW + 7 * DELAY_10S)
    stacker("trevor", "coffee", NOW + 7 * DELAY_10S)
    stacker("michael", "coffee", NOW + 7 * DELAY_10S)
    stacker("franklin", "coffee", NOW + 7 * DELAY_10S)
    stacker("andrew", "picnic", NOW + 5 * DELAY_10S)
    pool = RequestsPool(storage)
    pool.update_requests_from_storage()
    return pool


def test_requests_pool_filters_relevant():
    pool = make_filled_request_pool()
    active_requests = pool.current_activities_requests
    assert len(active_requests) == 20


def test_ignored_pairs():
    pool = make_filled_request_pool()
    pool.ignore_list.ignore('christopher', 'olivia')
    pool.ignore_list.ignore('christopher', 'martin')
    pool.ignore_list.ignore('christopher', 'andrew')
    pool.ignore_list.ignore('olivia', 'andrew')
    pool.ignore_list.ignore('olivia', 'martin')
    for activity in pool.activity_list:
        pool.make_groups(pool, activity)
    assert len(pool.pairs['picnic']) == 1
    assert len(pool.pairs['coffee']) == 8


def test_ignored_groups_of_7():
    pool = make_filled_request_pool()
    pool.ignore_list.ignore('christopher', 'olivia')
    pool.ignore_list.ignore('christopher', 'martin')
    pool.ignore_list.ignore('christopher', 'andrew')
    pool.ignore_list.ignore('olivia', 'andrew')
    pool.ignore_list.ignore('olivia', 'martin')
    for activity in pool.activity_list:
        pool.make_groups(pool, activity, 7)
    assert len(pool.pairs['picnic']) == 0
    assert len(pool.pairs['coffee']) == 2


def test_pairing_activities():
    pool = make_filled_request_pool()
    for activity in pool.activity_list:
        pool.make_groups(pool, activity)
    assert len(pool.pairs['picnic']) == 2
    assert len(pool.pairs['coffee']) == 8


def test_number_of_activities():
    pool = make_filled_request_pool()
    storage = pool._requests_storage
    assert len(pool.activity_list) == 2

    stacker = make_request_stacker(storage)
    stacker("jack", "running", NOW + 45 * DELAY_10S)

    pool.update_requests_from_storage()
    assert len(pool.activity_list) == 3


def test_pool_ignores_duplicates():
    pool = make_filled_request_pool()
    storage = pool._requests_storage

    stacker = make_request_stacker(storage)
    stacker("john", "coffee", NOW + 5 * DELAY_10S)
    stacker("james", "coffee", NOW + 5 * DELAY_10S)

    pool.update_requests_from_storage()
    active_requests = pool.current_activities_requests
    assert len(active_requests) == 21
