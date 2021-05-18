from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
import os
from flask_pymongo import PyMongo
from flask_dance.contrib.google import make_google_blueprint, google
import sys
from datetime import date

#Initize App
app = Flask(__name__)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app.config["SECRET_KEY"] = os.environ.get("SECRET")

#Initilize Mongo
app.config["MONGO_URI"]= os.environ.get("MONGO_URI")
mongo = PyMongo(app)

#Initialize google oauth
app.secret_key = os.urandom(24)
blueprint = make_google_blueprint(
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_SECRET"),
    authorized_url= "/",
    scope = ["https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile", "openid"])
app.register_blueprint(blueprint, url_prefix="/login")


                           
class SignUpForm(FlaskForm):
    """This class creates all of the buttons for the acccount creation form"""
    zipcode = IntegerField("zip")
    submit1 = SubmitField("submit")

class TempForm(FlaskForm):
    """This class creates all of the buttons for the add temp form"""
    temp = IntegerField("temp")
    submit1 = SubmitField("submit")

class Search(FlaskForm):
    """This class is for the search in the nav."""
    fname = StringField("fname")
    search = StringField("search")
    submit = SubmitField("search")

def search_results(text):
    """The function runs whenever a search is submitted it runs the search and renders the HTML"""
    return redirect(text)

@app.route("/", methods=["get", "post"])
def index():
    """Very simple function for providing the home page html; only code other than the return is the search bar code"""
    #Search bar code
    try:
        if google.authorized:
                resp = google.get("/oauth2/v1/userinfo").json()
                if "id" not in session:
                    session["id"] = resp["email"][:resp["email"].index("@")]
                    session["email"] = resp["email"]
                    session["name"] = resp["given_name"]+" "+resp["family_name"]
                    print('Cookie Left', file=sys.stderr)
    except:
        pass

    if "id" in session:
        print('Not index', file=sys.stderr)
        c = mongo.db.users.find_one({'id': session["id"]})
        if c:
            return redirect("my-temp/")
        else:
            return redirect("entry")
    

    #Renders home page HTML, passing in the search bar class instance
    return render_template("index.html")

@app.route("/signin")
def signin():
    if not google.authorized:
        return redirect(url_for("google.login"))
    else:
        return redirect("/")

@app.route("/about", methods=["get", "post"])
def about():
    """Basically same as home function"""
    #Renders home page HTML, passing in the search bar class instance
    return render_template("about.html")

@app.route("/how", methods=["get", "post"])
def how():
    """Basically same as home function"""
    #Renders home page HTML
    return render_template("how.html")
  
@app.route("/changelog", methods=["get", "post"])
def change():
    """Basically same as home function"""
    #Renders home page HTML
    return render_template("changelog.html")

@app.route("/entry/", methods=["get", "post"])
def entry():
    """Very long function; gets data from the primary form and used it to create a user json, add user to all their classes' jsons and the site directory"""
    if not google.authorized:
        print("test1, file=sys.stderr")
        redirect("/")
    resp = google.get("/oauth2/v1/userinfo")
    json1 = resp.json()
    #Initialize form class
    form = SignUpForm()
    #this if statement funs when the form is submitted
    if form.submit1.data and form.is_submitted():
        c = mongo.db.users.find_one({'id': session["id"]})
        if c:
            print("test", file=sys.stderr)
            return redirect("/")
        result = request.form               #Gets data from form in a dictionary data format
        #Creates the majority of the JSON just by directly refrencing the form data 
        data = {"id":json1["email"][:json1["email"].index("@")],
                "email":json1["email"],
                 "zip":result["zipcode"],
                 "temps":[]}
        mongo.db.users.insert(data)
        zip1 = mongo.db.zipscodes.find_one({'zip': result["zipcode"]})
        if not(zip1):
          mongo.db.zipcodes.insert({'zip':result["zipcode"], 'temps':[]})
        return render_template("zip.html", temps = mongo.db.zipcodes.find_one_or_404({"zip":result["zipcode"]}), search = Search())
    return render_template("entry.html", form=form)

@app.route("/add-temp/", methods=["get", "post"])
def add_temp():            
    form = TempForm()
    #this if statement funs when the form is submitted
    if form.submit1.data and form.is_submitted():
        user = mongo.db.users.find_one({'id': session["id"]})
        result = request.form
        zip1 = mongo.db.zipcodes.find_one({'zip': user['zip']})
        result = request.form
        user["temps"][date()].append(result["temp"])
        mongo.db.users.replace_one({"id":session["id"]}, user)
        if zip1:
          zip1["temps"][date()].append(result["temp"])
          mongo.db.zipcodes.replace_one({"zip":zip1['zip']}, zip1)
        else:
          zip1 = {'zip':user['zip'], 'temps':{date():[result["temp"]]}}
          mongo.db.zipcodes.insert(zip1)
        return render_template("zip.html", temps = zip1["temps"], search = Search())
    return render_template("add-temp.html", form = form)
    
@app.route("/my-temp/", methods=["get", "post"])
def mytemp():
  "Renders graps of users tempratures by day."       
  return render_template("mytemps.html",person = mongo.db.users.find_one_or_404({"id":session["id"]}))

@app.route("/zip/<string:zip>", methods=["get", "post"])
def zipcode(zip):
    search = Search()
    if search.is_submitted():
        results = request.form
        return search_results(results["search"])
    if zip == "user":
      zip = mongo.db.users.find_one_or_404({"id":session["id"]})["zip"]
 
    return render_template("zip.html", temps = mongo.db.zipcodes.find_one_or_404({"zip":zip})['temps'], search = search)

@app.route("/map/", methods=["get", "post"])
def map():
  """Basically same as home function"""

  return render_template("map.html", map_data = [])



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
   
          

