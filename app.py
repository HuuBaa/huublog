#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify

from models import DBSession,Users,Blogs,Comments
from datetime import datetime
app=Flask(__name__)

def timeFormat(create_at):
	timestamp=float(create_at)
	dt=datetime.fromtimestamp(timestamp)
	return dt.strftime('%Y-%m-%d %H:%M:%S')
app.add_template_filter(timeFormat,'timeFormat')

def queryAllDesc(table_class):
	session=DBSession()
	qClass=session.query(table_class).order_by(table_class.create_at.desc()).all()
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
	try:
		page=request.args['page']
	except:
		page='1'
	users_list=queryAllDesc(Users)
	return render_template('manage_users.html',users=users_list,page=page)

if __name__=='__main__':
	app.run(debug=True)

