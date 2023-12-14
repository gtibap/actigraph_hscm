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
vma_a='vma_a'
vma_b='vma_b'
inc_a='inc_a'
inc_b='inc_b'

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
        df = list_objs[i].get_df1()
        ## paint each day and each night
        labels_list = df[label_day_night].unique().tolist()
        for label in labels_list:
            df_label = df[df[label_day_night]== label]
            vma=df_label[label_vma].to_list()
            ids=df_label.index
            if label.startswith('d'):
                ax[i].plot(ids, vma, color='tab:blue')
            else:
                ax[i].plot(ids, vma, color='tab:orange')
        
        ax[i].set_ylim(y_ini,y_end)
        
        # sns.lineplot(data=df, x=df.index, y=label_vma, hue=label_binary_day_night, ax=ax[i])
        # ax[i].get_legend().set_visible(False)
        
        # arr_vm = list_objs[i].getVectorMagnitude()
        # ax2[i].plot(arr_vm)
        # ax2[i].set_ylim(y_ini,y_end)
        
    return 0

def plot_vma_step(list_objs, step):
    
    rows_number = len(list_objs)
    fig, ax = plt.subplots(nrows=rows_number, ncols=1, figsize=(12, 6), sharex=True,)
    fig.canvas.mpl_connect('key_press_event', on_press)
    fig.canvas.draw()
    
    y_ini=  -0.08
    y_end=   1.08
    
    if step==1:
        label_step = vma_a
    else:
        label_step = vma_b
    
    for i, obj in enumerate(list_objs):
        ## get dataframe 
        df = list_objs[i].get_df1()
        ## paint each day and each night
        labels_list = df[label_day_night].unique().tolist()
        for label in labels_list:
            df_label = df[df[label_day_night]== label]
            vma=df_label[label_step].to_list()
            ids=df_label.index
            if label.startswith('d'):
                ax[i].plot(ids, vma, color='tab:blue')
            else:
                ax[i].plot(ids, vma, color='tab:orange')
        
        ax[i].set_ylim(y_ini,y_end)
        
    return 0


def plot_vma_cycle(list_objs):
    
    rows_number = len(list_objs)
    fig, ax = plt.subplots(nrows=rows_number, ncols=1, figsize=(12, 6), sharex=True,)
    fig.canvas.mpl_connect('key_press_event', on_press)
    fig.canvas.draw()
    
    y_ini=  -0.08
    y_end=   1.08
    
    label_step = vma_b
    
    length_day=12*3600 ## 12 hours in seconds
    length_night=12*3600 ## 12 hours in seconds
    total_days=5
    total_nights=5
    
    list_days=['d1','d2','d3','d4','d5']
    list_nights=['n1','n2','n3','n4','n5']
    
    for i, obj in enumerate(list_objs):
        ## get dataframe 
        df = list_objs[i].get_df1()
        ## paint each day and each night
        labels_list = df[label_day_night].unique().tolist()
        
        for label in labels_list:
            
            df_label = df[df[label_day_night]== label]
            vma=df_label[label_step].to_list()

            if (label in list_days):
                ax[i].plot(np.arange(0,length_day), vma, color='tab:blue')
            elif (label in list_nights):
                ax[i].plot(np.arange(length_day,length_day+length_night), vma, color='tab:orange')
            else:
                pass

        ax[i].set_ylim(y_ini,y_end)
        
    return 0


def plot_cycle_alpha(list_objs, selected_label, title):
    
    rows_number = len(list_objs)
    fig, ax = plt.subplots(nrows=rows_number, ncols=1, figsize=(12, 6), sharex=True,)
    fig.canvas.mpl_connect('key_press_event', on_press)
    fig.canvas.draw()
    
    y_ini=  -0.08
    y_end=   1.08
    
    list_ticks_x =[]
    
    hour_0 = 9
    list_ticks_x.extend(np.arange(hour_0,24,1)) 
    list_ticks_x.extend(np.arange(0,hour_0+1,1)) 
    
    
    label_step = selected_label
    
    length_day=12*3600 ## 12 hours in seconds
    length_night=12*3600 ## 12 hours in seconds
    total_days=5
    total_nights=5
    
    list_days=['d1','d2','d3','d4','d5']
    list_nights=['n1','n2','n3','n4','n5']
    
    
    for i, obj in enumerate(list_objs):
        ## get dataframe 
        df = list_objs[i].get_df1()
        ## paint each day and each night
        labels_list = df[label_day_night].unique().tolist()
        
        df_day = pd.DataFrame(columns=list_days)
        df_night = pd.DataFrame(columns=list_nights)
        
        for label in labels_list:
            
            df_label = df[df[label_day_night]== label]
            arr=df_label[label_step].to_list()

            if (label in list_days):
                df_day[label]=arr
                # ax[i].plot(np.arange(0,length_day), vma, color='tab:blue')
            elif (label in list_nights):
                df_night[label]=arr
                # ax[i].plot(np.arange(length_day,length_day+length_night), vma, color='tab:orange')
            else:
                pass

        df_day['median'] = df_day.median(axis=1)
        df_day['min']    = df_day.min(axis=1)
        df_day['max']    = df_day.max(axis=1)
        
        df_night['median'] = df_night.median(axis=1)
        df_night['min']    = df_night.min(axis=1)
        df_night['max']    = df_night.max(axis=1)
        
        
        # specifying horizontal line type 
        ax[i].axhline(y = 0.5, color = 'black', linestyle = '--', alpha=0.3) 
        
        color_day='tab:blue'
        color_night='tab:orange'
        
        pattern_day='//'
        pattern_night='..'
        
        ax[i] = plot_alpha(df_day, 0, length_day, color_day, pattern_day, 'day', ax[i])
        ax[i] = plot_alpha(df_night, length_day, length_night, color_night, pattern_night, 'night', ax[i])
        
        ax[i].set_ylim(y_ini,y_end)
    
    # length_x = length_day + length_night
    # length_day / 

    ax[0].legend(loc='upper right', bbox_to_anchor=(1.0, 1.4),fancybox=False, shadow=False, ncol=2)
    
    x_ticks= b=np.arange(0,(25*3600), 3600)
    ax[-1].set_xticks(x_ticks, list_ticks_x,) 
    
    
    ax[0].set_ylabel('P_1')
    ax[1].set_ylabel('P_2')
    ax[2].set_ylabel('P_3')
    ax[3].set_ylabel('P_4')
    
    ax[-1].set_xlabel('time(h)')
   
    fig.suptitle(title)
        
    return 0
    
def plot_alpha(df, start, size, color, pattern, sel_label, ax):
    
    x = np.arange(start,start+size)
    y = df['median'].to_list()
    ymax = df['max'].to_list()
    ymin = df['min'].to_list()
    alpha_fill = 0.3
    
    ax.plot(x, y, color=color)
    ax.fill_between(x, ymax, ymin, color=color, hatch=pattern, alpha=alpha_fill, label=sel_label)
    
    return ax
    


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
    win_b = 180 # 120 minutes
    
    for i, obj in enumerate(list_objs):
        print(f'processing {obj.filename}... ', end='')
        obj.vma_processing(win_a, win_b)
        obj.inc_processing(win_a, win_b)
        ## calculate mean value for 12h periods of days and nights for vector magnitude and inclinometers
        obj.means_days_nights()
        print('done.')

    ## plot results processing
    # plot_vma_step(list_objs, 1)
    # plot_vma_step(list_objs, 2)
    # plot_vma_cycle(list_objs)
    plot_cycle_alpha(list_objs, vma_b, 'Vector Magnitude Activity')
    # plot_cycle_alpha(list_objs, inc_b, 'Inclinometers Activity')

    plt.show()
    
    return 0
    
    

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
