import pytest

from iwant_bot.storage import MemoryRequestsStorage
from iwant_bot.requests import IWantRequest


def test_storage_saves_and_restores():
    storage = MemoryRequestsStorage()
    request = IWantRequest("john", "coffee", 0)
    storage.store_request(request)
    recovered_request = storage.get_activity_requests()[0]
    assert request == recovered_request
    with pytest.raises(ValueError) as err:
        storage.store_request(42)
    assert "int" in str(err)


def test_storage_filters_activities():
    storage = MemoryRequestsStorage()
    storage.store_request(IWantRequest("john", "coffee", 1))
    storage.store_request(IWantRequest("jack", "coffee", 6))
    storage.store_request(IWantRequest("jane", "tea", 2))

    recovered_tea_requests = storage.get_activity_requests("tea")
    assert len(recovered_tea_requests) == 1
    assert recovered_tea_requests[0].person_id == "jane"

    recovered_coffee_requests = storage.get_activity_requests("coffee")
    assert len(recovered_coffee_requests) == 2

    recovered_coffee_requests = storage.get_activity_requests()
    assert len(recovered_coffee_requests) == 3
