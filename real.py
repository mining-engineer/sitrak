import simpy
import simpy.rt
from datetime import datetime, timedelta
import random

# Константы
START_TIME = datetime(2024, 1, 1, 0, 0, 0)
DISTANCE = 17.6  # Расстояние в километрах
SPEED = 27  # Скорость в км/ч
LOADING_TIME = 5  # Время загрузки в минутах
MORNING_SHIFT = datetime.strptime("6:30", "%H:%M").time() # окончание смены утром
EVENING_SHIFT = datetime.strptime("18:30", "%H:%M").time()  # окончание смены вечером
TIME_TO_SHIFT = timedelta(hours = 1, minutes = 30) # время до конца смены для постановки на пересменку
NEXT_DAY_TIME = datetime.strptime("00:00", "%H:%M").time()  # переход на следующие сутки


def time_formatter(dur):
    ''' переводит время моделирования в строку '''
    return (START_TIME + timedelta(minutes=dur)).strftime('%Y-%m-%d %H:%M')

def real_time(dur):
    return (START_TIME + timedelta(minutes =dur))


def delta_time(t1,t2):
    return timedelta(
        hours = t1.hour - t2.hour,
        minutes = t1.minute - t2.minute
    )


class Lory:
    def __init__(self, env, truck_id, loader):
        self.env = env
        self.truck_id = truck_id
        self.loader = loader
        self.is_loaded = False  # Состояние загрузки
        self.action = env.process(self.run())

    def run(self):
        while True:
            # Поездка к погрузчику
            yield self.env.process(self.drive())
            # Ожидание погрузки
            yield self.env.process(self.loader.load(self))
            self.is_loaded = True  # Грузовик теперь загружен
            # Поездка на разгрузку
            yield self.env.process(self.drive(return_trip=True))
            self.is_loaded = False  # Грузовик теперь разгружен
            
            # Проверка смены после разгрузки
            yield self.env.process(self.check_shift())

    def drive(self, return_trip=False):
        # Время в пути с учетом случайной погрешности ±10%
        travel_time = (DISTANCE / SPEED * (1 + random.uniform(-0.1, 0.1))) * 60  # Перевод в минуты
        direction = "разгрузки" if return_trip else "погрузчику"
        print(f"Грузовик {self.truck_id} выехал на {direction}, время {time_formatter(self.env.now)}.")
        
        # Ожидание окончания поездки
        yield self.env.timeout(travel_time)
        
        print(f"Грузовик {self.truck_id} приехал на {direction}, время {time_formatter(self.env.now)}.")
        
    def check_shift(self):
        if real_time(self.env.now).time() > MORNING_SHIFT and real_time(self.env.now).time() < EVENING_SHIFT:
            delta = delta_time(EVENING_SHIFT, real_time(self.env.now).time())
            if delta > TIME_TO_SHIFT:
                return print(f'Осталось рабоать {delta}')
            else:
                return print('пора на пересменку')
        elif real_time(self.env.now).time() > NEXT_DAY_TIME and real_time(self.env.now).time() < MORNING_SHIFT:
            delta = delta_time(MORNING_SHIFT, real_time(self.env.now).time())
            if delta > TIME_TO_SHIFT:
                return print(f'Осталось работать {delta}')
            else:
                return print('пора на пересменку')



class Loader:
    def __init__(self, env, loader_id):
        self.env = env
        self.loader_id = loader_id
        self.resource = simpy.Resource(env, capacity=1)  # Ограничиваем количество одновременно работающих погрузчиков

    def load(self, lory):
        with self.resource.request() as request:
            print(f"Грузовик {lory.truck_id} встал в очередь на погрузку, время {time_formatter(self.env.now)}.")
            yield request  # Ожидание, пока погрузчик будет свободен
            print(f"Погрузчик {self.loader_id} начинает загрузку самосвала {lory.truck_id}, время {time_formatter(self.env.now)}.")
            # Симуляция процесса загрузки
            yield self.env.timeout(LOADING_TIME)
            print(f"Погрузка завершена, время {time_formatter(self.env.now)}.")

def run_simulation():
    env = simpy.rt.RealtimeEnvironment(initial_time=390, factor=0.1)

    # Создаем 1 погрузчик и 2 грузовика
    loaders = [Loader(env, i) for i in range(1)]
    lories = [Lory(env, i, loaders[i % len(loaders)]) for i in range(2)]
    
    # Запуск симуляции
    env.run(until=24 * 60)  # Симуляция на 24 часа (в минутах)

if __name__ == '__main__':
    run_simulation()