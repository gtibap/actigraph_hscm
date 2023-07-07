#!/usr/bin/env python
# -*- coding: utf-8 -*-

from class_counting import Counting_Actigraphy
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
    files_list_out=[prefix+'_chest_counts.csv', prefix+'_thigh_counts.csv']
    
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
        
        dwt_level=10
        obj_chest.inclinometersDWT(dwt_level)
        obj_thigh.inclinometersDWT(dwt_level)
        
        obj_chest.nightCounts()
        obj_thigh.nightCounts()

        df_counts_chest=obj_chest.getNightCounts()
        df_counts_thigh=obj_thigh.getNightCounts()
        
        vma_act_chest=obj_chest.vecMagCounting()
        vma_act_thigh=obj_thigh.vecMagCounting()
        
        df_counts_chest['vma_act']=vma_act_chest
        df_counts_thigh['vma_act']=vma_act_thigh
        
        ## write csv files 
        df_counts_chest.to_csv(path_out+files_list_out[0], index=False)
        df_counts_thigh.to_csv(path_out+files_list_out[1], index=False)
        
        ## plot position changing
        # obj_chest.plotDWTInclinometers()
        # obj_thigh.plotDWTInclinometers()
  
        
        obj_chest.plotActigraphy()
        obj_thigh.plotActigraphy()
        
        
        plt.ion()
        plt.show(block=True)
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
