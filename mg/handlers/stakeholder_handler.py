#!/usr/bin/env python
# -*-coding:utf-8-*-
"""
role   : 用户管理API

status = '0'    正常
status = '10'   逻辑删除
status = '20'   禁用
"""

import json
import shortuuid
import base64
from websdk.jwt_token import gen_md5
from websdk.tools import check_password
from libs.base_handler import BaseHandler
from websdk.db_context import DBContext
from models.admin import UserRoles,Stakeholder, model_to_dict
from websdk.consts import const
from websdk.cache_context import cache_conn
from websdk.tools import convert
from websdk.web_logs import ins_log
import  os
import pandas as pd


def sync_stakeholder_to_redis():
    redis_conn = cache_conn()
    with DBContext('r') as session:
        dict_info = session.query(Stakeholder).all()
    for msg in dict_info:
        data_dict = model_to_dict(msg)
        tempstr  =  data_dict["username"] + '--' +  data_dict["company"]
        redis_conn.hset('stakeholder_hash', data_dict["id"], tempstr)

class StakeholderHandler(BaseHandler):
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
                conditions.append(Stakeholder.username.like('%{}%'.format(value)))
            if key == "company":
                conditions.append(Stakeholder.company.like('%{}%'.format(value)))
            if key == "department":
                conditions.append(Stakeholder.department.like('%{}%'.format(value)))
            if key == "position":
                conditions.append(Stakeholder.position.like('%{}%'.format(value)))
            if key == "duty":
                conditions.append(Stakeholder.duty.like('%{}%'.format(value)))
            if key == "tel":
                conditions.append(Stakeholder.tel.like('%{}%'.format(value)))
            if key == "addr":
                conditions.append(Stakeholder.addr.like('%{}%'.format(value)))
            if key == "email":
                conditions.append(Stakeholder.email.like('%{}%'.format(value)))
            if key == "remarks":
                conditions.append(Stakeholder.remarks.like('%{}%'.format(value)))

            todata = session.query(Stakeholder).filter(*conditions).order_by(Stakeholder.ctime.desc()).offset(limit_start).limit(int(limit)).all()
            tocount = session.query(Stakeholder).filter(*conditions).count()

        for msg in todata:
            case_dict = {}
            data_dict = model_to_dict(msg)
            case_dict["id"] = data_dict["id"]
            case_dict["username"] = data_dict["username"]
            case_dict["company"] = data_dict["company"]
            case_dict["department"] = data_dict["department"]
            case_dict["position"] = data_dict["position"]
            case_dict["duty"] = data_dict["duty"]
            case_dict["tel"] = data_dict["tel"]
            case_dict["addr"] = data_dict["addr"]
            case_dict["email"] = data_dict["email"]
            case_dict["remarks"] = data_dict["remarks"]


            case_dict["ctime"] = str(data_dict["ctime"])
            data_list.append(case_dict)

        if len(data_list) > 0:
            self.write(dict(code=0, msg='获取成功', count=tocount, data=data_list))
        else:
            self.write(dict(code=-1, msg='没有相关数据', count=0, data=[]))

    def post(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        username = data.get('username', None)
        company = data.get('company', None)
        department = data.get('department', None)
        position = data.get('position', None)
        duty = data.get('duty', None)
        tel = data.get('tel', None)
        addr = data.get('addr', None)
        email = data.get('email', None)
        remarks = data.get('remarks', None)
        if not username or not  company :
            return self.write(dict(code=-1, msg='参数不能为空'))
        with DBContext('r') as session:
            user_info2 = session.query(Stakeholder).filter(Stakeholder.tel == tel).first()
            user_info3 = session.query(Stakeholder).filter(Stakeholder.email == email).first()
        # if user_info1:
        #     return self.write(dict(code=-2, msg='微信号已存在，请重新输入。'))

        if user_info2:
            return self.write(dict(code=-3, msg='手机号已存在，请重新输入。'))

        # if user_info3:
        #     return self.write(dict(code=-4, msg='邮箱已存在，请重新输入。'))

        with DBContext('w', None, True) as session:
            session.add(Stakeholder(
                username=username,
                department=department,
                company=company,
                position=position,
                duty=duty,
                tel=tel,
                addr=addr,
                email=email,
                remarks=remarks,
            ))
            session.commit()

        sync_stakeholder_to_redis()
        self.write(dict(code=0, msg='成功', count=0, data=[]))

    def delete(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        id = data.get('id', None)
        if not id:
            return self.write(dict(code=-1, msg='ID不能为空'))

        redis_conn = cache_conn()
        redis_conn.hdel('stakeholder_hash', id)

        with DBContext('w', None, True) as session:
            session.query(Stakeholder).filter(Stakeholder.id == id).delete(synchronize_session=False)
        self.write(dict(code=0, msg='删除成功'))

    def put(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        id = data.get('id', None)
        username = data.get('username', None)
        company = data.get('company', None)
        department = data.get('department', None)
        position = data.get('position', None)
        duty = data.get('duty', None)
        tel = data.get('tel', None)
        addr = data.get('addr', None)
        email = data.get('email', None)
        remarks = data.get('remarks', None)

        # if not key or not value or not user_id:
        #     return self.write(dict(code=-1, msg='不能为空'))

        try:
            with DBContext('w', None, True) as session:
                session.query(Stakeholder).filter(Stakeholder.id == id).update({
                Stakeholder.username: username,
                Stakeholder.company: company,
                Stakeholder.department: department,
                Stakeholder.position: position,
                Stakeholder.duty: duty,
                Stakeholder.tel: tel,
                Stakeholder.addr: addr,
                Stakeholder.email: email,
                Stakeholder.remarks: remarks,
                })
                session.commit()
        except Exception as e:
            return self.write(dict(code=-2, msg='修改失败，请检查数据是否合法或者重复'))
        sync_stakeholder_to_redis()
        self.write(dict(code=0, msg='编辑成功'))

class Stakeholder_redisList(BaseHandler):
    def get(self, *args, **kwargs):
        data_list = []
        redis_conn = cache_conn()
        stakeholder_all = redis_conn.hgetall('stakeholder_hash')
        data_dict = convert(stakeholder_all)
        for k , v in data_dict.items():
            data_list.append({"k":k,"v":v})
            # ins_log.read_log('info', k)
        if len(data_list) > 0:
            self.write(dict(code=0, msg='获取成功', data=data_list))
        else:
            self.write(dict(code=-1, msg='没有相关数据',  data=[]))
class StakeholderList(BaseHandler):
    def get(self, *args, **kwargs):
        data_list = []
        value = self.get_argument('value', default=None, strip=True)
        user_list = []
        with DBContext('r') as session:
            todata = session.query(Stakeholder).filter(Stakeholder.company == value).order_by(Stakeholder.ctime.desc()).all()
            tocount = session.query(Stakeholder).filter(Stakeholder.company == value).count()

        for msg in todata:
            case_dict = {}
            data_dict = model_to_dict(msg)
            case_dict["id"] = data_dict["id"]
            case_dict["username"] = data_dict["username"]
            case_dict["company"] = data_dict["company"]
            case_dict["department"] = data_dict["department"]
            case_dict["position"] = data_dict["position"]
            case_dict["duty"] = data_dict["duty"]
            case_dict["tel"] = data_dict["tel"]
            case_dict["addr"] = data_dict["addr"]
            case_dict["email"] = data_dict["email"]
            case_dict["remarks"] = data_dict["remarks"]
            case_dict["ctime"] = str(data_dict["ctime"])
            data_list.append(case_dict)

        if len(data_list) > 0:
            self.write(dict(code=0, msg='获取成功', count=tocount, data=data_list))
        else:
            self.write(dict(code=-1, msg='没有相关数据', count=0, data=[]))


class uploadStakeholder(BaseHandler):
    def post(self, *args, **kwargs):
        ###文件保存到本地
        Base_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        upload_path = '{}/static/stakeholder/'.format(Base_DIR)
        file_body = self.request.files["file"][0]["body"]  # 提取表单中‘name’为‘file’的文件元数据
        file_path = upload_path + "tempfile.xls"
        with open(file_path, 'wb') as up:
            up.write(file_body)
        df = pd.read_excel(file_path)
        allsum = len(df.index)
        ins_log.read_log('info', allsum)
        for i in  range(0 , allsum):
            username = str(df.iloc[i, 0]),
            company = str(df.iloc[i,1]),
            department = str(df.iloc[i, 2]),
            position = str(df.iloc[i, 3]),
            duty = str(df.iloc[i, 4]),
            tel = str(df.iloc[i, 5]),
            addr = str(df.iloc[i, 6]),
            email = str(df.iloc[i, 7]),
            remarks = str(df.iloc[i, 8]),
            try:
                with DBContext('w', None, True) as session:
                    session.add(Stakeholder(
                        username=username,
                        company=company,
                        department=department,
                        position=position,
                        duty=duty,
                        tel=tel,
                        addr=addr,
                        email=email,
                        remarks=remarks,
                    ))
                session.commit()
            except:
                continue
        # session.commit()
        sync_stakeholder_to_redis()
stakeholder_urls = [
    (r"/v2/accounts/stakeholder/", StakeholderHandler),
    (r"/v2/accounts/redislist/", Stakeholder_redisList),
    (r"/v2/accounts/stakeholderlist/", StakeholderList),
    (r"/v2/accounts/stakeholder/upload/", uploadStakeholder),
]

if __name__ == "__main__":
    pass
