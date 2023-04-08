import numpy as np
import numpy.ma as ma
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D
import datetime
import seaborn as sns
import os


# Selecting data from time_0 to time_1 from all days. It could be from the same day or two consecutive days. For example, from 22h (current day) to 10h (next day); from 17h to 19h same day
# the function returns a DataFrame that includes the 'night' column (int from 0 - N), which allows to identify each selected period
def getSelectedData(df, time0, time1, same_day):

    dates_list = df['Date'].unique().tolist()
    print(dates_list, len(dates_list), type(dates_list))

    names_columns = df.columns.tolist()
    names_columns.append('night')

    # print(names_columns)

    # empty dataframe initialization
    df_all = pd.DataFrame(columns=names_columns)

    cont_nights=1
    if same_day==False:
        for day_now, day_next in zip(dates_list, dates_list[1:]):
            # df_now =df.loc[(df['Date']==day_now)]
            # df_next=df.loc[(df['Date']==day_next)]
            df_night_part0 = df.loc[(df['Date']==day_now) & (df[' Time']>=time0)]
            df_night_part1 = df.loc[(df['Date']==day_next) & (df[' Time']<=time1)]

            df_night = pd.concat([df_night_part0,df_night_part1],  ignore_index=True)
            df_night['night']=cont_nights
            # print('night number ', cont_nights)
            # print(df_night.info())
            # print(df_night.head)
            cont_nights+=1

            # adding a column number of nights

            df_all=pd.concat([df_all, df_night], ignore_index=True)
            # print(df_all.info())
            # print(df_all.head)
            # fig, axes = plt.subplots(nrows=3, ncols=1)
            # df_now['Vector Magnitude'].plot(ax=axes[0])
            # df_next['Vector Magnitude'].plot(ax=axes[1])
            # df_night['Vector Magnitude'].plot(ax=axes[2])
            # plt.show()

    else:
        for day_now in dates_list:
            df_night = df.loc[(df['Date']==day_now) & (df[' Time']>=time0) & (df[' Time']<=time1)]
            # df_night_part1 = df.loc[(df['Date']==day_next) & (df[' Time']<=time1), ['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude']]

            # df_night = df_night_part0.append(df_night_part1)
            df_night['night']=cont_nights
            # print('night number ', cont_nights)
            # print(df_night.info())
            # print(df_night.head)
            cont_nights+=1

            # adding a column number of nights

            df_all=pd.concat([df_all, df_night], ignore_index=True)
            # print(df_all.info())
            # print(df_all.head)

    return df_all        


def statistics_motion_2(df, night_num, incl_pos):
    
    min_value = 3 # min intensity value

    acc_spend_0=0
    acc_spend_1=0
    values_all=[night_num]
    for incl_single in incl_pos:
        # print('incl single: ', incl_single)
        # activity per 1 second
        spend_0 = df[incl_single].sum()

        binary_array = (df['Vector Magnitude'] > min_value) & (df[incl_single])
        spend_1 = np.sum(binary_array)

        acc_spend_0+=spend_0
        acc_spend_1+=spend_1

        values_all.append(spend_1)
        values_all.append(spend_0)

        # print('spending time '+incl_single+': ', spend_0, spend_1)
    # print('acc: ', acc_spend_0, acc_spend_1)
    values_all.append(acc_spend_1)
    values_all.append(acc_spend_0)

    return values_all


def non_motion_periods(mag_col, inclinometer_pos):
    # nights_list = df['night'].unique().tolist()
    min_value = 3 # min intensity value
    # for night_num in nights_list[:1]:
    # mag_col = df.loc[(df['night']==night_num), ['Vector Magnitude']]

    # 'Vector Magnitude' values greater than 'min_value' and when 'Inclinometer Off' is 1
    # mag_col['active'] = (mag_col['Vector Magnitude'] > min_value) & (mag_col['Inclinometer Off'])
    # mag_col['active'] = (mag_col['Vector Magnitude'] > min_value) & (mag_col['Inclinometer Sitting/Lying'])
    mag_col['active'] = (mag_col['Vector Magnitude'] > min_value) & (mag_col[inclinometer_pos])

    # mag_col['active'] = (mag_col['Vector Magnitude'] > min_value)
    # boolean array where True means activity higher than min_value
    active_arrray = mag_col['active'].to_numpy()
    # print('active_arrray: ', active_arrray)
    # comparison of active _array (boolean vector) with itself but moved one position. The idea is to identify changes--True to False or False to True.
    changes_array = active_arrray[:-1] != active_arrray[1:]
    # changes_array is a boolean vector; True means a change; False means no change
    # print('changes: ', changes_array)
    # indices or location of Trues (changes) values 
    idx_changes = np.flatnonzero(changes_array)

    if len(idx_changes)>0:
        # print('idx_changes: ', idx_changes)
        # print(active_arrray[idx_changes])
        # distance between two consecutive changes (time in our case)
        intervals = idx_changes[1:]-idx_changes[:-1]
        # print('intervals: ', intervals)

        # period before the first detection of change in activity
        # print('idx_changes[0]: ', idx_changes[0])
        initial_value = [idx_changes[0] + 1]
        # if false means that the collected data start with inactivity. The first detected change is from inactivity to activity; therefore, the intervals[0] is the first period of activity
        
        # print('len(active_arrray): ', len(active_arrray))
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
    else:
        duration_active=np.array([0])
        duration_inactive=np.array([len(active_arrray)])
        start_active=False

    return duration_active, duration_inactive, start_active


####### main function ###########
if __name__== '__main__':

    # Get the list of all files and directories
    path = "../data/all_data_1s/"
    path_out = "../data/results_each_pose/"
    files_list = os.listdir(path)
    
    print("Files Actigraph registration '", path, "' :")
    # prints all files
    print(files_list)

    # the header in line 10 of the csv file
    header_location=10
    time_start='22:00:00'
    time_end='08:00:00'
    same_day=False

    # inclinometer_pos = 'Inclinometer Off'
    incl_off ='Inclinometer Off'
    incl_sta ='Inclinometer Standing'
    incl_sit ='Inclinometer Sitting'
    incl_lyi ='Inclinometer Lying'
    # inclinometer_pos = 'Inclinometer Sitting/Lying'

    for sample in files_list:
        print('file: ', sample)
        try:
 
            df1 = pd.read_csv(path+sample, header=header_location, decimal=',', usecols=['Date',' Time', incl_off, incl_sta, incl_sit, incl_lyi, 'Vector Magnitude'])
            
            # print(df1.columns)
            print('file sample: ', sample)
            print(df1.head)
            # print(df1.info())
            # every night comprises 'Vector Magnitude' values from 22h00 to 8h00
            df_nights = getSelectedData(df1, time_start, time_end, same_day)
            # print(df_nights.info())

            # df_results=pd.DataFrame(columns=['nights', 'counts'])
            # df_statistics = pd.DataFrame(columns=['night','min','max','median','mean','std','valid_samples','inclinometer_samples','total_samples'])
            df_statistics = pd.DataFrame(columns=['night',incl_off+'_active',incl_off+'_total', incl_sta+'_active', incl_sta+'_total', incl_sit+'_active',incl_sit+'_total', incl_lyi+'_active',incl_lyi+'_total', 'total_active','total_total'])

            # extracting blocs of data per night
            nights_list = df_nights['night'].unique().tolist()
            print('nights: ', nights_list)

            for night_num in nights_list:

                print('\nnight number: ', night_num)

                df_mag = df_nights.loc[(df_nights['night']==night_num), [incl_off, incl_sta, incl_sit, incl_lyi, 'Vector Magnitude']]
                
                # calculating mean, std, median, min, and max of 'Vector Magnitude' for the regions when 'Inclinometer Off' or 'Inclinometer Sitting/Lying' are active (1)
                # min,max,median,mean,std,valid_samples, inclinometer_samples, total_samples = statistics_motion_2(df_mag, [incl_off, incl_sta, incl_sit, incl_lyi])
                values_spended = statistics_motion_2(df_mag, night_num, [incl_off, incl_sta, incl_sit, incl_lyi])
                # print('values_spended: ', values_spended)

                df_night_stat = pd.DataFrame([values_spended],columns=['night',incl_off+'_active',incl_off+'_total', incl_sta+'_active', incl_sta+'_total', incl_sit+'_active',incl_sit+'_total', incl_lyi+'_active',incl_lyi+'_total', 'total_active','total_total'])

                # print('min,max,median,mean,std,valid_samples,inclinometer_samples,total_samples: ', min,max,median,mean,std,valid_samples,inclinometer_samples,total_samples)

                # df_night_stat = pd.DataFrame([[night_num, min, max, median, mean, std,valid_samples,inclinometer_samples,total_samples]],columns=['night','min','max','median','mean','std','valid_samples','inclinometer_samples','total_samples'])

                # print('night_stat: ', df_night_stat)
                df_statistics = pd.concat([df_statistics, df_night_stat], ignore_index=True)

            # print(df_statistics)
            # df_results.to_csv(path_out+'counts_'+sample, index=False)
            df_statistics.to_csv(path_out+'stat_'+sample, index=False)
        
        except ValueError:
            print('Problem reading the file', sample, '... it is skipped.')



