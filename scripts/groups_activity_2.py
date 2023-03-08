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


def activity_sectors(df, vector_mag, min_value, min_gap):
    
    # nights_list = df['night'].unique().tolist()
    # min_value = 3 # min intensity value
    # for night_num in nights_list[:1]:
    # mag_col = df.loc[(df['night']==night_num), ['Vector Magnitude']]
    # min_gap = 10 # seconds

    df['activity'] = df[vector_mag] > min_value
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

    # fig, axes = plt.subplots(nrows=3, ncols=1, sharex=True)
    # axes[0].plot(df[vector_mag].to_numpy())
    # # axes[1].plot(activity_arrray)
    # axes[1].plot(new_activity_array)
    # axes[2].plot(df[incl_off].to_numpy())

    # plt.show()

    return new_activity_array

def activity_intervals(activity_vector):

    changes_activity = activity_vector[:-1] != activity_vector[1:]
    # changes_array is a boolean vector; True means a change; False means no change
    # indices or location of Trues (changes) values; +1 because I want the index when the data already changed from left to right
    idx_changes = np.flatnonzero(changes_activity) + 1

    # at least three detected changes
    if len(idx_changes) > 3:
        if activity_vector[0]==False:
            idx_ini=idx_changes[0::2]
            idx_end=idx_changes[1::2]
        else:
            idx_ini=idx_changes[1::2]
            idx_end=idx_changes[2::2]

        # removing the initial index of the last sector if it has not finished
        if activity_vector[-1]==True:
            idx_ini=idx_ini[0:-1]
        else:
            pass
    else:
        idx_ini=[0]
        idx_end=[0]

    return idx_ini, idx_end

####### main function ###########
if __name__== '__main__':

    # Get the list of all files and directories
    path = "../data/all_data_1s/"
    path_out = "../data/results_motion/"
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
            df_active_nights = pd.DataFrame(columns=['night','t_ini','t_end'])
            for night_num in nights_list:
                # print('night: ', night_num)
                df_n = df_nights.loc[(df_nights['night']==night_num), [vec_mag]]
                # print('df_n.info: ', df_n.info())
                # print(df_n.head())
                # print(df_n.tail())

                # identifying sectors of activity per night where gaps of 10s of inactivity are considered part of the activity section
                min_gap=10 # seconds
                min_value=3 # Vector Magnitude should be greater than this value to be considered as a valid motor activity
                activity_vector=activity_sectors(df_n, vec_mag, min_value, min_gap)
                idx_ini, idx_end = activity_intervals(activity_vector)
                print('idx_ini: ', len(idx_ini), idx_ini)
                print('idx_end: ', len(idx_end), idx_end)
                df_act_night = pd.DataFrame(columns=['night','t_ini','t_end'])
                df_act_night['t_ini']=idx_ini
                df_act_night['t_end']=idx_end
                df_act_night['night']=night_num
                df_active_nights=pd.concat([df_active_nights, df_act_night], ignore_index=True)

            # print(df_active_nights)
            # save on disk df_active_nights
            df_active_nights.to_csv(path_out+'active_'+sample, index=False)
            
        except ValueError:
            print('Problem reading the file', sample, '... it is skipped.')

    

