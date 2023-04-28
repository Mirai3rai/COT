from datetime import datetime
from peewee import *

db = SqliteDatabase('test.sqlite')

class Message(Model):
    name = CharField()
    uid = CharField()
    content = CharField()
    
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
def insert_message(name, uid, content, time=None):
    if time:
        Message.create(name=name, uid=uid, content=content, time=time)
    else:
        Message.create(name=name, uid=uid, content=content)
    
# 查询数据
def get_message(name=None, uid=None, content=None):
    query = Message.select()
    if name:
        query = query.where(Message.name == name)
    if uid:
        query = query.where(Message.uid == uid)
    if content:
        query = query.where(Message.content == content)
    return query

# 删除数据
def delete_message(name=None, uid=None, content=None):
    query = Message.delete()
    if name:
        query = query.where(Message.name == name)
    if uid:
        query = query.where(Message.uid == uid)
    if content:
        query = query.where(Message.content == content)
    return query.execute()

# 查询uid为uid的数据
def get_message_by_uid(uid):
    return get_message(uid=uid)

# 查询name为name的数据
def get_message_by_name(name):
    return get_message(name=name)

# 查询content为content的数据
def get_message_by_content(content):
    return get_message(content=content)

# 查询uid为uid，content为content的数据
def get_message_by_uid_and_content(uid, content):
    return get_message(uid=uid, content=content)

# 查询uid为uid，name为name的数据
def get_message_by_uid_and_name(uid, name):
    return get_message(uid=uid, name=name)

# 查询name为name，content为content的数据
def get_message_by_name_and_content(name, content):
    return get_message(name=name, content=content)

# 获取指定uid的数据，按照time排序
def get_message_by_uid_order_by_time(uid):
    return get_message(uid=uid).order_by(Message.time.desc())

# 删除uid为uid的数据
def delete_message_by_uid(uid):
    return delete_message(uid=uid)

# 删除name为name的数据
def delete_message_by_name(name):
    return delete_message(name=name)

# 删除content为content的数据
def delete_message_by_content(content):
    return delete_message(content=content)

# 删除uid为uid，content为content的数据
def delete_message_by_uid_and_content(uid, content):
    return delete_message(uid=uid, content=content)

# 删除uid为uid，name为name的数据
def delete_message_by_uid_and_name(uid, name):
    return delete_message(uid=uid, name=name)

# 删除name为name，content为content的数据
def delete_message_by_name_and_content(name, content):
    return delete_message(name=name, content=content)



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
    