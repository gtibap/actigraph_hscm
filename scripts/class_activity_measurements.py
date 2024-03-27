from datetime import datetime
from scipy import signal

import numpy as np
import pandas as pd
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as st
from scipy.stats import skewnorm

import os
import re
import sys

class Activity_Measurements:


    def __init__(self, name):
        
        # print('Activity Measurements object constructor initialization')
        
        self.name = name

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
        
        # self.time_ini='21:00:00'
        # self.time_end='09:00:00'
        self.time_ini='23:00:00'
        self.time_end='07:00:00'
        
        self.list_days=['d1','d2','d3','d4','d5']
        self.list_nights=['n1','n2','n3','n4','n5']

        
        self.color_day = 'tab:green'
        self.color_night = 'tab:purple'
        
        self.label_time = ' Time'
        self.label_date = 'Date'
        self.time_sec = 'time_sec'
        self.label_day_night = 'day_night'
        self.label_binary_day_night = 'binary_day_night'
        self.label_incl = 'Inclinometers Activity'
        self.label_duration = 'duration'
        
        self.vma_a='vma_a'
        self.vma_b='vma_b'
        self.inc_a='inc_a'
        self.inc_b='inc_b'
        
        self.df1 = pd.DataFrame([])
        self.df_days  = pd.DataFrame(columns  =['sample_size', 'vma_mean', 'inc_mean'])
        self.df_nights= pd.DataFrame(columns=['sample_size', 'vma_mean', 'inc_mean'])
        self.df_incl_filtered = pd.DataFrame()
        self.df_act = pd.DataFrame(columns=[self.label_duration, self.label_day_night])
        self.df_imm = pd.DataFrame(columns=[self.label_duration, self.label_day_night])

        
        
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
        print(self.df1)
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


    def immobility(self):
        ## spending time of continous immobility and continuous activity
        ## immobility identifies changes of activity-inactivity and inactivity-activity
        ## identifies duration of inactivity segments
        ## a histogram of inactivity segments duration is plotted after their calculation
        
        arr_vma = self.df1[self.vec_mag].to_numpy()
        labels_day_night = self.df1[self.label_day_night].to_numpy()
        
        # print(f'vma: {len(arr_vma)}, {len(labels_day_night)}')
        # print(f'vma: {arr_vma}, {labels_day_night}')
        
        ## values of Vector Magnitude greater than zero means activity; zero means immobility
        arr_vma = (arr_vma > 0).astype(int)
        
        ## True means change in state: from immobility to activity or from activity to immobility
        arr = (arr_vma[:-1] != arr_vma[1:])
        ## adding a zero at the begining to make the output array same size than the input one
        arr = np.insert(arr,0,0).astype(int)
        
        ## get indices values non-zero; where changes in state happened
        ids_nz = np.flatnonzero(arr)
        ## insert index for the first and last samples; extremes of the input array
        ids_nz = np.insert(ids_nz,0,0)
        ids_nz = np.insert(ids_nz, len(ids_nz), len(arr_vma))
        
        ## difference between two neiborn values
        arr_diff = np.diff(ids_nz)
        
        ## to associate periods of immobility to days and nights
        labels_dn = labels_day_night[ids_nz[:-1]]
        
        
        ## if VM starts with zero, then the immobility values are with even indexes starting with 0
        if arr_vma[0] == 0:
            ## immobility data
            self.df_imm[self.label_duration] = arr_diff[::2]
            self.df_imm[self.label_day_night] = labels_dn[::2]
            ## activity data
            self.df_act[self.label_duration] = arr_diff[1::2]
            self.df_act[self.label_day_night] = labels_dn[1::2]
        else:
            ## immobility data
            self.df_imm[self.label_duration] = arr_diff[1::2]
            self.df_imm[self.label_day_night] = labels_dn[1::2]
            ## activity data
            self.df_act[self.label_duration] = arr_diff[::2]
            self.df_act[self.label_day_night] = labels_dn[::2]
        
        # print(f'imm:\n{self.df_imm}')
        # print(f'act:\n{self.df_act}')
        
        return 0

    def boxplots(self):
        
        df_imm_bp = pd.DataFrame(columns=['time','day_night','cycle'])
        df_act_bp = pd.DataFrame(columns=['time','day_night','cycle'])
        
        labels_list = self.df_imm[self.label_day_night].unique().tolist()
        print(f'days and nights: {labels_list}')
    
        for label in labels_list:
            
            df_temp_imm = pd.DataFrame()
            df_temp_act = pd.DataFrame()
            
            if (label in self.list_days) or (label in self.list_nights):
                
                # print(f'{label}:    ')
            
                df_i = self.df_imm[self.df_imm[self.label_day_night]== label]
                df_temp_imm['time']=df_i[self.label_duration].to_numpy()
                # print(f'x_imm: {x_imm}')
                
                df_a = self.df_act[self.df_act[self.label_day_night]== label]
                df_temp_act['time']=df_a[self.label_duration].to_numpy()
                
                if label.startswith('d'):
                    df_temp_imm['day_night']='d'
                    df_temp_act['day_night']='d'
                else:
                    df_temp_imm['day_night']='n'
                    df_temp_act['day_night']='n'
                ## cycle could be 1,2, ..., or 5
                df_temp_imm['cycle']=label[-1]
                df_temp_act['cycle']=label[-1]
                
                df_imm_bp = pd.concat([df_imm_bp, df_temp_imm], ignore_index=True)
                df_act_bp = pd.concat([df_act_bp, df_temp_act], ignore_index=True)

            else:
                pass
                
        print(f'New dataframes:\n{df_imm_bp}\n{df_act_bp}')
        
        
        fig, ax = plt.subplots(figsize=(12, 6))
        fig.canvas.mpl_connect('key_press_event', self.on_press)
        fig.canvas.draw()
        
        ax = sns.boxplot(data=df_imm_bp, x='cycle', y="time", hue="day_night", palette="pastel")
        
        return 0
        


    def statistics(self):
        
        list_ratio_act_d=[]
        list_ratio_imm_d=[]
        list_ratio_act_n=[]
        list_ratio_imm_n=[]
        list_thr1_d=[]
        list_thr2_d=[]
        list_thr1_n=[]
        list_thr2_n=[]
        
        
        ## spending time of both detected activity and immobility
        labels_list = self.df_imm[self.label_day_night].unique().tolist()
        # print(f'days and nights: {labels_list}')
        
        df_imm_all=pd.DataFrame()
        df_ratio_d=pd.DataFrame()
        df_ratio_n=pd.DataFrame()
    
        for label in labels_list:
            
            if (label in self.list_days) or (label in self.list_nights):
                
                # print(f'{label}:    ')
            
                ## immobility day or night
                df_i = self.df_imm[self.df_imm[self.label_day_night]== label]
                x_imm=df_i[self.label_duration].to_numpy()
                # print(f'x_imm: {x_imm}')
                
                ## activity day or night
                df_a = self.df_act[self.df_act[self.label_day_night]== label]
                x_act=df_a[self.label_duration].to_numpy()
                # print(f'x_act: {x_act}')
                
                ## description of data distribution using quartiles Q0, Q1, Q2, Q3, Q4
                # q_act = np.percentile(x_act, [0, 25, 50, 75, 100])
                # q_imm = np.percentile(x_imm, [0, 25, 50, 75, 100])
                
                # print(f'stats:\nact: {q_act}\nimm:{q_imm}')

                ## calculate percentages of spending time
                imm_sum = np.sum(x_imm)
                act_sum = np.sum(x_act)
                ref_sum = imm_sum + act_sum

                ratio_imm = imm_sum/ref_sum
                ratio_act = act_sum/ref_sum
                
                # print(f'summing of act, imm, total: {act_sum}, {imm_sum}, {ref_sum}')
                # print(f'sum act imm: {label} {round(100*ratio_act,2)} %, {round(100*ratio_imm,2)} %')
                
                # row = [label, round(100*ratio_act,2), round(100*ratio_imm,2)] 
                # new_df = pd.DataFrame([row], columns=['label', '%act', '%imm'])
                # df_ref_all = pd.concat([df_ref_all, new_df], axis=0, ignore_index=True)
                
                # arr_threshold_imm = 60*np.array([10,30,60])  ## numbers inside array in minutes, multiply by 60 to obtain values in seconds
                
                # arr_threshold_imm = np.insert(arr_threshold_imm,0,0)
                # arr_threshold_imm = np.insert(arr_threshold_imm, len(arr_threshold_imm), np.max(x_imm))
                
                # print(f'threshold_imm: {arr_threshold_imm}')
                
                # df_table_imm = pd.DataFrame()
                
                # cont=0
                # for thr_0, thr_1 in zip(arr_threshold_imm[:-1], arr_threshold_imm[1:]):
                    # outliers_imm = x_imm[(x_imm > thr_0) & (x_imm <= thr_1)]
                    # print(f'outliers_imm {thr_0}, {thr_1}: {outliers_imm}')
                    
                    # num_samples = len(outliers_imm)
                    # time_samples= np.sum(outliers_imm)
                    # per_samples = round(100*(time_samples / imm_sum),2) 
                    
                    # values_col = [num_samples, time_samples, per_samples]
                    # df_table_imm[cont] = values_col
                    # cont+=1
                
                # df_table_imm['labels']=['samples','time','percentage']
                # df_table_imm['day_night']=label
                
                # print(f'table imm:\n{df_table_imm}')
                # print(f'100 %: {df_table_imm.iloc[2,:].sum()}')
                
                # df_imm_all = pd.concat([df_imm_all, df_table_imm], ignore_index=True)
                    
                ## immobility samples greater than a threshold
                thr=15*60 ## 15 min * 60 s/min
                outliers_imm = x_imm[x_imm >= thr]
                ratio_thr0 = np.sum(outliers_imm)/ref_sum    
                
                ## immobility samples greater than a threshold
                thr=30*60 ## 30 min * 60 s/min
                outliers_imm = x_imm[x_imm >= thr]
                ratio_thr1 = np.sum(outliers_imm)/ref_sum
                
                thr=60*60 ## 60 min * 60 s/min
                outliers_imm = x_imm[x_imm >= thr]
                ratio_thr2 = np.sum(outliers_imm)/ref_sum
                
                thr=120*60 ## 120 min * 60 s/min
                outliers_imm = x_imm[x_imm >= thr]
                ratio_thr3 = np.sum(outliers_imm)/ref_sum
                
                
                # outliers_act = x_act[x_act > (q_act[3]+1.5*(q_act[3]-q_act[1]))]
                
                # outliers_act = x_act[x_act > (q_act[3]+1.5*(q_act[3]-q_act[1]))]
                # sum_outliers_act = np.sum(outliers_act)
                # print(f'outliers act: {outliers_act}, {sum_outliers_act}, {sum_outliers_act/act_sum},')
                
                # threshold_imm = q_imm[3]+1.5*(q_imm[3]-q_imm[1])
                # outliers_imm = x_imm[x_imm > threshold_imm]
                
                # sum_outliers_imm = np.sum(outliers_imm)
                # print(f'threshold outliers imm: {threshold_imm}')
                # print(f'outliers imm: {outliers_imm}, {sum_outliers_imm}, {sum_outliers_imm/imm_sum},')
                
                row = [label, round(100*ratio_act,2), round(100*ratio_imm,2), round(100*ratio_thr0,2), round(100*ratio_thr1,2), round(100*ratio_thr2,2), round(100*ratio_thr3,2)] 
                
                new_df = pd.DataFrame([row], columns=['label', '%act', '%imm_total', '%imm_15min', '%imm_30min', '%imm_60min', '%imm_120min'])
                
                if label.startswith('d'):
                    # list_ratio_act_d.append(ratio_act)
                    # list_ratio_imm_d.append(ratio_imm)
                    # list_thr1_d.append(ratio_thr1)
                    # list_thr2_d.append(ratio_thr2)
                    
                    df_ratio_d = pd.concat([df_ratio_d, new_df], axis=0, ignore_index=True)
                
                else:
                    # list_ratio_act_n.append(ratio_act)
                    # list_ratio_imm_n.append(ratio_imm)
                    # list_thr1_n.append(ratio_thr1)
                    # list_thr2_n.append(ratio_thr2)
                    
                    df_ratio_n = pd.concat([df_ratio_n, new_df], axis=0, ignore_index=True)
                    list_ratio_act_n.append(row[1])
                    
                    
            else:
                pass
        
        # print(f'df_ratio_d:\n{df_ratio_d}\n{df_ratio_d.median(numeric_only=True)}\n{df_ratio_d.median(numeric_only=True).tolist()}')
        # print(f'df_ratio_n:\n{df_ratio_n}\n{df_ratio_n.median(numeric_only=True)}\n{df_ratio_n.median(numeric_only=True).tolist()}')
                
        # print(f'df_imm_all imm:\n{df_imm_all}')
        
        # print(f'list ratio:\n{list_ratio_act_d}\n{list_ratio_imm_d}\n{list_ratio_act_n}\n{list_ratio_imm_n}')
        ## average of both activity and immobility
        # print(f'average ratio:\n \
        # {np.mean(list_ratio_act_d)}, {np.std(list_ratio_act_d)}\n \
        # {np.mean(list_ratio_imm_d)}, {np.std(list_ratio_imm_d)}\n \
        # {np.mean(list_ratio_act_n)}, {np.std(list_ratio_act_n)}\n \
        # {np.mean(list_ratio_imm_n)}, {np.std(list_ratio_imm_n)}')
        
        median_d = df_ratio_d.median(numeric_only=True).tolist()
        median_n = df_ratio_n.median(numeric_only=True).tolist()
        
        return median_d, median_n, list_ratio_act_n
        

    def histogram_immobility(self):
        

        fig1, ax1 = plt.subplots(nrows=1, ncols=2, sharex=True, sharey=True, figsize=(16, 8))
        fig1.canvas.mpl_connect('key_press_event', self.on_press)
        
        fig2, ax2 = plt.subplots(nrows=1, ncols=2, sharex=True, sharey=True, figsize=(16, 8))
        fig2.canvas.mpl_connect('key_press_event', self.on_press)
        
        ## plot histograms day by day and night by night
        labels_list = self.df_imm[self.label_day_night].unique().tolist()
        
        for label in labels_list:
            
            if (label in self.list_days) or (label in self.list_nights):
            
                df_imm = self.df_imm[self.df_imm[self.label_day_night]== label]
                x_imm=df_imm[self.label_duration].to_numpy()
                
                df_act = self.df_act[self.df_act[self.label_day_night]== label]
                x_act=df_act[self.label_duration].to_numpy()
                
                binwidth_imm = 60
                bins_imm=range(min(x_imm), max(x_imm) + binwidth_imm, binwidth_imm)
                
                binwidth_act = 1
                bins_act=range(min(x_act), max(x_act) + binwidth_act, binwidth_act)
                
                if label.startswith('d'):
                    ax1[0].hist(x_imm, density=False, bins=bins_imm)
                    ax2[0].hist(x_act, density=False, bins=bins_act)
                else:
                    ax1[1].hist(x_imm, density=False, bins=bins_imm)
                    ax2[1].hist(x_act, density=False, bins=bins_act)
        
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
        print(f'arr_inc, df1: {len(arr_inc)}, {len(self.df1)}')
        self.df1[self.label_incl] = arr_inc
        
        
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
        
    def getName(self):
        return self.name

