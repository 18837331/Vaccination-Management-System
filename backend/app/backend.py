from datetime import datetime
from typing import DefaultDict, SupportsAbs
from flask import Flask, json, render_template, request, session, redirect, url_for, send_file, jsonify
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
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')

SUCCESS = {"result":True}
FAILURE = {"result":False}

@app.route("/loginAuth", methods=["POST"])
def loginAuth():
    # print(vars(request))
    if request.form:
        requestData = request.form
        usertype = requestData["usertype"]
        hashedPassword = requestData["hashedpassword"]
        email = requestData["uname"]
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
            username = ""
            id = data[0]
            if usertype == "medical_provider":
                username = data[1]
            else:
                username = data[1]+" "+data[2]
            result = SUCCESS.copy()
            result.update({"username":username,"usertype":usertype,"id":id})
            return jsonify(result)
        return jsonify(FAILURE)
    return jsonify(FAILURE)

@app.route("/registerAuth", methods=["POST"])
def registerAuth():
    requestData = dict(request.form)
    usertype = requestData["usertype"]
    if usertype == "patient" or usertype == "doctor":
        first_name = requestData["fname"]
        mid_name=requestData["mname"]
        last_name = requestData["lname"]
        bd = requestData["birthday"].replace('-','')
        email= requestData["email"]
        phone_num= requestData["phone_num"]
        hashedPassword = requestData["password"]
        try:
            with connection.cursor() as cursor:
                if usertype == "patient":
                    query = "INSERT INTO vaccine_taker (first_name,mid_name,last_name,birthdate,email,phone_num,Password) VALUES (%s, %s, %s, %s,%s, %s, %s)"
                    cursor.execute(query, (first_name,mid_name,last_name,bd,email,phone_num,hashedPassword))
                elif usertype == "doctor":
                    query = "INSERT INTO doctor (first_name,mid_name,last_name,birthdate,email,phone_num,Password) VALUES (%s, %s, %s, %s,%s, %s, %s)"
                    cursor.execute(query, (first_name,mid_name,last_name,bd,email,phone_num,hashedPassword))
            return jsonify(SUCCESS)
        except:
            return jsonify(FAILURE)
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
        hashedPassword = requestData["password"]
        try:
            with connection.cursor() as cursor:
                query = "INSERT INTO medical_provider (name, password, address1, address2, city, state, country, zipcode, email, phone_num) VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s, %s)"
                cursor.execute(query, (name, hashedPassword, address1, address2, city, state, country, zipcode, email, phone_num))
            return jsonify(SUCCESS)
        except:
            return jsonify(FAILURE)

@app.route("/manage_provider_profile/<int:id>")
def manage_provider_profile(id):
    try:
        cursor = connection.cursor()
        query = "SELECT address1, address2, city, state, country, zipcode, phone_num from medical_provider where id=%s;"
        cursor.execute(query, (id,))
        data = cursor.fetchone()
        cursor.close()
        if data:
            result = SUCCESS.copy()
            result.update({"data":data})
            return jsonify(result)
    except:
        return jsonify(FAILURE)

@app.route("/update_provider_profile", methods=["POST"])
def update_provider_profile():
    try:
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
            id = requestData["id"]
        else:
            return redirect("/")
        with connection.cursor() as cursor:
            query = "UPDATE medical_provider SET name=%s, address1=%s, address2=%s, city=%s, state=%s, country=%s, zipcode=%s, phone_num=%s where id=%s;"
            cursor.execute(query, (name, address1, address2, city, state, country, zipcode, phone_num, id))
        result = SUCCESS.copy()
        result.update({"name":name})
        return jsonify(result)
    except:
        return jsonify(FAILURE)

@app.route("/manage_availability/<int:id>")
def manage_availability(id):
    try:
        cursor = connection.cursor()
        query = "select v.vaccine_name, description, version, available_num, in_progress_num, used_num, wasted_num, a.vaccination_id from availability a join vaccination v on a.vaccination_id = v.id where a.medical_provider_id=%s;"
        cursor.execute(query, (id,))
        data = cursor.fetchall()
        cursor.close()
        result = SUCCESS.copy()
        result.update({"data":data})
        return jsonify(result)
    except:
        return jsonify(FAILURE)

@app.route("/update_availability", methods=["POST"])
def update_availability():
    if request.form:
        requestData = request.form
        id = requestData["id"]
        with connection.cursor() as cursor:
            for key in requestData.keys():
                vaccine_id = int(key.split("_")[-1])
                new_availability = requestData[key]
                query = "UPDATE availability SET available_num = %s where medical_provider_id=%s and vaccination_id=%s;"
                cursor.execute(query, (new_availability, id, vaccine_id))
                return jsonify(SUCCESS)
    return jsonify(FAILURE)

@app.route("/add_new_availability_page/<int:id>")
def add_new_availability_page(id):
    cursor = connection.cursor()
    query = """select vaccine_name, description, version, fda_approved, who_listing, clinical_trial, v.id from vaccination v left join
    (select vaccination_id from availability where medical_provider_id = %s) exist
    on v.id = exist.vaccination_id
    where exist.vaccination_id is NULL;"""
    cursor.execute(query, (id,))
    data = cursor.fetchall()
    cursor.close()
    if data:
        result = SUCCESS.copy()
        result.update({"data":data})
        return jsonify(result)
    return jsonify(FAILURE)

@app.route("/add_new_availability/<int:id>", methods=["POST"])
def add_new_availability(id=-1):
    if request.form:
        requestData = request.form
        with connection.cursor() as cursor:
            for key in requestData.keys():
                vaccine_id = int(key.split("_")[-1])
                new_availability = requestData[key]
                if new_availability != "":
                    query = "insert into availability (medical_provider_id, vaccination_id, available_num) values(%s, %s, %s)"
                    cursor.execute(query, (id, vaccine_id, new_availability))
        return jsonify(SUCCESS)
    return jsonify(FAILURE)

@app.route("/create_vaccination", methods=["POST"])
def create_vaccination():
    if request.form:
        requestData = request.form
        vaccine_name = requestData["vaccine_name"]
        description = requestData["description"]
        version = requestData["version"]
        fda_approved = requestData["fda_approved"]
        who_listing = requestData["who_listing"]
        clinical_trial = requestData["clinical_trial"]
        available_num = requestData["available_num"]
        id = requestData["id"]
        with connection.cursor() as cursor:
            query = "insert into vaccination (vaccine_name, description, version, fda_approved, who_listing, clinical_trial) values (%s, %s, %s, %s, %s, %s) returning id;"
            cursor.execute(query, (vaccine_name, description, version, fda_approved, who_listing, clinical_trial))
            vaccination_id = cursor.fetchone()[0]
            query = "insert into availability values (%s, %s, %s, 0, 0, 0)"
            cursor.execute(query, (id, vaccination_id, available_num))
        return jsonify(SUCCESS)
    return jsonify(FAILURE)

@app.route("/manage_doctor_profile/<int:id>", methods=["POST","GET"])
def manage_doctor_profile(id=-1):
    if request.method == "GET":
        cursor = connection.cursor()
        query = "SELECT first_name, mid_name, last_name, birthdate, phone_num FROM doctor where id=%s;"
        cursor.execute(query, (id,))
        data = cursor.fetchone()
        mp_query = """select m.name, m.address1, m.address2, m.city, m.state, m.country, m.zipcode from 
        doctor d join medical_provider m on d.medical_provider_id = m.id 
        where d.id=%s;"""
        cursor.execute(mp_query, (id,))
        mp_data = cursor.fetchone()
        cursor.close()
        if data:
            formated_birthdate = data[3][:4] + "-" + data[3][4:6] + "-" + data[3][6:]
            data = (data[0], data[1], data[2], formated_birthdate, data[4])
            result = SUCCESS.copy()
            result.update({"mp_data":mp_data,"data":data})
            return jsonify(result)
        return jsonify(FAILURE)
        
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
            result = SUCCESS.copy()
            result.update({"username":first_name+" "+last_name})
            return jsonify(result)
        return jsonify(FAILURE)

@app.route("/manage_doctor_provider/<int:id>", methods=["GET","POST"])
def manage_doctor_provider(id=-1):
    if request.method == "GET":
        cursor = connection.cursor()
        mp_query = "SELECT name, address1, address2, city, state, country, zipcode, id FROM medical_provider;"
        cursor.execute(mp_query)
        medical_provider_data = cursor.fetchall()
        cursor.close()
        if medical_provider_data:
            result = SUCCESS.copy()
            result.update({"medical_provider_data":medical_provider_data})
            return jsonify(result)
        return jsonify(FAILURE)
    elif request.method == "POST":
        if request.form:
            requestData = request.form
            for key in requestData.keys():
                if requestData[key]=="Select":
                    with connection.cursor() as cursor:
                        query = "UPDATE doctor SET medical_provider_id=%s WHERE id=%s;"
                        cursor.execute(query, (key, id))
                    break
            return jsonify(SUCCESS)
        return jsonify(FAILURE)

@app.route("/manage_taker_profile/<int:id>", methods=["POST", "GET"])
def manage_taker_profile(id=-1):
    if request.method == "GET":
        cursor = connection.cursor()
        query = "SELECT first_name, mid_name, last_name, birthdate, phone_num FROM vaccine_taker where id=%s;"
        cursor.execute(query, (id,))
        data = cursor.fetchone()
        if data:
            formated_birthdate = data[3][:4] + "-" + data[3][4:6] + "-" + data[3][6:]
            data = (data[0], data[1], data[2], formated_birthdate, data[4])
            result = SUCCESS.copy()
            result.update({"data":data})
            return jsonify(result)
        return jsonify(FAILURE)

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
            result = SUCCESS.copy()
            result.update({"username":first_name+" "+last_name})
            return jsonify(result)
        return jsonify(FAILURE)

@app.route("/manage_doctor_time_appointment/<int:id>", methods=["POST","GET"])
def manage_doctor_time_appointment(id=-1):
    if request.method == "GET":
        try:
            # Show/manage work hours
            cursor = connection.cursor()
            query = "SELECT work_start_time, work_end_time, work_monday, work_tuesday, work_wednesday, work_thursday, work_friday, work_saturday, work_sunday FROM doctor where id=%s;"
            cursor.execute(query, (id,))
            work_time_data = cursor.fetchone()
            # Show upcoming appointments
            cursor = connection.cursor()
            query = """
            select vaccine_name, first_name, last_name, time, success, dose_num, doctor_notes, vaccine_taker_note, appointment_id from
                (select first_name, last_name, success, time, dose_num, vaccine_id, doctor_notes, vaccine_taker_note, appointment_id from
                    (select success, time, dose_num, vaccine_taker_id, vaccine_id, doctor_notes, vaccine_taker_note, appointment_id from
                        (select time, dose_num, vaccine_taker_id, vaccine_id, doctor_notes, vaccine_taker_note, vaccine_result_id, appointment.id appointment_id
                        from appointment join time_slot on appointment.time_slot_id = time_slot.id where time_slot.doctor_id=%s)
                    tmp join vaccine_result on vaccine_result.id = tmp.vaccine_result_id)
                tmp2 join vaccine_taker on tmp2.vaccine_taker_id = vaccine_taker.id)
            tmp3 join vaccination on vaccination.id = tmp3.vaccine_id
            """
            cursor.execute(query, (id,))
            appointment_data = list(cursor.fetchall())
            for i in range(len(appointment_data)):
                appointment_data[i] = list(appointment_data[i])
                appointment_data[i][4] = utils.VACCINE_RESULT_STATUS[appointment_data[i][4]]
                appointment_data[i][3] = utils.format_time(appointment_data[i][3])
            cursor.close()
            result = SUCCESS.copy()
            result.update({"work_time_data":work_time_data,"appointment_data":appointment_data})
            return jsonify(result)
        except:
            return jsonify(FAILURE)
    else:
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
            return jsonify(SUCCESS)
        return jsonify(FAILURE)

@app.route("/doctor_fill_time_slot/<int:id>", methods=["POST"])
def doctor_fill_time_slot(id=-1):
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
        return jsonify(SUCCESS)
    return jsonify(FAILURE)

@app.route("/aptmt_selection/<formatted_date>")
def aptmt_selection(formatted_date):
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
    result = SUCCESS.copy()
    result.update({"availabilities":availabilities})
    return jsonify(result)

@app.route("/aptmt_schedule/<int:id>", methods=["GET", "POST"])
def aptmt_schedule(id=-1):
    if request.method == "GET":
        params = request.args
        medical_provider_id = int(params["medical_provider_id"])
        formatted_time = params["formatted_time"]
        try:
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
            result = SUCCESS.copy()
            result.update({"vaccine_data":vaccine_data,"provider":provider,"doctor_data":doctor_data})
            return jsonify(result)
        except:
            return jsonify(FAILURE)
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
                    cursor.execute(appointment_query, (id, time_slot_id, dose_num, vaccine_id, 2, notes, vaccine_result_id))
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
        return jsonify(SUCCESS)

@app.route("/manage_taker_appointment/<int:id>", methods=["GET"])
def manage_taker_appointment(id=-1):
    if request.method == "GET":
        try:
            cursor = connection.cursor()
            query = """
            select vaccine_name, tmp4.first_name, tmp4.last_name, tmp4.time, tmp4.success, tmp4.dose_num, tmp4.doctor_notes, tmp4.vaccine_taker_note, appointment_id from
                (select first_name, last_name, tmp3.time, tmp3.success, tmp3.dose_num, tmp3.vaccine_id, tmp3.doctor_notes, tmp3.vaccine_taker_note, appointment_id from
                    (select doctor_id, time, tmp2.success, tmp2.dose_num, tmp2.vaccine_id, tmp2.doctor_notes, tmp2.vaccine_taker_note, appointment_id from
                        (select success, tmp.time_slot_id, tmp.dose_num, tmp.vaccine_id, tmp.doctor_notes, tmp.vaccine_taker_note, appointment_id from 
                            (select time_slot_id, dose_num, vaccine_id, doctor_notes, vaccine_taker_note, vaccine_result_id, appointment.id appointment_id
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
            result = SUCCESS.copy()
            result.update({"data":data})
            return jsonify(result)
        except:
            return jsonify(FAILURE)
    return jsonify(FAILURE)

@app.route("/vaccine_pass/<int:id>", methods=["get"])
def vaccine_pass(id=-1):
    try:
        cursor = connection.cursor()
        query="""
        select vaccine_taker.first_name, vaccine_taker.mid_name, vaccine_taker.last_name,doctor.first_name as doctor_fname,
        doctor.mid_name as doctor_mname, doctor.last_name as doctor_lname, time_slot.time as date, appointment.status
        from appointment 
        inner join vaccine_taker on appointment.vaccine_taker_id=vaccine_taker.id
        inner join time_slot on appointment.time_slot_id = time_slot.id
        inner join doctor on doctor.id=time_slot.doctor_id
        where appointment.vaccine_taker_id=%s and appointment.dose_num>=2 and appointment.status=1
        order by appointment.dose_num DESC;
        """
        cursor.execute(query, (id, ))
        data=cursor.fetchone()
        if (data is not None):
            data = list(data)
            data[6] = utils.format_time(data[6])
            result = SUCCESS.copy()
            result.update({"data":data,"found":True})
            return jsonify(result)
        else:
            query="select first_name, mid_name, last_name from vaccine_taker where id=%s"
            cursor.execute(query, (id, ))
            data=cursor.fetchone()
            result = SUCCESS.copy()
            result.update({"data":data, "found":False})
            return jsonify(result)
    except:
        return jsonify(FAILURE)
        
@app.route("/appointment_success/<int:id>")
def appointment_success(id=-1):
    try:
        params = request.args
        appointment_id = params["appointment_id"]
        with connection.cursor() as cursor:
            query = """
            do
            $do$
            begin
                if exists (select * from appointment join time_slot on appointment.time_slot_id = time_slot.id where appointment.id=%s and doctor_id=%s and appointment.status=2) then
                update vaccine_result set success = 1 from 
                    (select * from appointment where id = %s)
                tmp where vaccine_result.id = tmp.vaccine_result_id;
                update availability
                set in_progress_num = in_progress_num - 1, used_num = used_num + 1
                from 
                    (select * from appointment where id = %s)
                tmp2 where availability.vaccination_id = tmp2.vaccine_id;
                    update appointment set status = 1 where id = %s;
                end if;
            end
            $do$
            """
            cursor.execute(query, (appointment_id, id, appointment_id, appointment_id, appointment_id))
        return jsonify(SUCCESS)
    except:
        return jsonify(FAILURE)

@app.route("/appointment_failed/<int:id>")
def appointment_failed(id=-1):
    try:
        params = request.args
        appointment_id = params["appointment_id"]
        with connection.cursor() as cursor:
            query = """
            do
            $do$
            begin
                if exists (select * from appointment join time_slot on appointment.time_slot_id = time_slot.id where appointment.id=%s and doctor_id=%s and appointment.status=2) then
                update vaccine_result set success = 0 from 
                    (select * from appointment where id = %s)
                tmp where vaccine_result.id = tmp.vaccine_result_id;
                update availability
                set in_progress_num = in_progress_num - 1, available_num = available_num + 1
                from 
                    (select * from appointment where id = %s)
                tmp2 where availability.vaccination_id = tmp2.vaccine_id;
                update appointment set status = 0 where id = %s;
                end if;
            end
            $do$
            """
            cursor.execute(query, (appointment_id, id, appointment_id, appointment_id, appointment_id))
        return jsonify(SUCCESS)
    except:
        return jsonify(FAILURE)

@app.route("/appointment_cancel_doctor/<int:id>")
def appointment_cancel_doctor(id=-1):
    try:
        params = request.args
        appointment_id = params["appointment_id"]
        with connection.cursor() as cursor:
            query = """
                do
                $do$
                begin
                    if exists (select * from appointment join time_slot on appointment.time_slot_id = time_slot.id where appointment.id=%s and doctor_id=%s and appointment.status=2) then
                    update vaccine_result set success = 4 from 
                        (select * from appointment where id = %s)
                    tmp where vaccine_result.id = tmp.vaccine_result_id;
                    update availability
                    set in_progress_num = in_progress_num - 1, available_num = available_num + 1
                    from 
                        (select * from appointment where id = %s)
                    tmp2 where availability.vaccination_id = tmp2.vaccine_id;
                    update appointment set status = 4 where id = %s;
                    end if;
                end
                $do$
            """
            cursor.execute(query, (appointment_id, id, appointment_id, appointment_id, appointment_id))
        return jsonify(SUCCESS)
    except:
        return jsonify(FAILURE)

@app.route("/appointment_cancel_taker/<int:id>")
def appointment_cancel_taker(id=-1):
    try:
        params = request.args
        appointment_id = params["appointment_id"]
        with connection.cursor() as cursor:
            query = """
                do
                $do$
                begin
                    if exists (select * from appointment where appointment.id=%s and vaccine_taker_id=%s and appointment.status=2) then
                    update vaccine_result set success = 3 from 
                        (select * from appointment where id = %s)
                    tmp where vaccine_result.id = tmp.vaccine_result_id;
                    update availability
                    set in_progress_num = in_progress_num - 1, available_num = available_num + 1
                    from 
                        (select * from appointment where id = %s)
                    tmp2 where availability.vaccination_id = tmp2.vaccine_id;
                    update appointment set status = 3 where id = %s;
                    end if;
                end
                $do$
            """
            cursor.execute(query, (appointment_id, id, appointment_id, appointment_id, appointment_id))
        return jsonify(SUCCESS)
    except:
        return jsonify(FAILURE)

@app.route("/taker_chat_selection/<int:id>")
def taker_chat_selection(id=-1):
    try:
        query = """
        select doctor_id, first_name, last_name, medical_provider.name from
            (select doctor_id, first_name, last_name, medical_provider_id from
                (select distinct doctor_id 
                from appointment join time_slot on appointment.time_slot_id = time_slot.id
                where vaccine_taker_id = %s)
            tmp join doctor on tmp.doctor_id = doctor.id)
        tmp2 join medical_provider on medical_provider_id = medical_provider.id
        """
        cursor = connection.cursor()
        cursor.execute(query, (id,))
        data = cursor.fetchall()
        result = SUCCESS.copy()
        result.update({"data":data})
        return jsonify(result)
    except:
        return jsonify(FAILURE)

@app.route("/general_chat_taker/<int:id>", methods=["GET","POST"])
def general_chat_taker(id=-1):
    if request.method == "GET":
        try:
            params = request.args
            doctor_id = params["doctor_id"]
            query = """
            select doctor.first_name doctor_fname, doctor.last_name doctor_lname, direction, content, if_read, tmp.create_time, doctor_id from
            (select vaccine_taker_id, doctor_id, direction, content, if_read, create_time from message
            where vaccine_taker_id = %s and doctor_id = %s and valid = 1
            order by create_time asc)
            tmp join doctor on doctor.id = tmp.doctor_id
            """
            cursor = connection.cursor()
            cursor.execute(query, (id,doctor_id))
            messages = list(cursor.fetchall())
            messages = utils.process_messages(messages)
            result = SUCCESS.copy()
            result.update({"messages":messages})
            return jsonify(result)
        except:
            return jsonify(FAILURE)
    elif request.method == "POST":
        if request.form:
            try:
                requestData = request.form
                doctor_id = requestData["doctor_id"]
                content = requestData["content"]
                query = """
                insert into message (doctor_id, vaccine_taker_id, direction, content)
                values (%s,%s,0,%s)	
                """
                with connection.cursor() as cursor:
                    cursor.execute(query, (doctor_id, id, content))
                return jsonify(SUCCESS)
            except:
                return jsonify(FAILURE)

@app.route("/doctor_chat_selection/<int:id>")      
def doctor_chat_selection(id=-1):
    try:
        query = """
        select vaccine_taker_id, vaccine_taker.first_name, vaccine_taker.last_name from
            (select distinct vaccine_taker_id
            from appointment join time_slot on appointment.time_slot_id = time_slot.id
            where doctor_id=%s)
        tmp join vaccine_taker on tmp.vaccine_taker_id = vaccine_taker.id
        """
        cursor = connection.cursor()
        cursor.execute(query, (id,))
        data = cursor.fetchall()
        result = SUCCESS.copy()
        result.update({"data":data})
        return jsonify(result)
    except:
        return jsonify(FAILURE)

@app.route("/general_chat_doctor/<int:id>", methods=["GET","POST"])
def general_chat_doctor(id=-1):
    if request.method == "GET":
        try:
            params = request.args
            vaccine_taker_id = params["vaccine_taker_id"]
            query = """
                select vaccine_taker.first_name, vaccine_taker.last_name, direction, content, if_read, tmp.create_time, vaccine_taker_id from
                    (select vaccine_taker_id, direction, content, if_read, create_time from message
                    where vaccine_taker_id = %s and doctor_id = %s and valid = 1
                    order by create_time asc)
                tmp join vaccine_taker on vaccine_taker.id = tmp.vaccine_taker_id
            """
            cursor = connection.cursor()
            cursor.execute(query, (vaccine_taker_id, id))
            messages = list(cursor.fetchall())
            messages = utils.process_messages(messages)
            result = SUCCESS.copy()
            result.update({"messages":messages})
            print("Success")
            return jsonify(result)
        except:
            return jsonify(FAILURE)
    elif request.method == "POST":
        try:
            if request.form:
                requestData = request.form
                vaccine_taker_id = requestData["vaccine_taker_id"]
                content = requestData["content"]
                query = """
                insert into message (doctor_id, vaccine_taker_id, direction, content)
                values (%s,%s,1,%s)	
                """
                with connection.cursor() as cursor:
                    cursor.execute(query, (id, vaccine_taker_id, content))
                return jsonify(SUCCESS)
            return jsonify(FAILURE)
        except:
            return jsonify(FAILURE)
if __name__ == "__main__":
    connected = False
    while not connected:
        try:
            connection = psycopg2.connect(host=POSTGRES_HOST,
                                    user="postgres",
                                    password=POSTGRES_PASSWORD,
                                    database=POSTGRES_DB)
            connection.autocommit = True
            connected = True
        except:
            pass
    app.run(host="0.0.0.0",port="5001")