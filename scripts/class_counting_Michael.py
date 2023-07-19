from datetime import datetime, timedelta
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

    def __init__(self):
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
        
        self.vma_counts='vma_counts'
        self.off_counts='off_counts'
        self.lyi_counts='lyi_counts'
        self.sit_counts='sit_counts'
        self.sta_counts='sta_counts'
        self.night = 'night'
        
        self.time_ini='20:00:00'
        self.time_end='10:59:59'
        # self.time_ini=datetime.strptime('22:00:00','%H:%M:%S')
        # self.time_end=datetime.strptime('07:59:59','%H:%M:%S')
        
        self.color_day = 'tab:green'
        self.color_night = 'tab:purple'
        
        self.label_time = ' Time'
        self.label_date = 'Date'
        self.time_sec = 'time_sec'

        self.df1 = pd.DataFrame([])
        self.df_activity_indexes = pd.DataFrame([], columns=['idx_ini','idx_end','length'])
        self.df_all_nights = pd.DataFrame()
        # self.df_counts = pd.DataFrame([])
        self.df_inclinometers = pd.DataFrame([])
        self.df_dwt_vma = pd.DataFrame([])
        self.df_nights_dwt_vma = pd.DataFrame([])

        self.delta_samples_incl=1
        self.delta_samples_vma=1
        self.delta_samples = 1
        self.min_vma = 3 # counts
        self.min_samples = 2 # min number of samples inside the window (function: rollingWindow())
        self.window_min = 10 ## window size in min
        self.min_gap_act =15 # seconds
        self.min_gap_rep =600 # seconds (1 min)
        self.arr_fig = [[] for i in range(10)]
        self.arr_axs = [[] for i in range(10)]
        
        self.list_start_end_night=[]
        self.list_start_end_night_original=[]
        self.list_range_roi=[]


    def openFile(self, path, filename):
        self.path = path
        self.filename = filename
        self.df1 = pd.read_csv(self.path+self.filename, header=self.header_location, decimal=',')

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


    def maximumIds(self):
        ## We determine the start and the end of each night with the location of maximum values before and after midnight (0h00). We look for one maximum (start) among the Vector Magnitude values between 20h00 and 23:59:59, and for the other between 00:00:00 and 10:00:00
        
        df = self.df1
        
        time_start = '20:00:00'
        time_end = '10:59:59'
        # time_middle = '03:30:00'
        
        df_all_nights = pd.DataFrame()
        
        dates_list = df[self.label_date].unique().tolist()
        
        id_night=1
        for date0, date1 in zip(dates_list[:-1], dates_list[1:]):
            ## from 22:00:00 to 23:59:59
            df_nightA = df.loc[(df[self.label_date]==date0) & (df[self.label_time] >= time_start)]
            ## from 00:00:00 to 07:59:59
            df_nightB = df.loc[(df[self.label_date]== date1) & (df[self.label_time] <=time_end)] 
            
            ## concatenate partA and partB
            df_night = pd.concat([df_nightA, df_nightB])
            
            ## looking for maximums in the first and second halfs of the night
            ## maximum of the first half
            idx_ini=df_night.iloc[ :len(df_night)//2,:][self.vec_mag].idxmax()
            ## maximum of the second half
            idx_end=df_night.iloc[len(df_night)//2: ,:][self.vec_mag].idxmax()
            
            ## trimming of 15 min after the maximum first half and 15 min before the maximum second half
            trim_delta = int(round((15*60)/self.delta_samples))
            idx_ini = idx_ini + trim_delta
            idx_end = idx_end - trim_delta
            
            ## night duration
            night_duration = (idx_end - idx_ini)*self.delta_samples
            
            self.list_range_roi.append([idx_ini,idx_end, night_duration])
            
            id_night+=1
        
        return 0


    def inclinometersDWT(self):
        
        ## calculate level of decomposition using discrete wavelet transform
        ## subsampling until a sample represent a value between 15 min (900 s) and 20min (1200 s)
        delta_value = self.delta_samples
        ## estimate level for the discrete wavelet transform
        nlevel = 0
        th1 = 900 # seconds
        th2 = 1200 # seconds
        while delta_value < th1:
            delta_value = delta_value * 2
            nlevel+=1
        else:
            pass
            
        ## read inclinometers 
        arr_off = self.df1[self.incl_off].to_numpy()
        arr_lyi = self.df1[self.incl_lyi].to_numpy()
        arr_sit = self.df1[self.incl_sit].to_numpy()
        arr_sta = self.df1[self.incl_sta].to_numpy()

        ## very important avoid any nan value; it could be a missing data in the original recording
        # print(f'mean {np.mean(arr_off)}, {np.mean(arr_lyi)}, {np.mean(arr_sit)}, {np.mean(arr_sta)}')
        # print(f'nan ids: {np.argwhere(np.isnan(arr_off))}, {np.argwhere(np.isnan(arr_lyi))}, {np.argwhere(np.isnan(arr_sit))}, {np.argwhere(np.isnan(arr_sta))}') 
        
        ## apply discrete wavelet transform (DWT)
        waveletname = 'Haar'
        coeff_off = pywt.wavedec(arr_off, waveletname, mode='symmetric', level=nlevel, axis=-1)
        coeff_lyi = pywt.wavedec(arr_lyi, waveletname, mode='symmetric', level=nlevel, axis=-1)
        coeff_sit = pywt.wavedec(arr_sit, waveletname, mode='symmetric', level=nlevel, axis=-1)
        coeff_sta = pywt.wavedec(arr_sta, waveletname, mode='symmetric', level=nlevel, axis=-1)
        
        ## amplitude normalization
        coeff_all = coeff_off[0] + coeff_lyi[0] + coeff_sit[0] + coeff_sta[0]

        mean_coeff = np.mean(coeff_all)

        coeff_off[0] = coeff_off[0]/mean_coeff
        coeff_lyi[0] = coeff_lyi[0]/mean_coeff
        coeff_sit[0] = coeff_sit[0]/mean_coeff
        coeff_sta[0] = coeff_sta[0]/mean_coeff
        coeff_all = coeff_all/mean_coeff
        
        ## pile the inclinometers resultant coefficients (level 10) and select the inclinometer with the maximum value per each sample
        coeff_stack = np.vstack((coeff_off[0],coeff_lyi[0],coeff_sit[0],coeff_sta[0]))
        index_coeff = np.argmax(coeff_stack, axis=0)
        arr_new_off = (index_coeff==0).astype(int)
        arr_new_lyi = (index_coeff==1).astype(int)
        arr_new_sit = (index_coeff==2).astype(int)
        arr_new_sta = (index_coeff==3).astype(int)
        
        ## resampling 'Date' and 'Time'
        arr_date = self.df1[self.label_date].to_numpy()
        arr_time = self.df1[self.label_time].to_numpy()
        
        size_org = len(arr_date)
        size_sampled = len(coeff_off[0])
        last_index = size_org-1
        
        indexes_datetime, delta_sampled = np.linspace(0, last_index, size_sampled, endpoint=True, retstep=True)
        
        idx_samples = np.rint(indexes_datetime).astype(int)
        
        arr_new_date = arr_date[idx_samples]
        arr_new_time = arr_time[idx_samples]
        
        ## grouping the resultant data
        self.df_inclinometers[self.label_date]=arr_new_date
        self.df_inclinometers[self.label_time]=arr_new_time
        self.df_inclinometers[self.dwt_off]=coeff_off[0]
        self.df_inclinometers[self.dwt_lyi]=coeff_lyi[0]
        self.df_inclinometers[self.dwt_sit]=coeff_sit[0]
        self.df_inclinometers[self.dwt_sta]=coeff_sta[0]
        self.df_inclinometers[self.incl_off]=arr_new_off
        self.df_inclinometers[self.incl_lyi]=arr_new_lyi
        self.df_inclinometers[self.incl_sit]=arr_new_sit
        self.df_inclinometers[self.incl_sta]=arr_new_sta
        
        return 0
    
    
    def nightCounts(self):
        
        ## each night has a starting and ending points. The indexes of those points are in the 'list_range_roi'. We use the indexes to get date and time
        id_night = 1
        for indexes in self.list_range_roi:
            
            date_ini = self.df1._get_value(indexes[0],self.label_date)
            date_end = self.df1._get_value(indexes[1],self.label_date)
            
            time_ini = self.df1._get_value(indexes[0],self.label_time)
            time_end = self.df1._get_value(indexes[1],self.label_time)
            
            night_duration = indexes[2]
        
            df_nightA = self.df_inclinometers.loc[(self.df_inclinometers[self.label_date]==date_ini) & (self.df_inclinometers[self.label_time] >= time_ini)]
            ## from 00:00:00 to 07:59:59
            df_nightB = self.df_inclinometers.loc[(self.df_inclinometers[self.label_date]== date_end) & (self.df_inclinometers[self.label_time] <=time_end)] 
            
            df_night = pd.concat([df_nightA, df_nightB], ignore_index=True)
            
            id_start=df_nightA.index.values[0]
            id_end=df_nightB.index.values[-1]
            
            self.list_start_end_night.append([id_start,id_end])
            
            len_night = len(df_night)
            # normalized number of counts per inclinometer
            counts_off=np.round(df_night[self.incl_off].sum()/len_night, 2)
            counts_lyi=np.round(df_night[self.incl_lyi].sum()/len_night, 2)
            counts_sit=np.round(df_night[self.incl_sit].sum()/len_night, 2)
            counts_sta=np.round(df_night[self.incl_sta].sum()/len_night, 2)
            
            repos_labels, repos_data  = self.counting_repositioning(df_night)
            
            counts_data = [id_night,id_start,id_end] + repos_data + [counts_off, counts_lyi, counts_sit, counts_sta, night_duration]
            counts_labels = ['night','id_start','id_end'] + repos_labels + ['counts_off','counts_lyi','counts_sit','counts_sta', 'night_duration (s)']
            
            df_counts_night = pd.DataFrame([counts_data], columns=counts_labels)
            self.df_all_nights = pd.concat([self.df_all_nights, df_counts_night], ignore_index=True)
            
            id_night+=1
        
        return 0
        
        
    def counting_repositioning(self, df):
        
        arr_off = df[self.incl_off].to_numpy()
        arr_lyi = df[self.incl_lyi].to_numpy()
        arr_sit = df[self.incl_sit].to_numpy()
        arr_sta = df[self.incl_sta].to_numpy()
        
        off_lyi=self.counting_per_two_incl(arr_off, arr_lyi)
        off_sit=self.counting_per_two_incl(arr_off, arr_sit)
        off_sta=self.counting_per_two_incl(arr_off, arr_sta)
        
        lyi_off=self.counting_per_two_incl(arr_lyi, arr_off)
        lyi_sit=self.counting_per_two_incl(arr_lyi, arr_sit)
        lyi_sta=self.counting_per_two_incl(arr_lyi, arr_sta)
        
        sit_off=self.counting_per_two_incl(arr_sit, arr_off)
        sit_lyi=self.counting_per_two_incl(arr_sit, arr_lyi)
        sit_sta=self.counting_per_two_incl(arr_sit, arr_sta)
        
        sta_off=self.counting_per_two_incl(arr_sta, arr_off)
        sta_lyi=self.counting_per_two_incl(arr_sta, arr_lyi)
        sta_sit=self.counting_per_two_incl(arr_sta, arr_sit)
    
        return ['off_lyi', 'off_sit', 'off_sta', 'lyi_off', 'lyi_sit', 'lyi_sta', 'sit_off', 'sit_lyi', 'sit_sta', 'sta_off', 'sta_lyi', 'sta_sit'], [off_lyi, off_sit, off_sta, lyi_off, lyi_sit, lyi_sta, sit_off, sit_lyi, sit_sta, sta_off, sta_lyi, sta_sit]
        

    def counting_per_two_incl(self, arr0, arr1):
        arr = (arr0[:-1] == arr1[1:]) & (arr0[:-1]==1)
        return np.sum(arr)
    
    
    def on_press(self, event):
        # print('press', event.key)
        sys.stdout.flush()
        
        if event.key == 'x':
            plt.close('all')
        else:
            pass
         
     
    def plotActigraphy(self):
        self.arr_fig[0], self.arr_axs[0] = plt.subplots(nrows=5, ncols=1, sharex=True)
        self.plotWithColors(self.arr_fig[0], self.arr_axs[0],signals=0)
        ## transform from id values to seconds
        arr_range_roi_sec = np.array(self.list_range_roi) * self.delta_samples
        self.plotVerticalLines(self.arr_axs[0],arr_range_roi_sec)
        return 0
        
    def plotActigraphyMod(self):
        self.arr_fig[1], self.arr_axs[1] = plt.subplots(nrows=5, ncols=1, sharex=True)
        self.plotWithColors(self.arr_fig[1], self.arr_axs[1],signals=1)
        return 0
    

    def plotWithColors(self,fig,ax,signals):
        
        fig.canvas.mpl_connect('key_press_event', self.on_press)
        
        for i in np.arange(5):
            ax[i].cla()
        
        ax[0].set_title(self.filename)
        ax[0].set_ylabel('v.m.')
        ax[1].set_ylabel('off')
        ax[2].set_ylabel('lyi')
        ax[3].set_ylabel('sit')
        ax[4].set_ylabel('sta')

        ax[4].set_xlabel('time (s)')
        
        dates_list = self.df1[self.label_date].unique().tolist()
        
        for date in dates_list:
            df_date = self.df1.loc[self.df1[self.label_date]== date]

            ## from midnight to the end of the night sleep
            df_segment = df_date.loc[df_date[self.label_time]<=self.time_end]
            self.plotSignals(fig, ax, df_segment, self.color_night,signals)
            
            ## from the end of the previous night sleep to the beginning of the next night sleep
            df_segment = df_date.loc[(df_date[self.label_time] > self.time_end) & (df_date[self.label_time] < self.time_ini)]
            self.plotSignals(fig, ax, df_segment, self.color_day,signals)
            
            ## from the beginning of the night sleep to midnight
            df_segment = df_date.loc[df_date[self.label_time] >= self.time_ini]
            self.plotSignals(fig, ax, df_segment, self.color_night,signals)
        
        return 0
            

    def plotSignals(self,fig,ax,df,cr,signals):
        
        x_values = df[self.time_sec]
        
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
        
        self.plotVerticalLines(axarr, self.list_start_end_night)
        
        axarr[0].set_title(self.filename, loc='left')
        axarr[0].set_ylabel('off')
        axarr[1].set_ylabel('lyi')
        axarr[2].set_ylabel('sit')
        axarr[3].set_ylabel('sta')
        axarr[4].set_ylabel('rep.')
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
    
    
    def getActigraphyData(self):
        return self.df1
        
    def getNightCounts(self):
        return self.df_all_nights


