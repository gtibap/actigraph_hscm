#!/usr/bin/env python
# -*- coding: utf-8 -*-

from class_plots_activity import Activity_Measurements
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# global instances
# obj_chest=Activity_Measurements()
# obj_thigh=Activity_Measurements()

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
    
    path = "../../data/projet_officiel/ancient_2/"
    path_out = "../../data/projet_officiel/measurements/immobility/"
    
    # prefix = 'A010'
    prefix = args[1]
    # files_list=[prefix+'_chest.csv', prefix+'_thigh.csv']
    files_list=[prefix+'_chest.csv',]
    
    # print('files_list: ', files_list)
    
    obj_chest=Activity_Measurements(prefix+'_chest')
    # obj_thigh=Activity_Measurements(prefix+'_thigh')

    try:
        obj_chest.openFile(path, files_list[0])
        # obj_thigh.openFile(path, files_list[1])
    except:
        print(f'Problem reading the file {prefix}_chest.')
        return 0

    print('reading success!')
    
    ############################
    ## repositioning estimation
    print(f'immobility estimation')
    win_size_minutes = 1 # minutes
    print(f'window size: {win_size_minutes}')
    obj_chest.inclinometers_sliding_window(win_size_minutes)
    # obj_thigh.inclinometers_sliding_window(win_size_minutes)

    ######## plot inclinometers ############
    obj_chest.plot_Inclinometers_filtered()
    # obj_thigh.plot_Inclinometers_filtered()

    ######## activity rates calculation #########
    win_a= 10
    win_b=120
    obj_chest.vma_processing(win_a, win_b)

    ####### plot activity counts and activity rates ############
    obj_chest.plot_activity_rates()

    plt.show()
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
