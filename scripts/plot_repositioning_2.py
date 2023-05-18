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


class countsClass:
    
    def __init__(self):
        self.df_counts_chest = pd.DataFrame()
        self.df_counts_thigh = pd.DataFrame()
        self.filename=''
        self.list_active_chest=[]
        self.list_active_thigh=[]
        # print('Object created.')
        
    def openFile(self, path, filename):
        
        self.filename=filename
        path_base = path + self.filename
        
        file_name_chest = path_base + '_chest_counts.csv'
        file_name_thigh = path_base + '_thigh_counts.csv'
        self.filename_chest = filename + '_chest'
        self.filename_thigh = filename + '_thigh'
        try:
            self.df_counts_chest = pd.read_csv(file_name_chest)
            self.df_counts_thigh = pd.read_csv(file_name_thigh)
        except ValueError:
            print(f'Problem reading the files {self.filename}.')
            return 1
        self.list_width_filter = self.df_counts_chest['width_filter'].unique().tolist()
        self.list_nights = self.df_counts_chest['night'].unique().tolist()
        return 0
        
    def estimateCounts(self):
        
        for night in self.list_nights:
            arr_chest=(self.df_counts_chest.loc[self.df_counts_chest['night']==night])['total'].to_numpy()
            arr_thigh=(self.df_counts_thigh.loc[self.df_counts_thigh['night']==night])['total'].to_numpy()
            
            indexes = np.arange(len(arr_chest))
            weights_chest = (indexes / np.sum(indexes)) ## percentage
            
            indexes = np.arange(len(arr_thigh))
            weights_thigh = (indexes / np.sum(indexes)) ## percentage
            
            self.list_active_chest.append(np.sum(np.multiply(weights_chest, arr_chest)))
            self.list_active_thigh.append(np.sum(np.multiply(weights_thigh, arr_thigh)))
        
        return 0
        
    def getCountsChest(self):
        return self.list_active_chest
        
    def getCountsThigh(self):
        return self.list_active_thigh
    
         
list_instances = []    

arr_fig = [[] for i in range(10)]
arr_axs = [[] for i in range(10)]

def on_press(event):
    global id_filter
    
    print('press', event.key)
    sys.stdout.flush()
    
    if event.key == 'x':
        plt.close('all')
    else:
        pass
      
    return 0


def main(args):
    # print('repositioning!')
    ## read cvs files data repositioning at different scales after filtering with filter_width from 0 to 15 min every 60 seconds
    path_filtered = "../data/projet_officiel_filtered/"
    prefix = 'A005'
    
    list_files = ['A001','A002','A003','A004','A005','A006','A008','A009','A010']
    
    for filename in list_files:
        obj = countsClass()
        flag=obj.openFile(path_filtered, filename)
        print('flag: ', flag, obj.filename)
        obj.estimateCounts()
        
        list_instances.append(obj)
    
    
    
    path_base = path_filtered + prefix
    
    file_name_chest = path_base + '_chest_counts.csv'
    file_name_thigh = path_base + '_thigh_counts.csv'
    
    df_counts_chest = pd.read_csv(file_name_chest)
    df_counts_thigh = pd.read_csv(file_name_thigh)
    
    # print(df_counts_chest)
    # print(df_counts_thigh)
    # print(df_counts_chest.loc[df_counts_chest['night']==0])
    ## these values allow to collect filtered signals every 'delta' seconds
    # delta = 60
    # start = 1*delta
    # end   = 15*delta
    # step  = 1*delta 
    
    # list_width_filter = np.concatenate([[0],np.arange(start,end+step,step)])
    # print('list_width_filter: ', list_width_filter)

    # df_counts_chest['width_filter']
    list_width_filter = df_counts_chest['width_filter'].unique().tolist()
    print(list_width_filter)
    
    # df_plot = pd.DataFrame()
    # list_median_wf_chest = []
    # list_median_wf_thigh = []
    # list_median_night_chest = []
    # list_median_night_thigh = []

    list_active_chest = []
    list_active_thigh = []


    # for wf in list_width_filter:
        ## print(df_counts_chest.loc[df_counts_chest['width_filter']==wf, ['total']])
        # arr_chest=(df_counts_chest.loc[df_counts_chest['width_filter']==wf])['total'].to_numpy()
        # arr_thigh=(df_counts_thigh.loc[df_counts_thigh['width_filter']==wf])['total'].to_numpy()
        ## df_plot[str(wf)] = arr[:]
        # list_median_wf_chest.append(np.median(arr_chest))
        # list_median_wf_thigh.append(np.median(arr_thigh))
        
    list_nights = df_counts_chest['night'].unique().tolist()
    print(list_nights)
    
    for night in list_nights:
        arr_chest=(df_counts_chest.loc[df_counts_chest['night']==night])['total'].to_numpy()
        arr_thigh=(df_counts_thigh.loc[df_counts_thigh['night']==night])['total'].to_numpy()
        
        # df_plot[str(wf)] = arr[:]
        # print(arr_chest)
        # print(arr_thigh)
        indexes = np.arange(len(arr_chest))
        weights_chest = (indexes / np.sum(indexes)) ## percentage
        
        indexes = np.arange(len(arr_thigh))
        weights_thigh = (indexes / np.sum(indexes)) ## percentage
        
        ## print(indexes, np.sum(indexes))
        ## print(weights)
        
        # bool_chest = arr_chest > 0
        # bool_thigh = arr_thigh > 0

        # list_active_chest.append(np.sum(bool_chest))
        # list_active_thigh.append(np.sum(bool_thigh))
        
        list_active_chest.append(np.sum(np.multiply(weights_chest, arr_chest)))
        list_active_thigh.append(np.sum(np.multiply(weights_thigh, arr_thigh)))
        
        # print('arr_chest:', arr_chest, len(arr_chest))
        # print('weights_chest:', weights_chest, len(weights_chest))
        # print('\nnight:',night)
        # print()
        # print()
        
        ## print(bool_chest)
        ## print(np.sum(bool_chest))
        
        


        
        # list_median_night_chest.append(arr_chest[3])
        # list_median_night_thigh.append(arr_thigh[3])
    
    print('chest:', list_active_chest)
    print('thigh:', list_active_thigh)
    
    # arr_nights=np.array(list_nights)
    # ## linear regression
    # A = np.vstack([arr_nights, np.ones(len(list_nights))]).T
    ## print(A)
    # m_chest, c_chest = np.linalg.lstsq(A, list_active_chest, rcond=None)[0]
    # m_thigh, c_thigh = np.linalg.lstsq(A, list_active_thigh, rcond=None)[0]
    # print(m_chest, c_chest)
    # print(m_thigh, c_thigh)

    # y_chest=m_chest*arr_nights+c_chest
    # y_thigh=m_thigh*arr_nights+c_thigh
    
    # print(y_chest)
    # print(np.mean(y_chest))
    # print(y_thigh)
    # print(np.mean(y_thigh))
    
    # print(df_plot)
    # df_counts_chest['total'].groupby('night').boxplot()
    # plt.show()

    # fig = plt.figure(figsize =(10, 7))
 
    ## Creating axes instance
    ## ax = fig.add_axes([0, 0, 1, 1])
    arr_fig[0], arr_axs[0] = plt.subplots(nrows=1, ncols=1, sharex=True)
    arr_fig[1], arr_axs[1] = plt.subplots(nrows=1, ncols=1, sharex=True)

    ## Creating plot
    ## arr_axs[0].boxplot(df_plot)
    # arr_axs[0].plot(list_median_wf_chest, label='chest')
    # arr_axs[0].plot(list_median_wf_thigh, label='thigh')
    # arr_axs[0].set_title(prefix)
    # arr_axs[1].set_title(prefix)
    # arr_axs[1].set_xlabel('night')
    
    list_chest_all=[]
    list_thigh_all=[]
    
    for instance in list_instances:
        list_chest_all.append(instance.getCountsChest())
        list_thigh_all.append(instance.getCountsThigh())
        
    arr_axs[0].boxplot(list_chest_all)
    arr_axs[1].boxplot(list_thigh_all)
    
    # arr_axs[0].boxplot([list_active_chest, list_active_thigh])
    # arr_axs[0].boxplot([list_active_chest, list_active_thigh])
    
    
    
    # arr_axs[1].plot(list_active_chest, 'o', label='chest', color='orange')
    # arr_axs[1].plot(list_active_thigh, 'o', label='thigh', color='blue')
    # arr_axs[0].plot(arr_nights, y_chest, label='chest', color='orange')
    # arr_axs[0].plot(arr_nights, y_thigh, label='thigh', color='blue')
    
    # arr_axs[1].plot(list_median_night_chest, label='chest')
    # arr_axs[1].plot(list_median_night_thigh, label='thigh')
    
    # arr_fig[0].canvas.draw()
    # arr_fig[1].canvas.draw()
    ## arr_fig[0].canvas.flush_events()
    
    cid_0  = arr_fig[0].canvas.mpl_connect('key_press_event', on_press)
    cid_1  = arr_fig[1].canvas.mpl_connect('key_press_event', on_press)
     
    ## show plot
    plt.legend()
    # plt.show()
    plt.ion()
    plt.show(block=True)
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

