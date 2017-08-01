import abc
from contextlib import contextmanager
import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, ForeignKey, Float, Integer, DateTime, Enum

from . import requests
from . import storage

RequestsBase = declarative_base()


class SQLAlchemyStorage(abc.ABC):
    def __init__(self, sqlalchemy_connection_string, base):
        from sqlalchemy import create_engine
        self.declarative_base = base
        self.engine = create_engine(sqlalchemy_connection_string)
        self.declarative_base.metadata.create_all(self.engine)

    def wipe_database(self):
        self.declarative_base.metadata.drop_all(self.engine)
        self.declarative_base.metadata.create_all(self.engine)

    # taken from:  http://docs.sqlalchemy.org/en/latest/orm/session_basics.html
    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        from sqlalchemy.orm import sessionmaker
        session = sessionmaker(bind=self.engine)()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()


class Request(RequestsBase):
    __tablename__ = 'requests'

    id = Column(String, nullable=False, primary_key=True, unique=True)
    person_id = Column(String, nullable=False)


class IWantRequest(Request):
    __tablename__ = 'iwantrequests'

    id = Column(String, ForeignKey("requests.id"),
                primary_key=True, unique=True)
    deadline = Column(DateTime, nullable=False)
    activity_start = Column(DateTime, nullable=False)
    activity_duration = Column(Float, nullable=False)
    activity = Column(String, nullable=False)

    resolved_by = Column(Integer, ForeignKey("results.id"))

    def toIWantRequest(self):
        result = requests.IWantRequest(
            self.person_id, self.activity, self.deadline,
            self.activity_start, self.activity_duration)
        result.id = self.id
        result.resolved_by = self.resolved_by
        return result


class Result(RequestsBase):
    __tablename__ = 'results'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    deadline = Column(DateTime)
    status = Column(Enum(requests.Status))

    def toResult(self, requests_ids):
        result = requests.Result(
            self.id, requests_ids, self.deadline)
        result.status = self.status
        return result
    # notification_status


class SqlAlchemyRequestStorage(SQLAlchemyStorage, storage.RequestStorage):
    def __init__(self, backend_url):
        SQLAlchemyStorage.__init__(self, backend_url, RequestsBase)

    def store_request(self, request):
        if isinstance(request, requests.IWantRequest):
            return self._store_activity_request(request)
        else:
            raise ValueError(f"Can't store requests of type {type(request)}.")

    def _store_activity_request(self, request):
        with self.session_scope() as session:
            new_result_id = self._create_result()
            request_to_add = IWantRequest(
                id=request.id, person_id=request.person_id, deadline=request.deadline,
                activity=request.activity, activity_start=request.activity_start,
                activity_duration=request.activity_duration, resolved_by=new_result_id)
            session.add(request_to_add)
        request.resolved_by = new_result_id
        return request

    def get_activity_requests(self, activity=None):
        result = []
        with self.session_scope() as session:
            query_results = (
                session.query(Request, IWantRequest)
                .filter(Request.id == IWantRequest.id)
            )
            if activity is not None:
                query_results = query_results.filter(
                    IWantRequest.activity == activity)
            result = [record.toIWantRequest()
                      for base, record in query_results.all()]
        return result

    def remove_activity_request(self, request_id, person_id):
        with self.session_scope() as session:
            query_results = (
                session.query(IWantRequest)
                .filter(IWantRequest.id == request_id, IWantRequest.person_id == person_id)
            )
            all_results = query_results.all()
            assert len(all_results) == 1
            request_to_delete = all_results[0]
            session.delete(request_to_delete)

        concerned_result_id = request_to_delete.resolved_by
        self.__update_result_status(concerned_result_id)

    def __update_result_status(self, result_id):
        with self.session_scope() as session:
            query_results = (
                session.query(IWantRequest)
                .filter(IWantRequest.resolved_by == result_id)
            )

            requests_of_the_same_result = [req.toIWantRequest()
                                           for req in query_results.all()]
        with self.session_scope() as session:
            result_obj = self._get_result_object(session, result_id)
            self._update_result_status(result_obj, requests_of_the_same_result)

    def resolve_requests(self, requests_ids):
        with self.session_scope() as session:
            query_results = (
                session.query(IWantRequest)
                .filter(IWantRequest.id.in_(requests_ids))
            )
            resolved_by = None
            all_results = query_results.all()
            assert len(all_results) > 1
            result_objs = [self._get_result_object(session, req.resolved_by)
                           for req in all_results]
            involved_result_ids = [result.id for result in result_objs]
            resolved_by = self._find_fitting_result_id(result_objs)
            for record in all_results:
                record.resolved_by = resolved_by

        with self.session_scope() as session:
            for involved_id in involved_result_ids:
                self.__update_result_status(involved_id)
        self._update_result_deadline(resolved_by)
        return resolved_by

    def get_requests_of_result(self, result_id):
        with self.session_scope() as session:
            query_results = (
                session.query(IWantRequest)
                .filter(IWantRequest.resolved_by == result_id)
            )
            result = [record.toIWantRequest()
                      for record in query_results.all()]
        return result

    def get_result(self, result_id):
        with self.session_scope() as session:
            query_results = (
                session.query(IWantRequest)
                .filter(IWantRequest.resolved_by == result_id)
            )
            requests_ids = {req.id for req in query_results.all()}
            result = self._get_result_object(session, result_id).toResult(requests_ids)
        return result

    def _get_result_object(self, session, result_id):
        query_results = (
            session.query(Result)
            .filter(Result.id == result_id)
        )
        result = query_results.first()
        return result

    def get_requests_by_deadline_proximity(self, deadline, time_buffer_in_seconds):
        time_end = deadline
        time_start = time_end - datetime.timedelta(seconds=time_buffer_in_seconds)
        with self.session_scope() as session:
            query_results = (
                session.query(IWantRequest)
                .filter(IWantRequest.deadline > time_start)
                .filter(IWantRequest.deadline < time_end)
            )
            result = [record.toIWantRequest()
                      for record in query_results.all()]
        return result

    def get_results_by_deadline_proximity(self, deadline, time_buffer_in_seconds):
        time_end = deadline
        time_start = time_end - datetime.timedelta(seconds=time_buffer_in_seconds)
        with self.session_scope() as session:
            query_results = (
                session.query(Result)
                .filter(Result.deadline > time_start)
                .filter(Result.deadline < time_end)
            )
            result = [record.Result(self.get_requests_of_result(record.id))
                      for record in query_results.all()]
        return result

    def _create_result(self):
        # The context manager doesn't work for some reason
        from sqlalchemy.orm import sessionmaker
        session = sessionmaker(bind=self.engine)()
        result = Result(status=requests.Status.PENDING)
        session.add(result)
        session.commit()
        result_id = result.id
        session.close()
        return result_id

    def _update_result_deadline(self, result_id):
        with self.session_scope() as session:
            query_results = (
                session.query(IWantRequest.deadline)
                .filter(IWantRequest.resolved_by == result_id)
                .order_by(IWantRequest.deadline.asc())
            )
            result_object = self._get_result_object(session, result_id)
            if result_object.status == requests.Status.INVALID:
                return
            result_object.deadline = query_results.first()[0]
