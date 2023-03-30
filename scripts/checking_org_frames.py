import numpy as np
import pandas as pd

def check_diff(df, col):

    df_time = df[col].str.split(":", expand=True)
    # print(df_time.info())
    # print(df_time.head())
    # print(np.array(df_time[1].to_numpy(), int) + 4 )
    h = np.array(df_time[0].to_numpy(), int)
    m = np.array(df_time[1].to_numpy(), int)
    s = np.array(df_time[2].to_numpy(), float)

    arr_sec = h*3600 + m*60 + s
    # print(arr_sec.shape)
    diff_sec = arr_sec[1:]-arr_sec[:-1]
    # print(diff_sec[diff_sec>1], np.argwhere(diff_sec>1))

    return diff_sec[diff_sec>1], np.argwhere(diff_sec>1)

####### main function ###########
if __name__== '__main__':

    print('checking time difference between two consecutive original frames')
     
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
    # loading data mattress pressure
    df_ma = pd.read_csv(path_mattress+he+file_head)
    # print(df_ma.info())
    # print(df_ma.head())

    vals, id_vals = check_diff(df_ma, 'hour')
    print('mattress: ', vals, id_vals)

    # loading data actigraphy

    header_location=10
   # load actigraph data
    df_chest = pd.read_csv(path_actigraph+filename_actigraph_chest, header=header_location, decimal=',')
    df_thigh = pd.read_csv(path_actigraph+filename_actigraph_thigh, header=header_location, decimal=',')
    # print(df_actigraph)

    # print(df_chest.head())
    # df_chest[' Time']
    # df_thigh[' Time']

    vals, id_vals = check_diff(df_chest, ' Time')
    print('chest: ', vals, id_vals)

    vals, id_vals = check_diff(df_thigh, ' Time')
    print('thigh: ', vals, id_vals)

