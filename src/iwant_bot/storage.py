import abc
import collections
import queue

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


# TODO: Remove -> Invalidate
# store results ID of the result the request is solved by.
class MemoryRequestsStorage(RequestStorage):
    def __init__(self):
        self._requests = collections.defaultdict(list)

    def store_request(self, request):
        if isinstance(request, requests.IWantRequest):
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

    def remove_activity_request(self, request_id, person_id):
        activity_requests = self._requests["activity"]

        def request_has_right_id(req): return req.id == request_id
        requests_with_right_id = list(filter(request_has_right_id, activity_requests))
        assert len(requests_with_right_id) == 1, \
            "There should be exactly one request of such ID to remove"
        request_to_remove = requests_with_right_id[0]
        assert request_to_remove.person_id == person_id, \
            f"The request of the given ID can't be removed by {person_id}"
        activity_requests.remove(request_to_remove)

    def wipe_database(self):
        pass

    def resolve_requests(self, requests):
        pass


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
        def request_is_effective(req): return req.effective_time > time
        results_past_time = filter(request_is_effective, list(self._all_results))
        results_past_time = sorted(results_past_time, key=lambda req: req.effective_time)
        return results_past_time

    def _pop_result(self, result):
        for request_id in result.requests_ids:
            self._cathegory_storage.pop(request_id)
        self._all_results.discard(result)
        return result
