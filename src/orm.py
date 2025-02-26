import os

import sqlalchemy
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

_Base = declarative_base()


class User(_Base):
    __tablename__ = "user"
    uid = Column(Integer, primary_key=True)
    name = Column(String(20))


class Ban(_Base):
    __tablename__ = "ban"
    uid = Column(Integer, primary_key=True)


class Cookies(_Base):
    __tablename__ = "cookies"
    key = Column(String(100), primary_key=True)
    data = Column(String(100))


_engine = create_engine(f"sqlite:///{os.path.join(os.getcwd(), 'db', 'data.db')}")
_Base.metadata.create_all(_engine)
DBSession = sessionmaker(_engine)


def set_cookies(key: str, data: str):
    try:
        session = DBSession()
        _cookies = session.query(Cookies).filter(Cookies.key == key).one()
    except sqlalchemy.exc.NoResultFound:
        _cookies = Cookies(key=key, data=data)
        session.add(_cookies)
        session.commit()
    else:
        _cookies = session.query(Cookies).filter(Cookies.key == key).first()
        _cookies.data = data  # type: ignore
        session.commit()
    finally:
        session.close()
