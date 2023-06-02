#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  segmentation_actigraphy.py
#  
#  Copyright 2023 Gerardo <gerardo@CNMTLO-MX2074SBP>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
from class_segmentation import Seg_Actigraphy

# global instances
obj_chest=Seg_Actigraphy()
obj_thigh=Seg_Actigraphy()

vec_mag  ='Vector Magnitude'
incl_off ='Inclinometer Off'
incl_sta ='Inclinometer Standing'
incl_sit ='Inclinometer Sitting'
incl_lyi ='Inclinometer Lying'


def main(args):
    
    path = "../data/projet_officiel/"
    path_out = "../data/projet_officiel_filtered/counts_june02/"
    # prefix = 'A010'
    prefix = args[1]
    files_list=[prefix+'_chest.csv', prefix+'_thigh.csv']
    
    
    print('files_list: ', files_list)
    
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
        # print(obj_chest.df1)
        # print(obj_thigh.df1)
        print('inclinometers state changing')
        obj_chest.inclinometersStateChanging()
        df_actigraphy = obj_chest.getActigraphyData()
        
        # file_name_chest=path_out+prefix+'chest_act.csv'
        # df_actigraphy.to_csv(file_name_chest, index=False)
        
        obj_chest.plotActigraphy()
        # plt.show(block=True)
        
        
          
            
    
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
