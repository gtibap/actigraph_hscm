import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator    
import numpy as np
import datetime
import re
import sys

###########
# global variables
t0=0
t1=3600

# global variables
###########

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
    nights_samples=[]

    cont_nights=1
    if same_day==False:
        for day_now, day_next in zip(dates_list, dates_list[1:]):

            df_night_part0 = df.loc[(df['Date']==day_now) & (df[' Time']>=time0)]
            df_night_part1 = df.loc[(df['Date']==day_next) & (df[' Time']<=time1)]

            df_night = pd.concat([df_night_part0,df_night_part1],  ignore_index=True)
            df_night['night']=cont_nights
            # number of samples per night
            nights_samples.append(df_night['night'].to_numpy().size)
            
            cont_nights+=1

            df_all=pd.concat([df_all, df_night], ignore_index=True)

    else:
        for day_now in dates_list:
            df_night = df.loc[(df['Date']==day_now) & (df[' Time']>=time0) & (df[' Time']<=time1)]

            df_night['night']=cont_nights
            # number of samples per night
            nights_samples.append(df_night['night'].to_numpy().size)
            cont_nights+=1

            df_all=pd.concat([df_all, df_night], ignore_index=True)

    return df_all, nights_samples

###############################



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

def redraw_par(x_values,vec_mag,inc_off):
    global t0,t1
    
    x_v = x_values[t0:t1]
    v_m =  vec_mag[t0:t1]
    i_o =  inc_off[t0:t1]
    print('t0 t1: ', t0/60, t1/60)

    return x_v, v_m, i_o


def update_par(x_values,vec_mag,inc_off):
    global t0,t1
    
    t0=t1
    t1=t1+3600
    if (t1<len(x_values)):
        x_v = x_values[t0:t1]
        v_m =  vec_mag[t0:t1]
        i_o =  inc_off[t0:t1]
    else:
        pass
    print('t0 t1: ', t0/60, t1/60)

    return x_v, v_m, i_o


def on_press(event,fig,ax1,ax2, x_values,vec_mag,inc_off):
    print('press', event.key)
    sys.stdout.flush()
    if event.key == 'x':
        x_v, v_m, i_o = update_par(x_values,vec_mag,inc_off)
        ax1.cla() 
        ax2.cla() 
        ax1.plot(x_v, v_m)
        ax2.plot(x_v, i_o)
    elif event.key == 'r':
        x_v, v_m, i_o = redraw_par(x_values,vec_mag,inc_off)
        ax1.cla() 
        ax2.cla() 
        ax1.plot(x_v, v_m)
        ax2.plot(x_v, i_o)  
        # fig.canvas.draw()
    
    fig.canvas.draw_idle()
###############################

def plot_night_zoom(df_night, inclinometer, filename='title'):
    global t0,t1

    print('plots subplots zoom')
    
    vec_mag = df_night['Vector Magnitude'].to_numpy()
    inc_off = df_night[inclinometer].to_numpy()

    xmin = 0 
    xmax = len(vec_mag)
    
    # presenting xticks in hh:mm format
    # xdelta = 1 # seconds in one hour
    x_values = np.arange(xmin,xmax) / 60 #  in minutes

    x_v = x_values[t0:t1]
    v_m =  vec_mag[t0:t1]
    i_o =  inc_off[t0:t1]


    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

    # ax1=plt.subplot(211)
    fig.canvas.mpl_connect('key_press_event', lambda event: on_press(event, fig,ax1,ax2, x_values,vec_mag,inc_off))

    ax1.margins(0.05)           # Default margin is 0.05, value 0 means fit
    # ax1.plot(x_values, vec_mag)
    ax1.plot(x_v, v_m)

    # ax2=plt.subplot(212, sharex=ax1)
    ax2.margins(x=0, y=0.25)           # Default margin is 0.05, value 0 means fit
    # ax2.plot(x_values, inc_off)
    ax2.plot(x_v, i_o)

    
    plt.show()

    return


def average_frames_1s(df_head, raw_data):
    # averaging of frames per second; example: 2 or 3 FPS (2Hz or 3Hz) will become 1 FPS 1Hz

    data_mean=np.array([],dtype=float).reshape(0, raw_data.shape[1], raw_data.shape[2])
    data_time=[]

    id_sel=0
    # print(len(raw_data))
    while id_sel < len(raw_data):
        sel_hour=df_head['hour'].values[id_sel]
        # print("df['hour'].values[0]: ", sel_hour)
        
        # hour_splitted = datetime.datetime.strptime(sel_hour, "%H:%M:%S.%f")
        # h=hour_splitted.hour
        # m=hour_splitted.minute
        # s=hour_splitted.second

        h,m,s,m_s= np.array(re.split('[:.]', sel_hour), int)

        h_inf =str(h).zfill(2)
        m_inf =str(m).zfill(2)
        s_inf =str(s).zfill(2)


        h_inf =str(h).zfill(2)
        m_inf =str(m).zfill(2)
        s_inf =str(s).zfill(2)
        
        if s+1==60:
            s_sup=str(0).zfill(2)
            if m+1==60:
                m_sup=str(0).zfill(2)
                h_sup=str(h+1).zfill(2)
            else:
                m_sup=str(m+1).zfill(2)
                h_sup=str(h).zfill(2)
        else:
            s_sup=str(s+1).zfill(2)
            m_sup=str(m).zfill(2)
            h_sup=str(h).zfill(2)
        
        # u_sec = str(hour_splitted.microsecond)
        # print(hour+':'+min+':'+sec_inf+'.'+u_sec)

        lim_inf = h_inf+':'+m_inf+':'+s_inf
        lim_sup = h_sup+':'+m_sup+':'+s_sup

        # print('lim_inf, lim_sup: ', lim_inf, lim_sup)

        idx_s = df_head.loc[(df_head['hour']>= lim_inf) & (df_head['hour']<lim_sup)].index.values
        # print(idx_s)

        # id_last = idx_s[-1]
        id_last = np.amax(idx_s)
        id_sel = id_last+1

        # indexes to average matrices of the mattress pressure
        mean_sec = np.mean(raw_data[idx_s[0]:id_sel], axis=0)
        
        data_mean = np.vstack([data_mean, np.expand_dims(mean_sec,axis=0)])

        data_time.append(lim_sup)

        # print(idx_s, raw_data[idx_s[0]:id_sel].shape, mean_sec.shape, data_mean.shape, len(data_time), data_time[-1])

    df_ts = pd.DataFrame(data_time,columns=['time_stamp'])

    return df_ts, data_mean

