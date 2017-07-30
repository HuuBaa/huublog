#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify

from sqlalchemy.sql import func
from datetime import datetime

from models import DBSession,Users,Blogs,Comments
from page import getPageStr,Page
app=Flask(__name__)

def timeFormat(create_at):
	timestamp=float(create_at)
	dt=datetime.fromtimestamp(timestamp)
	return dt.strftime('%Y-%m-%d %H:%M:%S')
app.add_template_filter(timeFormat,'timeFormat')

def queryNumById(table_class):
	session=DBSession()
	qNum=session.query(func.count(table_class.id)).scalar()
	session.close()
	return qNum

def queryAllDesc(table_class,offset=None,limit=None):
	if offset is None and limit is None:
		session=DBSession()
		qClass=session.query(table_class).order_by(table_class.create_at.desc()).all()
		session.close()
	else:
		session=DBSession()
		qClass=session.query(table_class).order_by(table_class.create_at.desc()).offset(offset).limit(limit).all()
		session.close()

	for user in qClass:
		user.passwd='******'
	qClass_list=[]
	for i in range(len(qClass)):
		qClass_list.append(qClass[i].to_dict())
	return qClass_list

#主页
@app.route('/',methods=['GET'])
def index(user=None):
	session=DBSession()
	user=session.query(Users).filter(Users.name=='Huu2').one()
	session.close()
	return render_template('index.html', user=user)

#获取用户api
@app.route('/api/users',methods=['GET'])
def get_users_api():
	users_list=queryAllDesc(Users)	
	return jsonify(users=users_list)

@app.route('/manage/users',methods=['GET'])
def manage_users():
	item_count=queryNumById(Users)
	try:
		page_arg=request.args['page']
	except:
		page_arg='1'
	page_index=getPageStr(page_arg)
	page=Page(item_count,page_index)
	
	users_list=queryAllDesc(Users,page.offset,page.limit)
	return render_template('manage_users.html',users=users_list,page=page)

if __name__=='__main__':
	app.run(debug=True)
