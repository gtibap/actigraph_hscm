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
        
        # obj_chest.waveletTransform(0)
        obj_chest.waveletTransform(10)
        
        # obj_chest.rollingWindow()
       

        # obj_chest.plotActigraphy()
        # obj_thigh.plotActigraphy()
        
        # obj_chest.countChanges()
        # obj_thigh.countChanges()
        
        # print('\nchest\n',obj_chest.getNightCounts())
        # print('\nthigh\n',obj_thigh.getNightCounts())
        
        # obj_chest.plotActigraphyMod()
        # obj_thigh.plotActigraphyMod()
        
        plt.ion()
        # plt.show()
        plt.show(block=True)
        
        ## file_name_chest=path_out+prefix+'chest_act.csv'
        ## df_actigraphy.to_csv(file_name_chest, index=False)
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
