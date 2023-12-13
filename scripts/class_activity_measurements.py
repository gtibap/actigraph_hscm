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
        
        
        self.time_ini='20:00:00'
        self.time_end='08:00:00'
        
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

            ## from 00:00:00 to 08:00:00
            df_segment = df_date.loc[df_date[self.label_time]<=self.time_end]
            # labels for the night values
            if len(df_segment) > 0:
                # creates a list of labels same size df_segment to identify the night number
                labels_day_night.extend(len(df_segment)*['n'+str(l_night)]) 
                labels_binary_day_night.extend(len(df_segment)*['night']) 
                l_night+=1
            else:
                pass

            ## from 08:00:00 to 20:00:00
            df_segment = df_date.loc[(df_date[self.label_time] > self.time_end) & (df_date[self.label_time] <= self.time_ini)]
            # labels for the day values
            if len(df_segment) > 0:
                # creates a list of labels same size df_segment to identify the day number
                labels_day_night.extend(len(df_segment)*['d'+str(l_day)]) 
                labels_binary_day_night.extend(len(df_segment)*['day']) 
                l_day+=1
            else:
                pass

            ## from 20:00:00 to 23:59:59
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

    
    def posture_changing(self):
        
        arr_off = self.df1[self.incl_off].to_numpy()
        arr_lyi = self.df1[self.incl_lyi].to_numpy()
        arr_sit = self.df1[self.incl_sit].to_numpy()
        arr_sta = self.df1[self.incl_sta].to_numpy()
        
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
    
        ## array of repositionings (logical or |)
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
        
    def inc_processing(self, size_a, size_b):
        
        arr_inc = self.posture_changing()
        
        arr_a = self.slidingWindow_A(arr_inc, size_a)
        arr_b = self.slidingWindow_B(arr_a, size_b)
        
        self.df1[self.inc_a]=arr_a
        self.df1[self.inc_b]=arr_b
        
        return 0
    
    
    def getDataFrame(self):
        return self.df1
        
    def getVectorMagnitude(self):
        return self.df1[self.vec_mag].tolist()
    
    def getDayNightLabels(self):
        return self.df1[self.label_day_night].tolist()

