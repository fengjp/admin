#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Desc    : 字典配置
"""

import json
from libs.base_handler import BaseHandler
from websdk.db_context import DBContext
from models.admin import Components, RolesComponents, model_to_dict
from models.app_config import DictConfig, model_to_dict
from websdk.web_logs import ins_log
from websdk.cache_context import cache_conn
from websdk.tools import convert


## 同步字典配置到redis
def sync_dictconfg_to_redis():
    redis_conn = cache_conn()
    with DBContext('r') as session:
        dict_info = session.query(DictConfig).all()

    for msg in dict_info:
        data_dict = model_to_dict(msg)
        redis_conn.hset('dictconf_hash', data_dict['dictkey'], data_dict['dictvalue'])


class DictConfigRDHandler(BaseHandler):
    def get(self, *args, **kwargs):
        key = self.get_argument('key', default=None, strip=True)
        count = 0
        dict_list = []
        redis_conn = cache_conn()
        dictconfig_all = redis_conn.hgetall('dictconf_hash')
        dictconfig_all = convert(dictconfig_all)
        return self.write(dict(code=0, msg='获取成功', data=dictconfig_all))


class DictConfigHandler(BaseHandler):
    def get(self, *args, **kwargs):
        key = self.get_argument('key', default=None, strip=True)
        value = self.get_argument('value', default=None, strip=True)
        dict_list = []
        with DBContext('r') as session:
            if key and value:
                count = session.query(DictConfig).filter_by(**{key: value}).count()
                dict_info = session.query(DictConfig).filter_by(**{key: value}).order_by(DictConfig.id.desc()).all()
            else:
                count = session.query(DictConfig).count()
                dict_info = session.query(DictConfig).order_by(DictConfig.id.desc()).all()

        for msg in dict_info:
            data_dict = model_to_dict(msg)
            dict_list.append(data_dict)

        return self.write(dict(code=0, msg='获取成功', data=dict_list, count=count))

    def post(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        dictname = data.get('dictname', None)
        dictkey = data.get('dictkey', None)
        dictvalue = str(data.get('dictvalue', None))
        ins_log.read_log('info', data)
        # dictvalue = dictvalue.replace('\'', '\"').replace('\n', '').replace('\r', '').replace(' ', '')
        # try:
        #     json.loads(dictvalue)
        # except:
        #     return self.write(dict(code=-4, msg="字典值 格式错误"))

        if not dictkey:
            return self.write(dict(code=-1, msg='字典KEY不能为空'))

        with DBContext('r') as session:
            is_exist = session.query(DictConfig.dictkey).filter(DictConfig.dictkey == dictkey).first()

        if is_exist:
            return self.write(dict(code=-3, msg='"{}"已存在'.format(dictkey)))

        with DBContext('w', None, True) as session:
            session.add(DictConfig(dictname=dictname, dictkey=dictkey, dictvalue=dictvalue))
            session.commit()

        sync_dictconfg_to_redis()

        return self.write(dict(code=0, msg='添加成功'))

    def put(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        id = data.get('id', None)
        dictname = data.get('dictname', None)
        dictkey = data.get('dictkey', None)
        dictvalue = str(data.get('dictvalue', None))
        ins_log.read_log('info', data)
        # try:
        #     json.loads(dictvalue)
        # except:
        #     return self.write(dict(code=-4, msg="字典值 格式错误"))

        if not dictkey:
            return self.write(dict(code=-1, msg='字典KEY不能为空'))

        with DBContext('w', None, True) as session:
            session.query(DictConfig).filter(DictConfig.id == int(id)).update({
                DictConfig.dictname: dictname, DictConfig.dictkey: dictkey, DictConfig.dictvalue: dictvalue,
            }, synchronize_session=False)

        sync_dictconfg_to_redis()

        return self.write(dict(code=0, msg='编辑成功'))

    def delete(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        id = data.get('id', None)
        if not id:
            return self.write(dict(code=-1, msg='ID不能为空'))

        redis_conn = cache_conn()
        with DBContext('r') as session:
            dictkey = session.query(DictConfig.dictkey).filter(DictConfig.id == id).first()
            # ins_log.read_log('info', dictkey)
            redis_conn.hdel('dictconf_hash', dictkey[0])

        with DBContext('w', None, True) as session:
            session.query(DictConfig).filter(DictConfig.id == id).delete(synchronize_session=False)

        return self.write(dict(code=0, msg='删除成功'))


dictconfig_urls = [
    (r"/v2/dictconfig/", DictConfigHandler),
    (r"/v2/dictconfig/rd/", DictConfigRDHandler),
]

if __name__ == "__main__":
    pass
