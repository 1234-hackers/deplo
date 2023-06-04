
from flask import Flask, render_template, request, session, redirect, url_for , sessions
from flask_sqlalchemy import SQLAlchemy
import hashlib

import passlib 
from passlib.context import CryptContext 
from passlib.hash import argon2, bcrypt_sha256,argon2,ldap_salted_md5,md5_crypt 
import sqlite3

from pymongo import MongoClient

Hash_passcode = CryptContext(schemes="sha256_crypt",sha256_crypt__min_rounds=131072) 
username_hash = CryptContext(schemes=["sha256_crypt","argon2"])

username_hash.hash("name")

app = Flask(__name__)
app.secret_key = "super secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'


from pymongo import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://jackson:mutamuta@hbcall.ihz6j.azure.mongodb.net/test?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Get the users collection
users_collection = client.Hases.backup


db = SQLAlchemy(app)
with app.app_context():
    db.create_all()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120))
    password = db.Column(db.String(80))

class UserFiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    fileName = db.Column(db.String(200))
    md5 = db.Column(db.String(200))

@app.route("/")
def index():

    return render_template("index.html")


@app.route("/deletefile", methods=["GET", "POST"])
def deletefile():
    fileName = request.form.get('delete')
    return render_template("home.html")


@app.route("/viewRecords")
def records():
    all_files=[]
    dem_hs = []
    files = UserFiles.query.filter_by(username=session.get('user')).all()
    h = "d"
    for file in files:
        all_files.append(file.fileName)
    return render_template("viewRecords.html", len = len(all_files), records=all_files,x=files )


@app.route("/home")
def home():
    username = session['user']
    return render_template("home.html", user=username)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["uname"]
        passw = request.form["passw"]
        
        login = User.query.filter_by(username=uname, password=passw).first()
        if login is not None:
            session['user'] = uname
            return redirect(url_for("home", user=uname))
    return render_template("login.html" )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form['uname']
        mail = request.form['mail']
        passw = request.form['passw']

        register = User(username=uname, email=mail, password=passw)
        db.session.add(register)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("register.html")


@app.route('/upload')  
def upload():
    username = session.get('user')  
    return render_template('file_upload_form.html', user=username)





@app.route('/verif')  
def verif():
    username = session.get('user')  

    input = request.files('file')
    filed = "app.py"

    with open(filed , 'r') as f:
        contents = f.read()

    haze = users_collection.find_one({"name" : input.filename})

    haze_n = haze['hash']

    Hash_passcode.verify(contents , haze_n )


    return render_template('verif.html')



@app.route('/success', methods=['POST'])  
def success():  
    if request.method == 'POST':  
        f = request.files['file']

        img_key = hashlib.md5(f.read()).hexdigest()
        check = UserFiles.query.filter_by(md5=img_key).first()
        if check is None: 
            with app.app_context():
                db.create_all()
                f.save(f.filename)
                file = UserFiles(username=session.get('user'), fileName=f.filename, md5=img_key)
                db.session.add(file)
                db.session.commit()
                                # Insert one user into the collection
                user = {"name": f.filename, "hash": img_key}
                users_collection.insert_one(user)
            return render_template("success.html", name=f.filename + " successfully uploaded")
        return render_template("success.html", name=f.filename + " already exists")  


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
 
    app.run(debug=True)
