import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D
import datetime
import seaborn as sns
import os
import sys

from functions_tools import getSelectedData


def non_motion_periods(mag_col):
    # nights_list = df['night'].unique().tolist()
    min_value = 3 # min intensity value
    # for night_num in nights_list[:1]:
    # mag_col = df.loc[(df['night']==night_num), ['Vector Magnitude']]

    mag_col['active'] = mag_col['Vector Magnitude'] > min_value
    # boolean array where True means activity higher than min_value
    active_arrray = mag_col['active'].to_numpy()
    # print('active_arrray: ', active_arrray)
    # comparison of active _array (boolean vector) with itself but moved one position. The idea is to identify changes--True to False or False to True.
    changes_array = active_arrray[:-1] != active_arrray[1:]
    # changes_array is a boolean vector; True means a change; False means no change
    # print('changes: ', changes_array)
    # indices or location of Trues (changes) values 
    idx_changes = np.flatnonzero(changes_array)
    # print('idx_changes: ', idx_changes)
    # print(active_arrray[idx_changes])
    # distance between two consecutive changes (time in our case)
    intervals = idx_changes[1:]-idx_changes[:-1]
    # print('intervals: ', intervals)

    # period before the first detection of change in activity
    initial_value = [idx_changes[0] + 1]
    # if false means that the collected data start with inactivity. The first detected change is from inactivity to activity; therefore, the intervals[0] is the first period of activity
    
    if active_arrray[idx_changes[0]]==False:
        # alternance between activity and inactivity
        duration_active = intervals[::2]
        duration_inactive = np.concatenate([initial_value, intervals[1::2]])
        start_active = False
    else:
        # alternance between activity and inactivity
        duration_active = np.concatenate([initial_value, intervals[1::2]])
        duration_inactive = intervals[::2]
        start_active = True

    # print('duration_active: ', duration_active)
    # print('duration_inactive: ', duration_inactive)
    
    return duration_active, duration_inactive, start_active


def activity_sectors(df, column):
    
    # nights_list = df['night'].unique().tolist()
    min_value = 3 # min intensity value
    # for night_num in nights_list[:1]:
    # mag_col = df.loc[(df['night']==night_num), ['Vector Magnitude']]
    min_gap = 10 # seconds

    df['activity'] = df[column] > min_value
    # boolean array where True means activity higher than min_value
    activity_arrray = df['activity'].to_numpy()
    # print('active_arrray: ', active_arrray)
    # comparison of active _array (boolean vector) with itself but moved one position. The idea is to identify changes--True to False or False to True.
    
    changes_activity = activity_arrray[:-1] != activity_arrray[1:]

    # changes_array is a boolean vector; True means a change; False means no change
    # print('changes: ', changes_array)
    # indices or location of Trues (changes) values; +1 because I want the index when the data already changed from left to right
    # first index is location 0 in the array
    idx_changes=[0]
    idx_changes = np.concatenate((idx_changes, np.flatnonzero(changes_activity) + 1), axis=None)
    # last index is the size of the original array
    idx_end =len(activity_arrray)
    idx_changes = np.concatenate((idx_changes, idx_end), axis=None)

    # print('idx_changes: ', idx_changes)
    # print(active_arrray[idx_changes])
    # distance between two consecutive changes (time in our case)
    intervals = idx_changes[1:]-idx_changes[:-1]
    # print('intervals: ', intervals)

    # if false means that the collected data started with inactivity
    # alternancy between activity and inactivity
    start_active=False
    if activity_arrray[0]==False:
        duration_inactive = intervals[0::2]
        duration_active =   intervals[1::2]
    else:
        duration_active =   intervals[0::2]
        duration_inactive = intervals[1::2]
        start_active=True

    end_active=False
    if activity_arrray[-1]==False:
        pass
    else:
        end_active=True

    # print('duration_active: ', duration_active)
    # print('duration_inactive: ', duration_inactive)

    # construction of new_activity_array inverting inactivity periods less than 10s
    new_activity_array=np.array([])
    
    if start_active==False:
        new_activity_array=np.concatenate((new_activity_array, duration_inactive[0]*[False]))
        
        for d_a, d_i in zip(duration_active[0:], duration_inactive[1:]):
            
            new_activity_array=np.concatenate((new_activity_array, d_a*[True]))
            if d_i < min_gap:
                new_activity_array=np.concatenate((new_activity_array, d_i*[True]))
            else:
                new_activity_array=np.concatenate((new_activity_array, d_i*[False]))
        
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

    
    
        # if the last values where not included in the previous loop
        # new_activity_array=np.concatenate((new_activity_array, duration_active[cont_id]*[True]))
        # new_activity_array=np.concatenate((new_activity_array, duration_inactive[cont_id]*[False]))


    
    print('len(new_activity_array): ', len(new_activity_array))
    print('len(activity_array): ', len(activity_arrray))

    fig, axes = plt.subplots(nrows=3, ncols=1, sharex=True)
    axes[0].plot(df[column].to_numpy())
    axes[1].plot(activity_arrray)
    axes[2].plot(new_activity_array)
    plt.show()



    

    return

####### main function ###########
if __name__== '__main__':

    # Get the list of all files and directories
    path = "../data/all_data_1s/"
    path_out = "../data/results_each_pose/"
    files_list = os.listdir(path)
    
    print("Files in '", path, "' :")
    # prints all files
    print(files_list)

    # the header in line 10 of the csv file
    header_location=10
    time_start='22:00:00'
    time_end='08:00:00'
    same_day=False

    incl_off ='Inclinometer Off'
    vec_mag  ='Vector Magnitude'

    header_location=10
    for sample in files_list[:1]:
        print('file: ', sample)
        try:
            df1 = pd.read_csv(path+sample, header=header_location, decimal=',', usecols=['Date',' Time', vec_mag, incl_off])
            # print(df1.info())

            # getting all nights data
            df_nights = getSelectedData(df1, time_start, time_end, same_day)
            # print(df_nights.info())

            # plot 'Vector Magnitude' night by night
            nights_list = df_nights['night'].unique().tolist()
            # print('nights: ', nights_list)
            for night_num in nights_list[:2]:
                # print('night: ', night_num)
                df_n = df_nights.loc[(df_nights['night']==night_num), [vec_mag]]
                # print('df_n.info: ', df_n.info())
                # print(df_n.head())
                # print(df_n.tail())

                # identifying sectors of activity per night
                activity_sectors(df_n, vec_mag)
            
        except ValueError:
            print('Problem reading the file', sample, '... it is skipped.')

    

    # # the header in line 10 of the csv file
    # header_location=10
    # df1 = pd.read_csv("../data/p00/Turner Chest1secDataTable.csv", header=header_location, decimal=',', usecols=['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude'])
    # # print(df.empty)
    # # print(df.shape)
    # print(df1.columns)
    # print(df1.head)
    # print(df1.info())
    
    # df2 = pd.read_csv("../data/p00/Turner Thigh1secDataTable.csv", header=header_location, decimal=',', usecols=['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude'])
    # # print(df.empty)
    # # print(df.shape)
    # print(df2.columns)
    # # print(df.head)1
    # print(df2.info())
    
    
    # print(df.describe())
    # print(df['Inclinometer Off'].unique())
    # print(df['Inclinometer Off'].value_counts())
    # print(df.loc[(df['Date']=='13/12/2022'), ['Date',' Time','Vector Magnitude']])
    # print(df.loc[(df['Date']=='13/12/2022') & (df['Vector Magnitude'].isnull()), ['Date',' Time','Vector Magnitude']])
    # print(df.loc[(df['Date']=='13/12/2022') & ((df[' Axis1']>0)|(df['Axis2']>0)|(df['Axis3']>0)), ['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude']])

    # print(df.loc[(df['Date']=='12/12/2022') & (df[' Time']>='22:00:00'), ['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude']])
    # print(df.loc[(df['Date']=='13/12/2022') & (df[' Time']<='10:00:00'), ['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude']])

    # plot_data(df1, 'chest')
    # plot_data(df2, 'thigh')
    # plt.show()

    # time_start='22:00:00'
    # time_end='10:00:00'
    # same_day=False

    # time_start='04:45:00'
    # time_end='05:45:00'
    # same_day=True


    # df_chest = getSelectedData(df1, time_start, time_end, same_day)
    # df_thigh = getSelectedData(df2, time_start, time_end, same_day)
    # print(df1_nights.columns)
    # print(df1_nights.info())
    # print(df1_nights.head)

    # plot_nights(df_chest, df_thigh)
    # plt.show()


    # histograms

    # plt.figure(1)
    # nights_list = df_chest['night'].unique().tolist()
    # for night_num in nights_list[:1]:
    #     mag_col = df_chest.loc[(df_chest['night']==night_num), ['Vector Magnitude']]
    #     activity, inactivity = non_motion_periods(mag_col)
    #     plt.subplot(211)
    #     activityHistogram(activity, inactivity)

    # nights_list = df_thigh['night'].unique().tolist()
    # for night_num in nights_list[:1]:
    #     mag_col = df_thigh.loc[(df_thigh['night']==night_num), ['Vector Magnitude']]
    #     activity, inactivity = non_motion_periods(mag_col)
    #     plt.subplot(212)
    #     activityHistogram(activity, inactivity)

    # plt.show()
    
    #
    # empty dataframe initialization
    # df_all = pd.DataFrame(columns=names_columns)

    max_list_chest=[]
    max_list_thigh=[]
    df_freqs = pd.DataFrame(columns=['night', 'location', 'activity','inactivity'])

    # extracting blocs of data per night
    nights_list = df_chest['night'].unique().tolist()
    all_count_groups=[]
    for night_num in nights_list:

        df_mag_chest = df_chest.loc[(df_chest['night']==night_num), ['Vector Magnitude']]
        df_mag_thigh = df_thigh.loc[(df_chest['night']==night_num), ['Vector Magnitude']]

        # chest        
        # duration of continuous periods of actitity and inactivity in seconds
        activity, inactivity, start_active = non_motion_periods(df_mag_chest)

        # print ('results', len(activity), len(inactivity), start_active)
        # print('activity: ', activity)
        # print('inactivity: ', inactivity)

        min_gap = 10 # seconds
        small_gap =  inactivity < min_gap
        # print('small_gap: ', small_gap)
    
        long_result = np.array([])
        new_activity = list()
        count_groups=0
        id_ac = 0
        if start_active == True:
            id_in = 0
        else:
            id_in = 1
            # number of zeros; one zero per second
            long_result = np.concatenate((long_result, np.zeros(inactivity[0], np.int8)), axis=None)
        
        # print('id_in: ', id_in)
        while id_ac < (len(activity)-1):
            acc_temp = activity[id_ac]
            acc_neta = activity[id_ac]
            # true means that the gap is less than min_gap
            while (id_in < len(small_gap)) and (small_gap[id_in]) and (id_ac < (len(activity)-1)):
                id_ac+=1
                acc_temp += activity[id_ac]
                acc_neta += activity[id_ac] + inactivity[id_in]
                id_in+=1
            new_activity.append(acc_temp)
            # 1 per activity group per second
            # longitudinal_result.append(acc_neta*[1])
            long_result = np.concatenate((long_result, np.ones(acc_neta,np.int8)), axis=None)
            # 0 per inactivity group per second
            # longitudinal_result.append(inactivity[id_in]*[0])
            long_result = np.concatenate((long_result, np.zeros(inactivity[id_in],np.int8)), axis=None)
            count_groups+=1
            id_ac+=1
            id_in+=1
        
        print('count_groups: ', count_groups)
        all_count_groups.append(count_groups)



    nights = list(range(0,len(all_count_groups)))
    print(nights)
    print(all_count_groups)
    plt.bar(nights[:-1], all_count_groups[:-1])
    plt.xlabel('night')
    plt.ylabel('count of detected motions')
    plt.show()

