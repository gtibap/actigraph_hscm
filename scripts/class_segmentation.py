import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import re
import sys


class Seg_Actigraphy:

    def __init__(self):
        print('Seg_Actigraphy object initialization')
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
        self.min_gap=3600 # seconds
        self.arr_fig = [[] for i in range(10)]
        self.arr_axs = [[] for i in range(10)]
        # self.colors=np.array([])



    def openFile(self, path, filename):
        self.path = path
        self.filename = filename
        self.df1 = pd.read_csv(self.path+self.filename, header=self.header_location, decimal=',')
        self.colorsActigraphy()
        return 0

    def colorsActigraphy(self):
        hours=[]
        arr_time = self.df1[self.label_time].to_numpy()
        for sample in arr_time:
            hhmmss = re.split('[:]', sample)
            # hhmmss = np.array(hhmmss).astype(float)
            # print(hhmmss)
            # hours.append(hhmmss[0]+hhmmss[1]/60+hhmmss[2]/3600)
            hours.append(hhmmss[0])
            # hours=np.array()
        # print(arr_time)
        hours = np.array(hours).astype(int)
        # colors= 0.5*(1+np.cos(np.pi*hours/12))
        # self.df1['color']=colors
        # print(colors)
        return 0
        
    def inclinometersStateChanging(self):
        arr_off = self.df1[self.incl_off].to_numpy()
        arr_lyi = self.df1[self.incl_lyi].to_numpy()
        arr_sit = self.df1[self.incl_sit].to_numpy()
        arr_sta = self.df1[self.incl_sta].to_numpy()
        arr_vma = self.df1[self.vec_mag].to_numpy()

        ## vector magnitude: any value greater than zero
        arr_vma = arr_vma > 3

        # arr_act = np.logical_or(arr_off,arr_lyi)
        # arr_act = np.logical_or(arr_act,arr_sit)
        # arr_act = np.logical_or(arr_act,arr_sta)
        # arr_act = np.logical_or(arr_act,arr_vma)

        act_off = self.stateChanging(arr_off)
        act_lyi = self.stateChanging(arr_lyi)
        act_sit = self.stateChanging(arr_sit)
        act_sta = self.stateChanging(arr_sta)
        act_vma = self.stateChanging(arr_vma)

        arr_act = np.logical_or(act_off,act_lyi)
        arr_act = np.logical_or(arr_act,act_sit)
        arr_act = np.logical_or(arr_act,act_sta)
        arr_act = np.logical_or(arr_act,act_vma)
        
        self.df1['activity']=arr_act
        # self.activityRegions(arr_act)
        self.signal_segmentation()
        # print(self.df_activity_indexes)
        # ax = self.df_activity_indexes.boxplot(column=['length'])
        # plt.show()
        return 0

        
    def stateChanging(self, arr_incl):
        changes_activity = arr_incl[:-1] != arr_incl[1:]
        changes_activity = np.concatenate(([0],changes_activity), axis=None)
        return changes_activity


    def signal_segmentation(self):

        # indexes_ini = self.df_activity_indexes['idx_ini'].to_numpy()
        # indexes_end = self.df_activity_indexes['idx_end'].to_numpy()
        # arr_active = self.df_activity_indexes['length'].to_numpy()
        arr_act = self.df1['activity']
        
        idx_changes = np.flatnonzero(arr_act)

        ## first element of the arr_deltas is the number of samples from the start (0) until the first activity index idx_changes[0]
        arr_deltas = np.array([idx_changes[0]])
        arr_deltas = np.concatenate((arr_deltas, idx_changes[1:]-idx_changes[:-1]), axis=None)
        arr_deltas = np.concatenate((arr_deltas, len(arr_act)-idx_changes[-1]), axis=None)
        
        ## fill with zeros until the index: indexes_ini[0]
        # arr_seg=np.array((idx_changes[0])*[0])
        arr_seg=np.array([])
        ## fill with ones and zeros alternately
        for delta in arr_deltas:
            if delta < self.min_gap:
                arr_seg=np.concatenate((arr_seg, delta*[1]), axis=None)
            else:
                arr_seg=np.concatenate((arr_seg, delta*[0]), axis=None)
        
        ## the loop above is limited by the length of arr_inactive; therefore, arr_seg is completed with the last active and inactive samples
        # arr_seg=np.concatenate((arr_seg, arr_active[-1]*[1]), axis=None)
        # arr_seg=np.concatenate((arr_seg, (len(self.df1)-indexes_end[-1])*[0]), axis=None)
        
        arr_seg = np.logical_or(arr_act,arr_seg)
        
        self.df1['signal']=arr_seg
        
        return 0

    # def activityRegions(self, activity_array):
        ## comparison of active _array (boolean vector) with itself but moved one position. The idea is to identify changes--True to False or False to True.
        # changes_activity = self.stateChanging(activity_array)

        ## if false means that the collected data started with inactivity
        ## alternancy between activity and inactivity
        # start_active=False
        # if activity_array[0]==False:
            # idx_changes = np.flatnonzero(changes_activity)
        # else:
            # idx_changes = np.concatenate(([0], np.flatnonzero(changes_activity)), axis=None)
            # start_active=True

        # end_active=False
        # if activity_array[-1]==False:
            # pass
        # else:
            # idx_changes = np.concatenate((idx_changes, len(activity_array)), axis=None)
            # end_active=True

        # indexes_ini = idx_changes[0::2]
        # indexes_end = idx_changes[1::2]
        
        # self.df_activity_indexes['idx_ini']=indexes_ini
        # self.df_activity_indexes['idx_end']=indexes_end
        # self.df_activity_indexes['length'] =indexes_end-indexes_ini

        # return 0
        
    
    # def signal_segmentation(self):

        # indexes_ini = self.df_activity_indexes['idx_ini'].to_numpy()
        # indexes_end = self.df_activity_indexes['idx_end'].to_numpy()
        # arr_active = self.df_activity_indexes['length'].to_numpy()

        # arr_inactive = indexes_ini[1:]-indexes_end[:-1]
        
        # ## fill with zeros until the index: indexes_ini[0]
        # arr_seg=np.array((indexes_ini[0])*[0])
        
        # ## fill with ones and zeros alternately
        # for num_ac, num_in in zip(arr_active, arr_inactive):
            # arr_seg=np.concatenate((arr_seg, num_ac*[1]), axis=None)
            # arr_seg=np.concatenate((arr_seg, num_in*[0]), axis=None)
        
        # ## the loop above is limited by the length of arr_inactive; therefore, arr_seg is completed with the last active and inactive samples
        # arr_seg=np.concatenate((arr_seg, arr_active[-1]*[1]), axis=None)
        # arr_seg=np.concatenate((arr_seg, (len(self.df1)-indexes_end[-1])*[0]), axis=None)
        
        # self.df1['signal']=arr_seg
        
        # return 0
        
    def plotActigraphy(self):
        self.arr_fig[0], self.arr_axs[0] = plt.subplots(nrows=7, ncols=1, sharex=True)
        # self.plotSignals(self.arr_fig[0], self.arr_axs[0])
        self.plotWithColors(self.arr_fig[0], self.arr_axs[0])
        
        return 0
    
    def plotWithColors(self,fig,ax):
        
        time_ini='22:00:00'
        time_end='07:59:59'
        
        for i in np.arange(7):
            ax[i].cla()
        # ax[0].set_xlim(0,5000)
        ax[0].set_ylim(0,400)
        ax[0].set_title(self.filename)
        ax[0].set_ylabel('v.m.')
        ax[1].set_ylabel('off')
        ax[2].set_ylabel('lyi')
        ax[3].set_ylabel('sit')
        ax[4].set_ylabel('sta')
        ax[5].set_ylabel('act')
        ax[6].set_ylabel('signal')
        ax[6].set_xlabel('time (s)')
        
        dates_list = self.df1[self.label_date].unique().tolist()
        print(dates_list)
        for date in dates_list:
            df_date = self.df1.loc[self.df1[self.label_date]== date]
            
            ## from 00:00:00 to 07:59:59
            df_segment = df_date.loc[df_date[self.label_time]<=time_end]
            color='purple'
            self.plotSignals(fig, ax, df_segment, color)
            
            ## from 08:00:00 to 21:59:59
            df_segment = df_date.loc[(df_date[self.label_time] > time_end) & (df_date[self.label_time] <= time_ini)]
            color='orange'
            self.plotSignals(fig, ax, df_segment, color)
            
            ## from 22:00:00 to 23:59:59
            df_segment = df_date.loc[df_date[self.label_time] > time_ini]
            color='purple'
            self.plotSignals(fig, ax, df_segment, color)
            # print(df_segment)
            # print(df_segment.index.tolist())
        
        
        
        return 0
            
    def plotSignals(self,fig,ax,df,cr):
        
        # for i in np.arange(7):
            # ax[i].cla()
        # ax[0].set_xlim(0,5000)
        # ax[0].set_ylim(0,400)
        # ax[0].set_title(filename+', night:'+str(night_num))
        # ax[0].set_ylabel('v.m.')
        # ax[1].set_ylabel('off')
        # ax[2].set_ylabel('lyi')
        # ax[3].set_ylabel('sit')
        # ax[4].set_ylabel('sta')
        # ax[5].set_ylabel('act')
        # ax[6].set_ylabel('signal')
        # ax[6].set_xlabel('time (s)')
        
        # ax[0].plot(self.df1[self.vec_mag].to_numpy())
        # ax[1].plot(self.df1[self.incl_off].to_numpy())
        # ax[2].plot(self.df1[self.incl_lyi].to_numpy())
        # ax[3].plot(self.df1[self.incl_sit].to_numpy())
        # ax[4].plot(self.df1[self.incl_sta].to_numpy())
        # ax[5].plot(self.df1['activity'].to_numpy())
        # ax[6].plot(self.df1['signal'].to_numpy())
        
        x_values = df.index.tolist()
        
        ax[0].plot(x_values, df[self.vec_mag].to_numpy(), color=cr)
        ax[1].plot(x_values, df[self.incl_off].to_numpy(), color=cr)
        ax[2].plot(x_values, df[self.incl_lyi].to_numpy(), color=cr)
        ax[3].plot(x_values, df[self.incl_sit].to_numpy(), color=cr)
        ax[4].plot(x_values, df[self.incl_sta].to_numpy(), color=cr)
        ax[5].plot(x_values, df['activity'].to_numpy(), color=cr)
        ax[6].plot(x_values, df['signal'].to_numpy(), color=cr)
        
        
        return 0
        
        
    def getActigraphyData(self):
        return self.df1


