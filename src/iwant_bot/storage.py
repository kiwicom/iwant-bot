import abc
import collections

from iwant_bot.requests import IWantRequest


class RequestStorage(abc.ABC):
    @abc.abstractmethod
    def __init__(self):
        pass

    @abc.abstractmethod
    def store_request(self, request):
        """
        Stores a Request data structure so it can be retreived.

        Raises:
            ValueError if the request structure is not recognized.
        """
        pass

    @abc.abstractmethod
    def get_activity_requests(self, activity=None):
        """
        Retreives an activity-related request

        Args:
            activity: If not none, all retreived requests will be related
            to this activity.
        """
        pass


class MemoryRequestsStorage(RequestStorage):
    def __init__(self):
        self._requests = collections.defaultdict(list)

    def store_request(self, request):
        if isinstance(request, IWantRequest):
            destination = self._requests["activity"]
        else:
            raise ValueError(f"Can't store requests of type {type(request)}.")
        destination.append(request)

    def get_activity_requests(self, activity=None):
        ret = list(self._requests["activity"])
        if activity is not None:
            ret = [req for req in ret
                   if req.activity == activity]
        return ret
