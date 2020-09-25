#!/usr/bin/env python
# -*-coding:utf-8-*-


import json
import shortuuid
import base64
from websdk.jwt_token import gen_md5
from websdk.tools import check_password
from libs.base_handler import BaseHandler
from websdk.db_context import DBContext
from models.admin import Peoplelist, model_to_dict
from websdk.consts import const
from websdk.cache_context import cache_conn
from websdk.tools import convert
from websdk.web_logs import ins_log
import os
import pandas as pd


class PeoplelistHandler(BaseHandler):
    def get(self, *args, **kwargs):
        data_list = []
        key = self.get_argument('key', default=None, strip=True)
        value = self.get_argument('value', default=None, strip=True)
        page_size = self.get_argument('page', default=1, strip=True)
        limit = self.get_argument('limit', default=30, strip=True)
        limit_start = (int(page_size) - 1) * int(limit)
        user_list = []
        with DBContext('r') as session:
            conditions = []
            if key == "username":
                conditions.append(Peoplelist.username.like('%{}%'.format(value)))
            if key == "jobpost":
                conditions.append(Peoplelist.jobpost.like('%{}%'.format(value)))
            if key == "tel":
                conditions.append(Peoplelist.tel.like('%{}%'.format(value)))

            todata = session.query(Peoplelist).filter(*conditions).order_by(Peoplelist.ctime.desc()).offset(
                limit_start).limit(int(limit)).all()
            tocount = session.query(Peoplelist).filter(*conditions).count()

        for msg in todata:
            case_dict = {}
            data_dict = model_to_dict(msg)
            case_dict["id"] = data_dict["id"]
            case_dict["username"] = data_dict["username"]
            case_dict["jobpost"] = data_dict["jobpost"]
            case_dict["tel"] = data_dict["tel"]

            case_dict["ctime"] = str(data_dict["ctime"])
            data_list.append(case_dict)

        if len(data_list) > 0:
            self.write(dict(code=0, msg='获取成功', count=tocount, data=data_list))
        else:
            self.write(dict(code=-1, msg='没有相关数据', count=0, data=[]))

    def post(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        username = data.get('username', None)
        jobpost = data.get('jobpost', None)
        tel = data.get('tel', None)

        with DBContext('r') as session:
            user_info2 = session.query(Peoplelist).filter(Peoplelist.tel == tel).first()
            # user_info3 = session.query(peoplelist).filter(peoplelist.email == email).first()

        if user_info2:
            return self.write(dict(code=-3, msg='手机号已存在，请重新输入。'))


        with DBContext('w', None, True) as session:
            session.add(Peoplelist(
                username=username,
                jobpost=jobpost,
                tel=tel,

            ))
            session.commit()

        self.write(dict(code=0, msg='成功', count=0, data=[]))

    def delete(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        id = data.get('id', None)
        if not id:
            return self.write(dict(code=-1, msg='ID不能为空'))

        with DBContext('w', None, True) as session:
            session.query(Peoplelist).filter(Peoplelist.id == id).delete(synchronize_session=False)
        self.write(dict(code=0, msg='删除成功'))

    def put(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        id = data.get('id', None)
        username = data.get('username', None)
        jobpost = data.get('jobpost', None)
        tel = data.get('tel', None)

        try:
            with DBContext('w', None, True) as session:
                session.query(Peoplelist).filter(Peoplelist.id == id).update({
                    Peoplelist.username: username,
                    Peoplelist.jobpost: jobpost,
                    Peoplelist.tel: tel,
                })
                session.commit()
        except Exception as e:
            return self.write(dict(code=-2, msg='修改失败，请检查数据是否合法或者重复'))
        self.write(dict(code=0, msg='编辑成功'))


peoplelist_urls = [
    (r"/v2/accounts/peoplelist/", PeoplelistHandler),
]

if __name__ == "__main__":
    pass
