#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  activity_measurements.py

from class_activity_measurements import Activity_Measurements

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys

label_vma  ='Vector Magnitude'
label_day_night = 'day_night'
label_binary_day_night = 'binary_day_night'

def on_press(event):
    # print('press', event.key)
    sys.stdout.flush()
    
    if event.key == 'x':
        plt.close('all')
    else:
        pass

def plot_vector_magnitude(list_objs):

    rows_number = len(list_objs)
    fig, ax = plt.subplots(nrows=rows_number, ncols=1, figsize=(12, 6),)
    fig.canvas.mpl_connect('key_press_event', on_press)
    fig.canvas.draw()
    
    # fig2, ax2 = plt.subplots(nrows=rows_number, ncols=1, figsize=(12, 6),)
    # fig2.canvas.mpl_connect('key_press_event', on_press)
    # fig2.canvas.draw()

    y_ini=  -10.0
    y_end=  380.0
    
    for i, obj in enumerate(list_objs):
        df = list_objs[i].getDataFrame()
        sns.lineplot(data=df, x=df.index, y=label_vma, hue=label_binary_day_night, ax=ax[i])
        ax[i].set_ylim(y_ini,y_end)
        ax[i].get_legend().set_visible(False)
        
        # arr_vm = list_objs[i].getVectorMagnitude()
        # ax2[i].plot(arr_vm)
        # ax2[i].set_ylim(y_ini,y_end)
        
    return 0


def main(args):
    
    path = "../data/projet_officiel/"

    # prefix patient id. Example: A006
    # prefix = args[1]
    # window size (in minutes) for sliding window algorithm. Example: 10 
    # sw_val = int(args[2])
    
    files_list=['A006_chest.csv', 'A003_chest.csv', 'A026_chest.csv', 'A018_chest.csv',]
    list_objs = [[]]*len(files_list)
    
    for i,filename in enumerate(files_list) :
        try:
            print(f'reading file: {filename}... ', end='')
            # create object class
            list_objs[i] = Activity_Measurements()
            list_objs[i].openFile(path, filename)
            print(f'done.')
            
        except ValueError:
            print(f'Problem reading the file {filename}.')
            
    ## plot Vector Magnitude
    # plot_vector_magnitude(list_objs)
    
    
    ## parameters
    win_a =  10 # 10 minutes
    win_b = 120 # 120 minutes
    
    for i, obj in enumerate(list_objs):
        print(f'processing {obj.filename}... ', end='')
        obj.vma_processing(win_a, win_b)
        obj.inc_processing(win_a, win_b)
        ## calculate mean value for 12h periods of days and nights
        obj.means_days_nights()
        print('done.')

    plt.show()
    
    return 0
    
    

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
