import abc
import collections
import datetime
import time


class Request(object):
    def __init__(self, person_id, request_id=None):
        self.person_id = person_id
        self.id = request_id


class IWantRequest(Request):
    def __init__(self, person_id, activity, lifespan_in_minutes):
        super().__init__(person_id)
        self.activity = activity
        self.timeframe_start = time.time()
        lifespan = datetime.timedelta(minutes=lifespan_in_minutes)
        self.timeframe_end = self.timeframe_start + lifespan.total_seconds()

    def is_active_now(self):
        return self.is_active_by(time.time())

    def is_active_by(self, by_the_time):
        return self.timeframe_start <= by_the_time < self.timeframe_end


class ICancelRequest(Request):
    def __init__(self, person_id, activity, offset_in_minutes):
        super().__init__(person_id)
        self.activity = activity
        self.time_of_request = time.time() + offset_in_minutes * 60

    def cancels(self, request):
        if (request.person_id == self.person_id
                and request.is_active_by(self.time_of_request)):
            return True
        else:
            return False


class RequestsPool(object):
    def __init__(self, storage):
        self._requests_storage = storage
        self.current_activities_requests = set()

    def update_requests_from_storage(self):
        activity_requests = self._requests_storage.get_activity_requests()
        time_relevant_requests = {request for request in activity_requests
                                  if request.is_active_now()}

        blacklisted_requests = set()
        cancellation_requests = self._requests_storage.get_cancellation_requests()
        for cancellation_request in cancellation_requests:
            blacklisted_requests.update({req for req in activity_requests
                                         if cancellation_request.cancels(req)})
        self.current_activities_requests = time_relevant_requests.difference(blacklisted_requests)

    def filter_duplicate_requests(self):
        pass


def partition_requests(requests):
    partitions = collections.defaultdict(list)
    for request in requests:
        partitions[request.activity].append(request)
    return partitions


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
            raise ValueError("Can't store requests of type {type(request)}.")
        destination.append(request)

    def get_cancellation_requests(self):
        return list(self._requests["cancel"])

    def get_activity_requests(self):
        return list(self._requests["activity"])
