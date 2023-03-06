# plotting actigraphy data
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D
import datetime
import os
from functions_tools import getSelectedData
from functions_tools import plot_night_zoom

####### main function ###########
if __name__== '__main__':

    # Get the list of all files and directories
    path = "../data/all_data_1s/"
    path_out = "../data/results_each_pose/"
    files_list = os.listdir(path)
    
    print("Files in '", path, "' :")
    # prints all files
    print(files_list)

    # the header in line 10 of the csv file
    header_location=10
    time_start='22:00:00'
    time_end='08:00:00'
    same_day=False

    incl_off ='Inclinometer Off'
    incl_sta ='Inclinometer Standing'
    incl_sit ='Inclinometer Sitting'
    incl_lyi ='Inclinometer Lying'
    vec_mag  ='Vector Magnitude'

    header_location=10
    for sample in files_list[:1]:
        print('file: ', sample)
        try:
            df1 = pd.read_csv(path+sample, header=header_location, decimal=',', usecols=['Date',' Time', incl_off, incl_sta, incl_sit, incl_lyi, vec_mag])
            # print(df1.info())

            # getting nights data
            df_nights = getSelectedData(df1, time_start, time_end, same_day)
            # print(df_nights.info())

            # plot 'Vector Magnitude' night by night
            nights_list = df_nights['night'].unique().tolist()
            # print('nights: ', nights_list)
            for night_num in nights_list[:1]:
                df_n = df_nights.loc[(df_nights['night']==night_num)]
                plot_night_zoom(df_n, incl_off, filename=sample)
            
        except ValueError:
            print('Problem reading the file', sample, '... it is skipped.')

    