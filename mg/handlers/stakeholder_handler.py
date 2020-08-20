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
            if key == "nickname":
                conditions.append(Stakeholder.nickname.like('%{}%'.format(value)))
            if key == "email":
                conditions.append(Stakeholder.email.like('%{}%'.format(value)))
            if key == "tel":
                conditions.append(Stakeholder.tel.like('%{}%'.format(value)))
            if key == "wechat":
                conditions.append(Stakeholder.wechat.like('%{}%'.format(value)))
            if key == "department":
                conditions.append(Stakeholder.department.like('%{}%'.format(value)))

            todata = session.query(Stakeholder).filter(*conditions).order_by(Stakeholder.ctime.desc()).offset(limit_start).limit(int(limit)).all()
            tocount = session.query(Stakeholder).filter(*conditions).count()

        for msg in todata:
            case_dict = {}
            data_dict = model_to_dict(msg)
            case_dict["id"] = data_dict["id"]
            case_dict["username"] = data_dict["username"]
            case_dict["nickname"] = data_dict["nickname"]
            case_dict["email"] = data_dict["email"]
            case_dict["tel"] = data_dict["tel"]
            case_dict["wechat"] = data_dict["wechat"]
            case_dict["department"] = data_dict["department"]
            case_dict["ctime"] = str(data_dict["ctime"])
            data_list.append(case_dict)

        if len(data_list) > 0:
            self.write(dict(code=0, msg='获取成功', count=tocount, data=data_list))
        else:
            self.write(dict(code=-1, msg='没有相关数据', count=0, data=[]))

    def post(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        username = data.get('username', None)
        nickname = data.get('nickname', None)
        department = data.get('department', None)
        tel = data.get('tel', None)
        wechat = data.get('wechat', None)
        email = data.get('email', None)
        if not username or not nickname or not department or not tel or not wechat or not email:
            return self.write(dict(code=-1, msg='参数不能为空'))
        with DBContext('r') as session:
            user_info1 = session.query(Stakeholder).filter(Stakeholder.wechat == wechat).first()
            user_info2 = session.query(Stakeholder).filter(Stakeholder.tel == tel).first()
            user_info3 = session.query(Stakeholder).filter(Stakeholder.email == email).first()
        if user_info1:
            return self.write(dict(code=-2, msg='微信号已存在，请重新输入。'))

        if user_info2:
            return self.write(dict(code=-3, msg='手机号已存在，请重新输入。'))

        if user_info3:
            return self.write(dict(code=-4, msg='邮箱已存在，请重新输入。'))

        with DBContext('w', None, True) as session:
            session.add(Stakeholder(
                username=username,
                nickname=nickname,
                department=department,
                tel=tel,
                wechat=wechat,
                email=email,))
            session.commit()
        self.write(dict(code=0, msg='成功', count=0, data=[]))

    def delete(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        id = data.get('id', None)
        if not id:
            return self.write(dict(code=-1, msg='ID不能为空'))

        with DBContext('w', None, True) as session:
            session.query(Stakeholder).filter(Stakeholder.id == id).delete(synchronize_session=False)
        self.write(dict(code=0, msg='删除成功'))

    def put(self, *args, **kwargs):
        data = json.loads(self.request.body.decode("utf-8"))
        id = data.get('id', None)
        username = data.get('username', None)
        nickname = data.get('nickname', None)
        department = data.get('department', None)
        tel = data.get('tel', None)
        wechat = data.get('wechat', None)
        email = data.get('email', None)

        # if not key or not value or not user_id:
        #     return self.write(dict(code=-1, msg='不能为空'))

        try:
            with DBContext('w', None, True) as session:
                session.query(Stakeholder).filter(Stakeholder.id == id).update({
                Stakeholder.username: username,
                Stakeholder.nickname: nickname,
                Stakeholder.department: department,
                Stakeholder.tel: tel,
                Stakeholder.wechat: wechat,
                Stakeholder.email: email,
                })
                session.commit()
        except Exception as e:
            return self.write(dict(code=-2, msg='修改失败，请检查数据是否合法或者重复'))

        self.write(dict(code=0, msg='编辑成功'))


stakeholder_urls = [
    (r"/v2/accounts/stakeholder/", StakeholderHandler),
]

if __name__ == "__main__":
    pass
