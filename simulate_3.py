import simpy
import csv
import random

# Константы
SPEED = 25  # базовая скорость грузовика, км/ч
DISTANCE = 17  # расстояние до погрузчика, км
LOADING_TIME = 5  # время загрузки, минут
HOURS_PER_DAY = 24  # количество часов в сутках
DAYS = 0.5  # количество дней симуляции
SIM_TIME = DAYS * HOURS_PER_DAY * 60  # время симуляции в минутах
BREAK_PROBABILITY = 0.1  # вероятность поломки погрузчика
BREAK_DURATION = 60  # продолжительность поломки в минуту
NUM_LOADERS = 1  # количество погрузчиков

# Класс грузовика
class Lory:
    def __init__(self, env, loader, truck_id):
        self.env = env
        self.loader = loader
        self.truck_id = truck_id  # уникальный идентификатор грузовика
        self.trips = 0  # счетчик рейсов
        self.queue_time = 0  # время простоя в очереди
        self.action = env.process(self.transport_loop())  # запускаем основной процесс

    def transport_loop(self):
        while True:
            travel_time = (DISTANCE / SPEED) * 60  # перевод в минуты
            
            print(f"Грузовик {self.truck_id} едет к погрузчику, время {self.env.now:.2f} минут.")
            yield self.env.timeout(travel_time)

            # Ожидание погрузки
            yield self.env.process(self.loader.load(self))

            # Грузовик едет обратно
            print(f"Грузовик {self.truck_id} загружен и возвращается обратно, время {self.env.now:.2f} минут.")
            yield self.env.timeout(travel_time)

            # Увеличиваем счетчик рейсов
            self.trips += 1
            print(f"Грузовик {self.truck_id} завершил рейс {self.trips}.")

# Класс погрузчика
class Loader:
    def __init__(self, env, loader_id):
        self.env = env
        self.loader_id = loader_id  # уникальный идентификатор погрузчика
        self.is_broken = False  # состояние погрузчика (работает/сломался)
        self.action = env.process(self.break_down_process())  # запуск процесса поломки
        self.resource = simpy.Resource(env, capacity=1)  # ресурс (один погрузчик)

    def break_down_process(self):
        while True:
            yield self.env.timeout(random.randint(1, 100))  # случайная работа до поломки
            if random.random() < BREAK_PROBABILITY:
                self.is_broken = True
                print(f"Погрузчик {self.loader_id} сломался, время {self.env.now:.2f} минут.")
                yield self.env.timeout(BREAK_DURATION)  # время ремонта
                self.is_broken = False
                print(f"Погрузчик {self.loader_id} был отремонтирован, время {self.env.now:.2f} минут.")

    def load(self, truck):
        if self.is_broken:
            print(f"Погрузчик {self.loader_id} не может загрузить грузовик {truck.truck_id}, время {self.env.now:.2f} минут.")
            return
        
        with self.resource.request() as request:
            yield request  # ждем, пока не освободится погрузчик
            truck.queue_time += self.env.now - truck.env.now 
            # Погрузка
            print(f"Грузовик {truck.truck_id} начинает загрузку, время {self.env.now:.2f} минут.")
            yield self.env.timeout(LOADING_TIME)
            print(f"Грузовик {truck.truck_id} загрузился, время {self.env.now:.2f} минут.")

# Функция запуска симуляции
def run_simulation(num_trucks=36, num_loaders=NUM_LOADERS):
    env = simpy.Environment()
    loaders = [Loader(env, i) for i in range(num_loaders)]
    trucks = [Lory(env, loaders[i % num_loaders], i) for i in range(num_trucks)]
    
    # Запускаем симуляцию
    env.run(until=SIM_TIME)

    # Подсчет итогов
    total_trips = sum(truck.trips for truck in trucks)
    total_queue_time = sum(truck.queue_time for truck in trucks)

    print(f"\nИтоги симуляции:")
    print(f"Всего рейсов: {total_trips}")
    print(f"Общее время простоя в очереди: {total_queue_time:.2f} минут.")
    
    # Запись логов в CSV файл
    write_log_to_csv(loader.log, 'loading_log.csv')

# Запуск симуляции
if __name__ == '__main__':
    run_simulation()