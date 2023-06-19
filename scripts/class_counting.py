from scipy import ndimage
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
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
        self.min_gap_rep =600 # seconds (10 min)
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


