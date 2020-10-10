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
    - set your input directory (for the raw openephys files) and output directory (for processed files)
    - choose a mouse group (options are in comments)
    - choose test(s), day(s)
    - choose the downsample time
    - the mouse groups must be added to the code at the end of this file

"""

File_List = (['mouse', 'group', 'protocol', 'week', 'day', 'filename', 'here', 'dataframe length'])


################################################ CHANGE THESE ONCE FOR YOUR COMPUTER ################################################
input_directory = "C:\\Users\\clarityt2\\Documents\\Gordon Lab\\Photometry Processing\\vHPC_PFC_plasticity\\Photon Count Excel Input\\"
output_directory = "C:\\Users\\clarityt2\\Documents\\Gordon Lab\\Photometry Processing\\vHPC_PFC_plasticity\\Photodata Output\\"
#input_directory = "C:\\Users\\mikofskyrm\\Desktop\\Sample_DATA\\" #"D:\\Old Tmaze\\TMaze\\Photometry Blackrock\\"
#output_directory = "C:\\Users\\mikofskyrm\\Desktop\\Example_Files\\" #"C:\\Users\\mikofskyrm\\Desktop\\DATA_OUT\\Processed_Files_TMaze\\"

################################################ CHANGE THESE FOR WHAT YOU WANT TO RUN ################################################
mouse_group = 'sst_gcamp' #'test' #'all' #'sst_gcamp', 'pv_gcamp', 'camk_gcamp', 'sst_gcamp_nochr', 'sst_egfp'

protocol = 'Plasticity' #'Plasticity' or 'IO'
week_list = ['w0', 'w1', 'w2', 'w3', 'w4'] #'w0', 'w1', 'w2', 'w3', 'w4'
day_list = ['d1','d2']
photometry_filetype = 'photon count output' #'photon count output' or 'unmix coeff output'

downsample = 0.1 #in seconds
#yvalue = 'pDFoFG'    #For lines, photon count output file
#yvalue = 'pDCoCG'    #For lines, unmix coeff output file 
#yvalue = 'raw_photoncounts'
yvalue = 'peak_dFoFG'  #For peaks, photon count output file
#yvalue = 'peak_dCoCG'  #For peaks, unmix coeff output file 
#yvalue = 'peak_SNRG'  #For peaks,


add_to_title = ''


#%% ============================================= LOAD PHOTOMETRY - Lines =====================================================
def Photometry_Downsample(mouse, protocol, photometry_filetype, week, day, fpath, file, downsample):
    """
    This definition opens the comments, parses and interprets (determines correct, incorrect, phases of the task, etc) them and puts them into a dataframe
    
    These commented out variables below can be used for testing this definition 
    -- comment in these variables and comment out any time it says 'return', then you can select and run the code from here down to test this definition
    """     
#    mouse = 'm360'
#    protocol = 'Plasticity'
#    fpath = "D:\\DATA_IN\\"
#    file = 'm360_Plasticity_w3d1'
#    week = 'w3'
#    day = 'd1'
#    photometry_filetype = 'photon count output'   
    
    if photometry_filetype == 'photon count output': 
        input_yvalue = 'LRCpcG'
        #output_yvalue = 'pDFoFG'
    elif photometry_filetype == 'unmix coeff output':
        input_yvalue = 'LRCcoeffG'
        #output_yvalue = 'pDCoCG'
        
    photofile = glob(f'{fpath}/{file}*{photometry_filetype}.xlsx')
    #print(nev_file)
    if len(photofile) > 1:
        print('error there is more than one photometry file starting with ' + fpath +  '/' + file)
        return 'not here'
    elif len(photofile) < 1:
        print('error, no photometry file exists for ' + fpath + '/' + file)
        return 'not here'
    else: 
        fid2 = str(glob(f'{fpath}/{file}**{photometry_filetype}.xlsx')[0])
        print(fid2) 
        
    photometry_all = pd.read_excel(fid2)
    photometry_all = photometry_all.rename({"Unnamed: 1": 'TimeStamps'},axis=1)         
    photometry_all.insert(0, 'TimeStampsZerod',(photometry_all['TimeStamps'] - photometry_all['TimeStamps'].iloc[0]) / 1000)    

    photometry_temp = pd.DataFrame()
    
    RoundTime = round(photometry_all['TimeStampsZerod'], 5) #change the number of decimal points for rounding
    
#    mouselist = [mouse] * len(photometry_all['TimeStampsZerod']) 
    photometry_temp.insert(0, 'Mouse', mouse)
    photometry_temp.insert(1, 'Protocol', protocol)
    photometry_temp.insert(2, 'TimeStamp', RoundTime )
    photometry_temp.insert(3, input_yvalue, photometry_all[input_yvalue])
    photometry_temp.insert(4, 'Week', week)
    photometry_temp.insert(5, 'Day', day)
#    photometry_temp.insert(4, 'pDFoFRatio', photometry_all['pDFoFRatio'] )
#    photometry_temp.insert(5, 'zScorepDFoFRatio', photometry_all['zScorepDFoFRatio'] )
#    photometry_temp.insert(6, 'pDFoFG', photometry_all['pDFoFG'] )
#    photometry_temp.insert(7, 'zScorepDFoFG', photometry_all['zScorepDFoFG'] )
#    photometry_temp.insert(8, 'pcRowSumG', photometry_all['pcRowSumG'])
    
    
    
    photo_times = photometry_temp['TimeStamp']
    photo_data = photometry_temp[input_yvalue]
    
    #This portion finds the trials by a two second gap
    trial_ends = []
    trial_starts = []    
    trial_starts.append(0) 
    for time_i in range(1,len(photometry_temp)):  
        current_time = photo_times[time_i]
        last_time = photo_times[time_i-1]
        #print (current_time)
        #print (next_time)
        if (current_time - last_time) > 1.5 and (current_time - last_time) < 5:
            #print('gap is at' + str(time_i) + ' time is ' + str(current_time) + ' and ' + str(last_time))
            trial_ends.append(time_i-1)
            trial_starts.append(time_i)
    trial_ends.append(len(photometry_temp)-1)
       
#    print (trial_ends)
#    print(trial_starts)
    
#    for start, end in zip(trial_starts, trial_ends):
#        plt.plot(photo_data[start:end])
#        plt.show()
#   
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
        
    for this_start_index in trial_starts:
        this_start_time = photo_times[this_start_index]
        
#        data_indices = np.where(
#            (photo_times >= (this_start)) &
#            (photo_times <= (this_start+30)))[0]
        i=0
        for start_i_ms in range(0,30000,downsample_ms):
            start_i = start_i_ms/1000
            end_i = start_i + downsample

            # create sliding window ("timezone") that includes photo_times that are within 100 ms. The sliding window starts at the
            # beginning of each trial (starts at each element "trial_starts") and slides for 30 seconds, combining
            # photo_time indices into 100 ms bins
            
            timezone = np.where(
            (photo_times >= (this_start_time+start_i)) &
            (photo_times < (this_start_time+end_i)))[0]
            
            if timezone.size == 0:
                print('empty')
                
            elif timezone.size > 0:
                tempdata = list(photometry_temp[input_yvalue].loc[timezone])
                
                average_tempdata = statistics.mean(tempdata)
                
                downsample_data.append(average_tempdata)
                downsample_trialtime.append(start_i)
                downsample_index.append(i)
                downsample_tottime.append(this_start_time+start_i)
#                trial_start_count.append(this_start)
            i+=1

            
    new_data.insert(0, 'trial_index', downsample_index)
    new_data.insert(1, 'trial_time', downsample_trialtime)
    new_data.insert(2, 'total_time', downsample_tottime)
    new_data.insert(3, 'downsample_photoncounts', downsample_data)
    new_data.insert(4, 'protocol', protocol)
    new_data.insert(5, 'day', day)
    new_data.insert(6, 'week', week)
    new_data.insert(7, 'mouse', mouse)
#    new_data.insert(8, 'trial_start', trial_start_count)
            
            
#   new_data.to_csv ("C:\\Users\\mikofskyrm\\Desktop\\Photometry\\photodata_test.csv", index = None, header=True)
            
#    print(photometry_temp)
    return new_data


#%% ========================== DO NOT CHANGE THIS PART =======================================================
"""
This is where you can add to the mouse groups but be careful about changing anything else!
"""
if mouse_group == 'camk_gcamp': 
    mouse_list = ['m343', 'm328', 'm322', 'm342', 'm344', 'm349'] #Cohort 1 (camk gcamp, sst geco, hpc chrimson)
elif mouse_group == 'sst_gcamp':
    mouse_list = ['m356', 'm357', 'm358', 'm360', 'm362', 'm363', 'm364'] #Cohort 2 (sst gcamp)
elif mouse_group == 'sst_gcamp_nochr':
    mouse_list = ['m347', 'm348']
elif mouse_group == 'pv_gcamp':
    mouse_list = ['m368', 'm369']
elif mouse_group == 'sst_egfp':
    mouse_list = ['m366', 'm365']
elif mouse_group == 'test':
    mouse_list = ['m357']
elif mouse_group == 'all':
    mouse_list = ['m343', 'm328', 'm322', 'm342', 'm344', 'm349', 'm356', 'm357', 'm358', 'm360', 'm362', 'm363', 'm364',
                  'm347', 'm348', 'm368', 'm369', 'm366', 'm365']
else:
    print ('Mouse group is not valid. The code will now quit, please try again')
    sys.exit()

filename = protocol + '_' + mouse_group + add_to_title

fpath = input_directory


title = filename

                                
photodata_all = pd.DataFrame()
this_photodata = pd.DataFrame()

for m in range(len(mouse_list)):
    mouse = mouse_list[m]
    
    for week in week_list:
        
        for day in day_list:
            
            file = str(mouse) + '_' + str(protocol) + '_' + str(week) + str(day)
            
            print(file)
            
            this_photodata = Photometry_Downsample(mouse = mouse, protocol = protocol, photometry_filetype = photometry_filetype, week = week, day = day, fpath = fpath, file = file, downsample =  downsample)
            if  type(this_photodata) == str:
                File_file = ([mouse, mouse_group, protocol, week, day, file, 'not here', 'NA'])
                File_List = np.vstack((File_List, File_file))
                np.savetxt(output_directory + "Stim_PhotoFiles_" + protocol + '_' + mouse_group + ".csv", File_List, delimiter=",",fmt='%s')

            else:
                length = len(this_photodata)
                File_file = ([mouse, mouse_group, protocol, week, day, file, 'here', length])
                File_List = np.vstack((File_List, File_file))
                this_photodata.to_csv (output_directory + "photodata_" + file + ".csv", index = None, header=True)
                np.savetxt(output_directory + "Stim_PhotoFiles_" + protocol  + '_' + mouse_group + ".csv", File_List, delimiter=",",fmt='%s')
