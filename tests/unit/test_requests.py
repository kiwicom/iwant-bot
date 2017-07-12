import time

from iwant_bot import requests


def test_create_request():
    now = time.time()
    request = requests.IWantRequest("john", "coffee", now + 60, 0, 0)
    assert request.is_active_now()
    assert not request.is_active_by(now + 65)


def test_request_overlaps():
    request = requests.IWantRequest("john", "coffee", 0, 0, 50)
    longer_request = requests.IWantRequest("jack", "coffee", 0, 0, 100)
    assert request.overlaps_with(longer_request)
    assert longer_request.overlaps_with(request)
    assert not request.conflicts_with(longer_request)
    longer_request.activity_start += 70
    assert not request.overlaps_with(longer_request)
