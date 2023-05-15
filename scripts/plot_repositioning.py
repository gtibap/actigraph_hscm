#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  plot_repositioning.py
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
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


arr_fig = [[] for i in range(10)]
arr_axs = [[] for i in range(10)]

def main(args):
    # print('repositioning!')
    ## read cvs files data repositioning at different scales after filtering with filter_width from 0 to 15 min every 60 seconds
    path_filtered = "../data/projet_officiel_filtered/"
    prefix = 'A006'
    
    path_base = path_filtered + prefix
    
    file_name_chest = path_base + '_chest_counts.csv'
    file_name_thigh = path_base + '_thigh_counts.csv'
    
    df_counts_chest = pd.read_csv(file_name_chest)
    df_counts_thigh = pd.read_csv(file_name_thigh)
    
    # print(df_counts_chest)
    # print(df_counts_thigh)
    # print(df_counts_chest.loc[df_counts_chest['night']==0])
    ## these values allow to collect filtered signals every 'delta' seconds
    delta = 60
    start = 1*delta
    end   = 15*delta
    step  = 1*delta 
    
    # list_width_filter = np.concatenate([[0],np.arange(start,end+step,step)])
    # print('list_width_filter: ', list_width_filter)

    # df_counts_chest['width_filter']
    list_width_filter = df_counts_chest['width_filter'].unique().tolist()
    print(list_width_filter)
    
    df_plot = pd.DataFrame()
    list_median_wf_chest = []
    list_median_wf_thigh = []
    list_median_night_chest = []
    list_median_night_thigh = []

    for wf in list_width_filter:
        # print(df_counts_chest.loc[df_counts_chest['width_filter']==wf, ['total']])
        arr_chest=(df_counts_chest.loc[df_counts_chest['width_filter']==wf])['total'].to_numpy()
        arr_thigh=(df_counts_thigh.loc[df_counts_thigh['width_filter']==wf])['total'].to_numpy()
        # df_plot[str(wf)] = arr[:]
        list_median_wf_chest.append(np.median(arr_chest))
        list_median_wf_thigh.append(np.median(arr_thigh))
        
    list_nights = df_counts_chest['night'].unique().tolist()
    print(list_nights)
    
    for night in list_nights:
        arr_chest=(df_counts_chest.loc[df_counts_chest['night']==night])['total'].to_numpy()
        arr_thigh=(df_counts_thigh.loc[df_counts_thigh['night']==night])['total'].to_numpy()
        # df_plot[str(wf)] = arr[:]
        
        list_median_night_chest.append(arr_chest[3])
        list_median_night_thigh.append(arr_thigh[3])
        
    # print(df_plot)
    # df_counts_chest['total'].groupby('night').boxplot()
    # plt.show()

    # fig = plt.figure(figsize =(10, 7))
 
    # Creating axes instance
    # ax = fig.add_axes([0, 0, 1, 1])
    arr_fig[0], arr_axs[0] = plt.subplots(nrows=1, ncols=1, sharex=True)
    arr_fig[1], arr_axs[1] = plt.subplots(nrows=1, ncols=1, sharex=True)

    # Creating plot
    # arr_axs[0].boxplot(df_plot)
    arr_axs[0].plot(list_median_wf_chest, label='chest')
    arr_axs[0].plot(list_median_wf_thigh, label='thigh')
    
    arr_axs[1].plot(list_median_night_chest, label='chest')
    arr_axs[1].plot(list_median_night_thigh, label='thigh')
    
    arr_fig[0].canvas.draw()
    arr_fig[1].canvas.draw()
    # arr_fig[0].canvas.flush_events()
     
    # show plot
    plt.legend()
    plt.show()
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

