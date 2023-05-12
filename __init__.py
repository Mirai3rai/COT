from typing import List
from aiocqhttp.exceptions import ActionFailed
from hoshino import Service, get_bot, priv
from hoshino.typing import CQEvent
from .database import *
import re

sv = Service('record', help_='回复一条消息，发送"记录"可记录该消息，发送"看记录"可查看记录，最多50条')
bot = get_bot()

@bot.on_startup
async def init():
    connect()
    create_tables()

@sv.on_message('group')
async def record(bot, ev: CQEvent):
    message_id = None
    match = re.match(r"\[CQ:reply,id=(?P<id>.*)\]\[CQ:", str(ev.message))
    if match is not None and "记录" in ev.message.extract_plain_text():
        message_id = match["id"]
        pre_msg = await bot.get_msg(message_id=message_id)
        print(pre_msg)
        hb = pre_msg["message"]
        if fidg := re.match(r'\[CQ:forward,id=(.*)\]', hb):
            try:
                fid = fidg[1]
                fmsg1 = await bot.get_forward_msg(id = fid,self_id=ev.self_id)
                fmsg = fmsg1["messages"]
                if len(fmsg) == 0:
                    await bot.finish(ev, '呃呃呃', at_sender=True)
                exist = 0
                for msg in fmsg:
                    print(msg)
                    nkn = msg["sender"]['nickname']
                    uid = str(msg["sender"]['user_id'])
                    gid = str(msg["group_id"])
                    time = msg["time"]
                    try:
                        # 插入数据
                        insert_message(name=nkn, uid=uid, content=msg["content"], time=time, message_id=f'{uid}-{time}', gid=gid)
                    except KeyError:
                        await bot.send(ev, f'内容为{msg["content"]}的消息已存在~', at_sender=True)
                        exist += 1
                await bot.send(ev, '该合并转发中的新消息记录完成~', at_sender=True) if exist != len(fmsg) else await bot.send(ev, '该合并转发中的消息已存在~', at_sender=True)
            except ActionFailed:
                await bot.finish(ev, '该消息已过期，请重新转发~', at_sender=True)
        else:
            try:
                nkn = pre_msg["sender"]['nickname']
                uid = str(pre_msg["sender"]['user_id'])
                time = pre_msg["time"]
                gid = str(pre_msg["group_id"])
                try:
                    # 插入数据
                    insert_message(name=nkn, uid=uid, content=hb, time=time, message_id=f'{uid}-{time}', gid=gid)
                except KeyError:
                    await bot.finish(ev, '该消息已存在~', at_sender=True)
                await bot.send(ev, '该消息记录完成~', at_sender=True)
            except ActionFailed:
                await bot.finish(ev, '该消息已过期，请重新转发~', at_sender=True)


@sv.on_prefix(('查记录'))
async def get_records(bot, ev: CQEvent):
    group_id = str(ev.group_id)
    user_id = None

    if ev.message[0].type == 'at':
        bot_id = str(ev.self_id)
        if ev.message[0].data['qq'] == bot_id:
            await bot.finish(ev, "不能at机器人", at_sender=True)
        else:
            user_id = str(ev.message[0].data['qq']) if ev.message[0].data['qq'] != 'all' else None

    keyword = ev.message.extract_plain_text().strip()

    if not keyword and not user_id: # 查询全部
        query = get_message_by_gid_order_by_time(group_id)
    elif not keyword: # 查询某人
        query = get_message_by_gid_and_uid_order_by_time(group_id, user_id)
    elif not user_id: # 查询关键词
        query = get_message_by_gid_and_keyword(group_id, keyword)
    else:
        query = get_message_by_gid_and_uid_and_keyword(group_id, user_id, keyword)

    await send_records(ev, query)

@sv.on_prefix(('删记录'))
async def del_records(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await sv.bot.send(ev, '只有超级用户才能删除记录哦~', at_sender=True)
        return
    mid = ev.message.extract_plain_text().strip()
    if not mid:
        await sv.bot.send(ev, '请输入要删除的消息id', at_sender=True)
        return
    try:
        delete_message_by_message_id(mid)
        await sv.bot.send(ev, f'已删除消息id为{mid}的记录~', at_sender=True)
    except KeyError:
        await sv.bot.send(ev, f'消息id为{mid}的记录不存在~', at_sender=True)

def merge_msg(data, msg, time, name, uid):
    data.append({
        "type": "node",
        "data": {
            "name": f"{name}",
            "uin": f"{uid}",
            "time": f"{time}",
            "content": msg
        }
    })


async def send_records(ev: CQEvent, query):
    # 如果没有记录，发送空消息
    if not query:
        await sv.bot.finish(ev, '没有记录~')
    msgs=[]
    # 对同一个uid，name取最新的一条记录的name
    last_name = {}
    for record in query:
        # 获取发送者的qq号
        uid = record.uid
        # 获取发送者的群昵称
        name = last_name.get(uid, record.name) # 如果没有记录，就取默认的name
        last_name[uid] = name
        # 获取消息内容
        msg = record.content
        # 获取消息发送时间
        time = int(record.time.timestamp())
        # 获取消息id
        message_id = record.message_id
        # 合并消息
        merge_msg(msgs, f"{message_id}", time, "消息id", ev.self_id)
        merge_msg(msgs, msg, time, name, uid)
    # 发送消息
    await sv.bot.send_group_forward_msg(group_id=ev.group_id, messages=msgs)