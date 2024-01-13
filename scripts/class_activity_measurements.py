from datetime import datetime
from scipy import signal
import numpy as np
import pandas as pd
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
import sys

class Activity_Measurements:

    def __init__(self):
        
        # print('Activity Measurements object constructor initialization')

        self.header_location=10

        self.vec_mag  ='Vector Magnitude'
        self.incl_off ='Inclinometer Off'
        self.incl_sta ='Inclinometer Standing'
        self.incl_sit ='Inclinometer Sitting'
        self.incl_lyi ='Inclinometer Lying'
        
        self.off_filtered = 'off_filtered'
        self.lyi_filtered = 'lyi_filtered'
        self.sit_filtered = 'sit_filtered'
        self.sta_filtered = 'sta_filtered'
        self.sum_filtered = 'sum_filtered'
        
        self.time_ini='21:00:00'
        self.time_end='09:00:00'
        
        self.color_day = 'tab:green'
        self.color_night = 'tab:purple'
        
        self.label_time = ' Time'
        self.label_date = 'Date'
        self.time_sec = 'time_sec'
        self.label_day_night = 'day_night'
        self.label_binary_day_night = 'binary_day_night'
        self.vma_a='vma_a'
        self.vma_b='vma_b'
        self.inc_a='inc_a'
        self.inc_b='inc_b'
        
        self.df1 = pd.DataFrame([])
        self.df_days  = pd.DataFrame(columns  =['sample_size', 'vma_mean', 'inc_mean'])
        self.df_nights= pd.DataFrame(columns=['sample_size', 'vma_mean', 'inc_mean'])
        self.df_incl_filtered = pd.DataFrame()
        
        
    def openFile(self, path, filename):
        
        self.path = path
        self.filename = filename
        self.df1 = pd.read_csv(path+filename, header=self.header_location, decimal=',')

        ## this is necesary for cases where datetime format is different or has repetitive values 
        with open(path+filename) as f:
            for i, line in enumerate(f):             
                if i < 10:
                    list_values = line.split()
                    if i == 2:
                        ## hh:mm:ss
                        start_time = list_values[2][:8]
                    elif i == 3:
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
        
        ## creates labels for data days and nights
        # print(f'creating labels for days and nights data... ', end='')
        self.days_nights()
        # print('done.\n')
        
        return 0
    
    
    def days_nights(self):
        
        ## all dates in one list
        dates_list = self.df1[self.label_date].unique().tolist()
        # print(self.filename,' dates: ',dates_list)
        
        labels_day_night=[]
        labels_binary_day_night=[]
        
        l_night=0
        l_day=0
        for date in dates_list:

            df_date = self.df1.loc[self.df1[self.label_date]== date]

            ## from 00:00:00 to self.time_end
            df_segment = df_date.loc[df_date[self.label_time]<=self.time_end]
            # labels for the night values
            if len(df_segment) > 0:
                # creates a list of labels same size df_segment to identify the night number
                labels_day_night.extend(len(df_segment)*['n'+str(l_night)]) 
                labels_binary_day_night.extend(len(df_segment)*['night']) 
                l_night+=1
            else:
                pass

            ## from self.time_end to self.time_ini
            df_segment = df_date.loc[(df_date[self.label_time] > self.time_end) & (df_date[self.label_time] <= self.time_ini)]
            # labels for the day values
            if len(df_segment) > 0:
                # creates a list of labels same size df_segment to identify the day number
                labels_day_night.extend(len(df_segment)*['d'+str(l_day)]) 
                labels_binary_day_night.extend(len(df_segment)*['day']) 
                l_day+=1
            else:
                pass

            ## from self.time_ini to 23:59:59
            df_segment = df_date.loc[df_date[self.label_time] > self.time_ini]
            # labels for the night values
            if len(df_segment) > 0:
                # creates a list of labels same size df_segment to identify the night number
                labels_day_night.extend(len(df_segment)*['n'+str(l_night)]) 
                labels_binary_day_night.extend(len(df_segment)*['night']) 
            else:
                pass
                
        self.df1[self.label_day_night]=labels_day_night
        self.df1[self.label_binary_day_night]=labels_binary_day_night
    
        return 0


    def filterLowPass(self, arr, fc, order):
        sampling_rate = 1 ## 1 Hz, 1 sample per second
        sos = signal.butter(order, fc, btype='lowpass', fs=sampling_rate, output='sos')
        filtered = signal.sosfiltfilt(sos, arr)
        return filtered

    def inclinometers_lpf(self, size_min):
        
        arr_date = self.df1[self.label_date].to_numpy()
        arr_time = self.df1[self.label_time].to_numpy()
        
        ## read inclinometers 
        arr_off = self.df1[self.incl_off].to_numpy()
        arr_lyi = self.df1[self.incl_lyi].to_numpy()
        arr_sit = self.df1[self.incl_sit].to_numpy()
        arr_sta = self.df1[self.incl_sta].to_numpy()
        
        spm = 60 ## seconds per min
        period = spm*size_min

        freq = 1/period
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
        df_lpf_inc = pd.DataFrame()
        df_lpf_inc[self.label_date]=arr_date
        df_lpf_inc[self.label_time]=arr_time
        df_lpf_inc[self.off_filtered]=arr_off_mod
        df_lpf_inc[self.lyi_filtered]=arr_lyi_mod
        df_lpf_inc[self.sit_filtered]=arr_sit_mod
        df_lpf_inc[self.sta_filtered]=arr_sta_mod
        df_lpf_inc[self.sum_filtered]=sum_coeff
        df_lpf_inc[self.incl_off]=arr_new_off
        df_lpf_inc[self.incl_lyi]=arr_new_lyi
        df_lpf_inc[self.incl_sit]=arr_new_sit
        df_lpf_inc[self.incl_sta]=arr_new_sta
        
        return df_lpf_inc
    
    
    def posture_changing(self, df):
        
        arr_off = df[self.incl_off].to_numpy()
        arr_lyi = df[self.incl_lyi].to_numpy()
        arr_sit = df[self.incl_sit].to_numpy()
        arr_sta = df[self.incl_sta].to_numpy()
        
        arr_off_lyi = self.counting_per_two_incl(arr_off, arr_lyi)
        arr_off_sit = self.counting_per_two_incl(arr_off, arr_sit)
        arr_off_sta = self.counting_per_two_incl(arr_off, arr_sta)
        
        arr_lyi_off = self.counting_per_two_incl(arr_lyi, arr_off)
        arr_lyi_sit = self.counting_per_two_incl(arr_lyi, arr_sit)
        arr_lyi_sta = self.counting_per_two_incl(arr_lyi, arr_sta)
        
        arr_sit_off = self.counting_per_two_incl(arr_sit, arr_off)
        arr_sit_lyi = self.counting_per_two_incl(arr_sit, arr_lyi)
        arr_sit_sta = self.counting_per_two_incl(arr_sit, arr_sta)
        
        arr_sta_off = self.counting_per_two_incl(arr_sta, arr_off)
        arr_sta_lyi = self.counting_per_two_incl(arr_sta, arr_lyi)
        arr_sta_sit = self.counting_per_two_incl(arr_sta, arr_sit)
    
        # ## array of repositionings (logical or |)
        arr_rep =(arr_off_lyi | arr_lyi_off | arr_sit_off | arr_sta_off |
                  arr_off_sit | arr_lyi_sit | arr_sit_lyi | arr_sta_lyi |
                  arr_off_sta | arr_lyi_sta | arr_sit_sta | arr_sta_sit)
    
        ## to make the output array same size than the input one
        arr_rep = np.insert(arr_rep,0,0).astype(int)
        return arr_rep

    def counting_per_two_incl(self, arr0, arr1):
        arr = (arr0[:-1] == arr1[1:]) & (arr0[:-1]==1)
        return arr

    
    def slidingWindow_A(self, arr, size_min):
        
        min_value = 1
        
        spm = 60 ## seconds per min
        window_size = int(spm*size_min)

        win = signal.windows.boxcar(window_size)
        ## dot product between the window and the signal per sample
        arr_mod = np.rint(signal.convolve(arr, win, mode='full'))
        ## arr_mod is larger than arr; making arr_mod same size than arr
        arr_mod = arr_mod[:len(arr)]
        ## applies a threshold
        arr_sw = (arr_mod>=min_value).astype(int) 

        return arr_sw
        
    def slidingWindow_B(self, arr, size_min):
        
        spm = 60 ## seconds per min
        window_size = int(spm*size_min)
        ## dot product between window and data per every sample
        win = signal.windows.boxcar(window_size)
        ## calculates mean values
        arr_mod = np.rint(signal.convolve(arr, win, mode='full')) / window_size
        ## arr_mod is larger than arr; making arr_mod same size than arr
        arr_mod = arr_mod[:len(arr)]
        
        return arr_mod
    
    def means_days_nights(self):
        
        ## all dates in one list
        labels_list = self.df1[self.label_day_night].unique().tolist()
        # print(f'labels_list: {labels_list}')
        
        for label in labels_list:
            
            df_label = self.df1[self.df1[self.label_day_night]== label]
            
            samples_size = len(df_label)
            mean_vma = df_label[self.vma_b].mean()
            mean_inc = df_label[self.inc_b].mean()
            
            if label.startswith('d'):
                # arr_days.append(mean_value)
                self.df_days.loc[len(self.df_days.index)]     = [samples_size, mean_vma, mean_inc] 
            else:
                # arr_nights.append(mean_value)
                self.df_nights.loc[len(self.df_nights.index)] = [samples_size, mean_vma, mean_inc] 
                
        return 0
        
    
    def vma_processing(self, size_a, size_b):
        
        arr_vma = self.df1[self.vec_mag].to_numpy()
                
        arr_a = self.slidingWindow_A(arr_vma, size_a)
        arr_b = self.slidingWindow_B(arr_a, size_b)
        
        self.df1[self.vma_a]=arr_a
        self.df1[self.vma_b]=arr_b
        
        return 0
        
    def inc_processing(self, size_a, size_b, flag):
        
        # ## first step signals' filtering to remove activity of short duration
        if flag:
            tc = 1.0 # minutes, fc = 1/(60*tc): to remove micro-movements
        else:
            tc = 1.0/29.0 # min ->  fc = 0.5 Hz : keep all components; half of frequency of sampling (max. freq. Nyquist)
            
        self.df_incl_filtered = self.inclinometers_lpf(tc)
        
        # self.plot_Inclinometers(df_incl_filtered)
        
        arr_inc = self.posture_changing(self.df_incl_filtered)
        
        arr_a = self.slidingWindow_A(arr_inc, size_a)
        arr_b = self.slidingWindow_B(arr_a, size_b)
        
        self.df1[self.inc_a]=arr_a
        self.df1[self.inc_b]=arr_b
        
        return 0

        
    def plot_Inclinometers_results(self):
        
        fig, ax = plt.subplots(nrows=10, ncols=1, sharex=True, figsize=(12, 6))
        fig.canvas.mpl_connect('key_press_event', self.on_press)
                
        arr_0 = np.empty((4, 0)).tolist()
        arr_2 = np.empty((4, 0)).tolist()
        
        arr_0[0] =self.df1[self.incl_off].to_numpy()
        arr_0[1] =self.df1[self.incl_lyi].to_numpy()
        arr_0[2] =self.df1[self.incl_sit].to_numpy()
        arr_0[3] =self.df1[self.incl_sta].to_numpy()
        
        arr_2[0] =self.df_incl_filtered[self.incl_off].to_numpy()
        arr_2[1] =self.df_incl_filtered[self.incl_lyi].to_numpy()
        arr_2[2] =self.df_incl_filtered[self.incl_sit].to_numpy()
        arr_2[3] =self.df_incl_filtered[self.incl_sta].to_numpy()
        
        arr_a = self.df1[self.inc_a].to_list()
        arr_b = self.df1[self.inc_b].to_list()
        
        ###########
        
        ax[0].plot(arr_0[0], color='tab:blue')
        ax[1].plot(arr_0[1], color='tab:orange')
        ax[2].plot(arr_0[2], color='tab:green')
        ax[3].plot(arr_0[3], color='tab:red')
        
        ax[4].plot(arr_2[0], color='tab:blue')
        ax[5].plot(arr_2[1], color='tab:orange')
        ax[6].plot(arr_2[2], color='tab:green')
        ax[7].plot(arr_2[3], color='tab:red')
        
        ax[8].plot(arr_a, color='tab:purple')
        ax[9].plot(arr_b, color='tab:brown')
        
        y_ini= -0.1
        y_end=  1.2
        ax[-1].set_ylim(y_ini,y_end)
        
        return 0
    
    
    def plot_Inclinometers(self):
        
        fig, ax = plt.subplots(nrows=12, ncols=1, sharex=True, figsize=(12, 6))
        fig.canvas.mpl_connect('key_press_event', self.on_press)
                
        arr_0 = np.empty((4, 0)).tolist()
        arr_1 = np.empty((4, 0)).tolist()
        arr_2 = np.empty((4, 0)).tolist()
        
        arr_0[0] =self.df1[self.incl_off].to_numpy()
        arr_0[1] =self.df1[self.incl_lyi].to_numpy()
        arr_0[2] =self.df1[self.incl_sit].to_numpy()
        arr_0[3] =self.df1[self.incl_sta].to_numpy()
        
        arr_1[0] = self.df_incl_filtered[self.off_filtered].to_numpy()
        arr_1[1] = self.df_incl_filtered[self.lyi_filtered].to_numpy()
        arr_1[2] = self.df_incl_filtered[self.sit_filtered].to_numpy()
        arr_1[3] = self.df_incl_filtered[self.sta_filtered].to_numpy()
        
        arr_2[0] =self.df_incl_filtered[self.incl_off].to_numpy()
        arr_2[1] =self.df_incl_filtered[self.incl_lyi].to_numpy()
        arr_2[2] =self.df_incl_filtered[self.incl_sit].to_numpy()
        arr_2[3] =self.df_incl_filtered[self.incl_sta].to_numpy()
        
        ###########
        
        ax[0].plot(arr_0[0], color='tab:blue')
        ax[1].plot(arr_0[1], color='tab:orange')
        ax[2].plot(arr_0[2], color='tab:green')
        ax[3].plot(arr_0[3], color='tab:red')
        
        ax[4].plot(arr_1[0], color='tab:blue')
        ax[5].plot(arr_1[1], color='tab:orange')
        ax[6].plot(arr_1[2], color='tab:green')
        ax[7].plot(arr_1[3], color='tab:red')
        
        ax[8].plot(arr_2[0], color='tab:blue')
        ax[9].plot(arr_2[1], color='tab:orange')
        ax[10].plot(arr_2[2], color='tab:green')
        ax[11].plot(arr_2[3], color='tab:red')
        
        return 0
    
    def on_press(self, event):
        # print('press', event.key)
        sys.stdout.flush()
        
        if event.key == 'x':
            plt.close('all')
        else:
            pass
        return 0
    
    def get_df1(self):
        return self.df1
        
    def getVectorMagnitude(self):
        return self.df1[self.vec_mag].tolist()
    
    def getDayNightLabels(self):
        return self.df1[self.label_day_night].tolist()
        
    def getMeansDays(self):
        return self.df_days
        
    def getMeansNights(self):
        return self.df_nights

