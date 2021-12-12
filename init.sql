CREATE OR REPLACE FUNCTION update_modified_time_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.modified_time = now(); 
   RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TABLE IF NOT EXISTS vaccine_taker (
    id SERIAL NOT NULL , -- 'ID for vaccine_takers',
    first_name varchar(32) NOT NULL , -- 'First Name',
    mid_name varchar(32) NOT NULL DEFAULT '' , -- 'Middle Name',
    last_name varchar(32) NOT NULL , -- 'Last Name',
    birthdate varchar(8) NOT NULL , -- 'Birthdate',
    email varchar(32) UNIQUE NOT NULL , -- 'Email',
    phone_num varchar(32) , -- 'Phone number',
    password varchar(256) NOT NULL , -- 'Password',
    status int NOT NULL DEFAULT 1 , -- 'Status code (to be designed)',
    create_time timestamp DEFAULT CURRENT_TIMESTAMP , -- 'TIME for create',
    modified_time timestamp DEFAULT CURRENT_TIMESTAMP, -- 'time stamp for last modification',
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS doctor (
    id SERIAL NOT NULL , -- 'ID for doctors',
    first_name varchar(32) NOT NULL , -- 'First Name',
    mid_name varchar(32) NOT NULL DEFAULT '' , -- 'Middle Name',
    last_name varchar(32) NOT NULL , -- 'Last Name',
    birthdate varchar(8) NOT NULL , -- 'Birthdate',
    password varchar(256) NOT NULL , -- 'Password',
    status int NOT NULL DEFAULT 1 , -- 'Status code (to be designed)',
    email varchar(32) NOT NULL UNIQUE, -- 'Email',
    phone_num varchar(32) , -- 'Phone number',
    work_start_time	varchar(4) NOT NULL DEFAULT '0900', -- The time start accepting appointments in a day (hhmm)
    work_end_time	varchar(4) NOT NULL DEFAULT '1700', -- The time stop accepting apopintments in a day (hhmm)
    work_monday	int NOT NULL DEFAULT 1, -- 1 for working, 0 for not working
    work_tuesday	int NOT NULL DEFAULT 1, -- 1 for working, 0 for not working
    work_wednesday	int NOT NULL DEFAULT 1, -- 1 for working, 0 for not working
    work_thursday	int NOT NULL DEFAULT 1, -- 1 for working, 0 for not working
    work_friday	int NOT NULL DEFAULT 1, -- 1 for working, 0 for not working
    work_saturday	int NOT NULL DEFAULT 0, -- 1 for working, 0 for not working
    work_sunday	int NOT NULL DEFAULT 0, -- 1 for working, 0 for not working
    medical_provider_id int NOT NULL DEFAULT 0 , -- 'ID of the assigned medical provider',
    create_time timestamp DEFAULT CURRENT_TIMESTAMP , -- 'TIME for create',
    modified_time timestamp DEFAULT CURRENT_TIMESTAMP, -- 'time stamp for last modification',
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS time_slot (
    id SERIAL NOT NULL , -- 'ID of time slot',
    doctor_id int NOT NULL , -- 'ID of the doctor the time slot belongs to',
    time varchar(32) NOT NULL , -- 'the starting time of the time slot(format YYYYMMDD HH:MM),  each time slot indicates 15 minutes from starting',
    status int NOT NULL DEFAULT 1 , -- 'status code for the time slot (2 is occupied, 1 is free, 0 is unavailable)',
    PRIMARY KEY (id),
    UNIQUE (doctor_id, time)
);

CREATE TABLE IF NOT EXISTS appointment (
    id SERIAL NOT NULL , -- 'ID of the appointment',
    vaccine_taker_id int NOT NULL , -- 'ID of the vaccine taker',
    time_slot_id int NOT NULL , -- 'ID of the time slot',
    dose_num int NOT NULL DEFAULT 1 , -- '1 as first dose, 2 as second dose…',
    vaccine_id int NOT NULL , -- 'ID of the vaccination shot',
    status int NOT NULL DEFAULT 1 , -- '0 for unvalid, 1 for normal, 2 for cancelled by vaccine taker, 3 for cancelled by doctor',
    doctor_notes varchar(256) NOT NULL DEFAULT '' , -- 'Doctor note',
    vaccine_taker_note varchar(256) NOT NULL DEFAULT '' , -- 'Vaccine Taker note',
    vaccine_result_id int NOT NULL , -- 'ID for the results of vaccine injection',
    create_time timestamp DEFAULT CURRENT_TIMESTAMP , -- 'time stamp for creation',
    modified_time timestamp DEFAULT CURRENT_TIMESTAMP, -- 'time stamp for last modification',
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS message (
    id SERIAL NOT NULL , -- 'ID of private chat message',
    vaccine_taker_id int NOT NULL , -- 'ID of vaccine taker',
    doctor_id int NOT NULL , -- 'ID of the doctor',
    direction int NOT NULL , -- '0 as message sent from vaccine taker to doctor, 1 as from doctor to vaccine taker',
    content text NOT NULL , -- 'The content of the private message',
    if_read int NOT NULL DEFAULT 0 , -- '0 as not read, 1 as read',
    valid int NOT NULL DEFAULT 1 , -- '0 as not valid, 1 as valid',
    create_time timestamp DEFAULT CURRENT_TIMESTAMP , -- 'time stamp for creation',
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS vaccine_result (
    id SERIAL NOT NULL , -- 'ID for vaccine_result',
    success int NOT NULL DEFAULT 2 , -- '0 as failed, 1 as success, 2 as in progress',
    fever int NOT NULL DEFAULT 0 , -- '0 as no fever side effect, 1 as fever side effect',
    fever_duration int NOT NULL DEFAULT 0 , -- 'duration of fever in days',
    fever_temp numeric(5,2) NOT NULL DEFAULT 0 , -- 'Highest temp of fever in F',
    pain int NOT NULL DEFAULT 0 , -- '0 as no pain side effect, 1 as pain side effect',
    pain_duration int NOT NULL DEFAULT 0 , -- 'duration of pain in days',
    redness int NOT NULL DEFAULT 0 , -- '0 as no redness side effect, 1 as redness side effect',
    redness_duration int NOT NULL DEFAULT 0 , -- 'duration of redness in days',
    swelling int NOT NULL DEFAULT 0 , -- '0 as no swelling side effect, 1 as swelling side effect',
    swelling_duration int NOT NULL DEFAULT 0 , -- 'duration of swelling in days',
    tiredness int NOT NULL DEFAULT 0 , -- '0 as no tiredness side effect, 1 as tiredness side effect',
    tiredness_duration int NOT NULL DEFAULT 0 , -- 'duration of tiredness in days',
    headache int NOT NULL DEFAULT 0 , -- '0 as no headache side effect, 1 as headache side effect',
    headache_duration int NOT NULL DEFAULT 0 , -- 'duration of headache in days',
    nausea int NOT NULL DEFAULT 0 , -- '0 as no nausea side effect, 1 as nausea side effect',
    nausea_duration int NOT NULL DEFAULT 0 , -- 'duration of nausea in days',
    create_time timestamp DEFAULT CURRENT_TIMESTAMP , -- 'TIME for create',
    modified_time timestamp DEFAULT CURRENT_TIMESTAMP, -- 'time stamp for last modification',
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS medical_provider(
    id SERIAL NOT NULL , -- 'ID of medical provider',
    name varchar(128) NOT NULL , -- 'Name of the medical provider',
    password varchar(256) NOT NULL , -- 'Password',
    address1 varchar(128) NOT NULL , -- 'First line of address',
    address2 varchar(128) NOT NULL DEFAULT '' , -- 'Second line of address',
    city varchar(32) NOT NULL , -- 'City',
    state char(2) NOT NULL , -- 'State (e.g. NY, WA)',
    country varchar(32) NOT NULL DEFAULT 'United States' , -- 'Country',
    zipcode char(5) NOT NULL, -- 'Zipcode'
    email varchar(32) UNIQUE , -- 'Email',
    phone_num varchar(32) , -- 'Phone number',
    valid int NOT NULL DEFAULT 1 , -- '0 as invalid, 1 as valid',
    create_time timestamp DEFAULT CURRENT_TIMESTAMP , -- 'TIME for create',
    modified_time timestamp DEFAULT CURRENT_TIMESTAMP, -- 'time stamp for last modification',
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS vaccination (
    id SERIAL NOT NULL , -- 'ID of vaccination',
    vaccine_name varchar(256) NOT NULL , -- 'Name of vaccination',
    description varchar(256) NOT NULL DEFAULT '' , -- 'Description of vaccination',
    version varchar(32) NOT NULL DEFAULT 'Default' , -- 'Version',
    fda_approved int NOT NULL , -- '1 as the vaccination is approved or authorized by FDA',
    who_listing int NOT NULL , -- '1 as the vaccination is in the WHO Emergency Use Listing',
    clinical_trial int NOT NULL , -- '1 as the vaccination is part of US based clinical trial',
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS availability (
    medical_provider_id int NOT NULL , -- 'ID of medical provider',
    vaccination_id int NOT NULL , -- 'ID of vaccination',
    available_num int NOT NULL , -- 'Number of available shots',
    in_progress_num int NOT NULL DEFAULT 0 , -- 'Number of shots in progress(being reserved in appointments)',
    used_num int NOT NULL DEFAULT 0 , -- 'Number of used shots',
    wasted_num int NOT NULL DEFAULT 0 , -- 'Number of wasted shots',
    create_time timestamp DEFAULT CURRENT_TIMESTAMP , -- 'TIME for create',
    modified_time timestamp DEFAULT CURRENT_TIMESTAMP -- 'time stamp for last modification'
);

CREATE TABLE IF NOT EXISTS post (
    id SERIAL NOT NULL , -- 'ID of the post',
    content text NOT NULL , -- 'Content of the post',
    visible int NOT NULL DEFAULT 1 , -- '0 as the post is not visible, 1 as the post is visible',
    create_time timestamp DEFAULT CURRENT_TIMESTAMP , -- 'TIME for create',
    modified_time timestamp DEFAULT CURRENT_TIMESTAMP, -- 'time stamp for last modification',
    PRIMARY KEY (id)
);

CREATE TRIGGER update_vaccine_taker_modified_time BEFORE UPDATE
ON vaccine_taker FOR EACH ROW EXECUTE PROCEDURE 
update_modified_time_column();

CREATE TRIGGER update_doctor_modified_time BEFORE UPDATE
ON doctor FOR EACH ROW EXECUTE PROCEDURE 
update_modified_time_column();

CREATE TRIGGER update_appointment_modified_time BEFORE UPDATE
ON appointment FOR EACH ROW EXECUTE PROCEDURE 
update_modified_time_column();

CREATE TRIGGER update_availability_modified_time BEFORE UPDATE
ON availability FOR EACH ROW EXECUTE PROCEDURE 
update_modified_time_column();

CREATE TRIGGER update_post_modified_time BEFORE UPDATE
ON post FOR EACH ROW EXECUTE PROCEDURE 
update_modified_time_column();

CREATE TRIGGER update_vaccine_result_modified_time BEFORE UPDATE
ON vaccine_result FOR EACH ROW EXECUTE PROCEDURE 
update_modified_time_column();

