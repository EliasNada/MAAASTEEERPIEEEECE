# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 16:23:47 2019

@author: Elias
"""
from flask import Flask,render_template
import sqlite3 as sql

app = Flask(__name__)    
    
@app.route("/",methods=["POST","GET"])
def index():
    with sql.connect("foodie.db") as con:
        cur = con.cursor()
        cur.execute("select post_id,post_img from posts")
        data= cur.fetchall()
        return render_template("index.html",data=data)

@app.errorhandler(404)
def notFound(error):
    return render_template("404.html")

if __name__ == "__main__":
    app.run()