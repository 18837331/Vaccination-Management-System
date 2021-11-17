from datetime import datetime, time, timedelta

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