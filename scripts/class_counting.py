from scipy import ndimage
from scipy import signal
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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
        self.df1 = pd.DataFrame([])
        self.df_counts = pd.DataFrame([])
        self.df_activity_indexes = pd.DataFrame([], columns=['idx_ini','idx_end','length'])
        self.min_vma = 3 # counts
        self.min_gap_act =10 # seconds
        self.min_gap_rep =600 # seconds (1 min)
        self.arr_fig = [[] for i in range(10)]
        self.arr_axs = [[] for i in range(10)]
        # self.colors=np.array([])


    def openFile(self, path, filename):
        self.path = path
        self.filename = filename
        self.df1 = pd.read_csv(self.path+self.filename, header=self.header_location, decimal=',')
        # print(self.df1.shape, self.df1.size, len(self.df1))
        return 0

    def countChanges(self):
        self.vectorMagMatMorpho()
        self.inclinometerMatMorpho()
        self.inclinometersStateChanging()
        self.nightCounts()
        
        return 0

    def vectorMagMatMorpho(self):
        arr_vma = self.df1[self.vec_mag].to_numpy()
        arr_vma = (arr_vma > self.min_vma).astype(int)
        arr_vma_mod = self.closingOpening(arr_vma, self.min_gap_act)
        self.df1[self.vma_mod] = arr_vma_mod
        return 0

    
    def inclinometerMatMorpho(self):
        arr_off = self.df1[self.incl_off].to_numpy()
        arr_lyi = self.df1[self.incl_lyi].to_numpy()
        arr_sit = self.df1[self.incl_sit].to_numpy()
        arr_sta = self.df1[self.incl_sta].to_numpy()
        
        arr_off_mod = self.closingOpening(arr_off,self.min_gap_rep)
        arr_lyi_mod = self.closingOpening(arr_lyi,self.min_gap_rep)
        arr_sit_mod = self.closingOpening(arr_sit,self.min_gap_rep)
        arr_sta_mod = self.closingOpening(arr_sta,self.min_gap_rep)
        
        self.df1[self.off_mod] = arr_off_mod
        self.df1[self.lyi_mod] = arr_lyi_mod
        self.df1[self.sit_mod] = arr_sit_mod
        self.df1[self.sta_mod] = arr_sta_mod
    
        return 0
    
    
    def closingOpening(self, arr_inc, dist):
        ## structuring element: odd number
        gap = int((2*dist)+1)
        struct1 = np.ones(gap).astype(int)
        
        arr_clo= ndimage.binary_closing(arr_inc, structure=struct1).astype(int)
        arr_ope= ndimage.binary_opening(arr_clo, structure=struct1).astype(int)
        return arr_ope
    
        
    def inclinometersStateChanging(self):
        
        arr_vma = self.df1[self.vma_mod].to_numpy()
        arr_off = self.df1[self.off_mod].to_numpy()
        arr_lyi = self.df1[self.lyi_mod].to_numpy()
        arr_sit = self.df1[self.sit_mod].to_numpy()
        arr_sta = self.df1[self.sta_mod].to_numpy()
        
        ## int to bool: any value greater than min_value vector magnitude (min_vm)
        # arr_vma = arr_vma > self.min_vma

        self.df1[self.vma_act] = self.stateChanging(arr_vma)
        self.df1[self.off_act] = self.stateChanging(arr_off)
        self.df1[self.lyi_act] = self.stateChanging(arr_lyi)
        self.df1[self.sit_act] = self.stateChanging(arr_sit)
        self.df1[self.sta_act] = self.stateChanging(arr_sta)
        # act_vma = self.stateChanging(arr_vma)
        
        return 0
        
        
    def stateChanging(self, arr_incl):
        changes_activity = arr_incl[:-1] != arr_incl[1:]
        changes_activity = np.concatenate(([0],changes_activity), axis=None)
        return changes_activity
        

    def nightCounts(self):
        
        dates_list = self.df1[self.label_date].unique().tolist()
        
        night_list=[]
        counts_vma=[]
        counts_off=[]
        counts_lyi=[]
        counts_sit=[]
        counts_sta=[]
        id_night=1
        # print(self.filename,' dates: ',dates_list)
        for date0, date1 in zip(dates_list[:-1], dates_list[1:]):
            
            ## from 22:00:00 to 23:59:59
            df_nightA = self.df1.loc[(self.df1[self.label_date]== date0) & (self.df1[self.label_time] > self.time_ini)]
            ## from 00:00:00 to 07:59:59
            df_nightB = self.df1.loc[(self.df1[self.label_date]== date1) & (self.df1[self.label_time] <=self.time_end)] 
            
            counts_vma.append(df_nightA[self.vma_act].sum() + df_nightB[self.vma_act].sum())
            counts_off.append(df_nightA[self.off_act].sum() + df_nightB[self.off_act].sum())
            counts_lyi.append(df_nightA[self.lyi_act].sum() + df_nightB[self.lyi_act].sum())
            counts_sit.append(df_nightA[self.sit_act].sum() + df_nightB[self.sit_act].sum())
            counts_sta.append(df_nightA[self.sta_act].sum() + df_nightB[self.sta_act].sum())

            night_list.append(id_night)
            id_night+=1
        
        self.df_counts[self.night]=night_list
        self.df_counts[self.vma_counts]=counts_vma
        self.df_counts[self.off_counts]=counts_off
        self.df_counts[self.lyi_counts]=counts_lyi
        self.df_counts[self.sit_counts]=counts_sit
        self.df_counts[self.sta_counts]=counts_sta
        
        return 0

    
    def rollingWindow(self):
        
        dates_list = self.df1[self.label_date].unique().tolist()
        
        df_loc = self.df1.loc[(self.df1[self.label_date]>=dates_list[1]) & (self.df1[self.label_date]<=dates_list[2])]
        
        arr_off = df_loc[self.incl_off].to_numpy()
        arr_lyi = df_loc[self.incl_lyi].to_numpy()
        arr_sit = df_loc[self.incl_sit].to_numpy()
        arr_sta = df_loc[self.incl_sta].to_numpy()
        
        ## window size: from 2 hours (original data) to the decomposition scale of dwt_level (2**dwt_level)
        hours = 1/3 ## number of hours 1/3 h = 20 min
        sph = 3600 ## seconds per hour
        window_size = int(sph*hours)
        print('window size (s): ', window_size)
        ## window to average values (same weight)
        win = signal.windows.boxcar(window_size)
        
        off_filtered = signal.convolve(arr_off, win, mode='same') / sum(win)
        lyi_filtered = signal.convolve(arr_lyi, win, mode='same') / sum(win)
        sit_filtered = signal.convolve(arr_sit, win, mode='same') / sum(win)
        sta_filtered = signal.convolve(arr_sta, win, mode='same') / sum(win)
        
        
        incl_stack = np.vstack((off_filtered,lyi_filtered,sit_filtered,sta_filtered))
        index_incl = np.argmax(incl_stack, axis=0)
        
        index_off = (index_incl==0).astype(int)
        index_lyi = (index_incl==1).astype(int)
        index_sit = (index_incl==2).astype(int)
        index_sta = (index_incl==3).astype(int)

        
        fig, axarr = plt.subplots(nrows=5, ncols=1, sharex=True)
        
        axarr[0].plot(off_filtered)
        axarr[1].plot(lyi_filtered)
        axarr[2].plot(sit_filtered)
        axarr[3].plot(sta_filtered)
        axarr[4].plot(index_off)
        axarr[4].plot(index_lyi)
        axarr[4].plot(index_sit)
        axarr[4].plot(index_sta)
        
        return 0

    def waveletTransform(self, nlevel):
        
        
        dates_list = self.df1[self.label_date].unique().tolist()
        
        # df_loc = self.df1.loc[(self.df1[self.label_date]>=dates_list[1]) & (self.df1[self.label_date]<=dates_list[2])]
        df_loc = self.df1
        
        ## samples 22h and 8h
        
        df_ini = df_loc.loc[df_loc[self.label_time]==self.time_ini]
        df_end = df_loc.loc[df_loc[self.label_time]==self.time_end]
        
        # print(df_ini)
        # print(df_ini.index.values)
        # print(df_end)
        # print(df_end.index.values)
        
        index_0 = df_loc.index.values[0]
        
        indexes_ini = df_ini.index.values - index_0
        indexes_end = df_end.index.values - index_0
        
        indexes_ini = (indexes_ini / (2**nlevel)).astype(int)
        indexes_end = (indexes_end / (2**nlevel)).astype(int) 
        
        arr_off = df_loc[self.incl_off].to_numpy()
        arr_lyi = df_loc[self.incl_lyi].to_numpy()
        arr_sit = df_loc[self.incl_sit].to_numpy()
        arr_sta = df_loc[self.incl_sta].to_numpy()
        
        # fig, ax = plt.subplots(figsize=(6,1))
        # ax.set_title("Original Signal: ")
        # ax.plot(data)

        waveletname = 'Haar'
        dwt_level = nlevel
        coeff_off = pywt.wavedec(arr_off, waveletname, mode='symmetric', level=dwt_level, axis=-1)
        coeff_lyi = pywt.wavedec(arr_lyi, waveletname, mode='symmetric', level=dwt_level, axis=-1)
        coeff_sit = pywt.wavedec(arr_sit, waveletname, mode='symmetric', level=dwt_level, axis=-1)
        coeff_sta = pywt.wavedec(arr_sta, waveletname, mode='symmetric', level=dwt_level, axis=-1)
        
        coeff_all = coeff_off[0] + coeff_lyi[0] + coeff_sit[0] + coeff_sta[0]
        mean_coeff = coeff_all.mean()
        std_coeff = coeff_all.std()
        print('mean, std: ', mean_coeff, std_coeff)
        
        coeff_off[0] = coeff_off[0]/mean_coeff
        coeff_lyi[0] = coeff_lyi[0]/mean_coeff
        coeff_sit[0] = coeff_sit[0]/mean_coeff
        coeff_sta[0] = coeff_sta[0]/mean_coeff
        coeff_all = coeff_all/mean_coeff
        
        print('len coeff: ', len(coeff_all))
        
        coeff_stack = np.vstack((coeff_off[0],coeff_lyi[0],coeff_sit[0],coeff_sta[0]))
        index_coeff = np.argmax(coeff_stack, axis=0)
        index_off = (index_coeff==0).astype(int)
        index_lyi = (index_coeff==1).astype(int)
        index_sit = (index_coeff==2).astype(int)
        index_sta = (index_coeff==3).astype(int)
        
        fig, axarr = plt.subplots(nrows=5, ncols=1, sharex=True, sharey=True)
        fig.canvas.mpl_connect('key_press_event', self.on_press)
        
        # print(len(data))
        # coeff_wave = pywt.wavedec(data, waveletname, mode='symmetric', level=9, axis=-1)
        # print(len(coeff_wave[0]))
        
        axarr[0].plot(coeff_off[0], color='tab:blue')
        axarr[1].plot(coeff_lyi[0], color='tab:orange')
        axarr[2].plot(coeff_sit[0], color='tab:green')
        axarr[3].plot(coeff_sta[0], color='tab:red')
        axarr[4].plot(index_off, color='tab:blue')
        axarr[4].plot(index_lyi, color='tab:orange')
        axarr[4].plot(index_sit, color='tab:green')
        axarr[4].plot(index_sta, color='tab:red')
        
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
        
        axarr[0].set_title(self.filename, loc='left')
        axarr[0].set_ylabel('off')
        axarr[1].set_ylabel('lyi')
        axarr[2].set_ylabel('sit')
        axarr[3].set_ylabel('sta')
        axarr[4].set_ylabel('rep.')
        axarr[4].set_xlabel('samples')
 
        resampling_value = 2**nlevel
        arr_time = df_loc[self.label_time].to_numpy()
        
        rt = arr_time[::resampling_value]
        print('len resampled:', len(arr_time), len(rt))
        print(rt)
        
        
        
        
        '''
        df_coeff = pd.DataFrame([])

        df_coeff['off']=coeff_off[0]
        df_coeff['lyi']=coeff_lyi[0]
        df_coeff['sit']=coeff_sit[0]
        df_coeff['sta']=coeff_sta[0]
        df_coeff['all']=coeff_all
        
        ## simple moving averages using pandas
        ## window size: from 2 hours (original data) to the decomposition scale of dwt_level (2**dwt_level)
        hours = 1/3 ## number of hours
        sph = 3600 ## seconds per hour
        window_size = int((sph*hours)/(2**dwt_level))
        print('window size: ', window_size)
        windows = df_coeff.rolling(window_size)
        ## Create a series of moving
        ## averages of each window
        moving_averages = windows.mean()
        # print(df_coeff)
        # print(windows)
        print(moving_averages)
        
        
        coeff_stack2 = np.vstack((moving_averages['off'].to_numpy(),moving_averages['lyi'].to_numpy(),moving_averages['sit'].to_numpy(),moving_averages['sta'].to_numpy()))
        index_coeff2 = np.argmax(coeff_stack2, axis=0)

        index_off = (index_coeff2==0).astype(int)
        index_lyi = (index_coeff2==1).astype(int)
        index_sit = (index_coeff2==2).astype(int)
        index_sta = (index_coeff2==3).astype(int)
        
        fig1, axarr1 = plt.subplots(nrows=5, ncols=1, sharex=True)
        
        axarr1[0].plot(moving_averages['off'].to_numpy(), color='tab:blue')
        axarr1[1].plot(moving_averages['lyi'].to_numpy(), color='tab:orange')
        axarr1[2].plot(moving_averages['sit'].to_numpy(), color='tab:green')
        axarr1[3].plot(moving_averages['sta'].to_numpy(), color='tab:red')
        axarr1[4].plot(index_off, color='tab:blue')
        axarr1[4].plot(index_lyi, color='tab:orange')
        axarr1[4].plot(index_sit, color='tab:green')
        axarr1[4].plot(index_sta, color='tab:red')
        
        
        # axarr[1].plot(coeff_wave[0])
        # axarr[0].set_title("Approximation coefficients"+title, fontsize=14)
        
        # for ii in range(levels):
            # (data, coeff_d) = pywt.dwt(data, waveletname)
            # axarr[ii, 0].plot(data, 'r')
            # axarr[ii, 1].plot(coeff_d, 'g')
            # axarr[ii, 0].set_ylabel("Level {}".format(ii + 1), fontsize=14, rotation=90)
            # axarr[ii, 0].set_yticklabels([])
            # if ii == 0:
                # axarr[ii, 0].set_title("Approximation coefficients"+title, fontsize=14)
                # axarr[ii, 1].set_title("Detail coefficients", fontsize=14)
            # axarr[ii, 1].set_yticklabels([])
        # plt.tight_layout()
        '''

        return 0
    
    
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
        
        print(self.filename,' dates: ',dates_list)
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
        
        
    def getActigraphyData(self):
        return self.df1
        
    def getNightCounts(self):
        return self.df_counts


