import time

from iwant_bot import requests


def test_create_request():
    request = requests.IWantRequest("john", "coffee", 1)
    assert request.is_active_now()
    assert not request.is_active_by(time.time() + 65)


def test_request_overlaps():
    request = requests.IWantRequest("john", "coffee", 1)
    longer_request = requests.IWantRequest("jack", "coffee", 2)
    assert request.overlaps_with(longer_request)
    assert longer_request.overlaps_with(request)
    assert not request.conflicts_with(longer_request)
    longer_request.timeframe_start += 70
    assert not request.overlaps_with(longer_request)
