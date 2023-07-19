#!/usr/bin/env python
# -*- coding: utf-8 -*-

from class_counting import Counting_Actigraphy
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


def main(args):
    
    path = "../data/projet_officiel/"
    path_out = "../data/projet_officiel_counting/"
    # prefix = 'A010'
    prefix = args[1]
    files_list=[prefix+'_chest.csv', prefix+'_thigh.csv']
    files_list_out_rep=[prefix+'_chest_repositioning.csv', prefix+'_thigh_repositioning.csv']
    files_list_out_act=[prefix+'_chest_activity.csv', prefix+'_thigh_activity.csv']
    
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
        dwt_level=10
        obj_chest.inclinometersDWT(dwt_level)
        obj_thigh.inclinometersDWT(dwt_level)
        
        obj_chest.nightCounts()
        obj_thigh.nightCounts()

        df_counts_chest=obj_chest.getNightCounts()
        df_counts_thigh=obj_thigh.getNightCounts()
        ## repositioning end
        ################
        
        ################
        ## vector magnitude activity        
        min_value=3 ## counts
        min_samples_window = 2 ## at least 2 samples to consider it as a valid activity
        ## get values using several window sizes; provides info activity frequency during each night
        ## windows' size base of 2 (from 1min [2**0] to 128min [2**7]): 1,2,4,8,16,32,64,128
        list_activity_chest = []
        list_activity_thigh = []
        list_name_cols = []
        # list_name_cols.append('night')
        print('activity estimation for')
        for i in np.arange(9):
            win_size=2**i ## min
            print(f'window size: {win_size}')
            list_activity_chest.append(obj_chest.vecMagCounting(min_value, win_size, min_samples_window))
            list_activity_thigh.append(obj_thigh.vecMagCounting(min_value, win_size, min_samples_window))
            
            list_name_cols.append('w_'+str(win_size))
            # vma_act_chest=obj_chest.vecMagCounting(min_value, win_size, min_samples_window)
            # vma_act_thigh=obj_thigh.vecMagCounting(min_value, win_size, min_samples_window)
        ## vector magnitude activity
        ################
        
        arr_activity_chest = np.array(list_activity_chest)
        arr_activity_thigh = np.array(list_activity_thigh)
        
        print('activity chest:')
        print(arr_activity_chest)
        print('activity thigh:')
        print(arr_activity_thigh)
        
        arr_activity_chest = np.transpose(arr_activity_chest)
        arr_activity_thigh = np.transpose(arr_activity_thigh)
        
        list_nights_chest = np.arange(1,len(arr_activity_chest)+1)
        list_nights_thigh = np.arange(1,len(arr_activity_thigh)+1)
        
        print(list_nights_chest, list_nights_thigh)
        
        df_activity_chest = pd.DataFrame(data = arr_activity_chest,
                                         index = list_nights_chest,
                                         columns=list_name_cols)
                                         
        df_activity_thigh = pd.DataFrame(data = arr_activity_thigh,
                                         index = list_nights_thigh,
                                         columns=list_name_cols)
        
        df_activity_chest.index.name = 'night'
        df_activity_thigh.index.name = 'night'
        
        # print(df_activity_chest)
        # print(df_activity_thigh)
        
        fig, ax = plt.subplots(nrows=1, ncols=1)
        ax=df_activity_thigh.boxplot()
        ax.set_ylabel('probability distribution')
        ax.set_xlabel('window size (min)')
        ax.set_title(f'Activity {prefix} based on Vector Magnitude values')
        
        
        ## adding vector magnitude activity to the dataframe of repositioning
        # df_counts_chest['vma_act']=vma_act_chest
        # df_counts_thigh['vma_act']=vma_act_thigh
        
        # ## write csv files 
        df_counts_chest.to_csv(path_out+files_list_out_rep[0], index=False)
        df_counts_thigh.to_csv(path_out+files_list_out_rep[1], index=False)
        
        df_activity_chest.to_csv(path_out+files_list_out_act[0], index=False)
        df_activity_thigh.to_csv(path_out+files_list_out_act[1], index=False)
        
        
        
        # ## plot position changing
        # obj_chest.plotDWTInclinometers()
        # obj_thigh.plotDWTInclinometers()
  
        # ## plot vector magnitude and inclinometers; all days and nights (original data)
        # obj_chest.plotActigraphy()
        obj_thigh.plotActigraphy()
        
        # obj_chest.plotVectorMagnitude()
        # obj_thigh.plotVectorMagnitude()
        
        plt.ion()
        plt.show(block=True)
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
