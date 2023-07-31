#!/usr/bin/env python
# -*- coding: utf-8 -*-

from class_counting_Islam import Counting_Actigraphy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# global instances
obj_chest=Counting_Actigraphy()
obj_thigh=Counting_Actigraphy()

vec_mag  ='Vector Magnitude'
incl_off ='Inclinometer Off'
incl_sta ='Inclinometer Standing'
incl_sit ='Inclinometer Sitting'
incl_lyi ='Inclinometer Lying'


def plotBoxPlot(list_data, list_name_cols, prefix, title):
    
    # arr_activity_chest = np.array(list_activity_chest)
    arr_activity_thigh = np.array(list_data)

    # print('activity chest:')
    # print(arr_activity_chest)
    print('activity thigh:')
    print(arr_activity_thigh)

    # arr_activity_chest = np.transpose(arr_activity_chest)
    arr_activity_thigh = np.transpose(arr_activity_thigh)

    # list_nights_chest = np.arange(1,len(arr_activity_chest)+1)
    list_nights_thigh = np.arange(1,len(arr_activity_thigh)+1)

    # print(list_nights_chest, list_nights_thigh)

    # df_activity_chest = pd.DataFrame(data = arr_activity_chest,
                                     # index = list_nights_chest,
                                     # columns=list_name_cols)
                                     
    df_activity_thigh = pd.DataFrame(data = arr_activity_thigh,
                                     index = list_nights_thigh,
                                     columns=list_name_cols)

    # df_activity_chest.index.name = 'night'
    df_activity_thigh.index.name = 'night'

    # print(df_activity_chest)
    # print(df_activity_thigh)
    col_names = np.array(df_activity_thigh.columns)

    fig, ax = plt.subplots(nrows=1, ncols=1)
    ax=df_activity_thigh.boxplot(column=col_names[7:].tolist())
    ax.set_ylim(-10, 100)
    ax.set_ylabel('magnitude')
    ax.set_xlabel('window size (min)')
    ax.set_title(f'{title} {prefix}')
    
    return 0


def activityDataFrame(list_data, list_name_cols):
    
    arr_activity = np.array(list_data)
    arr_activity = np.transpose(arr_activity)
    list_nights = np.arange(1,len(arr_activity)+1)
    
    df_activity = pd.DataFrame(data = arr_activity,
                              index = list_nights,
                             columns=list_name_cols)

    df_activity.index.name = 'night'
    
    return df_activity
    
    


def main(args):
    
    path = "../data/projet_officiel/"
    path_out = "../data/projet_officiel_counting_2/"
    # prefix = 'A010'
    prefix = args[1]
    files_list=[prefix+'_chest.csv', prefix+'_thigh.csv']
    files_list_out_rep=[prefix+'_chest_repositioning.csv', prefix+'_thigh_repositioning.csv']
    files_list_out_act=[prefix+'_chest_activity.csv', prefix+'_thigh_activity.csv']
    
    dict_df_rep_chest = {}
    dict_df_rep_thigh = {}
    
    # print('files_list: ', files_list)
    
    flag_read=False
    
    try:
        obj_chest.openFile(path, files_list[0])
        obj_thigh.openFile(path, files_list[1])
        flag_read=True
    except ValueError:
        print(f'Problem reading the file {self.filename}.')
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
        win_size_minutes = 15 # minutes
        print(f'window size: {win_size_minutes}')
        obj_chest.inclinometers_sliding_window(win_size_minutes)
        obj_thigh.inclinometers_sliding_window(win_size_minutes)
        
        obj_chest.nightCounts()
        obj_thigh.nightCounts()

        df_counts_chest=obj_chest.getNightCounts()
        df_counts_thigh=obj_thigh.getNightCounts()
        
        ## write csv files 
        df_counts_chest.to_csv(path_out+files_list_out_rep[0], index=False)
        df_counts_thigh.to_csv(path_out+files_list_out_rep[1], index=False)
        ## repositioning estimation
        ############################
        
        #############################
        ## vector magnitude activity        
        min_value=3 ## counts
        min_samples_window = 2 ## at least 2 samples to consider it as a valid activity
        ## get values using several window sizes; provides info activity frequency during each night
        ## windows' size base of 2 (from 1min [2**0] to 128min [2**7]): 1,2,4,8,16,32,64,128
        list_activity_chest = []
        list_activity_thigh = []
        list_name_cols = []

        print('activity estimation for')
        for i in np.arange(0,9):
            win_size=2**i ## min
            print(f'window size: {win_size}')
            list_activity_chest.append(obj_chest.vecMagCounting(min_value, win_size, min_samples_window))
            list_activity_thigh.append(obj_thigh.vecMagCounting(min_value, win_size, min_samples_window))
            
            list_name_cols.append(str(win_size)+'(min)')
            
        df_activity_chest = activityDataFrame(list_activity_chest, list_name_cols)
        df_activity_thigh = activityDataFrame(list_activity_thigh, list_name_cols)
        
        df_activity_chest.to_csv(path_out+files_list_out_act[0])
        df_activity_thigh.to_csv(path_out+files_list_out_act[1])
        ## vector magnitude activity
        #############################

        # plotBoxPlot(list_activity_thigh, list_name_cols, prefix, 'activity')
        
        # ## plot position changing
        obj_chest.plotDWTInclinometers()
        obj_thigh.plotDWTInclinometers()
  
        # ## plot vector magnitude and inclinometers; all days and nights (original data)
        obj_chest.plotActigraphy()
        obj_thigh.plotActigraphy()
        
        # obj_chest.plotVectorMagnitude()
        # obj_thigh.plotVectorMagnitude()
        
        plt.ion()
        plt.show(block=True)
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
