import time
import datetime
import typing


class Request(object):
    def __init__(self, person_id, request_id=None):
        self.person_id = person_id
        self.id = request_id


# TODO: Add the activity start + request deadline data (+ activity duration?)
class IWantRequest(Request):
    def __init__(self, person_id, activity, lifespan_in_minutes):
        super().__init__(person_id)
        self.activity = activity
        self.timeframe_start = time.time()
        lifespan = datetime.timedelta(minutes=lifespan_in_minutes)
        self.timeframe_end = self.timeframe_start + lifespan.total_seconds()
        self.resolved_by = None

    def __eq__(self, rhs):
        result = True
        if (
                self.activity != rhs.activity
                or self.timeframe_start != rhs.timeframe_start
                or self.timeframe_end != rhs.timeframe_end
                ):
            result = False
        return result

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


class CancellationRequest(Request):
    def __init__(self, person_id, cancelling_request_id):
        super().__init__(person_id)
        self.cancelling_request_id = cancelling_request_id


class Result(object):
    def __init__(self, requests_ids: typing.List[str], effective_time):
        self.requests_ids = requests_ids
        self.effective_time = effective_time
