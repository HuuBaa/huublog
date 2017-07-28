from flask import Flask
from flask import request
from flask import render_template
app=Flask(__name__)

user={'admin':1,'name':'Huu'}


@app.route('/',methods=['GET'])
def hello(name=None):
	return render_template('index.html',name=name,user=user)
	
		
if __name__=='__main__':
	app.run(debug=True)
