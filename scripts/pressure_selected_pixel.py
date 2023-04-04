import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from skimage.feature import peak_local_max
import datetime
import sys

from functions_tools import average_frames_1s


##################
# global variables
id_frame=0
pressed_key='qq'
figure_2, ax_2 = plt.subplots(figsize=(4.5, 9))
figure_roi, ax_roi = plt.subplots(figsize=(5, 5))
figure_plot, ax_plot = plt.subplots()

# figure_quantiles, ax_quantiles = plt.subplots()
# figure_hist, ax_hist = plt.subplots()
x_ini=0
y_ini=0
x_end=0
y_end=0

xi=0
yi=0
xe=0
ye=0
h=3
w=3
step=0

draw_rect=False
flag_rect=True
# global variables
##################

##################
# auxiliary functions

def select_frames_1s(df_head, raw_data):
    # averaging of frames per second; 2 or 3 FPS (2Hz or 3Hz) will become 1 FPS 1Hz

    data_mean=np.array([],dtype=float).reshape(0, raw_data.shape[1], raw_data.shape[2])
    data_time=[]

    id_sel=0
    # print(len(raw_data))
    while id_sel < len(raw_data):
        sel_hour=df_head['hour'].values[id_sel]
        # print("df['hour'].values[0]: ", sel_hour)
        
        hour_splitted = datetime.datetime.strptime(sel_hour, "%H:%M:%S.%f")
        h=hour_splitted.hour
        m=hour_splitted.minute
        s=hour_splitted.second

        h_inf =str(h).zfill(2)
        m_inf =str(m).zfill(2)
        s_inf =str(s).zfill(2)
        
        if s+1==60:
            s_sup=str(0).zfill(2)
            if m+1==60:
                m_sup=str(0).zfill(2)
                h_sup=str(h+1).zfill(2)
            else:
                m_sup=str(m+1).zfill(2)
                h_sup=str(h).zfill(2)
        else:
            s_sup=str(s+1).zfill(2)
            m_sup=str(m).zfill(2)
            h_sup=str(h).zfill(2)
        
        # u_sec = str(hour_splitted.microsecond)
        # print(hour+':'+min+':'+sec_inf+'.'+u_sec)

        lim_inf = h_inf+':'+m_inf+':'+s_inf
        lim_sup = h_sup+':'+m_sup+':'+s_sup

        # print('lim_inf, lim_sup: ', lim_inf, lim_sup)

        idx_s = df_head.loc[(df_head['hour']>= lim_inf) & (df_head['hour']<lim_sup)].index.values
        # print(idx_s)

        # id_last = idx_s[-1]
        id_last = np.amax(idx_s)
        id_sel = id_last+1

        # indexes to average matrices of the mattress pressure
        # mean_sec = np.mean(raw_data[idx_s[0]:id_sel], axis=0)
        selected_frame = raw_data[id_last]
        
        data_mean = np.vstack([data_mean, np.expand_dims(selected_frame,axis=0)])

        data_time.append(lim_sup)

        # print(idx_s, raw_data[idx_s[0]:id_sel].shape, mean_sec.shape, data_mean.shape, len(data_time), data_time[-1])

    df_ts = pd.DataFrame(data_time,columns=['time_stamp'])

    return df_ts, data_mean


# def visual_img(frame):
#     global draw_rect, w,h

#     ax_2.cla()    
#     ax_2.imshow(frame)

#     # Create a Rectangle patch
#     if draw_rect==True:
#         # w = x_end-x_ini
#         # h = y_end-y_ini
#         # print(w, h)
#         rect = patches.Rectangle((xi, yi), width=2*w, height=2*h, linewidth=1, edgecolor='w', facecolor='none')
#         # Add the patch to the Axes
#         ax_2.add_patch(rect)
#     else:
#         pass

#     figure_2.canvas.draw()
#     figure_2.canvas.flush_events()

#     return


def visual_img_2(frame, roi, roi_stats):
    # gll draw_rect
    ax_2.cla()  
    ax_2.set_ylabel('pixel (right)')  
    ax_2.set_xlabel('pixel (bottom)')  
    ax_2.imshow(frame)

    ax_roi.cla()  
    ax_roi.set_ylabel('pixel (right)')  
    ax_roi.set_xlabel('pixel (bottom)')
    
    roi_q3=np.copy(roi)
    roi_q3[roi_q3<roi_stats[3]]=0
    ax_roi.imshow(roi_q3)


    # Create a Rectangle patch
    # if draw_rect==True:
    # w = 2
    # h = 2
    # print(w, h)
    # rect = patches.Rectangle((xi, yi), width=2*w, height=2*h, linewidth=1, edgecolor='w', facecolor='none')
    rect = patches.Rectangle((xi, yi), width=(xe-xi), height=(ye-yi), linewidth=1, edgecolor='w', facecolor='none')
    # Add the patch to the Axes
    ax_2.add_patch(rect)
    # else:
    #     pass

    figure_2.canvas.draw()
    figure_2.canvas.flush_events()

    return


def visual_img_3(frame, roi, roi_stats):
    # gll draw_rect
    ax_2.cla()  
    ax_2.set_ylabel('pixel (right)')  
    ax_2.set_xlabel('pixel (bottom)')  
    ax_2.imshow(frame)

    ax_roi.cla()  
    ax_roi.set_ylabel('pixel (right)')  
    ax_roi.set_xlabel('pixel (bottom)')
    
    roi_q3=np.copy(roi)
    roi_q3[roi_q3<roi_stats[3]]=0
    ax_roi.imshow(roi_q3)


    # Create a Rectangle patch
    # if draw_rect==True:
    # w = 2
    # h = 2
    # print(w, h)
    # rect = patches.Rectangle((xi, yi), width=2*w, height=2*h, linewidth=1, edgecolor='w', facecolor='none')
    rect = patches.Rectangle((xi, yi), width=w, height=h, linewidth=1, edgecolor='w', facecolor='none')
    # Add the patch to the Axes
    ax_2.add_patch(rect)
    # else:
    #     pass

    figure_2.canvas.draw()
    figure_2.canvas.flush_events()

    return


# def visual_roi(img):

#     ax_roi.cla()    
#     ax_roi.imshow(img)

#     figure_roi.canvas.draw()
#     figure_roi.canvas.flush_events()

#     return


# def visual_roi_peaks(img, coord_peaks):

#     ax_roi.cla()    
#     ax_roi.imshow(img)

#     peaks_list=[]

#     for peak in coord_peaks:
#         # print('peak: ', peak, len(peak), peak[0])
#         rect = patches.Rectangle((peak[1]-1, peak[0]-1), width=2, height=2, linewidth=1, edgecolor='w', facecolor='none')
#         ax_roi.add_patch(rect)
#         peaks_list.append(roi[peak[0],peak[1]])
    
#     print('peaks_list: ', peaks_list)
#     figure_roi.canvas.draw()
#     figure_roi.canvas.flush_events()

#     return

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
    global pressed_key,w,h,step

    # print('pressed', event.key)
    pressed_key = event.key
    sys.stdout.flush()

    if pressed_key == 'x':
        print ("pressed x")
        exit_key=True
    elif pressed_key == 'm':
        step=1
    elif pressed_key == 'n':
        step=0
    elif pressed_key == 'p':
        h+=3
    elif pressed_key == 'o':
        w+=3
    elif pressed_key == 'P':
        if h>3:
            h-=3
        else:
            pass
    elif pressed_key == 'O':
        if w>3:
            w-=3
        else:
            pass
        # id_x0=int(min(x_ini,x_end))
        # id_x1=int(max(x_ini,x_end))
        # id_y0=int(min(y_ini,y_end))
        # id_y1=int(max(y_ini,y_end))
        # roi = frame[id_y0:id_y1,id_x0:id_x1]
        
        # # visual_roi(roi)
        # print(id_x0, id_x1, id_y0, id_y1)

        # figure_2.canvas.mpl_disconnect(cidpress)
        # figure_2.canvas.mpl_disconnect(cidrelease)
        # figure_2.canvas.mpl_disconnect(cidmotion)
    else:
        pass

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

# def on_release(event):
#     global x_end, y_end,flag_rect

#     if event.inaxes:
#         # print(f'data coords {event.xdata} {event.ydata},',
#             #   f'pixel coords {event.x} {event.y}')
#         x_end=event.xdata
#         y_end=event.ydata
#         flag_rect=False
#     else:
#         pass
#     return

# def on_motion(event):
#     global x_end, y_end,flag_rect

#     if event.inaxes:
#         # print(f'data coords {event.xdata} {event.ydata},',
#             #   f'pixel coords {event.x} {event.y}')
#         if flag_rect:
#             x_end=event.xdata
#             y_end=event.ydata
#         else:
#             pass
#     else:
#         pass
#     return


# def plot_quantiles(df_quantiles):

#     ax_quantiles.cla()    
#     q0_arr = df_quantiles['q0'].to_numpy()
    
#     ax_quantiles.plot(q0_arr)

#     figure_quantiles.canvas.draw()
#     figure_quantiles.canvas.flush_events()
    
#     return


# def plot_histogram(roi):
    
    
#     histogram, bin_edges = np.histogram(roi[roi>0])

#     ax_hist.cla()    
#     ax_hist.stairs(histogram, edges=bin_edges)
#     ax_hist.set_xlim(left=0,right=75)

#     figure_hist.canvas.draw()
#     figure_hist.canvas.flush_events()

#     return


def sacrum_stat(roi):
    # global xi,xe,yi,ye

    # yi= int(y_ini - h)
    # ye= int(y_ini + h)
    # xi= int(x_ini - w)
    # xe= int(x_ini + w)

    # roi_max = np.nanmax(frame[yi-1:yi+1, xi-1:xi+1])
    # roi_min = np.nanmin(frame[yi-1:yi+1, xi-1:xi+1])
    # roi_mean = np.nanmean(frame[yi-1:yi+1, xi-1:xi+1])
    # roi = frame[yi:ye, xi:xe]
    # print('roi.shape: ', roi.shape)
    
    # roi_max = np.nanmax(roi)
    # roi_min = np.nanmin(roi)
    # roi_mean = np.nanmean(roi)
    # roi_median = np.nanmedian(roi)

    q0 = np.nanquantile(roi,0.0)
    q1 = np.nanquantile(roi,0.25)
    q2 = np.nanquantile(roi,0.5)
    q3 = np.nanquantile(roi,0.75)
    q4 = np.nanquantile(roi,1.0)


    # print(f'bigger than {q3}: {np.argwhere(roi >= q3)} max: { np.unravel_index(np.nanargmax(roi), roi.shape)}, max2 {np.argwhere(roi >= q4)}')

    # return np.array([roi_min, roi_max, roi_mean, roi_median])
    return np.array([q0,q1,q2,q3,q4])


# def update_parameters():
#     global yi,ye,xi,xe

#     yi= int(y_ini - h)
#     ye= int(y_ini + h)
#     xi= int(x_ini - w)
#     xe= int(x_ini + w)

#     return
def update_parameters():
    global yi,ye,xi,xe

    xi= int(x_ini)
    yi= int(y_ini)

    ye= int(y_ini + h)
    xe= int(x_ini + w)

    return


def plot_pressure(stat_all, df_ann):

    ax_plot.cla()
    ax_plot.set_ylim(0,50)
    ax_plot.set_xlim(0,len(frames_sec))
    ax_plot.set_ylabel('pressure (mmHg)')
    ax_plot.set_xlabel('frame')

    ini_arr=df_ann['id_frame_ini'].to_numpy()
    end_arr=df_ann['id_frame_end'].to_numpy()
    type_arr=df_ann['type_motion'].to_numpy()
    # only one line may be specified; full height
    for ini, end, label in zip(ini_arr,end_arr,type_arr):
        # ax_plot[0].axvline(x = ini, color = 'r', label = 'axvline - full height')
        # ax_plot[0].axvline(x = end, color = 'g', label = 'axvline - full height')
        ax_plot.axvspan(ini, end, facecolor='wheat', alpha=0.5)
        # ax_plot[0].axvline(x = ini, color = 'r')
        # ax_plot[0].axvline(x = end, color = 'g')
        ax_plot.annotate(label, xy=(ini, 1), xytext=(ini, 1))
        
    
    # ax_plot[0].axhline(y = 25, color = 'g', label = 'axvline - full height', linestyle='--')
    # ax_plot.axhlqine(y = 25, color = 'orange', linestyle=':', alpha=0.5)

    # ax_plot.plot(p_list)
    # ax_plot.plot(stat_all[:,0])
    # ax_plot.plot(stat_all[:,1])
    # ax_plot.plot(stat_all[:,2])
    # ax_plot.plot(stat_all[:,3])
    ax_plot.plot(stat_all[:,4]) # max. value in the roi

    return
        

def plot_pressure_2(stat_left, stat_center, stat_right, df_ann):

    ax_plot.cla()
    ax_plot.set_ylim(0,50)
    ax_plot.set_xlim(0,len(frames_sec))
    ax_plot.set_ylabel('pressure (mmHg)')
    ax_plot.set_xlabel('frame')

    ini_arr=df_ann['id_frame_ini'].to_numpy()
    end_arr=df_ann['id_frame_end'].to_numpy()
    type_arr=df_ann['type_motion'].to_numpy()
    # only one line may be specified; full height
    for ini, end, label in zip(ini_arr,end_arr,type_arr):
        # ax_plot[0].axvline(x = ini, color = 'r', label = 'axvline - full height')
        # ax_plot[0].axvline(x = end, color = 'g', label = 'axvline - full height')
        ax_plot.axvspan(ini, end, facecolor='wheat', alpha=0.5)
        # ax_plot[0].axvline(x = ini, color = 'r')
        # ax_plot[0].axvline(x = end, color = 'g')
        ax_plot.annotate(label, xy=(ini, 1), xytext=(ini, 1))
        
    
    # ax_plot[0].axhline(y = 25, color = 'g', label = 'axvline - full height', linestyle='--')
    # ax_plot.axhline(y = 25, color = 'orange', linestyle=':', alpha=0.5)

    # ax_plot.plot(p_list)
    # ax_plot.plot(stat_all[:,0])
    # ax_plot.plot(stat_all[:,1])
    # ax_plot.plot(stat_all[:,2])
    # ax_plot.plot(stat_all[:,3])
    # ax_plot.plot(stat_all[:,4]) # max. value in the roi
    ax_plot.plot(stat_left[:,4], label='left', alpha=1.0) # max. value in the roi
    ax_plot.plot(stat_center[:,4], label='center', alpha=1.0) # max. value in the roi
    ax_plot.plot(stat_right[:,4], label='right', alpha=1.0) # max. value in the roi
    ax_plot.legend()

    return

####### main function ###########
if __name__== '__main__':
    
    # print('Interface Pressure Visualization')
    # read data Interface pressure
    path_mattress = '../data/mattress_actigraph/mattress/new_format/'
    path_annotations = '../data/mattress_actigraph/info/'
    
    day_n='day02' # ['day00', 'day01'] day number
    pp = 'p00' # ['p00','p01','p02','p03','p04'] subject number
    nt='2' # ['1','2'] test number
    ann='annotations.csv'

    he = 'head_'
    ra = 'raw_'

    file_head= day_n+'_'+pp+'_'+nt+'.csv'
    file_raw= day_n+'_'+pp+'_' +nt+'.npz'
    file_ann= path_annotations+day_n+'_'+ann

    #########
    # loading annotations
    df_ann_all = pd.read_csv(file_ann)
    df_ann = df_ann_all.loc[df_ann_all['patient']==pp]

    print(df_ann.info())
    print(df_ann.head())

    # loading data mattress pressure
    df_ma = pd.read_csv(path_mattress+he+file_head)
    
    with open(path_mattress+ra+file_raw, 'rb') as f:
        loaded=np.load(f)
        data_all = loaded['xyt']

    # print(df_ma.info())
    # print(data_all.shape)

    # df_f, frames_sec = average_frames_1s(df_ma, data_all)
    df_f, frames_sec = select_frames_1s(df_ma, data_all)
    
    # print(df_f)
    # print(frames_sec.shape)


    cidpress  = figure_2.canvas.mpl_connect('button_press_event', on_press)
    # cidrelease= figure_2.canvas.mpl_connect('button_release_event', on_release)
    # cidmotion = figure_2.canvas.mpl_connect('motion_notify_event', on_motion)
    cidkeys   = figure_2.canvas.mpl_connect('key_press_event', on_keyboard)
    # pressure mattress visualization
    plt.ion()
    plt.show()
    # print('cid1: ', cid1)
    # print('cid2: ', cid2)
    
    flag =True
    exit_key=False
    flag_start=True
    
    id_frame_ini = 0
    id_frame_end = len(frames_sec)

    p_list = []
    stat_all = np.array([])
    stat_all=np.array([],dtype=float).reshape(0,5)
    stat_all_left=np.array([],dtype=float).reshape(0,5)
    stat_all_center=np.array([],dtype=float).reshape(0,5)
    stat_all_right=np.array([],dtype=float).reshape(0,5)

    # frames_sec=data_all    

    while (exit_key==False) and (id_frame < len(frames_sec)) and flag:
        print('id_frame: ',id_frame)

        update_parameters()

        frame=frames_sec[id_frame]
        roi = frame[yi:ye, xi:xe]
        # print('roi.shape: ', roi.shape)

        # dividing roi in three sections
        delta =int(w/3)
        delta2=int(2*delta)

        roi_right =roi[:,0:delta]
        roi_center=roi[:,delta:delta2]
        roi_left  = roi[:,delta2:w]

        roi_stat = sacrum_stat(roi)
        roi_stat_left = sacrum_stat(roi_left)
        roi_stat_center = sacrum_stat(roi_center)
        roi_stat_right = sacrum_stat(roi_right)

        visual_img_3(frame, roi, roi_stat)

        # print('row, col:', int(y_ini), int(x_ini))

        if step>0:
            # roi_stat = sacrum_stat(frame)
            # print(roi_stat)
            # stat_all = np.vstack([stat_all, np.expand_dims(roi_stat,axis=0)])
            stat_all_left = np.vstack([stat_all_left, np.expand_dims(roi_stat_left,axis=0)])
            stat_all_center = np.vstack([stat_all_center, np.expand_dims(roi_stat_center,axis=0)])
            stat_all_right = np.vstack([stat_all_right, np.expand_dims(roi_stat_right,axis=0)])

        # p_list.append(frame[int(y_ini), int(x_ini)])
        # p_list.append(roi_stat)

        # plot_pressure(stat_all,df_ann)
        plot_pressure_2(stat_all_left,stat_all_center,stat_all_right,df_ann)

        plt.pause(0.01)
        
        id_frame+=step
        # if id_frame >= len(frames_sec):
        #     id_frame=0
        # else:
        #     pass

    # list_q0=[]
    # list_q1=[]
    # list_q2=[]
    # list_q3=[]
    # list_q4=[]
    # list_ratio_nan=[]

    # # statistical values region of interest (ROI)
    # for id_frame, frame in enumerate(frames_sec):
    #     roi = frame[id_y0:id_y1,id_x0:id_x1]
        
    #     coord_peaks = peak_local_max(roi, num_peaks=3, min_distance=1) # threshold_rel=0.25
    #     # print('coord_peaks: ',coord_peaks)
    #     visual_roi_peaks(roi, coord_peaks)
    #     plt.pause(1)
        
    #     if pressed_key == 'z':
    #         print ("pressed z")
    #         break
        


    #     # print(np.argmax(roi))

    #     # # print(roi)
    #     # q0= np.round(np.percentile(roi,  0),2)
    #     # q1= np.round(np.percentile(roi,  25),2)
    #     # q2= np.round(np.percentile(roi,  50),2)
    #     # q3= np.round(np.percentile(roi,  75),2)
    #     # q4= np.round(np.percentile(roi, 100),2)

    #     # print(id_frame)
    #     # print(q0,q1,q2,q3,q4)

    #     # roi[roi<=0.0]=np.nan
    #     # plot_histogram(roi)
    #     # plt.pause(1.0)
    #     # # print(roi)
        
    #     # q0 = np.round(np.nanquantile(roi,0.0),2)
    #     # q1 = np.round(np.nanquantile(roi,0.25),2)
    #     # q2 = np.round(np.nanquantile(roi,0.5),2)
    #     # q3 = np.round(np.nanquantile(roi,0.75),2)
    #     # q4 = np.round(np.nanquantile(roi,1.0),2)

    #     # ratio_nan = np.round(np.count_nonzero(np.isnan(roi)) / roi.size, 2)

    #     # list_q0.append(q0)
    #     # list_q1.append(q1)
    #     # list_q2.append(q2)
    #     # list_q3.append(q3)
    #     # list_q4.append(q4)
    #     # list_ratio_nan.append(ratio_nan)
    #     # # print(q0,q1,q2,q3,q4, ratio_nan)
    
    #     # df_quantiles=pd.DataFrame()
    #     # df_quantiles['q0']=list_q0
    #     # df_quantiles['q1']=list_q0
    #     # df_quantiles['q2']=list_q0
    #     # df_quantiles['q3']=list_q0
    #     # df_quantiles['q4']=list_q0
    #     # df_quantiles['ratio_nan']=list_ratio_nan

    #     # plot_quantiles(df_quantiles)
        
    plt.show(block=True)
        # print(roi.shape)
    # print(frames_sec.shape, frames_sec[0].shape)
        
    
