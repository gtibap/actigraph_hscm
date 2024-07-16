#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  activity_measurements.py

from class_activity_measurements import Activity_Measurements
from dict_days_nights import dict_days_nights

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys


label_day_night = 'day_night'
vma_b='vma_b'

# list_days=['d1','d2','d3','d4','d5']
# list_nights=['n1','n2','n3','n4','n5']


def median_values(df, range_dn):

    ## adding one to the upper limit to include the last day and last night in the generated arrays
    num_d = np.arange(range_dn[0][0], range_dn[0][1]+1)
    num_n = np.arange(range_dn[1][0], range_dn[1][1]+1)

    ## generating labels for days and nights
    list_d = ['d'+str(x) for x in num_d]
    list_n = ['n'+str(x) for x in num_n]

    # print(f'list   days: {list_d}')
    # print(f'list nights: {list_n}')

    arr_ds=[]
    arr_ns=[]
    
    for label_d, label_n in zip(list_d, list_n):
            
        df_label_d = df[df[label_day_night]== label_d]
        df_label_n = df[df[label_day_night]== label_n]
        ## data output stage 2 sliding window algorithms
        arr_d=df_label_d[vma_b].to_numpy()
        arr_n=df_label_n[vma_b].to_numpy()

        arr_ds = np.concatenate((arr_ds, arr_d), axis=None) 
        arr_ns = np.concatenate((arr_ns, arr_n), axis=None) 

    median_ds = np.median(arr_ds)
    median_ns = np.median(arr_ns)
    print(f'median d: {median_ds}')            
    print(f'median n: {median_ns}')
    
    return [median_ds, median_ns]

def on_press(event):
    # print('press', event.key)
    sys.stdout.flush()
    
    if event.key == 'x':
        plt.close('all')
    else:
        pass
    return 0

##
def plot_activity_rates(id_objs):

    fig, ax = plt.subplots(nrows=len(id_objs), ncols=1, sharex=True, figsize=(12, 6))
    fig.canvas.mpl_connect('key_press_event', on_press)

    y_ini= -0.1
    y_end=  1.1

    for i, obj in enumerate(id_objs):

        df1 = obj.get_df1()
        ## plot days and nights with different colors
        labels_list = df1[label_day_night].unique().tolist()
        # print(f'labels_list: {labels_list}')
        id_ini = 0

        for label in labels_list:
            df_period = df1[df1[label_day_night]== label]

            arr_ar = df_period[vma_b].to_list()

            ids=np.arange(id_ini, id_ini+len(df_period))
                
            if label.startswith('d'):
                ax[i].plot(ids, arr_ar, color='tab:orange', label='')
            else:
                ax[i].plot(ids, arr_ar, color='tab:blue', label='')

            id_ini=id_ini+len(df_period)
            
            # vertical line
            ax[i].vlines(x=[id_ini], ymin=y_ini, ymax=y_end, colors='purple', ls='--', lw=1, label='')

        ax[i].set_ylim(y_ini,y_end)
        ax[i].set_title(obj.getName())
        ax[i].set_ylabel('activity_rate')
    ax[-1].set_xlabel('samples')

    return 0


def main(args):

    ## parameters
    win_a =   10 # 10 minutes
    win_b =  120 # 120 minutes

    path = "../data/projet_officiel/"
    # path_out = "../data/projet_officiel/measurements/figures/"
    path_out_tables = "../data/projet_officiel/measurements/tables/"

    # print(f'dict days nights:\n{dict_days_nights}')
    # checking file list
    # id_names = ['A001','A015','A027','A029','A038']
    id_names = ['A046',]

    # ## filenames' sequence generation. For example from A001 to A050 -> min = 1, max = 50
    # min=42
    # max=42
    # list_files = np.arange(min,max+1,1).tolist()
    # id_names= ['A'+str(a).zfill(3) for a in list_files]

    id_objs = [[]]*2
    filenames = [[]]*2

    ## dataframe to register median values of activity rates for chest and thigh 
    df_median_values = pd.DataFrame(columns=['id','chest_d','chest_n','thigh_d','thigh_n'])

    ## loop to read files of multiple subjects
    for id in id_names:
        filenames[0] = id + '_chest'
        filenames[1] = id + '_thigh'
        ## loop read files chest and thigh one subject
        for i, fname in enumerate(filenames):
            try:
                print(f'reading file: {fname}... ', end='')
                # create object class
                id_objs[i] = Activity_Measurements(fname)
                id_objs[i].openFile(path, fname+'.csv')
                print(f'done.')
                
            except Exception:
                print(f'Problem reading the file {fname}.')
                continue

        ## range for median values calculation. Same range for chest and thigh
        range_days_nights = dict_days_nights[id]
        # print(f'range days nights {range_days_nights}')
        median_vals = [id]
        ## applying sliding window algorithm to chest and thigh recordings
        for obj in id_objs:
            print(f'processing {obj.filename}... ', end='')
            ## activity rates calculation
            obj.vma_processing(win_a, win_b)
            print('done.')

            ## mean values calculation
            median_vals.extend( median_values(obj.get_df1(), range_days_nights) )

        ## registering median values in dataframe
        df_median = pd.DataFrame([median_vals],columns=['id','chest_d','chest_n','thigh_d','thigh_n'])
        df_median_values = pd.concat([df_median_values, df_median], ignore_index=True)

        ## plot activity rates chest and thigh
        plot_activity_rates(id_objs)
        plt.show()

    # df_median_values.to_csv(path_out_tables+'median_values.csv')
    print (f'df_median_values:\n{df_median_values}')
    

    plt.show()
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
