#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Desc    : 系统配置项
"""

from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import class_mapper
from datetime import datetime

Base = declarative_base()


def model_to_dict(model):
    model_dict = {}
    for key, column in class_mapper(model.__class__).c.items():
        model_dict[column.name] = getattr(model, key, None)
    return model_dict


class AppSettings(Base):
    __tablename__ = 'mg_app_settings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)  # key
    value = Column(String(300))  # value
    update_time = Column('update_time', DateTime(), default=datetime.now, onupdate=datetime.now)


class DictConfig(Base):
    __tablename__ = 'mg_dict_conf'
    id = Column(Integer, primary_key=True, autoincrement=True)
    dictname = Column(String(50))  # name
    dictkey = Column(String(50), unique=True, nullable=False)  # key
    dictvalue = Column(Text)  # value
