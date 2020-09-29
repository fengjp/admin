#!/usr/bin/env python
# -*-coding:utf-8-*-


import json
import shortuuid
import base64
from websdk.jwt_token import gen_md5
from websdk.tools import check_password
from libs.base_handler import BaseHandler
from websdk.db_context import DBContext
from models.admin import Postlist,  model_to_dict
from websdk.consts import const
from websdk.cache_context import cache_conn
from websdk.tools import convert
from websdk.web_logs import ins_log
import os
import pandas as pd


class PostlistHandler(BaseHandler):
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
            if key == "postname":
                conditions.append(Postlist.postname.like('%{}%'.format(value)))
            if key == "outline":
                conditions.append(Postlist.outline.like('%{}%'.format(value)))
            if key == "remarks":
                conditions.append(Postlist.remarks.like('%{}%'.format(value)))

            todata = session.query(Postlist).filter(*conditions).order_by(Postlist.ctime.desc()).offset(limit_start).limit(int(limit)).all()
            tocount = session.query(Postlist).filter(*conditions).count()

        for msg in todata:
            case_dict = {}
            data_dict = model_to_dict(msg)
            case_dict["id"] = data_dict["id"]
            case_dict["postname"] = data_dict["postname"]
            case_dict["outline"] = data_dict["outline"]
            case_dict["remarks"] = data_dict["remarks"]
            case_dict["ctime"] = str(data_dict["ctime"])
            data_list.append(case_dict)

        if len(data_list) > 0:
            self.write(dict(code=0, msg='获取成功', count=tocount, data=data_list))
        else:
            self.write(dict(code=-1, msg='没有相关数据', count=0, data=[]))

    def post(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        postname = data.get('postname', None)
        outline = data.get('outline', None)
        remarks = str(data.get('remarks', None))


        with DBContext('w', None, True) as session:
            session.add(Postlist(
                postname=postname,
                outline=outline,
                remarks=remarks,
            ))
            session.commit()

        self.write(dict(code=0, msg='成功', count=0, data=[]))

    def delete(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        id = data.get('id', None)
        if not id:
            return self.write(dict(code=-1, msg='ID不能为空'))

        with DBContext('w', None, True) as session:
            session.query(Postlist).filter(Postlist.id == id).delete(synchronize_session=False)
        self.write(dict(code=0, msg='删除成功'))

    def put(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        id = data.get('id', None)
        postname = data.get('postname', None)
        outline = data.get('outline', None)
        remarks = str(data.get('remarks', None))

        try:
            with DBContext('w', None, True) as session:
                session.query(Postlist).filter(Postlist.id == id).update({
                    Postlist.postname: postname,
                    Postlist.outline: outline,
                    Postlist.remarks: remarks,

                })
                session.commit()
        except Exception as e:
            return self.write(dict(code=-2, msg='修改失败，请检查数据是否合法或者重复'))
        self.write(dict(code=0, msg='编辑成功'))


class Post_getId(BaseHandler):
    def get(self, *args, **kwargs):
        data_list = []
        with DBContext('r') as session:
            todata = session.query(Postlist).filter().order_by(Postlist.ctime.desc()).all()

        for msg in todata:
            case_dict = {}
            data_dict = model_to_dict(msg)
            case_dict["id"] = data_dict["id"]
            case_dict["postname"] = data_dict["postname"]
            case_dict["outline"] = data_dict["outline"]
            case_dict["remarks"] = data_dict["remarks"]
            case_dict["ctime"] = str(data_dict["ctime"])
            data_list.append(case_dict)

        if len(data_list) > 0:
            self.write(dict(code=0, msg='获取成功',  data=data_list))
        else:
            self.write(dict(code=-1, msg='没有相关数据', count=0, data=[]))


postlist_urls = [
    (r"/v2/accounts/postlist/", PostlistHandler),
    (r"/v2/accounts/post_getid/", Post_getId),
]

if __name__ == "__main__":
    pass
