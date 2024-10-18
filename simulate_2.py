import simpy
import csv
import random

# Константы
SPEED = 27  # базовая скорость грузовика, км/ч
DISTANCE = 17  # расстояние до погрузчика, км
LOADING_TIME = 5  # время загрузки, минут
HOURS_PER_DAY = 24  # количество часов в сутках
DAYS = 0.5  # количество дней симуляции (0.5 дня)
SIM_TIME = DAYS * HOURS_PER_DAY * 60  # время симуляции в минутах

# Класс грузовика
class Lory:
    def __init__(self, env, loader, truck_id):
        self.env = env
        self.loader = loader
        self.truck_id = truck_id  # идентификатор грузовика
        self.trips = 0  # счетчик рейсов
        self.queue_time = 0  # время простоя в очереди
        self.action = env.process(self.transport_loop())  # запускаем основной процесс

    def transport_loop(self):
        while True:
            track_speed = SPEED * (1 + random.uniform(-0.1, 0.1))  # случайная скорость
            travel_time = (DISTANCE / track_speed) * 60  # перевод в минуты
            
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
    def __init__(self, env, num_resources):
        self.env = env
        self.resource = simpy.Resource(env, capacity=num_resources)  # количество погрузчиков
        self.log = []  # список логов

    def load(self, truck):
        queue_start = self.env.now

        with self.resource.request() as request:
            yield request  # ждем, пока не освободится погрузчик
            truck.queue_time += self.env.now - queue_start  # учитываем время ожидания
            
            # Погрузка
            print(f"Грузовик {truck.truck_id} начинает загрузку, время {self.env.now:.2f} минут.")
            self.log.append((truck.truck_id, "начало погрузки", self.env.now, self.resource))
            yield self.env.timeout(LOADING_TIME)
            print(f"Грузовик {truck.truck_id} загрузился, время {self.env.now:.2f} минут.")
            # записываем в лог
            self.log.append((truck.truck_id, "погружен", self.env.now, self.resource.count))

# Функция записи логов в CSV файл
def write_log_to_csv(log, filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID_грузовика', 'Статус', 'Время', 'ID_погрузчика'])
        writer.writerows(log)

# Функция запуска симуляции
def run_simulation(num_trucks=36, num_loaders=3):
    env = simpy.Environment()
    loader = Loader(env, num_loaders)
    trucks = [Lory(env, loader, i) for i in range(num_trucks)]
    
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
run_simulation()