#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy import SmallInteger,Column,String,Text,Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import time,uuid
def next_id():
    return '%015d%s000'%(int(time.time()*1000),uuid.uuid4().hex)

engine=create_engine('mysql+pymysql://root:password@localhost:3306/huublog?charset=utf8')
Base=declarative_base()

def to_dict(self):
  return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}
Base.to_dict = to_dict

class Users(Base):
    __tablename__='users'
    id=Column(String(50),primary_key=True,default=next_id)
    name=Column(String(50),unique=True)
    email=Column(String(50),unique=True)
    passwd=Column(String(50))
    create_at=Column(String(50),default=time.time)
    image=Column(String(500),default='http://www.gravatar.com/avatar/7cbf7d3ca37ebad9b668542244ae75cd?d=mm&s=120')
    admin=Column(SmallInteger(),default=0)

class Blogs(Base):
    __tablename__='blogs'
    id=Column(String(50),primary_key=True,default=next_id)
    user_id=Column(String(50))
    user_name=Column(String(50))
    user_image=Column(String(200))
    name=Column(String(50))
    summary=Column(String(200))
    content=Column(Text())
    create_at=Column(String(50),default=time.time)

class Comments(Base):
    __tablename__='comments'
    id=Column(String(50),primary_key=True,default=next_id)
    blog_id=Column(String(50))
    user_id=Column(String(50))
    user_name=Column(String(50))
    user_image=Column(String(200))
    content=Column(Text())
    create_at=Column(String(50),default=time.time)

#在命令行进行创建表
# >>> from models import init_db
# >>> init_db()
def init_db():   
    Base.metadata.create_all(bind=engine)

def drop_db():   
    Base.metadata.drop_all(bind=engine)

DBSession=sessionmaker(bind=engine)

