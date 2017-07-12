import os

import pytest

from iwant_bot import storage, requests, storage_sqlalchemy


def test_storage_saves_and_restores():
    store = storage.MemoryRequestsStorage()
    request = requests.IWantRequest("john", "coffee", 0, 0, 0)
    store.store_request(request)
    recovered_request = store.get_activity_requests()[0]
    assert request == recovered_request
    with pytest.raises(ValueError) as err:
        store.store_request(42)
    assert "int" in str(err)


def test_storage_sqlalchemy_saves_and_restores():
    # TODO: do this properly as a pytest teardown function.
    try:
        os.remove("here.sqlite")
    except OSError:
        pass
    store = storage_sqlalchemy.SqlAlchemyRequestStorage("sqlite:///here.sqlite")
    request = requests.IWantRequest("john", "coffee", 0, 0, 0)
    request.id = 0
    store.store_request(request)
    recovered_request = store.get_activity_requests()[0]
    assert request == recovered_request
    with pytest.raises(ValueError) as err:
        store.store_request(42)
    assert "int" in str(err)


def test_storage_removes():
    store = storage.MemoryRequestsStorage()
    request = requests.IWantRequest("john", "coffee", 0, 0, 0)
    store.store_request(request)
    request = requests.IWantRequest("john", "coffee", 0, 0, 0)
    request.id = "foo"
    store.store_request(request)
    with pytest.raises(AssertionError):
        store.remove_activity_request("bar", "jack")
    with pytest.raises(AssertionError):
        store.remove_activity_request("foo", "jack")
    store.remove_activity_request("foo", "john")
    assert len(store.get_activity_requests()) == 1


def test_storage_filters_activities():
    store = storage.MemoryRequestsStorage()
    store.store_request(requests.IWantRequest("john", "coffee", 1, 0, 0))
    store.store_request(requests.IWantRequest("jack", "coffee", 6, 0, 0))
    store.store_request(requests.IWantRequest("jane", "tea", 2, 0, 0))

    recovered_tea_requests = store.get_activity_requests("tea")
    assert len(recovered_tea_requests) == 1
    assert recovered_tea_requests[0].person_id == "jane"

    recovered_coffee_requests = store.get_activity_requests("coffee")
    assert len(recovered_coffee_requests) == 2

    recovered_coffee_requests = store.get_activity_requests()
    assert len(recovered_coffee_requests) == 3


def test_task_queue():
    store = storage.MemoryTaskQueue()
    store.store_task("coffee-added")
    store.store_task("coffee-cancelled")
    task = store.retreive_task()
    assert task == "coffee-cancelled"
    store.store_task("covfefe-tweeted")
    assert store.retreive_task() == ("covfefe-tweeted")


def test_results_storage():
    store = storage.MemoryResultsStorage()
    late_result = requests.Result(["3"], 2)
    store.store_result(late_result)
    early_result = requests.Result(["1", "2"], 1)
    store.store_result(early_result)
    returned_result = store.get_results_concerning_request("1")
    assert early_result == returned_result
    assert store.get_results_past(1)[0] == late_result
    assert store.get_results_past(0)[0] == early_result
    assert store.get_results_past(0)[1] == late_result
