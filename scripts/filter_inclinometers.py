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
vec_mag  ='Vector Magnitude'
incl_off ='Inclinometer Off'
incl_sta ='Inclinometer Standing'
incl_sit ='Inclinometer Sitting'
incl_lyi ='Inclinometer Lying'
fig_chest=[]
ax_chest=[]
fig_chest2=[]
ax_chest2=[]
fig_thigh=[]
fig_thigh2=[]
ax_thigh=[]
ax_thigh2=[]


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
    # global fig_chest, ax_chest, fig_chest2, ax_chest2, fig_chest3, ax_chest3 
    
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
        

def plot_all():
    # global fig_chest, ax_chest, fig_chest2, ax_chest2, fig_thigh, fig_thigh2, ax_thigh, ax_thigh2
    
    plot_actigraphy(obj_chest.getActigraphyDataCropped(), obj_chest.night_num, obj_chest.filename, fig_chest, ax_chest)
    plot_actigraphy(obj_chest.getFilteredActigraphyDataCropped(), obj_chest.night_num, obj_chest.filename, fig_chest2, ax_chest2)
    plot_actigraphy(obj_thigh.getActigraphyDataCropped(), obj_thigh.night_num, obj_thigh.filename, fig_thigh, ax_thigh)
    plot_actigraphy(obj_thigh.getFilteredActigraphyDataCropped(), obj_thigh.night_num, obj_thigh.filename, fig_thigh2, ax_thigh2)
    
    return
        
def main(args):
    global fig_chest, ax_chest, fig_chest2, ax_chest2, fig_thigh, fig_thigh2, ax_thigh, ax_thigh2
    
    path = "../data/projet_officiel/"
    path_filtered = "../data/projet_officiel_filtered/"
    prefix = 'A003'
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
        obj_thigh.readInclinometers()
        
        obj_chest.filterInclinometers()
        obj_thigh.filterInclinometers()
        
        path_base = path_filtered + prefix
        mark_value = 60
        step=1
        initial=0
        # [1,900]
        for width_filter in np.arange(0,901):
            print('\nwidth_filter: ', width_filter)
            obj_chest.filterInclinometersStep2(width_filter)
            obj_thigh.filterInclinometersStep2(width_filter)
            
            
            # save in disk every 60*i, i+=2, i=[1,3,5,...,15]
            if width_filter == (initial*mark_value*step):
                file_name_chest = path_base + '_chest_'+ str(width_filter) + '.csv'
                file_name_thigh = path_base + '_thigh_'+ str(width_filter) + '.csv'
                df_chest_filtered = obj_chest.getFilteredActigraphyDataCropped()
                df_thigh_filtered = obj_thigh.getFilteredActigraphyDataCropped()
                df_chest_filtered.to_csv(file_name_chest, index=False)
                df_thigh_filtered.to_csv(file_name_thigh, index=False)
                step+=2
                initial=1
            else:
                pass
                
            # 2 min [0, 120)
            # elif width_filter == 119:
                # file_name_chest = path_base + '_chest_120.csv'
                # file_name_thigh = path_base + '_thigh_120.csv'
                # df_chest_filtered = obj_chest.getFilteredActigraphyDataCropped()
                # df_thigh_filtered = obj_thigh.getFilteredActigraphyDataCropped()
                # df_chest_filtered.to_csv(file_name_chest, index=False)
                # df_thigh_filtered.to_csv(file_name_thigh, index=False)
            # 5 min [0, 120)
            # elif width_filter == 119:
                # file_name_chest = path_base + '_chest_120.csv'
                # file_name_thigh = path_base + '_thigh_120.csv'
                # df_chest_filtered = obj_chest.getFilteredActigraphyDataCropped()
                # df_thigh_filtered = obj_thigh.getFilteredActigraphyDataCropped()
                # df_chest_filtered.to_csv(file_name_chest, index=False)
                # df_thigh_filtered.to_csv(file_name_thigh, index=False)
        
        
        
        # width_filter=2
        # obj_chest.filterInclinometersStep2(width_filter)
        
        # width_filter=3
        # obj_chest.filterInclinometersStep2(width_filter)
        
        fig_chest, ax_chest = plt.subplots(nrows=5, ncols=1, sharex=True)
        fig_chest2, ax_chest2 = plt.subplots(nrows=5, ncols=1, sharex=True)

        fig_thigh,  ax_thigh  = plt.subplots(nrows=5, ncols=1, sharex=True)
        fig_thigh2, ax_thigh2 = plt.subplots(nrows=5, ncols=1, sharex=True)
        
        # fig_chest3, ax_chest3 = plt.subplots(nrows=5, ncols=1, sharex=True)
        
        # df_act_chest = obj_chest.getActigraphyData()
        plot_all()
        # plot_actigraphy(obj_chest.getActigraphyData(), obj_chest.night_num, obj_chest.filename, fig_chest, ax_chest)
        # plot_actigraphy(obj_chest.getFilteredActigraphyData(), obj_chest.night_num, obj_chest.filename, fig_chest2, ax_chest2)
        
        # plot_actigraphy(obj_thigh.getActigraphyData(), obj_thigh.night_num, obj_thigh.filename, fig_thigh, ax_thigh)
        # plot_actigraphy(obj_thigh.getFilteredActigraphyData(), obj_thigh.night_num, obj_thigh.filename, fig_thigh2, ax_thigh2)
        
        # plot_actigraphy(obj_chest.getFilteredActigraphyDataStep2(), obj_chest.night_num, obj_chest.filename, fig_chest3, ax_chest3)
        
        
        cid_chest  = fig_chest.canvas.mpl_connect('key_press_event', on_press)
        cid_chest2 = fig_chest2.canvas.mpl_connect('key_press_event', on_press)
        cid_thigh  = fig_thigh.canvas.mpl_connect('key_press_event', on_press)
        cid_thigh2 = fig_thigh2.canvas.mpl_connect('key_press_event', on_press)
        
        # cid_chest3 = fig_chest3.canvas.mpl_connect('key_press_event', on_press)
        
        # cid_thigh  = fig_actigraphy_thigh.canvas.mpl_connect('key_press_event', on_press)
        # cid_vecMag = fig_vectMag.canvas.mpl_connect('key_press_event', on_press)
        # cid_stems = fig_incl_stems.canvas.mpl_connect('key_press_event', on_press)
                
        # cid1 = fig_incl_stems.canvas.mpl_connect('button_press_event', onclick)
        # cid2 = fig_incl_stems.canvas.mpl_connect('key_press_event', on_press)
        plt.ion()
        # plt.show()
        plt.show(block=True)
        
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
