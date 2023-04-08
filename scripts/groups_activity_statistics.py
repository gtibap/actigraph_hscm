
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

##################
# global variables
fig_initial, ax_initial = plt.subplots(nrows=5, ncols=1, sharex=True)
fig_stems, ax_stems = plt.subplots(nrows=1, ncols=1)
fig_act, ax_act = plt.subplots(nrows=5, ncols=1, sharex=True)
x_sel=0
night_num=0
df_n=pd.DataFrame()
activity_vector=np.array([])
df_act_night = pd.DataFrame()

vec_mag  ='Vector Magnitude'
incl_off ='Inclinometer Off'
incl_sta ='Inclinometer Standing'
incl_sit ='Inclinometer Sitting'
incl_lyi ='Inclinometer Lying'

# global variables
##################


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


def activity_sectors(activity_arrray):
    
    # nights_list = df['night'].unique().tolist()
    # min_value = 3 # min intensity value
    # for night_num in nights_list[:1]:
    # mag_col = df.loc[(df['night']==night_num), ['Vector Magnitude']]
    # min_gap = 10 # seconds

    # df['activity'] = df[vector_mag] > min_value
    # # boolean array where True means activity higher than min_value
    # activity_arrray = df['activity'].to_numpy()
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

    if duration_active.size == 0:
        duration_active=np.array([0])
    else:
        pass
    
    if duration_inactive.size == 0:
        duration_inactive=np.array([0])
    else:
        pass

    # time-intervals motion and non-motion per night
    print('duration_active: ', duration_active)
    print('duration_inactive: ', duration_inactive)

    return duration_active, duration_inactive, start_active, end_active


def redefinition_activity(duration_active, duration_inactive, start_active, end_active, min_gap):

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

    
    
        # if the last values where not included in the previous loop
        # new_activity_array=np.concatenate((new_activity_array, duration_active[cont_id]*[True]))
        # new_activity_array=np.concatenate((new_activity_array, duration_inactive[cont_id]*[False]))


    
    # print('len(new_activity_array): ', len(new_activity_array))
    # print('len(activity_array): ', len(activity_arrray))

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
    if np.sum(changes_activity)>0:
        # indices or location of Trues (changes) values; +1 because I want the index when the data already changed from left to right
        idx_changes = np.flatnonzero(changes_activity) + 1

        # at least three detected changes
        
        if activity_vector[0]==False:
            idx_ini=idx_changes[0::2]
            idx_end=idx_changes[1::2]
        else:
            idx_ini=np.concatenate((0, idx_changes[1::2]), axis=None)
            idx_end=idx_changes[0::2]

        # if the activity finished active (1), the last idx_end is the size of the activity array
        if activity_vector[-1]==True:
            idx_end=np.concatenate([idx_end, len(activity_vector)], axis=None)
        else:
            pass
    else:
        idx_ini=[0]
        idx_end=[0]

    return idx_ini, idx_end


def non_activity_intervals(activity_vector):

    changes_activity = activity_vector[:-1] != activity_vector[1:]
    # changes_array is a boolean vector; True means a change; False means no change
    # indices or location of Trues (changes) values; +1 because I want the index when the data already changed from left to right
    idx_changes = np.flatnonzero(changes_activity) + 1

    # at least three detected changes
    
    if activity_vector[0]==False:
        idx_ini=np.concatenate((0, idx_changes[1::2]), axis=None)
        idx_end=idx_changes[0::2]
    else:
        idx_ini=idx_changes[0::2]
        idx_end=idx_changes[1::2]

    # if the activity finished active (1), the last idx_end is the size of the activity array
    if activity_vector[-1]==False:
        idx_end=np.concatenate([idx_end, len(activity_vector)], axis=None)
    else:
        pass


    return idx_ini, idx_end


def plot_activity(actigraphy, activity_vector, idx_ini,idx_end):

    activity_signal=activity_vector.astype(float)
    
    for id0,id1 in zip(idx_ini,idx_end):
        activity_signal[id0:id1] *= (np.mean(actigraphy[id0:id1]))

    
    fig, axes = plt.subplots(nrows=3, ncols=1,sharex=True)
    axes[0].plot(actigraphy)
    axes[1].plot(activity_vector)
    axes[2].plot(activity_signal)

    axes[0].set_title('motion activity')
    axes[0].set_ylabel('mag. vec')
    axes[1].set_ylabel('det. act.')
    axes[2].set_ylabel('mean act.')
    axes[2].set_xlabel('time (s)')
    


    plt.show()

    return

def plot_areas(actigraphy, idx_ini,idx_end, non_idx_ini, non_idx_end):
    global ax1

    activity_samples=[]
    non_acti_samples=[]

    for id0,id1 in zip(idx_ini,idx_end):
        # print((id1-id0))
        # activity_samples.append( np.mean(actigraphy[id0:id1]) * (id1-id0) )
        activity_samples.append( id1-id0 )

    for id0,id1 in zip(non_idx_ini, non_idx_end):
        non_acti_samples.append( id1-id0 )

    len_as=len(activity_samples)
    len_nas=len(non_acti_samples)
    print('lengths:',len_as, len_nas)
    x_axis = np.arange(len_as + len_nas)
    
    # xa1=x_axis[0::2]
    # xa2=x_axis[1::2]

    if len_nas == len(x_axis[0::2]):
        x_nas=x_axis[0::2]
        x_as =x_axis[1::2]
    else:
        x_nas=x_axis[1::2]
        x_as =x_axis[0::2]


    color = 'tab:blue'
    ax_stems.set_xlabel('samples')
    ax_stems.set_ylabel('non-activity (s)', color=color)
    ax_stems.tick_params(axis='y', labelcolor=color)
    
    markerline1, stemlines1, baseline1 = ax_stems.stem(x_nas, non_acti_samples, basefmt=" ", linefmt =color)
    # plt.setp(stemlines1,'color','green')
    plt.setp(stemlines1, 'color', plt.getp(markerline1,'color'))
    

    ax2 = ax_stems.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:orange'
    ax2.set_ylabel('motor activity (s)', color=color)  # we already handled the x-label with ax1
    ax2.tick_params(axis='y', labelcolor=color)
    
    markerline2, stemlines2, baseline2 = ax2.stem(x_as, activity_samples, basefmt=" ", linefmt =color)
    # plt.setp(stemlines2,'color','red')
    plt.setp(stemlines2, 'color', plt.getp(markerline2,'color'))
    

    ax_initial[0].plot(df_n[vec_mag])
    ax_initial[1].plot(df_n[incl_off])
    ax_initial[2].plot(df_n[incl_lyi])
    ax_initial[3].plot(df_n[incl_sit])
    ax_initial[4].plot(df_n[incl_sta])

    # fig, axes = plt.subplots(nrows=3, ncols=1)
    # axes[0].plot(actigraphy)
    # axes[1].stem(activity_samples, basefmt=" ")
    # axes[2].stem(non_acti_samples, basefmt=" ")
    # # axes[1].stem(np.arange(len(activity_samples)), activity_samples, basefmt=" ")
    # # axes[2].stem(np.arange(len(non_acti_samples)), non_acti_samples, basefmt=" ")

    # # axes[1].plot(activity_samples,'o')
    # # axes[2].plot(activity_signal)

    # axes[0].set_title('motion and non-motion activity')
    # axes[0].set_ylabel('counts')
    # axes[0].set_xlabel('time (s)')
    # axes[0].legend(['Vector Magnitude'])

    # axes[1].set_ylabel('counts*s')
    # axes[1].set_xlabel('samples')
    # axes[1].legend(['area motion'])

    # axes[2].set_ylabel('time (s)')
    # axes[2].set_xlabel('samples')
    # axes[2].legend(['time non-motion'])

    # # axes[2].set_ylabel('mean act.')
    # # axes[2].set_xlabel('time (s)')


    plt.show()

    return


def onclick(event):
    global x_sel, ax_vm
    # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f, name=%s' %
        #   ('double' if event.dblclick else 'single', event.button,
        #    event.x, event.y, event.xdata, event.ydata, event.name))
    print(event.xdata, event.ydata)
    x_sel = int(event.xdata)

    df_night = df_act_night.loc[df_act_night['night']==night_num]
    arr_ini = df_night['t_ini'].to_numpy()
    arr_end = df_night['t_end'].to_numpy()
    
    # dividing in two because in the arr_ini and arr_end we have only half of the indexes (activity)... the other half are in the non-activity part
    x_min = arr_ini[int(x_sel/2)] -3600 # -3600 because one hour before the event
    x_max = arr_end[int(x_sel/2)] +3600 # +3600 because one hour after the event
   
    # ax_act[0].cla()
    for i in np.arange(5):
        ax_act[i].cla()

    ax_act[0].plot(df_n[vec_mag])
    # ax_act[0].plot(activity_vector)
    # ax_act[1].plot(df_n[vec_mag])
    ax_act[1].plot(df_n[incl_off])
    ax_act[2].plot(df_n[incl_lyi])
    ax_act[3].plot(df_n[incl_sit])
    ax_act[4].plot(df_n[incl_sta])
    
    for i in np.arange(0,5):
        ax_act[i].set_xlim(x_min,x_max)
        
    # for  i in np.arange(0,4):
    #     ax_act[i+1].sharex(ax_act[i])
    
    
    fig_act.canvas.draw()
    fig_act.canvas.flush_events()

    # if event.xdata >= id_frame_ini and event.xdata < id_frame_end:
    #     id_frame=int(event.xdata)
    #     id_act=int(event.xdata)
    # else:
    #     pass
    # # print('mouse: ', event.xdata, id_frame_ini, id_frame_end, id_frame)
    return


def active_nights_stats(df_active_nights, nights_samples):

    df_statistics = pd.DataFrame(columns=['night','number_of_movements','min_duration(s)','max_duration(s)','mean_duration(s)','std_duration(s)','total_duration(s)', 'night_duration(s)','duration_ratio(total_in_10h)'])

    nights_list = df_active_nights['night'].unique().tolist()
    print('nights_list2: ', nights_list, nights_samples)

    for night_num, night_sam in zip(nights_list, nights_samples):
        df_n = df_active_nights.loc[(df_active_nights['night']==night_num)]
        
        arr_duration = df_n['duration'].to_numpy()

        if np.amax(arr_duration)>0:
            num_movements = arr_duration.size
        else:
            num_movements = 0
        min_duration = np.amin(arr_duration)
        max_duration = np.amax(arr_duration)
        mean_duration = np.mean(arr_duration)
        std_duration = np.std(arr_duration)
        sum_duration = np.sum(arr_duration)
        per_duration = sum_duration/night_sam   # max value for night_sam is 36000 seconds in ten hours (22h to 8h [next day])

        df_night_stats = pd.DataFrame([[night_num,num_movements,min_duration,max_duration,mean_duration,std_duration,sum_duration,night_sam,per_duration]], columns=['night','number_of_movements','min_duration(s)','max_duration(s)','mean_duration(s)','std_duration(s)','total_duration(s)','night_duration(s)','duration_ratio(total_in_10h)'])

        df_statistics = pd.concat([df_statistics, df_night_stats], ignore_index=True)

    return df_statistics

####### main function ###########
if __name__== '__main__':

    # Get the list of all files and directories
    path_in  = "../data/projet_officiel/"
    path_out = "../data/projet_officiel_stats/"
    files_list = os.listdir(path_in)
    
    print("Files in '", path_in, "' :")
    # prints all files
    print(files_list)

    # the header in line 10 of the csv file
    header_location=10
    time_start='22:00:00'
    time_end='07:59:59'
    same_day=False

    min_gap=10 # seconds
    min_value=3 # Vector Magnitude should be greater than this value to be considered as a valid motor activity
    
    # to run GUI event loop
    # cid1 = fig_stems.canvas.mpl_connect('button_press_event', onclick)

    header_location=10
    for sample in files_list:
        # sample = 'A001_chest.csv'
        if not sample.startswith('.'):
            print('file: ', sample)
            try:
                df1 = pd.read_csv(path_in+sample, header=header_location, decimal=',')
                # usecols=['Date',' Time', vec_mag, incl_off]
                # print(df1.info())

                # getting all nights data
                df_nights, nights_samples = getSelectedData(df1, time_start, time_end, same_day)
                # print(df_nights.info())
                print('nights_samples:', nights_samples)

                # plot 'Vector Magnitude' night by night
                nights_list = df_nights['night'].unique().tolist()
                print('nights 1: ', nights_list)
                
                df_active_nights = pd.DataFrame()
                # df_non_active_nights = pd.DataFrame()

                for night_num in nights_list:
                    print('night_num: ', night_num)
    
                    df_n = df_nights.loc[(df_nights['night']==night_num),[vec_mag]]
     
                    # identifying sectors of activity per night where gaps of 10s of inactivity are considered part of the activity section

                    activity_vector = df_n[vec_mag].to_numpy()
                    activity_vector=activity_vector > min_value
                    # df_n['activity'] = df_n[vec_mag] > min_value
                    # boolean array where True means activity higher than min_value
                    # activity_vector = df_n['activity'].to_numpy()
                    print('activity_vector: ', activity_vector)

                    duration_active, duration_inactive, start_active, end_active=activity_sectors(activity_vector)

                    print('duration_active: ', duration_active)
                    print('duration_inactive: ', duration_inactive)

                    activity_vector=redefinition_activity(duration_active, duration_inactive, start_active, end_active, min_gap)

                    duration_active, duration_inactive, start_active, end_active=activity_sectors(activity_vector)
                    
                    #########
                    idx_ini, idx_end = activity_intervals(activity_vector)
                   
                    df_act_night = pd.DataFrame()
                    df_act_night['t_ini']=idx_ini
                    df_act_night['t_end']=idx_end
                    df_act_night['night']=night_num
                    df_act_night['duration']=duration_active

                    print(df_act_night)

                    df_active_nights=pd.concat([df_active_nights, df_act_night], ignore_index=True)
  
                df_night_stats = active_nights_stats(df_active_nights, nights_samples)

                words=sample.split('.')
                path_out_stats=path_out+words[0]+'_stats.csv'
                print('path output: ', path_out_stats)
                df_night_stats.to_csv(path_out_stats, index=False)
                
            except ValueError:
                print('Problem reading the file', sample, '... it is skipped.')
        
        else:
            print(f'Skipping {sample} because is a hidden file.')