from datetime import datetime
from typing import DefaultDict
from flask import Flask, render_template, request, session, redirect, url_for, send_file
import os
import uuid
import hashlib
import psycopg2
from functools import wraps
import time
import utils.utils as utils

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

@app.route("/application")
def application():
    try:
        usertype = session["usertype"]
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
        usertype = session["usertype"]
        if usertype != "medical_provider":
            return redirect("/application")
        username = session["username"]
    except:
        return redirect("/")
    return render_template("providerhome.html", username=username)

@app.route("/manage_provider_profile")
def manage_provider_profile():
    try:
        usertype = session["usertype"]
        if usertype != "medical_provider":
            return redirect("/application")
        username = session["username"]
        id = session["id"]
    except:
        return redirect("/")
    cursor = connection.cursor()
    query = "SELECT address1, address2, city, state, country, zipcode, phone_num from medical_provider where id=%s;"
    cursor.execute(query, (id,))
    data = cursor.fetchone()
    cursor.close()
    if data:
        return render_template("manage_provider_profile.html", username=username, data=data)

@app.route("/update_provider_profile", methods=["POST"])
def update_provider_profile():
    try:
        usertype = session["usertype"]
        if usertype != "medical_provider":
            return redirect("/application")
        id = session["id"]
    except:
        return redirect("/")
    if request.form:
        requestData = request.form
        name = requestData["name"]
        address1 = requestData["address1"]
        address2 = requestData["address2"]
        city = requestData["city"]
        state = requestData["state"]
        country = requestData["country"]
        zipcode = requestData["zipcode"]
        phone_num = requestData["phone_num"]
    else:
        return redirect("/")
    with connection.cursor() as cursor:
        query = "UPDATE medical_provider SET name=%s, address1=%s, address2=%s, city=%s, state=%s, country=%s, zipcode=%s, phone_num=%s where id=%s;"
        cursor.execute(query, (name, address1, address2, city, state, country, zipcode, phone_num, id))
    session["username"] = name
    return redirect("/application")

@app.route("/manage_availability")
def manage_availability():
    try:
        usertype = session["usertype"]
        if usertype != "medical_provider":
            return redirect("/application")
        id = session["id"]
        username = session["username"]
    except:
        return redirect("/")
    cursor = connection.cursor()
    query = "select v.vaccine_name, description, version, available_num, in_progress_num, used_num, wasted_num, a.vaccination_id from availability a join vaccination v on a.vaccination_id = v.id where a.medical_provider_id=%s;"
    cursor.execute(query, (id,))
    data = cursor.fetchall()
    cursor.close()
    return render_template("manage_availability.html", username=username, data=data)

@app.route("/update_availability", methods=["POST"])
def update_availability():
    try:
        usertype = session["usertype"]
        if usertype != "medical_provider":
            return redirect("/application")
        id = session["id"]
    except:
        return redirect("/")
    if request.form:
        requestData = request.form
    else:
        return redirect("/")
    with connection.cursor() as cursor:
        for key in requestData.keys():
            vaccine_id = int(key.split("_")[-1])
            new_availability = requestData[key]
            query = "UPDATE availability SET available_num = %s where medical_provider_id=%s and vaccination_id=%s;"
            cursor.execute(query, (new_availability, id, vaccine_id))
    return redirect("/application")

@app.route("/add_new_availability_page")
def add_new_availability_page():
    try:
        usertype = session["usertype"]
        if usertype != "medical_provider":
            return redirect("/application")
        id = session["id"]
        username = session["username"]
    except:
        return redirect("/")
    cursor = connection.cursor()
    query = """select vaccine_name, description, version, fda_approved, who_listing, clinical_trial, v.id from vaccination v left join
    (select vaccination_id from availability where medical_provider_id = %s) exist
    on v.id = exist.vaccination_id
    where exist.vaccination_id is NULL;"""
    cursor.execute(query, (id,))
    data = cursor.fetchall()
    cursor.close()
    if data:
        print(data)
        return render_template("add_new_availability_page.html", username=username, data=data)
    return render_template("add_new_availability_page.html", username=username)

@app.route("/add_new_availability", methods=["POST"])
def add_new_availability():
    try:
        usertype = session["usertype"]
        if usertype != "medical_provider":
            return redirect("/application")
        id = session["id"]
    except:
        return redirect("/")
    if request.form:
        requestData = request.form
    else:
        return redirect("/")
    with connection.cursor() as cursor:
        for key in requestData.keys():
            vaccine_id = int(key.split("_")[-1])
            new_availability = requestData[key]
            if new_availability != "":
                query = "insert into availability (medical_provider_id, vaccination_id, available_num) values(%s, %s, %s)"
                cursor.execute(query, (id, vaccine_id, new_availability))
    return redirect("/application")

@app.route("/create_vaccination", methods=["POST","GET"])
def create_vaccination():
    try:
        usertype = session["usertype"]
        if usertype != "medical_provider":
            return redirect("/application")
        username = session["username"]
        id = session["id"]
    except:
        return redirect("/")
    if request.method == "POST":
        if request.form:
            requestData = request.form
        else:
            return redirect("/")
        vaccine_name = requestData["vaccine_name"]
        description = requestData["description"]
        version = requestData["version"]
        fda_approved = requestData["fda_approved"]
        who_listing = requestData["who_listing"]
        clinical_trial = requestData["clinical_trial"]
        available_num = requestData["available_num"]
        with connection.cursor() as cursor:
            query = "insert into vaccination (vaccine_name, description, version, fda_approved, who_listing, clinical_trial) values (%s, %s, %s, %s, %s, %s) returning id;"
            cursor.execute(query, (vaccine_name, description, version, fda_approved, who_listing, clinical_trial))
            vaccination_id = cursor.fetchone()[0]
            query = "insert into availability values (%s, %s, %s, 0, 0, 0)"
            cursor.execute(query, (id, vaccination_id, available_num))
        return redirect("/application")
    else:
        return render_template("create_vaccination.html", username=username)

@app.route("/doctorhome")
def doctorhome():
    try:
        usertype = session["usertype"]
        if usertype != "doctor":
            return redirect("/application")
        username = session["username"]
    except:
        return redirect("/")
    return render_template("doctorhome.html", username=username)

@app.route("/manage_doctor_profile", methods=["POST","GET"])
def manage_doctor_profile():
    try:
        usertype = session["usertype"]
        if usertype != "doctor":
            return redirect("/application")
        username = session["username"]
        id = session["id"]
    except:
        return redirect("/")
    if request.method == "GET":
        cursor = connection.cursor()
        query = "SELECT first_name, mid_name, last_name, birthdate, phone_num FROM doctor where id=%s;"
        cursor.execute(query, (id,))
        data = cursor.fetchone()
        if data:
            formated_birthdate = data[3][:4] + "-" + data[3][4:6] + "-" + data[3][6:]
            data = (data[0], data[1], data[2], formated_birthdate, data[4])
        mp_query = """select m.name, m.address1, m.address2, m.city, m.state, m.country, m.zipcode from 
        doctor d join medical_provider m on d.medical_provider_id = m.id 
        where d.id=%s;"""
        cursor.execute(mp_query, (id,))
        mp_data = cursor.fetchone()
        cursor.close()
        return render_template("manage_doctor_profile.html", username=username, data=data, mp_data=mp_data)
    elif request.method == "POST":
        if request.form:
            requestData = request.form
            first_name = requestData["fname"]
            mid_name = requestData["mname"]
            last_name = requestData["lname"]
            bd = requestData["birthday"].replace('-','')
            phone_num = requestData["phone_num"]
            with connection.cursor() as cursor:
                query = "UPDATE doctor SET first_name=%s, mid_name=%s, last_name=%s, birthdate=%s, phone_num=%s WHERE id=%s;"
                cursor.execute(query, (first_name, mid_name, last_name, bd, phone_num, id))
            session["username"] = first_name + " " + last_name
        return redirect("/application")

@app.route("/manage_doctor_provider", methods=["GET","POST"])
def manage_doctor_provider():
    try:
        usertype = session["usertype"]
        if usertype != "doctor":
            return redirect("/application")
        username = session["username"]
        id = session["id"]
    except:
        return redirect("/")
    if request.method == "GET":
        cursor = connection.cursor()
        mp_query = "SELECT name, address1, address2, city, state, country, zipcode, id FROM medical_provider;"
        cursor.execute(mp_query)
        medical_provider_data = cursor.fetchall()
        cursor.close()
        return render_template("manage_doctor_provider.html", username=username, medical_provider_data=medical_provider_data)
    elif request.method == "POST":
        if request.form:
            requestData = request.form
            for key in requestData.keys():
                if requestData[key]=="Select":
                    with connection.cursor() as cursor:
                        query = "UPDATE doctor SET medical_provider_id=%s WHERE id=%s;"
                        cursor.execute(query, (key, id))
                    break
        return redirect("/application")

@app.route("/vaccinetakerhome")
def vaccinetakerhome():
    try:
        usertype = session["usertype"]
        if usertype != "vaccine_taker":
            return redirect("/application")
        username = session["username"]
    except:
        return redirect("/")
    return render_template("vaccinetakerhome.html", username=username)

@app.route("/manage_taker_profile", methods=["POST", "GET"])
def manage_taker_profile():
    try:
        usertype = session["usertype"]
        if usertype != "vaccine_taker":
            return redirect("/application")
        username = session["username"]
        id = session["id"]
    except:
        return redirect("/")
    if request.method == "GET":
        cursor = connection.cursor()
        query = "SELECT first_name, mid_name, last_name, birthdate, phone_num FROM vaccine_taker where id=%s;"
        cursor.execute(query, (id,))
        data = cursor.fetchone()
        if data:
            formated_birthdate = data[3][:4] + "-" + data[3][4:6] + "-" + data[3][6:]
            data = (data[0], data[1], data[2], formated_birthdate, data[4])
        return render_template("manage_taker_profile.html", data=data, username=username)
    elif request.method == "POST":
        if request.form:
            requestData = request.form
            first_name = requestData["fname"]
            mid_name = requestData["mname"]
            last_name = requestData["lname"]
            bd = requestData["birthday"].replace('-','')
            phone_num = requestData["phone_num"]
            with connection.cursor() as cursor:
                query = "UPDATE vaccine_taker SET first_name=%s, mid_name=%s, last_name=%s, birthdate=%s, phone_num=%s WHERE id=%s;"
                cursor.execute(query, (first_name, mid_name, last_name, bd, phone_num, id))
            session["username"] = first_name + " " + last_name
        return redirect("/application")

@app.route("/manage_doctor_time_appointment", methods=["POST","GET"])
def manage_doctor_time_appointment():
    try:
        usertype = session["usertype"]
        if usertype != "doctor":
            return redirect("/application")
        username = session["username"]
        id = session["id"]
    except:
        return redirect("/")
    if request.method == "GET":
        # Show/manage work hours
        cursor = connection.cursor()
        query = "SELECT work_start_time, work_end_time, work_monday, work_tuesday, work_wednesday, work_thursday, work_friday, work_saturday, work_sunday FROM doctor where id=%s;"
        cursor.execute(query, (id,))
        work_time_data = cursor.fetchone()
        # Show upcoming appointments
        cursor = connection.cursor()
        query = "SELECT * FROM doctor where id=%s;"
        cursor.execute(query, (id,))
        appointment_data = cursor.fetchall()
        cursor.close()
        return render_template("manage_doctor_time_appointment.html", username=username, work_time_data=work_time_data, appointment_data=appointment_data)
    elif request.method == "POST":
        if request.form:
            requestData = request.form
            work_start_time = requestData["work_start_time"]
            work_end_time = requestData["work_end_time"]
            work_day_dict = {
                "work_monday":0,
                "work_tuesday":0,
                "work_wednesday":0,
                "work_thursday":0,
                "work_friday":0,
                "work_saturday":0,
                "work_sunday":0
            }
            for key, value in requestData.items():
                if value == "on":
                    work_day_dict[key] = 1
            with connection.cursor() as cursor:
                query = "UPDATE doctor SET work_start_time=%s, work_end_time=%s, work_monday=%s, work_tuesday=%s, work_wednesday=%s, work_thursday=%s, work_friday=%s, work_saturday=%s, work_sunday=%s WHERE id=%s;"
                cursor.execute(query, (work_start_time, work_end_time, work_day_dict["work_monday"], work_day_dict["work_tuesday"], work_day_dict["work_wednesday"], work_day_dict["work_thursday"], work_day_dict["work_friday"], work_day_dict["work_saturday"], work_day_dict["work_sunday"], id))
        return redirect("/manage_doctor_time_appointment")

@app.route("/doctor_fill_time_slot", methods=["POST"])
def doctor_fill_time_slot():
    try:
        usertype = session["usertype"]
        if usertype != "doctor":
            return redirect("/application")
        id = session["id"]
    except:
        return redirect("/")
    if request.form:
            requestData = request.form
            work_start_time = requestData["work_start_time"]
            work_end_time = requestData["work_end_time"]
            work_day_dict = {
                "work_monday":0,
                "work_tuesday":0,
                "work_wednesday":0,
                "work_thursday":0,
                "work_friday":0,
                "work_saturday":0,
                "work_sunday":0
            }
            for key, value in requestData.items():
                if value == "on":
                    work_day_dict[key] = 1
            with connection.cursor() as cursor:
                query = "UPDATE doctor SET work_start_time=%s, work_end_time=%s, work_monday=%s, work_tuesday=%s, work_wednesday=%s, work_thursday=%s, work_friday=%s, work_saturday=%s, work_sunday=%s WHERE id=%s;"
                cursor.execute(query, (work_start_time, work_end_time, work_day_dict["work_monday"], work_day_dict["work_tuesday"], work_day_dict["work_wednesday"], work_day_dict["work_thursday"], work_day_dict["work_friday"], work_day_dict["work_saturday"], work_day_dict["work_sunday"], id))
            
            time_slots = utils.generate_time_slots(work_start_time, work_end_time, work_day_dict)
            for time in time_slots:
                with connection.cursor() as cursor:
                    query = "INSERT INTO time_slot (doctor_id, time) VALUES (%s, %s) ON CONFLICT DO NOTHING"
                    cursor.execute(query, (id, time))
    return redirect("/application")

@app.route("/aptmt_selection")
def aptmt_selection():
    try:
        usertype = session["usertype"]
        if usertype != "vaccine_taker":
            return redirect("/application")
        username = session["username"]
    except:
        return redirect("/")
    params = request.args
    if params.get("aptmt_date") is not None:
        target_date = datetime.today().strftime("%Y-%m-%d")
        if params.get("aptmt_date") != "":
            target_date = params["aptmt_date"]
        formatted_date = target_date.replace("-", "")
        # Get all time slots on target date
        query = """select id, name, address1, city, state, country, zipcode, tmp2.time from medical_provider join(
            select doctor.medical_provider_id, tmp.time from doctor join (
                select doctor_id, time from time_slot where substring(time, 1, 8) = %s and status = 1
            ) tmp on doctor.id = tmp.doctor_id
        ) tmp2 on tmp2.medical_provider_id = medical_provider.id;"""
        cursor = connection.cursor()
        cursor.execute(query, (formatted_date,))
        data = cursor.fetchall()
        cursor.close()
        availabilities = utils.format_apt_selection(data)
        return render_template("aptmt_selection.html", username=username, date=target_date, availabilities=availabilities)
    else:
        return render_template("aptmt_selection.html", username=username)

@app.route("/aptmt_schedule", methods=["GET", "POST"])
def aptmt_schedule():
    try:
        usertype = session["usertype"]
        if usertype != "vaccine_taker":
            return redirect("/application")
        username = session["username"]
        id = session["id"]
    except:
        return redirect("/")
    if request.method == "GET":
        params = request.args
        if params.get("date") is not None and params.get("time") is not None and params.get("id") is not None:
            target_date = params["date"]
            target_time = params["time"]
            formatted_time = target_date.replace("-", "")+target_time.replace(":", "")
            medical_provider_id = params["id"]
            cursor = connection.cursor()
            provider_query = "select id, name from medical_provider where id =%s"
            cursor.execute(provider_query, (medical_provider_id,))
            provider = cursor.fetchone()
            vaccine_query = """
            select vaccination.id, vaccine_name from vaccination join(
                select * from availability where available_num > 0
            ) tmp on vaccination.id = tmp.vaccination_id
            where id = %s;
            """
            cursor.execute(vaccine_query, (medical_provider_id,))
            vaccine_data = cursor.fetchall()
            doctor_query = """
                select doctor.id, first_name, last_name, tmp.time_slot_id from doctor join(
                    select id time_slot_id, doctor_id from time_slot where time = %s and status = 1
                ) tmp on doctor.id = tmp.doctor_id and medical_provider_id = %s;
            """
            cursor.execute(doctor_query, (formatted_time, medical_provider_id))
            doctor_data = cursor.fetchall()
            cursor.close()
            return render_template("aptmt_schedule.html", username=username, vaccine_data=vaccine_data, doctor_data=doctor_data, target_date=target_date, target_time=target_time, provider=provider)
        else:
            return redirect("/application")
    elif request.method == "POST":
        if request.form:
            requestData = request.form
            vaccine_id = int(requestData["vaccine_select"])
            medical_provider_id = int(requestData["medical_provider_id"])
            time_slot_id = int(requestData["time_slot_id"])
            notes = requestData["notes"]
            dose_num = requestData["dose_num"]
            connection.rollback()
            connection.autocommit = False
            try:
                with connection.cursor() as cursor:
                    # Update time_slot status
                    time_slot_query = "update time_slot set status = 2 where id = %s"
                    cursor.execute(time_slot_query, (time_slot_id,))
                    # Insert an appointment and vaccine_result
                    vaccine_result_query = "insert into vaccine_result (success) values (2) returning id;"
                    cursor.execute(vaccine_result_query)
                    vaccine_result_id = cursor.fetchone()[0]
                    appointment_query = """
                    insert into appointment (vaccine_taker_id, time_slot_id, dose_num, vaccine_id, 
                    status, vaccine_taker_note, vaccine_result_id) values (
                    %s, %s, %s, %s, %s, %s, %s);
                    """
                    cursor.execute(appointment_query, (id, time_slot_id, dose_num, vaccine_id, 1, notes, vaccine_result_id))
                    # Update availability
                    availability_query = """
                    update availability set
                    available_num = available_num - 1,
                    in_progress_num = in_progress_num + 1
                    where medical_provider_id = %s and vaccination_id = %s;
                    """
                    cursor.execute(availability_query, (medical_provider_id, vaccine_id))
                    connection.commit()
            except:
                connection.rollback()
            finally:
                connection.autocommit = True
        return redirect("/application")

@app.route("/manage_taker_appointment", methods=["GET", "POST"])
def manage_taker_appointment():
    try:
        usertype = session["usertype"]
        if usertype != "vaccine_taker":
            return redirect("/application")
        username = session["username"]
        id = session["id"]
    except:
        return redirect("/")
    if request.method == "GET":
        cursor = connection.cursor()
        query = """
        select vaccine_name, tmp4.first_name, tmp4.last_name, tmp4.time, tmp4.success, tmp4.dose_num, tmp4.doctor_notes, tmp4.vaccine_taker_note from
            (select first_name, last_name, tmp3.time, tmp3.success, tmp3.dose_num, tmp3.vaccine_id, tmp3.doctor_notes, tmp3.vaccine_taker_note from
                (select doctor_id, time, tmp2.success, tmp2.dose_num, tmp2.vaccine_id, tmp2.doctor_notes, tmp2.vaccine_taker_note from
                    (select success, tmp.time_slot_id, tmp.dose_num, tmp.vaccine_id, tmp.doctor_notes, tmp.vaccine_taker_note from 
                        (select time_slot_id, dose_num, vaccine_id, doctor_notes, vaccine_taker_note, vaccine_result_id
                        from appointment where vaccine_taker_id = %s)
                    tmp join vaccine_result on vaccine_result.id = tmp.vaccine_result_id)
                tmp2 join time_slot on tmp2.time_slot_id = time_slot.id)
            tmp3 join doctor on tmp3.doctor_id = doctor.id)
        tmp4 join vaccination on vaccination.id = tmp4.vaccine_id
        """
        cursor.execute(query, (id, ))
        data = list(cursor.fetchall())
        for i in range(len(data)):
            data[i] = list(data[i])
            data[i][4] = utils.VACCINE_RESULT_STATUS[data[i][4]]
            data[i][3] = utils.format_time(data[i][3])
        return render_template("manage_taker_appointment.html", username=username, data=data)
    return render_template("manage_taker_appointment.html", username=username)

if __name__ == "__main__":
    app.run()