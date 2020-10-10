# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 15:17:54 2020

@author: mikofskyrm
"""
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as patches
import scipy
from scipy import stats
import statistics 
#sys.path.append("C:\\Users\\mikofskyrm\\Desktop\\")
from glob import glob
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
import json
import time
sns.set(style="darkgrid")
sns.set_palette('muted')
sns.set_context("notebook")
pd.set_option('display.max_columns', 30)

#%% ========================== COLLECT DATA =======================================================
"""
INSTRUCTIONS:
In this portion you must:
    - set your input directory (for the pre-processed photometry files) and output directory
    - choose a mouse group (options are in comments)
    - choose test(s), day(s)
    - choose the downsample time
    - the mouse groups must be added to the code at the end of this file

"""

File_List = (['mouse', 'group', 'test', 'day', 'filename', 'here', 'dataframe length'])


################################################ CHANGE THESE ONCE FOR YOUR COMPUTER ################################################
input_directory = "C:\\Users\\clarityt2\\Documents\\Gordon Lab\\Photometry Preprocessing\\Preprocessing Output\\"
output_directory = "C:\\Users\\clarityt2\\Documents\\Gordon Lab\\Photometry Processing\\TMAZE Test\\Test Output\\"

################################################ CHANGE THESE FOR WHAT YOU WANT TO RUN ################################################
mouse_group = 'test' #'all' #'sst_gcamp', 'pv_gcamp', 'camk_gcamp', 'sst_gcamp_nochr', 'sst_egfp' 

test_list = ['train'] # 'test'
day_list = ['3'] #, '2', '3', '4', '5', '6', '7']
photometry_filetype = 'photon count output' #'photon count output' or 'unmix coeff output'

downsample = 0.1 #in seconds
yvalue = 'pDFoFG'

#yvalue = 'pDFoFG'    #For lines, photon count output file
#yvalue = 'pDCoCG'    #For lines, unmix coeff output file 
#yvalue = 'raw_photoncounts'
#yvalue = 'peak_dFoFG'  #For peaks, photon count output file
#yvalue = 'peak_dCoCG'  #For peaks, unmix coeff output file 
#yvalue = 'peak_SNRG'  #For peaks,

add_to_title = ''


#%% ============================================= LOAD PHOTOMETRY - Lines =====================================================
def Photometry_Downsample(mouse, test, photometry_filetype, day, fpath, file, downsample):
   
   mouse = 'M189'
   test = 'train'
   #fpath = "D:\\Old Tmaze\\All_Coeff_Files\\"
   file = 'M189_train3'
   day = '3'
   #photometry_filetype = 'unmix coeff output'
    
    if photometry_filetype == 'photon count output': 
        input_yvalue = 'LRCpcG'
        output_yvalue = 'downsample_photoncounts'

    elif photometry_filetype == 'unmix coeff output':
        input_yvalue = 'pDCoCG'
        output_yvalue = 'downsample_coeffs'
        
    photofile = glob(f'{fpath}/{mouse}*{test}*{day}_*{photometry_filetype}*.xlsx')
    #print(nev_file)
    if len(photofile) > 1:
        print('error there is more than one photometry file starting with ' + fpath +  '/' + file)
        return 'not here'
    elif len(photofile) < 1:
        print('error, no photometry file exists for ' + fpath + '/' + file)
        return 'not here'
    else: 
        fid2 = str(glob(f'{fpath}/{mouse}*{test}*{day}_*{photometry_filetype}*.xlsx')[0])
        print(fid2) 
        
    photometry_all = pd.read_excel(fid2)
    photometry_all = photometry_all.rename({"Unnamed: 1": 'TimeStamps'},axis=1)         
    photometry_all.insert(0, 'TimeStampsZerod',(photometry_all['TimeStamps'] - photometry_all['TimeStamps'].iloc[0]) / 1000)    

    photometry_temp = pd.DataFrame()
    
    RoundTime = round(photometry_all['TimeStampsZerod'], 5) #change the number of decimal points for rounding
    
#    mouselist = [mouse] * len(photometry_all['TimeStampsZerod']) 
    photometry_temp.insert(0, 'Mouse', mouse)
    photometry_temp.insert(1, 'Test', test)
    photometry_temp.insert(2, 'TimeStamp', RoundTime )
    photometry_temp.insert(3, input_yvalue, photometry_all[input_yvalue])
    photometry_temp.insert(4, 'Day', day)
#    photometry_temp.insert(4, 'pDFoFRatio', photometry_all['pDFoFRatio'] )
#    photometry_temp.insert(5, 'zScorepDFoFRatio', photometry_all['zScorepDFoFRatio'] )
#    photometry_temp.insert(6, 'pDFoFG', photometry_all['pDFoFG'] )
#    photometry_temp.insert(7, 'zScorepDFoFG', photometry_all['zScorepDFoFG'] )
#    photometry_temp.insert(8, 'pcRowSumG', photometry_all['pcRowSumG'])
    
    
    
    photo_times = photometry_temp['TimeStamp']
    photo_data = photometry_temp[input_yvalue]
    
    new_data = pd.DataFrame()
    downsample_data = []
    downsample_trialtime = []
    downsample_tottime = []
    downsample_index = []
#    trial_start_count = []
    
    if downsample == 0.1:
        downsample_ms = 100
    elif downsample == 0.05:
        downsample_ms = 50
        
    i=0
        
    time_start = 0
    index_end = len(photo_times) - 2
    time_end = photo_times[index_end]*1000
    for start_i_ms in range(time_start,int(time_end),downsample_ms):
        start_i = start_i_ms/1000
        end_i = start_i + downsample
        
        timezone = np.where(
        (photo_times >= (start_i)) &
        (photo_times < (end_i)))[0]
        
        if timezone.size == 0:
            #print('empty')
            zero = 0
            
        elif timezone.size > 0:
            tempdata = list(photometry_temp[input_yvalue].loc[timezone])
            type(photometry_temp[input_yvalue])
            
            average_tempdata = statistics.mean(tempdata)
            
            downsample_data.append(average_tempdata)
            downsample_trialtime.append(start_i)
            downsample_index.append(i)
            downsample_tottime.append(start_i)
#                trial_start_count.append(this_start)
        i+=1
    #print(downsample_tottime)
    total_time = downsample_tottime
            
    new_data.insert(0, 'trial_index', downsample_index)
    #new_data.insert(1, 'trial_time', downsample_trialtime)
    new_data.insert(1, 'total_time', total_time)
    new_data.insert(2, output_yvalue, downsample_data)
    new_data.insert(3, 'test', test)
    new_data.insert(4, 'day', day)
    new_data.insert(5, 'mouse', mouse)
#    new_data.insert(8, 'trial_start', trial_start_count)
            
            
#   new_data.to_csv ("C:\\Users\\mikofskyrm\\Desktop\\Photometry\\photodata_test.csv", index = None, header=True)
            
#    print(photometry_temp)
    return new_data


#%% ========================== DO NOT CHANGE THIS PART =======================================================
"""
This is where you can add to the mouse groups but be careful about changing anything else!
"""
if mouse_group == 'all':
    mouse_list = ['m259', 'm260', 'm261', 'm176', 'm178', 'm194', 'm195', 'm189', 'm208', 'm209']
elif mouse_group == 'test':
    mouse_list = ['M189']
else:
    print ('Mouse group is not valid. The code will now quit, please try again')
    sys.exit()

filename = mouse_group + add_to_title

fpath = input_directory
timestamps_yes_or_no = 'no' #'yes' or 'no' this will change the way comments are processed, default to no


title = filename
                              
photodata_all = pd.DataFrame()
this_photodata = pd.DataFrame()

for m in range(len(mouse_list)):
    mouse = mouse_list[m]
    
    for test in test_list:
        
        for day in day_list:
            
            file = str(mouse) + '_' + str(test) + str(day)
            
            print(file)
            
            this_photodata = Photometry_Downsample(mouse = mouse, test = test, photometry_filetype = photometry_filetype, day = day, fpath = fpath, file = file, downsample =  downsample)
            if  type(this_photodata) == str:
                File_file = ([mouse, mouse_group, test, day, file, 'not here', 'NA'])
                File_List = np.vstack((File_List, File_file))
                np.savetxt(output_directory + "TMazePhotoFiles_" + mouse_group + add_to_title + ".csv", File_List, delimiter=",",fmt='%s')

            else:
                length = len(this_photodata)
                File_file = ([mouse, mouse_group, test, day, file, 'here', length])
                File_List = np.vstack((File_List, File_file))
                this_photodata.to_csv (output_directory + "photodata_" + mouse + "_" + test  + day + add_to_title + ".csv", index = None, header=True)
                np.savetxt(output_directory + "TMazePhotoFiles_" + mouse_group + add_to_title +  ".csv", File_List, delimiter=",",fmt='%s')
