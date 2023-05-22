#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  readFilteredData.py
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
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# global instances
obj_chest=Actigraphy()
obj_thigh=Actigraphy()
df_filtered_all = []
list_width_filter = []
prefix = ''
id_filter = 0
vec_mag  ='Vector Magnitude'
incl_off ='Inclinometer Off'
incl_sta ='Inclinometer Standing'
incl_sit ='Inclinometer Sitting'
incl_lyi ='Inclinometer Lying'
arr_fig = [[] for i in range(10)]
arr_axs = [[] for i in range(10)]

def plot_actigraphy(df,night_num,filename,fig,ax):
    
    df_night = df.loc[(df['night']==night_num)]
    
    for i in np.arange(5):
        ax[i].cla()
        
    # ax[0].set_xlim(0,5000)

    ax[0].set_title(filename+', night:'+str(night_num))
    ax[0].set_ylabel('v.m.')
    ax[1].set_ylabel('off')
    ax[2].set_ylabel('lyi')
    ax[3].set_ylabel('sit')
    ax[4].set_ylabel('sta')
    ax[4].set_xlabel('time (s)')
    
    ax[0].plot(df_night[vec_mag].to_numpy())
    ax[1].plot(df_night[incl_off].to_numpy())
    ax[2].plot(df_night[incl_lyi].to_numpy())
    ax[3].plot(df_night[incl_sit].to_numpy())
    ax[4].plot(df_night[incl_sta].to_numpy())
    
    fig.canvas.draw()
    fig.canvas.flush_events()
    
    return 0

def on_press(event):
    global id_filter
    
    print('press', event.key)
    sys.stdout.flush()
    
    if event.key == 'x':
        plt.close('all')
    elif event.key == 'm':
        if (obj_chest.night_num < obj_chest.last_night) and (obj_thigh.night_num < obj_thigh.last_night):
            obj_chest.night_num+=1
            obj_thigh.night_num+=1
            plot_all()
        else:
            pass
    elif event.key == 'n':
        if (obj_chest.night_num > obj_chest.first_night) and (obj_thigh.night_num > obj_thigh.first_night):
            obj_chest.night_num-=1
            obj_thigh.night_num-=1
            plot_all()
        else:
            pass
    else:
        pass
      
    return 0
    
    
def plot_all():
    # global fig_chest, ax_chest, fig_chest2, ax_chest2, fig_thigh, fig_thigh2, ax_thigh, ax_thigh2
    
    plot_actigraphy(obj_chest.getActigraphyDataCropped(), obj_chest.night_num, obj_chest.filename, arr_fig[0], arr_axs[0])
    plot_actigraphy(obj_thigh.getActigraphyDataCropped(), obj_thigh.night_num, obj_thigh.filename, arr_fig[1], arr_axs[1])
    
    return 0

    
def main(args):
    global arr_fig, arr_axs, df_filtered_all, list_width_filter, prefix
    
    path = "../data/projet_officiel/"
    path_filtered = "../data/projet_officiel_filtered/"
    # prefix = 'A003'
    prefix = args[1]
    print('prefix: ', prefix)
    files_list=[prefix+'_chest.csv', prefix+'_thigh.csv']
    path_base = path_filtered + prefix
    mark_value = 60
    step=1

    
    flag_chest=False
    flag_thigh=False
    flag_filtered=False
    
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
        print('Reading data: Success')
        
        arr_fig[0], arr_axs[0] = plt.subplots(nrows=5, ncols=1, sharex=True)
        arr_fig[1], arr_axs[1] = plt.subplots(nrows=5, ncols=1, sharex=True)
        
        cid_0  = arr_fig[0].canvas.mpl_connect('key_press_event', on_press)
        cid_1  = arr_fig[1].canvas.mpl_connect('key_press_event', on_press)
        
        plot_all()

        plt.ion()
        plt.show(block=True)
    else:
        print('Reading data: Incompleted data.')
        
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
