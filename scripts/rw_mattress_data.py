import numpy as np
import pandas as pd
import csv
import datetime
import os
import re


def hour_reformat(sel_hour):

    h,m,s,m_s=re.split('[:]', sel_hour)
    
    h=str(h).zfill(2)
    m=str(m).zfill(2)
    s=str(s).zfill(2)
    m_s = str(m_s).zfill(3)

    # print(f'{h}:{m}:{s}:{m_s}')

    hour_formatted=h+':'+m+':'+s+'.'+m_s
    return hour_formatted

####### main function ###########
if __name__== '__main__':
    # print('Interface Pressure Visualization')
    # read data Interface pressure
    # path = '../data/interface_pressure/Gerardo_test/'
    # filename='test_gerardo_1.csv'
    # head_file = 'head_'
    # raw_file = 'raw_'

    path = '../data/mattress_actigraph/mattress/'
    ori_dir = 'original/'
    new_dir = 'new_format/' 
    day_n = 'day02'

    input_dir = path+ori_dir
    output_dir = path+new_dir

    # filename_mattress_1='test_gerardo_1.csv'
    # filename_mattress_2='test_gerardo_2.csv'
    
    head_file = 'head_'
    raw_file = 'raw_'

    # read file names from a directory
    file_names = []
    for fn in os.listdir(input_dir):
        if os.path.isfile(os.path.join(input_dir,fn)) and (day_n in fn) and (not fn.startswith('.')):
            print(fn)
            file_names.append(fn)
    print(file_names)

    for filename in file_names:
        # print('filename: ', filename)

        df = pd.DataFrame()
        # data_frame = np.array([],dtype=float)
        data_all = np.array([],dtype=float)

        start_frame=False
        first_frame=True
        first_line=True
        first_data_row=False

        print('filename: ', filename)
        id_frame=0
        with open(input_dir+filename, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0].startswith('FRAME'):
                    if first_line==True:
                        first_line=False
                    else:
                        cols_names= np.concatenate(['day','date','hour','am_pm'],axis=None)
                        cols_data = np.concatenate([day,date,hour,am_pm], axis=None)
                        df_row = pd.DataFrame([cols_data],columns=cols_names)

                        df = pd.concat([df,df_row],ignore_index=True)

                        if first_frame==True:
                            data_all=np.array([],dtype=float).reshape(0, data_frame.shape[0], data_frame.shape[1])
                            data_all = np.vstack([data_all, np.expand_dims(data_frame,axis=0)])
                            first_frame=False
                        else:
                            data_all = np.vstack([data_all, np.expand_dims(data_frame,axis=0)])
                            
                        id_frame+=1
                    
                    start_frame=True

                elif start_frame==True:
                    date_time = row[0].split()
                    day = date_time[0]
                    date =  date_time[5] +'-'+ date_time[1] +'-'+ date_time[2]
                    hour = hour_reformat(date_time[3])
                    am_pm = date_time[4]

                    start_frame=False
                    first_data_row=True
                else:
                    data_row = np.array(row[0].split(), dtype=float)
                    # print('data_row: ', data_row.shape, first_data_row)
                    if first_data_row == True:
                        data_frame=np.array([],dtype=float).reshape(0,len(data_row))
                        data_frame = np.vstack([data_frame, data_row])
                        first_data_row=False
                    else:
                        data_frame = np.vstack([data_frame, data_row])

            # the last frame
            cols_names= np.concatenate(['day','date','hour','am_pm'],axis=None)
            cols_data = np.concatenate([day,date,hour,am_pm], axis=None)
            df_row = pd.DataFrame([cols_data],columns=cols_names)

            df = pd.concat([df,df_row],ignore_index=True)
            data_all = np.vstack([data_all, np.expand_dims(data_frame,axis=0)])

            print('writing...')
            print(df.info())
            print('data shape:', data_all.shape)

            df.to_csv(output_dir+head_file+filename, index=False)
            nfn = os.path.splitext(filename)
            with open(output_dir+raw_file+nfn[0]+'.npz', 'wb') as f:
                # np.save(f, data_all, allow_pickle=False)
                np.savez_compressed(f, xyt=data_all)
            print('done.')
