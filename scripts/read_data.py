import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# the header in line 10 of the csv file
header_location=10
df = pd.read_csv("Turner_Chest1secDataTable.csv", header=header_location, decimal=',', usecols=['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude'])
# print(df.empty)
# print(df.shape)
print(df.columns)
# print(df.head)
print(df.info())
# print(df.describe())
# print(df['Inclinometer Off'].unique())
# print(df['Inclinometer Off'].value_counts())
# print(df.loc[(df['Date']=='13/12/2022'), ['Date',' Time','Vector Magnitude']])
# print(df.loc[(df['Date']=='13/12/2022') & (df['Vector Magnitude'].isnull()), ['Date',' Time','Vector Magnitude']])
# print(df.loc[(df['Date']=='13/12/2022') & ((df[' Axis1']>0)|(df['Axis2']>0)|(df['Axis3']>0)), ['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude']])

print(df.loc[(df['Date']=='12/12/2022') & (df[' Time']>='22:00:00'), ['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude']])
print(df.loc[(df['Date']=='13/12/2022') & (df[' Time']<='10:00:00'), ['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude']])


dates_list = df['Date'].unique().tolist()
print(dates_list, len(dates_list), type(dates_list))

fig, axes = plt.subplots(nrows=3, ncols=3, subplot_kw={'ylim': (0,250)})
row=0
col=0

for day_now, day_next in zip(dates_list, dates_list[1:]):
    df_night_part0 = df.loc[(df['Date']==day_now) & (df[' Time']>='22:00:00'), ['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude']]
    df_night_part1 = df.loc[(df['Date']==day_next) & (df[' Time']<='10:00:00'), ['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude']]

    df_night = df_night_part0.append(df_night_part1)
    df_night.plot(x=' Time', y='Vector Magnitude', title='', ax=axes[row,col])
    col+=1
    if col==3:
        col=0
        row+=1

plt.show()


# fig, axes = plt.subplots(nrows=3, ncols=3, subplot_kw={'ylim': (0,250)})

# # df_one_day = df.loc[(df['Date']=='13/12/2022') & ((df[' Axis1']>0)|(df['Axis2']>0)|(df['Axis3']>0)), ['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude']]
# row=0
# col=0
# for date in dates_list:
# # date_0 = '12/12/2022'
# # date_1 = '13/12/2022'
# # date_2 = '14/12/2022'
# # date_3 = '15/12/2022'

#     df_day = df.loc[(df['Date']==date), [' Time','Vector Magnitude']]
# # df_day_0 = df.loc[(df['Date']==date_0), [' Time','Vector Magnitude']]
# # df_day_1 = df.loc[(df['Date']==date_1), [' Time','Vector Magnitude']]
# # df_day_2 = df.loc[(df['Date']==date_2), [' Time','Vector Magnitude']]
# # df_day_3 = df.loc[(df['Date']==date_3), [' Time','Vector Magnitude']]
#     df_day.plot(x=' Time', y='Vector Magnitude', title='', ax=axes[row,col])
# # df_day_0.plot(x=' Time', y='Vector Magnitude', title='Day '+ date_0, ax=axes[0,0])
# # df_day_1.plot(x=' Time', y='Vector Magnitude', title='Day '+ date_1, ax=axes[0,1])
# # df_day_2.plot(x=' Time', y='Vector Magnitude', title='Day '+ date_2, ax=axes[1,0])
# # df_day_3.plot(x=' Time', y='Vector Magnitude', title='Day '+ date_3, ax=axes[1,1])
#     col+=1
#     if col==3:
#         col=0
#         row+=1


# plt.show()

# print(df.loc[df['Date']=='13/12/2022',['Time']])
