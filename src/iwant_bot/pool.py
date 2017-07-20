import collections
import itertools
from iwant_bot.ignore import IgnoreList
from bot_worker.celery import worker


class RequestsPool(object):
    """
    This class is a layer between the storage layer and higher-level
    logic layer --- it pulls requests from the storage and exposes
    only the relevant requests.
    """

    def __init__(self, storage):
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

    @worker.task()
    def make_groups(self, activity, group_of=2):
        requests = set(self.req_by_activities[activity])
        destination = self.pairs[activity]
        combinations_of_requests = itertools.combinations(requests, group_of)
        filter_ignored = self._filter_ignored(combinations_of_requests)
        filter_unique_items = self._filter_uniques(filter_ignored)

        destination += filter_unique_items
        merged = set(itertools.chain.from_iterable(destination))
        remaining = requests - merged
        self.req_by_activities[activity] = remaining

    def _filter_ignored(self, combinations):
        filtered = [group for group in combinations
                    if not self.ignore_list.group_ignore_check(group)]
        return filtered

    @staticmethod
    def _filter_uniques(combinations):
        seen = list()
        ans = list()
        for group in combinations:
            acceptance_sheet = set()
            for request in group:
                if request not in seen:
                    acceptance_sheet.add(request)
            if len(acceptance_sheet) == len(group):
                ans.append(group)
                seen += [req for req in group]
        return ans

    # TODO: There exist intricate strategies that would pick the request
    # that conflict with others most
    def _set_time_conflicting_requests(self):
        self._time_conflicting_requests = set()
        list_of_requests_to_filter = list(self._time_relevant_requests)
        for examined, first_request in enumerate(list_of_requests_to_filter):
            for second_request in list_of_requests_to_filter[examined:]:
                if first_request.conflicts_with(second_request):
                    self._time_conflicting_requests.add(first_request)
