import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_data(df, fig_title):
    dates_list = df['Date'].unique().tolist()
    print(dates_list, len(dates_list), type(dates_list))

    fig, axes = plt.subplots(nrows=3, ncols=3, subplot_kw={'ylim': (0,250)})
    fig.canvas.set_window_title(fig_title)
    fig.suptitle(fig_title, fontsize=16)
    row=0
    col=0
    for day_now, day_next in zip(dates_list, dates_list[1:]):
        df_night_part0 = df.loc[(df['Date']==day_now) & (df[' Time']>='22:00:00'), ['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude']]
        df_night_part1 = df.loc[(df['Date']==day_next) & (df[' Time']<='10:00:00'), ['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude']]

        df_night = pd.concat([df_night_part0, df_night_part1], ignore_index=True) 

        df_night.plot(x=' Time', y='Vector Magnitude', title='', ax=axes[row,col])
        col+=1
        if col==3:
            col=0
            row+=1
        else:
            pass
        
    return


def getSelectedData(df, time0, time1, same_day):

    dates_list = df['Date'].unique().tolist()
    print(dates_list, len(dates_list), type(dates_list))

    names_columns = df.columns.tolist()
    names_columns.append('night')

    # print(names_columns)

    # empty dataframe initialization
    df_all = pd.DataFrame(columns=names_columns)

    cont_nights=0
    if same_day==False:
        for day_now, day_next in zip(dates_list, dates_list[1:]):
            df_night_part0 = df.loc[(df['Date']==day_now) & (df[' Time']>=time0), ['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude']]
            df_night_part1 = df.loc[(df['Date']==day_next) & (df[' Time']<=time1), ['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude']]

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
    else:
        for day_now in dates_list:
            df_night = df.loc[(df['Date']==day_now) & (df[' Time']>=time0) & (df[' Time']<=time1), ['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude']]
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


def plot_nights(df1,df2):
    nights_list = df1['night'].unique().tolist()
    # print('nights: ', nights_list)
    fig, axes = plt.subplots(nrows=2, ncols=1, subplot_kw={'ylim': (0,250)})
    
    for night_num in nights_list[:1]:
        df1_night = df1.loc[(df1['night']==night_num), ['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude']]
        df2_night = df2.loc[(df2['night']==night_num), ['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude']]
        df1_night.plot(x=' Time', y='Vector Magnitude', ax=axes[0], label='magnitude (chest)')
        df2_night.plot(x=' Time', y='Vector Magnitude', ax=axes[1], label='magnitude (thigh)')
        # df_night.plot(x=' Time', y='Vector Magnitude', , ax=axes[row,col])
    return


def non_motion_periods(mag_col):
    # nights_list = df['night'].unique().tolist()
    min_value = 3
    # for night_num in nights_list[:1]:
    # mag_col = df.loc[(df['night']==night_num), ['Vector Magnitude']]

    mag_col['active'] = mag_col['Vector Magnitude'] > min_value

    active_arrray = mag_col['active'].to_numpy()
    print(active_arrray)
    changes_array = active_arrray[:-1] != active_arrray[1:]
    print(changes_array)
    idx_changes = np.flatnonzero(changes_array)
    print(idx_changes)
    # print(active_arrray[idx_changes])
    intervals = idx_changes[1:]-idx_changes[:-1]
    print(intervals)

    initial_value = [idx_changes[0] + 1]
    if active_arrray[idx_changes[0]]==False:
        duration_active = intervals[::2]
        duration_inactive = np.concatenate([initial_value, intervals[1::2]])
    else:
        duration_active = np.concatenate([initial_value, intervals[1::2]])
        duration_inactive = intervals[::2]

    print(duration_active)
    print(duration_inactive)
    
    return duration_active, duration_inactive


# histograms
def activityHistogram(activity, inactivity):

    # print(type(activity))
    binwidth=1
    # plt.hist(activity, bins=range(min(activity), max(activity) + binwidth, binwidth))
    # plt.hist(inactivity, bins=range(min(inactivity), max(inactivity) + binwidth, binwidth))
    plt.hist(inactivity)  # density=False would make counts
    plt.ylabel('Probability')
    plt.xlabel('Data')
    plt.show()

    return




        # print(mag_col.info())
        # print(mag_col.describe())
        # print(mag_col.head)
        # mag_array = mag_col.to_numpy()
        # print('vector magnitud: ', len(mag_array), mag_array[0], mag_array[0][0])
        # # find first value non-zero in the list
        # min_value = 3
        # count=0
        # while mag_array[count][0] < min_value:
        #     count+=1
        # print('count: ', count)
        # ts=0

    

# def plot_seaborn(df, fig_title):

#     sns.set(rc={'figure.figsize': (15, 5)}, style='white')
#     ax = sns.lineplot( data=long_df, x='date', y='value', hue='datatype')

####### main function ###########
if __name__== '__main__':

    # the header in line 10 of the csv file
    header_location=10
    df1 = pd.read_csv("../data/p00/Turner Chest1secDataTable.csv", header=header_location, decimal=',', usecols=['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude'])
    # print(df.empty)
    # print(df.shape)
    print(df1.columns)
    # print(df.head)
    print(df1.info())
    
    df2 = pd.read_csv("../data/p00/Turner Thigh1secDataTable.csv", header=header_location, decimal=',', usecols=['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude'])
    # print(df.empty)
    # print(df.shape)
    print(df2.columns)
    # print(df.head)1
    print(df2.info())
    
    
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

    time_start='22:00:00'
    time_end='10:00:00'
    same_day=False

    # time_start='04:45:00'
    # time_end='05:45:00'
    # same_day=True

    


    df_chest = getSelectedData(df1, time_start, time_end, same_day)
    df_thigh = getSelectedData(df2, time_start, time_end, same_day)
    # print(df1_nights.columns)
    # print(df1_nights.info())
    # print(df1_nights.head)

    # plot_nights(df_chest, df_thigh)
    # plt.show()

    nights_list = df_chest['night'].unique().tolist()
    for night_num in nights_list[:1]:
        mag_col = df_chest.loc[(df_chest['night']==night_num), ['Vector Magnitude']]
        activity, inactivity = non_motion_periods(mag_col)
        activityHistogram(activity, inactivity)


    # fig, axes = plt.subplots(nrows=3, ncols=3, subplot_kw={'ylim': (0,250)})

    # # df_one_day = df.loc[(df['Date']=='13/12/2022') & ((df[' Axis1']>0)|(df['Axis2']>0)|(df['Axis3']>0)), ['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude']]
    # row=0
    # col=0
    # for date in dates_list:
    # # date_0 = '12/12/2022'
    # # date_1 = '13/12/2022'
    # # date_2 = '14/12/2022'
    # # date_3 = '15/12/2022'

    #     df_day = df.loc[(df['Date']==date), [' Time','Vector Magnitude']]
    # # df_day_0 = df.loc[(df['Date']==date_0), [' Time','Vector Magnitude']]
    # # df_day_1 = df.loc[(df['Date']==date_1), [' Time','Vector Magnitude']]
    # # df_day_2 = df.loc[(df['Date']==date_2), [' Time','Vector Magnitude']]
    # # df_day_3 = df.loc[(df['Date']==date_3), [' Time','Vector Magnitude']]
    #     df_day.plot(x=' Time', y='Vector Magnitude', title='', ax=axes[row,col])
    # # df_day_0.plot(x=' Time', y='Vector Magnitude', title='Day '+ date_0, ax=axes[0,0])
    # # df_day_1.plot(x=' Time', y='Vector Magnitude', title='Day '+ date_1, ax=axes[0,1])
    # # df_day_2.plot(x=' Time', y='Vector Magnitude', title='Day '+ date_2, ax=axes[1,0])
    # # df_day_3.plot(x=' Time', y='Vector Magnitude', title='Day '+ date_3, ax=axes[1,1])
    #     col+=1
    #     if col==3:
    #         col=0
    #         row+=1


    # plt.show()

    # print(df.loc[df['Date']=='13/12/2022',['Time']])
