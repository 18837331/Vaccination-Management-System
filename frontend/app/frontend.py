from datetime import datetime
from typing import DefaultDict
from flask import Flask, render_template, request, session, redirect, url_for, send_file
import os
import uuid
import hashlib
from flask.helpers import make_response
import psycopg2
from functools import wraps
import time
import utils.utils as utils
import requests

app = Flask(__name__)
app.secret_key = "super secret key"
IMAGES_DIR = os.path.join(os.getcwd(), "images")

BACKEND_URL = "http://"+os.getenv('BACKEND_HOST')+":5001"


@app.route("/")
def index():
    try:
        return render_template("homepage.html",username=request.cookies["username"])
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
        requestData = dict(request.form)
        hashedPassword = hashlib.sha256(requestData["pswrd"].encode("utf-8")).hexdigest()
        requestData["hashedpassword"] = hashedPassword
        result = requests.post(BACKEND_URL+"/loginAuth", data=requestData).json()
        if result["result"]:
            usertype = result["usertype"]
            username = result["username"]
            id = str(result["id"])
            response = make_response(redirect(url_for("home")))
            response.set_cookie("usertype", usertype)
            response.set_cookie("username", username)
            response.set_cookie("id", id)
            return response
    return redirect("/loginpage")


@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html")

@app.route("/registerAuth", methods=["POST"])
def registerAuth():
    if request.form:
        requestData = dict(request.form)
        plaintextPasword = requestData["password"]
        hashedPassword = hashlib.sha256(plaintextPasword.encode("utf-8")).hexdigest()
        requestData["password"] = hashedPassword
        requests.post(BACKEND_URL+"/registerAuth", data=requestData)
        return redirect("/loginpage")
    return redirect("/register")

@app.route("/logout")
def logout():
    response = make_response(redirect("/"))
    response.set_cookie('id', '', expires=0)
    response.set_cookie('username', '', expires=0)
    response.set_cookie('usertype', '', expires=0)
    return response

@app.route("/application")
def application():
    try:
        usertype = request.cookies.get("usertype")
    except:
        return redirect("/")
    if usertype == "vaccine_taker":
        return redirect("/vaccinetakerhome")
    elif usertype == "doctor":
        return redirect("/doctorhome")
    elif usertype == "medical_provider":
        return redirect("/providerhome")

@app.route("/providerhome")
def provider_home():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "medical_provider":
            return redirect("/application")
        username = request.cookies.get("username")
    except:
        return redirect("/")
    return render_template("providerhome.html", username=username)

@app.route("/manage_provider_profile")
def manage_provider_profile():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "medical_provider":
            return redirect("/application")
        username = request.cookies.get("username")
        id = int(request.cookies.get("id"))
    except:
        return redirect("/")
    requestData = {}
    requestData["id"] = id
    result = requests.get(BACKEND_URL+"/manage_provider_profile/%d"%id).json()
    if result["result"]:
        return render_template("manage_provider_profile.html", username=username, data=result["data"])
    return redirect("/application")

@app.route("/update_provider_profile", methods=["POST"])
def update_provider_profile():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "medical_provider":
            return redirect("/application")
        id = int(request.cookies.get("id"))
    except:
        return redirect("/")
    if request.form:
        requestData = dict(request.form)
        requestData["id"] = id
    else:
        return redirect("/")
    result = requests.post(BACKEND_URL+"/update_provider_profile", data=requestData).json()
    if result["result"]:
        response = make_response(redirect("/application"))
        response.set_cookie('username', result["name"])
        return response
    return redirect("/application")

@app.route("/manage_availability")
def manage_availability():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "medical_provider":
            return redirect("/application")
        id = int(request.cookies.get("id"))
        username = request.cookies.get("username")
    except:
        return redirect("/")
    requestData = {}
    requestData["id"] = id
    result = requests.get(BACKEND_URL+"/manage_availability/%d"%id).json()
    if result["result"]:
        return render_template("manage_availability.html", username=username, data=result["data"])
    return redirect("/application")

@app.route("/update_availability", methods=["POST"])
def update_availability():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "medical_provider":
            return redirect("/application")
        id = int(request.cookies.get("id"))
    except:
        return redirect("/")
    if request.form:
        requestData = request.form
    else:
        return redirect("/")
    if request.form:
        requestData = dict(request.form)
        requestData["id"] = id
        requests.post(BACKEND_URL+"/update_availability", data=requestData).json()
    return redirect("/application")

@app.route("/add_new_availability_page")
def add_new_availability_page():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "medical_provider":
            return redirect("/application")
        id = int(request.cookies.get("id"))
        username = request.cookies.get("username")
    except:
        return redirect("/")
    result = requests.get(BACKEND_URL+"/add_new_availability_page/%d"%id).json()
    if result["result"]:
        data = result["data"]
        return render_template("add_new_availability_page.html", username=username, data=data)
    return render_template("add_new_availability_page.html", username=username)

@app.route("/add_new_availability", methods=["POST"])
def add_new_availability():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "medical_provider":
            return redirect("/application")
        id = int(request.cookies.get("id"))
    except:
        return redirect("/")
    if request.form:
        requestData = dict(request.form)
    else:
        return redirect("/")
    if request.form:
        requestData = dict(request.form)
        requests.post(BACKEND_URL+"/add_new_availability/%d"%id, data=requestData).json()
    return redirect("/application")

@app.route("/create_vaccination", methods=["POST","GET"])
def create_vaccination():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "medical_provider":
            return redirect("/application")
        username = request.cookies.get("username")
        id = int(request.cookies.get("id"))
    except:
        return redirect("/")
    if request.method == "POST":
        if request.form:
            requestData = dict(request.form)
            requestData["id"] = id
            requests.post(BACKEND_URL+"/create_vaccination", data=requestData).json()
        return redirect("/application")
    else:
        return render_template("create_vaccination.html", username=username)

@app.route("/doctorhome")
def doctorhome():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "doctor":
            return redirect("/application")
        username = request.cookies.get("username")
    except:
        return redirect("/")
    return render_template("doctorhome.html", username=username)

@app.route("/manage_doctor_profile", methods=["POST","GET"])
def manage_doctor_profile():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "doctor":
            return redirect("/application")
        username = request.cookies.get("username")
        id = int(request.cookies.get("id"))
    except:
        return redirect("/")
    if request.method == "GET":
        result = requests.get(BACKEND_URL+"/manage_doctor_profile/%d"%id).json()
        if result["result"]:
            data = result["data"]
            mp_data = result["mp_data"]
            return render_template("manage_doctor_profile.html", username=username, data=data, mp_data=mp_data)
    elif request.method == "POST":
        if request.form:
            requestData = dict(request.form)
            result = requests.post(BACKEND_URL+"/manage_doctor_profile/%d"%id, data=requestData).json()
            if result["result"]:
                username = result["username"]
                response = make_response(redirect("/application"))
                response.set_cookie("username", username)
                return response
        return redirect("/application")

@app.route("/manage_doctor_provider", methods=["GET","POST"])
def manage_doctor_provider():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "doctor":
            return redirect("/application")
        username = request.cookies.get("username")
        id = int(request.cookies.get("id"))
    except:
        return redirect("/")
    if request.method == "GET":
        result = requests.get(BACKEND_URL+"/manage_doctor_provider/%d"%id).json()
        if result["result"]:
            medical_provider_data = result["medical_provider_data"]
            return render_template("manage_doctor_provider.html", username=username, medical_provider_data=medical_provider_data)
        return redirect("/application")
    elif request.method == "POST":
        if request.form:
            requestData = dict(request.form)
            requests.post(BACKEND_URL+"/manage_doctor_provider/%d"%id, data=requestData).json()
        return redirect("/application")

@app.route("/vaccinetakerhome")
def vaccinetakerhome():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "vaccine_taker":
            return redirect("/application")
        username = request.cookies.get("username")
    except:
        return redirect("/")
    return render_template("vaccinetakerhome.html", username=username)

@app.route("/manage_taker_profile", methods=["POST", "GET"])
def manage_taker_profile():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "vaccine_taker":
            return redirect("/application")
        username = request.cookies.get("username")
        id = int(request.cookies.get("id"))
    except:
        return redirect("/")
    if request.method == "GET":
        result = requests.get(BACKEND_URL+"/manage_taker_profile/%d"%id).json()
        if result["result"]:
            data = result["data"]
            return render_template("manage_taker_profile.html", data=data, username=username)
        return redirect("/application")
    elif request.method == "POST":
        if request.form:
            requestData = dict(request.form)
            result = requests.post(BACKEND_URL+"/manage_taker_profile/%d"%id, data=requestData).json()
            if result["result"]:
                username = result["username"]
                response = make_response(redirect("/application"))
                response.set_cookie("username", username)
                return response
        return redirect("/application")

@app.route("/manage_doctor_time_appointment", methods=["POST","GET"])
def manage_doctor_time_appointment():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "doctor":
            return redirect("/application")
        username = request.cookies.get("username")
        id = int(request.cookies.get("id"))
    except:
        return redirect("/")
    if request.method == "GET":
        result = requests.get(BACKEND_URL+"/manage_doctor_time_appointment/%d"%id).json()
        if result["result"]:
            work_time_data = result["work_time_data"]
            appointment_data = result["appointment_data"]
            return render_template("manage_doctor_time_appointment.html", username=username, work_time_data=work_time_data, appointment_data=appointment_data)
    elif request.method == "POST":
        if request.form:
            requestData = dict(request.form)
            requests.post(BACKEND_URL+"/manage_doctor_time_appointment/%d"%id, data=requestData).json()
        return redirect("/manage_doctor_time_appointment")

@app.route("/doctor_fill_time_slot", methods=["POST"])
def doctor_fill_time_slot():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "doctor":
            return redirect("/application")
        id = int(request.cookies.get("id"))
    except:
        return redirect("/")
    if request.form:
        requestData = dict(request.form)
        requests.post(BACKEND_URL+"/doctor_fill_time_slot/%d"%id, data=requestData)
        return redirect("/manage_doctor_time_appointment")
    return redirect("/application")

@app.route("/aptmt_selection")
def aptmt_selection():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "vaccine_taker":
            return redirect("/application")
        username = request.cookies.get("username")
    except:
        return redirect("/")
    params = request.args
    if params.get("aptmt_date") is not None:
        target_date = datetime.today().strftime("%Y-%m-%d")
        if params.get("aptmt_date") != "":
            target_date = params["aptmt_date"]
            formatted_date = target_date.replace("-", "")
            # Get all time slots on target date
            result = requests.get(BACKEND_URL+"/aptmt_selection/%s"%formatted_date).json()
            if result["result"]:
                availabilities = result["availabilities"]
            return render_template("aptmt_selection.html", username=username, date=target_date, availabilities=availabilities)
    return render_template("aptmt_selection.html", username=username)

@app.route("/aptmt_schedule", methods=["GET", "POST"])
def aptmt_schedule():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "vaccine_taker":
            return redirect("/application")
        username = request.cookies.get("username")
        id = int(request.cookies.get("id"))
    except:
        return redirect("/")
    if request.method == "GET":
        params = request.args
        if params.get("date") is not None and params.get("time") is not None and params.get("id") is not None:
            target_date = params["date"]
            target_time = params["time"]
            formatted_time = target_date.replace("-", "")+target_time.replace(":", "")
            medical_provider_id = int(params["id"])
            result = requests.get(BACKEND_URL+"/aptmt_schedule/%d?medical_provider_id=%d&formatted_time=%s"%(id,medical_provider_id,formatted_time)).json()
            if result["result"]:
                doctor_data = result["doctor_data"]
                vaccine_data = result["vaccine_data"]
                provider = result["provider"]
                return render_template("aptmt_schedule.html", username=username, vaccine_data=vaccine_data, doctor_data=doctor_data, target_date=target_date, target_time=target_time, provider=provider)
        return redirect("/application")
    elif request.method == "POST":
        if request.form:
            requestData = request.form
            requests.post(BACKEND_URL+"/aptmt_schedule/%d"%id, data=requestData)
        return redirect("/application")

@app.route("/manage_taker_appointment", methods=["GET"])
def manage_taker_appointment():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "vaccine_taker":
            return redirect("/application")
        username = request.cookies.get("username")
        id = int(request.cookies.get("id"))
    except:
        return redirect("/")
    if request.method == "GET":
        result = requests.get(BACKEND_URL+"/manage_taker_appointment/%d"%id).json()
        if result["result"]:
            data = result["data"]
        return render_template("manage_taker_appointment.html", username=username, data=data)
    return render_template("manage_taker_appointment.html", username=username)

@app.route("/vaccine_pass", methods=["get"])
def vaccine_pass():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "vaccine_taker":
            return redirect("/application")
        username = request.cookies.get("username")
        id = int(request.cookies.get("id"))
    except:
        return redirect("/")
    result = requests.get(BACKEND_URL+"/vaccine_pass/%d"%id).json()
    if result["result"]:
        data = result["data"]
        if result["found"]:
            return render_template("vaccine_pass.html", username=username, data=data)
        else:
            return render_template("vaccine_not_pass.html", username=username,data=data)
    return redirect("/application")

@app.route("/appointment_success")
def appointment_success():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "doctor":
            return redirect("/application")
        id = int(request.cookies.get("id"))
    except:
        return redirect("/")
    params = request.args
    if params.get("id") is not None and params.get("id") != "":
        appointment_id = int(params["id"])
        requests.get(BACKEND_URL+"/appointment_success/%d?appointment_id=%d"%(id,appointment_id))
    return redirect("/application")

@app.route("/appointment_failed")
def appointment_failed():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "doctor":
            return redirect("/application")
        id = int(request.cookies.get("id"))
    except:
        return redirect("/")
    params = request.args
    if params.get("id") is not None and params.get("id") != "":
        appointment_id = int(params["id"])
        requests.get(BACKEND_URL+"/appointment_failed/%d?appointment_id=%d"%(id,appointment_id))
    return redirect("/application")

@app.route("/appointment_cancel_doctor")
def appointment_cancel_doctor():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "doctor":
            return redirect("/application")
        id = int(request.cookies.get("id"))
    except:
        return redirect("/")
    params = request.args
    if params.get("id") is not None and params.get("id") != "":
        appointment_id = int(params["id"])
        requests.get(BACKEND_URL+"/appointment_cancel_doctor/%d?appointment_id=%d"%(id,appointment_id))
    return redirect("/application")

@app.route("/appointment_remove_taker")
def appointment_cancel_taker():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "vaccine_taker":
            return redirect("/application")
        id = int(request.cookies.get("id"))
    except:
        return redirect("/")
    params = request.args
    if params.get("id") is not None and params.get("id") != "":
        appointment_id = int(params["id"])
        requests.get(BACKEND_URL+"/appointment_cancel_taker/%d?appointment_id=%d"%(id,appointment_id))
    return redirect("/application")

@app.route("/taker_chat_selection")
def taker_chat_selection():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "vaccine_taker":
            return redirect("/application")
        id = int(request.cookies.get("id"))
        username = request.cookies.get("username")
    except:
        return redirect("/")
    result = requests.get(BACKEND_URL+"/taker_chat_selection/%d"%id).json()
    if result["result"]:
        data = result["data"]
        return render_template("taker_chat_selection.html", username=username, data=data)
    return redirect("/application")

@app.route("/general_chat_taker", methods=["GET","POST"])
def general_chat_taker():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "vaccine_taker":
            return redirect("/application")
        id = int(request.cookies.get("id"))
        username = request.cookies.get("username")
    except:
        return redirect("/")
    if request.method == "GET":
        params = request.args
        if params["doctor_id"] is None or params["doctor_id"] == "":
            return redirect("/taker_chat_selection")
        result = requests.get(BACKEND_URL+"/general_chat_taker/%d"%id, params=request.args).json()
        if result["result"]:
            messages = result["messages"]
            return render_template("general_chat_taker.html", username=username, id=id, messages=messages)
        return redirect("/application")
    elif request.method == "POST":
        if request.form:
            requestData = request.form
            doctor_id = int(requestData["doctor_id"])
            result = requests.post(BACKEND_URL+"/general_chat_taker/%d"%id, data=requestData).json()
            if result["result"]:
                return redirect(url_for("general_chat_taker", doctor_id=doctor_id))
        return redirect("/application")
            
        

@app.route("/doctor_chat_selection")
def doctor_chat_selection():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "doctor":
            return redirect("/application")
        id = int(request.cookies.get("id"))
        username = request.cookies.get("username")
    except:
        return redirect("/")
    result = requests.get(BACKEND_URL+"/doctor_chat_selection/%d"%id).json()
    if result["result"]:
        data = result["data"]
        return render_template("doctor_chat_selection.html", username=username, data=data)
    return redirect("/application")

@app.route("/general_chat_doctor", methods=["GET","POST"])
def general_chat_doctor():
    try:
        usertype = request.cookies.get("usertype")
        if usertype != "doctor":
            return redirect("/application")
        id = int(request.cookies.get("id"))
        username = request.cookies.get("username")
    except:
        return redirect("/")
    if request.method == "GET":
        params = request.args
        if params["vaccine_taker_id"] is None or params["vaccine_taker_id"] == "":
            return redirect("/doctor_chat_selection")
        result = requests.get(BACKEND_URL+"/general_chat_doctor/%d"%id, params=params).json()
        if result["result"]:
            messages = result["messages"]
            return render_template("general_chat_doctor.html", username=username, id=id, messages=messages)
        return redirect("/application")
        
    elif request.method == "POST":
        if request.form:
            requestData = request.form
            vaccine_taker_id = int(requestData["vaccine_taker_id"])
            result = requests.post(BACKEND_URL+"/general_chat_doctor/%d"%id, data=requestData).json()
            if result["result"]:
                return redirect(url_for("general_chat_doctor", vaccine_taker_id=vaccine_taker_id))
        return redirect("/application")

if __name__ == "__main__":
    app.run(host="0.0.0.0",port="5000")