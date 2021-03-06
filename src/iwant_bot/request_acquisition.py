import abc
import uuid
import collections

from . import requests


class RequestPreprocessingPipeline(object):
    def __init__(self):
        self._blocks = collections.defaultdict(list)

    def add_block(self, request_type, block):
        self._blocks[request_type].append(block)

    def add_activity_request(
            self, person_id, activity, deadline,
            activity_start, activity_end):
        request = requests.IWantRequest(
            person_id, activity, deadline, activity_start, activity_end)
        return self._add_a_request(request, 'activity')

    # TODO: Restructure the code to be more understandable
    def _add_a_request(self, request, cathegory):
        new_chained_request = chained_request = request
        for block in self._blocks[cathegory]:
            if new_chained_request is None:
                return chained_request
            chained_request = new_chained_request
            new_chained_request = block.pass_request(chained_request)
        return chained_request

    def add_cancellation_request(self, person_id, cancelling_request_id):
        request = requests.CancellationRequest(person_id, cancelling_request_id)
        return self._add_a_request(request, 'cancel')


class AbstractBlock(abc.ABC):
    @abc.abstractmethod
    def pass_request(self, request):
        return request


class Notifier(AbstractBlock):
    def __init__(self):
        self._callbacks = []

    def append_callback(self, callback):
        self._callbacks.append(callback)

    def pass_request(self, request):
        for cb in self._callbacks:
            cb(request)
        return request


class NotifierOfCancelled(Notifier):
    def pass_request(self, request):
        for cb in self._callbacks:
            if request.cancellation_succeeded:
                cb(request)
        return request


class NotifierOfNotCancelled(Notifier):
    def pass_request(self, request):
        for cb in self._callbacks:
            if not request.cancellation_succeeded:
                cb(request)
        return request


class Breaker(AbstractBlock):
    def pass_request(self, request):
        return None


class PassThrough(AbstractBlock):
    def pass_request(self, request):
        return super().pass_request(request)


class UIDAssigner(AbstractBlock):
    def pass_request(self, request):
        request.id = str(uuid.uuid4())
        return request


class Saver(AbstractBlock):
    def __init__(self, storage):
        self._storage = storage

    def pass_request(self, request):
        self._storage.store_request(request)
        return request


class Canceller(AbstractBlock):
    def __init__(self, storage):
        self._storage = storage

    def pass_request(self, request):
        request.cancellation_succeeded = False
        try:
            self._storage.remove_activity_request(request.cancelling_request_id, request.person_id)
            request.cancellation_succeeded = True
        except AssertionError:
            # Request was not cancelled, but in case of a KeyError,
            # it is not a big deal
            pass
        return request


input_pipeline = RequestPreprocessingPipeline()
