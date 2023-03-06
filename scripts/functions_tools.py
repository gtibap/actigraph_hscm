import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator    
import numpy as np

# Selecting data from time_0 to time_1 from all days. It could be from the same day or two consecutive days. For example, from 22h (current day) to 08h (next day), hence 'same_day=False'; from 17h to 19h same day ('same_day=True')
# the function returns a DataFrame that includes the 'night' column (int from 1 - N), which allows to identify each selected period
def getSelectedData(df, time0, time1, same_day):

    dates_list = df['Date'].unique().tolist()
    print(dates_list, len(dates_list), type(dates_list))

    names_columns = df.columns.tolist()
    # adding a column number of nights
    names_columns.append('night')

    # empty dataframe initialization
    df_all = pd.DataFrame(columns=names_columns)

    cont_nights=1
    if same_day==False:
        for day_now, day_next in zip(dates_list, dates_list[1:]):

            df_night_part0 = df.loc[(df['Date']==day_now) & (df[' Time']>=time0)]
            df_night_part1 = df.loc[(df['Date']==day_next) & (df[' Time']<=time1)]

            df_night = pd.concat([df_night_part0,df_night_part1],  ignore_index=True)
            df_night['night']=cont_nights
            cont_nights+=1

            df_all=pd.concat([df_all, df_night], ignore_index=True)

    else:
        for day_now in dates_list:
            df_night = df.loc[(df['Date']==day_now) & (df[' Time']>=time0) & (df[' Time']<=time1)]

            df_night['night']=cont_nights
            cont_nights+=1

            df_all=pd.concat([df_all, df_night], ignore_index=True)

    return df_all


###############################

def plot_night(df_night, inclinometer, filename='title'):
    
    # fig, axes = plt.subplots(nrows=2, ncols=1)
    fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True)
    # ax1 = axes[0]
    axes[0].xaxis.set_major_locator(MaxNLocator(min_n_ticks=15))  
    axes[1].xaxis.set_major_locator(MaxNLocator(min_n_ticks=15))  

    # for night_num in nights_list[:1]:
    # df_night = df.loc[(df['night']==night_num) , [' Time','Vector Magnitude']]
    # df_night = df.loc[(df['night']==night_num)]
    fvalue=df_night[' Time'].values[0]
    lvalue=df_night[' Time'].values[-1]

    xmin = 0 
    xmax = len(df_night[' Time'])

    # presenting xticks in hh:mm format
    xdelta = 1 # seconds in one hour
    xticks = np.arange(xmin,xmax,xdelta)
    hours = np.floor(xticks/3600).astype(int)
    mins  = np.floor(np.remainder(xticks,3600)/60).astype(int)
    xticks_labels = [str(i)+':'+str(j) for i, j in zip(hours, mins)]
    
    
    ymin = 0
    ymax = 150
    ylabel = 'counts (1s epoch)'
    ylabel_2 = 'time (s)'
    xlabel = 'time (hh:mm)'
    # xlabels_2 = np.copy(xlabels)
    xticks_labels[0] = xticks_labels[0]+'\n'+fvalue
    xticks_labels[-1] = xticks_labels[-1]+'\n'+lvalue
    
    bx1=df_night.plot(x=' Time', y='Vector Magnitude', ax=axes[0], alpha=1.0)
    # bx1.set_xlim([xmin, xmax])
    # bx1.set_ylim([ymin, ymax])
    # bx1.set_xticks(xticks)
    # bx1.set_xticklabels(xticks_labels)
    bx1.set_ylabel(ylabel)
    bx1.set_xlabel(xlabel)
    bx1.set_title(filename)
    # bx1.set_title("Vector Magnitude")
    # bx1.legend(["chest"])

    bx2=df_night.plot(x=' Time', y=inclinometer, ax=axes[1], alpha=1.0)
    # bx2.set_xticks(xticks)
    # bx2.set_xticklabels(xticks_labels)
    bx2.set_ylabel(ylabel_2)
    bx2.set_xlabel(xlabel)
    # bx2.set_title(filename)
    
    plt.show()

    return

###############################

def plot_night_zoom(df_night, inclinometer, filename='title'):

    print('plots subplots zoom')
    
    vec_mag = df_night['Vector Magnitude'].to_numpy()
    inc_off = df_night[inclinometer].to_numpy()

    xmin = 0 
    xmax = len(vec_mag)
    
    # presenting xticks in hh:mm format
    # xdelta = 1 # seconds in one hour
    x_values = np.arange(xmin,xmax) / 60 #  in minutes

    ax1=plt.subplot(211)
    ax1.margins(0.05)           # Default margin is 0.05, value 0 means fit
    ax1.plot(x_values, vec_mag)

    ax2=plt.subplot(212, sharex=ax1)
    ax2.margins(x=0, y=0.25)           # Default margin is 0.05, value 0 means fit
    ax2.plot(x_values, inc_off)

    
    plt.show()

    return

