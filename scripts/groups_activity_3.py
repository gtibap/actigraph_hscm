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

#######################
# global variables
# fig, axes = plt.subplots(nrows=2, ncols=2, sharex=True)
incl_off ='Inclinometer Off'
incl_sta ='Inclinometer Standing'
incl_sit ='Inclinometer Sitting'
incl_lyi ='Inclinometer Lying'
vec_mag  ='Vector Magnitude'

# global variables
#######################


def activity_sectors(df, min_value):
    
    # nights_list = df['night'].unique().tolist()
    # min_value = 3 # min intensity value
    # for night_num in nights_list[:1]:
    # mag_col = df.loc[(df['night']==night_num), ['Vector Magnitude']]
    # min_gap = 10 # seconds

    df['activity'] = df[vec_mag] > min_value
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

    # time-intervals motion and non-motion per night
    # print('duration_active: ', duration_active)
    # print('duration_inactive: ', duration_inactive)

    return duration_active, duration_inactive


def plot_motion_seq(duration_active, duration_inactive, areas_active, areas_active_mean):

    fig, axes = plt.subplots(nrows=2, ncols=2)
    
    axes[0][0].plot(duration_active)
    axes[1][0].plot(areas_active)

    axes[0][1].plot(duration_inactive)
    axes[1][1].plot(areas_active_mean)

    plt.show()

    return

def areas_mean(ampl_vector, idx_ini, idx_end):

    # ampl_vector = df[vec_mag].to_numpy()
    # print('ampl vector:', len(ampl_vector), min(ampl_vector), max(ampl_vector))
    areas=[]
    
    for idx_0, idx_1 in zip(idx_ini,idx_end):
        # print('idx: ', idx_0, idx_1)
        areas.append(np.mean(ampl_vector[idx_0:idx_1]) * (idx_1-idx_0))

    return areas

def window_mean(a, window_size):
  window = np.ones(window_size)/float(window_size)
  return np.convolve(a, window, 'same')


def pos_non_active(df_data, df_non_active):

    vector_off = df_data[incl_off].to_numpy()
    vector_lyi = df_data[incl_lyi].to_numpy()
    vector_sit = df_data[incl_sit].to_numpy()
    vector_sta = df_data[incl_sta].to_numpy()

    idx_ini = df_non_active['t_ini'].to_numpy()
    idx_end = df_non_active['t_end'].to_numpy()

    df_counts = pd.DataFrame()
    for ii, ie in zip(idx_ini, idx_end):
        sum_off = np.sum(vector_off[ii:ie])
        sum_lyi = np.sum(vector_lyi[ii:ie])
        sum_sit = np.sum(vector_sit[ii:ie])
        sum_sta = np.sum(vector_sta[ii:ie])
        
        some_row = pd.DataFrame([{'sum_off':sum_off, 'sum_lyi':sum_lyi, 'sum_sit': sum_sit, 'sum_sta':sum_sta}])
        df_counts = pd.concat([df_counts, some_row])

    df_counts['total'] = df_non_active['duration'].to_numpy()
    # print (df_non_active['duration'].to_numpy())
    # print ('len duration: ', len(df_non_active['duration'].to_numpy()))
    # print(df_counts)
    return df_counts


def plot_counts_non_active(df_counts):
    fig, axes = plt.subplots(nrows=5, ncols=1)
    
    axes[0].plot(df_counts['sum_off'].to_numpy())
    axes[1].plot(df_counts['sum_lyi'].to_numpy())
    axes[2].plot(df_counts['sum_sit'].to_numpy())
    axes[3].plot(df_counts['sum_sta'].to_numpy())
    axes[4].plot(df_counts['total'].to_numpy())

    # plt.show()

    return


####### main function ###########
if __name__== '__main__':

    # Get the list of all files and directories
    path = "../data/all_data_1s/"
    path_results_in = "../data/results_motion/"
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


    header_location=10
    for sample in files_list[:1]:
        print('file here: ', sample)
        try:
            df1 = pd.read_csv(path+sample, header=header_location, decimal=',', usecols=['Date',' Time', vec_mag, incl_off, incl_lyi, incl_sit, incl_sta])
            # print(df1.info())

            # indexes start and end of each activity sector in the Vector Magnitude
            df_active_nights = pd.read_csv(path_results_in+'active_'+sample)
            df_non_active_nights = pd.read_csv(path_results_in+'non_active_'+sample)
            # print(df_active_nights.info())

            # getting all nights data
            df_nights = getSelectedData(df1, time_start, time_end, same_day)
            # print(df_nights.info())

            # plot 'Vector Magnitude' night by night
            nights_list = df_nights['night'].unique().tolist()
            # print('nights: ', nights_list)
            
            for night_num in nights_list[:1]:
                # print('night: ', night_num)
                df_n = df_nights.loc[(df_nights['night']==night_num)]
                # print('df_n.info: ', df_n.info())
                # print(df_n.head())
                # print(df_n.tail())

                # identifying sectors of activity per night where gaps of 10s of inactivity are considered part of the activity section
                # min_gap=10 # seconds
                # min_value=3 # Vector Magnitude should be greater than this value to be considered as a valid motor activity
                # duration_active, duration_inactive=activity_sectors(df_n, min_value)

                df_a = df_active_nights.loc[(df_active_nights['night']==night_num)]
                df_b = df_non_active_nights.loc[(df_non_active_nights['night']==night_num)]

                idx_ini = df_a['t_ini'].to_numpy()
                idx_end = df_a['t_end'].to_numpy()
                duration_active = df_a['duration'].to_numpy()
                duration_inactive = df_b['duration'].to_numpy()
                # print('a duration_active: ', duration_active)
                # print('a duration_inactive: ', duration_inactive)

                ampl_vector = df_n[vec_mag].to_numpy()
                areas_active = areas_mean(ampl_vector, idx_ini, idx_end)
                
                df_counts=pos_non_active(df_n, df_b)
                plot_counts_non_active(df_counts)

                window_size=2 # samples
                # average_window = window_mean(areas_active, window_size)
                average_window = window_mean(duration_inactive, window_size)


                # plot durantion active and duration inactive
                plot_motion_seq(duration_active, duration_inactive, areas_active, average_window)

               
                # plt.show()
                
            
        except ValueError:
            print('Problem reading the file', sample, '... it is skipped.')

    

