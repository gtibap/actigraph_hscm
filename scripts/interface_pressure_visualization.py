import pickle
import numpy as np
import pandas as pd
import csv

####### main function ###########
if __name__== '__main__':
    # print('Interface Pressure Visualization')
    # read data Interface pressure
    path = '../data/interface_pressure/Gerardo_test/'
    filename='test_gerardo_1.csv'
    filename_out_head = 'head_test_gerardo_1.csv'
    filename_out_raw = 'raw_test_gerardo_1.'

    df = pd.DataFrame()
    # data_frame = np.array([],dtype=float)
    data_all = np.array([],dtype=float)

    start_frame=False
    first_frame=True
    first_line=True
    first_data_row=False

    id_frame=0
    with open(path+filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0].startswith('FRAME'):
                # print(row, type(row), len(row), len(row[0]))
                if first_line==True:
                    first_line=False
                else:
                    # print(id_frame, data_concat, len(data_concat))
                    cols_names= np.concatenate(['day','date','hour','am_pm'],axis=None)
                    cols_data = np.concatenate([day,date,hour,am_pm], axis=None)
                    df_row = pd.DataFrame([cols_data],columns=cols_names)

                    # print('df_row: ', df_row)
                    df = pd.concat([df,df_row],ignore_index=True)
                    # print('df: ', df)
                    # np.concatenate([data_all,data_concat],a)
                    # data_frame = np.array([],dtype=float)
                    print('data_frame:', data_frame.shape, '\n', data_frame)
                    if first_frame==True:
                        data_all=np.array([],dtype=float).reshape(0, data_frame.shape[0], data_frame.shape[1])
                        data_all = np.vstack([data_all, np.expand_dims(data_frame,axis=0)])
                        first_frame=False
                    else:
                        data_all = np.vstack([data_all, np.expand_dims(data_frame,axis=0)])
                    print('data_all.shape: ', data_all.shape)
                        
                    id_frame+=1
                
                start_frame=True

            elif start_frame==True:
                date_time = row[0].split()
                # print(date_time, date_time.split())
                day = date_time[0]
                date = date_time[1] +'\\'+ date_time[2] +'\\'+ date_time[5]
                hour = date_time[3]
                am_pm = date_time[4]

                start_frame=False
                first_data_row=True
            else:
                data_row = np.array(row[0].split(), dtype=float)
                # print('len(data_row): ', len(data_row))
                if first_data_row == True:
                    # print('len(data_row): ', data_row.shape)
                    data_frame=np.array([],dtype=float).reshape(0,len(data_row))
                    data_frame = np.vstack([data_frame, data_row])
                    # print('data_frame.shape: ', data_frame.shape)
                    first_data_row=False
                else:
                    data_frame = np.vstack([data_frame, data_row])
                    # print(data_frame)                
                                    
            
