import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import datetime
import re
import sys


##########
# global variables
figure_1, ax_1 = plt.subplots(nrows=2, ncols=1, sharex=True)
figure_2, ax_2 = plt.subplots(figsize=(6, 8))
figure_3, ax_3 = plt.subplots(nrows=5, ncols=1, sharex=True)
figure_4, ax_4 = plt.subplots(nrows=5, ncols=1, sharex=True)

drawing = False
x0=0
y0=0
x1=0
y1=0
y_max=250
id_frame=0
id_frame_ini = 0
id_frame_end = 0
id_act=0

flag_start=True
pressed_key='nan'
incl_off ='Inclinometer Off'
incl_sta ='Inclinometer Standing'
incl_sit ='Inclinometer Sitting'
incl_lyi ='Inclinometer Lying'
vec_mag  ='Vector Magnitude'
# global variables
##########


# def resize_img(img):
#     # print('Original Dimensions : ',img.shape)
 
#     scale = 10 # percent of original size
#     width = int(img.shape[1] * scale)
#     height = int(img.shape[0] * scale)
#     dim = (width, height)
    
#     # resize image
#     resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    
#     # print('Resized Dimensions : ',resized.shape)
#     return resized


# def average_data(df_head, raw_data):
#     # averaging of frames per second; 2 or 3 FPS (2Hz or 3Hz) will become 1 FPS 1Hz

#     data_mean=np.array([],dtype=float).reshape(0, raw_data.shape[1], raw_data.shape[2])
#     data_time=[]

#     id_sel=0
#     # print(len(raw_data))
#     while id_sel < len(raw_data):
#         sel_hour=df_head['hour'].values[id_sel]
#         # print("df['hour'].values[0]: ", sel_hour)
        
#         # hour_splitted = datetime.datetime.strptime(sel_hour, "%H:%M:%S.%f")
#         # h=hour_splitted.hour
#         # m=hour_splitted.minute
#         # s=hour_splitted.second

#         h,m,s,m_s=re.split('[:]', sel_hour)

#         h_inf =str(h).zfill(2)
#         m_inf =str(m).zfill(2)
#         s_inf =str(s).zfill(2)
        
#         if s+1==60:
#             s_sup=str(0).zfill(2)
#             if m+1==60:
#                 m_sup=str(0).zfill(2)
#                 h_sup=str(h+1).zfill(2)
#             else:
#                 m_sup=str(m+1).zfill(2)
#                 h_sup=str(h).zfill(2)
#         else:
#             s_sup=str(s+1).zfill(2)
#             m_sup=str(m).zfill(2)
#             h_sup=str(h).zfill(2)
        
#         # u_sec = str(hour_splitted.microsecond)
#         # print(hour+':'+min+':'+sec_inf+'.'+u_sec)

#         lim_inf = h_inf+':'+m_inf+':'+s_inf
#         lim_sup = h_sup+':'+m_sup+':'+s_sup

#         # print('lim_inf, lim_sup: ', lim_inf, lim_sup)

#         idx_s = df_head.loc[(df_head['hour']>= lim_inf) & (df_head['hour']<lim_sup)].index.values
#         # print(idx_s)

#         # id_last = idx_s[-1]
#         id_last = np.amax(idx_s)
#         id_sel = id_last+1

#         # indexes to average matrices of the mattress pressure
#         mean_sec = np.mean(raw_data[idx_s[0]:id_sel], axis=0)
        
#         data_mean = np.vstack([data_mean, np.expand_dims(mean_sec,axis=0)])

#         data_time.append(lim_sup)

#         # print(idx_s, raw_data[idx_s[0]:id_sel].shape, mean_sec.shape, data_mean.shape, len(data_time), data_time[-1])

#     df_ts = pd.DataFrame(data_time,columns=['time_stamp'])

#     return df_ts, data_mean


def select_frames_1s(df_head, raw_data):
    # averaging of frames per second; 2 or 3 FPS (2Hz or 3Hz) will become 1 FPS 1Hz

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

        # print(f'{idx_s}, {id_last}, {id_sel}')
        # indexes to average matrices of the mattress pressure
        # mean_sec = np.mean(raw_data[idx_s[0]:id_sel], axis=0)
        selected_frame = raw_data[id_last]
        
        data_mean = np.vstack([data_mean, np.expand_dims(selected_frame,axis=0)])

        data_time.append(lim_sup)

        # print(idx_s, raw_data[idx_s[0]:id_sel].shape, mean_sec.shape, data_mean.shape, len(data_time), data_time[-1])

    df_ts = pd.DataFrame(data_time,columns=['time_stamp'])

    return df_ts, data_mean


def plot_inclinometers(df_sel, fig, ax, time, title):

    mag = df_sel[vec_mag].to_numpy()
    off = df_sel[incl_off].to_numpy()
    lyi = df_sel[incl_lyi].to_numpy()
    sit = df_sel[incl_sit].to_numpy()
    sta = df_sel[incl_sta].to_numpy()

    for id in np.arange(5):
        ax[id].cla()
        
    ax[0].set_ylim(0,y_max)

    ax[0].plot(mag)
    ax[1].plot(off)
    ax[2].plot(lyi)
    ax[3].plot(sit)    
    ax[4].plot(sta)   

    # only one line may be specified; full height
    for id in np.arange(5):
        ax[id].axvline(x = time, color = 'r', label = 'axvline - full height')
    

    ax[0].set_title('actigraphy '+title)
    ax[0].set_ylabel('mag')
    ax[1].set_ylabel('off')
    ax[2].set_ylabel('lyi')
    ax[3].set_ylabel('sit')
    ax[4].set_ylabel('sta')
    ax[4].set_xlabel('time (s)')

    fig.canvas.draw()
    fig.canvas.flush_events()

    return

def plot_actigraphy(img, df_chest_a, df_thigh_a, time, id_frame):
    global figure_1, figure_2, ax_1, ax_2, flag_start

    vm_chest = df_chest_a[vec_mag].to_numpy()
    vm_thigh = df_thigh_a[vec_mag].to_numpy()
    

    ax_1[0].cla()
    ax_1[1].cla()
    ax_2.cla()

    ax_1[0].set_ylim(0,y_max)
    ax_1[1].set_ylim(0,y_max)

    ax_1[0].plot(vm_chest)
    ax_1[1].plot(vm_thigh)
    

    # only one line may be specified; full height
    ax_1[0].axvline(x = time, color = 'r', label = 'axvline - full height')
    ax_1[1].axvline(x = time, color = 'r', label = 'axvline - full height')

    im=ax_2.imshow(img)
    ax_2.set_title('frame '+str(id_frame))

    ax_1[0].legend(['chest'])
    ax_1[1].legend(['thigh'])

    # ax_2.tick_params(labelbottom=True, labeltop=True, labelleft=True, labelright=True, bottom=True, top=True, left=True, right=True)
    ax_2.set_xlabel('pixel (bottom)')
    ax_2.set_ylabel('pixel (right)')

    figure_1.canvas.draw()
    figure_2.canvas.draw()

    figure_1.canvas.flush_events()
    figure_2.canvas.flush_events()
    # plt.pause(0.5)

    return


def onclick(event):
    global id_frame, id_act
    # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f, name=%s' %
        #   ('double' if event.dblclick else 'single', event.button,
        #    event.x, event.y, event.xdata, event.ydata, event.name))
    if event.xdata >= id_frame_ini and event.xdata < id_frame_end:
        id_frame=int(event.xdata)
        id_act=int(event.xdata)
    else:
        pass
    # print('mouse: ', event.xdata, id_frame_ini, id_frame_end, id_frame)
    return
    
   
def on_press(event):
    global pressed_key

    print('pressed', event.key)
    pressed_key = event.key
    sys.stdout.flush()


####### main function ###########
if __name__== '__main__':
    
    # print('Interface Pressure Visualization')
    # read data Interface pressure
    path_mattress = '../data/mattress_actigraph/mattress/new_format/'
    path_actigraph = '../data/mattress_actigraph/actigraph/'
    
    day_n='day02' # ['day00', 'day01', 'day02'] day number
    pp = 'p00' # ['p00','p01','p02','p03','p04'] subject number
    nt='2' # ['1','2', 'tech'] test number

    th = 'thigh.csv'
    ch = 'chest.csv'
    he = 'head_'
    ra = 'raw_'
    

    
    filename_actigraph_chest= day_n+'_'+pp+'_'+ch
    filename_actigraph_thigh= day_n+'_'+pp+'_'+th

    file_head= day_n+'_'+pp+'_'+nt+'.csv'
    file_raw= day_n+'_'+pp+'_' +nt+'.npz'

    #########
    # loading data mattress pressure header
    df_ma = pd.read_csv(path_mattress+he+file_head)
    # loading data mattress pressure raw data
    with open(path_mattress+ra+file_raw, 'rb') as f:
        loaded=np.load(f)
        data_all = loaded['xyt']

    print(df_ma.info())
    print('data_all.shape: ', data_all.shape)

    #  In a FPS greater than 1, selecting the closest frame to the next second to get FPS equal to 1
    df_f, frames_sec = select_frames_1s(df_ma, data_all)
    
    print('selected frames:')
    print(df_f)
    print(frames_sec.shape)
    
    #########
    # loading data actigraphy

    header_location=10
   # load actigraph data
    df_chest = pd.read_csv(path_actigraph+filename_actigraph_chest, header=header_location, decimal=',')
    df_thigh = pd.read_csv(path_actigraph+filename_actigraph_thigh, header=header_location, decimal=',')
    # print(df_actigraph)

    time_ini = df_f.iloc[0]['time_stamp']
    time_end = df_f.iloc[-1]['time_stamp']
    print('time_ini, time_end: ', time_ini, time_end)

    df_chest_a = df_chest.loc[(df_chest[' Time']>=time_ini) & (df_chest[' Time']<=time_end)]
    df_thigh_a = df_thigh.loc[(df_thigh[' Time']>=time_ini) & (df_thigh[' Time']<=time_end)]
    
    # to run GUI event loop
    cid1 = figure_1.canvas.mpl_connect('button_press_event', onclick)
    # cid2 = figure_2.canvas.mpl_connect('button_press_event', onclick)
    cid3 = figure_3.canvas.mpl_connect('button_press_event', onclick)
    cid4 = figure_4.canvas.mpl_connect('button_press_event', onclick)
    
    figure_1.canvas.mpl_connect('key_press_event', on_press)
    figure_2.canvas.mpl_connect('key_press_event', on_press)
    figure_3.canvas.mpl_connect('key_press_event', on_press)
    figure_4.canvas.mpl_connect('key_press_event', on_press)
    
    plt.ion()
    plt.show()
    # print('cid1: ', cid1)
    # print('cid2: ', cid2)

    time_mattress = df_f['time_stamp'].to_numpy()
    time_actigraph = df_chest_a[' Time'].to_numpy()

    print(f'times: {time_mattress}; {time_actigraph}')

    step=0
    exit_key=False
    flag =True
    id_frame_ini = 0
    id_frame_end = len(frames_sec)



    while (exit_key==False) and (id_frame <len(frames_sec)) and flag:
        # print('id_frame: ',id_frame)
        frame=frames_sec[id_frame]
        # vm_chest = df_chest_a[vec_mag].to_numpy()
        # vm_thigh = df_thigh_a[vec_mag].to_numpy()
        # off_chest = df_chest_a[incl_off].to_numpy()
        # off_thigh = df_thigh_a[incl_off].to_numpy()

        # plot_actigraphy(frame, vm_chest, vm_thigh, off_chest, off_thigh, id_frame)
        if time_mattress[id_frame] == time_actigraph[id_act]:
            plot_actigraphy(frame, df_chest_a, df_thigh_a, id_act, id_frame)
            plot_inclinometers(df_chest_a, figure_3, ax_3, id_act, 'chest')
            plot_inclinometers(df_thigh_a, figure_4, ax_4, id_act, 'thigh')
            plt.pause(0.1)
        else:
            while time_mattress[id_frame] != time_actigraph[id_act]:
                id_act+=1
                print('id_act: ', id_act)
            plot_actigraphy(frame, df_chest_a, df_thigh_a, id_frame, id_frame)
            plot_inclinometers(df_chest_a, figure_3, ax_3, id_frame, 'chest')
            plot_inclinometers(df_thigh_a, figure_4, ax_4, id_frame, 'thigh')
            plt.pause(0.1)


        # if flag_start == True:
        #     pressed_key = cv2.waitKey(0) # miliseconds
        #     flag_start=False
        # else:
        #     pressed_key = cv2.waitKey(100) # miliseconds

        if pressed_key == 'x':
            print ("pressed x")
            exit_key=True
        elif pressed_key == 'm':
            step=1
        elif pressed_key == 'n':
            step=0

        # else:
        #     print('id frame: ', id_frame, df_f.iloc[id_frame]['time_stamp'])
        #     id_frame+=1

        print('id frame: ', id_frame, df_f.iloc[id_frame]['time_stamp'])
        id_frame+=step
        id_act+=step
    
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # plt.close('all')
    plt.show(block=True)
