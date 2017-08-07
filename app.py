#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask
from flask import request,url_for,redirect,render_template
from flask import jsonify,make_response,g,session


from sqlalchemy.sql import func
from datetime import datetime

from models import DBSession,Users,Blogs,Comments
from page import getPageStr,Page

import hashlib

app=Flask(__name__)

def timeFormat(create_at):
	now=datetime.now().timestamp()
	timestamp=float(create_at)
	delta=int(now-timestamp)
	if delta < 60:
		return '刚刚'
	if delta < 3600:
		return '%s分钟前'%(delta//60)
	if delta < 86400:
		return '%s小时前'%(delta//3600)
	if delta < 604800:
		return '%s天前'%(delta//86400)
	dt=datetime.fromtimestamp(timestamp)
	return dt.strftime('%Y年%m月%d日 %H点%M分%S秒')
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


@app.before_request
def before_req():
	cookie = request.cookies.get('huusession')
	if cookie:
		user_id=cookie.split('-')[0]	
		if user_id:
			try:
				sess=DBSession()	
				user=sess.query(Users).filter(Users.id==user_id).one()
				sess.close()
				g.user=user
			except:				
				g.user=None

#主页
@app.route('/',methods=['GET'])
def index():
	user=g.get('user',None)
	item_count=queryNumById(Blogs)
	page_arg=request.args.get('page','1')
	page_index=getPageStr(page_arg)
	page=Page(item_count,page_index,3)
	blogs_list=queryAllDesc(Blogs,page.offset,page.limit)		
	return render_template('index.html', user=user,blogs=blogs_list,page=page)

#获取用户api
@app.route('/api/users',methods=['GET'])
def get_users_api():
	users_list=queryAllDesc(Users)
	user=g.get('user',None)
	if user is None:
		return redirect(url_for('login'))
	else:
		if user.admin:
			return jsonify(users=users_list)
		else:
			return redirect(url_for('login'))

	
#管理用户界面
@app.route('/manage/users',methods=['GET'])
def manage_users():
	user=g.get('user',None)
	if user is None:
		return redirect(url_for('login'))
	else:
		if user.admin:
			item_count=queryNumById(Users)
			page_arg=request.args.get('page','1')
			page_index=getPageStr(page_arg)
			page=Page(item_count,page_index)
			users_list=queryAllDesc(Users,page.offset,page.limit)
			return render_template('manage_users.html',users=users_list,page=page,user=user)
		else:
			return redirect(url_for('login'))
	
#获取blog文章api
@app.route('/api/blogs',methods=['GET'])
def get_blogs_api():
	blogs_list=queryAllDesc(Blogs)
	user=g.get('user',None)
	if user is  None:
		return redirect(url_for('login'))
	else:
		if user.admin:
			return jsonify(blogs=blogs_list)
		else:
			return redirect(url_for('login'))

@app.route('/manage/blog/create',methods=['GET'])
def create_blog():
	user=g.get('user',None)	
	if user is  None:
		return redirect(url_for('login'))
	else:
		if user.admin:
			return render_template('manage_blogs_create.html',user=user)
		else:
			return redirect(url_for('login'))
	
@app.route('/manage/blog/edit',methods=['GET'])
def edit_blog():
	blog_id=request.args.get('id','')
	if blog_id:
		try:
			sess=DBSession()
			blog=sess.query(Blogs).filter(Blogs.id==blog_id).one()
			sess.close()
		except:
			blog=None
	else:
		return redirect(url_for('manage_blogs'))
	user=g.get('user',None)	
	if user is  None:
		return redirect(url_for('login'))
	else:
		if user.admin:
			return render_template('manage_blogs_edit.html',user=user,blog=blog)
		else:
			return redirect(url_for('login'))
	

@app.route('/api/blog/create',methods=['POST'])
def create_blog_api():
	user=g.get('user',None)
	if user is  None:
		return redirect(url_for('login'))
	else:
		if user.admin:
			name=request.form['name'].encode('utf8')
			summary=request.form['summary'].encode('utf8')
			content=request.form['content'].encode('utf8')
			user_id=request.form['user_id'].encode('utf8')
			user_name=request.form['user_name'].encode('utf8')
			user_image=request.form['user_image'].encode('utf8')	
			sess=DBSession()
			blog=Blogs(user_id=user_id,user_name=user_name,user_image=user_image,name=name,summary=summary,content=content)
			sess.add(blog)
			sess.commit()
			sess.close()
			return 'ok'
		else:
			return redirect(url_for('login'))

@app.route('/api/blog/edit',methods=['POST'])
def edit_blog_api():
	user=g.get('user',None)
	if user is  None:
		return redirect(url_for('login'))
	else:
		if user.admin:
			blog_id=request.form['blog_id'].encode('utf8')
			name=request.form['name'].encode('utf8')
			summary=request.form['summary'].encode('utf8')
			content=request.form['content'].encode('utf8')
			sess=DBSession()
			blog=sess.query(Blogs).filter(Blogs.id==blog_id).update({Blogs.name:name,Blogs.summary:summary,Blogs.content:content})
			sess.commit()
			sess.close()
			return 'ok'
		else:
			return redirect(url_for('login'))

@app.route('/api/blog/delete',methods=['GET'])
def delete_blog_api():
	user=g.get('user',None)
	blog_id=request.args.get('id','')
	if user is  None:
		return redirect(url_for('login'))
	else:
		if user.admin:
			sess=DBSession()
			blog=sess.query(Blogs).filter(Blogs.id==blog_id).delete()
			sess.commit()
			sess.close()
		else:
			return redirect(url_for('login'))
		return 'ok'

@app.route('/manage/blogs',methods=['GET'])
def manage_blogs():
	user=g.get('user',None)
	if user is None:
		return redirect(url_for('login'))
	else:
		if user.admin:
			item_count=queryNumById(Blogs)
			page_arg=request.args.get('page','1')
			page_index=getPageStr(page_arg)
			page=Page(item_count,page_index)
			blogs_list=queryAllDesc(Blogs,page.offset,page.limit)
			return render_template('manage_blogs.html',blogs=blogs_list,page=page,user=user)
		else:
			return redirect(url_for('login'))

@app.route('/blog/<blog_id>')
def get_blog(blog_id):
	try:
		sess=DBSession()
		blog=sess.query(Blogs).filter(Blogs.id==blog_id).one()
		sess.close()
	except:
		blog=None
		return 'can not find the blog'
	user=g.get('user',None)
	try:
		sess=DBSession()
		comments=sess.query(Comments).filter(Comments.blog_id==blog_id).all()
		sess.close()
	except:
		comments=None

	return render_template("blog.html",blog=blog,user=user,comments=comments)

@app.route('/api/comments',methods=['POST'])
def create_comments_api():
	user=g.get('user',None)
	if user is  None:
		return 'notlogin'
	else:
		blog_id=request.form['blog_id']
		user_id=request.form['user_id']
		user_name=request.form['user_name']
		user_image=request.form['user_image']
		content=request.form['content']
		sess=DBSession()
		sess.add(Comments(blog_id=blog_id,user_id=user_id,user_name=user_name,user_image=user_image,content=content))
		sess.commit()
		sess.close()
		return 'ok'

@app.route('/manage/comments',methods=['GET'])
def manage_comments():
	user=g.get('user',None)
	if user is None:
		return redirect(url_for('login'))
	else:
		if user.admin:
			item_count=queryNumById(Comments)
			page_arg=request.args.get('page','1')
			page_index=getPageStr(page_arg)
			page=Page(item_count,page_index)
			comments_list=queryAllDesc(Comments,page.offset,page.limit)
			return render_template('manage_comments.html',comments=comments_list,page=page,user=user)
		else:
			return redirect(url_for('login'))

@app.route('/api/comment/delete',methods=['GET'])
def delete_comment_api():
	user=g.get('user',None)
	comment_id=request.args.get('id','')
	if user is  None:
		return redirect(url_for('login'))
	else:
		if user.admin:
			sess=DBSession()
			comment=sess.query(Comments).filter(Comments.id==comment_id).delete()
			sess.commit()
			sess.close()
		else:
			return redirect(url_for('login'))
		return 'ok'

#注册页面
@app.route('/register',methods=['GET'])
def register():
	return render_template('register.html')

#创建用户api
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
	user=sess.query(Users).filter(Users.email==email).one()
	sess.close()
	cookie_str='%s-%s-%s'%(user.id,user.email,user.passwd)
	L=[user.id,hashlib.sha1(cookie_str.encode('utf8')).hexdigest()]
	resp = make_response()
	resp.set_cookie('huusession','-'.join(L))
	return resp
	
#登录页面
@app.route('/login',methods=['GET'])
def login():	
	return render_template('login.html')

#登录验证api
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

#退出登录
@app.route('/signout', methods=['GET'])
def signout_api():
	resp = make_response()
	resp.set_cookie('huusession', '', expires=0)
	return resp

if __name__=='__main__':
	app.run()
