import base64
from email import message
#from turtle import st
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
from datetime import  datetime as dt
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
from flask_wtf.csrf import CSRFProtect,CSRFError
from wtforms.csrf.session import SessionCSRF 
from datetime import timedelta
import email_validator 
import random
import requests
#from flask_mail import Mail,Message
import base64
from bson.binary import Binary
#from werkzeug.utils import secure_filename
#mpsa imports
#from flask_mpesa import MpesaAPI
import pyshorteners

import markupsafe
from markupsafe import escape , Markup

from pymongo import MongoClient
from pymongo.server_api import ServerApi
uri = "mongodb+srv://jackson:mutamuta@hbcall.ihz6j.azure.mongodb.net/test?retryWrites=true&w=majority" 
 # Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
 # Get the users collection

#from postmarker.core import PostmarkClient
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
application.config['MONGO_URI'] = 'mongodb://localhost:27017/main'

mongo = PyMongo(application)

application.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

Hash_passcode = CryptContext(schemes=["sha256_crypt" ,"des_crypt"],sha256_crypt__min_rounds=131072)

mongo = PyMongo(application)

users = client.flaka.users
link_db = client.flaka.links
verif = client.flaka.verify_email
creators = client.flaka.creators
ips = client.flaka.ips


def login_required(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if "login_user" in session:
            return f(*args,**kwargs,)
        else:
            time.sleep(2)
            return redirect(url_for('login'))
    return wrap


def creator_required(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if "creator" in session:
            return f(*args,**kwargs,)
        else:
            time.sleep(2)
            return redirect(url_for('login_creator'))
    return wrap

def handle_csrf_error(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if not f == "":
            return render_template('index.html', error=f), 400
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
    
           
@application.route('/',methods = ["POST","GET"])
def home():
    r = link_db.find({}).limit(500)
    to_show = []
    em = []
    for x in r:
        em.append(x)
    random.shuffle(em)

    user_ip = request.remote_addr

    # Make a request to the IP geolocation service (ipinfo.io in this case)
    response = requests.get(f"https://ipinfo.io/{user_ip}")
    data = response.json()

    # Extract location information
    city = data.get('city', '')
    region = data.get('region', '')
    country = data.get('country', '')
    dag = ips.find_one({"ip":user_ip})
    if not dag:
        ips.insert_one({"city":city,"country":country,"ip":user_ip,"revisit":0})
    else:
       new_val = dag["revisit"] + 1
       ips.find_one_and_update({"ip" : user_ip} ,{ '$set' :  {"revisit": new_val}} )
    return render_template("landing.html",arr = em)


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
    reset_db = client.flaka.pass_reset
    code = random.randint(145346 , 976578)
    code = str(code)
    if request.method == "POST":
        email = request.form['email']
        existing = users.find_one({'email':email} )
        if existing:

            '''
            postmark = PostmarkClient(server_token='POSTMARK-SERVER-API-TOKEN-HERE')

# Send an email
postmark.emails.send(
  From='sender@example.com',
  To='recipient@example.com',
  Subject='Postmark test',
  HtmlBody='HTML body goes here'
)
            Send message here with the code
            '''
            now = dt.now()
            r_now =  now.strftime("Date  %Y:%m:%d: Time %H:%M:%S")
            session['rset'] = email
            if not reset_db.find_one({"email" : email}):
                reset_db.insert_one({"email" : email , "code" : code , "time_in" : r_now})
            return redirect(url_for('enter_code'))      
        else:
            return redirect(url_for('register'))
    return render_template('reset_pass.html')
@application.route('/enter_code/' , methods = ['POST','GET'])

def enter_code():
    email = session['rset']
    if "x" =="x":
        if request.method == "POST":
            reset_db = client.flaka.pass_reset
            code = request.form['code']
            legit = reset_db.find_one({"email" : email})
            if legit:
                legit_code = legit["code"]
                now = dt.now()
                now = now.strftime("Date  %Y:%m:%d: Time %H:%M:%S")
                req_time = legit['time_in']
                def timez():
                    now = dt.now()
                    now3 = now.strftime("Date  %Y:%m:%d: Time %H:%M:%S")
                    cr = str(now3)[23:28]
                    first_min = cr[3:5]
                    first_hour = cr[0:2]

                    cr2 = str(req_time)[23:28]
                    second_min = cr2[3:5]
                    second_hour = cr2[0:2]

                    dif = int(second_min) - int(first_min)
                    hours = int(first_hour) - int(second_hour)
                    if dif < 0:
                        dif = dif + 60
                    return dif
                    
                diff =timez()
                if code == legit_code:
                    reset_db.find_one_and_delete({'email' : email})
                    return redirect(url_for('peopleass'))  
                else:
                    return redirect(url_for('reset_pass' ))

            
    return render_template('enter_code.html')
     
      

@application.route('/peopleass/' , methods = ['POST','GET'])
def peopleass():
    email = session['rset']
    if request.method == "POST":
        users = client.flaka.users
        target_account = session['rset'] 
        pass1 = request.form['pas1']
        pass2 = request.form['pas2']
        if pass1 == pass2:
            passcode = Hash_passcode.hash(pass2)
            the_user = users.find_one({"email" : email})
            users.find_one_and_update({"email" :target_account} , { '$set' : {"password" : passcode} })
            session['login_user'] = target_account
            return redirect(url_for('feed'))
        else:
            check_pass = " Please Check The Password And Try Again"
            return render_template('new_pass.html', mess = check_pass)
            
    return render_template('new_pass.html' , form = form)


                  
@application.route('/login/' , methods = ['POST','GET'])
def login():
    if request.method == "POST":# and  hcaptcha.verify():
        email = request.form['email']
        existing_user  = users.find_one({'email':email} )
        if existing_user:
                passcode = request.form['passcode']
                v = str(existing_user['verified'])

                existing_pass = existing_user['password']
                if Hash_passcode.verify(passcode,existing_pass):
                    username = existing_user['email']
                    if username in session:
                        if v == 0 :
                             return redirect(url_for('complete_regist'))
                        else:
                            return redirect(url_for('feed'))
                    else:    
                        session.parmanent = True
                        session['login_user'] = email
                        return redirect(url_for('feed'))
    return render_template('login.html')



@application.route('/login_creator/' , methods = ['POST','GET'])
@login_required
def login_creator():
    if request.method == "POST":# and  hcaptcha.verify():
        email = request.form['user']
        existing_user  = creators.find_one({'username':email} )
        if existing_user:
                passcode = request.form['passcode']

                existing_pass = existing_user['password']
                if Hash_passcode.verify(passcode,existing_pass):
                    username = existing_user['username']
                    if username in session:
                        return redirect(url_for('post'))
                    else:
                        session.parmanent = True
                        session['creator'] = email
                        return redirect(url_for('post'))
    return render_template('login_creator.html')



@application.route('/creator_terms/' , methods = ['POST','GET'])
@login_required
def creator_terms():



     return render_template('agree.html')



@application.route('/request_account/' , methods = ['POST','GET'])
@login_required
def request_account():
     if request.method == "POST":
          plan = request.form.get('options')
          username = request.form['email']
          password =request.form['passcode']
          paasc = Hash_passcode.hash(password)
          leg = creators.find_one({'username':'xhot'})
          dl = leg['Ems']
          dalist = dl.split(',')
          emo = random.choice(dalist)
          creators.insert_one({'username': username , 'plan': plan , 'password':paasc ,'veri':1,'emote': emo })
          return redirect(url_for('post'))

     return render_template('req_acc.html')



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
    
    if request.method == "POST":
        
#        pic = request.files['img']
        
        email = request.form['email']
        
#        username =  request.form['username']
        
        passc = request.form['passc']
        
        passc2 = request.form['passc2']
        
        hashed = Hash_passcode.hash(passc2)
            
        registered = users.find_one({"email":email})
        if registered:
            mess = "You are already registered,please Log in"
            return redirect(url_for('home'))
        if passc == passc2  and not registered:
          favs = []
          tags = []
          users.insert_one({"email":email  , "password":hashed , 
                             "favs" : favs , "tags" : tags , "verified" :0 , 'saved' : [], "viewed" :[]  })
            
          if users.find_one({"email":email}):
                code = random.randint(145346 , 976578)
                code = str(code)
                session['login_user'] = email
                if not verif.find_one({"email" : email}):
                    verif.insert_one({"email" : email , "code" : code })
                    #send the code Here
                    return redirect(url_for('complete_regist'))
                else:
                    return redirect(url_for('complete_regist'))
                    
                
                
    return render_template('register.html')

@application.route('/complete_regist' , methods = ['POST' , 'GET'])
def complete_regist():
#    verif = client.flaka.verify_email
    user_email = session['login_user']
    in_db = verif.find_one({"email" : user_email})
    if request.method == "POST":
        de_code = request.form['code']
        if in_db:
            code = str(in_db['code'])
            if code == de_code:
                users.find_one_and_update({"email" : user_email} ,{ '$set' :  {"verified": 1}} )
                verif.find_one_and_delete({'email' : user_email})
                return redirect(url_for('login'))
            else:
                print("Wrong Code")
                time.sleep(2)
                return redirect(url_for('complete_regist'))
        else:
            return redirect(url_for('register'))
            
    return render_template('verif_reg.html' , m = user_email)
    


@application.route('/feed/' , methods = ['POST','GET'])
@login_required
def feed():
    session.pop('viewing', None)
    link_db = client.flaka.links
    em = link_db.find()
    user = client.flaka.users
    trending_db = client.flaka.trending
    randomly = link_db.find().limit(100)
    render_array = []
    render_array.extend(randomly)

    random.shuffle(render_array)
    for x in render_array:
        views = x['viewed']
        idn = x['_id']
        new = int(views)
        new_val = new + 1
        link_db.find_one_and_update({"_id" : idn} ,{ '$set' :  {"viewed": new_val}} )

    #view link functionality
    if request.method == "POST":
        return redirect(url_for('feed'))

    random.shuffle(render_array)
    return render_template('feed.html' , arr = render_array )

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
    trend = client.flaka.trending
    me = session['login_user']
    me2 = me.replace("." , "")
    the_arr = ["electric car" , "rap" , "football"]
    acc = users.find_one({"email" : me})

    return render_template('profile.html' , me = me  )


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
        if request.form['sub'] == "View": 
            session["linky"] = the_id
            return redirect(url_for('view_link' ))
        
        if request.form['sub'] == "Remove":
            the_id = request.form['id']
            if the_id in favss:
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
                users.find_one_and_update({'email' : user_email} , {'$set' : {'favs' : f}})
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
    link_db = client.flaka.links
    user = client.flaka.users
    user_email = session['login_user']
    the_user = users.find_one({"email" : user_email})
    viewed = the_user['viewed']
    
    de_name = str(the_user['username'])
    if request.method == "POST":
        the_id = request.form['id']
        if request.form['sub'] == "Comment":
                newx = []
                words = request.form['comm']
                the_post = link_db.find_one({"post_id" : the_id})
                comments = the_post['comments']
                commentz = {de_name : words}
                if not words =="" :
                    if not commentz in comments:
                        comments.append(commentz)
                        link_db.find_one_and_update({"post_id" : the_id} ,{ '$set' :  {"comments": comments}} )
                else:
                    return redirect(url_for('view_link'))
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
    link_db = client.flaka.links
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
    advert_db = client.flaka.adverts 
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

import secrets
from flask_uploads import UploadSet, configure_uploads, DATA
from werkzeug.utils import secure_filename
application.config['UPLOADED_VIDEOS_DEST'] = 'static/videos'


# Initialize the UploadSet
videos = UploadSet('videos', extensions=('jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm', 'm4v', 'mpeg', '3gp' ,'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm', '.m4v', '.mpeg', '.3gp'))
configure_uploads(application, videos)

@application.route('/post/', methods=['GET', 'POST'])
@login_required
@creator_required
def post():
    if request.method == 'POST':
        if 'thumb' not in request.files:
            return 'No file part'
        file = request.files['thumb']
        if file.filename == '':
            return 'No selected file'
        if file and videos.file_allowed(file, file.filename):
            dn = secure_filename(file.filename)
            #filename = videos.save(file)
            th = request.files['thumb']
            filename = th.filename
            delimeter = "."
            result = filename.split(delimeter, 1)[-1].strip()
            random_string = secrets.token_hex(13)
            new_filename = f"{random_string}"
            file.save(os.path.join(application.config['UPLOADED_VIDEOS_DEST'], new_filename + "." + result))

            link_db = client.flaka.links

            title = request.form['title']

            owner = session['login_user']
            cr =  session['creator']
            dec = creators.find_one({'username':cr })
            cd = dec['emote']
            viewed = random.randint(530,1000)
            xn = users.find_one({"email" : owner})
            #owner_name =xn["username"]
            now = dt.now()
            now_c = now.strftime("Time  %Y:%m:%d: , %H:%M:%S")
            timez = now_c

            fl = owner.replace("." , "")
            fjp  = fl + ".jpg"

            imz = "/static/images/"+fl +"/" + fjp

            post_id = md5_crypt.hash(title)
            da_nam = post_id.replace("." , "")
            da_nami = da_nam.replace("/" , "")
            da_name = da_nami[0:10]
            fle =  "/static/videos/" + new_filename + "." + result

            link_db.insert_one({ "viewed": viewed, "title" : title ,
                "post_id" : post_id , 'owner':owner, 'creator': cr, 'ima': fle , 'time' : timez , 'imz' : cd})

            return redirect(url_for('feed'))
        else:
            return 'Invalid file or file type not allowed'
    return render_template('pt.html')


@application.route('/my_post/' , methods = ['POST','GET'])

@login_required
def my_post():
    me =  session['login_user']
    me2 = me.replace("." , "")
    thiis_guy = users.find_one({"email" : me})

    my_posts = link_db.find({"owner" : me})
    
    tos = []
    for x in my_posts:
        tos.append(x)
    ll = len(tos)
    if ll  < 1:
        mess = "You Dont Have Any Posts"
    else:
        mess = "Manage Your posts"

    noz = len(tos)
        
    if request.method == "POST":
        if request.form['sub'] == "Edit":
            id = request.form['the_id']
            session['post_edit'] = id
            return redirect(url_for('edit_post'))
            
        if request.form['sub'] == "Delete":
            id = request.form['the_id']
            link_db.find_one_and_delete({"post_id" : id})
            my_posts2 = link_db.find({"owner" : me})
            new = []
            for x in my_posts2:
                new.append(x) 
            return render_template('my_post.html' , posts = new ,no = noz , dude = thiis_guy )
         
    return render_template('my_post.html' , posts = tos ,no = noz , dude = thiis_guy, mess= mess)

@application.route('/edit_post/' ,methods = ['POST','GET'])
@login_required
def edit_post():
    da_id = session['post_edit']
    the_post = link_db.find_one({"post_id" : da_id})
    if request.method == "POST":
        de_ttle = request.form['title']
        de_tags = request.form['tags']
        detags = de_tags.split(',')

        title = the_post['title']

        if not de_ttle =="":
            title = de_ttle
        else:
            title = title

        link_db.find_one_and_update({"post_id" : da_id } , { '$set' :  {"title" : title ,
            "edited" : "Modified", "tags" : detags}})  
        return redirect(url_for('my_post'))
    
    return render_template('edit_post.html' , post = the_post)
    
@application.route('/test/' , methods = ['POST' , 'GET'])
def test():
     
     
    return render_template('view_links2.html')  
 
@application.route('/trs/' , methods = ['POST' , 'GET'])
def trs():
    
    
    return render_template("ep.html")


@application.route('/topics/' , methods = ['POST' , 'GET'])
def topics():

    try:
        if request.method == "POST":
            rend = []
            the_topic = request.form['sub']
            rele = link_db.find().limit(100)
            for x in rele:
                y = x['tags']
                if the_topic in y:
                    rend.append(x)
                desc = x['description']
                if the_topic in desc:
                    if not x in rend:
                        rend.append(x)
                        
                if len(rend) < 1:
                    trending_db = client.flaka.links
                    rend2 = trending_db.find().limit(15)
                    return render_template("topics.html" , t = rend2)
            redirect(url_for('topics'))
    except UnboundLocalError as xz:
        return redirect(url_for('feed'))

    return render_template("topics.html" , t = rend)





@application.route('/receive_data', methods=['POST','GET'])
def receive_data():
     if request.method =="POST":

          data = request.json  # Assuming the data is sent as JSON
          # Process the data here
          return render_template("r.html",t = data)
     return render_template("r.html")


if __name__ == "__main__":
    application.secret_key = "Fucddggdgdfdgdrer5677u"
    application.run(debug = True , port = 5006)

    
