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
            if key == "startdate":
                conditions.append(Peoplelist.startdate.like('%{}%'.format(value)))
            if key == "enddate":
                conditions.append(Peoplelist.enddate.like('%{}%'.format(value)))
            if key == "othername":
                conditions.append(Peoplelist.othername.like('%{}%'.format(value)))

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
            case_dict["startdate"] = str(data_dict["startdate"])
            case_dict["enddate"] = str(data_dict["enddate"])
            case_dict["othername"] = data_dict["othername"]

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
        startdate = data.get('startdate', None)
        enddate = data.get('enddate', None)
        othername = data.get('othername', None)

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
                startdate=startdate,
                enddate=enddate,
                othername=othername,

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
        startdate = data.get('startdate', None)
        enddate = data.get('enddate', None)
        othername = data.get('othername', None)

        try:
            with DBContext('w', None, True) as session:
                session.query(Peoplelist).filter(Peoplelist.id == id).update({
                    Peoplelist.username: username,
                    Peoplelist.jobpost: jobpost,
                    Peoplelist.tel: tel,
                    Peoplelist.startdate: startdate,
                    Peoplelist.enddate: enddate,
                    Peoplelist.othername: othername,
                })
                session.commit()
        except Exception as e:
            return self.write(dict(code=-2, msg='修改失败，请检查数据是否合法或者重复'))
        self.write(dict(code=0, msg='编辑成功'))

class GetlistHandler(BaseHandler):
    def get(self, *args, **kwargs):
        data_list = []
        treelist = [{
            "name": "flare",
            "children": [
                {
                    "name": "data",
                    "children": [
                        {
                            "name": "converters",
                            "children": [
                                {"name": "Converters", "value": 721},
                                {"name": "DelimitedTextConverter", "value": 4294}
                            ]
                        },
                        {
                            "name": "DataUtil",
                            "value": 3322
                        }
                    ]
                },
                {
                    "name": "display",
                    "children": [
                        {"name": "DirtySprite", "value": 8833},
                        {"name": "LineSprite", "value": 1732},
                        {"name": "RectSprite", "value": 3623}
                    ]
                },
                {
                    "name": "flex",
                    "children": [
                        {"name": "FlareVis", "value": 4116}
                    ]
                },
                {
                    "name": "query",
                    "children": [
                        {"name": "AggregateExpression", "value": 1616},
                        {"name": "And", "value": 1027},
                        {"name": "Arithmetic", "value": 3891},
                        {"name": "Average", "value": 891},
                        {"name": "BinaryExpression", "value": 2893},
                        {"name": "Comparison", "value": 5103},
                        {"name": "CompositeExpression", "value": 3677},
                        {"name": "Count", "value": 781},
                        {"name": "DateUtil", "value": 4141},
                        {"name": "Distinct", "value": 933},
                        {"name": "Expression", "value": 5130},
                        {"name": "ExpressionIterator", "value": 3617},
                        {"name": "Fn", "value": 3240},
                        {"name": "If", "value": 2732},
                        {"name": "IsA", "value": 2039},
                        {"name": "Literal", "value": 1214},
                        {"name": "Match", "value": 3748},
                        {"name": "Maximum", "value": 843},
                        {
                            "name": "methods",
                            "children": [
                                {"name": "add", "value": 593},
                                {"name": "and", "value": 330},
                                {"name": "average", "value": 287},
                                {"name": "count", "value": 277},
                                {"name": "distinct", "value": 292},
                                {"name": "div", "value": 595},
                                {"name": "eq", "value": 594},
                                {"name": "fn", "value": 460},
                                {"name": "gt", "value": 603},
                                {"name": "gte", "value": 625},
                                {"name": "iff", "value": 748},
                                {"name": "isa", "value": 461},
                                {"name": "lt", "value": 597},
                                {"name": "lte", "value": 619},
                                {"name": "max", "value": 283},
                                {"name": "min", "value": 283},
                                {"name": "mod", "value": 591},
                                {"name": "mul", "value": 603},
                                {"name": "neq", "value": 599},
                                {"name": "not", "value": 386},
                                {"name": "or", "value": 323},
                                {"name": "orderby", "value": 307},
                                {"name": "range", "value": 772},
                                {"name": "select", "value": 296},
                                {"name": "stddev", "value": 363},
                                {"name": "sub", "value": 600},
                                {"name": "sum", "value": 280},
                                {"name": "update", "value": 307},
                                {"name": "variance", "value": 335},
                                {"name": "where", "value": 299},
                                {"name": "xor", "value": 354},
                                {"name": "_", "value": 264}
                            ]
                        },
                        {"name": "Minimum", "value": 843},
                        {"name": "Not", "value": 1554},
                        {"name": "Or", "value": 970},
                        {"name": "Query", "value": 13896},
                        {"name": "Range", "value": 1594},
                        {"name": "StringUtil", "value": 4130},
                        {"name": "Sum", "value": 791},
                        {"name": "Variable", "value": 1124},
                        {"name": "Variance", "value": 1876},
                        {"name": "Xor", "value": 1101}
                    ]
                },
                {
                    "name": "scale",
                    "children": [
                        {"name": "IScaleMap", "value": 2105},
                        {"name": "LinearScale", "value": 1316},
                        {"name": "LogScale", "value": 3151},
                        {"name": "OrdinalScale", "value": 3770},
                        {"name": "QuantileScale", "value": 2435},
                        {"name": "QuantitativeScale", "value": 4839},
                        {"name": "RootScale", "value": 1756},
                        {"name": "Scale", "value": 4268},
                        {"name": "ScaleType", "value": 1821},
                        {"name": "TimeScale", "value": 5833}
                    ]
                }
            ]
        }]
        with DBContext('r') as session:
            todata = session.query(Peoplelist).filter().order_by(Peoplelist.ctime.desc()).all()
        for msg in todata:
            case_dict = {}
            data_dict = model_to_dict(msg)
            case_dict["id"] = data_dict["id"]
            case_dict["username"] = data_dict["username"]
            case_dict["jobpost"] = data_dict["jobpost"]
            case_dict["tel"] = data_dict["tel"]
            case_dict["startdate"] = str(data_dict["startdate"])
            case_dict["enddate"] = str(data_dict["enddate"])
            case_dict["othername"] = data_dict["othername"]

            case_dict["ctime"] = str(data_dict["ctime"])
            data_list.append(case_dict)

        if len(data_list) > 0:
            self.write(dict(code=0, msg='获取成功',  data=data_list,treelist=treelist))
        else:
            self.write(dict(code=-1, msg='没有相关数据', count=0, data=[],treelist=treelist))


peoplelist_urls = [
    (r"/v2/accounts/peoplelist/", PeoplelistHandler),
    (r"/v2/accounts/getlist/", GetlistHandler),
]

if __name__ == "__main__":
    pass
