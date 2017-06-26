import pytest

from iwant_bot import storage, requests


def test_storage_saves_and_restores():
    store = storage.MemoryRequestsStorage()
    request = requests.IWantRequest("john", "coffee", 0)
    store.store_request(request)
    recovered_request = store.get_activity_requests()[0]
    assert request == recovered_request
    with pytest.raises(ValueError) as err:
        store.store_request(42)
    assert "int" in str(err)


def test_storage_removes():
    store = storage.MemoryRequestsStorage()
    request = requests.IWantRequest("john", "coffee", 0)
    store.store_request(request)
    request = requests.IWantRequest("john", "coffee", 0)
    request.id = "foo"
    store.store_request(request)
    with pytest.raises(KeyError):
        store.remove_activity_request("bar", "jack")
    with pytest.raises(KeyError):
        store.remove_activity_request("foo", "jack")
    store.remove_activity_request("foo", "john")
    assert len(store.get_activity_requests()) == 1


def test_storage_filters_activities():
    store = storage.MemoryRequestsStorage()
    store.store_request(requests.IWantRequest("john", "coffee", 1))
    store.store_request(requests.IWantRequest("jack", "coffee", 6))
    store.store_request(requests.IWantRequest("jane", "tea", 2))

    recovered_tea_requests = store.get_activity_requests("tea")
    assert len(recovered_tea_requests) == 1
    assert recovered_tea_requests[0].person_id == "jane"

    recovered_coffee_requests = store.get_activity_requests("coffee")
    assert len(recovered_coffee_requests) == 2

    recovered_coffee_requests = store.get_activity_requests()
    assert len(recovered_coffee_requests) == 3


def test_task_storage():
    store = storage.MemoryTaskStorage()
    store.store_task("coffee", "added")
    store.store_task("coffee", "cancelled")
    task = store.retreive_task("coffee")
    assert task == "cancelled"
    assert store.retreive_task("coffee") is None
    store.store_task("covfefe", "tweeted")
    assert store.retreive_any_task() == ("covfefe", "tweeted")
