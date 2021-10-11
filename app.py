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
        username = requestData["uname"]
        plaintextPasword = requestData["pswrd"]
        hashedPassword = hashlib.sha256(plaintextPasword.encode("utf-8")).hexdigest()

        with connection.cursor() as cursor:
            query = "SELECT * FROM person WHERE username = %s AND password = %s"
            cursor.execute(query, (username, hashedPassword))
        data = cursor.fetchone()
        if data:
            session["username"] = username
            return redirect(url_for("home"))

        error = "Incorrect username or password."
        return render_template("loginpage.html", error=error)

    error = "An unknown error has occurred. Please try again."
    return render_template("loginpage.html", error=error)



if __name__ == "__main__":
    app.run()