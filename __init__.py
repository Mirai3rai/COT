from typing import List
from aiocqhttp.exceptions import ActionFailed
from hoshino import Service, priv
from hoshino.typing import CQEvent

sv = Service('record', help_='发送"记录"可记录上一条消息，发送"看记录"可查看记录，最多50条')

# 记录最大数目
MAX_RECORDS = 50

# 存储记录的列表
records = []


@sv.on_message('group')
async def record(bot, ev: CQEvent):
    mid = ev.message_id
    uid = ev.user_id
    if not ev.message:
        sv.logger.error(f"message is empty: {ev.raw_message}")
        return
    seg = ev.message[0]
    if seg.type != 'reply':
        return
    tmid = seg.data['id']
    cmd = ev.message.extract_plain_text()
    is_at_me = 0
    flag2 = 0
    for recmd in ['记录']:
        if recmd in cmd:
            flag2 = 1
        # 发送所有记录
        # await send_records(ev)
    if not flag2:
        return
    try:
        tmsg = await bot.get_msg(self_id=ev.self_id, message_id=int(tmid))
        print(tmsg)
    except ActionFailed:
        await bot.finish(ev, '该消息已过期，请重新转发~')
    print(tmsg)
    if ev.is_group_chat and priv.check_priv(ev, priv.ADMIN):
        msg = await get_last_message(ev)
        if msg:
            # 记录消息内容和发送者
            record = f'{msg["sender"]["nickname"]}: {msg["message"]}'
            # 如果记录数量已经达到最大值，删除最旧的一条
            if len(records) >= MAX_RECORDS:
                records.pop(0)
            # 将新记录添加到列表
            records.append(record)
            # 发送确认消息
            await sv.bot.send(ev, '已记录上一条消息')


def merge_msg(data, msg, times, name, uid):
    data.append({
        "type": "node",
        "data": {
            "name": f"{name}",
            "uin": f"{uid}",
            "time": f"{times}",
            "content": msg
        }
    })
    return data


async def send_records(ev: CQEvent):
    # 如果没有记录，发送空消息
    if not records:
        await sv.bot.send(ev, '没有记录')
        return

    messages = [f'{i + 1}. {record}' for i, record in enumerate(records)]
    message = '\n'.join(messages)

    # 发送记录消息
    await sv.bot.send(ev, message)
