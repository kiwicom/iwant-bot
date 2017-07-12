import abc
from contextlib import contextmanager

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float

from . import requests
from . import storage

RequestsBase = declarative_base()


class SQLAlchemyStorage(abc.ABC):
    def __init__(self, sqlalchemy_connection_string, base):
        from sqlalchemy import create_engine
        self.engine = create_engine(sqlalchemy_connection_string)
        base.metadata.create_all(self.engine)

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

    id = Column(String, nullable=False, primary_key=True)
    person_id = Column(String, nullable=False)


class IWantRequest(RequestsBase):
    __tablename__ = 'iwantrequests'

    id = Column(Integer, ForeignKey("requests.id"),
                autoincrement=True, primary_key=True)
    deadline = Column(Float, nullable=False)
    activity_start = Column(Float, nullable=False)
    activity_duration = Column(Float, nullable=False)
    activity = Column(String, nullable=False)

    def toIWantRequest(self, person_id=None):
        result = requests.IWantRequest(
            person_id, self.activity, self.deadline,
            self.activity_start, self.activity_duration)
        result.id = self.id
        return result


class SqlAlchemyRequestStorage(SQLAlchemyStorage, storage.RequestStorage):
    def __init__(self, backend_url):
        SQLAlchemyStorage.__init__(self, backend_url, RequestsBase)

    def store_request(self, request):
        if isinstance(request, requests.IWantRequest):
            self._store_activity_request(request)
        else:
            raise ValueError(f"Can't store requests of type {type(request)}.")

    def _store_activity_request(self, request):
        with self.session_scope() as session:
            request_base_to_add = Request(
                id=request.id, person_id=request.person_id)
            request_to_add = IWantRequest(
                id=request.id, deadline=request.deadline, activity=request.activity,
                activity_start=request.activity_start, activity_duration=request.activity_duration)
            session.add(request_base_to_add)
            session.add(request_to_add)

    def get_activity_requests(self, activity=None):
        result = []
        with self.session_scope() as session:
            query_results = session.query(Request, IWantRequest).filter(Request.id == IWantRequest.id)
            if activity is not None:
                query_results = query_results.filter(
                    IWantRequest.activity == activity)
            result = [record.toIWantRequest(base.person_id) for base, record in query_results.all()]
        return result

    def remove_activity_request(self, request_id, person_id):
        pass
