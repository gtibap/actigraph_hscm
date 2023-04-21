import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys


class Actigraphy:

    # the header in line 10 of the csv actigraphy files
    header_location=10
    time_ini='22:00:00'
    time_end='07:59:59'
    same_day=False
    min_gap=10 # seconds
    min_value=3 # Vector Magnitude should be greater than this value to be considered as a valid motor activity
    vec_mag  ='Vector Magnitude'
    incl_off ='Inclinometer Off'
    incl_sta ='Inclinometer Standing'
    incl_sit ='Inclinometer Sitting'
    incl_lyi ='Inclinometer Lying'
            
    def __init__(self):
        
        self.first_night = 0
        self.last_night = 0
        self.night_num = 0
        self.nights_list = []
        self.df_actigraphy_nights = pd.DataFrame()
        self.samples_per_night = []
        self.df_vectMag = pd.DataFrame()
        

    def openFile(self, path, filename):
        
        self.path = path
        self.filename = filename

        self.df1 = pd.read_csv(self.path+self.filename, header=self.header_location, decimal=',')

        self.df_actigraphy_nights, self.samples_per_night = self.nightsData()
        
        self.nights_list = self.df_actigraphy_nights['night'].unique().tolist()
        self.first_night = self.nights_list[0]
        self.last_night  = self.nights_list[-1]
        self.night_num   = self.first_night
        
        # self.df_vectMag = self.activityVectorMag()
        # self.readInclinometers()
        return 0


    def nightsData(self):
        
        dates_list = self.df1['Date'].unique().tolist()
        # print(dates_list, len(dates_list), type(dates_list))

        names_columns = self.df1.columns.tolist()
        # adding a column number of nights
        names_columns.append('night')

        # empty dataframe initialization
        df_all = pd.DataFrame(columns=names_columns)
        nights_samples=[]

        cont_nights=1
        if self.same_day==False:
            for day_now, day_next in zip(dates_list, dates_list[1:]):

                df_night_part0 = self.df1.loc[(self.df1['Date']==day_now)  & (self.df1[' Time']>=self.time_ini)]
                df_night_part1 = self.df1.loc[(self.df1['Date']==day_next) & (self.df1[' Time']<=self.time_end)]

                df_night = pd.concat([df_night_part0,df_night_part1],  ignore_index=True)
                df_night['night']=cont_nights
                df_all=pd.concat([df_all, df_night], ignore_index=True)
                # number of samples per night
                nights_samples.append(df_night['night'].to_numpy().size)
                cont_nights+=1
        else:
            for day_now in dates_list:
                df_night = df.loc[(df['Date']==day_now) & (df[' Time']>=self.time_ini) & (df[' Time']<=self.time_end)]
                df_night['night']=cont_nights
                df_all=pd.concat([df_all, df_night], ignore_index=True)
                # number of samples per night
                nights_samples.append(df_night['night'].to_numpy().size)
                cont_nights+=1
                
        return df_all, nights_samples
    

    def activityVectorMag(self):
        
        nights_list = self.df_actigraphy_nights['night'].unique().tolist()
        df_vectMag_all = pd.DataFrame([],columns=['night', 'active', 'idx_ini', 'idx_end'])

        for night_num in nights_list:

            # actigraphy data night per night
            df_n = self.df_actigraphy_nights.loc[(self.df_actigraphy_nights['night']==night_num)]
        
            # boolean array where True means activity higher than min_value
            arr_mag = df_n[self.vec_mag].to_numpy()
            activity_array = arr_mag > self.min_value
            # boolean array where True means activity higher than min_value

            duration_active, duration_inactive, start_active, end_active = self.activity_sectors(activity_array)

            activity_array = self.redefinition_activity_arr(duration_active, duration_inactive, start_active, end_active, self.min_gap)
            
            idx_ini, idx_end = self.activity_sectors_indexes(activity_array)

            df_act_night = pd.DataFrame()
            df_act_night['idx_ini']=idx_ini
            df_act_night['idx_end']=idx_end
            df_act_night['night']=night_num
            df_act_night['active']=1

            df_vectMag_all=pd.concat([df_vectMag_all, df_act_night], ignore_index=True)

            non_activity_array = np.logical_not(activity_array)
            idx_ini, idx_end = self.activity_sectors_indexes(non_activity_array)

            df_non_act_night = pd.DataFrame()
            df_non_act_night['idx_ini']=idx_ini
            df_non_act_night['idx_end']=idx_end
            df_non_act_night['night']=night_num
            df_non_act_night['active']=0

            df_vectMag_all=pd.concat([df_vectMag_all, df_non_act_night], ignore_index=True)

        df_vectMag_all['duration'] = df_vectMag_all['idx_end'] - df_vectMag_all['idx_ini']
            
        return df_vectMag_all


    def activity_sectors(self, activity_arr):
    
        # comparison of active _array (boolean vector) with itself but moved one position. The idea is to identify changes--True to False or False to True.
        changes_activity = activity_arr[:-1] != activity_arr[1:]
        # changes_activity is a boolean vector; True means a change; False means no change
        # indices or location of Trues (changes) values; +1 because I want the index when the data already changed from left to right
        # first index is location 0 in the array
        idx_changes=[0]
        idx_changes = np.concatenate((idx_changes, np.flatnonzero(changes_activity) + 1), axis=None)
        # last index is the size of the original array
        idx_end =len(activity_arr)
        idx_changes = np.concatenate((idx_changes, idx_end), axis=None)
        # distance between two consecutive changes (time in our case)
        intervals = idx_changes[1:]-idx_changes[:-1]
        # if false means that the collected data started with inactivity
        # alternancy between activity and inactivity
        start_active=False
        if activity_arr[0]==False:
            duration_inactive = intervals[0::2]
            duration_active =   intervals[1::2]
        else:
            duration_active =   intervals[0::2]
            duration_inactive = intervals[1::2]
            start_active=True

        end_active=False
        if activity_arr[-1]==False:
            pass
        else:
            end_active=True

        return duration_active, duration_inactive, start_active, end_active


    def redefinition_activity_arr(self, duration_active, duration_inactive, start_active, end_active, min_gap):

        # construction of a new_activity_array. In this case, we convert inactivity periods less than 10s to activity ones
        new_activity_array=np.array([])
        
        if start_active==False:
            # we keep the first inactive period unchanged
            new_activity_array=np.concatenate((new_activity_array, duration_inactive[0]*[False]))
            
            for d_a, d_i in zip(duration_active[0:], duration_inactive[1:]):
                # then follows an active period
                new_activity_array=np.concatenate((new_activity_array, d_a*[True]))
                # then a non-active period; we transform the period to an active one if the period is less than ming_gap
                if d_i < min_gap:
                    new_activity_array=np.concatenate((new_activity_array, d_i*[True]))
                else:
                    new_activity_array=np.concatenate((new_activity_array, d_i*[False]))
            
            # the previous loop could have left behind the last activity period (if it was the last of the sequence)
            if end_active==True:
                new_activity_array=np.concatenate((new_activity_array, duration_active[-1]*[True]))
            else:
                pass

        else:
            for d_a, d_i in zip(duration_active[0:], duration_inactive[0:]):
                
                new_activity_array=np.concatenate((new_activity_array, d_a*[True]))
                if d_i < min_gap:
                    new_activity_array=np.concatenate((new_activity_array, d_i*[True]))
                else:
                    new_activity_array=np.concatenate((new_activity_array, d_i*[False]))
            
            if end_active==True:
                new_activity_array=np.concatenate((new_activity_array, duration_active[-1]*[True]))
            else:
                pass

        return new_activity_array


    def readInclinometers(self):
        
        df_incl_all = pd.DataFrame([],columns=['incl', 'idx_ini', 'idx_end'])

        for night_num in self.nights_list:

            # actigraphy data night per night
            df_n = self.df_actigraphy_nights.loc[(self.df_actigraphy_nights['night']==night_num)]
            
            arr_off = df_n[self.incl_off].to_numpy()
            arr_lyi = df_n[self.incl_lyi].to_numpy()
            arr_sit = df_n[self.incl_sit].to_numpy()
            arr_sta = df_n[self.incl_sta].to_numpy()
            
            df_incl_night = pd.DataFrame(columns=['incl', 'idx_ini', 'idx_end'])
            
            df_incl_night=self.inclinometer_sequence(df_incl_night, arr_off, 'off')
            df_incl_night=self.inclinometer_sequence(df_incl_night, arr_lyi, 'lyi')
            df_incl_night=self.inclinometer_sequence(df_incl_night, arr_sit, 'sit')
            df_incl_night=self.inclinometer_sequence(df_incl_night, arr_sta, 'sta')
            
            df_incl_night['night']=night_num
            
            df_incl_all = pd.concat([df_incl_all, df_incl_night], ignore_index=True)

        df_incl_all['duration']=df_incl_all['idx_end'] - df_incl_all['idx_ini']
        
        self.df_inclinometers = df_incl_all
        
        return 0
        
        
    def inclinometer_sequence(self, df_incl_night, arr_incl, label):
    
        indexes_ini, indexes_end =self.activity_sectors_indexes(arr_incl)
        df_incl = pd.DataFrame()
        df_incl['idx_ini'] = indexes_ini
        df_incl['idx_end'] = indexes_end
        df_incl['incl'] = label
        df_incl_night = pd.concat([df_incl_night, df_incl], ignore_index=True)
        
        return df_incl_night


    def activity_sectors_indexes(self, activity_array):
    
        # comparison of active _array (boolean vector) with itself but moved one position. The idea is to identify changes--True to False or False to True.
        
        changes_activity = activity_array[:-1] != activity_array[1:]

        # if false means that the collected data started with inactivity
        # alternancy between activity and inactivity
        start_active=False
        if activity_array[0]==False:
            idx_changes = np.flatnonzero(changes_activity) + 1
        else:
            idx_changes=[0]
            idx_changes = np.concatenate((idx_changes, np.flatnonzero(changes_activity) + 1), axis=None)
            start_active=True

        end_active=False
        if activity_array[-1]==False:
            pass
        else:
            idx_end =len(activity_array)
            idx_changes = np.concatenate((idx_changes, idx_end), axis=None)
            end_active=True

        indexes_ini = idx_changes[0::2]
        indexes_end = idx_changes[1::2]

        return indexes_ini, indexes_end
        
    
    def plot_actigraphy(self):
        self.fig_initial, self.ax_initial = plt.subplots(nrows=5, ncols=1, sharex=True)
        self.replot_actigraphy()
        return self.fig_initial, self.ax_initial
        
        
    def replot_actigraphy(self):
        
        df_night = self.df_actigraphy_nights.loc[(self.df_actigraphy_nights['night']==self.night_num)]
        
        for i in np.arange(5):
            self.ax_initial[i].cla()

        self.ax_initial[0].set_title(self.filename+', night:'+str(self.night_num))
        self.ax_initial[0].set_ylabel('v.m.')
        self.ax_initial[1].set_ylabel('off')
        self.ax_initial[2].set_ylabel('lyi')
        self.ax_initial[3].set_ylabel('sit')
        self.ax_initial[4].set_ylabel('sta')
        
        self.ax_initial[0].plot(df_night[self.vec_mag].to_numpy())
        self.ax_initial[1].plot(df_night[self.incl_off].to_numpy())
        self.ax_initial[2].plot(df_night[self.incl_lyi].to_numpy())
        self.ax_initial[3].plot(df_night[self.incl_sit].to_numpy())
        self.ax_initial[4].plot(df_night[self.incl_sta].to_numpy())
        
        self.fig_initial.canvas.draw()
        self.fig_initial.canvas.flush_events()
        
        return 0
        
    
    def filterInclinometers(self):
        
        df_in = (self.getInclinometersData()).copy()
        nights_list = df_in['night'].unique().tolist()
        for night_num in nights_list[:1]:
            print('night: ', night_num)
            df_night_off = df_in.loc[(df_in['night']==night_num) & (df_in['incl']=='off')]
            df_night_lyi = df_in.loc[(df_in['night']==night_num) & (df_in['incl']=='lyi')]
            df_night_sit = df_in.loc[(df_in['night']==night_num) & (df_in['incl']=='sit')]
            df_night_sta = df_in.loc[(df_in['night']==night_num) & (df_in['incl']=='sta')]
            # print(df_night)
            
            arr_off_ini = df_night_off['idx_ini'].to_numpy()
            arr_lyi_ini = df_night_lyi['idx_ini'].to_numpy()
            arr_sit_ini = df_night_sit['idx_ini'].to_numpy()
            arr_sta_ini = df_night_sta['idx_ini'].to_numpy()
            
            
            arr_off_end = df_night_off['idx_end'].to_numpy()
            arr_lyi_end = df_night_lyi['idx_end'].to_numpy()
            arr_sit_end = df_night_sit['idx_end'].to_numpy()
            arr_sta_end = df_night_sta['idx_end'].to_numpy()
            
            # arr_off_end_copy = np.copy(arr_off_end)
            # arr_lyi_end_copy = np.copy(arr_lyi_end)
            # arr_sit_end_copy = np.copy(arr_sit_end)
            
            new_arr_off_end = self.filterInclStanding(arr_sta_ini, arr_sta_end, arr_off_end)
            new_arr_lyi_end = self.filterInclStanding(arr_sta_ini, arr_sta_end, arr_lyi_end)
            new_arr_sit_end = self.filterInclStanding(arr_sta_ini, arr_sta_end, arr_sit_end)
            
            
            # for i,j in zip(arr_sit_end, new_arr_sit_end):
                # print(i, j, j-i)
            
        
        return 0
        
        
    def filterInclStanding(self, arr_sta_ini, arr_sta_end, arr_end):
            
        arr_copy = np.copy(arr_end)
        
        for id0, id1 in zip(arr_sta_ini, arr_sta_end):
            if id0 in arr_end:
                # print(idx, np.argwhere(arr_off_end==idx)[0][0])
                id_end = np.argwhere(arr_end==id0)[0][0]
                # replace end
                arr_copy[id_end] = id1
            else:
                pass
        
        return arr_copy
                    
            
        
        
    def getInclinometersData(self):
        return self.df_inclinometers
        
    def getVectMagActivity(self):
        return self.df_vectMag
        
    def getActigraphyData(self):
        return self.df_actigraphy_nights
        
    def setMinGap(self, value):
        self.min_gap=value
        return 0
    
    def setMinValue(self, value):
        self.min_value=value
        return 0
        
    
        
        
        

