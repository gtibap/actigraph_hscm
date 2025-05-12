import numpy as np
import pandas as pd

class Class_Actigraphy:

    #####################################
    def __init__(self, name):
        
        # print('Activity Measurements object constructor initialization')
        
        self.name = name
        self.header_location=10

        self.delta_samples = 1

        self.vec_mag  ='Vector Magnitude'
        self.incl_off ='Inclinometer Off'
        self.incl_sta ='Inclinometer Standing'
        self.incl_sit ='Inclinometer Sitting'
        self.incl_lyi ='Inclinometer Lying'

        self.label_time = ' Time'
        self.label_date = 'Date'
        self.time_sec = 'time_sec'

    #####################################
    def openFile(self, path, filename):
        
        self.path = path
        self.filename = filename
        self.df1 = pd.read_csv(path+filename, header=self.header_location, decimal=',')
        # print(f"self df1: {self.name}\n{self.df1}")

        ## this is necesary for cases where datetime format is different or has repetitive values 
        with open(path+filename) as f:

            print(f"path+filename: {path+filename}")
            for i, line in enumerate(f):             
                if i < 10:
                    list_values = line.split()
                    if i == 2:
                        ## hh:mm:ss
                        start_time = list_values[2][:8]
                    elif i == 3:
                        ## date dd/mm/yyyy
                        start_date = list_values[2][:10]
                        if '/' in start_date:
                            day, month, year = start_date.split('/')
                        elif '-' in start_date:
                            year, month, day  = start_date.split('-')
                        else:
                            print('Date format is not recognized!')
                            return 0
                        start_date = year+'-'+month+'-'+day
                    elif i == 4:
                        ## epoch period hh:mm:ss
                        epoch_period = list_values[3][:8]
                        ## epoch period in seconds
                        list_period = epoch_period.split(':')
                        delta_sec = int(list_period[0])*3600 + int(list_period[1])*60 + int(list_period[2])
                    elif i == 5:
                        ## hh:mm:ss
                        download_time = list_values[2][:8]
                    elif i == 6:
                        ## date dd/mm/yyyy
                        download_date = list_values[2][:10]
                        if '/' in download_date:
                            day, month, year = download_date.split('/')
                        elif '-' in download_date:
                            year, month, day  = download_date.split('-')
                        else:
                            print('Date format is not recognized!')
                            return 0
                        
                        download_date = year+'-'+month+'-'+day
                    else:
                        pass
                else:
                    break
            
        start_recording = start_date +' '+ start_time
        end_recording = download_date +' '+ '23:59:59'
        
        date_range_index = pd.date_range(start =start_recording, end =end_recording, freq = str(delta_sec)+'s')
        
        df_temp = date_range_index.to_frame(index=False, name='dateTime')
        df_temp = df_temp.iloc[:len(self.df1)]

        df_temp['date'] = df_temp['dateTime'].dt.date
        df_temp['time'] = df_temp['dateTime'].dt.time
        
        self.df1[self.label_date]= df_temp['date'].astype(str)
        self.df1[self.label_time]= df_temp['time'].astype(str)
        
        # ## column time in seconds
        # nsamples=len(self.df1)
        # start=0
        # end=start+(delta_sec*nsamples)
        # time_sec = np.arange(start,end,delta_sec)
        
        # self.df1[self.time_sec] = time_sec
        self.delta_samples = delta_sec

        a = pd.to_timedelta(self.df1[self.label_time])
        self.df1[self.time_sec] = a.dt.total_seconds()

        print(f"self df1: {self.name}\n{self.df1}")
        
        return 0
    

