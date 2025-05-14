import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import csv
import cv2
import sys

from class_actigraphy import Class_Actigraphy

# global variables
figure, ax = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(8, 6))

####################################
def get_time(df):

    date_time = df.iloc[0][0].split()
    
    day = date_time[0]
    date =  date_time[5] +'-'+ date_time[1] +'-'+ date_time[2]
    hour = date_time[3]
    am_pm = date_time[4]

    frame_time = hour.split(":")
    frame_time = np.array(frame_time).astype(int)

    total_sec = frame_time[0]*3600 + frame_time[1]*60 + frame_time[2] + (frame_time[3] / 1000 )
    # print(f"{frame_time} total_sec: {total_sec}")
    
    return total_sec

####################################
def resize_img(img):
    # print('Original Dimensions : ',img.shape)
 
    scale = 10 # percent of original size
    width = int(img.shape[1] * scale)
    height = int(img.shape[0] * scale)
    dim = (width, height)
    
    # resize image
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    
    # print('Resized Dimensions : ',resized.shape)
    return resized

####################################
def img_plot(df):

    frame = df.to_numpy()
    # print(f"frame numpy:\n{frame}")

    s_f = frame*2.5
    s_f[s_f>255.0]=255.0
    s_f = s_f.astype(np.uint8)
    s_f=resize_img(s_f)
    
    colormap = plt.get_cmap('plasma')
    heatmap = (colormap(s_f) * 2**16).astype(np.uint16)[:,:,:3]
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_RGB2BGR)

    # Use Flip code 0 to flip vertically 
    heatmap = cv2.flip(heatmap, -1) 
    # heatmap = cv2.flip(heatmap, 1) 

    cv2.imshow('image',heatmap)
    cv2.waitKey(1)

    return 0

#######################################
def plot_actigraphy(df_chest, df_thigh, ini_time, frame):
    global figure, ax
    ax[0].cla()
    ax[1].cla()

    time_sec = 'time_sec'
    vec_mag  ='Vector Magnitude'

    time_chest = df_chest.df1[time_sec].to_numpy()
    time_thigh = df_thigh.df1[time_sec].to_numpy()

    ax[0].plot(time_chest, df_chest.df1[vec_mag].to_numpy())
    ax[1].plot(time_thigh, df_thigh.df1[vec_mag].to_numpy())

    ax[0].set_xlim([ini_time-60, ini_time+300])

    ax[0].legend(['chest'])
    ax[1].legend(['thigh'])

    # only one line may be specified; full height
    ax[0].axvline(x = frame, color = 'r', label = 'axvline - full height')
    ax[1].axvline(x = frame, color = 'r', label = 'axvline - full height')

    figure.canvas.draw()
    figure.canvas.flush_events()

    return

##########################################
#define the events for the mouse_click.
def mouse_interact(event, x, y, flags, param):
    global drawing, x0,y0,x1,y1
      
    # to check if left mouse 
    # button was clicked
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        x0,y0=x,y
        # print('x0,y0:', x0,y0)
    
    elif event == cv2.EVENT_MOUSEMOVE and drawing == True:
        x1,y1=x,y
        print('x0,y0 x1,y1:', x0,y0, x1,y1)
    
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
    
    else:
        pass
    
    return

####### main function ###########
def main(args):
    
    # path_file_csv = args[1]
    # print(f"path_file_csv: {path_file_csv}")

    

    path = "../../data/matress_test_may2025/"

    filename_chest =  "actig_chest"
    filename_thigh =  "actig_thigh"

    obj_chest = Class_Actigraphy(filename_chest)
    obj_thigh = Class_Actigraphy(filename_thigh)

    try:
        obj_chest.openFile(path, filename_chest+'.csv')
        obj_thigh.openFile(path, filename_thigh+'.csv')
    except:
        print(f'Problem reading the file actig_chest.csv or actig_thigh.csv')
        return 0

    print('actigraphy data reading success!')

    # print(f"obj_chest:\n{obj_chest.df1}")
    # print(f"obj_thigh:\n{obj_thigh.df1}")



    ## load one frame at a time
    ## first read the line that describe date and time of frame's acquisition
    ## second read matrix of data (64x27)

    filename_mat = path + "gerar_mat_test1.csv"
    # filename_mat = path + "islam_mat_test1.csv"

    frames =  np.arange(0,10000,5)
    size = 66 # number of rows per frame (including two lines of header and 64 of data)

    # activate interactive mouse actions on window
    cv2.namedWindow('image')
    # cv2.setMouseCallback('image',mouse_interact)

    # to run GUI event loop
    plt.ion()
    plt.show()

    ## read line of time
    df_date = pd.read_csv(filename_mat, nrows= 1, skiprows=1, header=None)
    ## get the acquisition time ([hh,mm,ss,mm])
    ini_time = get_time(df_date)
    print(f"ini time: {ini_time}")

    for idx in frames:
        try:
            ## read line of time
            df_date = pd.read_csv(filename_mat, nrows= 1, skiprows=1+(idx*size), header=None)
            # print(f"time: {df_date.iloc[0][0]}")

            ## read matix of data
            df_data = pd.read_csv(filename_mat, nrows=64, skiprows=2+(idx*size), delim_whitespace=True, header=None)
            # print(f"data:\n{df_data}")
            
            ## get the acquisition time ([hh,mm,ss,mm])
            total_sec = get_time(df_date)

            # plot_actigraphy signals
            plot_actigraphy(obj_chest, obj_thigh, ini_time, total_sec)

            ## plot image
            img_plot(df_data)
        except:
            break
    
    print(f"end time: {total_sec}")


    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return 0

    

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))