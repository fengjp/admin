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
            conditions.append(Peoplelist.type.like('%{}%'.format("在职")))
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
            if key == "department":
                conditions.append(Peoplelist.department.like('%{}%'.format(value)))
            if key == "supe_department":
                conditions.append(Peoplelist.supe_department.like('%{}%'.format(value)))
            if key == "sex":
                conditions.append(Peoplelist.sex.like('%{}%'.format(value)))
            if key == "type":
                conditions.append(Peoplelist.type.like('%{}%'.format(value)))
            if key == "level":
                conditions.append(Peoplelist.level.like('%{}%'.format(value)))
            if key == "supe_name":
                conditions.append(Peoplelist.supe_name.like('%{}%'.format(value)))

            todata = session.query(Peoplelist).filter(*conditions).order_by(Peoplelist.ctime.desc()).offset(limit_start).limit(int(limit)).all()
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
            case_dict["department"] = data_dict["department"]
            case_dict["supe_department"] = data_dict["supe_department"]
            case_dict["sex"] = data_dict["sex"]
            case_dict["type"] = data_dict["type"]
            case_dict["level"] = data_dict["level"]
            case_dict["supe_name"] = data_dict["supe_name"]

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
        department = data.get('department', None)
        supe_department = data.get('supe_department', None)
        sex = data.get('sex', None)
        type = data.get('type', None)
        level = data.get('level', None)
        supe_name = '公司'
        if othername  == '':
            othername = '0'
        if str(level)  == '':
            level = '0'
        if str(enddate)  == '':
            enddate = '2900-12-31'
        if str(supe_department)  == '':
            supe_department = '公司'


        with DBContext('r') as session:
            user_info = session.query(Peoplelist).filter(Peoplelist.id == int(othername) ).all()

        if user_info:
            for msg in user_info:
                temp_dict = {}
                data_dict = model_to_dict(msg)
                temp_dict["id"] = data_dict["id"]
                temp_dict["username"] = data_dict["username"]
            supe_name = temp_dict["username"]
            if supe_name ==  "NUll":
                supe_name = "公司"


        with DBContext('w', None, True) as session:
            session.add(Peoplelist(
                username=username,
                jobpost=jobpost,
                tel=tel,
                sex=sex,
                type=type,
                level=level,
                startdate=startdate,
                enddate=enddate,
                othername=othername,
                supe_name=supe_name,
                department=department,
                supe_department=supe_department,

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
        othername = int(data.get('othername', None))
        department = data.get('department', None)
        supe_department = data.get('supe_department', None)
        sex = data.get('sex', None)
        type = data.get('type', None)
        level = data.get('level', None)
        supe_name = data.get('supe_name', None)

        with DBContext('r') as session:
            user_info = session.query(Peoplelist).filter(Peoplelist.id == othername ).all()

        if user_info:
            for msg in user_info:
                temp_dict = {}
                data_dict = model_to_dict(msg)
                temp_dict["id"] = data_dict["id"]
                temp_dict["username"] = data_dict["username"]
            supe_name = temp_dict["username"]

        try:
            with DBContext('w', None, True) as session:
                session.query(Peoplelist).filter(Peoplelist.id == id).update({
                    Peoplelist.username: username,
                    Peoplelist.jobpost: jobpost,
                    Peoplelist.tel: tel,
                    Peoplelist.startdate: startdate,
                    Peoplelist.enddate: enddate,
                    Peoplelist.othername: othername,
                    Peoplelist.department: department,
                    Peoplelist.supe_department: supe_department,
                    Peoplelist.sex: sex,
                    Peoplelist.type:type,
                    Peoplelist.level: level,
                    Peoplelist.supe_name: supe_name,
                })
                session.commit()
        except Exception as e:
            return self.write(dict(code=-2, msg='修改失败，请检查数据是否合法或者重复'))
        self.write(dict(code=0, msg='编辑成功'))

class GetlistHandler(BaseHandler):
    def get(self, *args, **kwargs):
        data_list = []
        department_list = []
        namelist = []
        namelist2 = []
        tree_temp = []
        treelist = [{"id": 0, "name":"", "label": "公司","img": 'https://ss0.bdstatic.com/70cFvHSh_Q1YnxGkpoWK1HF6hhy/it/u=629230260,2582796696&fm=26&gp=0.jpg',"position":"", "children": []}]  # 同级数据存一起
        with DBContext('r') as session:
            conditions = []
            conditions.append(Peoplelist.type.like('%{}%'.format("在职")))
            todata = session.query(Peoplelist).filter(*conditions).order_by(Peoplelist.ctime.asc()).all()  #升序asc
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
            case_dict["department"] = data_dict["department"]
            case_dict["supe_department"] = data_dict["supe_department"]
            case_dict["sex"] = data_dict["sex"]
            case_dict["type"] = data_dict["type"]
            case_dict["level"] = data_dict["level"]

            case_dict["ctime"] = str(data_dict["ctime"])
            if case_dict["username"] not in namelist:
                data_list.append(case_dict)
                namelist.append(case_dict["username"])
            if case_dict["department"] not in namelist2:
                department_list.append(case_dict)
                namelist2.append(case_dict["department"])
            tree_temp.append({"id":data_dict["id"],
                              "username": data_dict["username"],
                              "level":data_dict["level"],
                              "sex":data_dict["sex"],
                              "othername":data_dict["othername"],
                              "department":data_dict["department"],
                              "jobpost": data_dict["jobpost"],
                              "supe_department":data_dict["supe_department"]})

        if len(tree_temp) > 0:
            temp_id_list = []
            for  i in tree_temp:#获取层级
                if  int(i["othername"])  not in  temp_id_list:
                    temp_id_list.append(int(i["othername"]))
            temp_id_list.sort()

            temp_data_list = {}
            for  i in  temp_id_list:
                temp_data_list[i] = []
                for  j in tree_temp:
                    if str(i) ==  str(j["othername"]):
                        if j["sex"] == '男':
                            temp_data_list[i].append({"id": j["id"], "name": j["username"], "label": j["department"],
                                                      "img": 'https://ss0.bdstatic.com/70cFvHSh_Q1YnxGkpoWK1HF6hhy/it/u=2010835987,458488842&fm=15&gp=0.jpg',
                                                      "position": j["jobpost"], "children": []})  # 同级数据存一起
                        if j["sex"] == '女':
                            temp_data_list[i].append({"id": j["id"], "name": j["username"], "label": j["department"],
                                                      "img": 'https://ss0.bdstatic.com/70cFvHSh_Q1YnxGkpoWK1HF6hhy/it/u=2745812195,432411379&fm=26&gp=0.jpg',
                                                      "position": j["jobpost"], "children": []})  # 同级数据存一起
            # ins_log.read_log('info', "1111111111111111111111111111111111111")
            # ins_log.read_log('info', temp_id_list)
            # ins_log.read_log('info', "1111111111111111111111111111111111111")
            for i  in  range(len(temp_id_list)-1,-1,-1):
                temp_str2 = temp_id_list[i]
                for  k  in  temp_data_list[temp_str2]:
                    if k["id"] in temp_id_list:
                        k["children"] = temp_data_list[k["id"]]

            if len(temp_data_list[0]) > 1:
                treelist[0]["children"] = temp_data_list[0]
                treelist = treelist[0]
            else:
                treelist = temp_data_list[0][0]
        # ins_log.read_log('info', "800000000000000000000000000000000000")
        # ins_log.read_log('info', treelist)
        # ins_log.read_log('info', "800000000000000000000000000000000000")
        if len(data_list) > 0:
            self.write(dict(code=0, msg='获取成功',  data=data_list,treelist=treelist,department=department_list))
        else:
            self.write(dict(code=-1, msg='没有相关数据', count=0, data=[],treelist=treelist,department=department_list))

class GetdateHandler(BaseHandler):
    def get(self, *args, **kwargs):
        data_list = []
        data2_list = []
        starttime  = self.get_argument('start', default=None, strip=True)  + "00:00:00"
        endtime = self.get_argument('end', default=None, strip=True)  + "23:59:59"

        with DBContext('r') as session:
            conditions = []
            conditions.append(Peoplelist.enddate >=  starttime )
            conditions.append(Peoplelist.enddate <= endtime)
            conditions.append(Peoplelist.type == "离职")
            todata = session.query(Peoplelist).filter(*conditions).all()


        for msg in todata:
            case_dict = {}
            data_dict = model_to_dict(msg)
            case_dict["id"] = data_dict["id"]
            case_dict["username"] = data_dict["username"]
            case_dict["jobpost"] = data_dict["jobpost"]
            case_dict["tel"] = data_dict["tel"]
            case_dict["startdate"] = str(data_dict["startdate"]).split()[0]
            case_dict["enddate"] = str(data_dict["enddate"]).split()[0]
            case_dict["othername"] = data_dict["othername"]
            case_dict["department"] = data_dict["department"]
            case_dict["supe_department"] = data_dict["supe_department"]
            case_dict["sex"] = data_dict["sex"]
            case_dict["type"] = data_dict["type"]
            case_dict["supe_name"] = data_dict["supe_name"]

            case_dict["ctime"] = str(data_dict["ctime"])
            if case_dict["type"] == "离职":
                if case_dict["username"] not in  data_list:
                    data_list.append(case_dict)

        with DBContext('r') as session:
            conditions = []
            conditions.append(Peoplelist.startdate <= endtime)
            conditions.append(Peoplelist.type == "在职")
            todata = session.query(Peoplelist).filter(*conditions).all()

        for msg in todata:
            case_dict = {}
            data_dict = model_to_dict(msg)
            case_dict["id"] = data_dict["id"]
            case_dict["username"] = data_dict["username"]
            case_dict["jobpost"] = data_dict["jobpost"]
            case_dict["tel"] = data_dict["tel"]
            case_dict["startdate"] = str(data_dict["startdate"]).split()[0]
            case_dict["enddate"] = str(data_dict["enddate"]).split()[0]
            case_dict["othername"] = data_dict["othername"]
            case_dict["department"] = data_dict["department"]
            case_dict["supe_department"] = data_dict["supe_department"]
            case_dict["sex"] = data_dict["sex"]
            case_dict["type"] = data_dict["type"]
            case_dict["supe_name"] = data_dict["supe_name"]

            case_dict["ctime"] = str(data_dict["ctime"])
            if case_dict["type"]  == "在职":
                if case_dict["username"] not in data2_list:
                    data2_list.append(case_dict)
        temp_list = [{"yessum":len(data2_list),"nosum":len(data_list),"allsum":len(data_list)+len(data2_list)}]
        temp2_list = [{"在职": len(data2_list), "离职": len(data_list), "总数": len(data_list) + len(data2_list)}]
        if len(temp_list) > 0:
            self.write(dict(code=0, msg='获取成功',  data=temp_list,dict=temp2_list,bar_list= {"在职":data2_list,"离职":data_list}))
        else:
            self.write(dict(code=-1, msg='没有相关数据', count=0, data=[],dict=[],bar_list={}))


class getiddataHandler(BaseHandler):
    def get(self, *args, **kwargs):
        data_list = []
        id  = int(self.get_argument('id', default=None, strip=True))
        with DBContext('r') as session:
            todata = session.query(Peoplelist).filter(Peoplelist.id == id).all()


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
            case_dict["department"] = data_dict["department"]
            case_dict["supe_department"] = data_dict["supe_department"]
            case_dict["sex"] = data_dict["sex"]
            case_dict["type"] = data_dict["type"]
            case_dict["level"] = data_dict["level"]

            case_dict["ctime"] = str(data_dict["ctime"])
            data_list.append(case_dict)


        if len(data_list) > 0:
            self.write(dict(code=0, msg='获取成功',  data=data_list))
        else:
            self.write(dict(code=-1, msg='没有相关数据', count=0, data=[]))


peoplelist_urls = [
    (r"/v2/accounts/peoplelist/", PeoplelistHandler),
    (r"/v2/accounts/getlist/", GetlistHandler),
    (r"/v2/accounts/getdatelist/", GetdateHandler),
    (r"/v2/accounts/getiddata/", getiddataHandler),
]

if __name__ == "__main__":
    pass
