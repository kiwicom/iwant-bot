import abc
import collections

from iwant_bot.requests import IWantRequest, ICancelRequest


class RequestStorage(abc.ABC):
    @abc.abstractmethod
    def __init__(self):
        pass

    @abc.abstractmethod
    def store_request(self, request):
        pass

    @abc.abstractmethod
    def get_cancellation_requests(self):
        pass

    @abc.abstractmethod
    def get_activity_requests(self):
        pass


class MemoryRequestsStorage(RequestStorage):
    def __init__(self):
        self._requests = collections.defaultdict(list)

    def store_request(self, request):
        if isinstance(request, IWantRequest):
            destination = self._requests["activity"]
        elif isinstance(request, ICancelRequest):
            destination = self._requests["cancel"]
        else:
            raise ValueError(f"Can't store requests of type {type(request)}.")
        destination.append(request)

    def get_cancellation_requests(self):
        return list(self._requests["cancel"])

    def get_activity_requests(self):
        return list(self._requests["activity"])

