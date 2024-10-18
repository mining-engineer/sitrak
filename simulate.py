import simpy
import random

# Константы
SPEED = 25  # скорость грузовика, км/ч
DISTANCE = 17  # расстояние до погрузчика, км
LOADING_TIME = 5  # время загрузки, минут
HOURS_PER_DAY = 24  # количество часов в сутках
DAYS = 10  # количество дней симуляции
SIM_TIME = DAYS * HOURS_PER_DAY * 60  # время симуляции в минутах (10 дней по 24 часа)

# Класс грузовика
class Lory:
    def __init__(self, env, loader):
        self.env = env
        self.loader = loader
        self.action = env.process(self.transport_loop())  # Запускаем основной процесс

    def transport_loop(self):
        while True:
            track_speed = SPEED*(1 + random.uniform(-0.1, 0.1))
            # Грузовик едет к погрузчику
            travel_time = (DISTANCE / track_speed) * 60  # перевод в минуты
            print(f"Грузовик едет к погрузчику, время {self.env.now:.2f} минут.")
            yield self.env.timeout(travel_time)
            
            # Погрузка
            print(f"Грузовик прибыл к погрузчику, время {self.env.now:.2f} минут.")
            yield self.env.process(self.loader.load())
            
            # Грузовик едет обратно
            print(f"Грузовик загружен и возвращается обратно, время {self.env.now:.2f} минут.")
            yield self.env.timeout(travel_time)

# Класс погрузчика
class Loader:
    def __init__(self, env):
        self.env = env

    def load(self):
        print(f"Погрузчик начинает загрузку, время {self.env.now:.2f} минут.")
        yield self.env.timeout(LOADING_TIME)
        print(f"Погрузка завершена, время {self.env.now:.2f} минут.")

# Функция запуска симуляции
def run_simulation():
    env = simpy.Environment()
    loader = Loader(env)
    lory = Lory(env, loader)
    
    # Запускаем симуляцию на 10 дней (переводим в минуты)
    env.run(until=SIM_TIME)

# Запуск симуляции
run_simulation()