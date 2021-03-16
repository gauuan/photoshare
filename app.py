######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################


import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login
from io import BytesIO
from PIL import Image

#for image uploading
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'mango147'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out')

@app.route('/albums', methods=['GET'])
def showAlbums():
		return render_template('albums.html')
		#POST:
@app.route('/albums', methods=['POST'])
def showAlbums2():
	user_email = request.form.get('user')
	tag = request.form.get('tag')

	if user_email:
		return flask.redirect(flask.url_for('showAlbumsbyUser', user_id=getUserIdFromEmail(user_email)))
	elif tag:
		return flask.redirect(flask.url_for('showAlbumsbyTag', tag=tag))
	else:
		return render_template('albums.html')

@app.route('/albums/<string:tag>') #we should use tag_id, which is an int. need to figure out how 
def showAlbumsbyTag(tag):
	return 0
@app.route('/albums/<int:albumid>?album=True')
def showPhotosinAlbum(albumid):
	return 0

@app.route('/albums/<int:user_id>')
def showAlbumsbyUser(user_id):
	cursor = conn.cursor()
	cursor.execute(""" SELECT A.title FROM Users U, Albums A WHERE U.user_id = A.user_id AND (U.user_id = '{0}')""".format(user_id))
	album_names = cursor.fetchall()
	return render_template('photo_render.html', albums=album_names)

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier

@app.route("/register", methods=['GET'])
def register():
	return render_template('ee.html', display='True')

@app.route("/register/existingaccount", methods=['GET'])
def existingaccount():
	return render_template('ee.html',  display='True', duplicate='True')

@app.route("/register", methods=['POST'])
def register_user():
	try:
		firstName=request.form.get('firstname') #required
		lastName=request.form.get('lastname') #required
		email=request.form.get('email') #required
		DOB=request.form.get('birthday')
		hometown=request.form.get('hometown')
		gender=request.form.get('gender')
		password=request.form.get('password') #required

	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test = isEmailUnique(email)
	if test and firstName and lastName and password:
		print(cursor.execute("""
		INSERT INTO Users (fname, lname, DOB, gender, hometown, email, password) 
		VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')""".format(firstName, lastName, DOB, gender, hometown, email, password)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!')
	elif not test:
		#print("couldn't find all tokens")
		#cursor.close()
		return flask.redirect(flask.url_for('existingaccount'))
		#NOTE: actually does work, but not this part
	else:
		#cursor.close()
		return render_template('ee.html')


@app.route("/search", methods=['GET', 'POST'])
def searchFriends():
	if flask.request.method == 'GET':
		#get value of search term 
		cursor = conn.cursor()
		cursor.execute("SELECT ")




def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, photo_id, caption FROM Photos WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def resizeImage(img):
	img_bytes = BytesIO(img)
	img_bytes.seek(0)
	im = Image.open(img_bytes)
	im.thumbnail((400, 400), Image.ANTIALIAS)

	buffered = BytesIO()
	im.save(buffered, format="JPEG")
	return buffered.getvalue()

def getLikeCount(photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT COUNT(*) FROM liked_photos WHERE liked_photo = '{0}'".format(photo_id))
	return cursor.fetchall()

def getPicturesbyTag(tag_id):
	cursor = conn.cursor()


def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if not email or cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code

@app.route('/profile')
@flask_login.login_required
def protected():
	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile")

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		photo_data =imgfile.read()
		cursor = conn.cursor()
		album_name = request.form.get('newAlbum')
		cursor.execute('''INSERT INTO Photos (imgdata, user_id, caption) VALUES (%s, %s, %s )''' ,(photo_data,uid, caption))
		cursor.execute("""INSERT INTO Albums (title, user_id) VALUES (%s, %s )""", (album_name, uid))
		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid),base64=base64)
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		cursor = conn.cursor()
		return render_template('upload.html', albums=['red', 'blue'])
#end photo uploading code

@app.route('/explore', methods = ['GET', 'POST']))

	#user = request.form.get("user")
	#tag = request.form.get("tag")
	#no implemented at all, just trying to fifgure out how to submit info in form and get back


#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welecome to Photoshare')


if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
