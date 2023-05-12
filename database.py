from datetime import datetime
from peewee import *
import os

# 数据库文件路径
db_path = os.path.join(os.path.dirname(__file__), 'cot.sqlite')
db = SqliteDatabase(db_path)

class Message(Model):
    name = CharField()
    uid = CharField()
    gid = CharField()
    content = CharField()
    message_id = CharField(unique=True)
    recorder_id = CharField(null=True) # 记录者id
    # 时间戳格式的时间
    time = TimestampField(default=datetime.now().timestamp())
    
    class Meta:
        database = db

    def __str__(self):
        return f"Message(name={self.name}, uid={self.uid}, content={self.content}, time={self.time})"

def connect():
    db.connect()

def disconnect():
    db.close()

def create_tables():
    db.create_tables([Message])

# 插入数据
def insert_message(name, uid, content, message_id, gid, recorder_id, time=None):
    # 如果mid存在，抛出KeyError
    if Message.select().where(Message.message_id == message_id):
        raise KeyError(f"message_id={message_id} does not exist")
    if time:
        Message.create(name=name, uid=uid, content=content, time=time, message_id=message_id, gid=gid, recorder_id=recorder_id)
    else:
        Message.create(name=name, uid=uid, content=content, message_id=message_id, gid=gid, recorder_id=recorder_id)
    
# 查询数据
def get_message(name=None, uid=None, content=None, message_id=None, gid=None, recorder_id=None, keyword=None, limit: int=50):
    query = Message.select()
    if name:
        query = query.where(Message.name == name)
    if uid:
        query = query.where(Message.uid == uid)
    if content:
        query = query.where(Message.content == content)
    if message_id:
        # 如果mid不存在，抛出KeyError
        if not Message.select().where(Message.message_id == message_id):
            raise KeyError(f"message_id={message_id} does not exist")
        query = query.where(Message.message_id == message_id)
    if gid:
        query = query.where(Message.gid == gid)
    if recorder_id:
        query = query.where(Message.recorder_id == recorder_id)
    if keyword:
        query = query.where(Message.content.contains(keyword))
    # 按照时间从大到小排序
    query = query.order_by(Message.time.desc())
    if limit:
        query = query.limit(limit)
    return query

# 关键词查询
def get_message_by_keyword(keyword, limit: int=50):
    return get_message().where(Message.content.contains(keyword)).order_by(Message.time.desc()).limit(limit)

# 获取指定gid的数据
def get_message_by_gid_and_keyword(gid, keyword, limit: int=50):
    return get_message(gid=gid).where(Message.content.contains(keyword)).order_by(Message.time.desc()).limit(limit)

# 删除数据
def delete_message(name=None, uid=None, content=None, message_id=None, gid=None, recorder_id=None):
    query = Message.delete()
    if name:
        query = query.where(Message.name == name)
    if uid:
        query = query.where(Message.uid == uid)
    if content:
        query = query.where(Message.content == content)
    if message_id:
        query = query.where(Message.message_id == message_id)
    if gid:
        query = query.where(Message.gid == gid)
    if recorder_id:
        query = query.where(Message.recorder_id == recorder_id)
    return query.execute()
    