import os

import pytest

from iwant_bot import storage, requests, storage_sqlalchemy


def make_request_stacker(store):
    def stack_request(uid, person, activity, args=(0, 0, 0)):
        request = requests.IWantRequest(person, activity, * args)
        request.id = uid
        store.store_request(request)
        return request
    return stack_request


def test_memory_storage_saves_and_restores():
    store = storage.MemoryRequestsStorage()
    storage_saves_and_restores(store)


def storage_saves_and_restores(store):
    store.wipe_database()
    stack = make_request_stacker(store)

    request = stack("one", "john", "coffee")
    recovered_request = store.get_activity_requests()[0]
    assert request == recovered_request
    with pytest.raises(ValueError) as err:
        store.store_request(42)
    assert "int" in str(err)


def test_storage_sqlite_saves_and_restores():
    store = storage_sqlalchemy.SqlAlchemyRequestStorage("sqlite:///here.sqlite")
    storage_saves_and_restores(store)


@pytest.fixture()
def postgres_store():
    username = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    store = storage_sqlalchemy.SqlAlchemyRequestStorage(
        f"postgresql+psycopg2://{username}:{password}@postgres/{username}")
    return store


@pytest.mark.skipif("POSTGRES_USER" not in os.environ,
                    reason="Postgres container connection is not configured correctly")
def test_storage_postgres_saves_and_restores(postgres_store):
    storage_saves_and_restores(postgres_store)


def test_memory_storage_removes():
    store = storage.MemoryRequestsStorage()
    storage_removes(store)


def test_sqlite_storage_removes():
    store = storage_sqlalchemy.SqlAlchemyRequestStorage("sqlite:///here.sqlite")
    storage_removes(store)


@pytest.mark.skipif("POSTGRES_USER" not in os.environ,
                    reason="Postgres container connection is not configured correctly")
def test_postgres_storage_removes(postgres_store):
    storage_removes(postgres_store)


def test_sqlite_storage_resloves():
    store = storage_sqlalchemy.SqlAlchemyRequestStorage("sqlite:///here.sqlite")
    storage_resolves_and_fetches(store)


def storage_resolves_and_fetches(store):
    store.wipe_database()
    stack = make_request_stacker(store)

    stack("one", "john", "coffee")
    stack("two", "john", "coffee")
    stack("three", "john", "coffee")

    store.resolve_requests(["one", "two"])
    resolved_requests = store.get_activity_requests("coffee")
    coffee_result_id = resolved_requests[0].resolved_by
    assert coffee_result_id is not None
    assert coffee_result_id == resolved_requests[1].resolved_by

    store.resolve_requests(["one", "two", "three"])
    resolved_requests = store.get_activity_requests("coffee")
    for req in resolved_requests:
        assert req.resolved_by == coffee_result_id

    picnic_one = stack("four", "jack", "picnic")
    picnic_two = stack("five", "anna", "picnic")
    store.resolve_requests(["four", "five"])

    resolved_requests = store.get_activity_requests("picnic")
    picnic_result_id = resolved_requests[0].resolved_by
    assert picnic_result_id is not None
    assert picnic_result_id == resolved_requests[1].resolved_by
    assert picnic_result_id != coffee_result_id

    requests = store.get_requests_of_result(picnic_result_id)
    assert len(requests) == 2
    picnic_one.resolved_by = picnic_two.resolved_by = picnic_result_id
    assert picnic_one in requests
    assert picnic_two in requests


def storage_removes(store):
    store.wipe_database()
    stack = make_request_stacker(store)

    stack("one", "john", "coffee")
    stack("foo", "john", "coffee")

    with pytest.raises(AssertionError):
        store.remove_activity_request("bar", "jack")
    with pytest.raises(AssertionError):
        store.remove_activity_request("foo", "jack")
    store.remove_activity_request("foo", "john")
    assert len(store.get_activity_requests()) == 1


def test_memory_storage_filters_activities():
    store = storage.MemoryRequestsStorage()
    storage_filters_activities(store)


def test_sqlite_storage_filters_activities():
    store = storage_sqlalchemy.SqlAlchemyRequestStorage("sqlite:///here.sqlite")
    storage_filters_activities(store)


@pytest.mark.skipif("POSTGRES_USER" not in os.environ,
                    reason="Postgres container connection is not configured correctly")
def test_postgres_storage_filters_activities(postgres_store):
    storage_filters_activities(postgres_store)


def storage_filters_activities(store):
    store.wipe_database()
    stack = make_request_stacker(store)

    stack("1", "john", "coffee", (1, 0, 0))
    stack("2", "jack", "coffee", (6, 0, 0))
    stack("3", "jane", "tea", (2, 0, 0))

    recovered_tea_requests = store.get_activity_requests("tea")
    assert len(recovered_tea_requests) == 1
    assert recovered_tea_requests[0].person_id == "jane"

    recovered_coffee_requests = store.get_activity_requests("coffee")
    assert len(recovered_coffee_requests) == 2

    recovered_all_requests = store.get_activity_requests()
    assert len(recovered_all_requests) == 3


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
