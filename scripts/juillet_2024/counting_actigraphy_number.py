#!/usr/bin/env python
# -*- coding: utf-8 -*-

from class_counting_Islam import Counting_Actigraphy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# # global instances
# obj_chest=Counting_Actigraphy('chest')
# obj_thigh=Counting_Actigraphy('thigh')

vec_mag  ='Vector Magnitude'
incl_off ='Inclinometer Off'
incl_sta ='Inclinometer Standing'
incl_sit ='Inclinometer Sitting'
incl_lyi ='Inclinometer Lying'

label_day_night = 'day_night'
vma_b='vma_b'

label_time = ' Time'
label_date = 'Date'


def activityDataFrame(list_data, list_name_cols):
    
    arr_activity = np.array(list_data)
    arr_activity = np.transpose(arr_activity)
    list_nights = np.arange(1,len(arr_activity)+1)
    
    df_activity = pd.DataFrame(data = arr_activity,
                              index = list_nights,
                             columns=list_name_cols)

    df_activity.index.name = 'night'
    
    return df_activity


def activity_rates_incl_off(obj_chest, obj_thigh):

    df_chest = obj_chest.get_df_inclinometers()
    df_thigh = obj_thigh.get_df_inclinometers()

    ## all dates in one list
    dates_list = df_chest[label_date].unique().tolist()
    print(f'dates chest: {dates_list}')
    dates_list = df_thigh[label_date].unique().tolist()
    print(f'dates thigh: {dates_list}')

    return 0

############################
## plotting functions

def on_press(event):
    # print('press', event.key)
    sys.stdout.flush()
    
    if event.key == 'x':
        plt.close('all')
    else:
        pass
    return 0

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
    
    path = "../../data/projet_officiel/"
    path_out = "../../data/projet_officiel/counting/"
    
    # prefix = 'A010'
    prefix = args[1]
    arg_2 = args[2]

    files_list=[prefix+'_chest.csv', prefix+'_thigh.csv']
    files_list_out_rep=[prefix+'_chest_repositioning', prefix+'_thigh_repositioning']
    files_list_out_act=[prefix+'_chest_activity', prefix+'_thigh_activity']
    files_list_out_mov=[prefix+'_chest_numberMov', prefix+'_thigh_numberMov']
    
    dict_df_rep_chest = {}
    dict_df_rep_thigh = {}
    
    # print('files_list: ', files_list)
    
    flag_read=False

    # 
    obj_chest=Counting_Actigraphy(prefix+' chest')
    obj_thigh=Counting_Actigraphy(prefix+' thigh')
    
    try:
        obj_chest.openFile(path, files_list[0])
        obj_thigh.openFile(path, files_list[1])
        flag_read=True
    except ValueError:
        print(f'Problem reading the file {prefix}.')
        flag_read=False

    if flag_read==True:
        print('reading success!')
        
        #################
        ## repositioning start
        list_repos_chest=[]
        list_repos_thigh=[]
        list_names_repos=[]
        
        ############################
        ## repositioning estimation
        print(f'repositioning estimation')
        # win_size_minutes = 10.0 # minutes
        win_size_minutes = float(arg_2) # minutes
        print(f'window size: {win_size_minutes}')
        obj_chest.inclinometers_sliding_window(win_size_minutes)
        obj_thigh.inclinometers_sliding_window(win_size_minutes)

        ## plot inclinometers before and after the "inclinometers_sliding_window" function for comparison
        # x_min = 124000
        # x_max = x_min + 3600
        x_min = 0
        x_max = x_min + 3600*24*7
        obj_chest.plotActigraphy(0,x_min,x_max)
        # obj_chest.plotActigraphy(1,x_min,x_max)
        # plt.show()
        # return 0
        
        obj_chest.nightCounts()
        obj_thigh.nightCounts()

        df_counts_chest=obj_chest.getNightCounts()
        df_counts_thigh=obj_thigh.getNightCounts()
        
        ## write csv files 
        df_counts_chest.to_csv(path_out+files_list_out_rep[0]+arg_2+'.csv', index=False)
        df_counts_thigh.to_csv(path_out+files_list_out_rep[1]+arg_2+'.csv', index=False)
        ## repositioning estimation
        ############################

        #############################
        ## vector magnitude activity        
        min_value=1 ## counts
        win_size=float(arg_2) ## min
        min_samples_window =1 ## number of samples to validated activity
        
        list_activity_chest = []
        list_activity_thigh = []
        list_mov_conts_chest = []
        list_mov_conts_thigh = []
        list_name_cols = []

        print(f'window size: {win_size}')
        list_mov_grade_chest, list_mov_counts_chest = obj_chest.vecMagCounting(min_value, win_size, min_samples_window)
        list_mov_grade_thigh, list_mov_counts_thigh = obj_thigh.vecMagCounting(min_value, win_size, min_samples_window)
        
        list_activity_chest.append(list_mov_grade_chest)
        list_activity_thigh.append(list_mov_grade_thigh)
        
        list_mov_conts_chest.append(list_mov_counts_chest)
        list_mov_conts_thigh.append(list_mov_counts_thigh)
        
        list_name_cols.append(str(win_size)+'(min)')
            
        df_activity_chest = activityDataFrame(list_activity_chest, list_name_cols)
        df_activity_thigh = activityDataFrame(list_activity_thigh, list_name_cols)
        
        df_mov_counts_chest = activityDataFrame(list_mov_conts_chest, list_name_cols)
        df_mov_counts_thigh = activityDataFrame(list_mov_conts_thigh, list_name_cols)
        
        # saving data
        df_activity_chest.to_csv(path_out+files_list_out_act[0]+arg_2+'.csv')
        df_activity_thigh.to_csv(path_out+files_list_out_act[1]+arg_2+'.csv')
        
        df_mov_counts_chest.to_csv(path_out+files_list_out_mov[0]+arg_2+'.csv')
        df_mov_counts_thigh.to_csv(path_out+files_list_out_mov[1]+arg_2+'.csv')
        ## vector magnitude activity
        #############################

        #############################
        ## activity rates
        win_a =   10 # minutes
        win_b =  180 # minutes

        obj_chest.vma_processing(win_a, win_b)
        obj_thigh.vma_processing(win_a, win_b)

        ## plot activity rates chest and thigh
        # id_objs = [obj_chest, obj_thigh]
        # plot_activity_rates(id_objs)
        # plt.show()
        ## activity rates
        #############################

        #############################
        ## activity rates when Inclinometer_off is ON (when the patients are lying in their back)
        activity_rates_incl_off(obj_chest, obj_thigh)

        ## activity rates when Inclinometer_off is ON (when the patients are lying in their back)
        #############################
        


        
        # # ## plot position changing
        # obj_chest.plotDWTInclinometers()
        # obj_thigh.plotDWTInclinometers()
  
        # # ## plot vector magnitude and inclinometers; all days and nights (original data)
        # obj_chest.plotActigraphy()
        # obj_thigh.plotActigraphy()
                
        # plt.ion()
        # plt.show(block=True)
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
