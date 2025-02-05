from datetime import datetime
from scipy import ndimage
from scipy import signal
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pywt
import re
import sys



class Counting_Actigraphy:

    def __init__(self, name):

        self.name = name
        # print('Seg_Actigraphy object initialization')
        self.header_location=10
        self.vec_mag  ='Vector Magnitude'
        self.incl_off ='Inclinometer Off'
        self.incl_sta ='Inclinometer Standing'
        self.incl_sit ='Inclinometer Sitting'
        self.incl_lyi ='Inclinometer Lying'
        self.vma_mod = 'vma_mod'
        self.off_mod = 'off_mod'
        self.lyi_mod = 'lyi_mod'
        self.sit_mod = 'sit_mod'
        self.sta_mod = 'sta_mod'
        self.vma_act = 'vma_act'
        self.off_act = 'off_act'
        self.lyi_act = 'lyi_act'
        self.sit_act = 'sit_act'
        self.sta_act = 'sta_act'
        self.dwt_vma = 'dwt_vma'
        self.dwt_off = 'dwt_off'
        self.dwt_lyi = 'dwt_lyi'
        self.dwt_sit = 'dwt_sit'
        self.dwt_sta = 'dwt_sta'
        
        self.vma_mov = 'vma_mov'

        self.vma_a='vma_a'
        self.vma_b='vma_b'
        
        self.vma_counts='vma_counts'
        self.off_counts='off_counts'
        self.lyi_counts='lyi_counts'
        self.sit_counts='sit_counts'
        self.sta_counts='sta_counts'
        self.night = 'night'
        
        self.time_ini='22:00:00'
        self.time_end='07:59:59'
        
        self.color_day = 'tab:green'
        self.color_night = 'tab:purple'
        
        self.label_time = ' Time'
        self.label_date = 'Date'
        self.time_sec = 'time_sec'
        self.label_day_night = 'day_night'
        self.label_binary_day_night = 'binary_day_night'

        self.df1 = pd.DataFrame([])
        self.df_activity_indexes = pd.DataFrame([], columns=['idx_ini','idx_end','length'])
        self.df_all_nights = pd.DataFrame()
        
        self.df_inclinometers = pd.DataFrame([])
        self.df_dwt_vma = pd.DataFrame([])
        self.df_nights_dwt_vma = pd.DataFrame([])

        self.min_vma = 1 # counts
        self.min_samples = 1 # min number of samples inside the window (function: rollingWindow())
        self.compliance_win = 180 # min equal to 3h
        self.arr_fig = [[] for i in range(10)]
        self.arr_axs = [[] for i in range(10)]
        
        self.list_start_end_night=[]
        self.list_start_end_night_original=[]
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

        ## creates labels for data days and nights
        # print(f'creating labels for days and nights data... ', end='')
        self.days_nights()
        # print(self.df1)
        # print('done.\n')
        
        return 0
    

    def days_nights(self):
        
        ## all dates in one list
        dates_list = self.df1[self.label_date].unique().tolist()
        # print(self.filename,' dates: ',dates_list)
        
        labels_day_night=[]
        labels_binary_day_night=[]
        
        l_night=1
        l_day=1
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

        self.df_inclinometers[self.label_day_night]=labels_day_night
        self.df_inclinometers[self.label_binary_day_night]=labels_binary_day_night
    
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
        self.df1[self.vma_act] = (arr_vma_mod>=self.min_samples).astype(int) 
        
        ## number of movements counting
        self.df1[self.vma_mov] = self.counting_mov(self.df1[self.vma_act].to_numpy())
        
        ## retrieve only data of nights; from 22h to 8h
        df_nights = self.nightsDataFrame(self.df1)
        
        list_nights = df_nights[self.night].unique().tolist()

        list_mov_night = []
        list_counts_mov_night = []
        for num_night in list_nights:
            df = df_nights.loc[df_nights[self.night]==num_night]
            ## mean activity every night
            list_mov_night.append(df[self.vma_act].mean())
            
            ## counting number of movements per night
            if df.iloc[0][self.vma_act]==0:
                counts_mov_night = df[self.vma_mov].sum()
            else:
                counts_mov_night = df[self.vma_mov].sum() + 1
            list_counts_mov_night.append(counts_mov_night)
        
        return np.around(list_mov_night,3), list_counts_mov_night
     
     
    def inclinometers_sliding_window(self, win_size_minutes):
        
        # self.window_min = win_size_minutes
        
        ## read vector magnitude
        arr_vma = self.df1[self.vec_mag].to_numpy()

        ## read inclinometers 
        arr_off = self.df1[self.incl_off].to_numpy()
        arr_lyi = self.df1[self.incl_lyi].to_numpy()
        arr_sit = self.df1[self.incl_sit].to_numpy()
        arr_sta = self.df1[self.incl_sta].to_numpy()
        
        spm = 60 ## seconds per min
        window_size = int(spm*win_size_minutes)
        ## window to average values (same weight)
        win = signal.windows.boxcar(window_size)
        
        # results convolution aproximate to the closest integer to avoid inestabilities
        coeff_off = np.rint(signal.convolve(arr_off, win, mode='same'))
        coeff_lyi = np.rint(signal.convolve(arr_lyi, win, mode='same'))
        coeff_sit = np.rint(signal.convolve(arr_sit, win, mode='same'))
        coeff_sta = np.rint(signal.convolve(arr_sta, win, mode='same'))

        # ## size of coeff_off is larger than that of arr_off; making coeff_off same size than arr_off
        # coeff_off = coeff_off[:len(arr_off)]
        # coeff_lyi = coeff_lyi[:len(arr_lyi)]
        # coeff_sit = coeff_sit[:len(arr_sit)]
        # coeff_sta = coeff_sta[:len(arr_sta)]
        
        ## amplitude normalization
        coeff_all = coeff_off + coeff_lyi + coeff_sit + coeff_sta
        mean_coeff = coeff_all.mean()
        # std_coeff = coeff_all.std()
        # print('mean, std: ', mean_coeff, std_coeff)
        
        coeff_off = coeff_off/mean_coeff
        coeff_lyi = coeff_lyi/mean_coeff
        coeff_sit = coeff_sit/mean_coeff
        coeff_sta = coeff_sta/mean_coeff
        coeff_all = coeff_all/mean_coeff
        
        ## pile the inclinometers resultant coefficients (level 10) and select the inclinometer with the maximum value per each sample
        coeff_stack = np.vstack((coeff_off,coeff_lyi,coeff_sit,coeff_sta))
        index_coeff = np.argmax(coeff_stack, axis=0)
        arr_new_off = (index_coeff==0).astype(int)
        arr_new_lyi = (index_coeff==1).astype(int)
        arr_new_sit = (index_coeff==2).astype(int)
        arr_new_sta = (index_coeff==3).astype(int)
        
        
        arr_date = self.df1[self.label_date].to_numpy()
        arr_time = self.df1[self.label_time].to_numpy()
        
        ## grouping the resultant data
        # self.df_inclinometers = pd.DataFrame()
        self.df_inclinometers[self.label_date]=arr_date
        self.df_inclinometers[self.label_time]=arr_time
        self.df_inclinometers[self.dwt_off]=coeff_off
        self.df_inclinometers[self.dwt_lyi]=coeff_lyi
        self.df_inclinometers[self.dwt_sit]=coeff_sit
        self.df_inclinometers[self.dwt_sta]=coeff_sta
        self.df_inclinometers[self.incl_off]=arr_new_off
        self.df_inclinometers[self.incl_lyi]=arr_new_lyi
        self.df_inclinometers[self.incl_sit]=arr_new_sit
        self.df_inclinometers[self.incl_sta]=arr_new_sta
        self.df_inclinometers[self.vec_mag]=arr_vma
        
        return 0
        
        
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
 
    
    def nightCounts(self):
        ## from 22:00:00 until 07:59:59 (next day)
        self.list_start_end_night = []
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
            
            self.list_start_end_night.append([id_start,id_end])
            
            len_night = len(df_night)
            # normalized number of counts per inclinometer
            counts_off=np.round(100*df_night[self.incl_off].mean(),2)
            counts_lyi=np.round(100*df_night[self.incl_lyi].mean(),2)
            counts_sit=np.round(100*df_night[self.incl_sit].mean(),2)
            counts_sta=np.round(100*df_night[self.incl_sta].mean(),2)
            
            ## counting number of repositioning 
            arr_rep, repos_labels, repos_data  = self.counting_repositioning(df_night)
            
            ## compliance factor estimation
            compliance_factor = self.complianceEstimation(arr_rep)
            
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
        coeff_rep = np.rint(signal.convolve(arr_rep, win, mode='same'))
        
        coeff_rep = (coeff_rep>=1).astype(int) 
        
        return np.round(100*coeff_rep.mean(),2) 
        
    
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
        
    def counting_mov(self, arr0):
        arr = ((arr0[:-1] != arr0[1:]) & (arr0[:-1]==0))
        ## appending a value (0) to make the output same lenght as the input
        return np.append(0, arr)
    
    #########################
    # activity rates methods

    def slidingWindow_A(self, arr, size_min):
        min_value = 1
        spm = 60 ## seconds per min
        window_size = int(spm*size_min)

        win = signal.windows.boxcar(window_size)
        ## dot product between the window and the signal per sample
        arr_mod = np.rint(signal.convolve(arr, win, mode='same'))
        ## applies a threshold
        arr_sw = (arr_mod>=min_value).astype(int) 
        return arr_sw
        
    def slidingWindow_B(self, arr, size_min):
        
        spm = 60 ## seconds per min
        window_size = int(spm*size_min)
        ## dot product between window and data per every sample
        win = signal.windows.boxcar(window_size)
        ## calculates mean values
        arr_mod = np.rint(signal.convolve(arr, win, mode='same')) / window_size
        return arr_mod
    
    def vma_processing(self, size_a, size_b):
        
        arr_vma = self.df1[self.vec_mag].to_numpy()
                
        arr_a = self.slidingWindow_A(arr_vma, size_a)
        arr_b = self.slidingWindow_B(arr_a, size_b)
        
        self.df1[self.vma_a]=arr_a
        self.df1[self.vma_b]=arr_b

        self.df_inclinometers[self.vma_a]=arr_a
        self.df_inclinometers[self.vma_b]=arr_b
        
        return 0

    # activity rates methods
    #########################
    
    ####################
    ### plotting methods

    def on_press(self, event):
        # print('press', event.key)
        sys.stdout.flush()
        
        if event.key == 'x':
            plt.close('all')
        else:
            pass
         
     
    def plotActigraphy(self,option, x_min, x_max):
        self.arr_fig[0], self.arr_axs[0] = plt.subplots(nrows=5, ncols=1, sharex=True)
        if option==0:
            df = self.df1
        else:
            df = self.df_inclinometers

        self.plotWithColors(df, self.arr_fig[0], self.arr_axs[0],signals=0)
        self.arr_axs[0][0].set_xlim(x_min,x_max)
        return 0
        
    def plotActigraphyMod(self,df, option):
        self.arr_fig[1], self.arr_axs[1] = plt.subplots(nrows=5, ncols=1, sharex=True)
        if option==0:
            df = self.df1
        else:
            df = self.df_inclinometers
        self.plotWithColors(df, self.arr_fig[1], self.arr_axs[1],signals=1)
        return 0
    

    def plotWithColors(self,df,fig,ax,signals):
        
        fig.canvas.mpl_connect('key_press_event', self.on_press)
        
        for i in np.arange(5):
            ax[i].cla()
        
        # x_ini=100000
        # x_end=200000
        # ax[0].set_xlim(x_ini,x_end)
        
        # ax[0].set_ylim(0,400)
        
        ax[0].set_title(self.filename)
        ax[0].set_ylabel('v.m.')
        ax[1].set_ylabel('off')
        ax[2].set_ylabel('lyi')
        ax[3].set_ylabel('sit')
        ax[4].set_ylabel('sta')

        ax[4].set_xlabel('time (s)')
        
        dates_list = df[self.label_date].unique().tolist()
        
        # print(self.filename,' dates: ',dates_list)
        for date in dates_list:
            df_date = df[df[self.label_date]== date]

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
     
    
    def plotDWTInclinometers(self):
        
        arr_dwt  = np.empty((4, 0)).tolist()
        arr_incl = np.empty((4, 0)).tolist()
        
        arr_dwt[0] = self.df_inclinometers[self.dwt_off].to_numpy()
        arr_dwt[1] = self.df_inclinometers[self.dwt_lyi].to_numpy()
        arr_dwt[2] = self.df_inclinometers[self.dwt_sit].to_numpy()
        arr_dwt[3] = self.df_inclinometers[self.dwt_sta].to_numpy()
        
        arr_incl[0] = self.df_inclinometers[self.incl_off].to_numpy()
        arr_incl[1] = self.df_inclinometers[self.incl_lyi].to_numpy()
        arr_incl[2] = self.df_inclinometers[self.incl_sit].to_numpy()
        arr_incl[3] = self.df_inclinometers[self.incl_sta].to_numpy()
        
        fig, axarr = plt.subplots(nrows=5, ncols=1, sharex=True, sharey=True)
        fig.canvas.mpl_connect('key_press_event', self.on_press)
        
        axarr[0].plot(arr_dwt[0], color='tab:blue')
        axarr[1].plot(arr_dwt[1], color='tab:orange')
        axarr[2].plot(arr_dwt[2], color='tab:green')
        axarr[3].plot(arr_dwt[3], color='tab:red')
        
        axarr[4].plot(arr_incl[0], color='tab:blue')
        axarr[4].plot(arr_incl[1], color='tab:orange')
        axarr[4].plot(arr_incl[2], color='tab:green')
        axarr[4].plot(arr_incl[3], color='tab:red')

        # print(f'plot {len(arr_incl[0])}, {len(self.arr_rep)}')
        
        # axarr[5].plot(self.arr_rep, color='tab:blue')
        
        self.plotVerticalLines(axarr, self.list_start_end_night)
        
        axarr[0].set_title(self.filename, loc='left')
        axarr[0].set_ylabel('off')
        axarr[1].set_ylabel('lyi')
        axarr[2].set_ylabel('sit')
        axarr[3].set_ylabel('sta')
        axarr[4].set_ylabel('rep.')
        # axarr[5].set_ylabel('rep.2')
        axarr[4].set_xlabel('samples')
        
        return 0
    
    def plotVerticalLines(self, axarr, list_start_end_night):
        
        arr_indexes = np.array(list_start_end_night)
        
        indexes_ini = arr_indexes[:,0]
        indexes_end = arr_indexes[:,1]
        
        ## vertical lines for 22h00
        for idx in indexes_ini:
            axarr[0].axvline(x = idx, color = 'tab:purple')
            axarr[1].axvline(x = idx, color = 'tab:purple')
            axarr[2].axvline(x = idx, color = 'tab:purple')
            axarr[3].axvline(x = idx, color = 'tab:purple')
            axarr[4].axvline(x = idx, color = 'tab:purple')
        
        ## vertical lines for 8h00
        for idx in indexes_end:
            axarr[0].axvline(x = idx, color = 'tab:olive')
            axarr[1].axvline(x = idx, color = 'tab:olive')
            axarr[2].axvline(x = idx, color = 'tab:olive')
            axarr[3].axvline(x = idx, color = 'tab:olive')
            axarr[4].axvline(x = idx, color = 'tab:olive')
            
        return 0
    
    
    def plotVectorMagnitude(self):
        
        arr_vma = self.df1[self.vec_mag].to_numpy()
        arr_act = self.df1[self.vma_act].to_numpy()
        
        fig, ax = plt.subplots(nrows=2, ncols=1, sharex=True)
        fig.canvas.mpl_connect('key_press_event', self.on_press)
        
        ax[0].plot(arr_vma)
        ax[1].plot(arr_act)
        
        ## plot vertical lines
        arr_indexes = np.array(self.list_start_end_night_original)
        
        indexes_ini = arr_indexes[:,0]
        indexes_end = arr_indexes[:,1]
        
        ## vertical lines for 22h00
        for idx in indexes_ini:
            ax[0].axvline(x = idx, color = 'tab:purple')
            ax[1].axvline(x = idx, color = 'tab:purple')
        ## vertical lines for 8h00
        for idx in indexes_end:
            ax[0].axvline(x = idx, color = 'tab:olive')
            ax[1].axvline(x = idx, color = 'tab:olive')
        
        ax[0].set_title(self.filename)
        
        return 0
    
        
    def getActigraphyData(self):
        return self.df1
        
    def getNightCounts(self):
        return self.df_all_nights
    
    def get_df1(self):
        return self.df1
    
    def get_df_inclinometers(self):
        return self.df_inclinometers
    
    def getName(self):
        return self.name


