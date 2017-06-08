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

    def overlaps_with(self, other_request):
        overlaps = (self.timeframe_end > other_request.timeframe_start
                    and self.timeframe_start < other_request.timeframe_end)
        return overlaps

    # TODO: Find a more descriptive name
    def conflicts_with(self, other_request):
        overlaps = (self.timeframe_end > other_request.timeframe_start
                    and self.timeframe_start < other_request.timeframe_end)
        conflicts = (self is not other_request
                     and self.person_id == other_request.person_id
                     and overlaps)
        return conflicts


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

        self._time_relevant_requests = set()
        self._blacklisted_requests = set()
        self._cancelled_requests = set()
        self._time_conflicting_requests = set()

    def update_requests_from_storage(self):
        activity_requests = self._requests_storage.get_activity_requests()
        self._time_relevant_requests = {request for request in activity_requests
                                        if request.is_active_now()}

        self._blacklisted_requests = set()
        self._set_cancelled_requests()
        self._set_time_conflicting_requests()
        self._blacklisted_requests = self._cancelled_requests | self._time_conflicting_requests
        self.current_activities_requests = self._time_relevant_requests - self._blacklisted_requests

    def _set_cancelled_requests(self):
        self._cancelled_requests = set()
        cancellation_requests = self._requests_storage.get_cancellation_requests()
        for cancellation_request in cancellation_requests:
            self._cancelled_requests |= {req for req in self._time_relevant_requests
                                         if cancellation_request.cancels(req)}

    # TODO: There exist intricate strategies that would pick the request
    # that conflict with others most
    def _set_time_conflicting_requests(self):
        self._time_conflicting_requests = set()
        list_of_requests_to_filter = list(self._time_relevant_requests)
        for examined, first_request in enumerate(list_of_requests_to_filter):
            for second_request in list_of_requests_to_filter[examined:]:
                if first_request.conflicts_with(second_request):
                    self._time_conflicting_requests.add(first_request)


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
            raise ValueError(f"Can't store requests of type {type(request)}.")
        destination.append(request)

    def get_cancellation_requests(self):
        return list(self._requests["cancel"])

    def get_activity_requests(self):
        return list(self._requests["activity"])
