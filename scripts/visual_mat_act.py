import numpy as np
import pandas as pd
import csv
import cv2
import matplotlib.pyplot as plt
import datetime
import sys

##########
# global variables
figure_1, ax_1 = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(8, 6))
figure_2, ax_2 = plt.subplots(figsize=(6, 8))
drawing = False
x0=0
y0=0
x1=0
y1=0
pressed_key='nan'
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


def average_data(df_head, raw_data):
    # averaging of frames per second; 2 or 3 FPS (2Hz or 3Hz) will become 1 FPS 1Hz

    data_mean=np.array([],dtype=float).reshape(0, raw_data.shape[1], raw_data.shape[2])
    data_time=[]

    id_sel=0
    # print(len(raw_data))
    while id_sel < len(raw_data):
        sel_hour=df_head['hour'].values[id_sel]
        # print("df['hour'].values[0]: ", sel_hour)
        
        hour_splitted = datetime.datetime.strptime(sel_hour, "%H:%M:%S.%f")
        h=hour_splitted.hour
        m=hour_splitted.minute
        s=hour_splitted.second

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

        id_last = idx_s[-1]
        id_sel = id_last+1

        # indexes to average matrices of the mattress pressure
        mean_sec = np.mean(raw_data[idx_s[0]:id_sel], axis=0)
        
        data_mean = np.vstack([data_mean, np.expand_dims(mean_sec,axis=0)])

        data_time.append(lim_sup)

        # print(idx_s, raw_data[idx_s[0]:id_sel].shape, mean_sec.shape, data_mean.shape, len(data_time), data_time[-1])

    df_ts = pd.DataFrame(data_time,columns=['time_stamp'])

    return df_ts, data_mean


def plot_pressure(img):
    global figure_2, ax_2

    ax_2.cla()
    ax_2.imshow(img)

    figure_2.canvas.draw()
    figure_2.canvas.flush_events()

    return

def plot_actigraphy(img,chest,thigh,time):
    global figure_1, figure_2, ax_1, ax_2
    ax_1[0].cla()
    ax_1[1].cla()
    ax_2.cla()

    ax_1[0].plot(thigh)
    ax_1[1].plot(chest)

    # only one line may be specified; full height
    ax_1[0].axvline(x = time, color = 'r', label = 'axvline - full height')
    ax_1[1].axvline(x = time, color = 'r', label = 'axvline - full height')

    ax_2.imshow(img)

    ax_1[0].legend(['thigh'])
    ax_1[1].legend(['chest'])

    ax_2.set_xlabel('pixel')
    ax_2.set_ylabel('pixel')

    figure_1.canvas.draw()
    figure_2.canvas.draw()

    figure_1.canvas.flush_events()
    figure_2.canvas.flush_events()

    return


def onclick(event):
    print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f, name=%s' %
          ('double' if event.dblclick else 'single', event.button,
           event.x, event.y, event.xdata, event.ydata, event.name))
   
    

def on_press(event):
    global pressed_key

    print('press', event.key)
    pressed_key = event.key
    sys.stdout.flush()

    # if event.key == 'x':
    #     visible = xl.get_visible()
    #     xl.set_visible(not visible)
    #     fig.canvas.draw()

####### main function ###########
if __name__== '__main__':
    # print('Interface Pressure Visualization')
    # read data Interface pressure
    path_mattress = '../data/mattress_actigraph/mattress/new_format/'
    path_actigraph = '../data/mattress_actigraph/actigraph/'
    
    day_n='day_1' # ['day_0', 'day_1']
    pp = 'p03' # ['p00','p01','p02','p03','p04']
    th = 'thigh.csv'
    ch = 'chest.csv'
    he = 'head_'
    ra = 'raw_'
    ncsv = '1.csv' # ['1.csv','2.csv']
    nnpz = '1.npz' # ['1.npz','2.npz']

    
    filename_actigraph_chest= day_n+'_'+pp+'_'+ch
    filename_actigraph_thigh= day_n+'_'+pp+'_'+th

    file_head= day_n+'_'+pp+'_'+ncsv
    file_raw= day_n+'_'+pp+'_'+nnpz

    # filename_mattress_2='test_gerardo_2.csv'
    
    # filename = filename_mattress_1

    #########
    # loading data mattress pressure
    df = pd.read_csv(path_mattress+he+file_head)
    
    with open(path_mattress+ra+file_raw, 'rb') as f:
        loaded=np.load(f)
        data_all = loaded['xyt']

    print(df.info())
    print(data_all.shape)

    df_f, frames_sec = average_data(df, data_all)
    # print(df_f)
    # print(frames_sec.shape)
    
    #########
    # loading data actigraphy
    incl_off ='Inclinometer Off'
    incl_sta ='Inclinometer Standing'
    incl_sit ='Inclinometer Sitting'
    incl_lyi ='Inclinometer Lying'
    vec_mag  ='Vector Magnitude'

    header_location=10
   # load actigraph data
    df_chest = pd.read_csv(path_actigraph+filename_actigraph_chest, header=header_location, decimal=',')
    df_thigh = pd.read_csv(path_actigraph+filename_actigraph_thigh, header=header_location, decimal=',')
    # print(df_actigraph)

    time_ini = df_f.iloc[0]['time_stamp']
    time_end = df_f.iloc[-1]['time_stamp']
    print(time_ini, time_end)

    df_chest_a = df_chest.loc[(df_chest[' Time']>=time_ini) & (df_chest[' Time']<=time_end)]
    df_thigh_a = df_thigh.loc[(df_thigh[' Time']>=time_ini) & (df_thigh[' Time']<=time_end)]
    
    # # activate interactive mouse actions on window
    # cv2.namedWindow('image')
    # cv2.setMouseCallback('image',mouse_interact)

    # to run GUI event loop
    cid1 = figure_1.canvas.mpl_connect('button_press_event', onclick)
    cid2 = figure_2.canvas.mpl_connect('button_press_event', onclick)
    figure_1.canvas.mpl_connect('key_press_event', on_press)
    figure_2.canvas.mpl_connect('key_press_event', on_press)
    plt.ion()
    plt.show()
    print('cid1: ', cid1)
    print('cid2: ', cid2)
    

    id_frame=0
    step=0
    exit_key=False
    flag =True
    flag_start=True


    while (exit_key==False) and (id_frame <len(frames_sec)) and flag:

        frame=frames_sec[id_frame]
       
        plot_actigraphy(frame, df_chest_a[vec_mag].to_numpy(), df_thigh_a[vec_mag].to_numpy(), id_frame)
        # plt.pause(.01)

        # if flag_start == True:
        #     pressed_key = cv2.waitKey(0) # miliseconds
        #     flag_start=False
        # else:
        #     pressed_key = cv2.waitKey(100) # miliseconds

        if pressed_key == 'x':
            print ("pressed x")
            exit_key=True
        elif pressed_key == 'h':
            step=1
        elif pressed_key == 'd':
            step=0

        # else:
        #     print('id frame: ', id_frame, df_f.iloc[id_frame]['time_stamp'])
        #     id_frame+=1

        # print('id frame: ', id_frame, df_f.iloc[id_frame]['time_stamp'])
        id_frame+=step
    
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    plt.close('all')
    # plt.show()
