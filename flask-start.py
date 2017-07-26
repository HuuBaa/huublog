from flask import Flask
from flask import request
from flask import render_template
app=Flask(__name__)

@app.route('/hello/',methods=['GET'])
@app.route('/hello/<name>',methods=['GET'])
def hello(name=None):
	return render_template('hello.html',name=name),200
	
@app.route('/login/<name>',methods=['GET','POST'])
def login(name):
	if request.method=='POST':
		return do_login(name)		
	else:
		return show_login_page(name)
	
def show_login_page(name):
		return '''
		<form action="/login/%s" method="post">
		<label>输入用户名<input type="text" name="username">
		</label><label>输入密码<input type="password" name="password"></label>
		<input type="submit" value="login">
		</form>'''%name
def do_login(name):
		if request.form['username']==name and request.form['password']==name:
			return '%s ! login succeed!'%name
		else:
			return 'sorry!login failed!'
			

			
if __name__=='__main__':
	app.run(debug=True)
