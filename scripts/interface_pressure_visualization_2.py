import numpy as np
import pandas as pd
import csv
import cv2
import matplotlib.pyplot as plt
import datetime

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

    id_sel=0
    # print(len(raw_data))
    while id_sel < len(raw_data):
        sel_hour=df_head['hour'].values[id_sel]
        # print("df['hour'].values[0]: ", sel_hour)
        
        hour_splitted = datetime.datetime.strptime(sel_hour, "%H:%M:%S.%f")
        hour=str(hour_splitted.hour).zfill(2)
        min=str(hour_splitted.minute).zfill(2)
        sec_inf=str(hour_splitted.second).zfill(2)
        sec_sup=str(hour_splitted.second+1).zfill(2)
        u_sec = str(hour_splitted.microsecond)
        # print(hour+':'+min+':'+sec_inf+'.'+u_sec)

        lim_inf = hour+':'+min+':'+sec_inf
        lim_sup = hour+':'+min+':'+sec_sup

        # print('lim_inf, lim_sup: ', lim_inf, lim_sup)

        idx_s = df_head.loc[(df_head['hour']>= lim_inf) & (df_head['hour']<lim_sup)].index.values
        print(idx_s)

        id_last = idx_s[-1]
        id_sel = id_last+1

        # sel_hour = df_head.loc[[id_sel],['hour']].values[0][0]
        # print(sel_hour)
    
    # first_hour=df_head['hour'].values[0]

    # id_last = time_stamp.index.values[-1]
    # id_end = df.index.values[-1]
    # print(time_stamp, id_last, id_end)
    # print(df.loc[[id_last+1],['hour']].values[0][0])

    # return new_head, new_data
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

    # heading 
    df = pd.read_csv(path_mattress+head_file+filename)

    with open(path_mattress+raw_file+filename+'.npy', 'rb') as f:
        data_all=np.load(f, allow_pickle=False)

    print(df.info())
    print(data_all.shape)

    # a_head, a_data = average_data(df, data_all)
    average_data(df, data_all)

    # incl_off ='Inclinometer Off'
    # vec_mag  ='Vector Magnitude'
    # # load actigraph data
    # df1 = pd.read_csv(path+sample, header=header_location, decimal=',', usecols=['Date',' Time', vec_mag, incl_off])



    id_frame=0
    exit_key=False
    flag =False

    while (exit_key==False) and (id_frame <len(data_all)) and flag:

        frame=data_all[id_frame]
        frame=resize_img(frame)
        

        print('id frame: ', id_frame, time_stamp[id_frame])
        
        cv2.imshow('image',frame)
        pressed_key = cv2.waitKey(100) # miliseconds
        if pressed_key == ord('a'):
            print ("pressed a")
            exit_key=True
        else:
            id_frame+=2
    
    cv2.waitKey(0)
