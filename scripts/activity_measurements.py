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
    return 0

def plot_vector_magnitude(list_objs, flag_save, path):

    list_days=['d1','d2','d3','d4','d5']
    list_nights=['n1','n2','n3','n4','n5']
        
    rows_number = len(list_objs)
    fig, ax = plt.subplots(nrows=rows_number, ncols=1, figsize=(12, 6),)
    fig.canvas.mpl_connect('key_press_event', on_press)
    fig.canvas.draw()
    
    plt.rcParams.update({'font.size': 12})
    # plt.rc('axes', titlesize=12)     # fontsize of the axes title
    # plt.rc('axes', labelsize=12)    # fontsize of the x and y labels
    # plt.rc('xtick', labelsize=12)    # fontsize of the tick labels
    # plt.rc('ytick', labelsize=12)    # fontsize of the tick labels
    
    # fig2, ax2 = plt.subplots(nrows=rows_number, ncols=1, figsize=(12, 6),)
    # fig2.canvas.mpl_connect('key_press_event', on_press)
    # fig2.canvas.draw()

    num_samples = 43200

    y_ini=  -10.0
    y_end=  380.0
    
    x_text_pos = 0
    y_text_pos = y_end - 80
    
    for i, obj in enumerate(list_objs):

        df = list_objs[i].get_df1()
        
        trans = ax[i].get_xaxis_transform() # x in data untis, y in axes fraction
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
                vma=df_label[label_vma].to_list()
                # ids=df_label.index
                ids=np.arange(id_ini, id_ini+len(df_label))
                print(f'ids size: {len(ids)}, {len(df_label)}')
                
                if label.startswith('d'):
                    ax[i].plot(ids, vma, color='tab:blue')
                    # annotation
                    # x_text_pos = ids[int(len(ids)/2)]
                    # ax[i].annotate(f'd{id_d}', xy =(x_text_pos, y_text_pos),) 
                    # ann = ax[i].annotate(f'd{id_d}', xy=(x_text_pos, y_text_pos), xycoords=trans)    
                    # id_d+=1 
                else:
                    ax[i].plot(ids, vma, color='tab:orange')
                    # annotation
                    # x_text_pos = ids[int(len(ids)/2)]
                    # ax[i].annotate(f'n{id_n}', xy =(x_text_pos, y_text_pos),)  
                    # ann = ax[i].annotate(f'd{id_n}', xy=(x_text_pos, y_text_pos), xycoords=trans)    
                    # id_n+=1 
                
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
        
        # ax[0].set_ylabel('counts')
        # ax[1].set_ylabel('counts')
        # ax[2].set_ylabel('counts')
        # ax[3].set_ylabel('counts')
        
        # legend
        asia = ['B','A','A','A']
        nl = ['C4','C6','T7','T10']
        for i in np.arange(4):
            ax[i].legend(title=f'P{i+1} - VM\n(counts)\nAIS: {asia[i]}\nNLI: {nl[i]}', alignment='center', loc='upper left', bbox_to_anchor=(1.0, 1.1), ncol=1, fancybox=True, shadow=True)
        
        ## annotate
        trans = ax[0].get_xaxis_transform() # x in data untis, y in axes fraction
        list_x_pos = (2*num_samples)*np.arange(5)
        # ann = ax[0].annotate('MgII', xy=(2000, 1.05 ), xycoords=trans)
        for i, x_pos in enumerate(list_x_pos):
            ann = ax[0].annotate(f'd{i+1}', xy=(x_pos + int(num_samples/2), 1.05 ), xycoords=trans, fontsize=12, color='tab:blue')
            ann = ax[0].annotate(f'n{i+1}', xy=(x_pos + int(3*num_samples/2), 1.05 ), xycoords=trans, fontsize=12, color='tab:orange')
                

        ## font size labels and ticks
        ax[-1].set_xlabel('samples', fontsize=12)
        
        for i in range(len(ax)):
            ax[i].set_yticks([0,200], [0,200], fontsize=12)
        
        for tick in ax[-1].xaxis.get_major_ticks():
            tick.label.set_fontsize(12) 
        
        
        
        # multiple lines all full height
        
        # sns.lineplot(data=df, x=df.index, y=label_vma, hue=label_binary_day_night, ax=ax[i])
        # ax[i].get_legend().set_visible(False)
        
        # arr_vm = list_objs[i].getVectorMagnitude()
        # ax2[i].plot(arr_vm)
        # ax2[i].set_ylim(y_ini,y_end)
        
    if flag_save:
        fig.savefig(path+'vm_all.png', bbox_inches='tight')
        
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
    
    
    ax[0].set_ylabel('P1')
    ax[1].set_ylabel('P2')
    ax[2].set_ylabel('P3')
    ax[3].set_ylabel('P4')
    
    ax[-1].set_xlabel('time(h)')
   
    fig.suptitle(title)
    
    if flag_save:
        fig.savefig(path+'alpha.png', bbox_inches='tight')
        
    
        
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
        plt.savefig(path_out+'filter.png', bbox_inches='tight')
    
    return 0


def main(args):
    
    path = "../data/projet_officiel/"
    path_out = "../data/projet_officiel/measurements/figures/"

    # prefix patient id. Example: A006
    # prefix = args[1]
    # window size (in minutes) for sliding window algorithm. Example: 10 
    # sw_val = int(args[2])
    
    files_list=['A006_chest.csv', 'A003_chest.csv', 'A026_chest.csv', 'A018_chest.csv',]
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
            
    ## plot Vector Magnitude
    flag_save = False
    # plot_vector_magnitude(list_objs, flag_save, path_out)
    
    df_vma_days = pd.DataFrame(columns=files_names)
    df_vma_nights = pd.DataFrame(columns=files_names)
    
    df_inc_days = pd.DataFrame(columns=files_names)
    df_inc_nights = pd.DataFrame(columns=files_names)
    
    ## parameters
    win_a =  10 # 10 minutes
    win_b = 120 # 120 minutes
    
    flag_filter=True
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

    ## plot results processing
    # plot_vma_step(list_objs, 1)
    # plot_vma_step(list_objs, 2)
    # plot_vma_cycle(list_objs)
    flag_save = True
    # plot_cycle_alpha(list_objs, vma_b, 'Vector Magnitude Activity', flag_save, path_out+'vm_')
    plot_cycle_alpha(list_objs, inc_b, 'Inclinometers Activity, Filter On', flag_save, path_out+'inc_on_')
    # list_objs[0].plot_Inclinometers()
    # list_objs[0].plot_Inclinometers_results()
    
    
    ## plot boxplots
    # files_names=['A006', 'A003', 'A026', 'A018',]
    flag_boxplots = False
    
    if flag_boxplots:
        flag_save_fig=False
        title = 'Vector Magnitude'
        label_y = "activity rate"
        plot_boxplots(df_vma_days, df_vma_nights, label_y, title, path_out+'vma_rate_', flag_save_fig)
        
        flag_save_fig=False
        title = 'Inclinometers'
        if flag_filter:
            label_y = "posture changing rate\nfilter on"
        else:
            label_y = "posture changing rate\nfilter off"
        plot_boxplots(df_inc_days, df_inc_nights, label_y, title, path_out+'inc_rate_', flag_save_fig)
    
    # for i,filename in enumerate(files_names):
        # df_days = pd.read_csv(fn_days)  
        # df_nights = pd.read_csv(fn_nights)  
    

    plt.show()
    
    return 0
    
    

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
