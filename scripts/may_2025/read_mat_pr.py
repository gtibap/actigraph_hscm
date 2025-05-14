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

    ## total seconds = hh*3600 + mm*60 + ss
    total_sec = frame_time[0]*3600 + frame_time[1]*60 + frame_time[2]
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
def draw_square(image, ini_coord, end_coord):
    # Start coordinate, here (5, 5)
    # represents the top left corner of rectangle

    #########################
    ## test gerardo 1                                                  modify for each patient+++
    start_point = (9,30)
    end_point = (16,36)

    # Blue color in BGR
    color = (255, 0, 255)

    # Line thickness of 2 px
    thickness = 1

    # Using cv2.rectangle() method
    # Draw a rectangle with blue line borders of thickness of 2 px
    image = cv2.rectangle(image, start_point, end_point, color, thickness)

    return image


####################################
def img_plot(df, ini_coord, end_coord):

    frame = df.to_numpy()
    # print(f"frame numpy:\n{frame}")

    s_f = frame*2.0
    s_f[s_f>255.0]=255.0
    img = s_f.astype(np.uint8)

    colormap = plt.get_cmap('plasma')
    img = (colormap(img) * 2**16).astype(np.uint16)[:,:,:3]
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    ## drawing square selected region
    img = draw_square(img, ini_coord, end_coord)
    
    img = resize_img(img)

    # Use Flip code 0 to flip vertically 
    img = cv2.flip(img, 0) 

    cv2.imshow('image',img)
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

#######################
def split_square(frame):

    # start_point = (9,30)
    # end_point = (16,36)

    roi = frame[30:36,9:16]
    print(f"roi:\n{roi}, {roi.shape}")

    c1= np.mean(roi[0:2,0:2]) 
    c2= np.mean(roi[0:2,2:5]) 
    c3= np.mean(roi[0:2,5:7]) 
    c4= np.mean(roi[2:4,0:2]) 
    c5= np.mean(roi[2:4,2:5]) 
    c6= np.mean(roi[2:4,5:7]) 
    c7= np.mean(roi[4:6,0:2]) 
    c8= np.mean(roi[4:6,2:5]) 
    c9= np.mean(roi[4:6,5:7]) 

    print(c1,c2,c3,c4,c5,c6,c7,c8,c9)
    return 0


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

    frames_range =  np.arange(0,5896,1)
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

    # ini_coord = [10,33]
    # end_coord = [16,37]

    ini_coord = np.array([30, 9])
    end_coord = np.array([36, 16]) 
    
    print(f"ini_coord, end_coord: {ini_coord}, {end_coord} ")

    # coord_square = np.array([10, 10,0, 20])

    total_sec = 0

    frame_target = 1196
    flag_found=False

    i=0
    # for idx in frames_range:
    while flag_found==False:
        try:
            idx = frames_range[i]
            ## read line of time
            df_frame = pd.read_csv(filename_mat, nrows= 1, skiprows=0+(idx*size), header=None)
            
            # print(f"frame: {df_frame.iloc[0][0]}, {type(df_frame.iloc[0][0])} {df_frame.iloc[0][0].split()}")
            
            ## get the frame number from the frames' file
            list_frame = df_frame.iloc[0][0].split()
            split_list = list_frame[1].split("(")
            frame_number = int(split_list[0])
            # print(f"frame number: {frame_number}")

            if frame_number >= frame_target:

                flag_found=True
                print(f"frame_number: {frame_number}")

                # print(f"split_list: {split_list}")
                

                ## read line of time
                df_date = pd.read_csv(filename_mat, nrows= 1, skiprows=1+(idx*size), header=None)
                # print(f"time: {df_date.iloc[0][0]}")

                ## read matix of data
                df_data = pd.read_csv(filename_mat, nrows=64, skiprows=2+(idx*size), delim_whitespace=True, header=None)
                # print(f"data:\n{df_data}")

                frame = df_data.to_numpy()

                ## selected frame: extraction region of interest
                print(f"frame:\n{frame}")
                split_square(frame)
                
                ## get the acquisition time ([hh,mm,ss,mm])
                total_sec = get_time(df_date)

                # plot_actigraphy signals
                plot_actigraphy(obj_chest, obj_thigh, ini_time, total_sec)

                ## plot image
                img_plot(df_data, ini_coord, end_coord)

            else:
                pass
        except:
            break

        i=i+1
    
    # print(f"end time: {total_sec}")


    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return 0

    

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))