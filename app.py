from flask import Flask, render_template ,redirect, url_for, request, make_response,flash,url_for,send_from_directory
from pymongo import MongoClient
from functools import wraps
import string 
import random
import os 

app=Flask(__name__)
app.config['SECRET_KEY'] = "ngacnhienchua"
client = MongoClient("mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false")
db = client['web_course']
collection = db['practice']
S=10

def is_authenticated(request):
    username = request.cookies.get('username', '')
    token = request.cookies.get('token', '')
    db_username = collection.find_one({'username':username})
    if token:
        if username == db_username['username']:
            token == db_username['token']
            return True
        return False
    return False

def login_required(func):
    @wraps(func)
    def verify(*args, **kwargs):
        if is_authenticated(request):
            return func(*args, **kwargs)
        else:
            flash('Please login first!!!','error')
            return redirect(url_for('login'))
    return verify

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile/')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = collection.find_one({'username':request.form['username']})
        if user != None:
            if username == user['username']:
                if password == user['password']:
                    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k = S)) 
                    session_token = random_string
                    response = make_response(redirect(url_for('profile')))
                    response.set_cookie(key='username',value=username)
                    response.set_cookie(key='token',value=session_token)
                    collection.update_one({'username':username},{'$set':{'token':session_token}})
                    return response
                else:
                    flash('Username or password is invalid', 'error')  
            else:
                flash('Username or password is invalid', 'error')
        else:
            flash('Username or password is invalid!', 'error')

    return render_template('login.html')

@app.route('/signup',methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user = collection.find_one({'username':request.form['username']})
        if user:
            flash('Username is already existed', 'error')
        else:
            collection.insert_one({
                'username': request.form['username'],
                'password': request.form['password']
            })

        return render_template("signup.html",)

    return render_template('signup.html')

@app.route('/signout', methods=['GET', 'POST'])
@login_required
def signout():
    username = request.cookies.get('username', '')
    collection.update_one({'username':username},{'$set':{'token':' '}})
    response = make_response(redirect(url_for('login')))
    response.set_cookie(key='token',value='')
    flash('Sign Out successfully!', 'message')
    return response

app.run(host='localhost',port=5000,debug=True)
