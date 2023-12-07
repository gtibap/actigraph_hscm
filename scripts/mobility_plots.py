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

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def plot_boxplots(df_vma_days, df_vma_nights, df_inc_days, df_inc_nights):

    data_day = df_vma_days.assign(period='day')
    data_night = df_vma_nights.assign(period='night')
    cdf = pd.concat([data_day, data_night]) 
    print(cdf)
    mdf = pd.melt(cdf, id_vars=['period'], var_name=['subject'])
    print(mdf)
    ax = sns.boxplot(x='subject', y="value", hue="period", data=mdf)

    # data_day = df_vma_days.assign(Location=1)
    # data_night = df_vma_nights.assign(Location=2)
    # data3 = pd.DataFrame(np.random.rand(17,3)+0.4, columns=['A','B','C']).assign(Location=3)
 
    # cdf = pd.concat([data_day, data_night])    
    # mdf = pd.melt(cdf, id_vars=['Location'], var_name=['Subject'])
    # print(mdf.head())
    # print(mdf)

    #    Location Letter     value
    # 0         1      A  0.223565
    # 1         1      A  0.515797
    # 2         1      A  0.377588
    # 3         1      A  0.687614
    # 4         1      A  0.094116

    # ax = sns.boxplot(x="Location", y="value", hue="Subject", data=cdf)   

    return 0

def main(args):
    # print(f'mobility plots')
    path_in = "../data/projet_officiel/measurements/"
    filenames = ['A006','A003','A026','A018']
    
    df_vma_days = pd.DataFrame(columns=filenames)
    df_vma_nights = pd.DataFrame(columns=filenames)
    
    df_inc_days = pd.DataFrame(columns=filenames)
    df_inc_nights = pd.DataFrame(columns=filenames)
    
    for fn in filenames:
        print(fn)
        fn_days   = path_in + fn + '_days.csv'
        fn_nights = path_in + fn + '_nights.csv'
    
        df_days = pd.read_csv(fn_days)  
        df_nights = pd.read_csv(fn_nights)  
    
        # print(f'df_days:\n{df_days}')
        # print(f'df_nights:\n{df_nights}')
        
        #### vma_mean days from index 1 to index 5
        df_vma_days[fn] = df_days.iloc[1:6]['vma_mean'].to_list()
        #### vma_mean nights from index 0 to index 5
        df_vma_nights[fn] = df_nights.iloc[0:6]['vma_mean'].to_list()
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
    
    plot_boxplots(df_vma_days, df_vma_nights, df_inc_days, df_inc_nights)
    
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
