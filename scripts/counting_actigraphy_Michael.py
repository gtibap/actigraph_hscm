#!/usr/bin/env python
# -*- coding: utf-8 -*-

from class_counting_Michael import Counting_Actigraphy
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
    
    path = "../data/projet_communaute/"
    path_out = "../data/projet_communaute/counts/"
    # prefix = 'A010'
    prefix = args[1]
    files_list=[prefix+'.csv']
    files_list_out=[prefix+'_counts.csv']
    
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
        
    ## plot vector magnitude and inclinometers; all days and nights (original data)
    obj_chest.plotActigraphy()
    obj_chest.maximumIds()
    
    plt.ion()
    plt.show(block=True)
        
        
    '''
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
    win_size=120 ## min
    min_samples_window = 2 ## at least 2 samples to consider it as a valid activity
    vma_act_chest=obj_chest.vecMagCounting(min_value, win_size, min_samples_window)
    vma_act_thigh=obj_thigh.vecMagCounting(min_value, win_size, min_samples_window)
    ## vector magnitude activity
    ################
    
    ## adding vector magnitude activity to the dataframe of repositioning
    df_counts_chest['vma_act']=vma_act_chest
    df_counts_thigh['vma_act']=vma_act_thigh
    
    ## write csv files 
    df_counts_chest.to_csv(path_out+files_list_out[0], index=False)
    df_counts_thigh.to_csv(path_out+files_list_out[1], index=False)
    
    # ## plot position changing
    obj_chest.plotDWTInclinometers()
    obj_thigh.plotDWTInclinometers()

    # ## plot vector magnitude and inclinometers; all days and nights (original data)
    # obj_chest.plotActigraphy()
    # obj_thigh.plotActigraphy()
    
    # obj_chest.plotVectorMagnitude()
    # obj_thigh.plotVectorMagnitude()
    
    plt.ion()
    plt.show(block=True)
    
    '''
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
