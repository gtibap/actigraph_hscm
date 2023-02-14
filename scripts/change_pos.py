import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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
            df_night_part0 = df.loc[(df['Date']==day_now) & (df[' Time']>=time0), ['Date',' Time','Inclinometer Off','Inclinometer Standing','Inclinometer Sitting','Inclinometer Lying']]
            df_night_part1 = df.loc[(df['Date']==day_next) & (df[' Time']<=time1), ['Date',' Time','Inclinometer Off','Inclinometer Standing','Inclinometer Sitting','Inclinometer Lying']]

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
            df_night = df.loc[(df['Date']==day_now) & (df[' Time']>=time0) & (df[' Time']<=time1), ['Date',' Time','Inclinometer Off','Inclinometer Standing','Inclinometer Sitting','Inclinometer Lying']]
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


def plot_pos(df1):
    nights_list = df1['night'].unique().tolist()
    # print('nights: ', nights_list)
    fig, axes = plt.subplots(nrows=4, ncols=1)
    # fig.suptitle('Vector Magnitude', fontsize=12)
    # fig.subplots_adjust(wspace=0, hspace=10)
    # fig, axes = plt.subplots(subplot_kw={'ylim': (0,150)})

    # ax1 = axes[0]
    # ax2 = axes[1]
  

    time_0='10:00:00'
    time_1='11:00:00'

    for night_num in nights_list[1:2]:
        
        df1_off = df1.loc[(df1['night']==night_num), [' Time','Inclinometer Off']]
        df1_sta = df1.loc[(df1['night']==night_num), [' Time','Inclinometer Standing']]
        df1_sit = df1.loc[(df1['night']==night_num), [' Time','Inclinometer Sitting']]
        df1_lyi = df1.loc[(df1['night']==night_num), [' Time','Inclinometer Lying']]
        
        # df1_off = df1.loc[(df1['night']==night_num) & (df1[' Time']>=time_0) & (df1[' Time']<=time_1), [' Time','Inclinometer Off']]
        # df1_sta = df1.loc[(df1['night']==night_num) & (df1[' Time']>=time_0) & (df1[' Time']<=time_1), [' Time','Inclinometer Standing']]
        # df1_sit = df1.loc[(df1['night']==night_num) & (df1[' Time']>=time_0) & (df1[' Time']<=time_1), [' Time','Inclinometer Sitting']]
        # df1_lyi = df1.loc[(df1['night']==night_num) & (df1[' Time']>=time_0) & (df1[' Time']<=time_1), [' Time','Inclinometer Lying']]
        
        print(df1_off.columns)
        print(df1_off.head)
        print(df1_off.info())

        print('length column Time:', len(df1_off[' Time']))
        xmin = 0 
        xmax = len(df1_off[' Time'])

        # presenting xticks in hh:mm format
        xdelta = 3600 # seconds in one hour
        xticks = np.arange(xmin,xmax,xdelta)
        hours = np.floor(xticks/3600).astype(int)
        mins  = np.floor(np.remainder(xticks,3600)/60).astype(int)
        xlabels = [str(i)+':'+str(j) for i, j in zip(hours, mins)]
        xlabels_2 = xlabels.copy()
        xlabels_2[0] = xlabels[0]+'\n22h00'
        xlabels_2[-1] = xlabels[-1]+'\n10h00'
        # print(hours)
        # print(mins)
        # print(xlabels)
        # xlabels = np.around(xrange/3600,decimals=2)
        ymin = 0
        ymax = 210
        ylabel = 'counts (1s epoch)'
        xlabel = 'time (hh:mm)'
        # bx1=df1_night.plot(x=' Time', y='Vector Magnitude', ax=ax1, alpha=1.0, xlabel='', xticks=(np.arange(0, len(df1_night[' Time'])+1, 3600)))
        bx1=df1_off.plot(x=' Time', y='Inclinometer Off', ax= axes[0], alpha=1.0)
        # bx1.set_xlim([xmin, xmax])
        # bx1.set_ylim([ymin, ymax])
        bx1.set_xticks(xticks)
        bx1.set_xticklabels(xlabels)
        # bx1.set_ylabel(ylabel)
        bx1.set_xlabel('')
        bx1.set_title("Inclinometer")
        bx1.legend(["Inclinometer Off"])
        # bx1.set_xticklabels(np.arange(0, len(df1_night[' Time'])+1, 3600))
        
        # print([xlabels[0]+'\n22h00', xlabels[1:-1], xlabels[-1]+'\n10h00'])
        # bx1.xlabel('')
        bx2=df1_sta.plot(x=' Time', y='Inclinometer Standing', ax= axes[1],  alpha=1.0)
        # bx2.set_xlim([xmin, xmax])
        # bx2.set_ylim([ymin, ymax])
        bx2.set_xticks(xticks)
        bx2.set_xticklabels(xlabels)
        # bx2.set_ylabel(ylabel)
        bx2.set_xlabel(xlabel)
        bx2.legend(["Inclinometer Standing"])
        # bx2.set_title("Vector Magnitude : Thigh")

        bx3=df1_sit.plot(x=' Time', y='Inclinometer Sitting', ax= axes[2],  alpha=1.0)
        bx3.legend(["Inclinometer Sitting"])
        bx3.set_xticks(xticks)
        bx3.set_xticklabels(xlabels)

        bx4=df1_lyi.plot(x=' Time', y='Inclinometer Lying', ax= axes[3],  alpha=1.0)
        bx4.legend(["Inclinometer Lying"])
        bx4.set_xticks(xticks)
        bx4.set_xticklabels(xlabels_2)

        # bx2.set_xticks(np.arange(0, 12, step=0.2), np.arange(0, 12, step=0.2))
        # xticks(np.arange(0, 1, step=0.2))
        # bx2.xlabel('Time (h)')
        # bx1=df1_night.plot(x=' Time', y='Vector Magnitude', alpha=0.5, ax=axes, label='chest')
        # bx1.legend(["chest"])
        # bx2=df2_night.plot(x=' Time', y='Vector Magnitude',  alpha=0.5, ax=axes, label='thigh')
        # bx2.legend(["thigh"])
        # df_night.plot(x=' Time', y='Vector Magnitude', , ax=axes[row,col])
    return

def active_periods(mag_col):
    # nights_list = df['night'].unique().tolist()
    min_value = 3 # min intensity value
    # for night_num in nights_list[:1]:
    # mag_col = df.loc[(df['night']==night_num), ['Vector Magnitude']]

    # mag_col['active'] = mag_col['Inclinometer Off'] > min_value
    # boolean array where True means activity higher than min_value
    active_arrray = mag_col['Inclinometer Off'].to_numpy()
    print('Inclinometer Off: ', active_arrray)
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
    # sum of 1 to idx_changes because the changes_array vector is one element smaller than active_arrray (original data)
    return idx_changes+1, duration_active, duration_inactive, start_active

def linear_function(duration, weight):
    elements_list=[]
    for each_period in duration:
        # starting in 1 is better than in 0
        values_t = np.arange(1,each_period+1) * weight
        elements_list.append(values_t)
    return elements_list


def pressure(duration_active, duration_inactive, start_active):
    w_act =  1 # coefficient linear fuction y=(w_act)*t
    w_ina = -10 # coefficient linear fuction y=(w_ina)*t
    initial_value = 0 # initial pressure value
    values_active = linear_function(duration_active, w_act)
    values_inactive = linear_function(duration_inactive, w_ina)
    
    # vector initialization
    full_vector = np.array([initial_value])
    
    if start_active == True:
        for va, vi in zip(values_active, values_inactive):
            # first data of activity
            values = va+full_vector[-1]
            values[values<0]=0
            full_vector=np.concatenate((full_vector,values),axis=None)
            # then data of inactivity
            values=vi+full_vector[-1]
            values[values<0]=0
            full_vector=np.concatenate((full_vector,values),axis=None)
    else:
        for va, vi in zip(values_active, values_inactive):
            # first data of inactivity
            values=vi+full_vector[-1]
            values[values<0]=0
            full_vector=np.concatenate((full_vector,values),axis=None)
            # then data of activity
            values = va+full_vector[-1]
            values[values<0]=0
            full_vector=np.concatenate((full_vector,values),axis=None)
            
    return full_vector


def indices_postures(df1):
    nights_list = df1['night'].unique().tolist()

    for night_num in nights_list[1:2]:
        df1_off = df1.loc[(df1['night']==night_num), [' Time','Inclinometer Off']]
        indices, duration_active, duration_inactive, start_active = active_periods(df1_off)
        # print('indices: ', indices)
        # print('start active: ', start_active)
        # print('duration_active: ', duration_active)
        # print('duration_inactive: ', duration_inactive)

        data_pressure = pressure(duration_active, duration_inactive, start_active)

        df1_off.plot()
        plt.figure()
        plt.plot(data_pressure)
        plt.show()

        # print(df1_off.columns)
        # print(df1_off.head)
        # print(df1_off.info())



    return

####### main function ###########
if __name__== '__main__':

    # print('hello')
    # read file actigraph
    # the header in line 10 of the csv file
    header_location=10
    # df1 = pd.read_csv("../data/p00/Turner Chest1secDataTable.csv", header=header_location, decimal=',', usecols=['Date',' Time',' Axis1','Axis2','Axis3','Vector Magnitude'])
    df1 = pd.read_csv("../data/p00/Turner Chest1secDataTable.csv", header=header_location, decimal=',', usecols=['Date',' Time','Inclinometer Off','Inclinometer Standing','Inclinometer Sitting','Inclinometer Lying'])
    # df1 = pd.read_csv("../data/p00/Turner Chest1secDataTable.csv", header=header_location, decimal=',')
    # print(df.empty)
    # print(df.shape)
    print(df1.columns)
    print(df1.head)
    print(df1.info())
    
    # Data visualization

    # df1.plot['Inclinometer Off']

    # time_start='22:00:00'
    # time_end='10:00:00'
    # same_day=False

    time_start='22:00:00'
    time_end='10:00:00'
    same_day=False


    df_chest = getSelectedData(df1, time_start, time_end, same_day)
    # df_thigh = getSelectedData(df2, time_start, time_end, same_day)

    # print(df_chest.info())

    # plot_pos(df_chest)
    # plt.show()

    indices_postures(df_chest)
    
