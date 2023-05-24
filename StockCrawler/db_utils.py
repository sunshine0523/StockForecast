from pymongo import *
import pymysql
import yaml


def init_config():
    # py的相对路径的根是main函数的执行位置，可以通过os.getcwd()来查看
    # with open('/tmp/config/mongo_config.yaml', encoding='utf-8') as f:
    #     config = yaml.load(f.read(), Loader=yaml.FullLoader)
    with open('config.yaml', encoding='utf-8') as f:
        config = yaml.load(f.read(), Loader=yaml.FullLoader)
    return config


class MySQLConnector(object):

    def __init__(self, db_name):
        self.config = init_config()
        self.db = pymysql.connect(
            host=self.config['mysql']['host'],
            user=self.config['mysql']['user'],
            passwd=self.config['mysql']['passwd'],
            port=self.config['mysql']['port'],
            database=db_name
        )
        self.cursor = self.db.cursor()

    def execute_sql(self, sql: str):
        try:
            self.cursor.execute(sql)
        except Exception as e:
            print(e)

    def close(self):
        self.cursor.close()


# mongo工具
class MongoConnector(object):

    def __init__(self, db_name, collection_name):
        self.config = init_config()
        self.client = MongoClient(self.config['mongo']['host'], self.config['mongo']['port'])
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def insert_one(self, data):
        self.collection.insert_one(data)

    def insert_many(self, data):
        self.collection.insert_many(data)

    def find_all(self):
        return self.collection.find()

    def find_by_page(self, cur, per, m_filter=None):
        if m_filter is None:
            return self.collection.find().skip((cur - 1) * per).limit(per)
        else:
            return self.collection.find(filter=m_filter).skip((cur - 1) * per).limit(per)

    def dis_connect(self):
        self.client.close()


class MongoUtils2(object):
    def __init__(self, db_name):
        self.config = init_config()
        self.client = MongoClient(self.config['host'], self.config['port'])
        self.db = self.client[db_name]

    def list_collections(self):
        return self.db.list_collections(session=None)

    # 获取该集合下有多少项
    def get_count(self, collection_name):
        return self.db.get_collection(collection_name).estimated_document_count()

    def insert_one(self, collection_name, data):
        self.db.get_collection(collection_name).insert_one(data)

    def insert_many(self, collection_name, data):
        self.db.get_collection(collection_name).insert_many(data)

    def find(self, collection_name, m_filter=None):
        if m_filter is None:
            return self.db.get_collection(collection_name).find()
        else:
            return self.db.get_collection(collection_name).find(filter=m_filter)

    def find_by_page(self, collection_name, cur, per):
        return self.db.get_collection(collection_name).find().skip((cur - 1) * per).limit(per)

    def dis_connect(self):
        self.client.close()
