import simpy
import simpy.rt
from datetime import datetime, timedelta
import random

# Константы
START_TIME = datetime(2024, 1, 1, 0, 0, 0)
DISTANCE = 17.6  # Расстояние в километрах
SPEED = 27  # Скорость в км/ч
LOADING_TIME = 5  # Время загрузки в минутах

# Время начала смен
MORNING_SHIFT_START = datetime(2024, 1, 1, 6, 30)
EVENING_SHIFT_START = datetime(2024, 1, 1, 18, 30)

def time_formatter(dur):
    ''' переводит время моделирования в строку '''
    return (START_TIME + timedelta(minutes=dur)).strftime('%Y-%m-%d %H:%M')

class Lory:
    def __init__(self, env, truck_id, loader):
        self.env = env
        self.truck_id = truck_id
        self.loader = loader
        self.is_loaded = False  # Флаг, чтобы знать, загружен ли самосвал
        self.action = env.process(self.run())

    def run(self):
        while True:
            # Поездка к погрузчику
            yield self.env.process(self.drive())
            # Ожидание погрузки
            yield self.env.process(self.loader.load(self))
            self.is_loaded = True  # Устанавливаем флаг загрузки
            # Поездка на разгрузку
            yield self.env.process(self.drive(return_trip=True))
            self.is_loaded = False  # После разгрузки самосвал пустой
            # Проверка на пересменку только если самосвал пустой
            yield self.env.process(self.check_shift())

    def check_shift(self):
        current_time = START_TIME + timedelta(minutes=self.env.now)
        travel_time = (DISTANCE / SPEED * 2 + LOADING_TIME) * 60  # Общее время восстановления
        total_time = (DISTANCE / SPEED * 60 * 2) + LOADING_TIME  # Время на поездку туда и обратно

        # Если текущее время + время на поездку и загрузку превышает начало смены
        if current_time + timedelta(minutes=total_time) >= MORNING_SHIFT_START and not self.is_loaded:
            wait_time = (MORNING_SHIFT_START - current_time).total_seconds() / 60  # перевод в минуты
            print(f"Грузовик {self.truck_id} останавливается на пересменку, ожидает до {time_formatter(self.env.now + wait_time)}.")
            yield self.env.timeout(wait_time)
        
        # Если грузовик не успевает завершить для второй смены
        elif current_time + timedelta(minutes=total_time) >= EVENING_SHIFT_START and not self.is_loaded:
            wait_time = (EVENING_SHIFT_START - current_time).total_seconds() / 60  # перевод в минуты
            print(f"Грузовик {self.truck_id} останавливается на пересменку, ожидает до {time_formatter(self.env.now + wait_time)}.")
            yield self.env.timeout(wait_time)

    def drive(self, return_trip=False):
        # Время в пути с учетом случайной погрешности ±10%
        travel_time = (DISTANCE / SPEED * (1 + random.uniform(-0.1, 0.1))) * 60  # Перевод в минуты
        direction = "разгрузки" if return_trip else "погрузчику"
        print(f"Грузовик {self.truck_id} выехал на {direction}, время {time_formatter(self.env.now)}.")
        
        # Ожидание окончания поездки
        yield self.env.timeout(travel_time)
        
        print(f"Грузовик {self.truck_id} приехал на {direction}, время {time_formatter(self.env.now)}.")

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