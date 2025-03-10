import asyncio
import random
import time

import sqlalchemy
from bilibili_api import Credential, Danmaku
from bilibili_api.live import LiveDanmaku, LiveRoom
from loguru import logger as log

from src.const import BILI_JCT, BUVID3, MSG_DICT, PAUSE_DATE, ROOMID, SEND_CD, SESSDATA
from src.orm import Ban, DBSession, User

credential = Credential(sessdata=SESSDATA, bili_jct=BILI_JCT, buvid3=BUVID3)
sender = LiveRoom(ROOMID, credential=credential)
room = LiveDanmaku(ROOMID, credential=credential)


async def to_light(id):
    _sender = LiveRoom(id, credential=credential)
    log.info(f"正在点亮用户：{id}")
    log.debug(_sender)
    for i in range(11):
        log.info(f"点亮用户：{id}，第{i + 1}次")
        a = await _sender.send_danmaku(Danmaku(f"第{i + 1}个喵~"))
        log.debug(a)
        await asyncio.sleep(5)
    log.info(f"点亮用户：{id}，完成！")


class SendPool:
    def __init__(self):
        self._pool: list[str] = []
        self._flag = True

    async def add(self, msg: str):
        msg = msg.strip()
        if msg == "":
            log.info("消息为空，不添加进待发池。")
            return
        while len(msg) > 20:
            _temp_msg = msg[:20]
            msg = msg[20:]
            self._pool.append(_temp_msg)
            log.info(f"已添加：“{_temp_msg}”进入待发池。")
        else:
            self._pool.append(msg)
            log.info(f"已添加：“{msg}”进入待发池。")
        if self._flag:
            asyncio.create_task(self._loop())

    async def _loop(self):
        self._flag = False
        await asyncio.sleep(random.uniform(0.5, 2))
        while self._pool:
            await self._send()
            await asyncio.sleep(random.uniform(SEND_CD, SEND_CD + 2))
        else:
            self._flag = True

    async def _send(self):
        _msg: str = self._pool.pop(0)
        _send_data = await sender.send_danmaku(Danmaku(_msg))
        log.debug(_send_data)
        log.info(f"已发送弹幕：{_msg}")


# ----- 获取直播间各种信息 -----
@room.on("DANMU_MSG")
async def on_danmaku(event):
    # 收到弹幕
    _uid: int = event["data"]["info"][2][0]
    _msg: str = event["data"]["info"][1]
    if _msg in MSG_DICT.keys():
        if time.time() - MSG_DICT[_msg] > 300:
            MSG_DICT[_msg] = time.time()
            await sendPool.add(_msg)
    if _msg == "/help" or _msg == "/h":
        await sendPool.add("还没写")
    if _msg == "/pause" or _msg == "/p":
        global PAUSE_DATE
        PAUSE_DATE = time.time() + 120
        await sendPool.add("好的，我将暂停120秒")
    if _msg.startswith("/叫我"):
        _name: str = _msg[3:]
        _name = _name.strip()
        try:
            _session = DBSession()
            _user = _session.query(User).filter(User.uid == _uid).one()
        except sqlalchemy.exc.NoResultFound:
            _user = User(uid=_uid, name=_name)
            _session.add(_user)
            _session.commit()
        else:
            _user = _session.query(User).filter(User.uid == _uid).first()
            _user.name = _name  # type: ignore
            _session.commit()
        finally:
            _session.close()
            await sendPool.add(f"好的{_name[:16]}老师")
    if _msg == "/ban":
        try:
            _session = DBSession()
            _ban = _session.query(Ban).filter(Ban.uid == _uid).one()
        except sqlalchemy.exc.NoResultFound:
            _ban = Ban(uid=_uid)
            _session.add(_ban)
            _session.commit()
        else:
            pass
        finally:
            _session.close()
            await sendPool.add("好的老师")


@room.on("INTERACT_WORD")
async def interact_word(event):
    # 进入直播间
    log.debug(event)
    _name: str = event["data"]["data"]["uname"]
    _uid = event["data"]["data"]["uid"]
    _flag = False
    if time.time() < PAUSE_DATE:
        log.info(f"{_name}：进入直播间，但是在暂停期间，停止处理！")
        return
    try:
        _session = DBSession()
        _user = _session.query(Ban).filter(Ban.uid == _uid).one()
    except sqlalchemy.exc.NoResultFound:
        pass
    else:
        return
    finally:
        _session.close()
    try:
        _session = DBSession()
        _user = _session.query(User).filter(User.uid == _uid).one()
    except sqlalchemy.exc.NoResultFound:
        pass
    else:
        _name = str(_user.name)
        _flag = True
    finally:
        _session.close()
    if event["data"]["data"]["msg_type"] == 1:
        if event["data"]["data"]["spread_desc"] == "流量包推广":
            _flag = True
            log.info(f"{_name}：流量包推广，发送欢迎")
        if not _flag and event["data"]["data"]["uinfo"]["wealth"]["level"] <= 2:
            log.info(
                f"{_name}：会员等级：{event['data']['data']['uinfo']['wealth']['level']}，不发送欢迎"
            )
            return
        await sendPool.add(f"欢迎{_name[:8]}老师进入猫猫直播间~")
    elif event["data"]["data"]["msg_type"] == 2:
        await sendPool.add(f"感谢{_name[:8]}老师关注猫猫直播间~")
    else:
        log.warning("收到未知类型消息")


@room.on("SEND_GIFT")
async def on_gift(event):
    # 收到礼物
    pass


def bilibili_run():
    global sendPool
    sendPool = SendPool()
    asyncio.create_task(room.connect())
    return sendPool
