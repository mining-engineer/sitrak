
from datetime import datetime, timedelta

MORNING_SHIFT = datetime.strptime("6:30", "%H:%M").time() # окончание смены утром
EVNING_SHIFT = datetime.strptime("18:30", "%H:%M").time()  # окончание смены вечером
TIME_TO_SHIFT = timedelta(hours = 1, minutes = 30) # время до конца смены для постановки на пересменку
NEXT_DAY_TIME = datetime.strptime("00:00", "%H:%M").time()  # переход на следующие сутки

CURRENT_TIME = datetime(2024, 1, 1, 4, 50, 0) # текущее время


def delta_time(t1,t2):
    return timedelta(
        hours = t1.hour - t2.hour,
        minutes = t1.minute - t2.minute
    )


def check_shift(cur_time):
    if cur_time.time() > MORNING_SHIFT and cur_time.time() < EVNING_SHIFT:
        delta = delta_time(EVNING_SHIFT, cur_time.time())
        if delta > TIME_TO_SHIFT:
            return print(f'Осталось рабоать {delta}')
        else:
            return print('пора на пересменку')
    elif cur_time.time() > NEXT_DAY_TIME and cur_time.time() < MORNING_SHIFT:
        delta = delta_time(MORNING_SHIFT, cur_time.time())
        if delta > TIME_TO_SHIFT:
            return print(f'Осталось работать {delta}')
        else:
            return print('пора на пересменку')
        
        
check_shift(CURRENT_TIME)
        
        
        
        
#     elif cur_time.time() < EVNING_SHIFT:
#         # Утренная смена
#         shift_end = EVNING_SHIFT
#     elif cur_time.time() > EVNING_SHIFT:
#         # Вечерняя смена
#         shift_end = MORNING_SHIFT
#         if cur_time.date() == (datetime.combine(cur_time.date(), EVNING_SHIFT) + timedelta(days=1)).date():
#             shift_end = MORNING_SHIFT  # Следующая утренняя смена
        
#     # Вычисляем время до конца смены
#     if shift_end == MORNING_SHIFT:
#         shift_end_datetime = datetime.combine(cur_time.date() + timedelta(days=1), shift_end)
#     else:
#         shift_end_datetime = datetime.combine(cur_time.date(), shift_end)

#     time_until_shift_end = shift_end_datetime - cur_time

#     # Проверяем, осталось ли меньше 1,5 часов до конца смены
#     if time_until_shift_end < TIME_TO_SHIFT:
#         print('Пора на пересменку')
#     else:
#         minutes_left = time_until_shift_end.total_seconds() / 60
#         print(f'До пересменки осталось {minutes_left:.0f} минут')

# # Вызов функции с текущим временем
# check_shift(CURRENT_TIME)