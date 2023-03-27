import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import datetime
import sys

from functions_tools import average_frames_1s


##################
# global variables
id_frame=0
pressed_key='qq'
figure_2, ax_2 = plt.subplots(figsize=(6, 8))
figure_roi, ax_roi = plt.subplots(figsize=(4, 6))
x_ini=0
y_ini=0
x_end=0
y_end=0
draw_rect=False
flag_rect=True
# global variables
##################

##################
# auxiliary functions

def visual_img(frame):
    global draw_rect

    ax_2.cla()    
    ax_2.imshow(frame)

    # Create a Rectangle patch
    if draw_rect==True:
        w = x_end-x_ini
        h = y_end-y_ini
        # print(w, h)
        rect = patches.Rectangle((x_ini, y_ini), width=w, height=h, linewidth=1, edgecolor='w', facecolor='none')
        # Add the patch to the Axes
        ax_2.add_patch(rect)
    else:
        pass

    figure_2.canvas.draw()
    figure_2.canvas.flush_events()

    return


def visual_roi(img):

    ax_roi.cla()    
    ax_roi.imshow(img)

    figure_roi.canvas.draw()
    figure_roi.canvas.flush_events()

    return

# def onclick(event):
#     global id_frame
#     # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f, name=%s' %
#         #   ('double' if event.dblclick else 'single', event.button,
#         #    event.x, event.y, event.xdata, event.ydata, event.name))
    
#     if event.inaxes:
#         print(f'data coords {event.xdata} {event.ydata},',
#               f'pixel coords {event.x} {event.y}')
#     else:
#         pass
    
#     # if event.xdata >= id_frame_ini and event.xdata < id_frame_end:
#     #     id_frame=int(event.xdata)
#     # else:
#     #     pass
#     # print('mouse: ', event.xdata, id_frame_ini, id_frame_end, id_frame)
#     return

def on_keyboard(event):
    global pressed_key

    # print('pressed', event.key)
    pressed_key = event.key
    sys.stdout.flush()
    return

def on_press(event):
    global x_ini,y_ini,x_end,y_end,draw_rect,flag_rect

    if event.inaxes:
        # print(f'data coords {event.xdata} {event.ydata},',
            #   f'pixel coords {event.x} {event.y}')
        x_ini=event.xdata
        y_ini=event.ydata
        draw_rect=True
        flag_rect=True
    else:
        pass
    return

def on_release(event):
    global x_end, y_end,flag_rect

    if event.inaxes:
        # print(f'data coords {event.xdata} {event.ydata},',
            #   f'pixel coords {event.x} {event.y}')
        x_end=event.xdata
        y_end=event.ydata
        flag_rect=False
    else:
        pass
    return

def on_motion(event):
    global x_end, y_end,flag_rect

    if event.inaxes:
        # print(f'data coords {event.xdata} {event.ydata},',
            #   f'pixel coords {event.x} {event.y}')
        if flag_rect:
            x_end=event.xdata
            y_end=event.ydata
        else:
            pass
    else:
        pass
    return

####### main function ###########
if __name__== '__main__':
    
    # print('Interface Pressure Visualization')
    # read data Interface pressure
    path_mattress = '../data/mattress_actigraph/mattress/new_format/'
    
    day_n='day_1' # ['day_0', 'day_1'] day number
    pp = 'p03' # ['p00','p01','p02','p03','p04'] subject number
    nt='1' # ['1','2'] test number

    he = 'head_'
    ra = 'raw_'

    file_head= day_n+'_'+pp+'_'+nt+'.csv'
    file_raw= day_n+'_'+pp+'_' +nt+'.npz'

    #########
    # loading data mattress pressure
    df_ma = pd.read_csv(path_mattress+he+file_head)
    
    with open(path_mattress+ra+file_raw, 'rb') as f:
        loaded=np.load(f)
        data_all = loaded['xyt']

    # print(df_ma.info())
    # print(data_all.shape)

    df_f, frames_sec = average_frames_1s(df_ma, data_all)

    # print(df_f)
    # print(frames_sec.shape)


    cidpress  = figure_2.canvas.mpl_connect('button_press_event', on_press)
    cidrelease= figure_2.canvas.mpl_connect('button_release_event', on_release)
    cidmotion = figure_2.canvas.mpl_connect('motion_notify_event', on_motion)
    cidkeys   = figure_2.canvas.mpl_connect('key_press_event', on_keyboard)
    # pressure mattress visualization
    plt.ion()
    plt.show()
    # print('cid1: ', cid1)
    # print('cid2: ', cid2)
    
    flag =True
    exit_key=False
    flag_start=True
    step=0
    id_frame_ini = 0
    id_frame_end = len(frames_sec)


    while (exit_key==False) and flag:
        # print('id_frame: ',id_frame)
        frame=frames_sec[id_frame]

        visual_img(frame)
        plt.pause(0.1)
        
        if pressed_key == 'x':
            print ("pressed x")
            exit_key=True
        elif pressed_key == 'm':
            step=1
        elif pressed_key == 'n':
            step=0
        elif pressed_key == 'p':
            id_x0=int(min(x_ini,x_end))
            id_x1=int(max(x_ini,x_end))
            id_y0=int(min(y_ini,y_end))
            id_y1=int(max(y_ini,y_end))
            roi = frame[id_y0:id_y1,id_x0:id_x1]
            
            visual_roi(roi)
            print(id_x0, id_x1, id_y0, id_y1)

            figure_2.canvas.mpl_disconnect(cidpress)
            figure_2.canvas.mpl_disconnect(cidrelease)
            figure_2.canvas.mpl_disconnect(cidmotion)
        else:
            pass
        
        id_frame+=step
        if id_frame >= len(frames_sec):
            id_frame=0
        else:
            pass

    # statistical values region of interest (ROI)
    for id_frame, frame in enumerate(frames_sec):
        roi = frame[id_y0:id_y1,id_x0:id_x1]
        visual_roi(roi)
        # print(roi)
        q0= np.round(np.percentile(roi,  0),2)
        q1= np.round(np.percentile(roi,  25),2)
        q2= np.round(np.percentile(roi,  50),2)
        q3= np.round(np.percentile(roi,  75),2)
        q4= np.round(np.percentile(roi, 100),2)

        print(id_frame)
        print(q0,q1,q2,q3,q4)

        roi[roi==0]=np.nan
        # print(roi)
        
        q0 = np.round(np.nanquantile(roi,0.0),2)
        q1 = np.round(np.nanquantile(roi,0.25),2)
        q2 = np.round(np.nanquantile(roi,0.5),2)
        q3 = np.round(np.nanquantile(roi,0.75),2)
        q4 = np.round(np.nanquantile(roi,1.0),2)

        print(q0,q1,q2,q3,q4)


        # print(roi.shape)
    # print(frames_sec.shape, frames_sec[0].shape)
        
    
