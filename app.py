from flask import Flask, render_template, request, session, redirect, url_for, send_file
import os
import uuid
import hashlib
import psycopg2
from functools import wraps
import time

app = Flask(__name__)
app.secret_key = "super secret key"
IMAGES_DIR = os.path.join(os.getcwd(), "images")

connection = psycopg2.connect(host="localhost",
                             user="postgres",
                             password="1116",
                             database="test")
connection.autocommit = True


@app.route("/")
def index():
    try:
        return render_template("homepage.html",username=session["username"])
    except:
        return render_template("homepage.html")

@app.route("/home")
def home():
    return redirect("/")

@app.route("/loginpage")
def redlogin():
    return render_template("loginpage.html")

@app.route("/medicalregisterpage")
def medicalredregister():
    return render_template("register_medical_provider.html")

@app.route("/loginAuth", methods=["POST"])
def loginAuth():
    if request.form:
        requestData = request.form
        email = requestData["uname"]
        plaintextPasword = requestData["pswrd"]
        hashedPassword = hashlib.sha256(plaintextPasword.encode("utf-8")).hexdigest()
        usertype = requestData["usertype"]
        cursor = connection.cursor()
        query = ""
        if usertype == "vaccine_taker":
            query = "SELECT id, first_name, last_name FROM vaccine_taker WHERE email = %s AND password = %s"
        elif usertype == "doctor":
            query = "SELECT id, first_name, last_name FROM doctor WHERE email = %s AND password = %s"
        elif usertype == "medical_provider":
            query = "SELECT id, name FROM medical_provider WHERE email = %s AND password = %s"
        cursor.execute(query, (email, hashedPassword))
        data = cursor.fetchone()
        if data:
            session["usertype"] = usertype
            session["id"] = data[0]
            if usertype == "medical_provider":
                session["username"] = data[1]
            else:
                session["username"] = data[1]+" "+data[2]
            return redirect(url_for("home"))

        error = "Incorrect username or password."
        return render_template("loginpage.html", error=error)

    error = "An unknown error has occurred. Please try again."
    return render_template("loginpage.html", error=error)


@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html")

@app.route("/registerAuth", methods=["POST"])
def registerAuth():
    if request.form:
        requestData = request.form
        usertype = requestData["usertype"]
        print("Received", usertype)
        if usertype == "patient" or usertype == "doctor":
            plaintextPasword = requestData["password"]
            hashedPassword = hashlib.sha256(plaintextPasword.encode("utf-8")).hexdigest()
            first_name = requestData["fname"]
            mid_name=requestData["mname"]
            last_name = requestData["lname"]
            bd = requestData["birthday"].replace('-','')
            email= requestData["email"]
            phone_num= requestData["phone_num"]
            try:
                with connection.cursor() as cursor:
                    if usertype == "patient":
                        query = "INSERT INTO vaccine_taker (first_name,mid_name,last_name,birthdate,email,phone_num,Password) VALUES (%s, %s, %s, %s,%s, %s, %s)"
                        cursor.execute(query, (first_name,mid_name,last_name,bd,email,phone_num,hashedPassword))
                    elif usertype == "doctor":
                        query = "INSERT INTO doctor (first_name,mid_name,last_name,birthdate,email,phone_num,Password) VALUES (%s, %s, %s, %s,%s, %s, %s)"
                        cursor.execute(query, (first_name,mid_name,last_name,bd,email,phone_num,hashedPassword))
                        
            except psycopg2.IntegrityError:
                error = "%s is already taken." % (email)
                return render_template('register.html', error=error)
        elif usertype == "medical_provider":
            print("Type correct")
            name = requestData["name"]
            address1 = requestData["address1"]
            address2 = requestData["address2"]
            city = requestData["city"]
            state = requestData["state"]
            country = requestData["country"]
            zipcode = requestData["zipcode"]
            email = requestData["email"]
            phone_num = requestData["phone_num"]
            plaintextPasword = requestData["password"]
            hashedPassword = hashlib.sha256(plaintextPasword.encode("utf-8")).hexdigest()
            try:
                with connection.cursor() as cursor:
                    print("Before query")
                    query = "INSERT INTO medical_provider (name, password, address1, address2, city, state, country, zipcode, email, phone_num) VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s, %s)"
                    cursor.execute(query, (name, hashedPassword, address1, address2, city, state, country, zipcode, email, phone_num))
                    print("Query Success")
            except psycopg2.IntegrityError:
                print("Exception")
                error = "%s is already taken." % (email)
                return render_template('register.html', error=error)
        return redirect("/loginpage")

    error = "An error has occurred. Please try again."
    return render_template("register.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run()