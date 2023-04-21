#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  filter_inclinometers.py
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
from class_actigraphy import Actigraphy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# global instances
obj_chest=Actigraphy()
obj_thigh=Actigraphy()


def main(args):
    
    path = "../data/projet_officiel/"
    prefix = 'A004'
    files_list=[prefix+'_chest.csv', prefix+'_thigh.csv']
    
    flag_chest=False
    flag_thigh=False
    
    try:
        obj_chest.openFile(path, files_list[0])
        flag_chest=True
    except ValueError:
            print(f'Problem reading the file {self.filename}.')
            flag_chest=False
            
    try:
        obj_thigh.openFile(path, files_list[1])
        flag_thigh=True
    except ValueError:
            print(f'Problem reading the file {self.filename}.')
            flag_thigh=False
        
    if flag_chest and flag_thigh:
        
        obj_chest.readInclinometers()
        # obj_thigh.readInclinometers()
        
        obj_chest.filterInclinometers()
        # obj_thigh.filterInclinometers()
        
        # print(obj_chest.df_inclinometers)
        
        # print('ready!')
        # print(obj_chest.getActigraphyData())
        # print(obj_thigh.getActigraphyData())
        # obj_chest.filterInclinometers()
        # obj_thigh.filterInclinometers()
    
    else:
        print('Incompleted data.')
        
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
