import sqlalchemy

from src.orm import Cookies, DBSession

SESSDATA = ""
BILI_JCT = ""
BUVID3 = ""
COOKIES_KEY = ["SESSDATA", "BILI_JCT", "BUVID3"]
for i in COOKIES_KEY:
    try:
        session = DBSession()
        _cookies = session.query(Cookies).filter(Cookies.key == i).one()
    except sqlalchemy.exc.NoResultFound:
        ...
    else:
        globals()[i] = str(_cookies.data)
    finally:
        session.close()
ROOMID = 1839144158
SEND_CD = 5
MSG_DICT = {
    "喵": 0.0,
}
PAUSE_DATE = 0.0


def set_data(key, data):
    globals()[key] = data
