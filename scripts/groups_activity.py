import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D
import datetime
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
    fig, axes = plt.subplots(nrows=2, ncols=1)
    # fig.suptitle('Vector Magnitude', fontsize=12)
    # fig.subplots_adjust(wspace=0, hspace=10)
    # fig, axes = plt.subplots(subplot_kw={'ylim': (0,150)})

    ax1 = axes[0]
    # ax1.set_ylabel('counts')
    # ax1.set_xlabel('')
    # ax1.set_ylim(0, 200)
    # ax1.legend(["chest"])

    ax2 = axes[1]
    # ax2.set_ylabel('counts')
    # ax2.set_ylim(0, 200)
    # ax2.legend(["thigh"])


    for night_num in nights_list[:1]:
        df1_night = df1.loc[(df1['night']==night_num), ['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude']]
        df2_night = df2.loc[(df2['night']==night_num), ['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude']]

        print('length column Time:', len(df1_night[' Time']))
        xmin = 0 
        xmax = len(df1_night[' Time'])

        # presenting xticks in hh:mm format
        xdelta = 3600 # seconds in one hour
        xticks = np.arange(xmin,xmax,xdelta)
        hours = np.floor(xticks/3600).astype(int)
        mins  = np.floor(np.remainder(xticks,3600)/60).astype(int)
        xlabels = [str(i)+':'+str(j) for i, j in zip(hours, mins)]
        xlabels_2 = xlabels.copy()
        xlabels_2[0] = xlabels[0]+'\n22h00'
        xlabels_2[-1] = xlabels[-1]+'\n10h00'
        print(hours)
        print(mins)
        print(xlabels)
        # xlabels = np.around(xrange/3600,decimals=2)
        ymin = 0
        ymax = 210
        ylabel = 'counts (1s epoch)'
        xlabel = 'time (hh:mm)'
        # bx1=df1_night.plot(x=' Time', y='Vector Magnitude', ax=ax1, alpha=1.0, xlabel='', xticks=(np.arange(0, len(df1_night[' Time'])+1, 3600)))
        bx1=df1_night.plot(x=' Time', y='Vector Magnitude', ax=ax1, alpha=1.0)
        bx1.set_xlim([xmin, xmax])
        bx1.set_ylim([ymin, ymax])
        bx1.set_xticks(xticks)
        bx1.set_xticklabels(xlabels)
        bx1.set_ylabel(ylabel)
        bx1.set_xlabel('')
        bx1.set_title("Vector Magnitude")
        bx1.legend(["chest"])
        # bx1.set_xticklabels(np.arange(0, len(df1_night[' Time'])+1, 3600))
        
        # print([xlabels[0]+'\n22h00', xlabels[1:-1], xlabels[-1]+'\n10h00'])
        # bx1.xlabel('')
        bx2=df2_night.plot(x=' Time', y='Vector Magnitude', ax=ax2,  alpha=1.0)
        bx2.set_xlim([xmin, xmax])
        bx2.set_ylim([ymin, ymax])
        bx2.set_xticks(xticks)
        bx2.set_xticklabels(xlabels_2)
        bx2.set_ylabel(ylabel)
        bx2.set_xlabel(xlabel)
        bx2.legend(["thigh"])
        # bx2.set_title("Vector Magnitude : Thigh")

        # bx2.set_xticks(np.arange(0, 12, step=0.2), np.arange(0, 12, step=0.2))
        # xticks(np.arange(0, 1, step=0.2))
        # bx2.xlabel('Time (h)')
        # bx1=df1_night.plot(x=' Time', y='Vector Magnitude', alpha=0.5, ax=axes, label='chest')
        # bx1.legend(["chest"])
        # bx2=df2_night.plot(x=' Time', y='Vector Magnitude',  alpha=0.5, ax=axes, label='thigh')
        # bx2.legend(["thigh"])
        # df_night.plot(x=' Time', y='Vector Magnitude', , ax=axes[row,col])
    return

# def plot_nights_2(df1,df2):
#     nights_list = df1['night'].unique().tolist()
#     # print('nights: ', nights_list)
#     fig, axes = plt.subplots(nrows=2, ncols=1, subplot_kw={'ylim': (0,250)})
    
#     ax1 = axes[0]
#     ax1.set_ylabel('counts')
#     ax1.set_ylim(0, 250)

#     ax2 = axes[1]
#     ax2.set_ylabel('counts')
#     ax2.set_ylim(0, 250)

#     for night_num in nights_list[:1]:
#         df1_night = df1.loc[(df1['night']==night_num), ['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude']]
#         df2_night = df2.loc[(df2['night']==night_num), ['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude']]
        
#         df1_night.plot(x=' Time', y='Vector Magnitude', ax=ax1, label='magnitude (chest)')
#         df2_night.plot(x=' Time', y='Vector Magnitude', ax=ax2, label='magnitude (thigh)')
#         # df_night.plot(x=' Time', y='Vector Magnitude', , ax=axes[row,col])
#     return


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


# histograms
def activityHistogram(activity, inactivity):

    # print(type(activity))
    binwidth_a=1 # seconds
    binwidth_i=60 # seconds
    binsNum= np.rint((max(activity)-min(activity))/binwidth_a).astype(int)
    # binsNum= np.rint((max(inactivity)-min(inactivity))/binwidth_b).astype(int)

    # plt.hist(activity, bins=range(min(activity), max(activity) + binwidth, binwidth))
    # plt.hist(inactivity, bins= np.linspace(0, 1000, 100))
    # print('bins: ', np.rint((max(inactivity)-min(inactivity))/binwidth).astype(int))
    # print('bins: ', np.rint((max(inactivity)-min(inactivity))/binwidth))
    # print('bins: ', ((max(inactivity)-min(inactivity))/binwidth).astype(int))

    # print('list: ', np.linspace(min(inactivity), max(inactivity),  ))
    # plt.hist(inactivity, bins= np.linspace(min(activity), max(activity), np.rint((max(activity)-min(activity))/binwidth).astype(int) ))
    # plt.figure(1)
    plt.hist(activity, bins=binsNum)  # density=False would make counts
    # plt.hist(inactivity, bins=binsNum)  # density=False would make counts

    # plt.hist(inactivity)  # density=False would make counts
    plt.ylabel('Frequency')
    plt.xlabel('Data')

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

def function_boxplot(df_partial, max_val, title):
    # print('maxlist: ', max_list)
    ydelta = 60 # seconds in one minute
    ymin = 0 
    ymax = max_val + 30*ydelta
    print('ymax: ', ymax)

    # presenting yticks in minutes
    yticks = np.arange(ymin,ymax,ydelta)
    ylabels = [str(int(i/ydelta)) for i in yticks]
    
    # df_partial = df_freqs.loc[df_freqs['night']!=7]
    # fig_1 = plt.figure()
    # sns.catplot(data=df_partial, x="night", y="activity", kind="box")

    print('df_partial.head: ', df_partial.head())
    # fi/g_2 = plt.figure()
    # sns.catplot(data=df_partial, x="night", y="inactivity", kind="box")
    fig_boxplot = sns.boxplot(data=df_partial, x="night", y="inactivity",  
    showcaps=True,
    # flierprops={"marker": "o"},
    boxprops={"facecolor": (.4, .6, .8, .5)},
    medianprops={"color": "coral"},
    )

    delta_yticks = 30
    fig_boxplot.set_yticks(yticks[::delta_yticks])
    fig_boxplot.set_yticklabels(ylabels[::delta_yticks])
    fig_boxplot.set_ylabel('minutes')
    fig_boxplot.set_xlabel('night')
    fig_boxplot.set_title(title)
    # fig_boxplot.legend(["chest"])

    # df_values = df_partial.loc[(df_partial['night']==3)]
    # print('df_values: ', df_values.head())
    # fig_0 = plt.figure()
    # sns.histplot(data=df_values, x='inactivity', bins=100)
    plt.show()
    return
    

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
    print(df1.head)
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
    for night_num in nights_list[:1]:

        df_mag_chest = df_chest.loc[(df_chest['night']==night_num), ['Vector Magnitude']]
        df_mag_thigh = df_thigh.loc[(df_chest['night']==night_num), ['Vector Magnitude']]

        # chest        
        # duration of continuous periods of actitity and inactivity in seconds
        activity, inactivity, start_active = non_motion_periods(df_mag_chest)

        print ('results', len(activity), len(inactivity), start_active)
        print('activity: ', activity)
        print('inactivity: ', inactivity)

        min_gap = 5 # seconds
        small_gap =  inactivity < min_gap
        print('small_gap: ', small_gap)
    
        new_activity = list()
        count_groups=0
        id_ac = 0
        if start_active == True:
            id_in = 0
        else:
            id_in = 1
        
        print('id_in: ', id_in)
        while id_ac < (len(activity)-1):
            acc_temp = activity[id_ac]
            # true means that the gap is less than min_gap
            while (id_in < len(small_gap)) and (small_gap[id_in]) and (id_ac < (len(activity)-1)):
                id_ac+=1
                acc_temp += activity[id_ac]
                id_in+=1
            new_activity.append(acc_temp)
            count_groups+=1
            id_ac+=1
            id_in+=1

        print('count_groups: ', count_groups)
        print('new_activity: ', new_activity)
        # print('iqual? : ', np.sum(activity), np.sum(new_activity))



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

