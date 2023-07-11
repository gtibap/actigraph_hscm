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
        
        self.time_ini='22:00:00'
        self.time_end='07:59:59'
        # self.time_ini=datetime.strptime('22:00:00','%H:%M:%S')
        # self.time_end=datetime.strptime('07:59:59','%H:%M:%S')
        
        self.color_day = 'tab:green'
        self.color_night = 'tab:purple'
        
        self.label_time = ' Time'
        self.label_time2 = 'time'
        self.label_date = 'Date'

        self.df1 = pd.DataFrame([])
        self.df_activity_indexes = pd.DataFrame([], columns=['idx_ini','idx_end','length'])
        self.df_all_nights = pd.DataFrame()
        # self.df_counts = pd.DataFrame([])
        self.df_inclinometers = pd.DataFrame([])
        self.df_dwt_vma = pd.DataFrame([])
        self.df_nights_dwt_vma = pd.DataFrame([])

        self.delta_samples_incl=1
        self.delta_samples_vma=1
        self.min_vma = 3 # counts
        self.min_samples = 2 # min number of samples inside the window (function: rollingWindow())
        self.window_min = 10 ## window size in min
        self.min_gap_act =15 # seconds
        self.min_gap_rep =600 # seconds (1 min)
        self.arr_fig = [[] for i in range(10)]
        self.arr_axs = [[] for i in range(10)]
        
        self.list_start_end_night=[]
        self.list_start_end_night_original=[]
        # self.colors=np.array([])


    def openFile(self, path, filename):
        self.path = path
        self.filename = filename
        self.df1 = pd.read_csv(self.path+self.filename, header=self.header_location, decimal=',')
        ## adjust format hour
        self.df1[self.label_time2]=pd.to_datetime(self.df1[self.label_time]).dt.time
        self.df1[self.label_time2]=self.df1[self.label_time2].astype(str)
        # print(self.df1[self.label_time2])
        
        with open(self.path+self.filename) as f:
            for i, line in enumerate(f):             
                if i < 10:
                    list_values = line.split()
                    print (f'line {i} = {line.split()}')
                    if i == 2:
                        ## hh:mm:ss
                        start_time = list_values[2][:8]
                        print(start_time)
                    if i == 3:
                        ## date dd/mm/yyyy
                        start_date = list_values[2][:10]
                        print(start_date)
                        day, month, year = start_date.split('/')
                        start_date = year+'-'+month+'-'+day
                        print(start_date)
                    elif i == 4:
                        ## epoch period hh:mm:ss
                        epoch_period = list_values[3][:8]
                        print(epoch_period)
                    elif i == 5:
                        ## hh:mm:ss
                        download_time = list_values[2][:8]
                        print(download_time)
                    elif i == 6:
                        ## date dd/mm/yyyy
                        download_date = list_values[2][:10]
                        print(download_date)
                        day, month, year = download_date.split('/')
                        download_date = year+'-'+month+'-'+day
                        print(download_date)
                        
                    else:
                        pass
                    
                else:
                    break
            
            start_recording = start_date +' '+ start_time
            end_recording = download_date +' '+ download_time 
            
            print(start_recording)
            print(end_recording)
            
            
            date_range = pd.date_range(start =start_recording, end =end_recording, periods = len(self.df1))
            print(date_range)

                
                
                    
        
        # df=pd.date_range("00:00:00", "23:59:59", freq="240s")
        # print(df)
        

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
        
        ## retrieve only data of nights; from 22h to 8h
        df_nights = self.nightsDataFrame(self.df1)
        
        list_nights = df_nights[self.night].unique().tolist()

        list_mov_night = []
        for num_night in list_nights:
            df = df_nights.loc[df_nights[self.night]==num_night]
            # ## number of movements estimation divided by the window size
            # num_mov = df[self.vma_act].sum() / np.sum(win)
            # ## max. possible number of movements
            # num_max = len(df)/np.sum(win)
            # ## number of movements normalization 
            # list_mov_night.append(num_mov/num_max)
            ## mean activity every night
            list_mov_night.append(df[self.vma_act].mean())
        
        print(f'mean mov: {np.around(list_mov_night,2)}')
        
        # fig, ax = plt.subplots(nrows=3, ncols=1, sharex=True)
        # fig.canvas.mpl_connect('key_press_event', self.on_press)
        
        # ax[0].plot(arr_vma)
        # ax[1].plot(arr_vma_mod)
        # ax[2].plot(arr_vma_bin)
        
        return np.around(list_mov_night,3)
        
        
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
            
        # fig, ax = plt.subplots(nrows=1, ncols=1)
        # fig.canvas.mpl_connect('key_press_event', self.on_press)
        # sns.boxplot(x='night', y=self.dwt_vma, data=self.df_nights_dwt_vma, ax=ax, color="skyblue")
        
        # self.nightStatisticsVM()
        
        return df_all_nights
    
        


    # def binaryClosing(self, arr_in, dist):
        # ## structuring element: odd number
        # gap = int((2*dist)+1)
        # struct1 = np.ones(gap).astype(int)
        
        # arr_out= ndimage.binary_closing(arr_in, structure=struct1).astype(int)
        
        # return arr_out

    

    # def vecMagCounting(self):
        
        # ## read inclinometers 
        # arr_vma = self.df1[self.vec_mag].to_numpy()
        # arr_vma_binary = (arr_vma > self.min_vma).astype(int)
        
        # arr_vma_mod = self.binaryClosing(arr_vma_binary, int(self.min_gap_act/2))
        
        
        # fig, ax = plt.subplots(nrows=2, ncols=1, sharex=True)
        # fig.canvas.mpl_connect('key_press_event', self.on_press)
        
        # ax[0].plot(arr_vma)
        # ax[1].plot(arr_vma_mod)
        
        # return 0


    # def vecMagDWT(self, nlevel):
        
        ## read inclinometers 
        # arr_vma = self.df1[self.vec_mag].to_numpy()
        # arr_vma = (arr_vma >=3).astype(int)
        ## apply discrete wavelet transform (DWT)
        # waveletname = 'Haar'
        # coeff_vma = pywt.wavedec(arr_vma, waveletname, mode='symmetric', level=nlevel, axis=-1)
        
        ## resampling 'Date' and 'Time'
        # arr_date = self.df1[self.label_date].to_numpy()
        # arr_time = self.df1[self.label_time].to_numpy()
       
        # size_org = len(arr_date)
        # size_sampled = len(coeff_vma[0])
        # last_index = size_org-1

        # indexes_datetime, delta_sampled = np.linspace(0, last_index, size_sampled, endpoint=True, retstep=True)
        # print(f'delta_sampled dwt: {arr_date.shape}, {arr_time.shape}, {delta_sampled}')
        
        # idx_samples = np.rint(indexes_datetime).astype(int)
        
        # arr_new_date = arr_date[idx_samples]
        # arr_new_time = arr_time[idx_samples] 
        
        # self.delta_samples_vma = 2**nlevel
        # arr_new_date = arr_date[::self.delta_samples_vma]
        # arr_new_time = arr_time[::self.delta_samples_vma]
        
        ## grouping the resultant data
        # self.df_dwt_vma[self.label_date]=arr_new_date
        # self.df_dwt_vma[self.label_time]=arr_new_time
        # self.df_dwt_vma[self.dwt_vma]=coeff_vma[0]
        
        # print(self.df_dwt_vma)
        
        # fig, ax = plt.subplots(nrows=2, ncols=1)
        # fig.canvas.mpl_connect('key_press_event', self.on_press)
        
        # ax[0].plot(arr_vma)
        
        # ax[1].plot(coeff_vma[0])
        
        
        # ax[1].plot(filtered)
        
        # fig2, ax2 = plt.subplots(nrows=1, ncols=1)
        # fig2.canvas.mpl_connect('key_press_event', self.on_press)
        # ax2.boxplot(coeff_vma[0])
        
        # return 0
    
     
    # def nightCountsVM(self, df):
        
        # dates_list = self.df_dwt_vma[self.label_date].unique().tolist()
        
        # id_night=1
        # for date0, date1 in zip(dates_list[:-1], dates_list[1:]):
            # ## from 22:00:00 to 23:59:59
            # df_nightA = self.df_dwt_vma.loc[(self.df_dwt_vma[self.label_date]==date0) & (self.df_dwt_vma[self.label_time] >= self.time_ini)]
            # ## from 00:00:00 to 07:59:59
            # df_nightB = self.df_dwt_vma.loc[(self.df_dwt_vma[self.label_date]== date1) & (self.df_dwt_vma[self.label_time] <=self.time_end)] 
            
            # df_night = pd.concat([df_nightA, df_nightB], ignore_index=True)
            # df_night['night'] = id_night
            
            # self.df_nights_dwt_vma = pd.concat([self.df_nights_dwt_vma, df_night], ignore_index=True)
            
            # id_night+=1
            
        # fig, ax = plt.subplots(nrows=1, ncols=1)
        # fig.canvas.mpl_connect('key_press_event', self.on_press)
        # sns.boxplot(x='night', y=self.dwt_vma, data=self.df_nights_dwt_vma, ax=ax, color="skyblue")
        
        # self.nightStatisticsVM()
        
        # return 0

    
    # def nightStatisticsVM(self):
        
        # list_nights = self.df_nights_dwt_vma['night'].unique().tolist()
        
        # df_vma_stats=pd.DataFrame()
        # for night in list_nights:
            # df_n = self.df_nights_dwt_vma.loc[self.df_nights_dwt_vma['night']==night]
            # arr_dwt_vma = df_n[self.dwt_vma].to_numpy()
            # print(type(arr_dwt_vma), arr_dwt_vma, 'sum:',np.sum(arr_dwt_vma))
            # list_results = np.percentile(arr_dwt_vma, [25,50,75,100]).tolist()
            # list_results.append(np.sum(arr_dwt_vma))
            # print(list_results)
            # df_s = pd.DataFrame([list_results], columns=['q1','q2','q3','q4', 'sum'])
            # df_s['night']=night
            
            # df_vma_stats=pd.concat([df_vma_stats, df_s], ignore_index=True)
        
        # print(df_vma_stats)
        
        # return 0
        
        
    
    
    # def nightCountsVMOriginal(self):
        
        # df_nights_vma_org = pd.DataFrame()
        # dates_list = self.df1[self.label_date].unique().tolist()
        
        # id_night=1
        # for date0, date1 in zip(dates_list[:-1], dates_list[1:]):
            # ## from 22:00:00 to 23:59:59
            # df_nightA = self.df1.loc[(self.df1[self.label_date]==date0) & (self.df1[self.label_time] >= self.time_ini)]
            # ## from 00:00:00 to 07:59:59
            # df_nightB = self.df1.loc[(self.df1[self.label_date]== date1) & (self.df1[self.label_time] <=self.time_end)] 
            
            # df_night = pd.concat([df_nightA, df_nightB], ignore_index=True)
            # df_night['night'] = id_night
            
            # df_nights_vma_org = pd.concat([df_nights_vma_org, df_night], ignore_index=True)
            
            # id_night+=1
            
        # print(self.df_nights_vma)

        # fig, ax = plt.subplots(nrows=1, ncols=1)
        # fig.canvas.mpl_connect('key_press_event', self.on_press)
        # sns.boxplot(x='night', y=self.vec_mag, data=df_nights_vma_org, ax=ax)
        
        # return 0
    
    
    
  
    

    def inclinometersDWT(self, nlevel):
        
        ## read inclinometers 
        arr_off = self.df1[self.incl_off].to_numpy()
        arr_lyi = self.df1[self.incl_lyi].to_numpy()
        arr_sit = self.df1[self.incl_sit].to_numpy()
        arr_sta = self.df1[self.incl_sta].to_numpy()
        
        ## apply discrete wavelet transform (DWT)
        waveletname = 'Haar'
        coeff_off = pywt.wavedec(arr_off, waveletname, mode='symmetric', level=nlevel, axis=-1)
        coeff_lyi = pywt.wavedec(arr_lyi, waveletname, mode='symmetric', level=nlevel, axis=-1)
        coeff_sit = pywt.wavedec(arr_sit, waveletname, mode='symmetric', level=nlevel, axis=-1)
        coeff_sta = pywt.wavedec(arr_sta, waveletname, mode='symmetric', level=nlevel, axis=-1)
        
        ## amplitude normalization
        coeff_all = coeff_off[0] + coeff_lyi[0] + coeff_sit[0] + coeff_sta[0]
        mean_coeff = coeff_all.mean()
        std_coeff = coeff_all.std()
        # print('mean, std: ', mean_coeff, std_coeff)
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
        ## from 22:00:00 until 07:59:59 (next day)
        
        dates_list = self.df_inclinometers[self.label_date].unique().tolist()
        
        id_night=1
        for date0, date1 in zip(dates_list[:-1], dates_list[1:]):
            
            ## from 22:00:00 to 23:59:59
            df_nightA = self.df_inclinometers.loc[(self.df_inclinometers[self.label_date]==date0) & (self.df_inclinometers[self.label_time] >= self.time_ini)]
            ## from 00:00:00 to 07:59:59
            df_nightB = self.df_inclinometers.loc[(self.df_inclinometers[self.label_date]== date1) & (self.df_inclinometers[self.label_time] <=self.time_end)] 
            
            df_night = pd.concat([df_nightA, df_nightB], ignore_index=True)
            
            # print(f'indexes: {df_nightA.index.values[0]}:{df_nightB.index.values[-1]}')
            id_start=df_nightA.index.values[0]
            id_end=df_nightB.index.values[-1]
            
            self.list_start_end_night.append([id_start,id_end])
            
            len_night = len(df_night)
            # normalized number of counts per inclinometer
            counts_off=df_night[self.incl_off].sum()/len_night
            counts_lyi=df_night[self.incl_lyi].sum()/len_night
            counts_sit=df_night[self.incl_sit].sum()/len_night
            counts_sta=df_night[self.incl_sta].sum()/len_night
            
            repos_labels, repos_data  = self.counting_repositioning(df_night)
            
            counts_data = [id_night,id_start,id_end] + repos_data + [counts_off, counts_lyi, counts_sit, counts_sta]
            counts_labels = ['night','id_start','id_end'] + repos_labels + ['counts_off','counts_lyi','counts_sit','counts_sta']
            
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
        return 0
        
    def plotActigraphyMod(self):
        self.arr_fig[1], self.arr_axs[1] = plt.subplots(nrows=5, ncols=1, sharex=True)
        self.plotWithColors(self.arr_fig[1], self.arr_axs[1],signals=1)
        return 0
    

    def plotWithColors(self,fig,ax,signals):
        
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
        
        dates_list = self.df1[self.label_date].unique().tolist()
        
        # print(self.filename,' dates: ',dates_list)
        
        for date in dates_list:
            df_date = self.df1.loc[self.df1[self.label_date]== date]

            ## from 00:00:00 to 07:59:59
            df_segment = df_date.loc[df_date[self.label_time2]<=self.time_end]
            self.plotSignals(fig, ax, df_segment, self.color_night,signals)
            
            # print(f'date {date}')
            # print(df_segment)

            # ## from 08:00:00 to 21:59:59
            # df_segment = df_date.loc[(df_date[self.label_time] > self.time_end) & (df_date[self.label_time] < self.time_ini)]
            # self.plotSignals(fig, ax, df_segment, self.color_day,signals)
            
            # ## from 22:00:00 to 23:59:59
            # df_segment = df_date.loc[df_date[self.label_time] >= self.time_ini]
            # self.plotSignals(fig, ax, df_segment, self.color_night,signals)
        
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


