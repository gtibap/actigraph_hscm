#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  activity_measurements.py

from class_activity_measurements import Activity_Measurements
from matplotlib.ticker import LinearLocator

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys

label_vma  ='Vector Magnitude'
label_vma_b = 'vma_b'
label_day_night = 'day_night'
label_binary_day_night = 'binary_day_night'
label_incl = 'Inclinometers Activity'
vma_a='vma_a'
vma_b='vma_b'
inc_a='inc_a'
inc_b='inc_b'

# legend
asia = ['B','A','A','A']
nl = ['C4','C6','T7','T10']

list_days=['d1','d2','d3','d4','d5']
list_nights=['n1','n2','n3','n4','n5']

g_hen = 7
g_hed = 23
g_hours_night = g_hen + 24-g_hed
g_hours_day   = 24-g_hours_night


def on_press(event):
    # print('press', event.key)
    sys.stdout.flush()
    
    if event.key == 'x':
        plt.close('all')
    else:
        pass
    return 0


def plot_sw_outcomes(list_objs, labels_rec, labels_con, group_title, body_part_title, flag_save, path):

    # list_days=['d1','d2','d3','d4','d5']
    # list_nights=['n1','n2','n3','n4','n5']
        
    rows_number = len(list_objs)
    fig, ax = plt.subplots(nrows=rows_number, ncols=1, figsize=(18, 10), sharex=True, )
    fig.canvas.mpl_connect('key_press_event', on_press)
    fig.canvas.draw()
    
    plt.rcParams.update({'font.size': 19})
    
    # num_samples = 43200 ## 12 hours, a sample every second
    num_samples_night = g_hours_night*3600
    num_samples_day   = g_hours_day*3600
    num_samples_24 = 24*3600
    pad_h = 3600

    # y_ini=  -10.0
    # y_end=   60.0
    y_ini=  -0.08
    y_end=   1.08

    ## show night 3 + a little of day3 and day4 (before and after of night 3, respectively)
    # x_ini = 5*num_samples - int(num_samples/20) 
    # x_end = 6*num_samples + int(num_samples/20) 
    x_ini = 2*(num_samples_24) + num_samples_day - pad_h 
    x_end = 3*(num_samples_24) + pad_h
    
    # x_text_pos = 0
    # y_text_pos = y_end - 80
    
    for i, obj in enumerate(list_objs):
        
        df = list_objs[i].get_df1()
        
        # trans = ax[i].get_xaxis_transform() # x in data units, y in axes fraction. This is for legend location
        id_d = 1
        id_n = 1

        id_ini = 0
        
        ax[i].vlines(x=[id_ini], ymin=y_ini, ymax=y_end, colors='purple', ls='--', lw=1, label='')
        ## paint each day and each night
        labels_list = df[label_day_night].unique().tolist()
        # print(f'labels: {labels_list}')
        for label in labels_list:
            
            if (label in list_days) or (label in list_nights):
                
                df_label = df[df[label_day_night]== label]
                vma=df_label[label_vma_b].to_list()
                # ids=df_label.index
                ids=np.arange(id_ini, id_ini+len(df_label))
                # print(f'ids size: {len(ids)}, {len(df_label)}')
                
                if label.startswith('d'):
                    ax[i].plot(ids, vma, color='tab:orange', label='')
                else:
                    ax[i].plot(ids, vma, color='tab:blue', label='')
                
                id_ini=id_ini+len(df_label)
                # vertical line
                ax[i].vlines(x=[id_ini], ymin=y_ini, ymax=y_end, colors='purple', ls='--', lw=1, label='')
                
            else:
                pass


    # hide xtick values
    # ax[0].set_xticklabels([])
    # ax[1].set_xticklabels([])
    # ax[2].set_xticklabels([])
    
    ## legend
    # asia = ['B','A','A','A']
    # nl = ['C4','C6','T7','T10']
    
    # ## font size labels and ticks every hour
    ## 5 blocks of 24h each (5*24), plus 1 tick at the end -> (5*24)+1
    xticks = np.linspace(0, num_samples_24*5, int(5*24)+1).astype(int)
    
    
    # ticks_labels = np.concatenate((np.arange(9,24), np.arange(0,9)), axis=None)
    # g_hen = 7
    # g_hed = 23
    ticks_labels = np.concatenate((np.arange(g_hen,24), np.arange(0,g_hen)), axis=None)
    
    ticks_labels = [str(x).zfill(2) for x in ticks_labels]
    print(f'one ticks labels:{ticks_labels}')
    ticks_labels = ticks_labels*5
    print(f'two ticks labels:{ticks_labels}')
    ticks_labels.append(0)
    print(f'three ticks labels:{ticks_labels}')
    ax[-1].set_xticks(xticks, ticks_labels, fontsize=20)
    
    # ax[-1].set_xticks(xticks, ticks_labels, fontsize=12)
    # xticks = np.linspace(0, num_samples*10, 11).astype(int)
    # ax[-1].set_xticks(xticks, (xticks/3600).astype(int), fontsize=12)
    
    for i in np.arange(len(list_objs)):
        ##
        # ax[i].legend([], title=f'{labels_rec[i]}\n{labels_con[i]}', alignment='center', loc='upper left', bbox_to_anchor=(1.0, 1.15), ncol=1, fancybox=True, shadow=True,)
        ax[i].legend([], title=f'{labels_rec[i]}', alignment='center', loc='upper left', bbox_to_anchor=(1.0, 1.15), ncol=1, fancybox=True, shadow=True,)
        
        ## y scale
        ax[i].set_ylim(y_ini,y_end)
        
        ## x scales
        ax[i].set_xlim(x_ini,x_end)
        
        # hide xtick values
        # ax[i].set_xticklabels([])
        
    # for i in np.arange(4):
        # ax[i].legend([], title=f'P{i+1} - VM\n(counts)\nAIS: {asia[i]}\nNLI: {nl[i]}', alignment='center', loc='upper left', bbox_to_anchor=(1.0, 1.1), ncol=1, fancybox=True, shadow=True,)
    
    # ## annotate
    # trans = ax[0].get_xaxis_transform() # x in data units, y in axes fraction
    # list_x_pos = (2*num_samples)*np.arange(5)
    
    # for i, x_pos in enumerate(list_x_pos):
        # ann = ax[0].annotate(f'd{i+1}', xy=(x_pos + int(num_samples/2), 1.05 ), xycoords=trans, fontsize=12, color='tab:blue')
        # ann = ax[0].annotate(f'n{i+1}', xy=(x_pos + int(3*num_samples/2), 1.05 ), xycoords=trans, fontsize=12, color='tab:orange')
            
    ax[0].set_title('Vector Magnitude (counts)', fontsize=22)
    ax[-1].set_xlabel('24-hour clock [hh]', fontsize=22)
    
    # for i in range(len(ax)):
        # ax[i].set_yticks([y_ini+10,y_end-10], [int(y_ini+10),int(y_end-10)], fontsize=19)
    
    for tick in ax[-1].xaxis.get_major_ticks():
        tick.label1.set_fontsize(19) 
        
    # fig.suptitle(f'Vector Magnitude (counts)\n{group_title}')
        
    if flag_save:
        fig.savefig(path+'vm_b_night.png', bbox_inches='tight')
        
    return 0


def plot_vector_magnitude(list_objs, labels_rec, labels_con, group_title, body_part_title, flag_save, path):

    # list_days=['d1','d2','d3','d4','d5']
    # list_nights=['n1','n2','n3','n4','n5']
        
    rows_number = len(list_objs)
    fig, ax = plt.subplots(nrows=rows_number, ncols=1, figsize=(18, 10), sharex=True, )
    fig.canvas.mpl_connect('key_press_event', on_press)
    fig.canvas.draw()
    
    plt.rcParams.update({'font.size': 19})
    
    # num_samples = 43200 ## 12 hours, a sample every second
    num_samples_night = g_hours_night*3600
    num_samples_day   = g_hours_day*3600
    num_samples_24 = 24*3600
    pad_h = 3600

    y_ini=  -10.0
    y_end=   60.0

    ## show night 3 + a little of day3 and day4 (before and after of night 3, respectively)
    # x_ini = 5*num_samples - int(num_samples/20) 
    # x_end = 6*num_samples + int(num_samples/20) 
    # x_ini = 2*(num_samples_24) + num_samples_day - pad_h 
    x_ini = 2*(num_samples_24) - pad_h 
    x_end = 3*(num_samples_24) + pad_h
    
    # x_text_pos = 0
    # y_text_pos = y_end - 80
    
    for i, obj in enumerate(list_objs):
        
        df = list_objs[i].get_df1()
        
        # trans = ax[i].get_xaxis_transform() # x in data units, y in axes fraction. This is for legend location
        id_d = 1
        id_n = 1

        id_ini = 0
        
        ax[i].vlines(x=[id_ini], ymin=y_ini, ymax=y_end, colors='purple', ls='--', lw=1, label='')
        ## paint each day and each night
        labels_list = df[label_day_night].unique().tolist()
        # print(f'labels: {labels_list}')
        for label in labels_list:
            
            if (label in list_days) or (label in list_nights):
                
                df_label = df[df[label_day_night]== label]
                vma=df_label[label_vma].to_list()
                # ids=df_label.index
                ids=np.arange(id_ini, id_ini+len(df_label))
                # print(f'ids size: {len(ids)}, {len(df_label)}')
                
                if label.startswith('d'):
                    ax[i].plot(ids, vma, color='tab:orange', label='')
                else:
                    ax[i].plot(ids, vma, color='tab:blue', label='')
                
                id_ini=id_ini+len(df_label)
                # vertical line
                ax[i].vlines(x=[id_ini], ymin=y_ini, ymax=y_end, colors='purple', ls='--', lw=1, label='')
                
            else:
                pass
   
    # ## font size labels and ticks every hour
    ## 5 blocks of 24h each (5*24), plus 1 tick at the end -> (5*24)+1
    xticks = np.linspace(0, num_samples_24*5, int(5*24)+1).astype(int)
    
    ticks_labels = np.concatenate((np.arange(g_hen,24), np.arange(0,g_hen)), axis=None)
    
    ticks_labels = [str(x).zfill(2) for x in ticks_labels]
    # print(f'one ticks labels:{ticks_labels}')
    ticks_labels = ticks_labels*5
    # print(f'two ticks labels:{ticks_labels}')
    ticks_labels.append(0)
    # print(f'three ticks labels:{ticks_labels}')
    ax[-1].set_xticks(xticks, ticks_labels, fontsize=20)
    
    for i in np.arange(len(list_objs)):

        ax[i].legend([], title=f'{labels_rec[i]}', alignment='center', loc='upper left', bbox_to_anchor=(1.0, 1.15), ncol=1, fancybox=True, shadow=True,)
        
        ## y scale
        ax[i].set_ylim(y_ini,y_end)
        
        ## x scales
        # ax[i].set_xlim(x_ini,x_end)
            
    ax[0].set_title('Vector Magnitude (counts)', fontsize=22)
    ax[-1].set_xlabel('24-hour clock [hh]', fontsize=22)
    
    for i in range(len(ax)):
        ax[i].set_yticks([y_ini+10,y_end-10], [int(y_ini+10),int(y_end-10)], fontsize=19)
    
    for tick in ax[-1].xaxis.get_major_ticks():
        tick.label1.set_fontsize(19) 
        
    if flag_save:
        fig.savefig(path+'vm_night.png', bbox_inches='tight')
        
    return 0
  

def plot_incl_activity(list_objs, labels_rec, labels_con, group_title, body_part_title, flag_save, path):

    # list_days=['d1','d2','d3','d4','d5']
    # list_nights=['n1','n2','n3','n4','n5']
        
    rows_number = len(list_objs)
    fig, ax = plt.subplots(nrows=rows_number, ncols=1, figsize=(18, 10), sharex=True,)
    fig.canvas.mpl_connect('key_press_event', on_press)
    fig.canvas.draw()
    
    plt.rcParams.update({'font.size': 12})
    
    num_samples = 43200

    y_ini=  -0.2
    y_end=   1.2
    
    # x_text_pos = 0
    # y_text_pos = y_end - 80
    
    for i, obj in enumerate(list_objs):

        df = list_objs[i].get_df1()
        
        # trans = ax[i].get_xaxis_transform() # x in data untis, y in axes fraction
        ## counters initialization
        id_d = 1
        id_n = 1
        id_ini = 0
        
        ax[i].vlines(x=[id_ini], ymin=y_ini, ymax=y_end, colors='purple', ls='--', lw=1, label='')
        ## paint each day and each night
        labels_list = df[label_day_night].unique().tolist()
        print(f'labels: {labels_list}')
        for label in labels_list:
            
            if (label in list_days) or (label in list_nights):
                
                df_label = df[df[label_day_night]== label]
                incl=df_label[label_incl].to_list()
                # ids=df_label.index
                ids=np.arange(id_ini, id_ini+len(df_label))
                # print(f'ids size: {len(ids)}, {len(df_label)}')
                
                if label.startswith('d'):
                    ax[i].plot(ids, incl, color='tab:blue', label='', )
                else:
                    ax[i].plot(ids, incl, color='tab:orange', label='', )
                
                id_ini=id_ini+len(df_label)
                # vertical line
                ax[i].vlines(x=[id_ini], ymin=y_ini, ymax=y_end, colors='purple', ls='--', lw=1, label='')
                
            else:
                pass
    
    
    for i in np.arange(len(list_objs)):
        ##
        ax[i].legend([], title=f'{labels_rec[i]}\n{labels_con[i]}', alignment='center', loc='upper left', bbox_to_anchor=(1.0, 1.15), ncol=1, fancybox=True, shadow=True,)
        
        ## y scale
        ax[i].set_ylim(y_ini,y_end)
        
        # hide xtick values
        ax[i].set_xticklabels([])
        
    # ax[i].set_ylim(y_ini,y_end)
    
    # hide xtick values
    # ax[0].set_xticklabels([])
    # ax[1].set_xticklabels([])
    # ax[2].set_xticklabels([])
    
    ## legend
    # asia = ['B','A','A','A']
    # nl = ['C4','C6','T7','T10']
    # for i in np.arange(4):
        # ax[i].legend([], title=f'P{i+1} - Incl.\nActivity\nAIS: {asia[i]}\nNLI: {nl[i]}', alignment='center', loc='upper left', bbox_to_anchor=(1.0, 1.1), ncol=1, fancybox=True, shadow=True,)
    
    ## annotate
    trans = ax[0].get_xaxis_transform() # x in data untis, y in axes fraction
    list_x_pos = (2*num_samples)*np.arange(5)
    
    for i, x_pos in enumerate(list_x_pos):
        ann = ax[0].annotate(f'd{i+1}', xy=(x_pos + int(num_samples/2), 1.05 ), xycoords=trans, fontsize=12, color='tab:blue')
        ann = ax[0].annotate(f'n{i+1}', xy=(x_pos + int(3*num_samples/2), 1.05 ), xycoords=trans, fontsize=12, color='tab:orange')
            
    ## font size labels and ticks
    xticks = np.linspace(0, num_samples*10, 11).astype(int)
    ax[-1].set_xticks(xticks, (xticks/3600).astype(int), fontsize=12)
    ax[-1].set_xlabel('time [h]', fontsize=12)
    
    for i in range(len(ax)):
        ax[i].set_yticks([0,1], [0,1], fontsize=12)
    
    for tick in ax[-1].xaxis.get_major_ticks():
        tick.label1.set_fontsize(12) 
    
    fig.suptitle(f'Activity Inclinometers {body_part_title}\n{group_title}') 
    
    if flag_save:
        fig.savefig(path+'incl.png', bbox_inches='tight')
        
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


def plot_activitySamples_boxplots(list_objs, selected_label, flag_night, flag_save, path):
    
    rows_number = len(list_objs)
    fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(9, 6),)
    fig.canvas.mpl_connect('key_press_event', on_press)
    fig.canvas.draw()
    
    ## to iterate easily
    axs = np.array(axs)
    axs = axs.reshape(-1)
    # axs = axs.flatten()
    
    # y_ini=  -0.08
    # y_end=   1.08
    
    list_ticks_x =[]
    
    # hen = 7
    # hed = 23
    # hour_0 = 9
    # hour_0 = g_hen
    # list_ticks_x.extend(np.arange(hour_0,24,1)) 
    # list_ticks_x.extend(np.arange(0,hour_0+1,1)) 
    ## add one zero to the left for numbers of one digit
    # list_ticks_x = [str(x).zfill(2) for x in list_ticks_x]
    
    
    label_step = selected_label
    
    # self.time_ini='23:00:00'
    # self.time_end='07:00:00'
    # hen = 7
    # hed = 23
    # hours_night = hen + 24-hed
    # hours_day   = 24-hours_night
    
    
    # print(g_hours_day, g_hours_night)
    
    # length_day=g_hours_day*3600 ## hours in seconds
    # length_night=g_hours_night*3600 ## hours in seconds
    total_days=5
    total_nights=5
    
    # list_days=['d1','d2','d3','d4','d5']
    # list_nights=['n1','n2','n3','n4','n5']
    
    df_p_all = pd.DataFrame()
    
    for i, obj in enumerate(list_objs):
        ## get dataframe 
        df = list_objs[i].get_df1()
        name = list_objs[i].getName()
        
        ## paint each day and each night
        labels_list = df[label_day_night].unique().tolist()
        print(f'labels_list: {labels_list}')
        
        # df_day = pd.DataFrame(columns=list_days)
        # df_night = pd.DataFrame(columns=list_nights)
        
        
        arr_days=[]
        arr_nights=[]
        
        for label in labels_list:
            
            df_label = df[df[label_day_night]== label]
            ## data output stage 2 sliding window algorithms
            arr=df_label[label_step].to_numpy()

            if (label in list_days):
                # arr_days = np.concatenate((arr_days,arr), axis=None) 
                arr_days.append(arr.sum())
                
            elif (label in list_nights):
                # arr_nights = np.concatenate((arr_nights,arr), axis=None)
                arr_nights.append(arr.sum())
                
            else:
                pass
                
        df_day = pd.DataFrame(arr_days, columns=['value'])
        df_night = pd.DataFrame(arr_nights, columns=['value'])
        
        df_day = df_day.assign(period='day')
        df_night = df_night.assign(period='night')
        
        df_p = pd.concat([df_day,df_night], ignore_index=True)
        df_p = df_p.assign(subject=name)
        
        df_p_all = pd.concat([df_p_all,df_p], ignore_index=True)
        
        # print(f'df_day: {df_day}')
        # print(f'df_night: {df_night}')
        # print(f'df_p: {df_p}')
        
        ## add name patient and concat big dataframe for all patients that includes days and nights
        
    # print(f'df_p_all: {df_p_all}')
    
    ## boxplot
    
    # if flag_night:
        # mdf = df_p_all[df_p_all['period']=='night']
    # else:
        # mdf = df_p_all[df_p_all['period']=='day']
        
    
    # mdf = pd.melt(cdf, id_vars=['period'], var_name=['subject'])
    # print(mdf)
    
    dic_pat = {'A006':'P01', 'A021':'P02', 'A022':'P03', 'A025':'P04', 'A028':'P05', 'A037':'P06', 'A039':'P07', 'A044':'P08', 'A003':'P09', 'A023':'P10', 'A026':'P11', 'A018':'P12',}
    
    my_colors = {'day':'#ffb482', 'night':'#a1c9f4'}
    
    title = 'activity samples'
    
    mdf = df_p_all[df_p_all['period']=='day']
    order = mdf.groupby('subject')['value'].median().sort_values().index
    
    plot_boxplot_period(mdf, dic_pat, my_colors, order, axs[0], title)

    mdf = df_p_all[df_p_all['period']=='night']
    plot_boxplot_period(mdf, dic_pat, my_colors, order, axs[1], title)

    size_font = 12
    # ax.tick_params(labelsize=size_font)
    
    # ax.set(ylim=(-0.05, 1.05))
    axs[-1].set_xlabel("Subject",fontsize=size_font)
    # ax.set_ylabel(label_y,fontsize=size_font)
    # ax.tick_params(labelsize=size_font)

    # legend=ax.legend(fontsize=size_font, alignment='center', loc='upper left', bbox_to_anchor=(1.0, 1.0), ncol=1, fancybox=True, shadow=True)
    # legend.remove()
        
    
    if flag_save:
        fig.savefig(path+'boxplot_initial.png', bbox_inches='tight')
    
        
    return 0





def plot_activity_boxplots(list_objs, selected_label, flag_night, flag_save, path):
    
    rows_number = len(list_objs)
    fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(9, 6),)
    fig.canvas.mpl_connect('key_press_event', on_press)
    fig.canvas.draw()
    
    ## to iterate easily
    axs = np.array(axs)
    axs = axs.reshape(-1)
    # axs = axs.flatten()
    
    y_ini=  -0.08
    y_end=   1.08
    
    list_ticks_x =[]
    
    # hen = 7
    # hed = 23
    # hour_0 = 9
    # hour_0 = g_hen
    # list_ticks_x.extend(np.arange(hour_0,24,1)) 
    # list_ticks_x.extend(np.arange(0,hour_0+1,1)) 
    ## add one zero to the left for numbers of one digit
    # list_ticks_x = [str(x).zfill(2) for x in list_ticks_x]
    
    
    label_step = selected_label
    
    # self.time_ini='23:00:00'
    # self.time_end='07:00:00'
    # hen = 7
    # hed = 23
    # hours_night = hen + 24-hed
    # hours_day   = 24-hours_night
    
    
    # print(g_hours_day, g_hours_night)
    
    # length_day=g_hours_day*3600 ## hours in seconds
    # length_night=g_hours_night*3600 ## hours in seconds
    total_days=5
    total_nights=5
    
    # list_days=['d1','d2','d3','d4','d5']
    # list_nights=['n1','n2','n3','n4','n5']

    df_median = pd.DataFrame(columns=['id','median_day','median_night'])

    df_p_all = pd.DataFrame()
    
    for i, obj in enumerate(list_objs):
        ## get dataframe 
        df = list_objs[i].get_df1()
        name = list_objs[i].getName()

        print(f'patient: {name}')
        
        ## paint each day and each night
        labels_list = df[label_day_night].unique().tolist()
        print(f'labels_list: {labels_list}')
        
        # df_day = pd.DataFrame(columns=list_days)
        # df_night = pd.DataFrame(columns=list_nights)
        
        
        arr_days=[]
        arr_nights=[]
        
        for label in labels_list:
            
            df_label = df[df[label_day_night]== label]
            ## data output stage 2 sliding window algorithms
            arr=df_label[label_step].to_numpy()

            if (label in list_days):
                arr_days = np.concatenate((arr_days,arr), axis=None) 
                
            elif (label in list_nights):
                arr_nights = np.concatenate((arr_nights,arr), axis=None)
                
            else:
                pass

        median_days = np.median(arr_days)
        median_nights = np.median(arr_nights)
        print(f'{i} median d: {median_days}')            
        print(f'{i} median n: {median_nights}')

        df_row = pd.DataFrame([[name,median_days,median_nights]],columns=['id','median_day','median_night'])
        df_median = pd.concat([df_median, df_row], ignore_index = True)          
    
        df_day = pd.DataFrame(arr_days, columns=['value'])
        df_night = pd.DataFrame(arr_nights, columns=['value'])
        
        df_day = df_day.assign(period='day')
        df_night = df_night.assign(period='night')
        
        df_p = pd.concat([df_day,df_night], ignore_index=True)
        df_p = df_p.assign(subject=name)
        
        df_p_all = pd.concat([df_p_all,df_p], ignore_index=True)
        
        # print(f'df_day: {df_day}')
        # print(f'df_night: {df_night}')
        # print(f'df_p: {df_p}')
        
        ## add name patient and concat big dataframe for all patients that includes days and nights

    # df_median['median_sum'] = df_median['median_day'] + df_median['median_night']
    # df_sorted = df_median.sort_values('median_sum')
    # id_sorted = df_sorted['id'].tolist()
    # print(f'df sorted:\n{df_sorted}')
    # print(f'id sorted:\n{id_sorted}')

    # df_sorted = df_median.sort_values('median_night')
    df_sorted = df_median.sort_values('median_day')
    id_sorted = df_sorted['id'].tolist()
    print(f'id sorted:\n{id_sorted}')

    order = id_sorted 
    
    # print(f'df_p_all:\n{df_p_all}')
    
    ## boxplot
    
    # if flag_night:
        # mdf = df_p_all[df_p_all['period']=='night']
    # else:
        # mdf = df_p_all[df_p_all['period']=='day']
        
    
    # mdf = pd.melt(cdf, id_vars=['period'], var_name=['subject'])
    # print(mdf)
    
    dic_pat = {'A006':'P01', 'A021':'P02', 'A022':'P03', 'A025':'P04', 'A028':'P05', 'A037':'P06', 'A039':'P07', 'A044':'P08', 'A003':'P09', 'A023':'P10', 'A026':'P11', 'A018':'P12', 'A040':'P15', 'A001':'P15','A002':'P15',}
    
    my_colors = {'day':'#ffb482', 'night':'#a1c9f4'}
    
    title='activity rate'

    flag_order_day = False
    if flag_order_day:
        mdf = df_p_all[df_p_all['period']=='day']
        # order = mdf.groupby('subject')['value'].median().sort_values().index
        # print(f'order: {order}, {type(order)}')
        # order = ['A003', 'A026', 'A044']
        # order = id_sorted

        plot_boxplot_period(mdf, dic_pat, my_colors, order, axs[0],title)

        mdf = df_p_all[df_p_all['period']=='night']
        plot_boxplot_period(mdf, dic_pat, my_colors, order, axs[1],title)
    else:
        mdf = df_p_all[df_p_all['period']=='night']
        
        # order_night = mdf.groupby('subject')['value'].median().sort_values().index
        # values_night = mdf.groupby('subject')['value'].median().sort_values()
        # order = mdf.groupby('subject')['value'].median().sort_values().index
        # print(f'order: {order}, {type(order)}')
        # values = mdf.groupby('subject')['value'].quantile(0.25).sort_values()
        # order = mdf.groupby('subject')['value'].quantile(0.25).sort_values().index
        # print(f'values 0.25: {values}')
        # print(f'order 0.25: {order}')
        # values = mdf.groupby('subject')['value'].quantile(0.5).sort_values()
        # order = mdf.groupby('subject')['value'].quantile(0.5).sort_values().index
        # print(f'values 0.50: {values}')
        # print(f'order 0.50: {order}, {type(order)}')
        # values = mdf.groupby('subject')['value'].quantile(0.75).sort_values()
        # order = mdf.groupby('subject')['value'].quantile(0.75).sort_values().index
        # print(f'values 0.75: {values}')
        # print(f'order 0.75: {order}, {type(order)}')

        # order = ['A039','A025','A044','A028','A003','A006','A021','A023','A037','A022','A018','A026',]
        # order = id_sorted

        plot_boxplot_period(mdf, dic_pat, my_colors, order, axs[1],title)

        mdf = df_p_all[df_p_all['period']=='day']

        # order_day = mdf.groupby('subject')['value'].median().sort_values().index
        # values_day = mdf.groupby('subject')['value'].median().sort_values()

        # print(f'order night:\n{order_night}')
        # print(f'order day:\n{order_day}')
        # print(f'median night: {values_night}')
        # print(f'median day: {values_day}')

        plot_boxplot_period(mdf, dic_pat, my_colors, order, axs[0],title)

        

    size_font = 12
    # ax.tick_params(labelsize=size_font)
    
    axs[0].set(ylim=(-0.05, 1.05))
    axs[1].set(ylim=(-0.05, 1.05))
    axs[-1].set_xlabel("Subject",fontsize=size_font)
    # ax.set_ylabel(label_y,fontsize=size_font)
    # ax.tick_params(labelsize=size_font)

    # legend=ax.legend(fontsize=size_font, alignment='center', loc='upper left', bbox_to_anchor=(1.0, 1.0), ncol=1, fancybox=True, shadow=True)
    # legend.remove()
        
    
    if flag_save:
        fig.savefig(path+'boxplot_all.png', bbox_inches='tight')
    
        
    return 0


def plot_boxplot_period(mdf, dic_pat, my_colors, order, ax, title):
    
    sns.boxplot(data=mdf, x='subject', y="value", hue="period", palette=my_colors,order=order, showfliers = False, medianprops=dict(color="green", alpha=0.7), ax=ax)
    
    # ax.set(ylim=(-0.05, 1.05))
    
    ticks_x = []
    for idx in order:
        print(f'idx: {idx}, {dic_pat[idx]}')
        ticks_x.append(dic_pat[idx])
    
    ax.set_xticklabels(ticks_x)
    
    size_font = 12
    ax.set_xlabel('')
    # ax.set_ylabel('activity rate',fontsize=size_font)
    ax.set_ylabel(title,fontsize=size_font)
    ax.tick_params(labelsize=size_font)
    
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles[1:], labels=labels[1:],fontsize=size_font)
    
    return 0



def plot_cycle_alpha(list_objs, labels_rec, labels_con, selected_label, group_title, body_part_title, flag_save, path):
    
    rows_number = len(list_objs)
    fig, ax = plt.subplots(nrows=rows_number, ncols=1, figsize=(9, 5), sharex=True,)
    fig.canvas.mpl_connect('key_press_event', on_press)
    fig.canvas.draw()
    
    y_ini=  -0.08
    y_end=   1.08
    
    list_ticks_x =[]
    
    # hen = 7
    # hed = 23
    # hour_0 = 9
    hour_0 = g_hen
    list_ticks_x.extend(np.arange(hour_0,24,1)) 
    list_ticks_x.extend(np.arange(0,hour_0+1,1)) 
    ## add one zero to the left for numbers of one digit
    list_ticks_x = [str(x).zfill(2) for x in list_ticks_x]
    
    
    label_step = selected_label
    
    # self.time_ini='23:00:00'
    # self.time_end='07:00:00'
    # hen = 7
    # hed = 23
    # hours_night = hen + 24-hed
    # hours_day   = 24-hours_night
    
    
    # print(g_hours_day, g_hours_night)
    
    length_day=g_hours_day*3600 ## hours in seconds
    length_night=g_hours_night*3600 ## hours in seconds
    total_days=5
    total_nights=5
    
    # list_days=['d1','d2','d3','d4','d5']
    # list_nights=['n1','n2','n3','n4','n5']
    
    
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
        
        color_day='tab:orange'
        color_night='tab:blue'
        
        pattern_day='//'
        pattern_night='..'
        
        # vertical line
        ax[i].vlines(x=[0, length_day, length_day+length_night], ymin=y_ini, ymax=y_end, colors='purple', ls='--', lw=1, label='')
        
        ax[i] = plot_alpha(df_day, 0, length_day, color_day, pattern_day, 'day', ax[i])
        ax[i] = plot_alpha(df_night, length_day, length_night, color_night, pattern_night, 'night', ax[i])
        
        ax[i].set_ylim(y_ini,y_end)
        
        
    # length_x = length_day + length_night
    # length_day / 
    
    ## annotate
    trans = ax[0].get_xaxis_transform() # x in data units, y in axes fraction
    # list_x_pos = (2*num_samples)*np.arange(5)
    ax[0].annotate(f'day', xy=(int(length_day/2), 1.05 ), xycoords=trans, fontsize=12, color='tab:orange')
    ax[0].annotate(f'night', xy=(length_day + int(length_night/2), 1.05 ), xycoords=trans, fontsize=12, color='tab:blue')

    ## legend
    if selected_label == vma_b:
        # signal_label = 'VM'
        # fig.suptitle(f'Activity VM {body_part_title}\n{group_title}')
        # fig.suptitle(f'Mobility estimation from Vector Magnitude (VM) five nights')
        fig.suptitle(f'')
    else:
        # signal_label = 'Incl.'
        fig.suptitle(f'Activity Inclinometers {body_part_title}\n{group_title}')
    # ax[0].legend(loc='upper right', bbox_to_anchor=(1.0, 1.4),fancybox=False, shadow=False, ncol=2)
    # for i in np.arange(4):
        # ax[i].legend([], title=f'P{i+1} - S_out\nS_in: {signal_label}\nAIS: {asia[i]}\nNLI: {nl[i]}', alignment='center', loc='upper left', bbox_to_anchor=(1.0, 1.1), ncol=1, fancybox=True, shadow=True,)
        
    size_font = 12
    
    for i in np.arange(len(list_objs)):
        ##
        ax[i].legend([], title=f'{labels_rec[i]}\n{labels_con[i]}', alignment='center', loc='upper left', bbox_to_anchor=(1.0, 1.15), ncol=1, fancybox=True, shadow=True, title_fontsize=12,)
        
        ## y scale
        ax[i].set_ylim(y_ini,y_end)
        
        # hide xtick values
        ax[i].set_xticklabels([])
        
        # ax.set_xlabel('')
        ax[i].set_ylabel('activity rate',fontsize=size_font)
        ax[i].tick_params(labelsize=size_font)
    
    
    
    x_ticks= b=np.arange(0,(25*3600), 3600)
    ax[-1].set_xticks(x_ticks[::2], list_ticks_x[::2],) 
    
    ## font size labels and ticks
    # xticks = np.linspace(0, num_samples*10, 11).astype(int)
    # ax[-1].set_xticks(xticks, (xticks/3600).astype(int), fontsize=12)
    # ax[-1].set_xlabel('time [h]', fontsize=12)
    
    
    # ax[0].set_ylabel('P1')
    # ax[1].set_ylabel('P2')
    # ax[2].set_ylabel('P3')
    # ax[3].set_ylabel('P4')
    
    
    ax[-1].set_xlabel('24-hour clock [hh]',fontsize=size_font)
   
    # fig.suptitle(title)
    
    
    
    
    if flag_save:
        fig.savefig(path+'24h.png', bbox_inches='tight')
        
    
        
    return 0
    
def plot_alpha(df, start, size, color, pattern, sel_label, ax):
    
    x = np.arange(start,start+size)
    y = df['median'].to_list()
    ymax = df['max'].to_list()
    ymin = df['min'].to_list()
    alpha_fill = 0.3
    
    ax.plot(x, y, color=color)
    # ax.fill_between(x, ymax, ymin, color=color, hatch=pattern, alpha=alpha_fill, label=sel_label)
    ax.fill_between(x, ymax, ymin, color=color, alpha=alpha_fill,)
    
    return ax
    

## boxplots
def plot_boxplots(df_days, df_nights, sel_flag, color_boxes, label_y, labels_rec, labels_con, title, group_title, body_part_title, path_out, flag_save_fig):

    fig, ax = plt.subplots(figsize=(8, 4))
    fig.canvas.mpl_connect('key_press_event', on_press)
    fig.canvas.draw()
    
    data_day = df_days.assign(period='day')
    data_night = df_nights.assign(period='night')
    # cdf = pd.concat([data_day, data_night]) 
    if sel_flag:
        cdf = data_night
    else:
        cdf = data_day
    
    # print(cdf)
    mdf = pd.melt(cdf, id_vars=['period'], var_name=['subject'])
    # print(mdf)
    
    # Find the order
    # my_order = mdf.groupby(by=["subject"])["value"].median().iloc[::-1].index
    order = mdf.groupby('subject')['value'].median().sort_values().index
    print(f'order: {order}')
    
    # list_order=['P08','P01','P04','P07','P05','P02','P09','P10','P06','P03','P12','P11']
    dic_pat = {'A006':'P01', 'A021':'P02', 'A022':'P03', 'A025':'P04', 'A028':'P05', 'A037':'P06', 'A039':'P07', 'A044':'P08', 'A003':'P09', 'A023':'P10', 'A026':'P11', 'A018':'P12',}
    
    # my_colors = {'day':'#8de5a1', 'night':'#a1c9f4'}
    my_colors = {'day':'#ffb482', 'night':'#a1c9f4'}
    
    
    # print(f'pastel: {sns.color_palette("pastel").as_hex()}')
    # ax = sns.boxplot(data=mdf, x='subject', y="value", hue="period", palette="pastel",)
    # ax = sns.boxplot(data=mdf, x='subject', y="value", hue="period", palette="pastel",order=order)
    ax = sns.boxplot(data=mdf, x='subject', y="value", hue="period", palette=my_colors,order=order)
    # ax = sns.boxplot(data=mdf, x='subject', y="value", hue="period", palette="pastel", order=list_order)

    # #########################
    # hatches = ['//','//', '..','..', '//','..', '//','..', '//','..', '//','..', '//','..']
    # for i, patch in enumerate(ax.patches):
        ## print(i)
        # patch.set_hatch(hatches[i])
    # #########################
    
    ax.set(ylim=(-0.05, 1.05))
    # ax.set(xticklabels = (['P1', 'P2', 'P3', 'P4']))
    # ax.set(xticklabels = (['P1', 'P2', 'P3', 'P4']))
    
    ticks_x = []
    for idx in order:
        print(f'idx: {idx}, {dic_pat[idx]}')
        ticks_x.append(dic_pat[idx])
    
    # ticks_x = []
    # for a, b in zip(labels_rec, labels_con):
        # ticks_x.append(f'{a}\n{b}')
    
    ax.set_xticklabels(ticks_x)
    
    size_font = 12
    
    # ax.set_xlabel("ASIA Impairment Scale + (Neurological Level of Injury)",fontsize=size_font)
    ax.set_xlabel("Subject",fontsize=size_font)
    ax.set_ylabel(label_y,fontsize=size_font)
    ax.tick_params(labelsize=size_font)
    
    # fig.suptitle(title)

    # plt.legend(fontsize=size_font, loc='upper center', bbox_to_anchor=(0.5, 1.18), ncol=2, fancybox=True, shadow=False)
    legend=ax.legend(fontsize=size_font, alignment='center', loc='upper left', bbox_to_anchor=(1.0, 1.0), ncol=1, fancybox=True, shadow=True)
    legend.remove()
    
    # ax.legend([], title=f'{labels[i]}', alignment='center', loc='upper left', bbox_to_anchor=(1.0, 1.1), ncol=1, fancybox=True, shadow=True,)
    
    # fig.suptitle(f'Activity {title} {body_part_title}\n{group_title}')
    
    # ax.set_title('Mobility estimation from Vector Magnitude (VM) collected during five nights')
    
        
    if flag_save_fig:
        plt.savefig(path_out+'boxplot.png', bbox_inches='tight')
    
    return 0


def main(args):
    
    path = "../data/projet_officiel/"
    path_out = "../data/projet_officiel/measurements/figures/"
    path_out_2 = "../data/projet_officiel/measurements/tables/"
    
    # files_names=[]
    
    ## ASIA Impairment Scale (AIS)
    ## group from zero (0) to two (2), being 
    ##  0: A y B, 
    ##  1: C, and
    ##  2: D.
    group = args[1] 
    
    ## Actigraph's location (body_part)
    ## c: chest, and
    ## t: thigh.
    body_part = args[2] 
    
    if group == '0':
        files_names=['A006', 'A021', 'A022', 'A025', 'A028', 'A037', 'A039', 'A044', 'A003', 'A023', 'A026', 'A018',]
        prefix_one = 'AB_'
        group_title = 'AIS : A and B'
        ## Neurological Level of Injury
        list_nli_rec=['B (C4)', 'B (C4)', 'B (C4)', 'B (C5)', 'A (C5)', 'B (C5)', 'A (C5)', 'A (C5)', 'A (C6)', 'A (C6)', 'A (T7)', 'A (T10)',]
        list_nli_con=['B (C4)', 'B (C4)', 'D (C4)', 'B (C4)', 'A (C5)', 'D (C5)', 'A (C5)', 'Maybe C', 'A (C6)', 'A (C6)', 'A (T7)', 'C (T10)',]
        list_pi=[]
        ## number of days (and nights) of recorded values
        # list_records = [5, 5, 5, 5, 5, 5, 5, 5, 5, 2, 1, 4, 5, 5,]
    elif group == '1':
        files_names=['A019', 'A043', 'A005', 'A009', 'A014', 'A035', 'A041', 'A011',]
        prefix_one = 'C_'
        group_title = 'AIS : C'
        ## Neurological Level of Injury
        list_nli_rec=['C (C1)', 'C (C2)', 'C (C3)', 'C (C4)', 'C (C4)', 'C (C4)', 'C (C5)', 'C (D6)', ]
        list_nli_con=['D (C1)', 'C (C2)', 'D (C3)', 'C (C4)', 'C (C4)', 'C (C4)', 'D (C5)', 'C (D6)', ]
        list_pi=[]
    elif group == '2':
        files_names=['A024', 'A007', 'A010', 'A013', 'A016', 'A031', 'A036', 'A002',]
        prefix_one = 'D_'
        group_title = 'AIS : D'
        ## Neurological Level of Injury
        list_nli_rec=['D (C3)', 'D (C4)', 'D (C4)', 'D (C4)', 'D (C5)', 'D (C5)', 'D (C5)', 'D (T11)']
        list_nli_con=['D (C3)', 'D (C4)', 'D (C4)', 'D (C4)', 'D (C5)', 'D (C5)', 'D (C5)', 'D (T11)']
        list_pi=[]
        
    elif group == '3':
        files_names=['A001', 'A004', 'A015', 'A027', 'A033', 'A038', 'A042',]
        prefix_one = 'SQC_'
        group_title = 'AIS : SQC'
        list_nli_rec=['SQC', 'SQC', 'SQC', 'SQC', 'CCS C2', 'SQC', 'SQC',]
        list_nli_con=['SQC', 'SQC', 'SQC', 'SQC', 'CCS C2', 'SQC', 'SQC',]
        list_pi=[]
    elif group == '4':
        files_names=['A019', 'A035', 'A020', 'A016',]
        prefix_one = 'before_'
        group_title = 'Pressure injured patients\nBefore Recruitment'
        list_nli_rec=['C (C1)', 'C (C4)', 'D (C4)', 'D (C5)',]
        list_nli_con=['D (C1)', 'C (C4)', 'D (C4)', 'D (C5)',]
        list_pi=[]
    elif group == '5':
        files_names=['A023', 'A019', 'A014', 'A015',]
        prefix_one = 'during_'
        group_title = 'Pressure injured patients\nDuring Recruitment'
        list_nli_rec=['A (C6)', 'C (C1)', 'C (C4)', 'SQC',]
        list_nli_con=['A (C6)', 'D (C1)', 'C (C4)', 'SQC',]
        list_pi=[]
    elif group == '6':
        files_names=['A006', 'A039', 'A040', 'A005' , 'A041', 'A001', 'A015', 'A033',]
        prefix_one = 'after_'
        group_title = 'Pressure injured patients\nAfter Recruitment'
        list_nli_rec=['B (C4)', 'A (C5)', 'A (T4)', 'C (C3)', 'C (C5)', 'SQC', 'SQC', 'CCS (C2)',]
        list_nli_con=['B (C4)', 'A (C5)', 'A (T5)', 'D (C3)', 'D (C5)', 'SQC', 'SQC', 'CCS (C2)',]
        list_pi=[]
    elif group == '7':
        files_names=['A006', 'A021', 'A022', 'A025', 'A028', 'A037', 'A039', 'A044', 'A003', 'A023', 'A026', 'A018',]
        prefix_one = 'AB_'
        group_title = 'AIS : A and B'
        ## Neurological Level of Injury
        list_nli_rec=['P01', 'P02', 'P03', 'P04', 'P05', 'P06', 'P07', 'P08', 'P09', 'P10', 'P11', 'P12',]
        list_nli_con=['','','','','','','','','','','','','','',]
        dic_pat = {'A006':'P01', 'A021':'P02', 'A022':'P03', 'A025':'P04', 'A028':'P05', 'A037':'P06', 'A039':'P07', 'A044':'P08', 'A003':'P09', 'A023':'P10', 'A026':'P11', 'A018':'P12',}
        list_pi=[]
    elif group == '8':
        files_names=['A044', 'A003', 'A026']
        prefix_one = 'AB_'
        group_title = 'AIS : A and B'
        ## Neurological Level of Injury
        list_nli_rec=['P08', 'P09', 'P11',]
        list_nli_con=['','','',]
        list_pi=[]    
    elif group == '9':
        files_names=['A040','A040',]
        prefix_one = 'AB_'
        group_title = 'AIS : A and B'
        ## Neurological Level of Injury
        list_nli_rec=['P15','P15',]
        list_nli_con=['','',]
        list_pi=[]
    elif group == '10':
        prefix_one = 'AB_'
        list_nli_rec=['P08', 'P09', 'P11',]
        list_nli_con=['','','',]
        group_title = 'AIS : A and B'
        min=1
        max=2
        list_files = np.arange(min,max+1,1).tolist()
        files_names= ['A'+str(a).zfill(3) for a in list_files]
        print(f'file names: {files_names}')
     
    else:
        print(f'selected group out of the list (0,1,2). ')
        return 0

    ## actigraphy data collected from the patient's chest or thigh
    if body_part == 'c':
        files_list = [ name+'_chest.csv' for name in files_names]
        prefix_two='chest_'
        body_part_title = 'Chest'
    elif body_part == 't':
        files_list = [ name+'_thigh.csv' for name in files_names]
        prefix_two='thigh_'
        body_part_title = 'Thigh'
    else:
        print(f'selected one body part out of the list=[c,t], being c for chest, or t for thigh.')
        return 0
        
    list_objs = [[]]*len(files_list)
    
    for i,filename in enumerate(files_list):
        try:
            print(f'reading file: {filename}... ', end='')
            # create object class
            list_objs[i] = Activity_Measurements(files_names[i])
            list_objs[i].openFile(path, filename)
            print(f'done.')
            
        except ValueError:
            print(f'Problem reading the file {filename}.')
    
    prefix_name = prefix_one+prefix_two
    # ##########################        
    # ## plot Vector Magnitude
    # flag_save = False
    # plot_vector_magnitude(list_objs, list_nli_rec, list_nli_con, group_title, body_part_title, flag_save, path_out+prefix_name)
    # ##########################

    ## parameters
    win_a =   10 # 10 minutes
    win_b =  120 # 120 minutes
    
    flag_continue = True
    # flag_continue = False
    
    if flag_continue:
    
        for i, obj in enumerate(list_objs):
            
            print(f'processing {obj.filename}... ', end='')
            fn = files_names[i]
            ## activity rates calculation
            obj.vma_processing(win_a, win_b)
            print('done.')

            ## plot activity counts and activity rates
            obj.plot_activity_rates()

            # ## calculate activity rates per days and nights
            # obj.median_days_nights()
            # df_d_median = obj.getMedian_days()
            # df_n_median = obj.getMedian_nights()

            # print(f'{df_d_median}')
            # print(f'{df_n_median}')

        
        # #############################
        # flag_save = False
        # ## plots 24 h max. min. and median activity rate
        # plot_cycle_alpha(list_objs, list_nli_rec, list_nli_con, vma_b,  group_title, body_part_title, flag_save, path_out+prefix_name+'vm7_')
        # #############################
        # #############################
        # flag_save = False
        # flag_night=True
        # ## plot cumulative activity rates days and nights
        # plot_activity_boxplots(list_objs, vma_b, flag_night, flag_save, path_out+prefix_name+'box_plot_sorted_by_days')
        # #############################
        
    else:
        pass

    plt.show()
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
