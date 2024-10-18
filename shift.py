from datetime import datetime, timedelta
START_TIME = datetime(2024, 1, 1, 0, 0, 0)
time_now = 500
time_shift = datetime.strptime("7:30", "%H:%M").time()


current = START_TIME + timedelta(minutes = time_now)


current = current.time()

delta = timedelta(
     hours=time_shift.hour-current.hour,
     minutes=time_shift.minute-current.minute)


to_shift = timedelta(hours = 1, minutes = 30) # осталось до конца смены

print(f'текущее время {current}')
print(f' время до пересменки {delta}')
print(time_shift)

if delta > to_shift:
    print('можно рабоать')
else:
    print('пора на пересменку')
    


# MORNING_SHIFT = datetime.strptime("6:30", "%H:%M").time()
# EVNING_SHIFT = datetime.strptime("18:30", "%H:%M").time()
# TIME_TO_SHIFT = timedelta(hours = 1, minutes = 30) # время до конца смены


# def delta_time(t1,t2):
#     return timedelta(
#         hours = t1.hour - t2.hour,
#         minutes = t1.minute - t2.minute
#     )

# def check_shift(current_env_time):
#     cur_time = (START_TIME + timedelta(minutes=current_env_time)).time()
#     if delta_time(cur_time)
    
    