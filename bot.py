import logging
import os
import subprocess
import time

from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater, MessageHandler, Filters

from dotenv import load_dotenv 

load_dotenv()

secret_token = os.getenv('TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

def start(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([['/newsim']], resize_keyboard=True)

    context.bot.send_message(
        chat_id=chat.id,
        text='Привет, {}. Используй кнопку ниже, чтобы начать симуляцию.'.format(name),
        reply_markup=button
    )

def analyze_results():
    import pandas as pd

    df = pd.read_csv('output.csv')
    df = df.loc[df['Duration (min)'] != 0].reset_index(drop=True)

    count_of_trip = df.loc[df['Status'] == 'Погрузка'].shape[0]
    average_trip = count_of_trip / df['Truck ID'].nunique()
    average_shift = df.loc[df['Status'] == 'Пересменка']['Duration (min)'].mean()
    max_shift = df.loc[df['Status'] == 'Пересменка']['Duration (min)'].max()
    min_shift = df.loc[df['Status'] == 'Пересменка']['Duration (min)'].min()
    kio = df.loc[df['Status'].isin(['Погрузка', 'Движение на разгрузку', 'Движение на погрузку'])]['Duration (min)'].sum() / df['Duration (min)'].sum()
    time_in_queu = df.loc[df['Status'] == 'Ожидание погрузки']['Duration (min)'].sum() / 60

    return (f'Количество рейсов за 24ч {count_of_trip}\n'
            f'Ср количество рейсов за 24ч {average_trip:0.1f}\n'
            f'Ср значение пересменки {average_shift:0.0f} минут\n'
            f'Макс значение пересменки {max_shift:0.0f} минут\n'
            f'Мин значение пересменки {min_shift:0.0f} минут\n'
            f'Время в очередях на погрузку {time_in_queu:0.1f} часов\n'
            f'КИО {kio:0.2f}')

def request_simulation_params(update, context):
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text='Пожалуйста, укажи количество самосвалов и погрузчиков через запятую, например: 26, 2.'
    )

def handle_user_input(update, context):
    chat = update.effective_chat
    user_input = update.message.text

    # Отправляем сообщение о том, что пользователю придется подождать
    context.bot.send_message(
        chat_id=chat.id,
        text='Пожалуйста, подождите пару минут, начинается симуляция...'
    )

    time.sleep(2)  # Симуляция ожидания (в реальных условиях лучше использовать асинхронный подход)

    results = run_simulation(user_input)
    
    context.bot.send_message(
        chat_id=chat.id,
        text=results
    )

def run_simulation(args):
    # Здесь мы должны вызвать наш скрипт simulation.py с аргументами
    num_trucks, num_loaders = map(int, args.split(','))
    
    try:
        # Обратите внимание, что в этом месте запуск скрипта идет через subprocess
        subprocess.run(['python', 'simulation.py', str(num_trucks), str(num_loaders)], check=True)
        
        # Теперь вызовем анализ и получим результаты
        results = analyze_results()
        return results
    except Exception as e:
        return f'Ошибка при запуске симуляции: {e}'

def main():
    updater = Updater(token=secret_token)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('newsim', request_simulation_params))  # Обработчик команды для нового запроса
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_user_input))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()