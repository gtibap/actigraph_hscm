#!/usr/bin/env python
# -*- coding: utf-8 -*-

from class_immobility import Activity_Measurements
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
    files_list=[prefix+'_chest.csv', prefix+'_thigh.csv']
    
    # print('files_list: ', files_list)
    
    obj_chest=Activity_Measurements(prefix+'_chest')
    obj_thigh=Activity_Measurements(prefix+'_thigh')

    try:
        obj_chest.openFile(path, files_list[0])
        obj_thigh.openFile(path, files_list[1])
    except:
        print(f'Problem reading the file {prefix}_chest or {prefix}_thigh.')
        return 0

    print('reading success!')
    
    ############################
    ## repositioning estimation
    print(f'immobility estimation')
    win_size_minutes = 10 # minutes
    print(f'window size: {win_size_minutes}')
    obj_chest.inclinometers_sliding_window(win_size_minutes)
    obj_thigh.inclinometers_sliding_window(win_size_minutes)
 
    # df_incl_chest = obj_chest.get_inclinometers()
    # df_incl_thigh = obj_thigh.get_inclinometers()
    # print(f'incl chest:\n{df_incl_chest}')
    # print(f'incl thigh:\n{df_incl_thigh}')

    ## immobility during nights
    print('chest')
    df_immobility_chest = obj_chest.get_posture_duration()
    print('thigh')
    df_immobility_thigh = obj_thigh.get_posture_duration()

    ## write csv files 
    df_immobility_chest.to_csv(path_out+prefix+'_chest_immobility.csv', index=False)
    df_immobility_thigh.to_csv(path_out+prefix+'_thigh_immobility.csv', index=False)
    # ## immobility estimation
    # ############################

    ######## plot inclinometers ############
    obj_chest.plot_Inclinometers_filtered()
    obj_thigh.plot_Inclinometers_filtered()

    plt.show()
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
