from flask import Flask, render_template, request, session, redirect, url_for, send_file
import os
import uuid
import hashlib
import pymysql
from functools import wraps
import time

app = Flask(__name__)
app.secret_key = "super secret key"
IMAGES_DIR = os.path.join(os.getcwd(), "images")

connection = pymysql.connect(host="localhost",
                             user="root",
                             password="root",
                             db="vacc",
                             charset="utf8mb4",
                             port=3306,
                             cursorclass=pymysql.cursors.DictCursor,
                             autocommit=True)


@app.route("/")
def index():
    return render_template("homepage.html")

@app.route("/home")
def home():
    return redirect("/")

@app.route("/loginpage")
def redlogin():
    return render_template("loginpage.html")


@app.route("/registerpage")
def redlogin():
    return render_template("registerpage.html")




@app.route("/loginAuth", methods=["POST"])
def loginAuth():
    if request.form:
        requestData = request.form
        email = requestData["uname"]
        plaintextPasword = requestData["pswrd"]
        hashedPassword = hashlib.sha256(plaintextPasword.encode("utf-8")).hexdigest()

        with connection.cursor() as cursor:
            query = "SELECT * FROM vaccine_taker WHERE eamil = %s AND password = %s"
            cursor.execute(query, (email, hashedPassword))
        data = cursor.fetchone()
        if data:
            session["username"] = email
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
        plaintextPasword = requestData["password"]
        hashedPassword = hashlib.sha256(plaintextPasword.encode("utf-8")).hexdigest()
        first_name = requestData["fname"]
        mid_name=requestData["mname"]
        last_name = requestData["lname"]
        birthdate= requestData["birthdate"]
        email= requestData["email"]
        phone_num= requestData["phone_num"]
        try:
            with connection.cursor() as cursor:
                query = "INSERT INTO vaccine_taker (first_name,mid_name,last_name,birthdate,email,phone_num,Password) VALUES (%s, %s, %s, %s,%s, %s, %s)"
                cursor.execute(query, (first_name,mid_name,last_name,birthdate,email,phone_num,hashedPassword))
        except pymysql.err.IntegrityError:
            error = "%s is already taken." % (email)
            return render_template('register.html', error=error)

        return redirect(url_for("login"))

    error = "An error has occurred. Please try again."
    return render_template("register.html", error=error)




if __name__ == "__main__":
    app.run()