from datetime import datetime, timedelta
import simpy
import random
import csv

# Константы
START_TIME = datetime(2024, 1, 1, 0, 0, 0)
DISTANCE = 17.6  # Расстояние в километрах
SPEED = 27  # Скорость в км/ч
LOADING_TIME = 5  # Время загрузки в минутах
MORNING_SHIFT = datetime.strptime("6:30", "%H:%M").time()  # окончание смены утром
EVENING_SHIFT = datetime.strptime("18:30", "%H:%M").time()  # окончание смены вечером
TIME_TO_SHIFT = timedelta(hours=1, minutes=30)  # время до конца смены для постановки на пересменку


def real_time(dur) -> datetime:
    return (START_TIME + timedelta(minutes=dur))


def time_formatter(dur):
    return real_time(dur).strftime('%Y-%m-%d %H:%M')


class Logger:
    def __init__(self, filename='output.csv'):
        self.filename = filename
        with open(self.filename, 'w', newline='') as csvfile:
            fieldnames = ['Truck ID', 'Status', 'Loader ID', 'Start Time', 'End Time', 'Duration (min)']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

    def log_event(self, truck_id, status, loader_id=None, start_time=None, end_time=None):
        duration = None
        if start_time and end_time:
            duration = (datetime.strptime(end_time, '%Y-%m-%d %H:%M') - datetime.strptime(start_time, '%Y-%m-%d %H:%M')).total_seconds() / 60
        
        with open(self.filename, 'a', newline='') as csvfile:
            fieldnames = ['Truck ID', 'Status', 'Loader ID', 'Start Time', 'End Time', 'Duration (min)']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({
                'Truck ID': truck_id,
                'Status': status,
                'Loader ID': loader_id,
                'Start Time': start_time,
                'End Time': end_time,
                'Duration (min)': duration
            })
        duration_output = f"{duration:.2f}" if duration is not None else "N/A"
        print(f"Truck ID: {truck_id}, Status: {status}, Loader ID: {loader_id}, Start Time: {start_time}, End Time: {end_time}, Duration: {duration_output} min")


class Lory:
    def __init__(self, env, truck_id, loader, logger):
        self.env = env
        self.truck_id = truck_id
        self.loader = loader
        self.logger = logger
        self.action = env.process(self.run())

    def run(self):
        while True:
            yield self.env.process(self.drive_to_load())
            yield self.env.process(self.loader.load(self))
            yield self.env.process(self.drive_to_unload())
            yield self.env.process(self.check_shift())    

    def drive_to_load(self):
        travel_time = (DISTANCE / SPEED * (1 + random.uniform(-0.1, 0.1))) * 60
        start_time = time_formatter(self.env.now)
        self.logger.log_event(self.truck_id, "Движение на погрузку", start_time=start_time, end_time = time_formatter(self.env.now + travel_time))
        yield self.env.timeout(travel_time)

    def drive_to_unload(self):
        travel_time = (DISTANCE / SPEED * (1 + random.uniform(-0.1, 0.1))) * 60
        start_time = time_formatter(self.env.now)
        self.logger.log_event(self.truck_id, "Движение на разгрузку", start_time=start_time, end_time = time_formatter(self.env.now + travel_time))
        yield self.env.timeout(travel_time)

    def check_shift(self):
        current_time = real_time(self.env.now).time()
        delta = None
        
        if MORNING_SHIFT < current_time < EVENING_SHIFT:
            delta = timedelta(hours=EVENING_SHIFT.hour - current_time.hour, minutes=EVENING_SHIFT.minute - current_time.minute)
        elif current_time > EVENING_SHIFT or current_time < MORNING_SHIFT:
            if current_time < MORNING_SHIFT:
                delta = timedelta(hours=MORNING_SHIFT.hour - current_time.hour, minutes=MORNING_SHIFT.minute - current_time.minute)
            else: 
                delta = timedelta(hours=MORNING_SHIFT.hour - current_time.hour, minutes=MORNING_SHIFT.minute - current_time.minute) + timedelta(hours=24)

        if delta and delta < TIME_TO_SHIFT:
            start_time = time_formatter(self.env.now)
            yield self.env.timeout(delta.total_seconds() / 60)
            end_time = time_formatter(self.env.now)
            self.logger.log_event(self.truck_id, 'Пересменка', start_time=start_time, end_time=end_time)


class Loader:
    def __init__(self, env, loader_id, logger):
        self.env = env
        self.loader_id = loader_id
        self.resource = simpy.Resource(env, capacity=1)  

    def load(self, lory):
        with self.resource.request() as request:
            yield request  # Ожидание, пока погрузчик будет свободен
            
            loading_start_time = time_formatter(self.env.now)
            yield self.env.timeout(LOADING_TIME)  
            loading_end_time = time_formatter(self.env.now)

            # Логируем событие загрузки
            lory.logger.log_event(lory.truck_id, "Погрузка", loader_id=self.loader_id, start_time=loading_start_time, end_time=loading_end_time)

def run_simulation():
    env = simpy.rt.RealtimeEnvironment(initial_time=390, factor=0.01)
    logger = Logger()
    
    loaders = [Loader(env, i, logger) for i in range(1)]
    lories = [Lory(env, i, loaders[i % len(loaders)], logger) for i in range(4)]
    
    env.run(until=24 * 60)  # Симуляция на 24 часа

if __name__ == '__main__':
    run_simulation()