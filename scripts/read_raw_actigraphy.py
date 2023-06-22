#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  read_raw_actigraphy.py
#  
#  Copyright 2023 Gerardo <gerardo@CNMTLO-MX2074SBP>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
# import gt3x
from datetime import timedelta, datetime, time
from pygt3x.reader import FileReader
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pywt


def plot_wavelet(arr1, arr2):
    
    fig, ax = plt.subplots(nrows=2, ncols=1)
    ax[0].plot(arr1)
    ax[1].plot(arr2)
    
    return 0


def plot_actigraphy(df, title_name):
    ts = df.index.tolist()
    axis_x = df['X'].to_numpy()
    axis_y = df['Y'].to_numpy()
    axis_z = df['Z'].to_numpy()
    
    arr_vm = np.sqrt(axis_x**2 + axis_y**2 + axis_z**2)
    theta_x = np.rad2deg(np.arccos(axis_x / arr_vm))
    theta_y = np.rad2deg(np.arccos(axis_y / arr_vm))
    theta_z = np.rad2deg(np.arccos(axis_z / arr_vm))
    
    fig, ax = plt.subplots(nrows=3, ncols=1, sharex=True, sharey=True)
    ax[0].set_ylim(-5,185)
    ax[0].plot(ts, theta_x)
    ax[1].plot(ts, theta_y)
    ax[2].plot(ts, theta_z)
    # ax[3].plot(ts, arr_vm)
    
    # ## vertical lines for 22h00
    # for idx in indexes_ini:
        # ax[0].axvline(x = idx, color = 'tab:purple')
        # ax[1].axvline(x = idx, color = 'tab:purple')
        # ax[2].axvline(x = idx, color = 'tab:purple')
        
    
    # ## vertical lines for 8h00
    # for idx in indexes_end:
        # ax[0].axvline(x = idx, color = 'tab:olive')
        # ax[1].axvline(x = idx, color = 'tab:olive')
        # ax[2].axvline(x = idx, color = 'tab:olive')
    
    ax[0].set_title(title_name)
    ax[0].set_ylabel('accel. X')
    ax[1].set_ylabel('accel. Y')
    ax[2].set_ylabel('accel. Z')
    # ax[3].set_ylabel('accel. vm')
    ax[2].set_xlabel('samples')
    
    return 0

def ticks2datetime(ticks, i):
    ## ten (10) ticks per microsecond; hence, number_of_ticks divided by 10 = number_of_microseconds
    t_delta = timedelta(microseconds = ticks)
    t_add   = timedelta(microseconds = i*1e6)
    
    t_delta = t_delta + t_add
    ## ticks start counting from January 1, 0001
    converted_ticks = datetime(1,1,1) + t_delta
    
    date_sample = converted_ticks.strftime("%Y-%m-%d")
    time_sample = converted_ticks.strftime("%H:%M:%S")
    
    return date_sample, time_sample


def ticks2datetime64(ticks_start, arr_samples):
    # ticks = np.array([638137080000000000, 638142960470000000])//10
    # ticks = ticks_start + arr_samples
    ticks_start=np.array(ticks_start)
    
    t_delta = ticks_start.astype('timedelta64[us]')
    t_add   = arr_samples.astype('timedelta64[s]')
    
    t_delta = t_delta + t_add
    
    date_start=np.datetime64('0001-01-01')
    converted_ticks = date_start + t_delta
    list_datetime = converted_ticks.tolist()
    dates=[]
    times=[]
    for date_long in list_datetime:
        
        # print(type(date_long), date_long)
        dates.append(date_long.strftime("%Y-%m-%d"))
        times.append(date_long.strftime("%H:%M:%S"))

    # print(dates)
    # print(times)
    return dates, times


def main(args):
    
    path_gt3x = "../data/projet_officiel/gt3x/"
    path_agd  = "../data/projet_officiel/agd/"
    path_csv = "../data/projet_officiel/csv/"
    # prefix = 'A010'
    prefix = args[1]
    files_gt3x=[prefix+'_chest.gt3x', prefix+'_thigh.gt3x']
    files_csv=[prefix+'_chest.csv', prefix+'_thigh.csv']
    # files_agd=[prefix+'_chest.agd', prefix+'_thigh.agd']
    time_ini='22:00:00'
    time_end='07:59:59'
    
    filename_chest = path_gt3x + files_gt3x[0]
    filename_thigh = path_gt3x + files_gt3x[1]
    
    # filename_chest = path_agd + files_agd[0]
    # filename_thigh = path_agd + files_agd[1]
    title_name = files_gt3x[0]
   ## Read raw data and calibrate, then export to pandas data frame
    with FileReader(filename_chest) as reader:
        was_idle_sleep_mode_used = reader.idle_sleep_mode_activated
        df = reader.to_pandas()
        
        print(df)
        print(df.shape, df.size, len(df))
        print('sample_rate:', reader.info.sample_rate)
        print('info txt:', reader.info)
        
        first_sample_time = reader.info.start_date
        last_sample_time = reader.info.last_sample_time
        
        delta_time = last_sample_time - first_sample_time
        print('first time: ', first_sample_time)
        print('last_sample_time: ', last_sample_time)
        print('delta: ', delta_time)
        
        
        waveletname = 'Haar'
        dwt_level = 16
        coeff_X = pywt.wavedec(df['X'].to_numpy(), waveletname, mode='symmetric', level=dwt_level, axis=-1)
        coeff_Y = pywt.wavedec(df['Y'].to_numpy(), waveletname, mode='symmetric', level=dwt_level, axis=-1)
        coeff_Z = pywt.wavedec(df['Z'].to_numpy(), waveletname, mode='symmetric', level=dwt_level, axis=-1)
        
        df_coeff = pd.DataFrame([])
        df_coeff['X'] = coeff_X[0]
        df_coeff['Y'] = coeff_Y[0]
        df_coeff['Z'] = coeff_Z[0]
        
        plot_actigraphy(df, title_name)
        plot_actigraphy(df_coeff, title_name)
        plt.ion()
        # plt.show()
        plt.show(block=True)
        
        ''' 
        ## zero second
        # t_0s = timedelta(microseconds = 0)
        
        # date_start, time_start = ticks2datetime(reader.info.start_date//10, t_0s)
        # date_end, time_end = ticks2datetime(reader.info.last_sample_time//10, t_0s)
        
        
        # print(converted_ticks.strftime("%Y-%m-%d"))
        # print(converted_ticks.strftime("%H:%M:%S"))
        
        ## we estimate acceleration values per second
        ## applying mean 
        # sample_rate = reader.info.sample_rate
        # row_min = 0
        # row_max = num_samples
        # df_sampled = pd.DataFrame([], columns=['Date','Time','X','Y','Z'])
        
        # index_list = df.index.to_numpy() 
        # index_list = index_list.astype(int)
        # print(index_list)
        
        # date_sample=date_start
        # time_sample=time_start
        start_ticks = reader.info.start_date//10
        date_sample, time_sample = ticks2datetime(start_ticks, 0)
        print('start: ', date_sample)
        print('start: ', time_sample)
        
        # num_samples = len(df)//sample_rate
        # print(num_samples)
        
        date_list=[]
        time_list=[]
        index_list = df.index.to_numpy()
        index_list = index_list - index_list[0]
        
        list_dates, list_times = ticks2datetime64(start_ticks, index_list)
        print('dates:', len(list_dates), list_dates[0], list_dates[-1])
        print('times:', len(list_times), list_times[0], list_times[-1])
        
        df['Date'] = list_dates
        df['Time'] = list_times
        
        print(df)
        
        dates_list = df['Date'].unique().tolist()
        
        indexes_ini = []
        indexes_end = []
        
        for date0 in dates_list:
            df_ini = df.loc[(df['Date']==date0) & (df['Time']==time_ini)]
            df_end = df.loc[(df['Date']==date0) & (df['Time']==time_end)]
            indexes_ini.append(df_ini.index.values[0])
            indexes_end.append(df_end.index.values[0])
            
        # index_0 = df.index.values[0]
        
        # indexes_ini = df_ini.index.values - index_0
        # indexes_end = df_end.index.values - index_0
        
        plot_actigraphy(df, title_name)
        
        indexes_ini = (indexes_ini / (2**dwt_level)).astype(int)
        indexes_end = (indexes_end / (2**dwt_level)).astype(int) 
        
        print('indexes_ini:', indexes_ini)
        print('indexes_end:', indexes_end)
        
        plot_actigraphy(df_coeff, title_name)
        
        plt.ion()
        # plt.show()
        plt.show(block=True)

               
        df_all = pd.DataFrame([],columns=['Date','Time','X','Y','Z'])

        ## average samples per second
        dates_list = df['Date'].unique().tolist()
        for dateI in dates_list:
            print('date: ', dateI)
            df_date = df.loc[df['Date']==dateI]
            times_list = df_date['Time'].unique().tolist()
            ## 
            df_day = pd.DataFrame()
            X_mean = []
            Y_mean = []
            Z_mean = []
            
            for timeI in times_list:
                df_time = df_date.loc[df_date['Time']==timeI]
                X_mean.append(df_time['X'].mean())
                Y_mean.append(df_time['Y'].mean())
                Z_mean.append(df_time['Z'].mean())
                
            df_day['Time']=times_list
            df_day['X']=X_mean
            df_day['Y']=Y_mean
            df_day['Z']=Z_mean
            df_day['Date']=dateI
            
            # print(df_day)
            
            df_all = pd.concat([df_all, df_day], ignore_index=True)
            df_all.to_csv(files_csv[0], index=False)
            
        print(df_all)
        
        
        '''    
            
                
                
                
        
        
        # print('first: ', index_list[99], index_list[100], index_list[101])
        # print('last: ', index_list[-102], index_list[-101], index_list[-100])
        # print('delta:', index_list[-1]-index_list[0])
        # print('delta:', index_list[-2]-index_list[1])
        
        # date_sample, time_sample = ticks2datetime(start_ticks, index_list[-1])
        # print('last date: ', date_sample)
        # print('last time: ', time_sample)
        
        # print(index_list[:10])
        # for i in np.arange(num_samples):
        # for idx in index_list[:10]:
            
            # id0 = sample_rate*i
            # id1 = sample_rate*(i+1)
        
            # df_1s =  df.iloc[index_list[id0]:index_list[id1]]
            # df_1s =  df.iloc[id0:id1]
            # print(df_1s)
            # print(df_1s.size, len(df_1s), df_1s.shape)
            # print(df_1s.iloc[0])
            
            # mean_sample = df_1s.mean().to_numpy()
            # print(mean_sample)
            
            ## one second
            # date_sample, time_sample = ticks2datetime(start_ticks, idx)
            # date_sample, time_sample = ticks2datetime(idx)
            # date_list.append(date_sample)
            # time_list.append(time_sample)
            
            # df_temp = pd.DataFrame([[date_sample, time_sample, mean_sample[0],mean_sample[1],mean_sample[2]]], columns=['Date','Time','X','Y','Z'])
            # df_sampled = pd.concat([df_sampled, df_temp], ignore_index=True)
          
        # print(date_list)
        # print(time_list)
        
        # df['Date']=date_list
        # df['Time']=time_list
            
        # print(df)
        # df_sampled.plot()
        # plt.show()
        

        
        # ticks_download = reader.info.download_date
        # ticks_start = reader.info.start_date
        # ticks_stop = reader.info.stop_date
        # ticks_last_sample = reader.info.last_sample_time
        # t_zone = reader.info.timezone
        
        # date_download = datetime(1,1,1) + timedelta(microseconds = ticks_download//10)
        # date_start = datetime(1,1,1) + timedelta(microseconds = ticks_start//10)
        # date_stop = datetime(1,1,1) + timedelta(microseconds = ticks_stop//10)
        # date_last_sample = datetime(1,1,1) + timedelta(microseconds = ticks_last_sample//10)
        
        # print(date_download)
        # print(date_start)
        # print(date_stop)
        # print(date_last_sample)
        # print(t_zone)
        
        
        # ticks = df.index.to_numpy() // 10
        # print(ticks)
        # t_delta = ticks.astype('timedelta64[us]')
        # date_start=np.datetime64('0001-01-01')

        # converted_ticks = date_start + t_delta
        # list_datetime = converted_ticks.tolist()
        
        # dates=[]
        # times=[]
        # for date_long in list_datetime:
            
            ## print(type(date_long), date_long)
            # dates.append(date_long.strftime("%Y-%m-%d"))
            # times.append(date_long.strftime("%H:%M:%S.%f"))

        ## print(dates)
        ## print(times)
        
        # df['Date']=dates
        # df['Time']=times
        
        # print(df)

        
        
        
    
    
        # plot_actigraphy(df)
        # plt.show()
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
