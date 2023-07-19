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
    
    flag_read=False
    
    try:
        obj_chest.openFile(path, files_list[0])
        flag_read=True
    except ValueError:
        print(f'Problem reading the file {self.filename}.')
        flag_read=False

    if flag_read==True:
        print('reading success!')
    
    obj_chest.inclinometersDWT()
    obj_chest.maximumIds()
    obj_chest.nightCounts()
    df_counts_chest=obj_chest.getNightCounts()
    # print(df_counts_chest)
    ## write csv files 
    df_counts_chest.to_csv(path_out+files_list_out[0], index=False)
    
    ## plot position changing
    obj_chest.plotDWTInclinometers()
    ## plot vector magnitude and inclinometers; all days and nights (original data)
    obj_chest.plotActigraphy()
    plt.ion()
    plt.show(block=True)
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
