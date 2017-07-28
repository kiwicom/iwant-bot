import time
import typing
import enum
import datetime


@enum.unique
class Status(enum.Enum):
    PENDING = 0
    INVALID = 1
    DONE = 2


class Request(object):
    def __init__(self, person_id, request_id=None):
        self.person_id = person_id
        self.id = request_id

    def __hash__(self):
        return hash((self.id, self.person_id))


class IWantRequest(Request):
    def __init__(self, person_id, activity, deadline,
                 activity_start, activity_duration_seconds):
        super().__init__(person_id)
        self.activity = activity

        self.deadline = deadline
        self.activity_start = activity_start
        self.activity_duration = activity_duration_seconds

        self.resolved_by = None

    def __hash__(self):
        return hash((super().__hash__(),
                     self.activity, self.deadline,
                     self.activity_start, self.activity_duration))

    def __eq__(self, rhs):
        result = True
        if (
                False
                or self.id != rhs.id
                or self.person_id != rhs.person_id
                or self.activity != rhs.activity
                or self.deadline != rhs.deadline
                or self.activity_start != rhs.activity_start
                or self.activity_duration != rhs.activity_duration
                or self.resolved_by != rhs.resolved_by
                ):
            result = False
        return result

    @property
    def activity_end(self):
        return self.activity_start + self.activity_duration

    def is_active_now(self):
        return self.is_active_by(time.time())

    def is_active_by(self, by_the_time):
        return by_the_time < self.deadline

    def overlaps_with(self, other_request):
        overlaps = (self.activity_end > other_request.activity_start
                    and self.activity_start < other_request.activity_end)
        return overlaps

    # TODO: Find a more descriptive name
    def conflicts_with(self, other_request):
        overlaps = self.overlaps_with(other_request)
        conflicts = (self is not other_request
                     and self.person_id == other_request.person_id
                     and overlaps)
        return conflicts


class CancellationRequest(Request):
    def __init__(self, person_id, cancelling_request_id):
        super().__init__(person_id)
        self.cancelling_request_id = cancelling_request_id


class Result(object):
    def __init__(self, requests_ids: typing.List[str], deadline: datetime.datetime):
        self.requests_ids = requests_ids
        self.deadline = deadline
