from sre_parse import State
from flask import Flask, url_for, render_template, flash, request, redirect, session,logging,request
from flask_sqlalchemy import SQLAlchemy
# from model import classifier
from flask import Flask, render_template, request
import pickle
import numpy as np
from deployement import predict
import numpy as np
import matplotlib.pyplot as plt


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class User(db.Model):
	""" Create user table"""
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True)
	password = db.Column(db.String(80))

	def __init__(self, username, password):
		self.username = username
		self.password = password


@app.route('/', methods=['GET', 'POST'])
def home():
	""" Session control"""
	if not session.get('logged_in'):
		return render_template('index.html')
	else:
		if request.method == 'POST':
			return render_template('index.html') 
		return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
	"""Login Form"""
	if request.method == 'GET':
		return render_template('login.html')
	else:
		name = request.form['username']
		passw = request.form['password']
		try:
			data = User.query.filter_by(username=name, password=passw).first()
			if data is not None:
				session['logged_in'] = True
				return redirect(url_for('home'))
			else:
				return 'Incorrect Login'
		except:
			return "Incorrect Login"


@app.route('/register/', methods=['GET', 'POST'])
def register():
	"""Register Form"""
	if request.method == 'POST':
		new_user = User(username=request.form['username'], password=request.form['password'])
		db.session.add(new_user)
		db.session.commit()
		return render_template('login.html')
	return render_template('register.html')


@app.route("/logout")
def logout():
	"""Logout Form"""
	session['logged_in'] = False
	return redirect(url_for('home'))


filename = 'diabetes-prediction-rfc-model.pkl'
classifier = pickle.load(open(filename, 'rb'))

@app.route('/diabetes')
def  diabetes():
	return render_template('index1.html')

@app.route('/predict', methods=['POST'])
def predict():
	if request.method == 'POST':
		preg = request.form['pregnancies']
		glucose = request.form['glucose']
		bp = request.form['bloodpressure']
		st = request.form['skinthickness']
		insulin = request.form['insulin']
		bmi = request.form['bmi']
		dpf = request.form['dpf']
		age = request.form['age']

		data = np.array([[preg, glucose, bp, st, insulin, bmi, dpf, age]])
		my_prediction = classifier.predict(data) 
		# print(data[0])
		a = np.array(list(map(float,data[0])))
		b = np.array([15,115,0,0,0,35.3,0.134,29])

		default_x_ticks = range(len(a))

		plt.plot(a)
		plt.plot(b)

		plt.xticks(default_x_ticks, ['pregnancies','glucose','bloodpressure','skin thickness','insulin','bmi','dpf','age'], rotation = 340, fontsize=10)

		plt.savefig('./static/report.jpg')

		return render_template('result.html', prediction=my_prediction)


if __name__ == '__main__':
	app.debug = True
	db.create_all()
	app.secret_key = "123"
	app.run(host='0.0.0.0')
	
