# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 16:23:47 2019

@author: Elias
"""
from flask import Flask,render_template,request,redirect,url_for,session,flash,Response,jsonify,make_response
from werkzeug.security import generate_password_hash, check_password_hash
import os
from pathlib import Path
from werkzeug.utils import secure_filename
import sqlite3 as sql
import datetime


app = Flask(__name__)

app.config["IMAGE_UPLOADS"] = app.root_path+'\static\img'
app.config["POST_UPLOADS"] = app.root_path+'\static\posts'

app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
app.config["MAX_IMAGE_FILESIZE"] =  500000
app.secret_key = "XD"


def set_password(password):
        return generate_password_hash(password)
def check_password( password):
        return check_password_hash(password_hash, password)

def allowed_image(filename):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False

def allowed_image_filesize(filesize):
#    print(filesize)
    if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
        return True
    else:
        return False
    
    
@app.route("/",methods=["POST","GET"])
def index():
    if request.method == "GET":
        try:
            session['username']
            return render_template("index0.html")
        except:
            return redirect("signin")
        

@app.route("/signup",methods=["POST","GET"])
def signup():
    if request.method == "GET":
        try:
            session['username']
            return render_template("signup.html")
        except:
            flash("login -_-")
            return redirect("signin")
    else:
        flash("Already Logged In")
        return redirect(url_for('index'))
    
    
@app.route("/regist",methods=["POST","GET"])
def regist():
    if request.method == "POST":
        user=request.form["username"]
        rawpsw=request.form["psw"]
        img=os.path.join("/static/img/", "default.png")
        with sql.connect("foodie.db") as con:
                    cur = con.cursor()
                    cur.execute("insert into users (username,pass,img) \
                            values (?,?,?)",(user,rawpsw,img))
                    con.commit()
        return redirect(url_for('signin'))
    
    
@app.route("/signin",methods=["POST","GET"])
def signin():
    if request.method == "GET":
        try:
            session["username"]
            flash("Already Logged In")
            return redirect(url_for('index'))
        except:
            return render_template("signin.html")
    else:
        flash("Already Logged In")
        return redirect(url_for('index'))

@app.route("/auth",methods=["POST","GET"])
def auth():
    if request.method == 'POST':
        user = request.form['username']
        psw = request.form['psw']
        with sql.connect("foodie.db") as con:
            try:
                cur = con.cursor()
                cur.execute("select * from users where username=? AND pass=?",(user,psw))
                acc=cur.fetchall()[0]
            except:
                flash('Incorrect password.', 'danger')
                return redirect(url_for('signin'))
            if user == acc[1] and psw == acc[2]:
                session['logged_in'] = True
                session['id'] = acc[0]
                session['username'] = acc[1]
                session.permanent = True
                flash('You are now logged in.', 'success')
                return redirect(url_for('index'))
            else:
                flash('Incorrect password.', 'danger')
                return redirect(url_for('signin'))


@app.route("/user/<name>",methods=["POST","GET"])
def user(name):
    if request.method == "GET":
        try:
            session['username']
        except:
            flash("login -_-")
            return redirect("signin")
        with sql.connect("foodie.db") as con:
            try:
                cur = con.cursor()
                cur.execute("select username,img from users where username=?",(name,))
                acc=cur.fetchall()[0]
                return render_template("user.html",data=acc)
            except:
                print("error")


@app.route("/users",methods=["POST","GET"])
def users():
    try:
        session['username']
    except:
        flash("login -_-")
        return redirect("signin")
    with sql.connect("foodie.db") as con:
        cur = con.cursor()
        cur.execute("select username,img from users order by random()")
        accs=cur.fetchall()
    return render_template("users.html",accs=accs)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    try:
        session['username']
    except:
        flash("login -_-")
        return redirect("signin")
    session.clear()
    flash("Logged Out")
    return redirect(url_for('index'))


@app.route("/img", methods=['GET', 'POST'])
def img():
    if request.method == "POST":
        if request.files:
            image = request.files["img"]
            if "filesize" in request.cookies:
                if not allowed_image_filesize(request.cookies["filesize"]):
                    return "Filesize exceeded maximum limit"
            if image.filename == "":
                return "No filename"
            if allowed_image(image.filename):
                filename = str(datetime.datetime.now().strftime("%f"))+'.'+image.filename.rsplit(".", 1)[1]
                image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))
                img=os.path.join("/static/img/", filename)
                with sql.connect("foodie.db") as con:
                    cur = con.cursor()
                    cur.execute("update users set img=? where username=?",(img,session['username']))
                    con.commit()
                    return redirect(f"/user/{session['username']}")
            else:
                return "That file extension is not allowed"

@app.route("/add",methods=["POST","GET"])
def add():
    try:
        if session["logged_in"]==True:
            return render_template("addpost.html")          
    except:
        flash("You need to log in first!")
        return redirect(url_for('signin'))

@app.route("/addpost",methods=["GET","POST"])
def addpost():
    if request.method == "POST":
        if request.files:
            image = request.files["img"]
            if "filesize" in request.cookies:
                if not allowed_image_filesize(request.cookies["filesize"]):
                    return "Filesize exceeded maximum limit"
            if image.filename == "":
                return "No filename"
            if allowed_image(image.filename):
                filename = str(datetime.datetime.now().strftime("%f"))+'.'+image.filename.rsplit(".", 1)[1]
                image.save(os.path.join(app.config["POST_UPLOADS"], filename))
                desc=request.form["desc"]
                name=request.form["name"]
                img=os.path.join("/static/posts/", filename)
                with sql.connect("foodie.db") as con:
                    cur = con.cursor()
                    cur.execute("insert into posts (post_name,post_img,post_desc,poster_id) values (?,?,?,?)",(name,img,desc,session["id"]))
                    con.commit()
                    return redirect("/")

@app.route("/posts",methods=["GET","POST"])
def posts():
    if request.method =="GET":
        try:
            session['username']
        except:
            flash("login -_-")
            return redirect("signin")
        with sql.connect("foodie.db") as con:
            cur = con.cursor()
            cur.execute("select post_id,post_name,post_desc,post_img,username from posts \
                        left join users on poster_id=id")
            data= cur.fetchall()
            return render_template("foods.html",data=data)
        
@app.route("/delete",methods=["POST","GET"])
def delete():
    if request.method == "POST":
        with sql.connect("foodie.db") as con:
            try:
                name=request.form['name']
                cur = con.cursor()
                cur.execute("delete from posts where post_id=?",(name,))
                return redirect("/posts")
            except:
                print("error")   
                
@app.route("/edit",methods=["POST","GET"])  
def edit():
    try:
        session['username']
    except:
        flash("login -_-")
        return redirect("signin")
    post=request.form["post"]
    return render_template("edit.html",post=post)
                
@app.route("/editpost",methods=["POST","GET"])
def editpost():
    if request.method == "POST":
        if request.files:
            image = request.files["img"]
            if "filesize" in request.cookies:
                if not allowed_image_filesize(request.cookies["filesize"]):
                    return "Filesize exceeded maximum limit"
            if image.filename == "":
                return "No filename"
            if allowed_image(image.filename):
                filename = str(datetime.datetime.now().strftime("%f"))+'.'+image.filename.rsplit(".", 1)[1]
                image.save(os.path.join(app.config["POST_UPLOADS"], filename))
                desc=request.form["desc"]
                name=request.form["name"]
                img=os.path.join("/static/posts/", filename)
                post_id=request.form["post_id"]
                with sql.connect("foodie.db") as con:
                    cur = con.cursor()
                    cur.execute("update posts set post_name=?,post_img=?,post_desc=?,poster_id=? where post_id=?",(name,img,desc,session["id"],post_id))
                    con.commit()
                    return redirect("/posts")
                


@app.errorhandler(404)
def notFound(error):
    return render_template("404.html")

@app.errorhandler(500)
def xd(error):
    return render_template("404.html")

  

if __name__ == "__main__":
    app.run(port=8000)