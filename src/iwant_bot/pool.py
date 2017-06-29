import asyncio
import collections
from iwant_bot.ignore import IgnoreList


class RequestsPool(object):
    """
    This class is a layer between the storage layer and higher-level
    logic layer --- it pulls requests from the storage and exposes
    only the relevant requests.
    """

    def __init__(self, storage):
        # this is main loop which operates workers
        self._loop = asyncio.get_event_loop()
        self.activity_list = list()
        self.req_by_activities = collections.defaultdict(list)
        self.pairs = collections.defaultdict(list)
        self._requests_storage = storage
        self.current_activities_requests = set()
        self._time_relevant_requests = set()
        self._blacklisted_requests = set()
        self._time_conflicting_requests = set()
        self.ignore_list = IgnoreList()

    def update_requests_from_storage(self):
        activity_requests = self._requests_storage.get_activity_requests()
        self._time_relevant_requests = {request for request in activity_requests
                                        if request.is_active_now()}

        self._blacklisted_requests = set()
        self._set_time_conflicting_requests()
        self._blacklisted_requests = self._time_conflicting_requests
        self.current_activities_requests = self._time_relevant_requests \
            - self._blacklisted_requests
        self._update_activity_list()

    def _update_activity_list(self):
        for req in self.current_activities_requests:
            if req.activity not in self.activity_list:
                self.activity_list.append(req.activity)

            destination = self.req_by_activities[req.activity]
            if req.activity not in self.req_by_activities.keys():
                self.req_by_activities[req.activity] = req
            elif req not in destination:
                destination.append(req)

    def make_pairs(self, activity):
        ignore_list = self.ignore_list
        source = self.req_by_activities[activity]
        destination = self.pairs[activity]
        if len(source) > 1:
            for request1 in source:
                source.remove(request1)
                for request2 in source:
                    if ignore_list.mutual_ignore_check(request1.person_id, request2.person_id):
                        continue
                    paired = self.pair(request1, request2)
                    source.remove(request2)
                    destination.append(paired)
                    break
                source.append(request1)

    @staticmethod
    def pair(request1, request2):
        pair = {request1, request2}
        return pair

    # TODO: There exist intricate strategies that would pick the request
    # that conflict with others most
    def _set_time_conflicting_requests(self):
        self._time_conflicting_requests = set()
        list_of_requests_to_filter = list(self._time_relevant_requests)
        for examined, first_request in enumerate(list_of_requests_to_filter):
            for second_request in list_of_requests_to_filter[examined:]:
                if first_request.conflicts_with(second_request):
                    self._time_conflicting_requests.add(first_request)
