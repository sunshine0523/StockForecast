import fire
import tushare as ts
import yaml
from db_utils import MongoConnector


def init_config():
    # py的相对路径的根是main函数的执行位置，可以通过os.getcwd()来查看
    # with open('/tmp/config/mongo_config.yaml', encoding='utf-8') as f:
    #     config = yaml.load(f.read(), Loader=yaml.FullLoader)
    with open('config.yaml', encoding='utf-8') as f:
        _config = yaml.load(f.read(), Loader=yaml.FullLoader)
    return _config


config = init_config()


def main():
    pro = ts.pro_api(config['stock_info_crawler']['ts_token'])

    df = pro.stock_basic(**{

    }, fields=[
        "ts_code",
        "symbol",
        "name",
        "area",
        "industry",
        "market",
        "list_date",
        "fullname",
        "enname",
        "cnspell",
        "exchange",
        "curr_type",
        "list_status",
        "delist_date",
        "is_hs"
    ])

    mongo_connector = MongoConnector(
        config['stock_info_crawler']['db_name'],
        config['stock_info_crawler']['collection_name']
    )
    mongo_connector.collection.insert_many(df.to_dict('records'))
    mongo_connector.client.close()


if __name__ == '__main__':
    fire.Fire(main)
