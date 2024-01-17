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


def on_press(event):
    # print('press', event.key)
    sys.stdout.flush()
    
    if event.key == 'x':
        plt.close('all')
    else:
        pass
    return 0

def plot_vector_magnitude(list_objs, flag_save, path):

    # list_days=['d1','d2','d3','d4','d5']
    # list_nights=['n1','n2','n3','n4','n5']
        
    rows_number = len(list_objs)
    fig, ax = plt.subplots(nrows=rows_number, ncols=1, figsize=(12, 6), sharex=True, )
    fig.canvas.mpl_connect('key_press_event', on_press)
    fig.canvas.draw()
    
    plt.rcParams.update({'font.size': 12})
    
    num_samples = 43200 ## 12 hours, a sample every second

    y_ini=  -10.0
    y_end=   60.0
    
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
                    ax[i].plot(ids, vma, color='tab:blue', label='')
                else:
                    ax[i].plot(ids, vma, color='tab:orange', label='')
                
                id_ini=id_ini+len(df_label)
                # vertical line
                ax[i].vlines(x=[id_ini], ymin=y_ini, ymax=y_end, colors='purple', ls='--', lw=1, label='')
                
            else:
                pass
        
        ax[i].set_ylim(y_ini,y_end)
        
        # hide xtick values
        ax[0].set_xticklabels([])
        ax[1].set_xticklabels([])
        ax[2].set_xticklabels([])
        
        ## legend
        # asia = ['B','A','A','A']
        # nl = ['C4','C6','T7','T10']
        for i in np.arange(4):
            ax[i].legend([], title=f'P{i+1} - VM\n(counts)\nAIS: {asia[i]}\nNLI: {nl[i]}', alignment='center', loc='upper left', bbox_to_anchor=(1.0, 1.1), ncol=1, fancybox=True, shadow=True,)
        
        ## annotate
        trans = ax[0].get_xaxis_transform() # x in data units, y in axes fraction
        list_x_pos = (2*num_samples)*np.arange(5)
        
        for i, x_pos in enumerate(list_x_pos):
            ann = ax[0].annotate(f'd{i+1}', xy=(x_pos + int(num_samples/2), 1.05 ), xycoords=trans, fontsize=12, color='tab:blue')
            ann = ax[0].annotate(f'n{i+1}', xy=(x_pos + int(3*num_samples/2), 1.05 ), xycoords=trans, fontsize=12, color='tab:orange')
                
        ## font size labels and ticks
        xticks = np.linspace(0, num_samples*10, 11).astype(int)
        ax[-1].set_xticks(xticks, (xticks/3600).astype(int), fontsize=12)
        ax[-1].set_xlabel('time [h]', fontsize=12)
        
        for i in range(len(ax)):
            ax[i].set_yticks([y_ini+10,y_end-10], [int(y_ini+10),int(y_end-10)], fontsize=12)
        
        for tick in ax[-1].xaxis.get_major_ticks():
            tick.label1.set_fontsize(12) 
        
    if flag_save:
        fig.savefig(path+'vm.png', bbox_inches='tight')
        
    return 0
  

def plot_incl_activity(list_objs, flag_save, path):

    # list_days=['d1','d2','d3','d4','d5']
    # list_nights=['n1','n2','n3','n4','n5']
        
    rows_number = len(list_objs)
    fig, ax = plt.subplots(nrows=rows_number, ncols=1, figsize=(12, 6), sharex=True,)
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
        
        ax[i].set_ylim(y_ini,y_end)
        
        # hide xtick values
        ax[0].set_xticklabels([])
        ax[1].set_xticklabels([])
        ax[2].set_xticklabels([])
        
        ## legend
        # asia = ['B','A','A','A']
        # nl = ['C4','C6','T7','T10']
        for i in np.arange(4):
            ax[i].legend([], title=f'P{i+1} - Incl.\nActivity\nAIS: {asia[i]}\nNLI: {nl[i]}', alignment='center', loc='upper left', bbox_to_anchor=(1.0, 1.1), ncol=1, fancybox=True, shadow=True,)
        
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


def plot_cycle_alpha(list_objs, selected_label, title, flag_save, path):
    
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
    ## add one zero to the left for numbers of one digit
    list_ticks_x = [str(x).zfill(2) for x in list_ticks_x]
    
    
    label_step = selected_label
    
    length_day=12*3600 ## 12 hours in seconds
    length_night=12*3600 ## 12 hours in seconds
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
        
        color_day='tab:blue'
        color_night='tab:orange'
        
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
    ax[0].annotate(f'day', xy=(int(length_day/2), 1.05 ), xycoords=trans, fontsize=12, color='tab:blue')
    ax[0].annotate(f'night', xy=(length_day + int(length_night/2), 1.05 ), xycoords=trans, fontsize=12, color='tab:orange')

    ## legend
    if selected_label == vma_b:
        signal_label = 'VM'
    else:
        signal_label = 'Incl.'
    # ax[0].legend(loc='upper right', bbox_to_anchor=(1.0, 1.4),fancybox=False, shadow=False, ncol=2)
    for i in np.arange(4):
        ax[i].legend([], title=f'P{i+1} - S_out\nS_in: {signal_label}\nAIS: {asia[i]}\nNLI: {nl[i]}', alignment='center', loc='upper left', bbox_to_anchor=(1.0, 1.1), ncol=1, fancybox=True, shadow=True,)
    
    
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
    
    ax[-1].set_xlabel('24-hour clock [hh]')
   
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
def plot_boxplots(df_days, df_nights, label_y, title, path_out, flag_save_fig):

    fig, ax = plt.subplots()
    fig.canvas.mpl_connect('key_press_event', on_press)
    fig.canvas.draw()
    
    data_day = df_days.assign(period='day')
    data_night = df_nights.assign(period='night')
    cdf = pd.concat([data_day, data_night]) 
    # print(cdf)
    mdf = pd.melt(cdf, id_vars=['period'], var_name=['subject'])
    # print(mdf)
    
    ax = sns.boxplot(data=mdf, x='subject', y="value", hue="period", palette="pastel")

    #########################
    hatches = ['//','//', '..','..', '//','..', '//','..', '//','..', '//','..', '//','..']
    for i, patch in enumerate(ax.patches):
        # print(i)
        patch.set_hatch(hatches[i])
    #########################
    
    ax.set(ylim=(-0.05, 1.05))
    ax.set(xticklabels = (['P1', 'P2', 'P3', 'P4']))
    
    size_font = 20
    
    ax.set_xlabel("subject",fontsize=size_font)
    ax.set_ylabel(label_y,fontsize=size_font)
    ax.tick_params(labelsize=size_font)
    
    # fig.suptitle(title)

    plt.legend(fontsize=size_font, loc='upper center', bbox_to_anchor=(0.5, 1.18), ncol=2, fancybox=True, shadow=False)
    
    if flag_save_fig:
        plt.savefig(path_out+'boxplot.png', bbox_inches='tight')
    
    return 0


def main(args):
    
    path = "../data/projet_officiel/"
    path_out = "../data/projet_officiel/measurements/figures/"

    # prefix patient id. Example: A006
    # prefix = args[1]
    # window size (in minutes) for sliding window algorithm. Example: 10 
    # sw_val = int(args[2])
    
    limb = args[1]
    
    if limb == 'c':
        files_list=['A006_chest.csv', 'A003_chest.csv', 'A026_chest.csv', 'A018_chest.csv',]
        prefix_name='chest_'
    else:
        files_list=['A006_thigh.csv', 'A003_thigh.csv', 'A026_thigh.csv', 'A018_thigh.csv',]
        prefix_name='thigh_'
        
    files_names=['A006', 'A003', 'A026', 'A018',]
    
    
    
    list_objs = [[]]*len(files_list)
    
    for i,filename in enumerate(files_list):
        try:
            print(f'reading file: {filename}... ', end='')
            # create object class
            list_objs[i] = Activity_Measurements()
            list_objs[i].openFile(path, filename)
            print(f'done.')
            
        except ValueError:
            print(f'Problem reading the file {filename}.')
    
    ###########################        
    ## plot Vector Magnitude
    flag_save = True
    plot_vector_magnitude(list_objs, flag_save, path_out+prefix_name)
    ###########################
    
    df_vma_days = pd.DataFrame(columns=files_names)
    df_vma_nights = pd.DataFrame(columns=files_names)
    
    df_inc_days = pd.DataFrame(columns=files_names)
    df_inc_nights = pd.DataFrame(columns=files_names)
    
    ## parameters
    win_a =  10 # 10 minutes
    win_b = 120 # 120 minutes
    
    flag_filter=False
    # self.df_days  = pd.DataFrame(columns  =['sample_size', 'vma_mean', 'inc_mean'])
    # self.df_nights= pd.DataFrame(columns=['sample_size', 'vma_mean', 'inc_mean'])
    
    for i, obj in enumerate(list_objs):
        
        print(f'processing {obj.filename}... ', end='')
        fn = files_names[i]
        
        obj.vma_processing(win_a, win_b)
        obj.inc_processing(win_a, win_b, flag_filter)
        
        ## calculate mean value for 12h periods of days and nights for vector magnitude and inclinometers
        obj.means_days_nights()
        
        ## read data -> boxplots
        df_days = obj.getMeansDays()
        df_nights = obj.getMeansNights()
        
        #### vma_mean days from index 1 to index 5
        df_vma_days[fn] = df_days.iloc[1:6]['vma_mean'].to_list()
        #### vma_mean nights from index 1 to index 5
        df_vma_nights[fn] = df_nights.iloc[1:6]['vma_mean'].to_list()
        #### inc_mean days from index 1 to index 5
        df_inc_days[fn] = df_days.iloc[1:6]['inc_mean'].to_list()
        #### inc_mean nights from index 1 to index 5
        df_inc_nights[fn] = df_nights.iloc[1:6]['inc_mean'].to_list()
        
        print('done.')

    ###########################
    ## inclinometers activity: posture changing
    flag_save = True
    plot_incl_activity(list_objs, flag_save, path_out+prefix_name)
    ###########################
    
    ## plot results processing
    # plot_vma_step(list_objs, 1)
    # plot_vma_step(list_objs, 2)
    # plot_vma_cycle(list_objs)
    #############################
    flag_save = True
    plot_cycle_alpha(list_objs, vma_b, 'Vector Magnitude Activity', flag_save, path_out+prefix_name+'vm_')
    plot_cycle_alpha(list_objs, inc_b, 'Inclinometers Activity', flag_save, path_out+prefix_name+'incl_')
    #############################
    # list_objs[0].plot_Inclinometers()
    # list_objs[0].plot_Inclinometers_results()
    
    
    ## plot boxplots
    # files_names=['A006', 'A003', 'A026', 'A018',]
    flag_boxplots = True
    
    if flag_boxplots:
        flag_save_fig=True
        title = 'Vector Magnitude'
        label_y = "VM activity rate"
        plot_boxplots(df_vma_days, df_vma_nights, label_y, title, path_out+prefix_name+'vm_', flag_save_fig)
        
        flag_save_fig=True
        title = 'Inclinometers'
        # if flag_filter:
            # label_y = "posture changing rate\n(filter on)"
        # else:
            # label_y = "posture changing rate\n(filter off)"
        label_y = "Incl. activity rate"
        plot_boxplots(df_inc_days, df_inc_nights, label_y, title, path_out+prefix_name+'incl_', flag_save_fig)
    
    # for i,filename in enumerate(files_names):
        # df_days = pd.read_csv(fn_days)  
        # df_nights = pd.read_csv(fn_nights)  
    

    plt.show()
    
    return 0
    
    

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
