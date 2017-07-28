import abc
import collections
import queue
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
    def get_requests_by_deadline_proximity(self, deadline, time_proximity):
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
            raise ValueError(f"Can't store requests of type {type(request)}.")

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

    def _remove_request_by_id(self, request_id):
        request = self._requests_by_id[request_id]
        self._requests_by_id.pop(request_id)
        self._all_requests.discard(request)
        if request.resolved_by is not None:
            self._requests_by_result_id[request.resolved_by].discard(request)

    def _create_result(self):
        self._result_counter += 1
        self._results_by_id[self._result_counter] = requests.Result(
            self._result_counter, set(), None)
        return self._result_counter

    def wipe_database(self):
        pass

    def resolve_requests(self, requests_ids):
        all_requests = [self._requests_by_id[id] for id in requests_ids]
        assert len(all_requests) > 1

        resolved_by = None
        for request in all_requests:
            if request.resolved_by is not None:
                resolved_by = request.resolved_by

        if resolved_by is None:
            resolved_by = self._create_result()
        for request in all_requests:
            self._remove_request_by_id(request.id)
            request.resolved_by = resolved_by
            self.store_request(request)
        self._update_result_deadline(resolved_by)
        return resolved_by

    def get_requests_of_result(self, result_id):
        return self._requests_by_result_id[result_id]

    def _update_result_deadline(self, result_id):
        result = self.get_result(result_id)
        requests_deadlines = [req.deadline for req
                              in self._requests_by_result_id[result_id]]
        result.deadline = min(requests_deadlines)

    def get_requests_by_deadline_proximity(self, deadline, time_proximity):
        time_start = deadline
        time_end = time_start + datetime.timedelta(seconds=time_proximity)
        result = set()
        for req in self._all_requests:
            if time_start < req.deadline < time_end:
                result.add(req)
        return result

    def get_result(self, result_id):
        return self._results_by_id[result_id]


class TaskQueue(abc.ABC):
    @abc.abstractmethod
    def __init__(self):
        pass

    @abc.abstractmethod
    def store_task(self, task_id, task_content):
        """
        Stores a task so it can be retreived.
        """
        pass

    @abc.abstractmethod
    def retreive_task(self):
        """
        """
        pass

    @abc.abstractmethod
    def task_is_solved(self, task_id):
        """
        """
        pass


class MemoryTaskQueue(TaskQueue):
    def __init__(self):
        self._tasks = queue.LifoQueue()

    def store_task(self, task):
        self._tasks.put(task)

    def task_is_solved(self, task_id):
        pass

    def retreive_task(self):
        return self._tasks.get()


class ResultsStorage(abc.ABC):
    @abc.abstractmethod
    def __init__(self):
        pass

    @abc.abstractmethod
    def store_result(self, result):
        """
        Stores a result so it can be retreived.
        """
        pass

    @abc.abstractmethod
    def get_results_concerning_request(self, request_id):
        """
        """
        pass

    @abc.abstractmethod
    def get_results_past(self, time):
        pass


class MemoryResultsStorage(ResultsStorage):
    def __init__(self):
        self._cathegory_storage = collections.defaultdict(list)
        self._all_results = set()

    def store_result(self, result):
        """
        Stores a result so it can be retreived.
        """
        for request_id in result.requests_ids:
            self._cathegory_storage[request_id] = result
        self._all_results.add(result)

    def get_results_concerning_request(self, request_id):
        """
        """
        return self._cathegory_storage[request_id]

    def get_results_past(self, time):
        def request_is_effective(req): return req.deadline > time
        results_past_time = filter(request_is_effective, list(self._all_results))
        results_past_time = sorted(results_past_time, key=lambda req: req.deadline)
        return results_past_time

    def _pop_result(self, result):
        for request_id in result.requests_ids:
            self._cathegory_storage.pop(request_id)
        self._all_results.discard(result)
        return result
