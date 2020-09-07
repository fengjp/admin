#!/usr/bin/env python
# -*-coding:utf-8-*-

import json
import shortuuid
import base64
from websdk.jwt_token import gen_md5
from websdk.tools import check_password
from libs.base_handler import BaseHandler
from websdk.db_context import DBContext
from models.admin import UserRoles,Stakeholder,Companylist, model_to_dict
from websdk.consts import const
from websdk.cache_context import cache_conn
from websdk.web_logs import ins_log

class CompanyHandler(BaseHandler):
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
            if key == "company":
                conditions.append(Companylist.company.like('%{}%'.format(value)))
            if key == "addr":
                conditions.append(Companylist.addr.like('%{}%'.format(value)))
            if key == "bossname":
                conditions.append(Companylist.username.like('%{}%'.format(value)))
            if key == "duty":
                conditions.append(Companylist.duty.like('%{}%'.format(value)))
            if key == "tel":
                conditions.append(Companylist.tel.like('%{}%'.format(value)))
            if key == "website":
                conditions.append(Companylist.addr.like('%{}%'.format(value)))
            if key == "email":
                conditions.append(Companylist.email.like('%{}%'.format(value)))
            if key == "remarks":
                conditions.append(Companylist.remarks.like('%{}%'.format(value)))

            todata = session.query(Companylist).filter(*conditions).order_by(Companylist.ctime.desc()).offset(limit_start).limit(int(limit)).all()
            tocount = session.query(Companylist).filter(*conditions).count()

        for msg in todata:
            Companylist_dict = {}
            data_dict = model_to_dict(msg)
            Companylist_dict["id"] = data_dict["id"]
            Companylist_dict["company"] = data_dict["company"]
            Companylist_dict["addr"] = data_dict["addr"]
            Companylist_dict["bossname"] = data_dict["bossname"]
            Companylist_dict["duty"] = data_dict["duty"]
            Companylist_dict["tel"] = data_dict["tel"]
            Companylist_dict["website"] = data_dict["website"]
            Companylist_dict["email"] = data_dict["email"]
            Companylist_dict["remarks"] = data_dict["remarks"]
            Companylist_dict["ctime"] = str(data_dict["ctime"])
            data_list.append(Companylist_dict)

        if len(data_list) > 0:
            self.write(dict(code=0, msg='获取成功', count=tocount, data=data_list))
        else:
            self.write(dict(code=-1, msg='没有相关数据', count=0, data=[]))

    def post(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        company = data.get('company', None)
        addr = data.get('addr', None)
        bossname = data.get('bossname', None)
        duty = data.get('duty', None)
        tel = data.get('tel', None)
        website = data.get('website', None)
        email = data.get('email', None)
        remarks = data.get('remarks', None)
        if not bossname or not  company :
            return self.write(dict(code=-1, msg='参数不能为空'))
        with DBContext('r') as session:
            user_info2 = session.query(Companylist).filter(Companylist.tel == tel).first()
            user_info3 = session.query(Companylist).filter(Companylist.email == email).first()
        # if user_info1:
        #     return self.write(dict(code=-2, msg='微信号已存在，请重新输入。'))

        if user_info2:
            return self.write(dict(code=-3, msg='手机号已存在，请重新输入。'))

        # if user_info3:
        #     return self.write(dict(code=-4, msg='邮箱已存在，请重新输入。'))

        with DBContext('w', None, True) as session:
            session.add(Companylist(
                company=company,
                addr=addr,
                bossname=bossname,
                duty=duty,
                tel=tel,
                website=website,
                email=email,
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
            session.query(Companylist).filter(Companylist.id == id).delete(synchronize_session=False)
        self.write(dict(code=0, msg='删除成功'))

    def put(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        id = data.get('id', None)
        company = data.get('company', None)
        addr = data.get('addr', None)
        bossname = data.get('bossname', None)
        duty = data.get('duty', None)
        tel = data.get('tel', None)
        website = data.get('website', None)
        email = data.get('email', None)
        remarks = data.get('remarks', None)

        # if not key or not value or not user_id:
        #     return self.write(dict(code=-1, msg='不能为空'))

        try:
            with DBContext('w', None, True) as session:
                session.query(Companylist).filter(Companylist.id == id).update({
                Companylist.company: company,
                Companylist.addr: addr,
                Companylist.bossname: bossname,
                Companylist.duty: duty,
                Companylist.tel: tel,
                Companylist.website: website,
                Companylist.email: email,
                Companylist.remarks: remarks,
                })
                session.commit()
        except Exception as e:
            return self.write(dict(code=-2, msg='修改失败，请检查数据是否合法或者重复'))

        self.write(dict(code=0, msg='编辑成功'))

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

company_urls = [
    (r"/v2/accounts/company/", CompanyHandler),
]

if __name__ == "__main__":
    pass
