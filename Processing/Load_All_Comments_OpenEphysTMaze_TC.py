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
#import brpylib

sns.set(style="darkgrid")
sns.set_palette('muted')
sns.set_context("notebook")
pd.set_option('display.max_columns', 30)

#%% ========================== COLLECT DATA =======================================================
"""
INSTRUCTIONS:
In this portion you must:
    - set your input directory (for the raw openephys files) and output directory
    - choose a mouse group (options are in comments)
    - choose a protocol, day(s)
    - the mouse groups must be added to the code at the end of this file

"""

File_List = (['mouse', 'group', 'test', 'day', 'filename', 'here', 'dataframe length'])


################################################ CHANGE THESE ONCE FOR YOUR COMPUTER ################################################
input_directory = "C:\\Users\\clarityt2\\Documents\\Gordon Lab\\Photometry Processing\\TMAZE Test\\"
output_directory = "C:\\Users\\clarityt2\\Documents\\Gordon Lab\\Photometry Processing\\TMAZE Test\\Test Output\\"

################################################ CHANGE THESE FOR WHAT YOU WANT TO RUN ################################################
mouse_group = 'test' #'all', 'sst_gcamp', 'pv_gcamp', 'camk_gcamp', 'sst_gcamp_nochr', 'sst_egfp' 

test_list = ['Train'] # 'Test', 'Delays'
day_list = ['d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7']

add_to_title = '_example' #You can optionally add something to the output files

#%% ========================== Load Comments =======================================================
def load_comments(mouse, test, day, fpath, file, main_or_meta):
        
    """
    This definition opens the comments, splits which are events and which are metadata and outputs as a dataframe
    
    These commented out variables below can be used for testing this definition 
    -- comment in these variables and comment out any time it says 'return', then you can select and run the code from here down to test this definition
    """
    
    # mouse = 'm123'
    # test = 'Train'
    # day = 'd1'
    # fpath = "C:\\Users\\mikofskyrm\\Desktop"
    file = "m123_Train_d1"

    folder = file
    
    
    file1 = glob(f'{fpath}/{folder}*/experiment1\\recording1\\events\\Network_Events-106.0\\TEXT_group_1\\text.npy')

    if len(file1) > 1:
        print('error there is more than one comment file starting with ' + str(fpath) + str(file1))
        return 'not here'
    elif len(file1) < 1:
        print('error there is no comment file for ' + str(fpath) + str(file1))
        return 'not here'
    else: 
        print(str(file1[0]))
        file_to_load1 = file1[0]
  
    file2 = glob(f'{fpath}/{folder}*/experiment1\\recording1\\events\\Network_Events-106.0\\TEXT_group_1\\timestamps.npy')

    if len(file2) > 1:
        print('error there is more than one comment timestamp file starting with ' + str(fpath) + str(file2))
        return 'not here'
    elif len(file2) < 1:
        print('error there is no comment timestamp file for ' + str(fpath) + str(file2))
        return 'not here'
    else: 
        print(str(file2[0]))
        file_to_load2 = file2[0]
      
    comment_texts = []    
    comment_texts = np.load(file_to_load1)
    timestamps=np.load(file_to_load2)
    timestamps_seconds = timestamps/30000
    timestamps_seconds=timestamps_seconds-timestamps_seconds[0]
#    print(timestamps_seconds)

    comments = list()
    extrainfo = list()
    
    for comment_text, timestamp in zip(comment_texts, timestamps_seconds):
        if "trial" in comment_text.decode():
            #print(comment_text[item])
            commentdict = json.loads(comment_text)
            commentdict['timestamp'] = timestamp
            comments.append(commentdict)
        elif "header" in comment_text.decode():
            extrainfo.append(json.loads(comment_text))
    tempdata1 = pd.DataFrame(comments)
    tempdata2 = pd.DataFrame(extrainfo)
    
    
    tempdata1['t_delay'] = tempdata1['t_delay'].astype(str) +  ' sec'

    for trial_i in tempdata1['trial'].unique():
        correct_status_loc = np.where((tempdata1['trial']==trial_i) & (tempdata1['event']=='choice_selection'))[0]      # Determines the indices of the "choice selection" events
        if correct_status_loc.size == 0:
            continue
        print(correct_status_loc[0])
        correct_status = tempdata1['correct_status'][correct_status_loc[0]]     # Identifies if the "choice selection" event was correct or incorrect
        print(correct_status)
        trial_indexes = np.where((tempdata1['trial']==trial_i))[0]
        for index in trial_indexes:
            tempdata1['correct_status'][index] = correct_status        # Puts 'Correct' or 'Incorrect' in each unique index row based on the outcome of the "choice selection"
    
    tempdata1['phase_broad'] = ""       
    
    for row_i in range(len(tempdata1['tmaze_phase'])):
        row = tempdata1['tmaze_phase'][row_i]
        if 'ITI' in row:
            tempdata1['phase_broad'][row_i] = 'ITI'
        elif 'sample' in row:
            tempdata1['phase_broad'][row_i] = 'sample'
        elif 'delay' in row:
            tempdata1['phase_broad'][row_i] = 'delay'
        elif 'choice' in row:
            tempdata1['phase_broad'][row_i] = 'choice'
        else:
            tempdata1['phase_broad'][row_i] = 'error'
        #print(row)
    
    tempdata1.rename(columns={"tmaze_phase":"phase_specific"})        
            
        
    if main_or_meta == 'main':

        return tempdata1
    
    if main_or_meta == 'meta':
        
        return tempdata2



#%% ========================== DO NOT CHANGE THIS PART =======================================================

"""
This is where you can add to the mouse groups but be careful about changing anything else!
"""
if mouse_group == 'all':
    mouse_list = []
elif mouse_group == 'test':
    mouse_list = ['mtest']

else:
    print ('Mouse group is not valid. The code will now quit, please try again')
    sys.exit()

filename = mouse_group + add_to_title

fpath = input_directory

title = filename


#This is the start and end times of the window to look for the max value -- all trials start at 0s and the stim is at 10s
               
commentdata_all = pd.DataFrame()
this_commentdata = pd.DataFrame()

for m in range(len(mouse_list)):
    mouse = mouse_list[m]
    
    for test in test_list:
        
        for day in day_list:
            
            file = str(mouse) + '_' + str(test) + '_' + str(day)
            
            print(file)
            
            this_commentdata = load_comments(mouse = mouse, test = test, day = day, fpath = fpath, file = file, main_or_meta = 'main')
            if  type(this_commentdata) == str:
                File_file = ([mouse, mouse_group, test, day, file, 'not here', 'NA'])
                File_List = np.vstack((File_List, File_file))
                np.savetxt(output_directory + "TMazeOpenEphys_Comments_" + mouse_group + add_to_title + ".csv", File_List, delimiter=",",fmt='%s')

            else:
                length = len(this_commentdata)
                File_file = ([mouse, mouse_group, test, day, file, 'here', length])
                File_List = np.vstack((File_List, File_file))
                this_commentdata.to_csv (output_directory + "commentdataNEW_" + file + add_to_title + ".csv", index = None, header=True)
                np.savetxt(output_directory + "TMazeOpenEphys_NEWComments_" + mouse_group + ".csv", File_List, delimiter=",",fmt='%s')
                this_commentdata = load_comments(mouse = mouse, test = test, day = day, fpath = fpath, file = file, main_or_meta = 'meta')
                this_commentdata.to_csv (output_directory + "comment_metadata_" + file + add_to_title + ".csv", index = None, header=True)