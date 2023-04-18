import copy
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
# fig_stems, ax_stems = plt.subplots(nrows=1, ncols=1)
fig_incl_stems, ax_incl_stems = plt.subplots(nrows=1, ncols=1)
# fig_act, ax_act = plt.subplots(nrows=5, ncols=1, sharex=True)
x_sel=0
night_num=0
sample=''

# df_n=pd.DataFrame()
# activity_vector=np.array([])
# df_act_night = pd.DataFrame()
df_nights = pd.DataFrame()
df_active_nights = pd.DataFrame()
df_non_active_nights = pd.DataFrame()
df_incl_all = pd.DataFrame()

flag_nights=True
first_night=0
last_night=0

vec_mag  ='Vector Magnitude'
incl_off ='Inclinometer Off'
incl_sta ='Inclinometer Standing'
incl_sit ='Inclinometer Sitting'
incl_lyi ='Inclinometer Lying'

# global variables
##################

class Actigraphy:
    
    def __init__(self):
        self.header_location=10
        self.time_ini='22:00:00'
        self.time_end='07:59:59'
        self.same_day=False
        
    def openFile(self, path, filename):
        self.path = path
        self.filename = filename
        try:
            self.df1 = pd.read_csv(self.path+self.filename, header=self.header_location, decimal=',')
            print(f'Reading success. Size of the file {self.filename}: {len(self.df1)}')
            self.selectData()
            print(f'selectedData: {len(self.df_all)} and {len(self.nights_samples)}')
        except ValueError:
            print(f'Problem reading the file {self.filename}.')
            self.df1 = np.array([])
    

    def selectData(self):
        
        dates_list = self.df1['Date'].unique().tolist()
        print(dates_list, len(dates_list), type(dates_list))

        names_columns = self.df1.columns.tolist()
        # adding a column number of nights
        names_columns.append('night')

        # empty dataframe initialization
        self.df_all = pd.DataFrame(columns=names_columns)
        self.nights_samples=[]

        cont_nights=1
        if self.same_day==False:
            for day_now, day_next in zip(dates_list, dates_list[1:]):

                df_night_part0 = self.df1.loc[(self.df1['Date']==day_now)  & (self.df1[' Time']>=self.time_ini)]
                df_night_part1 = self.df1.loc[(self.df1['Date']==day_next) & (self.df1[' Time']<=self.time_end)]

                df_night = pd.concat([df_night_part0,df_night_part1],  ignore_index=True)
                df_night['night']=cont_nights
                # number of samples per night
                self.nights_samples.append(df_night['night'].to_numpy().size)
                
                cont_nights+=1

                self.df_all=pd.concat([self.df_all, df_night], ignore_index=True)

        else:
            for day_now in dates_list:
                df_night = df.loc[(df['Date']==day_now) & (df[' Time']>=self.time_ini) & (df[' Time']<=self.time_end)]

                df_night['night']=cont_nights
                # number of samples per night
                self.nights_samples.append(df_night['night'].to_numpy().size)
                cont_nights+=1

                self.df_all=pd.concat([self.df_all, df_night], ignore_index=True)





def activity_sectors_indexes(activity_arrray):
    
    # comparison of active _array (boolean vector) with itself but moved one position. The idea is to identify changes--True to False or False to True.
    
    changes_activity = activity_arrray[:-1] != activity_arrray[1:]

    # if false means that the collected data started with inactivity
    # alternancy between activity and inactivity
    start_active=False
    if activity_arrray[0]==False:
        idx_changes = np.flatnonzero(changes_activity) + 1
    else:
        idx_changes=[0]
        idx_changes = np.concatenate((idx_changes, np.flatnonzero(changes_activity) + 1), axis=None)
        start_active=True

    end_active=False
    if activity_arrray[-1]==False:
        pass
    else:
        idx_end =len(activity_arrray)
        idx_changes = np.concatenate((idx_changes, idx_end), axis=None)
        end_active=True

    indexes_ini = idx_changes[0::2]
    indexes_end = idx_changes[1::2]

    return indexes_ini, indexes_end


def onclick(event):
    global x_sel, df_act_night, ax_act, fig_act, df_active_nights, night_num, df_nights
    # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f, name=%s' %
        #   ('double' if event.dblclick else 'single', event.button,
        #    event.x, event.y, event.xdata, event.ydata, event.name))
    print(event.xdata, event.ydata)
    x_sel = int(event.xdata)

    df_night = df_active_nights.loc[df_active_nights['night']==night_num]
    print(df_night.head())
    arr_ini = df_night['t_ini'].to_numpy()
    arr_end = df_night['t_end'].to_numpy()

    
    # dividing in two because in the arr_ini and arr_end we have only half of the indexes (activity)... the other half are in the non-activity part
    x_min = arr_ini[int(x_sel/2)] -3600 # -3600 because one hour before the event
    x_max = arr_end[int(x_sel/2)] +3600 # +3600 because one hour after the event
   
    # ax_act[0].cla()
    for i in np.arange(5):
        ax_act[i].cla()

    df_actigraphy = df_nights.loc[(df_nights['night']==night_num)]


    ax_act[0].set_title(sample+', night:'+str(night_num))
    ax_act[0].set_ylabel('v.m.')
    ax_act[1].set_ylabel('off')
    ax_act[2].set_ylabel('lyi')
    ax_act[3].set_ylabel('sit')
    ax_act[4].set_ylabel('sta')

    ax_act[0].plot(df_actigraphy[vec_mag].to_numpy())
    # ax_act[0].plot(activity_vector)
    # ax_act[1].plot(df_n[vec_mag])
    ax_act[1].plot(df_actigraphy[incl_off].to_numpy())
    ax_act[2].plot(df_actigraphy[incl_lyi].to_numpy())
    ax_act[3].plot(df_actigraphy[incl_sit].to_numpy())
    ax_act[4].plot(df_actigraphy[incl_sta].to_numpy())
    
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


def on_press(event):
    global flag_nights, night_num

    print('press', event.key)
    sys.stdout.flush()
    if event.key == 'x':
        flag_nights=False
    elif event.key == 'm':
        if night_num < last_night:
            night_num+=1
        else:
            pass
    elif event.key == 'n':
        if night_num > first_night:
            night_num-=1
        else:
            pass
    else:
        pass
        
    if flag_nights==True:
        plot_actigraphy()
        plot_incl_stems()
    else:
        plt.close('all')
        


def inclinometer_sequence(df_incl_night, arr_incl, label):
    
    indexes_ini, indexes_end =activity_sectors_indexes(arr_incl)
    df_incl = pd.DataFrame()
    df_incl['idx_ini'] = indexes_ini
    df_incl['idx_end'] = indexes_end
    df_incl['incl'] = label
    df_incl_night = pd.concat([df_incl_night, df_incl], ignore_index=True)
    
    return df_incl_night

def stems_incl_color(df, ax, color, incl_type):
        
    markerline, stemlines, baseline = ax.stem(df['id'].to_numpy(), df['duration'].to_numpy(), basefmt=" ", linefmt =color, label=incl_type)
    plt.setp(stemlines, 'color', plt.getp(markerline,'color'))
    
    return ax
    
    
def plot_incl_stems():
    
    print('plot_incl_stems: ', night_num)
    
    df_incl_night = df_incl_all.loc[df_incl_all['night']==night_num]
    df_incl_sorted = df_incl_night.sort_values('idx_ini')
    df_incl_sorted['id'] = np.arange(0, len(df_incl_sorted))

    df_off = df_incl_sorted.loc[df_incl_sorted['incl']=='off',['id','duration']]
    df_lyi = df_incl_sorted.loc[df_incl_sorted['incl']=='lyi',['id','duration']]
    df_sit = df_incl_sorted.loc[df_incl_sorted['incl']=='sit',['id','duration']]
    df_sta = df_incl_sorted.loc[df_incl_sorted['incl']=='sta',['id','duration']]
    
    fig_incl_stems.clf()
    ax_incl_stems = fig_incl_stems.add_subplot(1,1,1)
    
    ax_incl_stems.cla()
    
    if len(df_off)>0:
        ax_incl_stems = stems_incl_color(df_off, ax_incl_stems, 'tab:blue', 'off')
    if len(df_lyi)>0:
        ax_incl_stems = stems_incl_color(df_lyi, ax_incl_stems, 'tab:orange', 'lyi')
    if len(df_sit)>0:
        ax_incl_stems = stems_incl_color(df_sit, ax_incl_stems, 'tab:green', 'sit')
    if len(df_sta)>0:        
        ax_incl_stems = stems_incl_color(df_sta, ax_incl_stems, 'tab:red', 'sta')
    ax_incl_stems.legend()
        
    fig_incl_stems.canvas.draw()
    fig_incl_stems.canvas.flush_events()
    
    return
    

def plot_actigraphy():
    
    df_night = df_nights.loc[(df_nights['night']==night_num)]
    
    for i in np.arange(5):
        ax_initial[i].cla()

    ax_initial[0].set_title(sample+', night:'+str(night_num))
    ax_initial[0].set_ylabel('v.m.')
    ax_initial[1].set_ylabel('off')
    ax_initial[2].set_ylabel('lyi')
    ax_initial[3].set_ylabel('sit')
    ax_initial[4].set_ylabel('sta')
    
    ax_initial[0].plot(df_night[vec_mag].to_numpy())
    ax_initial[1].plot(df_night[incl_off].to_numpy())
    ax_initial[2].plot(df_night[incl_lyi].to_numpy())
    ax_initial[3].plot(df_night[incl_sit].to_numpy())
    ax_initial[4].plot(df_night[incl_sta].to_numpy())
    
    fig_initial.canvas.draw()
    fig_initial.canvas.flush_events()
    
    return


####### main function ###########
if __name__== '__main__':
    
    # Get the list of all files and directories
    # path = "../data/all_data_1s/"
    # path_out = "../data/results_motion/"
    path = "../data/projet_officiel/"
    # path_out = "../data/results_motion/"
    # files_list = os.listdir(path)
    
    # print("Files in '", path, "' :")
    # prints all files
    # print(files_list)

    files_list=['A001_chest.csv', 'A001_thigh.csv']
    obj_chest = Actigraphy()
    obj_chest.openFile(path, files_list[0])
    
    
    obj_thigh = Actigraphy()
    obj_thigh.openFile(path, files_list[1])
    
    
    

    # the header in line 10 of the csv file
    

    
    # to run GUI event loop
    cid1 = fig_incl_stems.canvas.mpl_connect('button_press_event', onclick)
    cid2 = fig_incl_stems.canvas.mpl_connect('key_press_event', on_press)
    plt.ion()
    plt.show()

    
    
   
    header_location=10
    for sample in files_list[1:2]:
        print('file: ', sample)
        
        try:
            df1 = pd.read_csv(path+sample, header=header_location, decimal=',')
            # print(df1.info())
        
            # getting all nights data; df_nights is a dataframe of actigraphy from time_start to time_end per night; nights_samples are counts of spending time per night (in seconds)
            df_nights = pd.DataFrame()
            df_nights, nights_samples = getSelectedData(df1, time_start, time_end, same_day)
            
            nights_list = df_nights['night'].unique().tolist()
            
            df_incl_all = pd.DataFrame([],columns=['incl', 'idx_ini', 'idx_end'])

            for night_num in nights_list[:]:

                # actigraphy data night per night
                df_n = df_nights.loc[(df_nights['night']==night_num)]
                
                arr_off = df_n[incl_off].to_numpy()
                arr_lyi = df_n[incl_lyi].to_numpy()
                arr_sit = df_n[incl_sit].to_numpy()
                arr_sta = df_n[incl_sta].to_numpy()
                
                print(f'arr lengths: {arr_off.shape}, {arr_off.size}')
                
               
                
                df_incl_night = pd.DataFrame(columns=['incl', 'idx_ini', 'idx_end'])
                
                df_incl_night=inclinometer_sequence(df_incl_night, arr_off, 'off')
                df_incl_night=inclinometer_sequence(df_incl_night, arr_lyi, 'lyi')
                df_incl_night=inclinometer_sequence(df_incl_night, arr_sit, 'sit')
                df_incl_night=inclinometer_sequence(df_incl_night, arr_sta, 'sta')
                
                df_incl_night['night']=night_num
                
                df_incl_all = pd.concat([df_incl_all, df_incl_night], ignore_index=True)

            df_incl_all['duration']=df_incl_all['idx_end'] - df_incl_all['idx_ini']

            first_night = nights_list[0]
            last_night = nights_list[-1]
            night_num = first_night
            
            
            plot_actigraphy()
            plot_incl_stems()
            
            plt.show(block=True)

            # print(df_active_nights)
            # save on disk df_active_nights
            # df_active_nights.to_csv(path_out+'active_'+sample, index=False)
            # df_non_active_nights.to_csv(path_out+'non_active_'+sample, index=False)
            
        except ValueError:
            print('Problem reading the file', sample, '... it is skipped.')
        
