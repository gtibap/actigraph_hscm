#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  read_raw_actigraphy.py
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
# import gt3x
from pygt3x.reader import FileReader
import matplotlib.pyplot as plt
import numpy as np

def main(args):
    
    path_gt3x = "../data/projet_officiel/gt3x/"
    path_agd  = "../data/projet_officiel/agd/"
    # prefix = 'A010'
    prefix = args[1]
    files_gt3x=[prefix+'_chest.gt3x', prefix+'_thigh.gt3x']
    files_agd=[prefix+'_chest.agd', prefix+'_thigh.agd']
    
    filename_chest = path_gt3x + files_gt3x[0]
    filename_thigh = path_gt3x + files_gt3x[1]
    
    # filename_chest = path_agd + files_agd[0]
    # filename_thigh = path_agd + files_agd[1]
    
   ## Read raw data and calibrate, then export to pandas data frame
    with FileReader(filename_chest) as reader:
        was_idle_sleep_mode_used = reader.idle_sleep_mode_activated
        df = reader.to_pandas()
        print(df.head(5))
        print(df.shape, df.size, len(df))
        print('sample_rate:', reader.info.sample_rate)
        print('info txt:', reader.info)
    
    time = df.index.tolist()
    axis_x = df['X'].to_numpy()
    axis_y = df['Y'].to_numpy()
    axis_z = df['Z'].to_numpy()
    
    arr_vm = np.sqrt(axis_x**2 + axis_y**2 + axis_z**2)
    theta_x = np.rad2deg(np.arccos(axis_x / arr_vm))
    theta_y = np.rad2deg(np.arccos(axis_y / arr_vm))
    theta_z = np.rad2deg(np.arccos(axis_z / arr_vm))
    
    fig, ax = plt.subplots(nrows=4, ncols=1, sharex=True)
    ax[0].plot(time, theta_x)
    ax[1].plot(time, theta_y)
    ax[2].plot(time, theta_z)
    ax[3].plot(time, arr_vm)
    
    ax[0].set_title(files_gt3x[0])
    ax[0].set_ylabel('accel. X')
    ax[1].set_ylabel('accel. Y')
    ax[2].set_ylabel('accel. Z')
    ax[3].set_ylabel('accel. vm')
    ax[3].set_xlabel('samples')
    plt.show()
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
