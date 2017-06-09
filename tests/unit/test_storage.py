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
