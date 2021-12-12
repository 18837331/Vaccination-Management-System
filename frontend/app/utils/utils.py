from datetime import datetime, time, timedelta

VACCINE_RESULT_STATUS = {1:"Success", 0:"Failed", 2:"In Progress", 3:"Canceled by Vaccine Taker", 4:"Canceled by Doctor"}

# Input a dict indicating which weekday is working 
# Output a list of 0/1 where 0 indicates not working and 1 indicates working
def generate_weekday_list(work_day_dict):
    result = []
    result.append(work_day_dict["work_monday"])
    result.append(work_day_dict["work_tuesday"])
    result.append(work_day_dict["work_wednesday"])
    result.append(work_day_dict["work_thursday"])
    result.append(work_day_dict["work_friday"])
    result.append(work_day_dict["work_saturday"])
    result.append(work_day_dict["work_sunday"])
    return result

def generate_time_slots(work_start_time, work_end_time, work_day_dict):
    work_start_hour=int(work_start_time) // 100
    work_start_minute=int(work_start_time) % 100
    work_end_hour=int(work_end_time) // 100
    work_end_minute=int(work_end_time) % 100
    result = []

    # Transform work_day_dict into a list
    weekday_list = generate_weekday_list(work_day_dict)

    # Find start of this week and end of next week
    today = datetime.today()
    today = datetime(today.year, today.month, today.day)
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=14)

    while start < end:
        curr_weekday = start.weekday()
        if weekday_list[curr_weekday] == 1:
            curr_hour = start.hour
            curr_minute = start.minute
            if (work_start_hour < curr_hour or (curr_hour == work_start_hour and 
            work_start_minute <= curr_minute)) and (curr_hour < work_end_hour or 
            (curr_hour == work_end_hour and curr_minute < work_end_minute)):
                result.append(start.strftime("%Y%m%d%H%M"))
        # Forward start by 15 minutes
        start = start + timedelta(minutes=15)
    return result

def format_apt_selection(data):
    provider_id_info_dict = {}
    provider_id_time_dict = {}
    formatted_data = []
    for t in data:
        curr_id = t[0]
        id_time = t[7]
        if provider_id_info_dict.get(curr_id) is not None:
            provider_id_time_dict[curr_id].append(id_time[-4:-2]+":"+id_time[-2:])
        else:
            id_info = (t[1],t[2],t[3],t[4],t[5],t[6])
            provider_id_info_dict[curr_id] = id_info
            provider_id_time_dict[curr_id] = [id_time[-4:-2]+":"+id_time[-2:]]
    for id, info in provider_id_info_dict.items():
        time_slots = provider_id_time_dict[id]
        formatted_data.append((id,info,time_slots))
    return formatted_data

# Turn YYYYmmDDHHMM to YYYY-mm-DD HH:MM
def format_time(origin):
    result = origin[:4] + "-" + origin[4:6] + "-" + origin[6:8] + " " + origin[8:10] + ":" + origin[10:]
    return result

# Process and combine messages
def process_messages(messages):
    result = []
    p = 0
    tmp = []
    tmp_direction = -1
    while p < len(messages):
        if tmp_direction == -1 or messages[p][2] == tmp_direction:
            curr_message = list(messages[p])
            curr_message[5] = curr_message[5].strftime("%Y-%m-%d %H:%M")
            tmp.append(curr_message)
            tmp_direction = messages[p][2]
            p += 1
        else:
            result.append(tmp)
            tmp = []
            tmp_direction = -1
    if len(tmp) != 0:
        result.append(tmp)
    return result