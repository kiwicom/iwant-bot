

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
