import datetime

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey


Base = declarative_base()


class Nickname(Base):
    __tablename__ = 'nicknames'
    
    name = Column(String, nullable=False, primary_key=True)
    first_encountered = Column(DateTime, nullable=False)
    # multiple nicknames may share a user ID
    user_id = Column(Integer, autoincrement=True)


class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, autoincrement=True, primary_key=True)
    when = Column(DateTime, nullable=False)
    nickname = Column(Integer, ForeignKey("nicknames.name"), nullable=False)
    text = Column(String, nullable=False)


class DatabaseAccess(object):
    def __init__(self):
        self.engine = self._open_database()
            
    def _open_database(self):
        from sqlalchemy import create_engine
        engine = create_engine("sqlite:///lala.sqlite".format())
        Base.metadata.create_all(engine)
        return engine
        
    def _make_session(self):
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=self.engine)
        return Session()

    def add_new_nickname_to_session(self, session, nickname):
        nickname_to_add = Nickname(
            name=nickname,
            first_encountered=datetime.datetime.now(),
        )
        session.add(nickname_to_add)
        
    def save_message(self, message, nickname):
        session = self._make_session()
        try:
            query = session.query(sqlalchemy.exists().where(Nickname.name == nickname))
            nickname_is_known = query.scalar()
            if not nickname_is_known:
                self.add_new_nickname_to_session(session, nickname)
            
            message_to_add = Message(
                nickname=nickname, text=message,
                when=datetime.datetime.now())
            session.add(message_to_add)
            session.commit()
        except Exception:
            session.rollback()
            raise
    
    def load_n_last_messages(self, count=None):
        session = self._make_session()
        query_results = (
            session.query(Message)
            .order_by(Message.when)
        )
        if count is not None:
            query_results = query_results.limit(count)

        result = query_results.all()
        return list(result)
