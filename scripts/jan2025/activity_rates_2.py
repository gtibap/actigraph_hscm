#!/usr/bin/env python
# -*- coding: utf-8 -*-

from class_activity_rates import Counting_Actigraphy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# # global instances
# obj_chest=Counting_Actigraphy('chest')
# obj_thigh=Counting_Actigraphy('thigh')

vec_mag  ='Vector Magnitude'
incl_off ='Inclinometer Off'
incl_sta ='Inclinometer Standing'
incl_sit ='Inclinometer Sitting'
incl_lyi ='Inclinometer Lying'

label_day_night = 'day_night'
vma_b='vma_b'

label_time = ' Time'
label_date = 'Date'


def activityDataFrame(list_data, list_name_cols):
    
    arr_activity = np.array(list_data)
    arr_activity = np.transpose(arr_activity)
    list_nights = np.arange(1,len(arr_activity)+1)
    
    df_activity = pd.DataFrame(data = arr_activity,
                              index = list_nights,
                             columns=list_name_cols)

    df_activity.index.name = 'night'
    
    return df_activity


def activity_rates_cal(obj_chest, obj_thigh, prefix):

    df_chest = obj_chest.get_df_inclinometers()
    df_thigh = obj_thigh.get_df_inclinometers()

    ## labels days and nights from the chest
    labels_chest = df_chest[label_day_night].unique().tolist()
    ## only labels nights from the chest
    lc_nights = [lc for lc in labels_chest if lc.startswith('n')]
    print(f'periods chest: {lc_nights}')
    
    df_th_nights = pd.DataFrame()

    ## labels nights
    for label in lc_nights:
        ## dataframes of selected night (label) from chest and thigh
        df_ch = df_chest.loc[df_chest[label_day_night]== label]
        df_th = df_thigh.loc[df_thigh[label_day_night]== label]
        ## date first row for comparison
        date_ch = df_ch.iloc[0][label_date]
        date_th = df_th.iloc[0][label_date]
       
        # each night should correspond with same dates for chest and thigh
        if date_ch == date_th:

            ## inclinometers off and sitting only from the chest
            arr_off = df_ch[incl_off].to_numpy()
            arr_sit = df_ch[incl_sit].to_numpy()
            ## fusion of inclinometers off and sitting
            arr_incl = arr_off | arr_sit
            ## indexes when the inclinometer off or sit is active
            idx = np.argwhere(arr_incl > 0).flatten()

            ## activity rates from the chest and the thigh
            arr_ch = df_ch[vma_b].to_numpy()
            arr_th = df_th[vma_b].to_numpy()

            ## activity rate from chest and thigh when inclinometer off or sit is active
            arr_ar_ch = arr_ch[idx]
            arr_ar_th = arr_th[idx]

            ## median value of activity rates per night from chest and thigh
            mean_ar_ch = round(np.mean(arr_ch), 2)
            mean_ar_th = round(np.mean(arr_th), 2)

            median_ch = round(np.median(arr_ar_ch), 2)
            median_th = round(np.median(arr_ar_th), 2)
            mean_ch = round(np.mean(arr_ar_ch), 2)
            mean_th = round(np.mean(arr_ar_th), 2)
            std_ch=round(np.std(arr_ar_ch), 2)
            std_th=round(np.std(arr_ar_th), 2)

            # print(f'arr_incl_ar: {arr_incl_ar}')
            # print(f'median: {median_value}')
            # print(f'percentage: max:{arr_incl.max()}, mean:{arr_incl.mean()} ')

            ## calculate percentage of inclinometers off and lying during the night
            incl_percentage = round(100*arr_incl.mean(),2)
            ## creating dataframe to save info activity rates
            # df_act = pd.DataFrame([[prefix, label, incl_percentage, median_ch, median_th, mean_ch, mean_th, std_ch, std_th, mean_ar_ch, mean_ar_th]], columns=['id', 'night','off_sit_percentage', 'act_rates_chest_off_sit(median)','act_rates_thigh_off_sit(median)', 'act_rates_chest_off_sit(mean)','act_rates_thigh_off_sit(mean)','std_chest_off_sit', 'std_thigh_off_sit', 'act_rates_chest_all_night(median)','act_rates_thigh_all_night(median)' ])
            df_act = pd.DataFrame([[prefix, label, incl_percentage, mean_ch, mean_th, mean_ar_ch, mean_ar_th]], columns=['id', 'night','off_sit_percentage', 'act_rates_chest_off_sit(mean)','act_rates_thigh_off_sit(mean)', 'act_rates_chest_all_night(mean)','act_rates_thigh_all_night(mean)' ])
            # print(f'{df_act}')

            df_th_nights = pd.concat([df_th_nights, df_act], ignore_index=True)

            # print(f'off: {arr_off}')
            # print(f'sit: {arr_sit}')

            # print(f'activity rate: {arr_ar}')
        else:
            print('Error: mismatch between dates of nights {label} from chest and thigh.')
            return 0

        # df_date = df_chest.loc[df_chest[label_date]== date]
    # print(f'{df_th_nights}')
    return df_th_nights

############################
def wiggling(obj_chest, obj_thigh, prefix):

    df_chest = obj_chest.get_df_inclinometers()
    df_thigh = obj_thigh.get_df_inclinometers()

    ## labels days and nights from the chest
    labels_chest = df_chest[label_day_night].unique().tolist()
    ## only labels nights from the chest
    lc_nights = [lc for lc in labels_chest if lc.startswith('n')]
    print(f'periods chest: {lc_nights}')
    
    df_th_nights = pd.DataFrame()

    ## labels nights
    for label in lc_nights:
        ## dataframes of selected night (label) from chest and thigh
        df_ch = df_chest.loc[df_chest[label_day_night]== label]
        df_th = df_thigh.loc[df_thigh[label_day_night]== label]
        ## date first row for comparison
        date_ch = df_ch.iloc[0][label_date]
        date_th = df_th.iloc[0][label_date]
       
        # each night should correspond with same dates for chest and thigh
        if date_ch == date_th:

            ## inclinometers off and sitting only from the chest
            arr_off = df_ch[incl_off].to_numpy()
            arr_sit = df_ch[incl_sit].to_numpy()
            ## fusion of inclinometers off and sitting
            arr_incl = arr_off | arr_sit

            ## identify active segments from arr_incl, which includes off + sit
            ini_idx, end_idx = indexes_incl(arr_incl)
            # print(f'{prefix} indexes {label}:\n{ini_idx}\n{end_idx}')
            vma_ch = df_ch[vec_mag].to_numpy()
            vma_th = df_th[vec_mag].to_numpy()

            count_wigg(vma_ch, vma_th, ini_idx, end_idx)

        else:
            print('Error: mismatch between dates of nights {label} from chest and thigh.')
            return 0

    return

def indexes_incl(arr):

    arr_com = (arr[:-1] != arr[1:])
    arr_ini = arr_com & (arr[:-1]==0)
    arr_end = arr_com & (arr[:-1]==1)

    ## adding one element at the begining of the array
    arr_ini = np.concatenate((0, arr_ini), axis=None)
    arr_end = np.concatenate((0, arr_end), axis=None)

    ini_idx = np.argwhere(arr_ini==True).flatten()
    # print(f'lyi_idx: {lyi_idx}')
    ## find index where current lying finishes
    # arr_acc = arr_b_a | arr_b_c | arr_b_d
    end_idx = np.argwhere(arr_end==True).flatten()
    # print(f'arr_idx: {arr_idx}')

    ## adding value to begin if arr[0]==1
    if arr[0]==1:
        ini_idx = np.concatenate((0, ini_idx), axis=None)
    else:
        pass

    ## adding value to end if arr[-1]==1
    if arr[-1]==1:
        end_idx = np.concatenate((end_idx,len(arr)), axis=None)
    else:
        pass

    return ini_idx, end_idx


def count_wigg(vma_ch, vma_th, ini_idx, end_idx):
    ## for each lying segment find its respective end
    df_out = pd.DataFrame([])
    for id0 in ini_idx:
        ## all idx greater than id where lying changes
        idx = end_idx[end_idx > id0]
        ## minimum length lying segment
        if len(idx) > 0:
            id1 = np.min(idx)

            arr_seg_ch = vma_ch[id0:id1]
            arr_seg_th = vma_th[id0:id1]

            


            # delta = id1 - id0
            # ## when it start and when it finish: day or night and number (for instance d0, n0)
            # period_0 = arr_period[id0]
            # period_1 = arr_period[id1]

            # df_row = pd.DataFrame([[delta, period_0, period_1]],columns=['length','begin','end'])

            # df_out = pd.concat([df_out, df_row], ignore_index=True) 
        else:
            pass

    return df_out


############################
## plotting functions

def on_press(event):
    # print('press', event.key)
    sys.stdout.flush()
    
    if event.key == 'x':
        plt.close('all')
    else:
        pass
    return 0

def plot_activity_rates(id_objs):

    fig, ax = plt.subplots(nrows=len(id_objs), ncols=1, sharex=True, figsize=(12, 6))
    fig.canvas.mpl_connect('key_press_event', on_press)

    y_ini= -0.1
    y_end=  1.1

    for i, obj in enumerate(id_objs):

        df1 = obj.get_df_inclinometers()
        ## plot days and nights with different colors
        labels_list = df1[label_day_night].unique().tolist()
        # print(f'labels_list: {labels_list}')
        id_ini = 0

        for label in labels_list:
            df_period = df1[df1[label_day_night]== label]

            arr_ar = df_period[vma_b].to_list()

            ids=np.arange(id_ini, id_ini+len(df_period))
                
            if label.startswith('d'):
                ax[i].plot(ids, arr_ar, color='tab:orange', label='')
            else:
                ax[i].plot(ids, arr_ar, color='tab:blue', label='')

            id_ini=id_ini+len(df_period)
            
            # vertical line
            ax[i].vlines(x=[id_ini], ymin=y_ini, ymax=y_end, colors='purple', ls='--', lw=1, label='')

        ax[i].set_ylim(y_ini,y_end)
        ax[i].set_title(obj.getName())
        ax[i].set_ylabel('activity_rate')
    ax[-1].set_xlabel('samples')

    return 0
   

def main(args):
    
    path = "../data/"
    path_out = "../data/countingactivity/"
    
    #patient_list = ['A01','A02','A03','A04','A13','A49','A50','A51','A48']
    # patient_list = ['A44','A32',]
    patient_list = ['A44',]
    
    df_all = pd.DataFrame()

    for name in patient_list:
        
        prefix = name

        files_list=[prefix+'_chest.csv', prefix+'_thigh.csv']
        print('files_list: ', files_list)

        obj_chest=Counting_Actigraphy(prefix+' chest')
        obj_thigh=Counting_Actigraphy(prefix+' thigh')

        flag_read=False    
        try:
            obj_chest.openFile(path, files_list[0])
            obj_thigh.openFile(path, files_list[1])
            flag_read=True
        except ValueError:
            print(f'Problem reading the file {prefix}.')
            flag_read=False

        if flag_read==True:
            print('reading success!')
            
            ############################
            ## filtering to remove short transitory posture changes
            print(f'repositioning estimation')
            win_size_minutes = 0.5 # minutes
            print(f'window size: {win_size_minutes}')
            obj_chest.inclinometers_sliding_window(win_size_minutes)
            obj_thigh.inclinometers_sliding_window(win_size_minutes)

            ## plot inclinometers before and after the "inclinometers_sliding_window" function for comparison
            # x_min = 0
            # x_max = x_min + 3600*24*7
            # obj_chest.plotActigraphy(0,x_min,x_max)
            # obj_chest.plotActigraphy(1,x_min,x_max)
            # plt.show()
            # return 0
            
            #############################
            ## activity rates
            win_a =   10 # minutes
            win_b =  180 # minutes

            obj_chest.vma_processing(win_a, win_b)
            obj_thigh.vma_processing(win_a, win_b)

            # plot activity rates chest and thigh
            id_objs = [obj_chest, obj_thigh]
            plot_activity_rates(id_objs)
            # plt.show()
            ## activity rates
            #############################

            #############################
            ## activity rates when Inclinometer_off is ON (when the patients are lying in their back)
            df_act_rates = activity_rates_cal(obj_chest, obj_thigh, prefix)
            print(f'df_act_rates:\n{df_act_rates}')

            ## wiggling off + sit
            wiggling(obj_chest, obj_thigh, prefix)


            #df_all = pd.concat([df_all, df_act_rates],ignore_index=True)
            # df_act_rates.to_csv(path_out+name+'_act_rates.csv', index=False)

            ## activity rates when Inclinometer_off is ON (when the patients are lying in their back)
            #############################
            
            # # ## plot position changing
            # obj_chest.plotDWTInclinometers()
            # obj_thigh.plotDWTInclinometers()
    
            # # ## plot vector magnitude and inclinometers; all days and nights (original data)
            # obj_chest.plotActigraphy()
            # obj_thigh.plotActigraphy()
                    
            plt.ion()
            plt.show(block=True)
        else:
            pass
        
    ## save data in disk
    #df_all.to_csv(path_out+'act_rates.csv', index=False)
    # print(f'df_act_rates:\n{df_act_rates}')
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
