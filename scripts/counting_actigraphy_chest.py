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
    
    path = "../data/"
    path_out = "../data/counting/"
    
    # prefix = 'A010'
    prefix = args[1]
    files_list=[prefix+'_chest.csv']
    files_list_out_rep=[prefix+'_chest_repositioning.csv']
    files_list_out_act=[prefix+'_chest_activity.csv']
    files_list_out_mov=[prefix+'_chest_numberMov.csv']
    
    dict_df_rep_chest = {}
    
    # print('files_list: ', files_list)
    
    flag_read=False
    
    try:
        obj_chest.openFile(path, files_list[0])
        flag_read=True
    except ValueError:
        print(f'Problem reading the file {self.filename}.')
        flag_read=False

    if flag_read==True:
        print('reading success!')
        
        #################
        ## repositioning start
        list_repos_chest=[]
        list_names_repos=[]
        
        ############################
        ## repositioning estimation
        print(f'repositioning estimation')
        win_size_minutes = 15 # minutes
        print(f'window size: {win_size_minutes}')
        obj_chest.inclinometers_sliding_window(win_size_minutes)
        
        obj_chest.nightCounts()

        df_counts_chest=obj_chest.getNightCounts()
        
        ## write csv files 
        df_counts_chest.to_csv(path_out+files_list_out_rep[0], index=False)
        ## repositioning estimation
        ############################
        
        #############################
        ## vector magnitude activity        
        min_value=3 ## counts
        min_samples_window = 1 ## at least 2 samples to consider it as a valid activity
        ## get values using several window sizes; provides info activity frequency during each night
        ## windows' size base of 2 (from 1min [2**0] to 128min [2**7]): 1,2,4,8,16,32,64,128
        list_activity_chest = []
        list_mov_conts_chest = []
        list_name_cols = []

        print('activity estimation for')
        for i in np.arange(0,9):
            win_size=2**i ## min
            print(f'window size: {win_size}')
            list_mov_grade_chest, list_mov_counts_chest = obj_chest.vecMagCounting(min_value, win_size, min_samples_window)
            
            list_activity_chest.append(list_mov_grade_chest)
            
            list_mov_conts_chest.append(list_mov_counts_chest)
            
            list_name_cols.append(str(win_size)+'(min)')
            
        df_activity_chest = activityDataFrame(list_activity_chest, list_name_cols)
        
        df_mov_counts_chest = activityDataFrame(list_mov_conts_chest, list_name_cols)
        
        ## saving data
        df_activity_chest.to_csv(path_out+files_list_out_act[0])
        
        df_mov_counts_chest.to_csv(path_out+files_list_out_mov[0])
        ## vector magnitude activity
        #############################

        
        # ## plot position changing
        obj_chest.plotDWTInclinometers()
  
        # ## plot vector magnitude and inclinometers; all days and nights (original data)
        obj_chest.plotActigraphy()
                
        plt.ion()
        plt.show(block=True)
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
