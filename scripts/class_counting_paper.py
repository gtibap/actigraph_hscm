from datetime import datetime
from scipy import ndimage
from scipy import signal
import numpy as np
import pandas as pd
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pywt
import re
import sys



class Counting_Actigraphy:

    def __init__(self):
        # print('Seg_Actigraphy object initialization')
        self.header_location=10
        self.vec_mag  ='Vector Magnitude'
        self.incl_off ='Inclinometer Off'
        self.incl_sta ='Inclinometer Standing'
        self.incl_sit ='Inclinometer Sitting'
        self.incl_lyi ='Inclinometer Lying'
        
        self.vma_mod = 'vma_mod'
        self.vma_act = 'vma_act'
        self.vma_win = 'vma_win'
        
        self.off_mod = 'off_mod'
        self.lyi_mod = 'lyi_mod'
        self.sit_mod = 'sit_mod'
        self.sta_mod = 'sta_mod'
        
        self.off_filtered = 'off_filtered'
        self.lyi_filtered = 'lyi_filtered'
        self.sit_filtered = 'sit_filtered'
        self.sta_filtered = 'sta_filtered'
        self.sum_filtered = 'sum_filtered'
        
        self.off_act = 'off_act'
        self.lyi_act = 'lyi_act'
        self.sit_act = 'sit_act'
        self.sta_act = 'sta_act'
        
        self.dwt_vma = 'dwt_vma'
        self.dwt_off = 'dwt_off'
        self.dwt_lyi = 'dwt_lyi'
        self.dwt_sit = 'dwt_sit'
        self.dwt_sta = 'dwt_sta'
        self.dwt_sum = 'dwt_sum'
        
        self.vma_counts='vma_counts'
        self.off_counts='off_counts'
        self.lyi_counts='lyi_counts'
        self.sit_counts='sit_counts'
        self.sta_counts='sta_counts'
        self.night = 'night'
        
        self.time_ini='20:00:00'
        self.time_end='08:00:00'
        
        self.color_day = 'tab:green'
        self.color_night = 'tab:purple'
        
        self.label_time = ' Time'
        self.label_date = 'Date'
        self.time_sec = 'time_sec'
        
        self.dwt_level = 9
        self.x_ini= 120000
        self.x_end= 161500

        self.df1 = pd.DataFrame([])
        self.df_activity_indexes = pd.DataFrame([], columns=['idx_ini','idx_end','length'])
        self.df_all_nights = pd.DataFrame()
        
        self.df_inclinometers = pd.DataFrame([])
        self.df_sw_inclinometers = pd.DataFrame([])
        self.df_wt_inclinometers = pd.DataFrame([])
        self.df_mm_inclinometers = pd.DataFrame([])
        self.df_lpf_inclinometers = pd.DataFrame([])
        
        self.df_dwt_vma = pd.DataFrame([])
        self.df_nights_dwt_vma = pd.DataFrame([])

        self.min_vma = 3 # counts
        self.min_samples = 2 # min number of samples inside the window (function: rollingWindow())
        self.compliance_win = 120  # 180 min equal to 3h
        self.label_hours = '2h'
        self.arr_fig = [[] for i in range(10)]
        self.arr_axs = [[] for i in range(10)]
        
        self.list_start_end_night=[]
        self.list_start_end_night_original=[]
        self.list_arr_compl = []
        self.arr_rep = np.array([])


    def openFile(self, path, filename):
        self.path = path
        self.filename = filename
        self.df1 = pd.read_csv(self.path+self.filename, header=self.header_location, decimal=',')

        ## this is necesary for cases where datetime format is different or has repetitive values 
        with open(self.path+self.filename) as f:
            for i, line in enumerate(f):             
                if i < 10:
                    list_values = line.split()
                    if i == 2:
                        ## hh:mm:ss
                        start_time = list_values[2][:8]
                    if i == 3:
                        ## date dd/mm/yyyy
                        start_date = list_values[2][:10]
                        if '/' in start_date:
                            day, month, year = start_date.split('/')
                        elif '-' in start_date:
                            year, month, day  = start_date.split('-')
                        else:
                            print('Date format is not recognized!')
                            return 0
                        start_date = year+'-'+month+'-'+day
                    elif i == 4:
                        ## epoch period hh:mm:ss
                        epoch_period = list_values[3][:8]
                        ## epoch period in seconds
                        list_period = epoch_period.split(':')
                        delta_sec = int(list_period[0])*3600 + int(list_period[1])*60 + int(list_period[2])
                    elif i == 5:
                        ## hh:mm:ss
                        download_time = list_values[2][:8]
                    elif i == 6:
                        ## date dd/mm/yyyy
                        download_date = list_values[2][:10]
                        if '/' in download_date:
                            day, month, year = download_date.split('/')
                        elif '-' in download_date:
                            year, month, day  = download_date.split('-')
                        else:
                            print('Date format is not recognized!')
                            return 0
                        
                        download_date = year+'-'+month+'-'+day
                    else:
                        pass
                else:
                    break
            
            start_recording = start_date +' '+ start_time
            end_recording = download_date +' '+ '23:59:59'
            
            date_range_index = pd.date_range(start =start_recording, end =end_recording, freq = str(delta_sec)+'s')
            
            df_temp = date_range_index.to_frame(index=False, name='dateTime')
            df_temp = df_temp.iloc[:len(self.df1)]

            df_temp['date'] = df_temp['dateTime'].dt.date
            df_temp['time'] = df_temp['dateTime'].dt.time
            
            self.df1[self.label_date]= df_temp['date'].astype(str)
            self.df1[self.label_time]= df_temp['time'].astype(str)
            
            ## column time in seconds
            nsamples=len(self.df1)
            start=0
            end=start+(delta_sec*nsamples)
            time_sec = np.arange(start,end,delta_sec)
            
            self.df1[self.time_sec] = time_sec
            self.delta_samples = delta_sec
        
        return 0


    def vecMagCounting(self, min_value, win_size_minutes, min_samples_window):
        
        ## parameters definition: minimum vector magnitude intensity, sliding window size, and minimum number of samples in the window
        
        self.min_vma = min_value
        self.window_min = win_size_minutes
        self.min_samples = min_samples_window
        
        arr_vma = self.df1[self.vec_mag].to_numpy()
        ## we set to one any activity greater than or equal to the minimum value of counts (self.min_vma)
        arr_vma = (arr_vma >=self.min_vma).astype(int)
        ## window size: from 2 hours (original data) to the decomposition scale of dwt_level (2**dwt_level)
        
        spm = 60 ## seconds per min
        window_size = int(spm*self.window_min)
        # print(  'window size (s): ', window_size)
        ## window to average values (same weight)
        win = signal.windows.boxcar(window_size)
        
        arr_vma_mod = np.rint(signal.convolve(arr_vma, win, mode='same'))
        ## the sample is valid if the magnitude is greater than or equal to a min number of samples (self.min_samples)
        self.df1[self.vma_win] = arr_vma_mod
        self.df1[self.vma_act] = (arr_vma_mod>=self.min_samples).astype(int) 
        
        ## retrieve only data of nights; from 22h to 8h
        df_nights = self.nightsDataFrame(self.df1)
        
        list_nights = df_nights[self.night].unique().tolist()

        list_mov_night = []
        for num_night in list_nights:
            df = df_nights.loc[df_nights[self.night]==num_night]
            ## mean activity every night
            list_mov_night.append(df[self.vma_act].mean())
        
        return np.around(list_mov_night,3)
    
    
    def inclinometers_original(self):
        
        arr_date = self.df1[self.label_date].to_numpy()
        arr_time = self.df1[self.label_time].to_numpy()
         ## read inclinometers 
        arr_off = self.df1[self.incl_off].to_numpy()
        arr_lyi = self.df1[self.incl_lyi].to_numpy()
        arr_sit = self.df1[self.incl_sit].to_numpy()
        arr_sta = self.df1[self.incl_sta].to_numpy()
        
        self.df_inclinometers = pd.DataFrame()
        self.df_inclinometers[self.label_date]=arr_date
        self.df_inclinometers[self.label_time]=arr_time
        self.df_inclinometers[self.incl_off]=arr_off
        self.df_inclinometers[self.incl_lyi]=arr_lyi
        self.df_inclinometers[self.incl_sit]=arr_sit
        self.df_inclinometers[self.incl_sta]=arr_sta
        
        return 0
         
     
    def inclinometers_sliding_window(self, win_size_minutes):
        
        # self.window_min = win_size_minutes
        
        ## read inclinometers 
        arr_off = self.df1[self.incl_off].to_numpy()
        arr_lyi = self.df1[self.incl_lyi].to_numpy()
        arr_sit = self.df1[self.incl_sit].to_numpy()
        arr_sta = self.df1[self.incl_sta].to_numpy()
        
        spm = 60 ## seconds per min
        window_size = int(spm*win_size_minutes)
        # print(f'window size: {window_size}')
        ## window to average values (same weight)
        win = signal.windows.boxcar(window_size)
        
        # results convolution aproximate to the closest integer to avoid inestabilities
        coeff_off = np.rint(signal.convolve(arr_off, win, mode='same'))/window_size
        coeff_lyi = np.rint(signal.convolve(arr_lyi, win, mode='same'))/window_size
        coeff_sit = np.rint(signal.convolve(arr_sit, win, mode='same'))/window_size
        coeff_sta = np.rint(signal.convolve(arr_sta, win, mode='same'))/window_size
        
        ## pile the inclinometers resultant coefficients (level 10) and select the inclinometer with the maximum value per each sample
        coeff_stack = np.vstack((coeff_off,coeff_lyi,coeff_sit,coeff_sta))
        
        sum_coeff = np.sum(coeff_stack, axis=0)
        
        index_coeff = np.argmax(coeff_stack, axis=0)
        arr_new_off = (index_coeff==0).astype(int)
        arr_new_lyi = (index_coeff==1).astype(int)
        arr_new_sit = (index_coeff==2).astype(int)
        arr_new_sta = (index_coeff==3).astype(int)
        
        
        arr_date = self.df1[self.label_date].to_numpy()
        arr_time = self.df1[self.label_time].to_numpy()
        
        ## grouping the resultant data
        self.df_sw_inclinometers = pd.DataFrame()
        self.df_sw_inclinometers[self.label_date]=arr_date
        self.df_sw_inclinometers[self.label_time]=arr_time
        self.df_sw_inclinometers[self.off_filtered]=coeff_off
        self.df_sw_inclinometers[self.lyi_filtered]=coeff_lyi
        self.df_sw_inclinometers[self.sit_filtered]=coeff_sit
        self.df_sw_inclinometers[self.sta_filtered]=coeff_sta
        self.df_sw_inclinometers[self.sum_filtered]=sum_coeff
        self.df_sw_inclinometers[self.incl_off]=arr_new_off
        self.df_sw_inclinometers[self.incl_lyi]=arr_new_lyi
        self.df_sw_inclinometers[self.incl_sit]=arr_new_sit
        self.df_sw_inclinometers[self.incl_sta]=arr_new_sta
        
        return 0
        
    def inclinometers_wavelet_transform(self, win_size_minutes):
        
        # self.window_min = win_size_minutes
        
        ## read inclinometers 
        arr_off = self.df1[self.incl_off].to_numpy()
        arr_lyi = self.df1[self.incl_lyi].to_numpy()
        arr_sit = self.df1[self.incl_sit].to_numpy()
        arr_sta = self.df1[self.incl_sta].to_numpy()
        
        spm = 60 ## seconds per min
        window_size = int(spm*win_size_minutes)
        # print(f'window size: {window_size}')
        
        arr_date = self.df1[self.label_date].to_numpy()
        arr_time = self.df1[self.label_time].to_numpy()
        
        dwt_level=0
        
        ## subsampling according to wavelet decomposition level
        while (2**(dwt_level+1)) < window_size:
            dwt_level+=1
            arr_date=arr_date[::2]
            arr_time=arr_time[::2]
            
        print(f'dwt_level: {dwt_level}, arr_date {len(arr_date)}, arr_time {len(arr_time)}')
        
        self.dwt_level = dwt_level
        
        waveletname = 'Haar'
        
        coeff_off = pywt.wavedec(arr_off, waveletname, mode='symmetric', level=dwt_level, axis=-1)
        coeff_lyi = pywt.wavedec(arr_lyi, waveletname, mode='symmetric', level=dwt_level, axis=-1)
        coeff_sit = pywt.wavedec(arr_sit, waveletname, mode='symmetric', level=dwt_level, axis=-1)
        coeff_sta = pywt.wavedec(arr_sta, waveletname, mode='symmetric', level=dwt_level, axis=-1)
        
        print(f'coeff_off\n{len(coeff_off[0])}, {coeff_off[0].shape}')
        # , coeff_lyi {coeff_lyi.shape}, coeff_sit {coeff_sit.shape}, coeff_sta {coeff_sta.shape}')
        
        ## pile the inclinometers resultant coefficients (level 10) and select the inclinometer with the maximum value per each sample
        coeff_stack = np.vstack((coeff_off[0],coeff_lyi[0],coeff_sit[0],coeff_sta[0]))
        print(f'coeff_stack: {coeff_stack.shape}')
        
        sum_coeff = np.sum(coeff_stack, axis=0)
        
        print(f'sum_coeff {sum_coeff.shape}')
        median_value = np.median(sum_coeff)
        print(f'median_value: {median_value}')
        
        index_coeff = np.argmax(coeff_stack, axis=0)
        arr_new_off = (index_coeff==0).astype(int)
        arr_new_lyi = (index_coeff==1).astype(int)
        arr_new_sit = (index_coeff==2).astype(int)
        arr_new_sta = (index_coeff==3).astype(int)
        
        ## grouping the resultant data
        self.df_wt_inclinometers = pd.DataFrame()
        self.df_wt_inclinometers[self.label_date]=arr_date
        self.df_wt_inclinometers[self.label_time]=arr_time
        self.df_wt_inclinometers[self.off_filtered]=coeff_off[0]/median_value
        self.df_wt_inclinometers[self.lyi_filtered]=coeff_lyi[0]/median_value
        self.df_wt_inclinometers[self.sit_filtered]=coeff_sit[0]/median_value
        self.df_wt_inclinometers[self.sta_filtered]=coeff_sta[0]/median_value
        self.df_wt_inclinometers[self.sum_filtered]=sum_coeff/median_value
        self.df_wt_inclinometers[self.incl_off]=arr_new_off
        self.df_wt_inclinometers[self.incl_lyi]=arr_new_lyi
        self.df_wt_inclinometers[self.incl_sit]=arr_new_sit
        self.df_wt_inclinometers[self.incl_sta]=arr_new_sta
        
        return 0        
    
    
    def inclinometer_mat_morpho(self, win_size_minutes):
        
        spm = 60 ## seconds per min
        window_size = int(spm*win_size_minutes/2)
        
        # self.min_gap_rep = win_size_minutes
        
        arr_date = self.df1[self.label_date].to_numpy()
        arr_time = self.df1[self.label_time].to_numpy()
         
        arr_off = self.df1[self.incl_off].to_numpy()
        arr_lyi = self.df1[self.incl_lyi].to_numpy()
        arr_sit = self.df1[self.incl_sit].to_numpy()
        arr_sta = self.df1[self.incl_sta].to_numpy()
        
        arr_off_mod = self.closingOpening(arr_off,window_size)
        arr_lyi_mod = self.closingOpening(arr_lyi,window_size)
        arr_sit_mod = self.closingOpening(arr_sit,window_size)
        arr_sta_mod = self.closingOpening(arr_sta,window_size)
        
        coeff_stack = np.vstack((arr_off_mod, 
                                 arr_lyi_mod, 
                                 arr_sit_mod, 
                                 arr_sta_mod))
                                 
        print(f'coeff_stack: {coeff_stack.shape}')
        
        sum_coeff = np.sum(coeff_stack, axis=0)
        
        print(f'sum_coeff {sum_coeff.shape}')
        max_value = np.max(sum_coeff)
        print(f'max_value: {max_value}')
        
        index_coeff = np.argmax(coeff_stack, axis=0)
        arr_new_off = (index_coeff==0).astype(int)
        arr_new_lyi = (index_coeff==1).astype(int)
        arr_new_sit = (index_coeff==2).astype(int)
        arr_new_sta = (index_coeff==3).astype(int)
        
        ## grouping the resultant data
        self.df_mm_inclinometers = pd.DataFrame()
        self.df_mm_inclinometers[self.label_date]=arr_date
        self.df_mm_inclinometers[self.label_time]=arr_time
        self.df_mm_inclinometers[self.off_filtered]=arr_off_mod
        self.df_mm_inclinometers[self.lyi_filtered]=arr_lyi_mod
        self.df_mm_inclinometers[self.sit_filtered]=arr_sit_mod
        self.df_mm_inclinometers[self.sta_filtered]=arr_sta_mod
        self.df_mm_inclinometers[self.sum_filtered]=sum_coeff/max_value
        self.df_mm_inclinometers[self.incl_off]=arr_new_off
        self.df_mm_inclinometers[self.incl_lyi]=arr_new_lyi
        self.df_mm_inclinometers[self.incl_sit]=arr_new_sit
        self.df_mm_inclinometers[self.incl_sta]=arr_new_sta
        
        return 0
    
    
    def closingOpening(self, arr_inc, dist):
        ## structuring element: odd number
        gap = int((2*dist)+1)
        struct1 = np.ones(gap).astype(int)
        
        arr_clo= ndimage.binary_closing(arr_inc, structure=struct1).astype(int)
        arr_ope= ndimage.binary_opening(arr_clo, structure=struct1).astype(int)
        return arr_ope
    
    
    def inclinometers_low_pass_filter(self, win_size_minutes):
        
        arr_date = self.df1[self.label_date].to_numpy()
        arr_time = self.df1[self.label_time].to_numpy()
        
        ## read inclinometers 
        arr_off = self.df1[self.incl_off].to_numpy()
        arr_lyi = self.df1[self.incl_lyi].to_numpy()
        arr_sit = self.df1[self.incl_sit].to_numpy()
        arr_sta = self.df1[self.incl_sta].to_numpy()
        
        spm = 60 ## seconds per min
        window_size = int(spm*win_size_minutes)
        period = 2*window_size
        freq = 1/period
        print(f'lpf cut freq: {freq}')
        
        order=2
        arr_off_mod = self.filterLowPass(arr_off, freq, order)
        arr_lyi_mod = self.filterLowPass(arr_lyi, freq, order)
        arr_sit_mod = self.filterLowPass(arr_sit, freq, order)
        arr_sta_mod = self.filterLowPass(arr_sta, freq, order)
        
        coeff_stack = np.vstack((arr_off_mod, 
                                 arr_lyi_mod, 
                                 arr_sit_mod, 
                                 arr_sta_mod))
                                 
        sum_coeff = np.sum(coeff_stack, axis=0)
        
        index_coeff = np.argmax(coeff_stack, axis=0)
        arr_new_off = (index_coeff==0).astype(int)
        arr_new_lyi = (index_coeff==1).astype(int)
        arr_new_sit = (index_coeff==2).astype(int)
        arr_new_sta = (index_coeff==3).astype(int)
        
        ## grouping the resultant data
        self.df_lpf_inclinometers = pd.DataFrame()
        self.df_lpf_inclinometers[self.label_date]=arr_date
        self.df_lpf_inclinometers[self.label_time]=arr_time
        self.df_lpf_inclinometers[self.off_filtered]=arr_off_mod
        self.df_lpf_inclinometers[self.lyi_filtered]=arr_lyi_mod
        self.df_lpf_inclinometers[self.sit_filtered]=arr_sit_mod
        self.df_lpf_inclinometers[self.sta_filtered]=arr_sta_mod
        self.df_lpf_inclinometers[self.sum_filtered]=sum_coeff
        self.df_lpf_inclinometers[self.incl_off]=arr_new_off
        self.df_lpf_inclinometers[self.incl_lyi]=arr_new_lyi
        self.df_lpf_inclinometers[self.incl_sit]=arr_new_sit
        self.df_lpf_inclinometers[self.incl_sta]=arr_new_sta
        
        return self.df_lpf_inclinometers
    
    
    def filterLowPass(self, arr, fc, order):
        self.sampling_rate = 1 ## 1 Hz, 1 sample per second
        sos = signal.butter(order, fc, btype='lowpass', fs=self.sampling_rate, output='sos')
        filtered = signal.sosfiltfilt(sos, arr)
        return filtered
    
        
    def nightsDataFrame(self, df):
        
        df_all_nights = pd.DataFrame()
        dates_list = df[self.label_date].unique().tolist()
        
        id_night=1
        for date0, date1 in zip(dates_list[:-1], dates_list[1:]):
            ## from 22:00:00 to 23:59:59
            df_nightA = df.loc[(df[self.label_date]==date0) & (df[self.label_time] >= self.time_ini)]
            ## from 00:00:00 to 07:59:59
            df_nightB = df.loc[(df[self.label_date]== date1) & (df[self.label_time] <=self.time_end)] 
            
            df_night = pd.concat([df_nightA, df_nightB], ignore_index=True)
            df_night[self.night] = id_night
            
            df_all_nights = pd.concat([df_all_nights, df_night], ignore_index=True)
            
            id_start=df_nightA.index.values[0]
            id_end=df_nightB.index.values[-1]
            
            self.list_start_end_night_original.append([id_start,id_end])
            
            id_night+=1
            
        return df_all_nights
 
    
    def nightCounts(self, sel):
        
        if sel=='sw':
            self.df_inclinometers = self.df_sw_inclinometers
        elif sel=='wt':
            self.df_inclinometers = self.df_wt_inclinometers
        elif sel=='mm':
            self.df_inclinometers = self.df_mm_inclinometers
        elif sel=='lpf':
            self.df_inclinometers = self.df_lpf_inclinometers
        else:
            ## original data; no changes
            pass

        
        ## from 22:00:00 until 07:59:59 (next day)
        self.list_start_end_night = []
        self.list_arr_compl = []
        self.df_all_nights = pd.DataFrame()
        dates_list = self.df_inclinometers[self.label_date].unique().tolist()
        
        id_night=1
        for date0, date1 in zip(dates_list[:-1], dates_list[1:]):
            
            ## from 22:00:00 to 23:59:59
            df_nightA = self.df_inclinometers.loc[(self.df_inclinometers[self.label_date]==date0) & (self.df_inclinometers[self.label_time] >= self.time_ini)]
            # print(df_nightA)
            ## from 00:00:00 to 07:59:59
            df_nightB = self.df_inclinometers.loc[(self.df_inclinometers[self.label_date]== date1) & (self.df_inclinometers[self.label_time] <=self.time_end)] 
            
            df_night = pd.concat([df_nightA, df_nightB], ignore_index=True)
            
            # print(f'indexes: {df_nightA.index.values[0]}:{df_nightB.index.values[-1]}')
            id_start=df_nightA.index.values[0]
            id_end=df_nightB.index.values[-1]
            
            ## we use this info to plot vertical lines to indicate begining and end of each night
            self.list_start_end_night.append([id_start,id_end])
            
            len_night = len(df_night)
            # normalized number of counts per inclinometer
            
            counts_off=np.round(100*df_night[self.incl_off].mean(),2)
            counts_lyi=np.round(100*df_night[self.incl_lyi].mean(),2)
            counts_sit=np.round(100*df_night[self.incl_sit].mean(),2)
            counts_sta=np.round(100*df_night[self.incl_sta].mean(),2)
            
            ## counting number of repositioning 
            arr_rep, repos_labels, repos_data  = self.counting_repositioning(df_night)
            # print(f'repositioning {repos_labels[-1]}: {repos_data[-1]}')
            
            ## compliance factor estimation
            arr_compl, arr_compl_bin, compliance_factor = self.complianceEstimation(arr_rep)
            self.list_arr_compl.append(arr_compl.tolist())
            
            ## time period of each night in seconds subtracting first time and data from last time and date
            duration = self.nightDuration(df_night.iloc[0][self.label_date],
                                          df_night.iloc[-1][self.label_date],
                                          df_night.iloc[0][self.label_time],
                                          df_night.iloc[-1][self.label_time])
                                          
            counts_data = [id_night,id_start,id_end] + repos_data + [counts_off, counts_lyi, counts_sit, counts_sta, compliance_factor, duration]
            counts_labels = ['night','id_ini','id_end'] + repos_labels + ['time_off(%)','time_lyi(%)','time_sit(%)','time_sta(%)','compliance(%)','night_duration(s)']
           
            df_counts_night = pd.DataFrame([counts_data], columns=counts_labels)
            self.df_all_nights = pd.concat([self.df_all_nights, df_counts_night], ignore_index=True)
            
            id_night+=1
        
        return 0
    
    
    def complianceEstimation(self, arr_rep):
        
        spm = 60 ## seconds per min
        window_size = int(spm*self.compliance_win)
        ## window to average values (same weight)
        win = signal.windows.boxcar(window_size)
        
        # results convolution aproximate to the closest integer to avoid inestabilities
        coeff_rep = np.rint(signal.convolve(arr_rep, win, mode='full',))
        
        coeff_rep_act = (coeff_rep>=1).astype(int) 
        
        return  coeff_rep, coeff_rep_act, np.round(100*coeff_rep_act.mean(),2) 
        
    
    def nightDuration(self, date_ini, date_end, time_ini, time_end):
        
        date_ini = np.array(date_ini.split('-')).astype(int)
        date_end = np.array(date_end.split('-')).astype(int)
        
        time_ini = np.array(time_ini.split(':')).astype(int)
        time_end = np.array(time_end.split(':')).astype(int)
        
        ## datetime (yy,mm,dd,hh,mm,ss,us)
        time_ini = datetime(date_ini[0],date_ini[1],date_ini[2],time_ini[0],time_ini[1],time_ini[2],0)
        time_end = datetime(date_end[0],date_end[1],date_end[2],time_end[0],time_end[1],time_end[2],0)
        
        time_dif = time_end - time_ini
        
        return time_dif.total_seconds()
        
        
    def counting_repositioning(self, df):
        
        arr_off = df[self.incl_off].to_numpy()
        arr_lyi = df[self.incl_lyi].to_numpy()
        arr_sit = df[self.incl_sit].to_numpy()
        arr_sta = df[self.incl_sta].to_numpy()
        
        arr_off_lyi, off_lyi=self.counting_per_two_incl(arr_off, arr_lyi)
        arr_off_sit, off_sit=self.counting_per_two_incl(arr_off, arr_sit)
        arr_off_sta, off_sta=self.counting_per_two_incl(arr_off, arr_sta)
        
        arr_lyi_off, lyi_off=self.counting_per_two_incl(arr_lyi, arr_off)
        arr_lyi_sit, lyi_sit=self.counting_per_two_incl(arr_lyi, arr_sit)
        arr_lyi_sta, lyi_sta=self.counting_per_two_incl(arr_lyi, arr_sta)
        
        arr_sit_off, sit_off=self.counting_per_two_incl(arr_sit, arr_off)
        arr_sit_lyi, sit_lyi=self.counting_per_two_incl(arr_sit, arr_lyi)
        arr_sit_sta, sit_sta=self.counting_per_two_incl(arr_sit, arr_sta)
        
        arr_sta_off, sta_off=self.counting_per_two_incl(arr_sta, arr_off)
        arr_sta_lyi, sta_lyi=self.counting_per_two_incl(arr_sta, arr_lyi)
        arr_sta_sit, sta_sit=self.counting_per_two_incl(arr_sta, arr_sit)
    
        ## array of repositionings (logical or |)
        arr_rep =(arr_off_lyi | arr_lyi_off | arr_sit_off | arr_sta_off |
                  arr_off_sit | arr_lyi_sit | arr_sit_lyi | arr_sta_lyi |
                  arr_off_sta | arr_lyi_sta | arr_sit_sta | arr_sta_sit)
    
        ## number of repositionings
        num_rep = np.sum(off_lyi + off_sit + off_sta + 
                         lyi_off + lyi_sit + lyi_sta +
                         sit_off + sit_lyi + sit_sta +
                         sta_off + sta_lyi + sta_sit)
    
        return arr_rep, ['off_lyi', 'off_sit', 'off_sta', 'lyi_off', 'lyi_sit', 'lyi_sta', 'sit_off', 'sit_lyi', 'sit_sta', 'sta_off', 'sta_lyi', 'sta_sit', 'rep_total'], [off_lyi, off_sit, off_sta, lyi_off, lyi_sit, lyi_sta, sit_off, sit_lyi, sit_sta, sta_off, sta_lyi, sta_sit, num_rep]
        

    def counting_per_two_incl(self, arr0, arr1):
        arr = (arr0[:-1] == arr1[1:]) & (arr0[:-1]==1)
        return arr, np.sum(arr)
    
    
    def compliance_full(self, sel, win_size_minutes, filename, save_flag):
        
        if sel=='sw':
            self.df_inclinometers = self.df_sw_inclinometers
        elif sel=='wt':
            self.df_inclinometers = self.df_wt_inclinometers
        elif sel=='mm':
            self.df_inclinometers = self.df_mm_inclinometers
        elif sel=='lpf':
            self.df_inclinometers = self.df_lpf_inclinometers
        else:
            ## original data; no changes
            pass
        
        ## counting number of repositioning 
        arr_rep, repos_labels, repos_data  = self.counting_repositioning(self.df_inclinometers)
        # print(f'repositioning {repos_labels[-1]}: {repos_data[-1]}')
        
        ## compliance factor estimation
        arr_compl, arr_compl_bin, compliance_factor = self.complianceEstimation(arr_rep)
        
        x_ini = self.x_ini
        x_end = self.x_end
        compliance_factor = np.round(100*arr_compl_bin[x_ini:x_end].mean(),2)
        print(f'compliance_factor: {compliance_factor}')
        
        ## sliding window to average results of compliance
        # win_size_minutes = 60 ## min (1 hour)
        # arr_compl_curve = self.vm_sWin_groups(arr_compl_bin, win_size_minutes)
        # self.plot_measure_compl(arr_compl_bin, arr_compl_curve)
        
        ## smoothing appling a low pass filter
        # win_size_minutes=15
        # spm = 60 ## seconds per min
        # window_size = int(spm*win_size_minutes)
        # period = 2*window_size
        # freq = 1/period
        # order = 1
        # print(f'lpf cut freq: {freq}')
        # arr_compl = self.filterLowPass(arr_compl, freq, order)
        
        self.plot_compliance(arr_compl, filename, save_flag)
        
        return 0
        
    def plot_measure_compl(self, arr_bin, arr_curve):
        
        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(12, 1), gridspec_kw={'width_ratios': [3, 1]})
        fig.canvas.mpl_connect('key_press_event', self.on_press)
        fig.canvas.draw()
        
        x_ini = self.x_ini
        x_end = self.x_end
        
        ax[0].plot(arr_bin)
        ax[0].plot(arr_curve)
        
        ax[1].boxplot(arr_curve[x_ini:x_end], showfliers=False)

        ax[0].set_xlim(x_ini,x_end)
        ax[-1].xaxis.set_major_formatter(mticker.FuncFormatter(self.update_ticks_x))
        
        y_ini= -0.2
        y_end=  1.2
        ax[0].set_ylim(y_ini,y_end)
        
        
        return 0
        
    
    
    
    def on_press(self, event):
        # print('press', event.key)
        sys.stdout.flush()
        
        if event.key == 'x':
            plt.close('all')
        else:
            pass
         
    
    def update_ticks_x(self, x, pos):
        x = np.round(float(x)/3600, 1)
        return x
        
    def update_ticks_x_wt(self, x, pos):
        x = np.round(((2**self.dwt_level)*float(x))/3600, 1)
        return x
    
    
    def plotActigraphyNormal(self, filename, save_flag, title):
        
        fig, ax = plt.subplots(nrows=5, ncols=1, sharex=True, figsize=(12, 4), gridspec_kw={'height_ratios': [2, 1, 1, 1, 1]})
        fig.canvas.mpl_connect('key_press_event', self.on_press)
        fig.canvas.draw()
        
        arr_vec_mag  = self.df1[self.vec_mag].to_numpy()
        arr_incl_off = self.df1[self.incl_off].to_numpy()
        arr_incl_lyi = self.df1[self.incl_lyi].to_numpy()
        arr_incl_sit = self.df1[self.incl_sit].to_numpy()
        arr_incl_sta = self.df1[self.incl_sta].to_numpy()
        
        x_ini = self.x_ini
        x_end = self.x_end

        ax[0].set_xlim(x_ini,x_end)
        ax[-1].xaxis.set_major_formatter(mticker.FuncFormatter(self.update_ticks_x))
        
        y_ini= -10
        y_end=  150
        ax[0].set_ylim(y_ini,y_end)
        y_ini= -0.2
        y_end=  1.2
        ax[1].set_ylim(y_ini,y_end)
        ax[2].set_ylim(y_ini,y_end)
        ax[3].set_ylim(y_ini,y_end)
        ax[4].set_ylim(y_ini,y_end)
        
        # self.plotVerticalLines(ax, self.list_start_end_night)
        
        ax[0].plot(arr_vec_mag, color='tab:purple', label='VM (counts)')
        ax[0].legend()
        ax[1].plot(arr_incl_off, color='tab:blue')
        ax[2].plot(arr_incl_lyi, color='tab:orange')
        ax[3].plot(arr_incl_sit, color='tab:green')
        ax[4].plot(arr_incl_sta, color='tab:red')

        # font = {'fontname':'Arial'}
        # ax[0].set_title(self.filename)
        # ax[0].set_ylabel('v.m.')
        ax[1].set_ylabel('off')
        ax[2].set_ylabel('lyi')
        ax[3].set_ylabel('sit')
        ax[4].set_ylabel('sta')
        ax[-1].set_xlabel('time (h)')
        
        fig.suptitle(title)
        
        if save_flag:
            fig.savefig(filename, bbox_inches='tight')
        else:
            pass
        
        return 0

     
    def plotActigraphy(self):
        self.arr_fig[0], self.arr_axs[0] = plt.subplots(nrows=5, ncols=1, sharex=True)
        self.plotWithColors(self.arr_fig[0], self.arr_axs[0],signals=0)
        
        self.arr_axs[0][0].set_title(self.filename)
        self.arr_axs[0][0].set_ylabel('v.m.')
        self.arr_axs[0][1].set_ylabel('off')
        self.arr_axs[0][2].set_ylabel('lyi')
        self.arr_axs[0][3].set_ylabel('sit')
        self.arr_axs[0][4].set_ylabel('sta')
        self.arr_axs[0][4].set_xlabel('time (s)')
        
        # x_ini=100000
        # x_end=200000
        # x_ini= 60000
        # x_end=160000
        # ax[0].set_xlim(x_ini,x_end)
        # ax[0].set_ylim(0,400)
        
        return 0
        
    def plotActigraphyMod(self):
        self.arr_fig[1], self.arr_axs[1] = plt.subplots(nrows=5, ncols=1, sharex=True)
        self.plotWithColors(self.arr_fig[1], self.arr_axs[1],signals=1)
        
        self.arr_axs[1][0].set_title(self.filename)
        self.arr_axs[1][0].set_ylabel('v.m.')
        self.arr_axs[1][1].set_ylabel('off')
        self.arr_axs[1][2].set_ylabel('lyi')
        self.arr_axs[1][3].set_ylabel('sit')
        self.arr_axs[1][4].set_ylabel('sta')
        self.arr_axs[1][4].set_xlabel('time (s)')
        
        # x_ini=100000
        # x_end=200000
        x_ini= 60000
        x_end=160000
        ax[0].set_xlim(x_ini,x_end)
        # ax[0].set_ylim(0,400)
        
        return 0
    
    def plotVM(self):
        
        fig_vm, ax_vm = plt.subplots(nrows=2, ncols=1)
        # print(f'ax_vm: {ax_vm.shape}, {type(ax_vm)}')
        self.plotWithColors(fig_vm, ax_vm, signals=0)
        
        ax_vm[0].set_xlabel('time (s)')
        ax_vm[0].set_ylabel('counts')
        
        return 0
        
    def plotVM_temp(self, arr):
        
        fig_vm, ax_vm = plt.subplots(nrows=2, ncols=1, sharex=True)
        # print(f'ax_vm: {ax_vm.shape}, {type(ax_vm)}')
        self.plotWithColors(fig_vm, ax_vm, signals=0)
        
        ax_vm[1].plot(arr)
        
        ax_vm[-1].set_xlabel('time (s)')
        ax_vm[0].set_ylabel('counts')
        
        return 0

    def plotWithColors(self,fig,ax,signals):
        
        fig.canvas.mpl_connect('key_press_event', self.on_press)
        
        for i in np.arange(len(ax)):
            ax[i].cla()
        
        dates_list = self.df1[self.label_date].unique().tolist()
        
        # print(self.filename,' dates: ',dates_list)
        for date in dates_list:
            df_date = self.df1.loc[self.df1[self.label_date]== date]

            ## from 00:00:00 to 07:59:59
            df_segment = df_date.loc[df_date[self.label_time]<=self.time_end]
            self.plotSignals(fig, ax, df_segment, self.color_night,signals)

            ## from 08:00:00 to 21:59:59
            df_segment = df_date.loc[(df_date[self.label_time] > self.time_end) & (df_date[self.label_time] <= self.time_ini)]
            self.plotSignals(fig, ax, df_segment, self.color_day,signals)
            
            ## from 22:00:00 to 23:59:59
            df_segment = df_date.loc[df_date[self.label_time] > self.time_ini]
            self.plotSignals(fig, ax, df_segment, self.color_night,signals)
        
        return 0
            

    def plotSignals(self,fig,ax,df,cr,signals):
        
        x_values = df.index.tolist()
        
        if len(ax)==2:
            ax[0].plot(x_values, df[self.vec_mag].to_numpy(), color=cr)
        else:
            if signals==0:
                ax[0].plot(x_values, df[self.vec_mag].to_numpy(), color=cr)
                
                ax[1].plot(x_values, df[self.incl_off].to_numpy(), color=cr)
                ax[2].plot(x_values, df[self.incl_lyi].to_numpy(), color=cr)
                ax[3].plot(x_values, df[self.incl_sit].to_numpy(), color=cr)
                ax[4].plot(x_values, df[self.incl_sta].to_numpy(), color=cr)
            elif signals==1:
                ax[0].plot(x_values, df[self.vma_mod].to_numpy(), color=cr)
                
                ax[1].plot(x_values, df[self.off_mod].to_numpy(), color=cr)
                ax[2].plot(x_values, df[self.lyi_mod].to_numpy(), color=cr)
                ax[3].plot(x_values, df[self.sit_mod].to_numpy(), color=cr)
                ax[4].plot(x_values, df[self.sta_mod].to_numpy(), color=cr)
            else:
                pass
        
        return 0
    
    
    def plot_compliance(self, arr, filename, save_flag):
        
        fig, axarr = plt.subplots(nrows=1, ncols=1, sharex=True, sharey=True, figsize=(10, 2))
        fig.canvas.mpl_connect('key_press_event', self.on_press)
        
        # x_ini= 120000
        # x_end= 161500
        x_ini = self.x_ini
        x_end = self.x_end
        
        axarr.set_xlim(x_ini,x_end)
        axarr.xaxis.set_major_formatter(mticker.FuncFormatter(self.update_ticks_x))
        title='Low Pass Filter'
        
        indices_vertical_lines = self.list_start_end_night        
        # self.plotVerticalLines(axarr, indices_vertical_lines)
        
        axarr.axhline(y = 1, color = 'tab:gray', linewidth=2, linestyle = 'dashed', alpha=0.5)
        axarr.plot(arr, color='tab:blue')
        
        
    
        y_ini= -0.5
        y_end=  6.5
        
        y_t = [1, 3, 5]
        
        axarr.set_ylim(y_ini,y_end)
        plt.yticks(y_t, y_t)
        
        font = {'fontname':'DejaVu Sans'}
        axarr.set_xlabel('time [h]', **font)
        # axarr.set_ylabel(f'compliance [p.c./{self.label_hours}]', **font)
        axarr.set_ylabel(f'posture\nchanging rate', **font)
        
        if save_flag:
            fig.savefig(filename, bbox_inches='tight')
        else:
            pass
        
        
        return 0
         
    
    def plot_Inclinometers(self, sel, filename, save_flag):
        
        fig, axarr = plt.subplots(nrows=4, ncols=1, sharex=True, sharey=True, figsize=(10, 2))
        fig.canvas.mpl_connect('key_press_event', self.on_press)
        
        # x_ini= 120000
        # x_end= 161500
        x_ini = self.x_ini
        x_end = self.x_end
        
        if sel=='sw':
            self.df_inclinometers = self.df_sw_inclinometers
            x_ini=x_ini
            x_end=x_end
            axarr[0].set_xlim(x_ini,x_end)
            axarr[-1].xaxis.set_major_formatter(mticker.FuncFormatter(self.update_ticks_x))
            title='Sliding Windows'
            
        elif sel=='wt':
            scale_wt = 2**self.dwt_level
            self.df_inclinometers = self.df_wt_inclinometers
            x_ini=x_ini/scale_wt
            x_end=x_end/scale_wt
            axarr[0].set_xlim(x_ini,x_end)
            axarr[-1].xaxis.set_major_formatter(mticker.FuncFormatter(self.update_ticks_x_wt))
            # print(f'x_ini {x_ini}, x_end {x_end}')
            title='Discrete Wavelet Transform'

            # indices_vertical_lines = np.array(self.list_start_end_night)/(2**self.dwt_level)
            # indices_vertical_lines = np.array(self.list_start_end_night)
        elif sel=='mm':
            self.df_inclinometers = self.df_mm_inclinometers
            x_ini=x_ini
            x_end=x_end
            axarr[0].set_xlim(x_ini,x_end)
            axarr[-1].xaxis.set_major_formatter(mticker.FuncFormatter(self.update_ticks_x))
            title='Mathematical Morphology'
            
            # indices_vertical_lines = self.list_start_end_night
        else:
            self.df_inclinometers = self.df_lpf_inclinometers
            x_ini=x_ini
            x_end=x_end
            axarr[0].set_xlim(x_ini,x_end)
            axarr[-1].xaxis.set_major_formatter(mticker.FuncFormatter(self.update_ticks_x))
            title='Low Pass Filter'

            # indices_vertical_lines = self.list_start_end_night
            
        arr_dwt  = np.empty((5, 0)).tolist()
        arr_incl = np.empty((4, 0)).tolist()
        
        arr_dwt[0] = self.df_inclinometers[self.off_filtered].to_numpy()
        arr_dwt[1] = self.df_inclinometers[self.lyi_filtered].to_numpy()
        arr_dwt[2] = self.df_inclinometers[self.sit_filtered].to_numpy()
        arr_dwt[3] = self.df_inclinometers[self.sta_filtered].to_numpy()
        arr_dwt[4] = self.df_inclinometers[self.sum_filtered].to_numpy()
        
        arr_incl[0] =self.df_inclinometers[self.incl_off].to_numpy()
        arr_incl[1] =self.df_inclinometers[self.incl_lyi].to_numpy()
        arr_incl[2] =self.df_inclinometers[self.incl_sit].to_numpy()
        arr_incl[3] =self.df_inclinometers[self.incl_sta].to_numpy()
        
        indices_vertical_lines = self.list_start_end_night        
        # self.plotVerticalLines(axarr, indices_vertical_lines)
        
        axarr[0].plot(arr_dwt[0], color='tab:blue')
        axarr[1].plot(arr_dwt[1], color='tab:orange')
        axarr[2].plot(arr_dwt[2], color='tab:green')
        axarr[3].plot(arr_dwt[3], color='tab:red')
        # axarr[4].plot(arr_dwt[4], color='tab:brown')
        
        ## range x and y axes
        
        y_ini= -0.1
        y_end=  1.2
        axarr[0].set_ylim(y_ini,y_end)
        
        # axarr[0].plot(arr_incl[0], color='tab:blue')
        # axarr[1].plot(arr_incl[1], color='tab:orange')
        # axarr[2].plot(arr_incl[2], color='tab:green')
        # axarr[3].plot(arr_incl[3], color='tab:red')

        # print(f'plot {len(arr_incl[0])}, {len(self.arr_rep)}')
        
        # axarr[5].plot(self.arr_rep, color='tab:blue')
        
        # x_ini= 60000
        # x_end=160000
        # axarr[0].set_xlim(x_ini,x_end)
        
        font = {'fontname':'DejaVu Sans'}
        # ax[0].set_title(self.filename)
        axarr[0].set_ylabel('off', **font)
        axarr[1].set_ylabel('lyi', **font)
        axarr[2].set_ylabel('sit', **font)
        axarr[3].set_ylabel('sta', **font)
        axarr[3].set_xlabel('time (h)', **font)
        
        # axarr[0].set_title(self.filename, loc='left')
        # axarr[0].set_ylabel('off')
        # axarr[1].set_ylabel('lyi')
        # axarr[2].set_ylabel('sit')
        # axarr[3].set_ylabel('sta')
        # axarr[4].set_ylabel('sum')
        # axarr[4].set_ylabel('rep.')
        # axarr[5].set_ylabel('rep.2')
        axarr[-1].set_xlabel('time (h)')
        
        # fig.suptitle(title)
        if save_flag:
            fig.savefig(filename, bbox_inches='tight')
        else:
            pass
        
        return 0
        
    def plotDWTInclinometers(self):
        
        arr_dwt  = np.empty((5, 0)).tolist()
        arr_incl = np.empty((4, 0)).tolist()
        
        arr_dwt[0] = self.df_inclinometers[self.dwt_off].to_numpy()
        arr_dwt[1] = self.df_inclinometers[self.dwt_lyi].to_numpy()
        arr_dwt[2] = self.df_inclinometers[self.dwt_sit].to_numpy()
        arr_dwt[3] = self.df_inclinometers[self.dwt_sta].to_numpy()
        arr_dwt[4] = self.df_inclinometers[self.dwt_sum].to_numpy()
        
        arr_incl[0] = self.df_inclinometers[self.incl_off].to_numpy()
        arr_incl[1] = self.df_inclinometers[self.incl_lyi].to_numpy()
        arr_incl[2] = self.df_inclinometers[self.incl_sit].to_numpy()
        arr_incl[3] = self.df_inclinometers[self.incl_sta].to_numpy()
        
        fig, axarr = plt.subplots(nrows=5, ncols=1, sharex=True, sharey=True)
        fig.canvas.mpl_connect('key_press_event', self.on_press)
        
        self.plotVerticalLines(axarr, self.list_start_end_night)
        
        axarr[0].plot(arr_dwt[0], color='tab:blue')
        axarr[1].plot(arr_dwt[1], color='tab:orange')
        axarr[2].plot(arr_dwt[2], color='tab:green')
        axarr[3].plot(arr_dwt[3], color='tab:red')
        axarr[4].plot(arr_dwt[4], color='tab:brown')
        
        # axarr[0].plot(arr_incl[0], color='tab:blue')
        # axarr[1].plot(arr_incl[1], color='tab:orange')
        # axarr[2].plot(arr_incl[2], color='tab:green')
        # axarr[3].plot(arr_incl[3], color='tab:red')

        # print(f'plot {len(arr_incl[0])}, {len(self.arr_rep)}')
        
        # axarr[5].plot(self.arr_rep, color='tab:blue')
        
        # x_ini= 60000
        # x_end=160000
        # axarr[0].set_xlim(x_ini,x_end)
        
        x_ini= 120000
        x_end= 161500
        axarr[0].set_xlim(x_ini,x_end)
        axarr[-1].xaxis.set_major_formatter(mticker.FuncFormatter(self.update_ticks_x))
        
        y_ini= -0.1
        y_end=  1.2
        axarr[0].set_ylim(y_ini,y_end)
        
        # axarr[0].set_title(self.filename, loc='left')
        axarr[0].set_ylabel('off')
        axarr[1].set_ylabel('lyi')
        axarr[2].set_ylabel('sit')
        axarr[3].set_ylabel('sta')
        axarr[4].set_ylabel('sum')
        # axarr[4].set_ylabel('rep.')
        # axarr[5].set_ylabel('rep.2')
        axarr[-1].set_xlabel('time (h)')
        
        return 0
        
    def plotPosChanging(self, sel, filename, save_flag):
        
        fig, axarr = plt.subplots(figsize=(15, 2))
        fig.canvas.mpl_connect('key_press_event', self.on_press)
        
        x_ini = self.x_ini
        x_end = self.x_end
        
        if sel=='original':
            axarr.set_xlim(x_ini,x_end)
            axarr.xaxis.set_major_formatter(mticker.FuncFormatter(self.update_ticks_x))
            title='Original'
        
        elif sel=='sw':
            self.df_inclinometers = self.df_sw_inclinometers
            axarr.set_xlim(x_ini,x_end)
            axarr.xaxis.set_major_formatter(mticker.FuncFormatter(self.update_ticks_x))
            title='Sliding Windows'
            
        elif sel=='wt':
            scale_wt = 2**self.dwt_level
            self.df_inclinometers = self.df_wt_inclinometers
            x_ini=x_ini/scale_wt
            x_end=x_end/scale_wt
            axarr.set_xlim(x_ini,x_end)
            axarr.xaxis.set_major_formatter(mticker.FuncFormatter(self.update_ticks_x_wt))
            # print(f'x_ini {x_ini}, x_end {x_end}')
            title='Discrete Wavelet Transform'

            # indices_vertical_lines = np.array(self.list_start_end_night)/(2**self.dwt_level)
            # indices_vertical_lines = np.array(self.list_start_end_night)
        elif sel=='mm':
            self.df_inclinometers = self.df_mm_inclinometers
            axarr.set_xlim(x_ini,x_end)
            axarr.xaxis.set_major_formatter(mticker.FuncFormatter(self.update_ticks_x))
            title='Mathematical Morphology'
            
            # indices_vertical_lines = self.list_start_end_night
        else:
            print(f'low pass filter option selected.')
            self.df_inclinometers = self.df_lpf_inclinometers
            axarr.set_xlim(x_ini,x_end)
            axarr.xaxis.set_major_formatter(mticker.FuncFormatter(self.update_ticks_x))
            title='Low Pass Filter'
        
        arr_incl = np.empty((4, 0)).tolist()
        
        arr_incl[0] = self.df_inclinometers[self.incl_off].to_numpy()
        arr_incl[1] = self.df_inclinometers[self.incl_lyi].to_numpy()
        arr_incl[2] = self.df_inclinometers[self.incl_sit].to_numpy()
        arr_incl[3] = self.df_inclinometers[self.incl_sta].to_numpy()
        
       # fig, axarr = plt.subplots(nrows=4, ncols=1, sharex=True, sharey=True)
        # cm = 1/2.54  # centimeters in inches figsize=(15*cm, 5*cm)
        
        # fig.tight_layout()
        
        # self.plotVerticalLines(axarr, self.list_start_end_night)
        
        # axarr.plot(arr_incl[0], color='tab:blue')
        # axarr.plot(arr_incl[1], color='tab:orange')
        # axarr.plot(arr_incl[2], color='tab:green')
        # axarr.plot(arr_incl[3], color='tab:red')
        
        x = np.arange(len(arr_incl[0]))
        axarr.fill_between(x, 0, arr_incl[0], facecolor='tab:blue',   edgecolor="black", alpha=0.5, interpolate=True, hatch='.')
        axarr.fill_between(x, 0, arr_incl[1], facecolor='tab:orange', edgecolor="black", alpha=0.5, interpolate=True, hatch='\\')
        axarr.fill_between(x, 0, arr_incl[2], facecolor='tab:green',  edgecolor="black", alpha=0.5, interpolate=True, hatch='o')
        axarr.fill_between(x, 0, arr_incl[3], facecolor='tab:red',    edgecolor="black", alpha=0.5, interpolate=True, hatch='/')
        
        
        # print(f'plot {len(arr_incl[0])}, {len(self.arr_rep)}')
        
        # axarr[5].plot(self.arr_rep, color='tab:blue')
        
        # x_ini= 60000
        # x_end=160000
        # axarr.set_xlim(x_ini,x_end)
        
        y_ini= -0.1
        y_end=  1.1
        axarr.set_ylim(y_ini,y_end)
        
        # axarr.set_title(title)
        # axarr[0].set_ylabel('off')
        # axarr[1].set_ylabel('lyi')
        # axarr[2].set_ylabel('sit')
        # axarr[3].set_ylabel('sta')
        # axarr[4].set_ylabel('rep.')
        # axarr[5].set_ylabel('rep.2')
        axarr.set_xlabel('time (h)')
        
        # c = mpatches.Circle((0.5, 0.5), 0.25, facecolor="green",
                    # edgecolor="red", linewidth=3)
        # ax.add_patch(c)
        # ax.legend([c], ["An ellipse, not a rectangle"],
          # handler_map={mpatches.Circle: HandlerEllipse()})
        
        off_patch = mpatches.Patch(facecolor='tab:blue', edgecolor="black", label='off', alpha=0.5, hatch='.')
        lyi_patch = mpatches.Patch(facecolor='tab:orange', edgecolor="black", label='lyi', alpha=0.5,  hatch='\\')
        sit_patch = mpatches.Patch(facecolor='tab:green', edgecolor="black", label='sit', alpha=0.5, hatch='o')
        sta_patch = mpatches.Patch(facecolor='tab:red', edgecolor="black", label='sta', alpha=0.5, hatch='/')
        # red_patch = mpatches.Patch(color='red', label='The red data')
        # axarr.legend(handles=[red_patch], bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
        # fig.legend(handles=[red_patch], loc='outside upper right')
        # fig.legend(handles=[off_patch,lyi_patch,sit_patch,sta_patch], loc='outside right')
        fig.legend(handles=[off_patch,lyi_patch,sit_patch,sta_patch], loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=4, fancybox=True, shadow=True)
        
        plt.tick_params(left = False, right = False, labelleft = False, labelbottom = True, bottom = True)
        
        if save_flag:
            fig.savefig(filename, bbox_inches='tight')
        else:
            pass
        
        return 0
    
    
    def plotVerticalLines(self, axarr, list_start_end_night):
        
        arr_indexes = np.array(list_start_end_night)
        indexes_ini = arr_indexes[:,0]
        indexes_end = arr_indexes[:,1]
        
        # print(f'type(axarr): {type(axarr)}')
        if type(axarr).__module__ == np.__name__:
            num_subplots = len(axarr)
            print(f'num_subplots: {num_subplots}')
            ## vertical lines for 22h00
            for idx in indexes_ini:
                for i in np.arange(num_subplots):
                    axarr[i].axvline(x = idx, color = 'tab:purple', linewidth=2)
            
            ## vertical lines for 8h00
            for idx in indexes_end:
                for i in np.arange(num_subplots):
                    axarr[i].axvline(x = idx, color = 'tab:olive', linewidth=2)
        else:
            ## vertical lines for 22h00
            for idx in indexes_ini:
                axarr.axvline(x = idx, color = 'tab:purple', linewidth=2)
            
            ## vertical lines for 8h00
            for idx in indexes_end:
                axarr.axvline(x = idx, color = 'tab:olive', linewidth=2)
            
        return 0
    
    
    def plotVM_2(self, filename, save_flag, title):
       
##        fig_vm, ax_vm = plt.subplots(nrows=2, ncols=1,figsize=(10, 2))
        fig, ax = plt.subplots(nrows=4, ncols=1, sharex=True, figsize=(10, 3), gridspec_kw={'height_ratios': [2, 1, 1, 1,]})
        
        # fig2, ax2 = plt.subplots(nrows=3, ncols=2, figsize=(10, 3))
        fig2 = plt.figure(figsize=(10, 3))
        gs = fig2.add_gridspec(4,2)
        ax0 = fig2.add_subplot(gs[0, 0])
        ax1 = fig2.add_subplot(gs[1, 0])
        ax2 = fig2.add_subplot(gs[2, 0])
        ax3 = fig2.add_subplot(gs[3, 0])
        ax4 = fig2.add_subplot(gs[:, 1])

        
        # the next two lines are to convert ax to an one-dimensional array; making iteration of ax generic in case more subplots were required
        
        ax = np.array(ax)
        ax = ax.reshape(-1)
        
        # ax2 = np.array(ax2)
        # ax2 = ax2.reshape(-1)
        
        # print(f'ax_vm: {ax_vm.shape}, {type(ax_vm)}')
##        self.plotWithColors(fig_vm, ax_vm, signals=0)

        fig.canvas.mpl_connect('key_press_event', self.on_press)
        fig.canvas.draw()
        
        fig2.canvas.mpl_connect('key_press_event', self.on_press)
        fig2.canvas.draw()
       
        arr_vec_mag = self.df1[self.vec_mag].to_numpy()
        arr_sw_001min = self.vm_slidingWin(1)
        arr_sw_015min = self.vm_slidingWin(15)
        arr_sw_030min = self.vm_slidingWin(30)
        # arr_sw_060min = self.vm_slidingWin(60)
        # arr_sw_120min = self.vm_slidingWin(120)
        
        # ws = 15 # min 
        # arr_act_1min = self.vm_sWin_groups(arr_sw_001min, ws)
        
        ws = 120 # min 
        arr_act_001min  = self.vm_sWin_groups(arr_sw_001min, ws)
        arr_act_015min  = self.vm_sWin_groups(arr_sw_015min, ws)
        arr_act_030min  = self.vm_sWin_groups(arr_sw_030min, ws)
        # arr_act_060min  = self.vm_sWin_groups(arr_sw_060min, ws)
        # arr_act_120min = self.vm_sWin_groups(arr_sw_120min, ws)
       
       
       
        x_ini = self.x_ini
        x_end = self.x_end

        ax[0].set_xlim(x_ini,x_end)
        ax[-1].xaxis.set_major_formatter(mticker.FuncFormatter(self.update_ticks_x))
       
        y_ini= -10
        y_end=  150
        ax[0].set_ylim(y_ini,y_end)
        y_ini= -0.2
        y_end=  1.2
        ax[1].set_ylim(y_ini,y_end)
        ax[2].set_ylim(y_ini,y_end)
        ax[3].set_ylim(y_ini,y_end)
        # ax[4].set_ylim(y_ini,y_end)
        
       
        # self.plotVerticalLines(ax, self.list_start_end_night)
##        indices_vertical_lines = self.list_start_end_night        
##        self.plotVerticalLines(ax, indices_vertical_lines)
       
        ax[0].plot(arr_vec_mag,   color='tab:purple', label='VM (counts)')
        ax[1].plot(arr_sw_001min, color='tab:brown',  label='SW_1min'    )
        ax[2].plot(arr_sw_015min, color='tab:pink',   label='SW_15min'   )
        ax[3].plot(arr_sw_030min, color='tab:gray',   label='SW_30min'   )
        
        # ax[0].legend()
        # ax[1].legend()
        # ax[2].legend()
        # ax[3].legend()
        
        for sa in ax:
            leg = sa.legend(handlelength=0, handletextpad=0, fancybox=True)
            for item in leg.legendHandles:
                item.set_visible(False)
                
        ax[-1].set_xlabel('time (h)')
        
        # arg_arr_sw_001min = np.where(arr_sw_001min == 0)[0]
        # arg_arr_sw_015min = np.where(arr_sw_015min == 0)[0]
        # arg_arr_sw_030min = np.where(arr_sw_030min == 0)[0]
        
        # ax[1].scatter(arg_arr_sw_001min, arr_sw_001min[arg_arr_sw_001min], color='tab:brown', marker='o', markevery=0.5, label='SW_1min')
        # ax[2].scatter(arg_arr_sw_015min, arr_sw_015min[arg_arr_sw_015min], color='tab:pink',  marker='^', markevery=0.5, label='SW_15min')
        # ax[3].scatter(arg_arr_sw_030min, arr_sw_030min[arg_arr_sw_030min], color='tab:gray',  marker='s', markevery=0.5, label='SW_30min')
        
        # ax[4].plot(arr_sw_060min, color='tab:olive', label='SW_60min')
        # ax[5].plot(arr_sw_120min, color='tab:cyan', label='SW_120min')
        
        # ax[1].plot(arr_act_001min, color='tab:brown')
        # ax[2].plot(arr_act_015min, color='tab:pink')
        # ax[3].plot(arr_act_030min, color='tab:gray')
        
        ax0.plot(arr_vec_mag,    color='tab:purple', label='VM (counts)')
        ax1.plot(arr_act_001min, color='tab:brown',  marker='o', markevery=0.3, label='SM_1min' )
        ax2.plot(arr_act_015min, color='tab:pink',   marker='^', markevery=0.3, label='SM_15min')
        ax3.plot(arr_act_030min, color='tab:gray',   marker='s', markevery=0.3, label='SM_30min')
        # ax[4].plot(arr_act_060min, color='tab:olive')
        # ax[5].plot(arr_act_120min, color='tab:cyan')
       
        # ax0.legend()
        # ax1.legend()
        # ax2.legend()
        # ax3.legend()
       
        ax0.set_xlim(x_ini,x_end)
        ax1.set_xlim(x_ini,x_end)
        ax2.set_xlim(x_ini,x_end)
        ax3.set_xlim(x_ini,x_end)
        
        ax0.set_xticklabels([])
        ax1.set_xticklabels([])
        ax2.set_xticklabels([])
        ax3.xaxis.set_major_formatter(mticker.FuncFormatter(self.update_ticks_x))
        
        y_ini= -10
        y_end=  150
        ax0.set_ylim(y_ini,y_end)
        y_ini= -0.2
        y_end=  1.2
        ax1.set_ylim(y_ini,y_end)
        ax2.set_ylim(y_ini,y_end)
        ax3.set_ylim(y_ini,y_end)
       
        ax3.set_xlabel('time (h)')
        
        # data = [arr_act_001min[x_ini:x_end], arr_act_015min[x_ini:x_end], arr_act_030min[x_ini:x_end], arr_act_060min[x_ini:x_end], arr_act_120min[x_ini:x_end]]
        data = [arr_act_001min[x_ini:x_end], arr_act_015min[x_ini:x_end], arr_act_030min[x_ini:x_end]]
        
        ax4.boxplot(data, showfliers=False, labels=['SM_1min', 'SM_15min', 'SM_30min'])
        # ax4.set_xticklabels(['SW_1min', 'SW_15min', 'SW_30min'])
        
        y_ini= -0.02
        y_end=  1.02
        ax4.set_ylim(y_ini,y_end)
        
        
        
        # fig.legend(loc='upper center', bbox_to_anchor=(0.5, 1.02), ncol=4, fancybox=True, shadow=True)
        fig2.legend(loc='upper center', bbox_to_anchor=(0.5, 1.04), ncol=4, fancybox=True, shadow=True)
        # fig.suptitle(title)
        # fig2.suptitle(title)
        
        
        if save_flag:
            fig.savefig(filename+'.png', bbox_inches='tight')
            fig2.savefig(filename+'_boxplot.png', bbox_inches='tight')
        else:
            pass
       
        return 0
       
        
    def vm_slidingWin(self, win_size_minutes):
        
        self.min_vma = 1
        self.window_min = win_size_minutes
        self.min_samples = 1
        
        arr_vma = self.df1[self.vec_mag].to_numpy()
        ## we set to one any activity greater than or equal to the minimum value of counts (self.min_vma)
        arr_vma = (arr_vma >=self.min_vma).astype(int)
        ## window size: from 2 hours (original data) to the decomposition scale of dwt_level (2**dwt_level)
        
        spm = 60 ## seconds per min
        window_size = int(spm*self.window_min)
        # print(  'window size (s): ', window_size)
        ## window to average values (same weight)
        win = signal.windows.boxcar(window_size)
        
        arr_vma_mod = np.rint(signal.convolve(arr_vma, win, mode='full'))
        ## the sample is valid if the magnitude is greater than or equal to a min number of samples (self.min_samples)

        arr_vm_sw = (arr_vma_mod>=self.min_samples).astype(int) 

        return arr_vm_sw
        
        
    def vm_sWin_groups(self, arr_act, win_size_minutes):
        
        # self.min_vma = 3
        # self.window_min = win_size_minutes
        # self.min_samples = 1
        
        # arr_vma = self.df1[self.vec_mag].to_numpy()
        ## we set to one any activity greater than or equal to the minimum value of counts (self.min_vma)
        # arr_vma = (arr_vma >=self.min_vma).astype(int)
        ## window size: from 2 hours (original data) to the decomposition scale of dwt_level (2**dwt_level)
        
        spm = 60 ## seconds per min
        window_size = int(spm*win_size_minutes)
        # print(  'window size (s): ', window_size)
        ## window to average values (same weight)
        win = signal.windows.boxcar(window_size)
        
        arr_act_mod = np.rint(signal.convolve(arr_act, win, mode='full')) / window_size
        ## the sample is valid if the magnitude is greater than or equal to a min number of samples (self.min_samples)

        # arr_vm_sw = (arr_vma_mod>=self.min_samples).astype(int) 

        return arr_act_mod
    
    
    def mobility_estimation(self, win_size_1, win_size_2, win_size_3, path):
        
        ## we apply the algorithms to the complete data points (all data: days and nights in a row). 
        ##########################################
        ######## vector magnitude ################

        ## sliding window full provides a vector bigger than the original; that is why we cut the last part of the resultant vector

        arr_sw_vm_1 = self.vm_slidingWin(win_size_1)
        arr_sw_vm_1 = arr_sw_vm_1[:len(self.df1)]
        
        arr_sw_vm_2 = self.vm_sWin_groups(arr_sw_vm_1, win_size_2)
        arr_sw_vm_2 = arr_sw_vm_2[:len(self.df1)]

        ######## vector magnitude ################
        ##########################################
        ######## inclinometers ###################

        df_incl_filtered = self.inclinometers_low_pass_filter(win_size_3)
        ## counting number of repositioning 
        arr_rep, repos_labels, repos_data  = self.counting_repositioning(df_incl_filtered)
        ## insert a value of zero at the begining of the array to make it same size original
        arr_rep = np.insert(arr_rep,0,0).astype(int)
        # print(f'repositioning {repos_labels[-1]}: {repos_data[-1]}')
        ## compliance factor estimation
        arr_compl, arr_compl_bin, compliance_factor = self.complianceEstimation(arr_rep)
        arr_compl_bin = arr_compl_bin[:len(self.df1)]
        
        ######## inclinometers ###################
        ##########################################
        ##### day and night segmentation #########
        ## separate day and night and calculate mean for each day and each night

        df_mobility = self.days_nights() 
        
        df_mobility['vma_act'] = arr_sw_vm_2
        df_mobility['inc_act'] = arr_compl_bin
        
        # print(f'mobility:\n{df_mobility}')
        
        df_days, df_nights = self.means_mobility(df_mobility) 
        # print(f'df_days:\n{df_days}')
        # print(f'df_nights:\n{df_nights}')
        df_days.to_csv(path+'_days.csv', index=False)
        df_nights.to_csv(path+'_nights.csv', index=False)
        
        
        # ######## vector magnitude ################
        # ######## inclinometers ###################
        # df_incl_filtered = self.inclinometers_low_pass_filter(win_size_3)
        
        # ## counting number of repositioning 
        # arr_rep, repos_labels, repos_data  = self.counting_repositioning(df_incl_filtered)
        # print(f'repositioning {repos_labels[-1]}: {repos_data[-1]}')
        
        # ## compliance factor estimation
        # arr_compl, arr_compl_bin, compliance_factor = self.complianceEstimation(arr_rep)
        
        # x_ini = self.x_ini
        # x_end = self.x_end
        # compliance_factor = np.round(100*arr_compl_bin[x_ini:x_end].mean(),2)
        # print(f'compliance_factor: {compliance_factor}')
        
        # ######## inclinometers ###################
        
        return 0
    
    
    def days_nights(self):
        
        # print(f'means_mobility\ndf1, arr: {len(self.df1)}, {len(arr)}, {len(arr)-len(self.df1)}')
        df_mobility = pd.DataFrame()
        
        ## all dates in one list
        dates_list = self.df1[self.label_date].unique().tolist()
        print(self.filename,' dates: ',dates_list)
        
        labels_day_night=[]
        l_night=0
        l_day=0
        for date in dates_list:

            df_date = self.df1.loc[self.df1[self.label_date]== date]

            ## from 00:00:00 to 08:00:00
            df_segment = df_date.loc[df_date[self.label_time]<=self.time_end]
            # labels for the night values
            if len(df_segment) > 0:
                # creates a list of labels same size df_segment to identify the night number
                labels_day_night.extend(len(df_segment)*['n'+str(l_night)]) 
                l_night+=1
            else:
                pass

            ## from 08:00:00 to 20:00:00
            df_segment = df_date.loc[(df_date[self.label_time] > self.time_end) & (df_date[self.label_time] <= self.time_ini)]
            # labels for the day values
            if len(df_segment) > 0:
                # creates a list of labels same size df_segment to identify the day number
                labels_day_night.extend(len(df_segment)*['d'+str(l_day)]) 
                l_day+=1
            else:
                pass

            ## from 20:00:00 to 23:59:59
            df_segment = df_date.loc[df_date[self.label_time] > self.time_ini]
            # labels for the night values
            if len(df_segment) > 0:
                # creates a list of labels same size df_segment to identify the night number
                labels_day_night.extend(len(df_segment)*['n'+str(l_night)]) 
            else:
                pass
                
        # print(f'labels_day_night {len(labels_day_night)}')
        df_mobility['labels']=labels_day_night
        # df_mobility['activity']=arr
        # print(f'df_mobility:\n{df_mobility}')
        # self.plotVM_temp(arr)
    
        return df_mobility
    

    def means_mobility(self, df_mobility):
        
        ## all dates in one list
        labels_mobility = df_mobility['labels'].unique().tolist()
        print(f'labels_mobility: {labels_mobility}')
        
        # arr_days=[]
        # arr_nights=[]
        
        ### test ###
        # df_segment = df_mobility.loc[df_mobility['labels'].str.startswith('d')]
        # print(f'df_segment start with d: \n{df_segment}')
        
        # df_segment = df_mobility.loc[df_mobility['labels'].str.startswith('n')]
        # print(f'df_segment start with n: \n{df_segment}')
        
        df_days=pd.DataFrame(columns=['sample_size','vma_mean', 'inc_mean'])
        df_nights=pd.DataFrame(columns=['sample_size','vma_mean', 'inc_mean'])
        
        for label in labels_mobility:
            df_label = df_mobility[df_mobility['labels']== label]
            samples_size = len(df_label)
            mean_value_vma = df_label['vma_act'].mean()
            mean_value_inc = df_label['inc_act'].mean()
            
            if label.startswith('d'):
                # arr_days.append(mean_value)
                df_days.loc[len(df_days.index)] = [samples_size, mean_value_vma, mean_value_inc] 
            else:
                # arr_nights.append(mean_value)
                df_nights.loc[len(df_nights.index)] = [samples_size, mean_value_vma, mean_value_inc] 
                
        # print(f'{label}, {len(df_label)}, {mean_value}')
        # print(f'df_days:\n{df_days}')
        # print(f'df_nights:\n{df_nights}')
        
        return df_days, df_nights
        
    
    def plotVectorMagnitude(self):
        
        arr_vma = self.df1[self.vec_mag].to_numpy()
        arr_win = self.df1[self.vma_win].to_numpy()
        arr_act = self.df1[self.vma_act].to_numpy()
        
        
        fig, ax = plt.subplots(nrows=3, ncols=1, sharex=True)
        fig.canvas.mpl_connect('key_press_event', self.on_press)

        ## plot vertical lines
        self.plotVerticalLines(ax, self.list_start_end_night)        
        ## plot signals vector magnitude
        ax[0].plot(arr_vma)
        ax[1].plot(arr_win)
        ax[2].plot(arr_act)
        
        
        # arr_indexes = np.array(self.list_start_end_night_original)
        
        # indexes_ini = arr_indexes[:,0]
        # indexes_end = arr_indexes[:,1]
        
        # ## vertical lines for 22h00
        # for idx in indexes_ini:
            # ax[0].axvline(x = idx, color = 'tab:purple')
            # ax[1].axvline(x = idx, color = 'tab:purple')
        # ## vertical lines for 8h00
        # for idx in indexes_end:
            # ax[0].axvline(x = idx, color = 'tab:olive')
            # ax[1].axvline(x = idx, color = 'tab:olive')
        
        # ax[0].set_title(self.filename)
        
        # x_ini= 60000
        # x_end=160000
        x_ini = self.x_ini
        x_end = self.x_end
        
        ax[0].set_xlim(x_ini,x_end)
        
        y_ini= -0.1
        y_end=  1.2
        ax[2].set_ylim(y_ini,y_end)
        
        ax[0].set_ylabel('v.m.')
        ax[1].set_ylabel('s.w.')
        ax[2].set_ylabel('act.')
        ax[2].set_xlabel('time (s)')
        
        return 0
    
    
    def plotComplianceRep(self):
        
        arr_compl = np.array(self.list_arr_compl) 
        # print(f'arr_compl shape: {arr_compl.shape}')
        
        mean_arr_compl = np.mean(arr_compl, axis=0) 
        median_arr_compl = np.median(arr_compl, axis=0) 
        
        # print(f'mean_arr_compl {mean_arr_compl.shape}, {median_arr_compl.shape}')
        # self.plotImshow(arr_compl, np.reshape(median_arr_compl, (1, -1)))
        self.plotImshow_simple_2(arr_compl, np.reshape(median_arr_compl, (1, -1)))
        self.plotImshow_simple_2(arr_compl, np.reshape(mean_arr_compl, (1, -1)))
        
        # self.plotImshowRow(np.reshape(mean_arr_compl, (1, -1)), 'mean')
        # self.plotImshowRow(np.reshape(median_arr_compl, (1, -1)), 'median')
            
        return 0
        
        
    def plotImshow(self, arr_compl, arr_compl_2):
        
        size_x, size_y = arr_compl.shape
        print(f'size_x, size_y: {size_x},{size_y}')
        
        # fig, ax = plt.subplots(nrows=2, ncols=1, sharex=True)
        fig = plt.figure()
        fig.canvas.mpl_connect('key_press_event', self.on_press)
        fig.suptitle(self.filename)
        
        # im = ax[0].imshow(arr_compl,interpolation='none', vmin=0, vmax=5, aspect='auto') 
        ax1 = plt.subplot2grid(shape=(10, 15), loc=(0, 0), rowspan= 8, colspan=14) 
        ax2 = plt.subplot2grid(shape=(10, 15), loc=(8, 0), rowspan= 2, colspan=14) 
        ax3 = plt.subplot2grid(shape=(10, 15), loc=(0, 14), rowspan=10, colspan=1)
        
        im1 = ax1.imshow(arr_compl,interpolation='none', vmin=0, vmax=3, aspect='auto')
        im2 = ax2.imshow(arr_compl_2,interpolation='none', vmin=0, vmax=3, aspect='auto')
        # ax1.figure.colorbar(im1,ax=ax3)
        cbar = fig.colorbar(im1, cax=ax3, ticks=[0,1,2,3], label='repositioning compliance')
        cbar.ax.set_yticklabels(['0','1','2','>=3'])
        
        arr_xticks = np.arange(0,size_y+1,3600)

        ax1.set_xticks(arr_xticks)
        ax2.set_xticks(arr_xticks)
        ax2.set_xticklabels(['22','23','00','01','02','03','04','05','06','07','08']) # fontsize=12
        
        ax1.tick_params(left = True, labelleft = True,
                        bottom = True, labelbottom = False)
        ax2.tick_params(left = False, labelleft = False)
        
        ax1.set_ylabel('night')
        ax2.set_ylabel('median')
        ax2.set_xlabel('hour')
        
        return 0
        
        
    def plotImshow_simple(self, arr_compl, arr_compl_2):
        
        size_x, size_y = arr_compl.shape
        print(f'size_x, size_y: {size_x},{size_y}')
        
        # fig, ax = plt.subplots(nrows=2, ncols=1, sharex=True)
        fig = plt.figure()
        fig.canvas.mpl_connect('key_press_event', self.on_press)
        fig.suptitle(self.filename)
        
        # im = ax[0].imshow(arr_compl,interpolation='none', vmin=0, vmax=5, aspect='auto') 
        # ax1 = plt.subplot2grid(shape=(10, 15), loc=(0, 0), rowspan= 8, colspan=14) 
        ax2 = plt.subplot2grid(shape=(10, 15), loc=(0, 0), rowspan= 10, colspan=14) 
        ax3 = plt.subplot2grid(shape=(10, 15), loc=(0, 14), rowspan=10, colspan=1)
        
        # im1 = ax1.imshow(arr_compl,interpolation='none', vmin=0, vmax=3, aspect='auto')
        im2 = ax2.imshow(arr_compl_2,interpolation='none', vmin=0, vmax=3, aspect='auto')
        # ax1.figure.colorbar(im1,ax=ax3)
        cbar = fig.colorbar(im2, cax=ax3, ticks=[0,1,2,3], label='repositioning compliance')
        cbar.ax.set_yticklabels(['0','1','2','>=3'])
        
        arr_xticks = np.arange(0,size_y+1,3600)

        # ax1.set_xticks(arr_xticks)
        ax2.set_xticks(arr_xticks)
        ax2.set_xticklabels(['22','23','00','01','02','03','04','05','06','07','08']) # fontsize=12
        
        # ax1.tick_params(left = True, labelleft = True,
                        # bottom = True, labelbottom = False)
        ax2.tick_params(left = False, labelleft = False)
        
        # ax1.set_ylabel('night')
        ax2.set_ylabel('median')
        ax2.set_xlabel('hour')
        
        return 0

    
    def plotImshow_simple_2(self, arr_compl, arr_compl_2):
        
        fig, ax = plt.subplots(nrows=1, ncols=1, sharex=True)
        fig.canvas.mpl_connect('key_press_event', self.on_press)
        
        ax.plot(arr_compl_2[0])
        # print(f'arr_compl_2:\n{arr_compl_2}, {arr_compl_2.shape}')
        
        
    def plotImshowRow(self, arr_compl, text):
        
        size_x, size_y = arr_compl.shape
        
        fig, ax = plt.subplots()
        fig.canvas.mpl_connect('key_press_event', self.on_press)
        
        im = ax.imshow(arr_compl,interpolation='none', vmin=0, vmax=5) # extent=[0,36,0,8]
        ax.set_aspect((size_y/10)/size_x)
        # cbar = ax.figure.colorbar(im, ax=ax)
        
        ax.set_title(f'{self.filename}, {text}' )
        
        return 0
    
        
    def getActigraphyData(self):
        return self.df1
        
    def getNightCounts(self):
        return self.df_all_nights


