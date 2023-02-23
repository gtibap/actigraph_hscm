import numpy as np
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



def non_motion_periods(mag_col, selected_column):
    # nights_list = df['night'].unique().tolist()
    min_value = 3 # min intensity value
    # for night_num in nights_list[:1]:
    # mag_col = df.loc[(df['night']==night_num), ['Vector Magnitude']]

    # 'Vector Magnitude' values greater than 'min_value' and when 'Inclinometer Off' is 1
    # mag_col['active'] = (mag_col['Vector Magnitude'] > min_value) & (mag_col['Inclinometer Off'])
    # mag_col['active'] = (mag_col['Vector Magnitude'] > min_value) & (mag_col['Inclinometer Sitting/Lying'])
    mag_col['active'] = (mag_col['Vector Magnitude'] > min_value) & (mag_col[selected_column])

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
    path = "../data/all_data_1s/counts_missing/"
    path_out = "../data/results_counts_10s_missing/"
    files_list = os.listdir(path)
    
    print("Files Actigraph registration '", path, "' :")
    # prints all files
    print(files_list)

    # the header in line 10 of the csv file
    header_location=10
    time_start='22:00:00'
    time_end='10:00:00'
    same_day=False

    # selected_column = 'Inclinometer Off'
    selected_column = 'Inclinometer Sitting/Lying'

    for sample in files_list:
        print('file: ', sample)
        try:
            # df1 = pd.read_csv(path+sample, header=header_location, decimal=',', usecols=['Date',' Time', 'Inclinometer Off', 'Vector Magnitude'])
            # df1 = pd.read_csv(path+sample, header=header_location, decimal=',', usecols=['Date',' Time', 'Inclinometer Sitting/Lying', 'Vector Magnitude'])
            df1 = pd.read_csv(path+sample, header=header_location, decimal=',', usecols=['Date',' Time', selected_column, 'Vector Magnitude'])
            
            # print(df1.columns)
            print('file sample: ', sample)
            print(df1.head)
            # print(df1.info())
            # every night comprises 'Vector Magnitude' values from 22h00 to 10h00
            df_nights = getSelectedData(df1, time_start, time_end, same_day)
            # print(df_nights.info())

            df_results=pd.DataFrame(columns=['nights', 'counts'])

            # extracting blocs of data per night
            nights_list = df_nights['night'].unique().tolist()
            print('nights: ', nights_list)

            df_results['nights'] = nights_list

            all_count_groups=[]
            for night_num in nights_list:

                # df_mag = df_nights.loc[(df_nights['night']==night_num), ['Inclinometer Off', 'Vector Magnitude']]
                # df_mag = df_nights.loc[(df_nights['night']==night_num), ['Inclinometer Sitting/Lying', 'Vector Magnitude']]
                df_mag = df_nights.loc[(df_nights['night']==night_num), [selected_column, 'Vector Magnitude']]
                
                # df_mag_thigh = df_thigh.loc[(df_chest['night']==night_num), ['Vector Magnitude']]

                # chest        
                # duration of continuous periods of actitity and inactivity in seconds
                activity, inactivity, start_active = non_motion_periods(df_mag, selected_column)

                # print ('results night ', night_num, len(activity), len(inactivity), start_active)
                # print('activity: ', activity)
                # print('inactivity: ', inactivity)

                min_gap = 10 # seconds
                small_gap =  inactivity < min_gap
                # print('small_gap: ', small_gap)
            
                # long_result = np.array([])
                # new_activity = list()
                count_groups=0
                # id_ac = 0
                # if start_active == True:
                #     id_in = 0
                # else:
                #     id_in = 1
                    # number of zeros; one zero per second
                    # long_result = np.concatenate((long_result, np.zeros(inactivity[0], np.int8)), axis=None)
                id_in = 0
                # print('id_in: ', id_in)
                # while id_ac < (len(activity)-1):
                while id_in < len(small_gap):
                    # acc_temp = activity[id_ac]
                    # acc_neta = activity[id_ac]
                    # true means that the gap is less than min_gap
                    while (small_gap[id_in]==True) and (id_in < (len(small_gap)-1)):
                        # id_ac+=1
                        # acc_temp += activity[id_ac]
                        # acc_neta += activity[id_ac] + inactivity[id_in]
                        id_in+=1
                    # new_activity.append(acc_temp)
                    # 1 per activity group per second
                    # longitudinal_result.append(acc_neta*[1])
                    # long_result = np.concatenate((long_result, np.ones(acc_neta,np.int8)), axis=None)
                    # 0 per inactivity group per second
                    # longitudinal_result.append(inactivity[id_in]*[0])
                    # long_result = np.concatenate((long_result, np.zeros(inactivity[id_in],np.int8)), axis=None)
                    count_groups+=1
                    # id_ac+=1
                    id_in+=1
                
                # print('count_groups: ', count_groups)
                all_count_groups.append(count_groups)

            df_results['counts'] = all_count_groups
            print(df_results)
            df_results.to_csv(path_out+'counts_'+sample, index=False)
        
        except ValueError:
            print('Problem reading the file', sample, '... it is skipped.')




    # nights = list(range(0,len(all_count_groups)))
    # print(nights)
    # print(all_count_groups)
    # plt.bar(nights[:-1], all_count_groups[:-1])
    # plt.xlabel('night')
    # plt.ylabel('count of detected motions')
    # plt.show()



        # print('new_activity: ', new_activity)
        # print('longitudinal_result: ', len(long_result))
        # print('sum: ', np.sum(activity)+np.sum(inactivity))
        # print('inactivity: ', inactivity)
        # print('new_inacti: ', inactivity[inactivitymin_gap])
        # print('iqual? : ', np.sum(activity), np.sum(new_activity))

        # delta=60 # seconds
        # new_long = []
        # for idx in np.arange(0, len(long_result), delta):
        #     new_long.append(np.sum(long_result[idx:idx+delta]))

        # print('new_long: ', new_long)
        # plt.figure()
        # plt.plot(long_result)
        # plt.figure()
        # plt.plot(new_long)

        # # plt.hist(long_result)
        # # mu, sigma = 100, 15
        # plt.show()



    #     df_a = pd.DataFrame(columns=['night', 'location', 'activity','inactivity'])
    #     df_a['activity'] = activity
    #     df_a['inactivity'] = inactivity
    #     df_a['night'] = night_num
    #     df_a['location'] = 'chest'

    #     max_list_chest.append(df_a['inactivity'].max())
    #     # print(df_a.head())
    #     df_freqs=pd.concat([df_freqs, df_a], ignore_index=True)
    #     # chest
    #     # thigh        
    #     # duration of continuous periods of actitity and inactivity in seconds
    #     activity, inactivity = non_motion_periods(df_mag_thigh)

    #     df_a = pd.DataFrame(columns=['night', 'location', 'activity','inactivity'])
    #     df_a['activity'] = activity
    #     df_a['inactivity'] = inactivity
    #     df_a['night'] = night_num
    #     df_a['location'] = 'thigh'

    #     max_list_thigh.append(df_a['inactivity'].max())
    #     # print(df_a.head())
    #     df_freqs=pd.concat([df_freqs, df_a], ignore_index=True)
    #     # thigh

    # print('maxlistchest: ', max_list_chest)
    # print('maxlistthigh: ', max_list_thigh)

    # print('df_freqs.head: ', df_freqs.head())

    # max_yaxis = max(np.amax(max_list_chest[:-1]), np.amax(max_list_thigh[:-1]))

    # df_c = df_freqs.loc[(df_freqs['night']!=7) & (df_freqs['location']=='chest')]
    # function_boxplot(df_c, max_yaxis, 'inactivity periods recorded on the chest')

    # df_t = df_freqs.loc[(df_freqs['night']!=7) & (df_freqs['location']=='thigh')]
    # function_boxplot(df_t, max_yaxis, 'inactivity periods recorded on the thigh')

