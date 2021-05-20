from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
import os


#Initize App
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET")



@app.route("/", methods=["get", "post"])
def index():
    """Very simple route for Index page, just returns the index.html page"""
    #Renders home page HTML
    return render_template("index.html")

@app.route("/about/", methods=["get", "post"])
def about():
    """Basically same as home function"""
    #Renders home page HTML, passing in the search bar class instance
    return render_template("about.html")

@app.route("/view/", methods=["get", "post"])
def view():
    """Basically same as home function"""
    #Renders home page HTML
    return render_template("view.html")
  
@app.route("/watch/", methods=["get", "post"])
def watch():
    """Basically same as home function"""
    #Renders home page HTML
    return render_template("watch.html")

@app.route("/priv/", methods=["get", "post"])
def priv():
    """Basically same as home function"""
    #Renders home page HTML
    return render_template("privacy.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
   
          

