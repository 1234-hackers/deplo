import base64
from email import message
from turtle import st
from dns.message import Message
from flask import Flask, render_template, url_for, request, redirect,flash,session
from flask.scaffold import F
from flask_pymongo import PyMongo
from flask_wtf.form import FlaskForm
from pymongo import MongoClient
import passlib
from passlib.context import CryptContext
from passlib.hash import bcrypt_sha256,argon2,ldap_salted_md5,md5_crypt
import time
from datetime import timedelta , datetime
import smtplib
from email.message import EmailMessage
import socket,os
from functools import wraps
from gridfs import*
from bson import ObjectId
#from flask_hcaptcha import hCaptcha
from flask_wtf import RecaptchaField,FlaskForm
from wtforms import *
from wtforms.validators import EqualTo, InputRequired
from flask_wtf.csrf import CSRFProtect
from wtforms.csrf.session import SessionCSRF 
from datetime import timedelta
import email_validator 
import random
#from flask_mail import Mail,Message
import base64
from bson.binary import Binary
from werkzeug.utils import secure_filename
#mpsa imports
#from flask_mpesa import MpesaAPI

import PIL
from PIL import Image

import markupsafe
from markupsafe import escape , Markup
ip = socket. gethostbyname(socket. gethostname())
ipst = str(ip)
application = Flask(__name__)

#captcha


application.config['HCAPTCHA_ENABLED'] =  False

application.config ["HCAPTCHA_SITE_KEY"]  =  "cd654ebc-97ad-44fb-8ddc-963287c6d77b"

application.config ['HCAPTCHA_SECRET_KEY'] = "0xb1E280895395797DCF11D0B1807aa9678A4B391d" 

#hcaptcha = hCaptcha(application)
#images
upload_folder = 'static/images'
application.config['UPLOAD_FOLDER'] = upload_folder
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])



#csrf protection
SECRET_KEY = "dsfdsjgdjgdfgdfgjdkjgdg"
csrf = CSRFProtect(application)

#mongoDB configs
application.config['MONGO_DBNAME'] = 'users'
# application.config['MONGO_URI'] = 'mongodb://'+ipst+':27017/users'
application.config['MONGO_URI'] = 'mongodb://localhost:27017/users'

mongo = PyMongo(application)

client = MongoClient('localhost', 27017)
db_pic = client.users
gfs = GridFS(db_pic)

application.permanent_session_lifetime = timedelta(days=30)

Hash_passcode = CryptContext(schemes=["sha256_crypt" ,"des_crypt"],sha256_crypt__min_rounds=131072)

mongo = PyMongo(application)

users = mongo.db.users
link_db = mongo.db.links
verif = mongo.db.verify_email

def login_required(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if "login_user" in session:
            return f(*args,**kwargs,)
        else:
            time.sleep(2)
            return redirect(url_for('home'))
    return wrap

        
def re_sess(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if "login_user" in session:
            return f(*args,**kwargs,)
        else:
            time.sleep(2)
            return redirect(url_for('login'))
    return wrap
    
class Base_form(Form):
    
    class Meta:
        csrf = False
        csrf_class = SessionCSRF
        csrf_secret = 'EPj00jpfj8Gx1SjndfgdgdgdfgdfgyLxwBBSQfnQ9DJYe0Ym'
        csrf_time_limit = timedelta(minutes=20)
        
           
@application.route('/',methods = ["POST","GET"])
def home():
    if request.method == "POST":# and hcaptcha.verify():
        email = request.form['email']
        existing_user  = users.find_one({'email':email} )
        if existing_user:
                passcode = request.form['passcode']
                v = str(existing_user['verified'])

                existing_pass = existing_user['password']
                if Hash_passcode.verify(passcode,existing_pass):
                    username = existing_user['username']
                    if username in session:
                        fa = existing_user['tags']
                        if len(fa) < 5:
                             return redirect(url_for('choose_tags'))
                        if v == 0:
                            return redirect(url_for('complete_regist'))
                        else:
                            return redirect(url_for('feed'))
                    else:    
                        session_time = request.form.get("session_time") 
                        if  session_time == 2:
                            session.parmanent = True
                        session['login_user'] = email
                        fa = existing_user['tags']
                        if len(fa) < 5:
                            return redirect(url_for('choose_tags'))
                        else:    
                            return redirect(url_for('feed'))   
    return render_template("index.html")


def reset_session_required(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if "login_user" in session:
            return f(*args,**kwargs,)
        else:
            time.sleep(2)
            return redirect(url_for('reset_pass'))
    return wrap
@application.route('/reset_pass/', methods = ['POST','GET'])

def  reset_pass():
    reset_db = mongo.db.pass_reset
    code = random.randint(145346 , 976578)
    code = str(code)
    if request.method == "POST":
        email = request.form['email']
        existing = users.find_one({'email':email} )
        if existing:
            '''
            Send message here with the code
            '''
            now = datetime.now()
            r_now =  now.strftime("Date  %Y:%m:%d: Time %H:%M:%S")
            session['rset'] = email
            reset_db.insert_one({"email" : email , "code" : code , "time_in" : r_now})
            return redirect(url_for("enter_code"))      
        else:
            return redirect(url_for('register'))
    return render_template('reset_pass.html')
@application.route('/enter_code/' , methods = ['POST','GET'])

def enter_code():
    email = session['rset']
    if email in session:
        if request.method == "POST":
            reset_db = mongo.db.pass_reset
            code = request.form['code']
            mailed = email
            legit = reset_db.find_one({"email" : email})
            if legit:
                legit_code = legit["code"]
                now = datetime.now()
                now = now.strftime("Date  %Y:%m:%d: Time %H:%M:%S")
                req_time = legit['time_in']
                diff = now - req_time
                if code == legit_code and diff < 7:
                    return redirect(url_for('peopleass'))  
                if diff > 7:
                    return redirect(url_for('reset_pass' ))
            else:
                return redirect(url_for('reset_pass'))
    else:
        return redirect(url_for('reset_pass'))
            
    return render_template('enter_code.html')
     
class peopleass(Base_form):
      
        pass1 = PasswordField("Password" , [validators.Length(min = 8 , max = 15 , message = "Minimum Length Is 8 Characters")]) 
           
        pass2 = PasswordField("Confirm Password" , [validators.Length(min = 8,max=15 , message="8 To 15 Characters") , EqualTo("passc",message="Must Be Same To The Input Above") , InputRequired()])
        
        

@application.route('/peopleass/' , methods = ['POST','GET'])
@login_required
def peopleass(email):
    form = peopleass()
    if request.method == "POST" and form.validate():
        users = mongo.db.users
        target_account = session['rset'] 
        pass1 = form.pass1.data
        pass2 = form.pass2.data
        if pass1 == pass2 and len(pass2) > 8 and len(pass2) < 15 :
            passcode = Hash_passcode.hash(pass2)
            the_user = users.find_one({"email" : email})
            users.find_one_and_update({"email" :target_account} , { 'set' : {"password" : passcode} })
            session['login_user'] = target_account
            return redirect(url_for('main'))
        else:
            check_pass = " Please Check The Password And Try Again"
            return render_template('peopleass.html' , form = form , mess = check_pass)
            
    return render_template('peopleass.html' , form = form)


class Base_form(FlaskForm):
    
    class Meta:
        csrf = True 
        csrf_class = SessionCSRF 
        csrf_secret = b"cffhgfghfgjgherydumbo"
        csrf_time_limit = timedelta(minutes=25)
                   
@application.route('/login/' , methods = ['POST','GET'])
def login():
 
    if request.method == "POST":# and  hcaptcha.verify():
        email = request.form['email']
        existing_user  = users.find_one({'email':email} )
        if existing_user:
                passcode = request.form['passcode']

                existing_pass = existing_user['password']
                v = str(existing_user['verified'])
                if Hash_passcode.verify(passcode,existing_pass)  :
                    username = existing_user['username']
                    if username in session:
                        fa = existing_user['tags']
                        if len(fa) < 5:
                             return redirect(url_for('choose_tags'))
                        if v == 0:
                            return redirect(url_for('complete_regist'))
                        else:
                            return redirect(url_for('feed'))
                    else:    
                        session_time = request.form.get("session_time") 
                        if  session_time == 2:
                            session.parmanent = True
                        session['login_user'] = email
                        fa = existing_user['tags']
                        if len(fa) < 5:
                            return redirect(url_for('choose_tags'))
                        else:    
                            return redirect(url_for('feed'))
    return render_template('login.html')

@application.route('/logout/' , methods = ['POST','GET'])
@login_required
def logout():
    if request.method == "POST":
        if request.form['sub'] == "Yes":
            session.pop('login_user', None)
            return redirect(url_for('login'))
        else:
            return redirect(url_for('feed')) 
    return render_template('logout.html')

@application.route('/register/',methods = ['POST','GET'])
def register():
    
    if request.method == "POST" and "img" in request.files:
        
        pic = request.files['img']
        
        email = request.form['email']
        
        username =  request.form['username']
        
        passc = request.form['passc']
        
        passc2 = request.form['passc2']
        
        hashed = Hash_passcode.hash(passc2)
        
        filename = pic.filename
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
            
        registered = users.find_one({"email":email})
        if registered:
            mess = "You are already registered,please Log in"
            return redirect(url_for('home'))
        if passc == passc2  and not registered:
            if allowed_file(filename):
                fl = email.replace("." , "")
                os.mkdir("static/images/" + fl)
                pt = "static/images/" + fl + "/"
                des = fl + "/" + filename
                dess = "static/images/" + des
                
                pic.save("static/images/" + des)
                image1 = "static/images/" + des
                image = Image.open(image1)
                image2 = image.resize((150,150),Image.ANTIALIAS)
                new = image2.convert("RGB")
                new.save(pt + fl + '.jpg')
                
                image = pt +fl + ".jpg"
                
                os.remove(dess)
            
            mess = "Registerd Successfully" 
            favs = []
            tags = []
            users.insert_one({"email":email ,'username':username , "password":hashed , 
                             "favs" : favs , "tags" : tags , "verified" :0 , 'saved' : [] })
            
            if users.find_one({"email":email}):
                code = random.randint(145346 , 976578)
                code = str(code)
                session['login_user'] = email
                verif.insert_one({"email" : email , "code" : code })
                #send the code Here
                
                return redirect(url_for('complete_regist'))
    return render_template('register.html')

class complete_regist(Base_form):
    code = StringField("Verification Code" , [validators.InputRequired(message="Please Enter The Code Sent Via Email")])

@application.route('/complete_regist' , methods = ['POST' , 'GET'])
@login_required
@re_sess
def complete_regist():
    verif = mongo.db.verify_email
    user_email = session['login_user']
    in_db = verif.find_one({"email" : user_email})
    if request.method == "POST":
        de_code = request.form['code']
        if in_db:
            code = str(in_db['code'])
            if code == de_code:
                users.find_one_and_update({"email" : user_email} ,{ '$set' :  {"verified": 1}} )
                verif.find_one_and_delete({'email' : user_email})
                return redirect(url_for('choose_tags'))
            else:
                print("Wrong Code")
                time.sleep(2)
                return redirect(url_for('complete_regist'))
        else:
            return redirect(url_for('register'))
            
    return render_template('verif_reg.html' , m = user_email)
    


@application.route('/choose_tags/' , methods = ['POST','GET'])
@login_required
def choose_tags():
    the_tags = tags1 = ['music','sports','crypto','technology','real estate','nature','art',
                        'gaming','nft','politics','elon','watch','memes','russia']
    user_email = session['login_user']
    if request.method == "POST":
        aaction = request.form.getlist('tags')
        user_db = mongo.db.users
        
        list2 = random.sample(the_tags , 6)
        user = user_db.find_one({"email" : user_email})
        if len(aaction) < 5:
            em_tags = user['tags']
            for x in list2:
                em_tags.append(x)
            user_db.find_one_and_update({"email" : user_email} ,{ '$set' :  {"tags": em_tags}} )
            return redirect(url_for('feed'))
        else:
            em_tags = user['tags']
            for y in aaction:
                em_tags.append(y)
            user_db.find_one_and_update({"email" : user_email} ,{ '$set' :  {"tags": em_tags}} )
            return redirect(url_for('feed' ))      
    return render_template('choose_tags.html' , tags = the_tags)

@application.route('/feed/' , methods = ['POST','GET'])
@login_required
def feed():
    link_db = mongo.db.links
    em = link_db.find()
    user = mongo.db.users
    trending_db = mongo.db.trending
    randomly = link_db.find().limit(100)
    render_array = []
    render_array.extend(randomly)
    #based on following people
    user_email = session['login_user']
    the_user = users.find_one({"email" : user_email})
    favs = the_user["favs"]
    fav_arr = []
    if len(favs) <10:
        count = 3
    else:
        count = 2
    for x in favs:         
        user = x
        documentz = link_db.find({"owner" : user }).limit(count)
        for kk in documentz:
            if not kk in render_array:
                fav_arr.extend(documentz)      
    render_array.extend(fav_arr)

    #based on tags
    my_tags = the_user["tags"]
    for y in my_tags:
        indiv_tags  = y
        #relevant = trending_db.find({"tags" : tags})
        arr1 = []
        all_posts= link_db.find().limit(300)
        for x in all_posts:
            tags = x['tags']
            if indiv_tags in tags:
                if not  x in render_array: 
                    arr1.append(x)        
    render_array.extend(arr1)
    random.shuffle(render_array)
    
        
    #view link functionality
    if request.method == "POST":
        the_id = request.form['id']
        if request.form['sub'] == "View": 
            session["linky"] = the_id
            the_post = link_db.find_one({"post_id" : the_id})
            likes= the_post['likes']
            total_likes = len(likes)
            clicker = session['login_user']
            if clicker in likes:
                likes.remove(clicker)
                total_likes = len(likes)
                link_db.find_one_and_update({"post_id" : the_id} ,{ '$set' :  {"likes": likes  , 'total_likes' : total_likes }} )
                return redirect(url_for('view_link' ))
                
            else:
                likes.append(clicker) 
                total_likes = len(likes)
                link_db.find_one_and_update({"post_id" : the_id} ,{ '$set' :  {"likes": likes  , 'total_likes' : total_likes}} )
                return redirect(url_for('view_link' ))
            
        
        
                        
    return render_template('feed.html' , arr = render_array , fav = fav_arr , email = user_email )

@application.route('/search/' , methods = ['POST','GET'])
@login_required
def search():
    user_email = session['login_user']
    if request.method == "POST":
        de_search = request.form['search']
        session['q'] = de_search           
        return redirect(url_for('found_posts'))    
   
    return render_template('search.html')

@application.route('/found_posts/' , methods = ['POST','GET'])
@login_required
def found_posts():
    to_show = []
    de_search = session['q']
    finds = de_search.split()
    al = link_db.find()
    for x in finds: 
        for c in al:
            emt = c['tags']
            if x in emt:
                if not x in to_show:
                    to_show.append(c)      
            lks = c['link']
            de_lin = lks.split()
            if x in de_lin:
                if not x in to_show:
                    to_show.append(c) 
            ttl = c['title']
            de_ttl = ttl.split()
            if x in de_ttl:
                if not x in to_show:
                    to_show.append(c)
            desc = c['description']
            de_desc = desc.split()
            if x in to_show:
                if not x in to_show:
                    to_show.append(c)
            if len(to_show) < 1:
                no = "No Result Found,Please Check Your Spelling See More"
            else:
                no = "Results From Search"
    return render_template('found_post.html' , post = to_show , n = no)


@application.route('/found_people' , methods = ['POST','GET'])
@login_required
def found_people():
    session.pop("de_email" ,None)
    de_search = session['q']
    de_users = []
    people = []
    temp = []
    all_usr = users.find()
    for q in all_usr:
        name = q['username']
        email = q['email']
        new_m = email.split('@' , maxsplit = 1 )
        mai = new_m[0]
        if name == de_search:
            if not q in de_users:
                de_users.append(q) 
        if de_search in mai:
            if not q in de_users:
                de_users.append(q)
        if mai in de_search:
            if not q in de_users:
                de_users.append(q) 
        if name in de_search:
            if not q in de_users:
                de_users.append(q)
        if de_search in name:
            if not q in de_users:
                de_users.append(q) 
        people.extend(de_users)
        new_p = []
        for i in people:
            if i not in new_p:
                new_p.append(i)
    
        if len(new_p) < 1:
                no = "No Result Found,Please Check Your Spelling See More..."
        else:
                no = "Results From Search"
        
        if request.method == "POST":
            the_id = request.form['id']
            if request.form['sub'] == "View Profile": 
                session["de_email"] = the_id
                return redirect(url_for('view_prof' ))
            
            pass
        
    return render_template('found_people.html' , p = new_p , n = no)

@application.route('/pple/' , methods = ['POST','GET'])
@login_required
def pple():
    if request.method == "POST":
        name = request.form['id']
        session.pop("de_email" ,None)
        name = request.form['id']
        session['de_email'] == name
        redirect(url_for('view_prof'))
    
    return render_template('')


@application.route('/profile/' , methods = ['POST','GET'])  
@login_required
def profile():
    trend = mongo.db.trending
    me = session['login_user']
    me2 = me.replace("." , "")
    the_arr = ["electric car" , "rap" , "football"]
    acc = users.find_one({"email" : me})
    favs = acc['favs']
    emps = []
    for x in favs:
        de_name = users.find_one({'email': x})['username']
        emps.append(de_name)
        
    tags = acc['tags']
    user = acc['username']
    minez = []
    my_posts = link_db.find({"owner" : me})
    more_posts = link_db.find({}).limit(5)
    
    
    if os.path.exists("static/images/" + me2 +"/" + me2 +".jpg"):
        prof_pic = "static/images/" + me2 +"/" + me2 +".jpg" 
      
    else:
        prof_pic = "/static/images/default.jpg"
    links = []
    links.append(prof_pic)
    dez_name = Markup(prof_pic)
    nnn =   "/static/images/" + me2 +"/" + me2 +".jpg" 
    if request.method == "POST":
        tag = request.form['sub'] 
    
        if tag:
            session['de_tag'] = tag
            


    def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    user = mongo.db.users
    user_email = session['login_user']
    email = user_email
    fl = email.replace("." , "")
    info = user.find_one({"email" : user_email})
    if request.method == "POST":
        
        if request.form['sub'] == "Update Profile Picture":
            image = request.files['img']
            os.remove('static/images/' + fl)
            filename = image.filename
            if allowed_file(filename): 
                os.mkdir("static/images/" + fl)
                pt = "static/images/" + fl + "/"
                des = fl + "/" + filename
                dess = "static/images/" + des
                    
                image.save("static/images/" + des)
                image1 = "static/images/" + des
                image = Image.open(image1)
                image2 = image.resize((270,150),Image.ANTIALIAS)
                new = image2.convert("RGB")
                new.save(pt + fl + '.jpg')
                image = pt +fl + ".jpg"
                os.remove(dess)
                return redirect(url_for('feed'))
        
        
        if request.form['sub'] == "Update Username":
            name = request.form['username']
            if not name == info['username']:
                if not name == "":
                    users.find_one_and_update({"email" : user_email} ,{ '$set' :  {"username":name}})
                    return redirect(url_for('feed'))
             
    
        
                      
    return render_template('profile.html' , me = me , favs = emps , tags = tags , mine = minez ,
                           more = more_posts , links = links , prof = dez_name , nn = nnn ,obj = acc ,inf = info )


@application.route('/saved/' , methods = ['POST','GET'])
@login_required
def saved():
    de_render = []
    user_email = session['login_user']
    the_user = users.find_one({"email" :user_email})
    favss = the_user['saved']
    if len(favss) < 1:
        m = "You Dont Have Saved Items"
    else:
        m = " These Are Your Saved Items"
    n = ""
    if n in favss:
        favss.remove(n)
        users.find_one_and_update({'email' : user_email} , {'$set' :  {'saved':favss}})

    for x in favss:
        the_post = link_db.find_one({"post_id" :x})
        de_render.append(the_post)
    if request.method == "POST":
        the_id = request.form['id']
        if request.form['sub'] == "View Link": 
            session["linky"] = the_id
            return redirect(url_for('view_link' ))
        
        if request.form['sub'] == "Remove":
            the_id = request.form['id']
            favss.remove(the_id)
            users.find_one_and_update({'email' : user_email} , {'$set' :  {'saved':favss}})

    return render_template('saved.html' , favss = de_render , m = m )

@application.route('/view_prof/' , methods = ['POST','GET'])
@login_required
def view_prof():
    user = session['de_email']
    user_email = session['login_user']
    
    the_user = users.find_one({"email" :user})
    mez = users.find_one({'email': user_email})
    
    all_em_posts = link_db.find({'owner' : user})
        

    folloinx = users.find_one({'email' :user_email})
    f = folloinx['favs']
    
    dudes = session["de_email"]
    if dudes in f:
        state = "Unfollow"
    else:
        state = "Follow"
    
    me = user
    me2 = me.replace("." , "")
    
    if os.path.exists("static/images/" + me2 +"/" + me2 +".jpg"):
        prof_pic = "static/images/" + me2 +"/" + me2 +".jpg" 
      
    else:
        prof_pic = "/static/images/default.jpg"
    links = []
    links.append(prof_pic)
    dez_name = Markup(prof_pic)
    nnn =   "/static/images/" + me2 +"/" + me2 +".jpg" 
    
    if request.method == "POST":
        if request.form['sub'] == "Follow":
            em = []
            the_id = request.form['id']
            if not the_id in f:
                f.append(the_id)
                state = "Unfollow"
                users.find_one_and_update({'email' : user_email} , {'$set' : {'favs' : f}})
                return render_template('view_prof.html' , usr = the_user, state = state, pic = nnn , posts = all_em_posts)
            else:
                f.remove(the_id)
                state = "Follow"
                users.find_one_and_update({'email' : user_email} , {'set' : {'favs' : f}})
                return render_template('view_prof.html' , usr = the_user, pic = nnn , state = state , posts = all_em_posts)
                
 
    return render_template('view_prof.html' , usr = the_user, state = state , pic = nnn , posts = all_em_posts)




@application.route('/post_on_tags/' , methods = ['POST','GET'])

@login_required
def post_on_tags():
    
    tag = session['le']
   
    return render_template('post_on_tags.html')
@application.route('/view_link/' , methods = ['POST','GET'])
@login_required
def view_link():
    link_db = mongo.db.links
    user = mongo.db.users
    user_email = session['login_user']
    the_user = users.find_one({"email" : user_email})
    de_name = the_user['username']
    if request.method == "POST":
        the_id = request.form['id']
        words = request.form['comm']
        if request.form['sub'] == "Comment":
                the_post = link_db.find_one({"post_id" : the_id})
                comments = the_post['comments']
                commentz = {de_name : words}
                if not words =="":
                    comments.append(commentz)
                    link_db.find_one_and_update({"post_id" : the_id} ,{ '$set' :  {"comments": comments}} )
  
        if request.form['sub'] == "View Profile": 
            the_id = request.form['id']
            fou = link_db.find_one({"post_id" : the_id})
            the_id_owner = fou['owner']
            session["de_email"] = the_id_owner
            return redirect(url_for('view_prof' ))
        if request.form['sub'] == "Save": 
            saved = the_user['saved']
            if not the_id in saved : 
                saved.append(the_id)
                users.find_one_and_update({'email' : user_email}  ,{ '$set' :  {'saved': saved}}) 
                return redirect(url_for('saved'))
            else:
                pass
                
                

    link = session['linky']
    link_db = mongo.db.links
    render_arr = []
    all_posts = link_db.find()
    post_in = link_db.find_one({"post_id" : link})
    if post_in :
        post_in_2 =  link_db.find_one({"post_id" : link})
        post_tags = post_in_2['tags']
        for y in post_tags:
            indiv_tags  = y
            #relevant = trending_db.find({"tags" : tags})
            arr1 = []
            all_posts= link_db.find({}).limit(500)
            for x in all_posts:
                tags = x['tags']
                if indiv_tags in tags: 
                    if not x in render_arr: 
                        arr1.append(x)        
        render_arr.extend(arr1)
        if len(render_arr) < 500:
            random_psts = all_posts = link_db.find().limit(10)
            for x in random_psts:
                p = x
                if not p in render_arr:
                    render_arr.extend(random_psts)   
            
    else:
        return redirect(url_for('feed'))
    return render_template('view_link.html' , taged = render_arr ,  item = post_in , link = link)

@application.route('/advert/' , methods = ['POST','GET'])
@login_required
def advert():
    advert_db = mongo.db.adverts 
    if request.method == "POST":
        
        title = request.form['title']
        
        description = request.form['description']

        pic = request.files['img']
        
        plan = request.form.get("plan")
        if plan == "1":
            the_plan = "two_dollar"
        if plan == "2":
            plan = "five_dollar"
        if plan == "3":
            the_plan  = "12_dollar"
        if plan == "4":
            plan = "fifty_dollar"
        
        filename = secure_filename(pic.filename)
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS       
        if allowed_file(filename):
            pic.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
            image = upload_folder +  "/" + filename
            with open(image , "rb") as image2string:
                converted_string = base64.b64encode(image2string.read())
                uploa = converted_string.decode('utf-8')        
        advert_db.insert_one({"title" : title , "desc" : description , "ad_pic" : uploa , 
                             "plan" : plan })        
    
    return render_template('advert.html')
@application.route('/post/' , methods = ['POST','GET'])
@login_required
def post(): 
    if request.method == "POST":
        
        th = request.files['thumb']
        
        filename = th.filename
            
        link_db = mongo.db.links
        
        title = request.form['title']
        
        desc = request.form['desc']
        
        link = request.form['link']

        post_id = md5_crypt.hash(title)
            
        tag1 = request.form['tag1']
        
        tag2 = request.form['tag2']

        tag_arr = []
        
        
        
        
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
            
        if allowed_file(filename): 
            da_nam = post_id.replace("." , "")
            da_nami = da_nam.replace("/" , "")
            da_name = da_nami[0:10]
            th.save("static/images/" + filename)
            image1 = "static/images/"  + filename
            image = Image.open(image1)
            image2 = image.resize((500,500),Image.ANTIALIAS)
            new = image2.convert("RGB")
            new.save( "static/images/" + da_name + '.jpg')
            image = da_name + '.jpg'
            to_db =  "/static/images/" + image
        
        tag_arr.append(tag1)
        tag_arr.append(tag2)
        owner = session['login_user']
        wner_name = users.find_one({'email' : owner})
        owner_name = wner_name['username']
        like_arr = [owner]
        comments = []
        now = datetime.now()
        now_c = now.strftime("Time  %Y:%m:%d: , %H:%M:%S")
        timez = now_c
        fl = owner.replace("." , "")
        fjp  = fl + ".jpg"
        imz = "/static/images/"+fl +"/" + fjp
        link_db.insert_one({"owner" : owner , "link" : link ,  "likes" : like_arr , "comments" : comments ,
                            "tags" : tag_arr , "title" : title , "description" : desc , "post_id" : post_id ,
                            'owner_name' : owner_name , 'ima': to_db , 'time' : timez , 'imz' : imz})
        return redirect(url_for('feed'))
    return render_template('post.html')


@application.route('/my_post/' , methods = ['POST','GET'])

@login_required
def my_post():
    me =  session['login_user']
    me2 = me.replace("." , "")
    thiis_guy = users.find_one({"email" : me})
    this_guy = thiis_guy['username']
    
    
    my_posts = link_db.find({"owner" : me})
    tos = []
    for x in my_posts:
        tos.append(x)
   
    if os.path.exists("static/images/" + me2 +"/" + me2 +".jpg"):
        prof_pic = "static/images/" + me2 +"/" + me2 +".jpg" 
      
    else:
        prof_pic = "/static/images/default.jpg"
    
    dez_name = Markup(prof_pic)
    nnn =   "/static/images/" + me2 +"/" + me2 +".jpg" 
    noz = my_posts.count()
        
    if request.method == "POST":
        if request.form['sub'] == "Edit":
            id = request.form['the_id']
            session['post_edit'] = id
            return redirect(url_for('edit_post'))
            
        if request.form['sub'] == "Delete":
            id = request.form['the_id']
            link_db.find_one_and_delete({"post_id" : id})
            return render_template('my_post.html' , posts = tos)
         
    return render_template('my_post.html' , posts = tos ,no = noz , dude = this_guy , ppic = nnn)

@application.route('/edit_post/' ,methods = ['POST','GET'])
@login_required
def edit_post():
    da_id = session['post_edit']
    the_post = link_db.find_one({"post_id" : da_id})
    if request.method == "POST":
        de_link = request.form['link']
        de_ttle = request.form['title']
        de_desc = request.form['desc']
        de_tags = request.form['tags']
        
        link = the_post['link']
        title = the_post['title']
        desc= the_post['description']
           
        
        
        if not de_link  == "":
            link = de_link
        if not de_ttle =="":
            title = de_ttle
        if not de_desc =="":
            desc = de_desc
        if not de_tags =="":
            tags = de_tags
            tags = tags.split(",")
   
            link_db.find_one_and_update({"post_id" : da_id } , { '$set' :  {"link" : link ,"title" : title , "description" : desc, "tags" : tags}})  
            return redirect(url_for('my_post'))
    
    return render_template('edit_post.html' , post = the_post)
    
@application.route('/test/' , methods = ['POST' , 'GET'])
def test():
     
     
    return render_template('view_links2.html')  
 
@application.route('/trs/' , methods = ['POST' , 'GET'])
def trs():
    
    
    return render_template("ep.html")


if __name__ == "__main__":
    application.secret_key = "Fuckoffmen"
    application.run(debug = True , port = 5006)

    
