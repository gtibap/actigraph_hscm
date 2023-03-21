import numpy as np
import pandas as pd
import csv
import cv2
import matplotlib.pyplot as plt
import datetime

##########
# global variables
figure, ax = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(8, 6))


def resize_img(img):
    # print('Original Dimensions : ',img.shape)
 
    scale_percent = 1000 # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    
    # resize image
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    
    # print('Resized Dimensions : ',resized.shape)
    return resized


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


def plot_actigraphy(chest,thigh,time):
    global figure, ax
    ax[0].cla()
    ax[1].cla()
    ax[0].plot(thigh)
    ax[1].plot(chest)

    ax[0].legend(['thigh'])
    ax[1].legend(['chest'])

    # only one line may be specified; full height
    ax[0].axvline(x = time, color = 'r', label = 'axvline - full height')
    ax[1].axvline(x = time, color = 'r', label = 'axvline - full height')

    figure.canvas.draw()
    figure.canvas.flush_events()

    return



####### main function ###########
if __name__== '__main__':
    # print('Interface Pressure Visualization')
    # read data Interface pressure
    path_mattress = '../data/interface_pressure/Mattress_test/Gerardo_test/Mattress/'
    path_actigraph = '../data/interface_pressure/Mattress_test/Gerardo_test/Actigraph/'
    filename_mattress_1='test_gerardo_1.csv'
    filename_mattress_2='test_gerardo_2.csv'
    filename_actigraph_chest='ger_test_1_chest1secDataTable.csv'
    filename_actigraph_thigh='ger_test_1_thigh1secDataTable.csv'
    head_file = 'head_'
    raw_file = 'raw_'

    filename = filename_mattress_1

    #########
    # loading data mattress pressure
    df = pd.read_csv(path_mattress+head_file+filename)

    with open(path_mattress+raw_file+filename+'.npy', 'rb') as f:
        data_all=np.load(f, allow_pickle=False)

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
    # to run GUI event loop
    plt.ion()
    plt.show()

    id_frame=0
    exit_key=False
    flag =True
    flag_start=True

    while (exit_key==False) and (id_frame <len(frames_sec)) and flag:

        frame=frames_sec[id_frame]
        frame=resize_img(3.0*frame)
        frame = frame.astype(np.uint8)
        
        colormap = plt.get_cmap('plasma')
        heatmap = (colormap(frame) * 2**16).astype(np.uint16)[:,:,:3]
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_RGB2BGR)

        cv2.imshow('image',heatmap)

        # plot_actigraphy(df_chest_a.iloc[0:id_frame][vec_mag].to_numpy(), df_thigh_a.iloc[0:id_frame][vec_mag].to_numpy())
        plot_actigraphy(df_chest_a[vec_mag].to_numpy(), df_thigh_a[vec_mag].to_numpy(), id_frame)

        if flag_start == True:
            pressed_key = cv2.waitKey(0) # miliseconds
            flag_start=False
        else:
            pressed_key = cv2.waitKey(100) # miliseconds

        if pressed_key == ord('a'):
            print ("pressed a")
            exit_key=True
        else:
            print('id frame: ', id_frame, df_f.iloc[id_frame]['time_stamp'])
            id_frame+=1
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()
