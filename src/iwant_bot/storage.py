import abc
import collections
import datetime

from iwant_bot import requests


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

    @abc.abstractmethod
    def remove_activity_request(self, request_id, person_id):
        """
        Remove a request from storage

        Raises:
            KeyError if there is no request of such ID issued by that person.
        """
        pass

    @abc.abstractmethod
    def wipe_database(self):
        pass

    @abc.abstractmethod
    def resolve_requests(self, requests):
        pass

    @abc.abstractmethod
    def get_requests_by_deadline_proximity(self, deadline, time_buffer_in_seconds):
        pass

    @abc.abstractmethod
    def get_results_by_deadline_proximity(self, deadline, time_proximity):
        pass

    @abc.abstractmethod
    def get_requests_of_result(self, result_id):
        pass

    @abc.abstractmethod
    def get_result(self, result_id) -> requests.Result:
        pass

    @abc.abstractmethod
    def _update_result_deadline(self, result_id):
        pass

    def _update_result_status(self, result, concerned_requests):
        if len(concerned_requests) == 1:
            result.status = requests.Status.PENDING
        elif len(concerned_requests) > 1:
            result.status = requests.Status.FRESH
        elif len(concerned_requests) == 0:
            result.status = requests.Status.INVALID
        return result

    def _find_fitting_result_id(self, results):
        good_id = None
        for result in results:
            if result.status == requests.Status.FRESH:
                good_id = result.id
                break
        if good_id is None:
            for result in results:
                if result.status == requests.Status.PENDING:
                    good_id = result.id
                    break
        assert good_id is not None
        return good_id


# TODO: Remove -> Invalidate
# store results ID of the result the request is solved by.
class MemoryRequestsStorage(RequestStorage):
    def __init__(self):
        self._results_by_id = dict()
        self._all_requests = set()
        self._requests_by_id = dict()
        self._requests_by_result_id = collections.defaultdict(set)

        self._result_counter = 0

    def store_request(self, request):
        if isinstance(request, requests.IWantRequest):
            self._all_requests.add(request)
            if request.id is not None:
                self._requests_by_id[request.id] = request
            if request.resolved_by is not None:
                self._requests_by_result_id[request.resolved_by].add(request)
                self._results_by_id[request.resolved_by].requests_ids.add(request.id)
            else:
                resolved_by = self._create_result(request)
                request.resolved_by = resolved_by
        else:
            raise ValueError(f"Can't store requests of type {type(request)}.")
        return request

    def get_activity_requests(self, activity=None):
        ret = list(self._all_requests)
        if activity is not None:
            ret = [req for req in ret
                   if req.activity == activity]
        return ret

    def remove_activity_request(self, request_id, person_id):
        activity_requests = self._requests_by_id.values()

        def request_has_right_id(req): return req.id == request_id
        requests_with_right_id = list(filter(request_has_right_id, activity_requests))
        assert len(requests_with_right_id) == 1, \
            "There should be exactly one request of such ID to remove"
        request_to_remove = requests_with_right_id[0]
        assert request_to_remove.person_id == person_id, \
            f"The request of the given ID can't be removed by {person_id}"
        self._remove_request_by_id(request_id)
        according_result_id = self.get_result(request_to_remove.resolved_by).id

        concerned_requests = self._requests_by_result_id[according_result_id]
        self._update_result_status(self._results_by_id[according_result_id], concerned_requests)
        self._update_result_deadline(according_result_id)

    def _remove_request_by_id(self, request_id):
        request = self._requests_by_id[request_id]
        self._requests_by_id.pop(request_id)
        self._all_requests.discard(request)
        if request.resolved_by is not None:
            self._requests_by_result_id[request.resolved_by].discard(request)

    def _create_result(self, request):
        self._result_counter += 1
        self._results_by_id[self._result_counter] = requests.Result(
            self._result_counter, set(), request.deadline)
        return self._result_counter

    def wipe_database(self):
        pass

    def resolve_requests(self, requests_ids):
        all_requests = [self._requests_by_id[id] for id in requests_ids]
        assert len(all_requests) > 1

        existing_results = [self.get_result(req.resolved_by) for req in all_requests]
        resolved_by = self._find_fitting_result_id(existing_results)
        for request in all_requests:
            self._remove_request_by_id(request.id)
            request.resolved_by = resolved_by
            self.store_request(request)

        for result in existing_results:
            result_id = result.id
            concerned_requests = self._requests_by_result_id[result_id]
            self._update_result_status(self._results_by_id[result_id], concerned_requests)
            self._update_result_deadline(result_id)
        return resolved_by

    def get_requests_of_result(self, result_id):
        return self._requests_by_result_id[result_id]

    def _update_result_deadline(self, result_id):
        result = self.get_result(result_id)
        if result.status == requests.Status.INVALID:
            return
        requests_deadlines = [req.deadline for req
                              in self._requests_by_result_id[result_id]]
        result.deadline = min(requests_deadlines)

    def _get_item_by_deadline_proximity(self, container, deadline, time_proximity):
        time_end = deadline
        time_start = time_end - datetime.timedelta(seconds=time_proximity)
        result = set()
        for req in container:
            if time_start < req.deadline < time_end:
                result.add(req)
        return result

    def get_requests_by_deadline_proximity(self, deadline, time_buffer_in_seconds):
        return self._get_item_by_deadline_proximity(self._all_requests, deadline, time_buffer_in_seconds)

    def get_results_by_deadline_proximity(self, deadline, time_proximity):
        results = self._get_item_by_deadline_proximity(
            self._results_by_id.values(), deadline, time_proximity)
        results = filter(
            lambda res: res.status in (requests.Status.PENDING, requests.Status.FRESH),
            results
        )
        return results

    def get_result(self, result_id):
        result = self._results_by_id[result_id]
        return result
