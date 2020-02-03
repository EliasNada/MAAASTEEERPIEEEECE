# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 16:23:47 2019

@author: Elias
"""
from flask import Flask,render_template,request
import sqlite3 as sql

app = Flask(__name__)    
    
@app.route("/",methods=["POST","GET"])
def index():
    with sql.connect("foodie.db") as con:
        cur = con.cursor()
        cur.execute("select post_id,post_img from posts")
        data= cur.fetchall()
        return render_template("index.html",data=data)


@app.route("/reserve",methods=["POST","GET"])
def reserve():
    if request.method=="POST":
        client_name=request.form["form_name"]
        client_email=request.form["email"]
        client_phone=request.form["phone"]
        persons=request.form["no_of_persons"]
        date=request.form["date-picker"]
        time=request.form["time-picker"]
        food=request.form["preferred_food"]
        occasion=request.form["occasion"]
        with sql.connect("foodie.db") as con:
            cur = con.cursor()
            cur.execute("insert into reservations (client_name,client_email,client_phone,number_of_persons,    \
                                                   client_date,client_time,client_preffered_food,occasion)     \
                        values(?,?,?,?,?,?,?,?)",(client_name,client_email,client_phone,persons,date,time,food,occasion))
            return render_template("view.html",i=(client_name,client_email,client_phone,persons,date,time,food,occasion))

@app.errorhandler(404)
def notFound(error):
    return render_template("404.html")
@app.errorhandler(500)
def notFound(error):
    return render_template("404.html")

if __name__ == "__main__":
    app.run()