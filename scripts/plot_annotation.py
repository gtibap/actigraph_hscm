# plotting actigraphy data
import numpy as np
from numpy.fft import fft
from scipy.interpolate import UnivariateSpline
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D
import datetime
import os
import sys


from functions_tools import getSelectedData
from functions_tools import plot_night_zoom

############
# global variables 
incl_off ='Inclinometer Off'
incl_sta ='Inclinometer Standing'
incl_sit ='Inclinometer Sitting'
incl_lyi ='Inclinometer Lying'
vec_mag  ='Vector Magnitude'

fig, axes = plt.subplots(nrows=5, ncols=1, sharex=True)

# xl = axes[1].set_xlabel('time (s)')
idx_ini=np.array([])
idx_end=np.array([])
values_mag=np.array([])
idx_number=0
xmin=0
xmax=1


#############

def on_press(event):
    global idx_number, xmin, xmax

    print('press', event.key)
    sys.stdout.flush()
    if event.key == 'x':
        # visible = xl.get_visible()
        # xl.set_visible(not visible)
        xmin= idx_ini[idx_number] 
        xmax=idx_end[idx_number]  
        # delta_t = idx_end[idx_number]-idx_ini[idx_number]
        delta_t = xmax-xmin

        # print('min max: ', type(xmin), type(xmax), xmin, xmax)
        # print('vec_mag[xmin:xmax]: ', values_mag[xmin:xmax])
        ampl = np.amax(values_mag[xmin:xmax])
        # rms_t = np.sqrt(np.mean(values_mag[xmin:xmax]**2)) * delta_t
        average_t = np.mean(values_mag[xmin:xmax]) * delta_t


        # print('xmin, xmax: ',xmin, xmax)
        
        # x-range of visualization 
        width = 240
        axes[0].set_xlim([xmin- width, xmax+ width]) # an additional window of 10 min (600s) to the left
        axes[0].set_title("duration "+str(delta_t)+'s '+' amplitude:'+str(ampl) + ' rms:'+ str(round(average_t, 2)))

        # underlining the current signal segment
        offset = -5
        axes[0].plot(np.arange(xmin-1,xmax+1), offset*np.ones((xmax-xmin+2)) , 'm')

        # redrawing the plot
        fig.canvas.draw()
        
        # white underlining the previous signal segment
        axes[0].plot(np.arange(xmin-1,xmax+1), offset*np.ones((xmax-xmin+2)) , 'w')
        idx_number+=1

    elif event.key == 'e':
        print('espontaneous motion')
        
    



def plot_active_seg(df_n):
    global values_mag

    values_mag = df_n[vec_mag].to_numpy()
    values_off = df_n[incl_off].to_numpy()
    values_lyi = df_n[incl_lyi].to_numpy()
    values_sta = df_n[incl_sta].to_numpy()
    values_sit = df_n[incl_sit].to_numpy()

    fig.canvas.mpl_connect('key_press_event', on_press)    

    # rms_values = window_rms(values_mag, 2)
    
    # x=np.arange(len(values_mag))
    # f = UnivariateSpline(x, values_mag, s=10)

    axes[0].plot(values_mag)
    
    # axes[1].plot(f(x))


    axes[1].plot(values_off)
    axes[2].plot(values_lyi)
    axes[3].plot(values_sit)
    axes[4].plot(values_sta)

    axes[4].set_xlabel('time (s)')

    axes[0].set_ylabel('vec. mag')
    axes[1].set_ylabel('inc. off')
    axes[2].set_ylabel('inc. lyi')
    axes[3].set_ylabel('inc. sit')
    axes[4].set_ylabel('inc. sta')

    plt.show()
 
    return


def window_rms(a, window_size):
  a2 = np.power(a,2)
  window = np.ones(window_size)/float(window_size)
  return np.sqrt(np.convolve(a2, window, 'valid'))


def window_mean(a, window_size):
  window = np.ones(window_size)/float(window_size)
  return np.convolve(a, window, 'valid')

####### main function ###########
if __name__== '__main__':

    # Get the list of all files and directories
    path = "../data/all_data_1s/"
    path_results_in = "../data/results_motion/"
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

    header_location=10
    for sample in files_list[:1]:
        print('file: ', sample)
        try:
            df1 = pd.read_csv(path+sample, header=header_location, decimal=',', usecols=['Date',' Time', incl_off, incl_lyi, incl_sta, incl_sit ,vec_mag])
            # print(df1.info())

            # getting nights data
            df_nights = getSelectedData(df1, time_start, time_end, same_day)
            # print(df_nights.info())

            # indexes start and end of each activity sector in the Vector Magnitude
            df_active_nights = pd.read_csv(path_results_in+'active_'+sample)
            # print(df_active_nights.info())

            # plot 'Vector Magnitude' night by night
            nights_list = df_nights['night'].unique().tolist()
            # print('nights: ', nights_list)
            for night_num in nights_list[:1]:
                df_n = df_nights.loc[(df_nights['night']==night_num)]


                df_a = df_active_nights.loc[(df_active_nights['night']==night_num)]
                idx_ini = df_a['t_ini'].to_numpy()
                idx_end = df_a['t_end'].to_numpy()
                # print(df_n.info())
                # print(df_a.info())

                plot_active_seg(df_n)


                # plot_night_zoom(df_n, incl_off, filename=sample)
            
        except ValueError:
            print('Problem reading the file', sample, '... it is skipped.')

    