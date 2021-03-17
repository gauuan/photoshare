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

from pymysql import NULL

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'isham536'
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
			user_id = getUserIdFromEmail(email)
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('profile', user_id = user_id)) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
@flask_login.login_required
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out')

@app.route('/photos', methods=['GET'])
def showAlbums():
		return render_template('photo_search.html')
		#POST:
@app.route('/photos', methods=['POST'])
def getTagData():
	photos = []
	tag_str= request.form.get('tag')
	tags = tag_str.split(',')
	photo_ids = conjuctiveTagSearch(tags)
	for id in photo_ids:
		photos.append(getPhotoFromPhotoID(id))
	return render_template('photo_render.html', photos=photos, base64=base64)
		

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
		
		return flask.redirect(flask.url_for('existingaccount'))
		#NOTE: actually does work, but not this part
	else:
		#cursor.close()
		return render_template('ee.html')

"""
	outputs tuple of photo data
"""
def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, photo_id, caption FROM Photos WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getPhotoFromPhotoID(pid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, caption FROM Photos WHERE photo_id = '{0}'".format(pid))
	return cursor.fetchall()

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
	return cursor.fetchone()[0]

def getPhotoIDsbyTag(tag):
	cursor = conn.cursor()
	cursor.execute(""" SELECT tag_id FROM Tags WHERE tag = '{0}' """.format(tag))
	tags_id = cursor.fetchone()
	if tags_id:
		cursor.execute(""" SELECT photo_id FROM is_tagged WHERE tag_id = '{0}'""".format(tags_id[0]))
		return cursor.fetchall()
	return NULL;

def conjuctiveTagSearch(tags):
	conjIDs = []
	photo_ids = {}
	for tag in tags:
		for id in getPhotoIDsbyTag(tag):
			if id[0] not in photo_ids.keys():
				photo_ids[id[0]] = 0
			else:
				photo_ids[id[0]] += 1
	for id, count in photo_ids.items():
		if count == len(tags):
			
			conjIDs.append(id)

	return conjIDs


def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def getUserNameFromID(user_id):
	cursor = conn.cursor()
	cursor.execute("SELECT Concat(fname, ' ', lname) FROM Users WHERE user_id = '{0}'".format(user_id))
	return cursor.fetchone()

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if not email or cursor.execute("SELECT email FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code


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
		tags = request.form.get('tags').split(',')
		photo_data =imgfile.read()
		cursor = conn.cursor()
		album_name = request.form.get('newAlbum')
		
		cursor.execute('''INSERT INTO Photos (imgdata, user_id, caption) VALUES (%s, %s, %s )''' ,(photo_data,uid, caption))
		cursor.execute("""INSERT INTO Albums (title, user_id) VALUES (%s, %s )""", (album_name, uid))

		#NOTE: code to attach tags to photos
		
		for tag in tags:
			cursor.execute("""SELECT tag_id FROM Tags where tag = %s""",(tag))
			tag_id = cursor.fetchone()
			if not tag_id:
				cursor.execute("""INSERT INTO Tags (tag) VALUES (%s) """, tag)
				conn.commit()
				cursor.execute("""SELECT tag_id FROM Tags WHERE tag = '{0}'""".format(tag))
				tag_id = cursor.fetchone()
			cursor.execute("""SELECT photo_id FROM PHOTOS WHERE imgdata = %s""", (photo_data))
			photo_id = cursor.fetchone()[0]
			cursor.execute(""" INSERT INTO is_tagged (tag_id, photo_id) VALUES (%s, %s )""", (tag_id[0], photo_id))

		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid),base64=base64)
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		cursor = conn.cursor()
		return render_template('upload.html', albums=['red', 'blue'])
#end photo uploading code

@app.route('/explore', methods = ['GET', 'POST'])
def explore():
	if request.method == 'GET':
		return render_template('explore.html')
	
	else:
		email = request.form.get("user")
		if isEmailUnique(email) == False:
			uid = getUserIdFromEmail(email)
			return flask.redirect(flask.url_for('profile',user_id=uid), code=302)
		else:
			return render_template('explore.html', no_user_found = 'True')

@app.route('/<user_id>', methods = ['GET', 'POST'])
def profile(user_id):
	if flask.request.method == 'GET':
		if flask_login.current_user.is_authenticated:
			if getUserIdFromEmail(flask_login.current_user.id) == user_id:
				# current user is looking at their own profile
				# functionality to delete albums and picture
				# add route to upload new photos
				return render_template('profile.html', name = getUserNameFromID(user_id), photos=getUsersPhotos(user_id), base64=base64, self_view = 'True', uid=user_id)
				#only this case doesn't work, bc test msg isnt showing
			else:
				# current user is looking at someone else's profile
				return render_template('profile.html', name = getUserNameFromID(user_id), photos=getUsersPhotos(user_id), base64=base64, uid=user_id)
		else:
		# anonymous user view
			return render_template('profile.html', name = getUserNameFromID(user_id), photos=getUsersPhotos(user_id), base64=base64, anon = 'True', uid=user_id)
	else:
		comment = request.form.get('comment')
		pid = request.form['submit_comment']
		if flask_login.current_user.is_authenticated:
			uid = getUserIdFromEmail(flask_login.current_user.id)
		else:
			uid = NULL
		cursor = conn.cursor()
		poster_id = cursor.execute(""" SELECT user_id FROM Photos WHERE photo_id = %s""" % pid)
		cursor.execute(""" INSERT INTO Comments (text, commenter_id, poster_id, photo_id) VALUES (%s, %s, %s, %s )""", (comment, uid, poster_id[0], pid))
		return flask.redirect(flask.url_for('profile', user_id), code=302)


@app.route("/<user_id>/friends", methods=['GET', 'POST'])
def friendsOfUser(user_id):
	if flask.request.method == 'GET':
		cursor = conn.cursor()
		cursor.execute("""(SELECT friend_id FROM are_friends WHERE user_id = '{0}')""".format(user_id))
		friend_ids = cursor.fetchall()
		friend_id_list = [x[0] for x in friend_ids]
		#cursor.execute("""SELECT Concat(U.fname, ' ', U.lname) FROM Users U, are_friends F WHERE F.friend_id = U.user_id AND F.user_id = '{0}')""".format(user_id))
		#friend_names = cursor.fetchall()
		friend_name_list = [getUserNameFromID(x) for x in friend_id_list]
		#friends = cursor.fetchall()
		return render_template('friends.html', friends = friend_name_list, friend_id = friend_id_list)
	else: #POST. if have time, add hyperlinks to friends profiles
		return render_template('friends.html', friends=['red', 'blue'])

#default page
@app.route("/", methods=['GET'])
def hello():
	if flask_login.current_user.is_authenticated:
		user_id = getUserIdFromEmail(flask_login.current_user.id)
		return render_template('hello.html', user_id = user_id, message='Welecome to Photoshare')
	else: 
		return render_template('hello.html', message='Welecome to Photoshare')
if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
