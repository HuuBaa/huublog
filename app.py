#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask
from flask import request,url_for,redirect,render_template,session
from flask import jsonify,make_response


from sqlalchemy.sql import func
from datetime import datetime

from models import DBSession,Users,Blogs,Comments
from page import getPageStr,Page
import hashlib
app=Flask(__name__)

def timeFormat(create_at):
	timestamp=float(create_at)
	dt=datetime.fromtimestamp(timestamp)
	return dt.strftime('%Y-%m-%d %H:%M:%S')
app.add_template_filter(timeFormat,'timeFormat')

def queryNumById(table_class):
	sess=DBSession()
	qNum=sess.query(func.count(table_class.id)).scalar()
	sess.close()
	return qNum

def queryAllDesc(table_class,offset=None,limit=None):
	if offset is None and limit is None:
		sess=DBSession()
		qClass=sess.query(table_class).order_by(table_class.create_at.desc()).all()
		sess.close()
	else:
		sess=DBSession()
		qClass=sess.query(table_class).order_by(table_class.create_at.desc()).offset(offset).limit(limit).all()
		sess.close()

	for user in qClass:
		user.passwd='******'
	qClass_list=[]
	for i in range(len(qClass)):
		qClass_list.append(qClass[i].to_dict())
	return qClass_list

#主页
@app.route('/',methods=['GET'])
def index(user=None):	
	cookie = request.cookies.get('huusession')
	if cookie:
		user_id=cookie.split('-')[0]	
		if user_id:
			try:
				sess=DBSession()	
				user=sess.query(Users).filter(Users.id==user_id).one()
				sess.close()
			except:
				user=None
	return render_template('index.html', user=user)

#获取用户api
@app.route('/api/users',methods=['GET'])
def get_users_api():
	users_list=queryAllDesc(Users)	
	return jsonify(users=users_list)

@app.route('/manage/users',methods=['GET'])
def manage_users():
	item_count=queryNumById(Users)
	page_arg=request.args.get('page','1')
	page_index=getPageStr(page_arg)
	page=Page(item_count,page_index)
	users_list=queryAllDesc(Users,page.offset,page.limit)
	return render_template('manage_users.html',users=users_list,page=page)

@app.route('/register',methods=['GET'])
def register():
	return render_template('register.html')

@app.route('/api/users',methods=['POST'])
def register_api():
	name=request.form['name'].encode('utf8')
	email=request.form['email'].encode('utf8')
	passwd=request.form['passwd'].encode('utf8')
	s='%s:%s'%(email,passwd)
	passwd=hashlib.sha1(s.encode('utf8')).hexdigest()
	sess=DBSession()
	if sess.query(Users).filter(Users.name==name).count() > 0:
		return 'usernameError'
	if sess.query(Users).filter(Users.email==email).count() > 0:
		return 'emailError'
	sess.close()
	sess=DBSession()
	sess.add(Users(name=name,email=email,passwd=passwd))
	sess.commit()
	sess.close()
	return 'ok'

@app.route('/login',methods=['GET'])
def login():	
	return render_template('login.html')

@app.route('/api/authenticate',methods=['POST'])
def authenticate_api():
	email=request.form['email'].encode('utf8')
	passwd=request.form['passwd'].encode('utf8')
	sess=DBSession()
	try:
		user=sess.query(Users).filter(Users.email==email).one()
	except:
		return 'emailError'
	sess.close()
	s='%s:%s'%(email,passwd)
	passwd=hashlib.sha1(s.encode('utf8')).hexdigest()
	if passwd==user.passwd:
		cookie_str='%s-%s-%s'%(user.id,user.email,user.passwd)
		L=[user.id,hashlib.sha1(cookie_str.encode('utf8')).hexdigest()]
		resp = make_response()
		resp.set_cookie('huusession','-'.join(L))
		return resp
	else:
		return 'passwordError'

@app.route('/signout', methods=['GET'])
def signout_api():
	resp = make_response()
	resp.set_cookie('huusession', '', expires=0)
	return resp


if __name__=='__main__':
	app.run(debug=True)
