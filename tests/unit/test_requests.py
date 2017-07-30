import datetime

from iwant_bot import requests


NOW = datetime.datetime.now()
TIME_1MIN = datetime.timedelta(minutes=1)


def test_create_request():
    request = requests.IWantRequest("john", "coffee", NOW + TIME_1MIN, 0, 0)
    assert request.is_active_now()
    assert not request.is_active_by(NOW + TIME_1MIN * 1.1)


def test_request_overlaps():
    request = requests.IWantRequest("john", "coffee", NOW, NOW, 50)
    longer_request = requests.IWantRequest("jack", "coffee", NOW, NOW, 100)
    assert request.overlaps_with(longer_request)
    assert longer_request.overlaps_with(request)
    assert not request.conflicts_with(longer_request)
    longer_request.activity_start += TIME_1MIN
    assert not request.overlaps_with(longer_request)
