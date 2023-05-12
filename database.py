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
    # 如果message_id已存在，则不插入
    if get_message(message_id=message_id):
        raise KeyError(f"message_id={message_id} already exists")
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
        query = query.where(Message.message_id == message_id)
    if gid:
        query = query.where(Message.gid == gid)
    if recorder_id:
        query = query.where(Message.recorder_id == recorder_id)
    if limit:
        query = query.limit(limit)
    if keyword:
        query = query.where(Message.content.contains(keyword))
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




# 测试
def test():
    # 连接数据库
    connect()
    # 创建表
    create_tables()
    # 测试数据
    insert_message("三来","10086","我是三来",10086)
    insert_message("三来","10086","我是三来")
    insert_message("三来","10086","我不是三来")
    insert_message("四来lai","10011","我是四来")
    # 查询数据
    print("查询uid为10086的数据：")
    for message in get_message_by_uid("10086"):
        print(message)
    print("查询name为三来的数据：")
    for message in get_message_by_name("三来"):
        print(message)
    print("查询content为我是三来的数据：")
    for message in get_message_by_content("我是三来"):
        print(message)
    print("查询uid为10086，content为我是三来的数据：")
    for message in get_message_by_uid_and_content("10086", "我是三来"):
        print(message)
    print("查询uid为10086，name为三来的数据：")
    for message in get_message_by_uid_and_name("10086", "三来"):
        print(message)
    print("查询name为三来，content为我是三来的数据：")
    for message in get_message_by_name_and_content("三来", "我是三来"):
        print(message)
    print("获取指定uid的数据，按照time从大到小排序：")
    for message in get_message_by_uid_order_by_time("10086"):
        print(message)
    
            
if __name__ == '__main__':
    test()
    