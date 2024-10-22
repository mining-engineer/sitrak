# /sanalys.py

import pandas as pd

df = pd.read_csv('output.csv')
df = df.loc[df['Duration (min)'] != 0].reset_index(drop=True)

count_of_trip= df.loc[df['Status'] == 'Погрузка'].shape[0]

average_trip = df.loc[df['Status'] == 'Погрузка'].shape[0] / df['Truck ID'].nunique()

average_shift = df.loc[df['Status'] == 'Пересменка']['Duration (min)'].mean()

max_shift = df.loc[df['Status'] == 'Пересменка']['Duration (min)'].max()

min_shift = df.loc[df['Status'] == 'Пересменка']['Duration (min)'].min()

kio = df.loc[df['Status'].isin(['Погрузка', 'Движение на разгрузку', 'Движение на погрузку'])]['Duration (min)'].sum() / df['Duration (min)'].sum()

time_in_queu = df.loc[df['Status'] == 'Ожидание погрузки']['Duration (min)'].sum() / 60



print(f'Количество рейсов за 24ч {count_of_trip}')
print(f'Ср количество рейсов за 24ч {average_trip:0.1f}')
print(f'Ср значение пересменки {average_shift:0.0f} минут')
print(f'Макс значение пересменки {max_shift:0.0f} минут')
print(f'Мин значение пересменки {min_shift:0.0f} минут')
print(f'Время в очередях на погрузку {time_in_queu:0.1f} часов')
print(f'КИО {kio:0.2f}')
