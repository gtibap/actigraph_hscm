#!/usr/bin/env python
# -*- coding: utf-8 -*-

from class_counting_paper import Counting_Actigraphy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# global instances
obj_chest=Counting_Actigraphy()
obj_thigh=Counting_Actigraphy()

vec_mag  ='Vector Magnitude'
incl_off ='Inclinometer Off'
incl_sta ='Inclinometer Standing'
incl_sit ='Inclinometer Sitting'
incl_lyi ='Inclinometer Lying'


def plotBoxPlot(list_data, list_name_cols, prefix, title):
    
    # arr_activity_chest = np.array(list_activity_chest)
    arr_activity_thigh = np.array(list_data)

    # print('activity chest:')
    # print(arr_activity_chest)
    # print('activity thigh:')
    # print(arr_activity_thigh)

    # arr_activity_chest = np.transpose(arr_activity_chest)
    arr_activity_thigh = np.transpose(arr_activity_thigh)

    # list_nights_chest = np.arange(1,len(arr_activity_chest)+1)
    list_nights_thigh = np.arange(1,len(arr_activity_thigh)+1)

    # print(list_nights_chest, list_nights_thigh)

    # df_activity_chest = pd.DataFrame(data = arr_activity_chest,
                                     # index = list_nights_chest,
                                     # columns=list_name_cols)
                                     
    df_activity_thigh = pd.DataFrame(data = arr_activity_thigh,
                                     index = list_nights_thigh,
                                     columns=list_name_cols)

    # df_activity_chest.index.name = 'night'
    df_activity_thigh.index.name = 'night'

    # print(df_activity_chest)
    # print(df_activity_thigh)
    col_names = np.array(df_activity_thigh.columns)

    fig, ax = plt.subplots(nrows=1, ncols=1)
    # ax=df_activity_thigh.boxplot(column=col_names[7:].tolist())
    ax=df_activity_thigh.boxplot()
    ax.set_ylim(-10, 150)
    ax.set_ylabel('magnitude')
    ax.set_xlabel('window size (min)')
    ax.set_title(f'{title} {prefix}')
    
    return 0


def activityDataFrame(list_data, list_name_cols):
    
    arr_activity = np.array(list_data)
    arr_activity = np.transpose(arr_activity)
    list_nights = np.arange(1,len(arr_activity)+1)
    
    df_activity = pd.DataFrame(data = arr_activity,
                              index = list_nights,
                             columns=list_name_cols)

    df_activity.index.name = 'night'
    
    return df_activity
    
    


def main(args):
    
    path = "../data/projet_officiel/"
    path_out = "../data/projet_officiel_counting_2/"
    path_fig = "../data/projet_officiel/figures/"
    # prefix = 'A010'
    prefix = args[1]
    sw_val = int(args[2])
    lpf_val = float(args[3])
    
    files_list=[prefix+'_chest.csv', prefix+'_thigh.csv']
    files_list_out_rep=[prefix+'_chest_repositioning.csv', prefix+'_thigh_repositioning.csv']
    files_list_out_act=[prefix+'_chest_activity.csv', prefix+'_thigh_activity.csv']
    
    dict_df_rep_chest = {}
    dict_df_rep_thigh = {}
    
    ## adjust font size matplotlib figures
    plt.rcParams.update({'font.size': 12})
    
    # print('files_list: ', files_list)
    
    flag_read=False
    
    try:
        obj_chest.openFile(path, files_list[0])
        # obj_thigh.openFile(path, files_list[1])
        flag_read=True
    except ValueError:
        print(f'Problem reading the file {self.filename}.')
        flag_read=False

    if flag_read==True:
        print('reading success!')
        
        #################
        ## repositioning start
        list_repos_chest=[]
        list_repos_thigh=[]
        list_names_repos=[]
        
        ############################
        ## repositioning estimation
        print(f'repositioning estimation')
        list_repo_chest = []
        list_repo_thigh = []
        list_compl_chest = []
        list_compl_thigh = []
        list_name_cols = []
        
        ###############
        # obj_chest.plotVM()
        ###############
        
        # #################################
        # ## original data inclinometers ##
        # obj_chest.inclinometers_original()
        # obj_chest.nightCounts('original')
        # plt.rcParams.update({'font.size': 12})
        # save_flag=False
        # obj_chest.plotActigraphyNormal(path_fig+prefix+'chest.png', save_flag, prefix+' chest')
        # plt.rcParams.update({'font.size': 12})
        # ## original data inclinometers ##
        # #################################
        # #################################
        # ## original data inclinometers ##
        # obj_thigh.inclinometers_original()
        # obj_thigh.nightCounts('original')
        # plt.rcParams.update({'font.size': 12})
        # save_flag=False
        # obj_thigh.plotActigraphyNormal(path_fig+prefix+'thigh.png', save_flag, prefix+' thigh')
        # plt.rcParams.update({'font.size': 12})
        # ## original data inclinometers ##
        # #################################
        
        # obj_chest.plotPosChanging('original')
        # obj_chest.plotComplianceRep()
        
        # for i in np.arange(0,1):
        # print(f'iteration {i}')
        # win_size_minutes=2**i ## min
        
        ##################################
        # win_size_minutes=5 ## min
        # print(f'window size: {win_size_minutes}')
        ##################################
        
        ## sliding windows ##
        # obj_chest.inclinometers_sliding_window(win_size_minutes)
        # obj_chest.nightCounts('sw')
        # obj_chest.plot_Inclinometers('sw')
        # obj_chest.plotPosChanging('sw')
        
        ## wavelet transform ##
        # obj_chest.inclinometers_wavelet_transform(win_size_minutes)
        # obj_chest.nightCounts('wt')
        # obj_chest.plot_Inclinometers('wt')
        # obj_chest.plotPosChanging('wt')
        
        ## mathematical morphology ##
        # obj_chest.inclinometer_mat_morpho(win_size_minutes)
        # obj_chest.nightCounts('mm')
        # obj_chest.plot_Inclinometers('mm')
        # obj_chest.plotPosChanging('mm')
        
        # #######################
        # ## low pass filter ##
        # obj_chest.inclinometers_low_pass_filter(win_size_minutes)
        # obj_chest.nightCounts('lpf')
        # plt.rcParams.update({'font.size': 12})
        # save_flag=False
        # obj_chest.plot_Inclinometers('lpf', path_fig+prefix+'lpf_chest.png', save_flag)
        # plt.rcParams.update({'font.size': 18})
        # save_flag=False
        # obj_chest.plotPosChanging('lpf', path_fig+prefix+'pos_chest.png', save_flag)
        # plt.rcParams.update({'font.size': 12})
        # save_flag=True
        # obj_chest.compliance_full('lpf', win_size_minutes, path_fig+prefix+'com_chest.png', save_flag)
        # ## low pass filter ##
        # ##########################
        
        # obj_chest.plotComplianceRep()
        
        # obj_thigh.inclinometers_sliding_window(win_size_minutes)
        
        

        # obj_thigh.nightCounts()

        # df_counts_chest=obj_chest.getNightCounts()
        # df_counts_thigh=obj_thigh.getNightCounts()
        
        ## total number of repositioning for all nights for every window size
        # list_repo_chest.append(df_counts_chest['rep_total'].tolist()) 
        # list_repo_thigh.append(df_counts_thigh['rep_total'].tolist()) 
        
        # list_compl_chest.append(df_counts_chest['compliance(%)'].tolist()) 
        # list_compl_thigh.append(df_counts_thigh['compliance(%)'].tolist()) 
        
        # list_name_cols.append(str(win_size_minutes))
        
        # print(f'list_repo_chest:\n{list_repo_chest}')
        # plotBoxPlot(list_repo_chest, list_name_cols, prefix, 'repositioning')
        # plotBoxPlot(list_compl_chest, list_name_cols, prefix, 'compliance repositioning')
        
            # obj_chest.plotComplianceRep()
            # obj_thigh.plotComplianceRep()
        
        # obj_chest.plotPosChanging()
        # obj_thigh.plotPosChanging()
        
        ## write csv files 
        # df_counts_chest.to_csv(path_out+files_list_out_rep[0], index=False)
        # df_counts_thigh.to_csv(path_out+files_list_out_rep[1], index=False)
        ## repositioning estimation
        ############################
        
        
        #############################
        ## vector magnitude activity        
        # min_value=1 ## counts
        # min_samples_window = 1 ## at least 2 samples to consider it as a valid activity
        # win_size=15 ## min
        ## get values using several window sizes; provides info activity frequency during each night
        ## windows' size base of 2 (from 1min [2**0] to 128min [2**7]): 1,2,4,8,16,32,64,128
        
        
        # list_activity_chest = []
        # list_activity_thigh = []
        # list_name_cols = []

        save_flag=True
        obj_chest.plotVM_3(path_fig+prefix+'_sw_chest_out', save_flag, prefix+'_sw_chest')
        # obj_thigh.plotVM_2(path_fig+prefix+'_thigh', save_flag, prefix+'_thigh')
        
        ###################################
        win_size_1 = sw_val # min applied to vector magnitude
        win_size_2 = 120 # min applied to vector magnitude
        win_size_3 = lpf_val # min applied to inclinometers
        
        print(f'window size: {win_size_1}')
        print(f'low-pass filter: {win_size_3}')
        
        path_measurements_out = "../data/projet_officiel/measurements/"
        
        # obj_chest.mobility_vma(win_size_1, win_size_2, path_measurements_out+'vma_'+prefix+'_'+str(win_size_1)+'min')
        # obj_chest.mobility_inc(win_size_3, path_measurements_out+'inc_'+prefix+'_'+str(int(win_size_3))+'min')
        obj_chest.mobility_inc_2(win_size_3, path_measurements_out+'inc2_'+prefix+'_'+str(int(win_size_3))+'min')
        ###################################
        
        
        
        # obj_chest.vecMagCounting(min_value, win_size, min_samples_window)
        # obj_chest.plotVectorMagnitude()
        
        
        
        flag_activity=False

        if flag_activity:
        
            # list_win_size = [1, 5, 15, 30, 60, 120, 180]
            list_win_size = [15]
            print('activity estimation for')
            # for i in np.arange(0,9):
            for i in list_win_size:
                # win_size=2**i ## min
                win_size=i ## min
                # win_size=30 ## min
                # win_size=15*i ## min
                print(f'window size: {win_size}')
                list_activity_chest.append(obj_chest.vecMagCounting(min_value, win_size, min_samples_window))
                # list_activity_thigh.append(obj_thigh.vecMagCounting(min_value, win_size, min_samples_window))
                
                # list_name_cols.append(str(win_size)+'(min)')
                list_name_cols.append(str(win_size))
                
            df_activity_chest = activityDataFrame(list_activity_chest, list_name_cols)
            # df_activity_thigh = activityDataFrame(list_activity_thigh, list_name_cols)
            
            # df_activity_chest.to_csv(path_out+files_list_out_act[0])
            # df_activity_thigh.to_csv(path_out+files_list_out_act[1])
            
            print(f'df_activity_chest:\n{df_activity_chest}\n{df_activity_chest.T}')
            # print(f'df_activity_thigh:\n{df_activity_thigh}\n{df_activity_thigh.T}')
            
            # df_activity_chest_T = df_activity_chest.T
            fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6, 6))
            # df_activity_chest.T.plot(ax=ax)
            # df_activity_thigh.T.plot(ax=ax)
            
            y_ini = -0.02
            y_end =  1.02

            ax.set_ylim(y_ini,y_end)
            
            plt.tight_layout()
            
            df_activity_chest.T.plot(ax=ax)
            # fig.savefig(f'{path_fig}act_{prefix}_chest.png')
            
            # df_activity_thigh.T.plot(ax=ax)
            # fig.savefig(f'{path_fig}act_{prefix}_thigh.png')
        
        ## vector magnitude activity
        ############################
        
        # plotBoxPlot(list_activity_chest, list_name_cols, prefix, 'activity')
        # plotBoxPlot(list_activity_thigh, list_name_cols, prefix, 'activity')
        
        ## plot position changing
        # obj_chest.plotDWTInclinometers()
        # obj_thigh.plotDWTInclinometers()
  
        # ## plot vector magnitude and inclinometers; all days and nights (original data)
        # obj_chest.plotActigraphy()
        # obj_thigh.plotActigraphy()
        
        
        
        # obj_chest.plotDWTInclinometers()
        
        # obj_chest.plotVectorMagnitude()
        # obj_thigh.plotVectorMagnitude()
        
        # obj_chest.plotVM()
        
        plt.ion()
        plt.show(block=True)
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
