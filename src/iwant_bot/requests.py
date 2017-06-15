import time
import datetime


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


class CancellationRequest(Request):
    def __init__(self, person_id, cancelling_request_id):
        super().__init__(person_id)
        self.cancelling_request_id = cancelling_request_id
