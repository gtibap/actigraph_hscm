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
        self.label_time = ' Time'
        self.label_date = 'Date'
        self.df1 = pd.DataFrame([])
        self.df_activity_indexes = pd.DataFrame([], columns=['idx_ini','idx_end','length'])
        self.min_vma = 3
        self.min_gap=300 # seconds
        self.arr_fig = [[] for i in range(10)]
        self.arr_axs = [[] for i in range(10)]
        # self.colors=np.array([])


    def openFile(self, path, filename):
        self.path = path
        self.filename = filename
        self.df1 = pd.read_csv(self.path+self.filename, header=self.header_location, decimal=',')
        # print(self.df1.shape, self.df1.size, len(self.df1))
        return 0

        
    def inclinometersStateChanging(self):
        
        arr_off = self.df1[self.incl_off].to_numpy()
        arr_lyi = self.df1[self.incl_lyi].to_numpy()
        arr_sit = self.df1[self.incl_sit].to_numpy()
        arr_sta = self.df1[self.incl_sta].to_numpy()
        arr_vma = self.df1[self.vec_mag].to_numpy()

        ## int to bool: any value greater than min_value vector magnitude (min_vm)
        arr_vma = arr_vma > self.min_vma

        act_off = self.stateChanging(arr_off)
        act_lyi = self.stateChanging(arr_lyi)
        act_sit = self.stateChanging(arr_sit)
        act_sta = self.stateChanging(arr_sta)
        act_vma = self.stateChanging(arr_vma)
        
        ## indexes change activity

        return 0

        
    def stateChanging(self, arr_incl):
        changes_activity = arr_incl[:-1] != arr_incl[1:]
        changes_activity = np.concatenate(([0],changes_activity), axis=None)
        return changes_activity


    
    def on_press(self, event):
        # print('press', event.key)
        sys.stdout.flush()
        
        if event.key == 'x':
            plt.close('all')
        else:
            pass
         
     
    def plotActigraphy(self):
        self.arr_fig[0], self.arr_axs[0] = plt.subplots(nrows=5, ncols=1, sharex=True)
        self.plotWithColors(self.arr_fig[0], self.arr_axs[0])
        return 0
    

    def plotWithColors(self,fig,ax):
        
        time_ini='22:00:00'
        time_end='07:59:59'
        
        color_day = 'tab:green'
        color_night = 'tab:purple'
        
        fig.canvas.mpl_connect('key_press_event', self.on_press)
        
        for i in np.arange(5):
            ax[i].cla()
        
        # x_ini=100000
        # x_end=200000
        # ax[0].set_xlim(x_ini,x_end)
        
        ax[0].set_ylim(0,400)
        
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
            df_segment = df_date.loc[df_date[self.label_time]<=time_end]
            self.plotSignals(fig, ax, df_segment, color_night)

            ## from 08:00:00 to 21:59:59
            df_segment = df_date.loc[(df_date[self.label_time] > time_end) & (df_date[self.label_time] <= time_ini)]
            self.plotSignals(fig, ax, df_segment, color_day)
            
            ## from 22:00:00 to 23:59:59
            df_segment = df_date.loc[df_date[self.label_time] > time_ini]
            self.plotSignals(fig, ax, df_segment, color_night)
        
        return 0
            

    def plotSignals(self,fig,ax,df,cr):
        
        x_values = df.index.tolist()
        
        ax[0].plot(x_values, df[self.vec_mag].to_numpy(), color=cr)
        
        ax[1].plot(x_values, df[self.incl_off].to_numpy(), color=cr)
        ax[2].plot(x_values, df[self.incl_lyi].to_numpy(), color=cr)
        ax[3].plot(x_values, df[self.incl_sit].to_numpy(), color=cr)
        ax[4].plot(x_values, df[self.incl_sta].to_numpy(), color=cr)
        
        return 0
        
        
    def getActigraphyData(self):
        return self.df1


