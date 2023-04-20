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


class Actigraphy:

    # the header in line 10 of the csv actigraphy files
    header_location=10
    time_ini='22:00:00'
    time_end='07:59:59'
    same_day=False
    min_gap=60 # seconds
    min_value=3 # Vector Magnitude should be greater than this value to be considered as a valid motor activity
    vec_mag  ='Vector Magnitude'
    incl_off ='Inclinometer Off'
    incl_sta ='Inclinometer Standing'
    incl_sit ='Inclinometer Sitting'
    incl_lyi ='Inclinometer Lying'
            
    def __init__(self):
        
        self.first_night = 0
        self.last_night = 0
        self.night_num = 0
        self.nights_list = []
        self.df_actigraphy_nights = pd.DataFrame()
        self.samples_per_night = []
        self.df_vectMag = pd.DataFrame()
        # self.duration_active = []
        # self.duration_inactive = []
        # self.start_active = False
        # self.end_active = False

    def openFile(self, path, filename):
        
        self.path = path
        self.filename = filename

        self.df1 = pd.read_csv(self.path+self.filename, header=self.header_location, decimal=',')
        # print(f'Reading success. Size of the file {self.filename}: {len(self.df1)}')
        # print(f'Selecting data per night; from {self.time_ini} to {self.time_end} (next day)')
        self.df_actigraphy_nights, self.samples_per_night = self.nightsData()
        
        self.nights_list = self.df_actigraphy_nights['night'].unique().tolist()
        self.first_night = self.nights_list[0]
        self.last_night  = self.nights_list[-1]
        self.night_num   = self.first_night
        
        # print(f'Selected data: {len(self.df_actigraphy_nights)}, {len(self.samples_per_night)} nights')
        self.df_vectMag = self.activityVectorMag()
        # print(f'Selected data: {len(self.df_actigraphy_nights)}, {len(self.samples_per_night)} nights')
        
        # self.df_inclinometers = self.readInclinometers()
        # print(self.df_inclinometers)
    

    def nightsData(self):
        
        dates_list = self.df1['Date'].unique().tolist()
        # print(dates_list, len(dates_list), type(dates_list))

        names_columns = self.df1.columns.tolist()
        # adding a column number of nights
        names_columns.append('night')

        # empty dataframe initialization
        df_all = pd.DataFrame(columns=names_columns)
        nights_samples=[]

        cont_nights=1
        if self.same_day==False:
            for day_now, day_next in zip(dates_list, dates_list[1:]):

                df_night_part0 = self.df1.loc[(self.df1['Date']==day_now)  & (self.df1[' Time']>=self.time_ini)]
                df_night_part1 = self.df1.loc[(self.df1['Date']==day_next) & (self.df1[' Time']<=self.time_end)]

                df_night = pd.concat([df_night_part0,df_night_part1],  ignore_index=True)
                df_night['night']=cont_nights
                df_all=pd.concat([df_all, df_night], ignore_index=True)
                # number of samples per night
                nights_samples.append(df_night['night'].to_numpy().size)
                cont_nights+=1
        else:
            for day_now in dates_list:
                df_night = df.loc[(df['Date']==day_now) & (df[' Time']>=self.time_ini) & (df[' Time']<=self.time_end)]
                df_night['night']=cont_nights
                df_all=pd.concat([df_all, df_night], ignore_index=True)
                # number of samples per night
                nights_samples.append(df_night['night'].to_numpy().size)
                cont_nights+=1
                
        return df_all, nights_samples
    

    def activityVectorMag(self):
        
        nights_list = self.df_actigraphy_nights['night'].unique().tolist()
        df_vectMag_all = pd.DataFrame([],columns=['night', 'active', 'idx_ini', 'idx_end'])

        for night_num in nights_list:

            # actigraphy data night per night
            df_n = self.df_actigraphy_nights.loc[(self.df_actigraphy_nights['night']==night_num)]
        
            # boolean array where True means activity higher than min_value
            arr_mag = df_n[self.vec_mag].to_numpy()
            activity_array = arr_mag > self.min_value
            # boolean array where True means activity higher than min_value
            # activity_vector = df_n['activity'].to_numpy()

            duration_active, duration_inactive, start_active, end_active = self.activity_sectors(activity_array)

            activity_array = self.redefinition_activity_arr(duration_active, duration_inactive, start_active, end_active, self.min_gap)
            
            idx_ini, idx_end = self.activity_sectors_indexes(activity_array)

            df_act_night = pd.DataFrame()
            df_act_night['idx_ini']=idx_ini
            df_act_night['idx_end']=idx_end
            df_act_night['night']=night_num
            df_act_night['active']=1

            df_vectMag_all=pd.concat([df_vectMag_all, df_act_night], ignore_index=True)

            non_activity_array = np.logical_not(activity_array)
            idx_ini, idx_end = self.activity_sectors_indexes(non_activity_array)

            df_non_act_night = pd.DataFrame()
            df_non_act_night['idx_ini']=idx_ini
            df_non_act_night['idx_end']=idx_end
            df_non_act_night['night']=night_num
            df_non_act_night['active']=0

            df_vectMag_all=pd.concat([df_vectMag_all, df_non_act_night], ignore_index=True)

        df_vectMag_all['duration'] = df_vectMag_all['idx_end'] - df_vectMag_all['idx_ini']
            
        return df_vectMag_all


    def activity_sectors(self, activity_arr):
    
        # comparison of active _array (boolean vector) with itself but moved one position. The idea is to identify changes--True to False or False to True.
        changes_activity = activity_arr[:-1] != activity_arr[1:]
        # changes_activity is a boolean vector; True means a change; False means no change
        # indices or location of Trues (changes) values; +1 because I want the index when the data already changed from left to right
        # first index is location 0 in the array
        idx_changes=[0]
        idx_changes = np.concatenate((idx_changes, np.flatnonzero(changes_activity) + 1), axis=None)
        # last index is the size of the original array
        idx_end =len(activity_arr)
        idx_changes = np.concatenate((idx_changes, idx_end), axis=None)
        # distance between two consecutive changes (time in our case)
        intervals = idx_changes[1:]-idx_changes[:-1]
        # if false means that the collected data started with inactivity
        # alternancy between activity and inactivity
        start_active=False
        if activity_arr[0]==False:
            duration_inactive = intervals[0::2]
            duration_active =   intervals[1::2]
        else:
            duration_active =   intervals[0::2]
            duration_inactive = intervals[1::2]
            start_active=True

        end_active=False
        if activity_arr[-1]==False:
            pass
        else:
            end_active=True

        return duration_active, duration_inactive, start_active, end_active


    def redefinition_activity_arr(self, duration_active, duration_inactive, start_active, end_active, min_gap):

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

        return new_activity_array


    
        
    def readInclinometers(self):
        
        df_incl_all = pd.DataFrame([],columns=['incl', 'idx_ini', 'idx_end'])

        for night_num in self.nights_list:

            # actigraphy data night per night
            df_n = self.df_actigraphy_nights.loc[(self.df_actigraphy_nights['night']==night_num)]
            
            arr_off = df_n[self.incl_off].to_numpy()
            arr_lyi = df_n[self.incl_lyi].to_numpy()
            arr_sit = df_n[self.incl_sit].to_numpy()
            arr_sta = df_n[self.incl_sta].to_numpy()
            
            df_incl_night = pd.DataFrame(columns=['incl', 'idx_ini', 'idx_end'])
            
            df_incl_night=self.inclinometer_sequence(df_incl_night, arr_off, 'off')
            df_incl_night=self.inclinometer_sequence(df_incl_night, arr_lyi, 'lyi')
            df_incl_night=self.inclinometer_sequence(df_incl_night, arr_sit, 'sit')
            df_incl_night=self.inclinometer_sequence(df_incl_night, arr_sta, 'sta')
            
            df_incl_night['night']=night_num
            
            df_incl_all = pd.concat([df_incl_all, df_incl_night], ignore_index=True)

        df_incl_all['duration']=df_incl_all['idx_end'] - df_incl_all['idx_ini']
        
        # self.first_night = nights_list[0]
        # self.last_night = nights_list[-1]
        # self.night_num = self.first_night

        return df_incl_all
        
        
    def inclinometer_sequence(self, df_incl_night, arr_incl, label):
    
        indexes_ini, indexes_end =self.activity_sectors_indexes(arr_incl)
        df_incl = pd.DataFrame()
        df_incl['idx_ini'] = indexes_ini
        df_incl['idx_end'] = indexes_end
        df_incl['incl'] = label
        df_incl_night = pd.concat([df_incl_night, df_incl], ignore_index=True)
        
        return df_incl_night


    def activity_sectors_indexes(self, activity_array):
    
        # comparison of active _array (boolean vector) with itself but moved one position. The idea is to identify changes--True to False or False to True.
        
        changes_activity = activity_array[:-1] != activity_array[1:]

        # if false means that the collected data started with inactivity
        # alternancy between activity and inactivity
        start_active=False
        if activity_array[0]==False:
            idx_changes = np.flatnonzero(changes_activity) + 1
        else:
            idx_changes=[0]
            idx_changes = np.concatenate((idx_changes, np.flatnonzero(changes_activity) + 1), axis=None)
            start_active=True

        end_active=False
        if activity_array[-1]==False:
            pass
        else:
            idx_end =len(activity_array)
            idx_changes = np.concatenate((idx_changes, idx_end), axis=None)
            end_active=True

        indexes_ini = idx_changes[0::2]
        indexes_end = idx_changes[1::2]

        return indexes_ini, indexes_end
        
    
    def plot_actigraphy(self):
        
        self.fig_initial, self.ax_initial = plt.subplots(nrows=5, ncols=1, sharex=True)
        
        self.replot_actigraphy()
        
        return self.fig_initial, self.ax_initial
        
    def replot_actigraphy(self):
        
        df_night = self.df_actigraphy_nights.loc[(self.df_actigraphy_nights['night']==self.night_num)]
        
        for i in np.arange(5):
            self.ax_initial[i].cla()

        self.ax_initial[0].set_title(self.filename+', night:'+str(self.night_num))
        self.ax_initial[0].set_ylabel('v.m.')
        self.ax_initial[1].set_ylabel('off')
        self.ax_initial[2].set_ylabel('lyi')
        self.ax_initial[3].set_ylabel('sit')
        self.ax_initial[4].set_ylabel('sta')
        
        self.ax_initial[0].plot(df_night[self.vec_mag].to_numpy())
        self.ax_initial[1].plot(df_night[self.incl_off].to_numpy())
        self.ax_initial[2].plot(df_night[self.incl_lyi].to_numpy())
        self.ax_initial[3].plot(df_night[self.incl_sit].to_numpy())
        self.ax_initial[4].plot(df_night[self.incl_sta].to_numpy())
        
        self.fig_initial.canvas.draw()
        self.fig_initial.canvas.flush_events()
        
    def getInclinometersData(self):
        return self.df_inclinometers
        
    def getVectMagActivity(self):
        return self.df_vectMag
        
    def getActigraphyData(self):
        return self.df_actigraphy_nights
        

##################
# global variables
obj_chest = Actigraphy()
obj_thigh = Actigraphy()
fig_incl_stems = []
ax_incl_stems = []
fig_vectMag = []
ax_vectMag = []
vec_mag  ='Vector Magnitude'
incl_off ='Inclinometer Off'
incl_sta ='Inclinometer Standing'
incl_sit ='Inclinometer Sitting'
incl_lyi ='Inclinometer Lying'


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

def redraw_plots():
    obj_chest.replot_actigraphy()
    obj_thigh.replot_actigraphy()
    plot_vectMag()
    # fig_incl_stems.clf()
    # plot_incl_stems(obj_chest.getInclinometersData(), obj_chest.night_num, 1, obj_chest.filename)
    # plot_incl_stems(obj_thigh.getInclinometersData(), obj_thigh.night_num, 2, obj_thigh.filename)
    return

def on_press(event):
    
    print('press', event.key)
    sys.stdout.flush()
    
    if event.key == 'x':
        plt.close('all')
    elif event.key == 'm':
        if (obj_chest.night_num < obj_chest.last_night) and (obj_thigh.night_num < obj_thigh.last_night):
            obj_chest.night_num+=1
            obj_thigh.night_num+=1
            redraw_plots()
        else:
            pass
    elif event.key == 'n':
        if (obj_chest.night_num > obj_chest.first_night) and (obj_thigh.night_num > obj_thigh.first_night):
            obj_chest.night_num-=1
            obj_thigh.night_num-=1
            redraw_plots()
        else:
            pass
    else:
        pass
        


def stems_incl_color(df, ax, color, incl_type):
        
    markerline, stemlines, baseline = ax.stem(df['id'].to_numpy(), df['duration'].to_numpy(), basefmt=" ", linefmt =color, label=incl_type)
    plt.setp(stemlines, 'color', plt.getp(markerline,'color'))
    
    return ax
    
    
def plot_incl_stems(df_incl_all, night_num, location, title):
    
    print('plot_incl_stems: ', night_num)
    
    df_incl_night = df_incl_all.loc[df_incl_all['night']==night_num]
    df_incl_sorted = df_incl_night.sort_values('idx_ini')
    df_incl_sorted['id'] = np.arange(0, len(df_incl_sorted))

    df_off = df_incl_sorted.loc[df_incl_sorted['incl']=='off',['id','duration']]
    df_lyi = df_incl_sorted.loc[df_incl_sorted['incl']=='lyi',['id','duration']]
    df_sit = df_incl_sorted.loc[df_incl_sorted['incl']=='sit',['id','duration']]
    df_sta = df_incl_sorted.loc[df_incl_sorted['incl']=='sta',['id','duration']]
    
    ax_incl_stems = fig_incl_stems.add_subplot(2,1,location)
    ax_incl_stems.cla()
    ax_incl_stems.set_title(title+' night:'+str(night_num))
    ax_incl_stems.set_ylabel('time (s)')
    ax_incl_stems.set_xlabel('samples')
    
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


def plot_vectMag():
    
    df_nights_chest = obj_chest.getActigraphyData()
    df_nights_thigh = obj_thigh.getActigraphyData()
    
    df_vm_chest_all = obj_chest.getVectMagActivity()
    df_vm_thigh_all = obj_thigh.getVectMagActivity()
    
    for i in np.arange(4):
        ax_vectMag[i].cla()
    
    night_num = obj_chest.night_num
    plot_vectMag_single(df_nights_chest, df_vm_chest_all, night_num, 0, 'chest')
    
    night_num = obj_thigh.night_num
    plot_vectMag_single(df_nights_thigh, df_vm_thigh_all, night_num, 1, 'thigh')

    ax_vectMag[0].set_title('Vector Magnitude, night:'+str(night_num))
    # self.ax_initial[0].set_ylabel('v.m.')
    # self.ax_initial[1].set_ylabel('off')
    # self.ax_initial[2].set_ylabel('lyi')
    # self.ax_initial[3].set_ylabel('sit')
    # self.ax_initial[4].set_ylabel('sta')
    ax_vectMag[0].legend()
    ax_vectMag[1].legend()
    
    fig_vectMag.canvas.draw()
    fig_vectMag.canvas.flush_events()
    
    return

def plot_vectMag_single(df_nights, df_vm_all, night_num, id_ax, label):
    
    # print('plot vector magnitude: ', obj_single.night_num)
    df_n = df_nights.loc[df_nights['night']==night_num]
    df_vm = df_vm_all.loc[(df_vm_all['night']==night_num) & (df_vm_all['active']==1)]
    
    indexes_ini = df_vm['idx_ini'].to_numpy()
    indexes_end = df_vm['idx_end'].to_numpy()
    
    for id_ini, id_end in zip(indexes_ini,indexes_end):
        ax_vectMag[id_ax].axvspan(id_ini, id_end, facecolor='b', alpha=0.5)
    
    ax_vectMag[id_ax].plot(df_n[vec_mag].to_numpy(), label=label)
    # ax_vectMag.legend()
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
    
    prefix = 'A004'
    files_list=[prefix+'_chest.csv', prefix+'_thigh.csv']
    
    flag_chest=False
    flag_thigh=False
    
    try:
        obj_chest.openFile(path, files_list[0])
        flag_chest=True
    except ValueError:
            print(f'Problem reading the file {self.filename}.')
            flag_chest=False
            
    try:
        obj_thigh.openFile(path, files_list[1])
        flag_thigh=True
    except ValueError:
            print(f'Problem reading the file {self.filename}.')
            flag_thigh=False
        
    if flag_chest and flag_thigh:
        
         # to run GUI event loop
        fig_actigraphy_chest, ax_actigraphy_chest = obj_chest.plot_actigraphy()
        fig_actigraphy_thigh, ax_actigraphy_thigh = obj_thigh.plot_actigraphy()
        
        fig_vectMag, ax_vectMag = plt.subplots(nrows=4, ncols=1, sharex=True)
        plot_vectMag()
        
        # fig_incl_stems, ax_incl_stems = plt.subplots(nrows=2, ncols=1)
        
        # fig_incl_stems.clf()
        # plot_incl_stems(obj_chest.getInclinometersData(), obj_chest.night_num, 1, obj_chest.filename)
        # plot_incl_stems(obj_thigh.getInclinometersData(), obj_thigh.night_num, 2, obj_thigh.filename)

        # cid1 = fig_act.canvas.mpl_connect('button_press_event', onclick)
        cid_chest  = fig_actigraphy_chest.canvas.mpl_connect('key_press_event', on_press)
        cid_thigh  = fig_actigraphy_thigh.canvas.mpl_connect('key_press_event', on_press)
        cid_vecMag = fig_vectMag.canvas.mpl_connect('key_press_event', on_press)
        # cid_stems = fig_incl_stems.canvas.mpl_connect('key_press_event', on_press)
                
        # cid1 = fig_incl_stems.canvas.mpl_connect('button_press_event', onclick)
        # cid2 = fig_incl_stems.canvas.mpl_connect('key_press_event', on_press)
        plt.ion()
        plt.show()
        
        
            
        plt.show(block=True)
    
    else:
        print('Incompleted data.')
        
