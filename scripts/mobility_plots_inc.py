#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  mobility_plots.py
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
from itertools import cycle

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
# sns.set()


def plot_vma(df_vma_days, df_vma_nights, path_out, flag_save_fig):

    data_day = df_vma_days.assign(period='day')
    data_night = df_vma_nights.assign(period='night')
    cdf = pd.concat([data_day, data_night]) 
    # print(cdf)
    mdf = pd.melt(cdf, id_vars=['period'], var_name=['subject'])
    # print(mdf)
    
    fig, ax = plt.subplots()
    
    ax = sns.boxplot(data=mdf, x='subject', y="value", hue="period", palette="pastel")

    #########################
    hatches = ['//','//', '..','..', '//','..', '//','..', '//','..']
    for i, patch in enumerate(ax.patches):
        patch.set_hatch(hatches[i])
    #########################
    
    ax.set(ylim=(-0.05, 1.05))
    ax.set(xticklabels = (['P_1', 'P_2', 'P_3', 'P_4']))
    
    size_font = 20
    
    ax.set_xlabel("subject",fontsize=size_font)
    ax.set_ylabel("activity rate",fontsize=size_font)
    ax.tick_params(labelsize=size_font)

    plt.legend(fontsize=size_font, loc='upper center', bbox_to_anchor=(0.5, 1.18), ncol=2, fancybox=True, shadow=False)
    
    if flag_save_fig:
        plt.savefig(path_out+'boxplot_act.png', bbox_inches='tight')
    
    return 0


def plot_incl(df_inc_days, df_inc_nights, path_out, flag_save_fig):

    data_day = df_inc_days.assign(period='day')
    data_night = df_inc_nights.assign(period='night')
    cdf = pd.concat([data_day, data_night]) 
    print(cdf)
    mdf = pd.melt(cdf, id_vars=['period'], var_name=['subject'])
    print(mdf)
    
    fig, ax = plt.subplots()
    
    ax = sns.boxplot(data=mdf, x='subject', y="value", hue="period", palette="pastel")

    #########################
    hatches = ['//','//', '..','..', '//','..', '//','..', '//','..', '//','..', '//','..']
    for i, patch in enumerate(ax.patches):
        # print(i)
        patch.set_hatch(hatches[i])
    #########################
    
    ax.set(ylim=(-0.05, 1.05))
    ax.set(xticklabels = (['P_1', 'P_2', 'P_3', 'P_4']))
    
    size_font = 20
    
    ax.set_xlabel("subject",fontsize=size_font)
    ax.set_ylabel("posture changing rate",fontsize=size_font)
    ax.tick_params(labelsize=size_font)

    plt.legend(fontsize=size_font, loc='upper center', bbox_to_anchor=(0.5, 1.18), ncol=2, fancybox=True, shadow=False)
    
    if flag_save_fig:
        plt.savefig(path_out+'boxplots.png', bbox_inches='tight')
    
    return 0


def main(args):
    # print(f'mobility plots')
    path_in = "../data/projet_officiel/measurements/"
    path_out = "../data/projet_officiel/measurements/figures/inc2_"
    filenames = ['A006','A003','A026','A018']
    
    ## prefix could be: 1, 5, 10, 15, or 30 -- represents the applied window size in minutes (low-pass filter)
    prefix = args[1]
    
    df_vma_days = pd.DataFrame(columns=filenames)
    df_vma_nights = pd.DataFrame(columns=filenames)
    
    df_inc_days = pd.DataFrame(columns=filenames)
    df_inc_nights = pd.DataFrame(columns=filenames)
    
    for fn in filenames:
        # print(fn)
        fn_days   = path_in + 'inc2_' + fn +'_' + prefix + 'min_days.csv'
        fn_nights = path_in + 'inc2_' + fn +'_' + prefix + 'min_nights.csv'
    
        df_days = pd.read_csv(fn_days)  
        df_nights = pd.read_csv(fn_nights)  
    
        # print(f'df_days:\n{df_days}')
        # print(f'df_nights:\n{df_nights}')
        
        #### vma_mean days from index 1 to index 5
        # df_vma_days[fn] = df_days.iloc[1:6]['vma_mean'].to_list()
        #### vma_mean nights from index 0 to index 5
        # df_vma_nights[fn] = df_nights.iloc[0:6]['vma_mean'].to_list()
        #### inc_mean days from index 1 to index 5
        df_inc_days[fn] = df_days.iloc[1:6]['inc_mean'].to_list()
        #### inc_mean nights from index 0 to index 5
        df_inc_nights[fn] = df_nights.iloc[0:6]['inc_mean'].to_list()
        # print(df_vm_days)
        # print(df_vma_nights)
    
    # print(f'df_vma_days\n{df_vma_days}')
    # df_vma_days.boxplot()
    # df_vma_nights.boxplot()
    # df_inc_days.boxplot()
    # df_inc_nights.boxplot()
    # flag_save_fig=False
    # plot_vma(df_vma_days, df_vma_nights, path_out+prefix+'min_', flag_save_fig)
    flag_save_fig=True
    plot_incl(df_inc_days, df_inc_nights, path_out+prefix+'min_', flag_save_fig)
    
    # titanic = sns.load_dataset("titanic")
    # print(titanic)
    # Load the example tips dataset
    # tips = sns.load_dataset("tips")
    # print(tips)
    
    plt.show()
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
