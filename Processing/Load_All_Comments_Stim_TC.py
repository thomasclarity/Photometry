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
    - set your input directory (for the raw openephys files) and output directory
    - choose a mouse group (options are in comments)
    - choose a protocol, week(s), day(s)
    - the mouse groups must be added to the code at the end of this file

"""

File_List = (['mouse', 'group', 'protocol', 'week', 'day', 'filename', 'here', 'dataframe length'])


################################################ CHANGE THESE ONCE FOR YOUR COMPUTER ################################################
#input_directory = "C:\\Users\\clarityt2\\Documents\\Gordon Lab\\Photometry Processing\\vHPC_PFC_plasticity\\OE Comment Input\\"
#output_directory = "C:\\Users\\clarityt2\\Documents\\Gordon Lab\\Photometry Processing\\vHPC_PFC_plasticity\\Comment Data Output\\"
input_directory = "F:\\Clarity\\Gordon Lab\\OpenEphys\\OE_Tracking_Input\\"
output_directory = "F:\\Clarity\\Gordon Lab\\OpenEphys\\Tracking_Comment_Output\\"

################################################ CHANGE THESE FOR WHAT YOU WANT TO RUN ################################################
mouse_group = 'sst_gcamp' #'test' #'sst_gcamp', 'pv_gcamp', 'camk_gcamp', 'sst_gcamp_nochr', 'sst_egfp'

protocol = 'Plasticity' #'Plasticity' or 'IO'
week_list = ['w0', 'w1', 'w2', 'w3', 'w4']
day_list = ['d1', 'd2']


add_to_title = '' #You can optionally add something to the output files


#%% ========================== Load Comments =======================================================
def load_comments(mouse, protocol, week, day, fpath, file, main_or_meta):
     
    """
    This definition opens the comments, splits which are events and which are metadata and outputs as a dataframe
    
    These commented out variables below can be used for testing this definition 
    -- comment in these variables and comment out any time it says 'return', then you can select and run the code from here down to test this definition
    """
#    mouse = 'm365'
#    test = 'Plasticity'
#    fpath = "D:\\Plasticity"

    file = "GPIO2_Train_d1"

    folder = file
    
    
    file1 = glob(f'{fpath}/{folder}*/experiment1\\recording*\\events\\Network_Events-106.0\\TEXT_group_1\\text.npy')

    if len(file1) > 1:
        print('error there is more than one comment file starting with ' + str(fpath) + str(file1))
        return 'not here'
    elif len(file1) < 1:
        print('error there is no comment file for ' + str(fpath) + str(file1))
        return 'not here'
    else: 
        print(str(file1[0]))
        file_to_load1 = file1[0]
  
    file2 = glob(f'{fpath}/{folder}*/experiment1\\recording*\\events\\Network_Events-106.0\\TEXT_group_1\\timestamps.npy')

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
    timedf = pd.DataFrame(timestamps_seconds)
#    print(timestamps_seconds)

    comments = list()
    extrainfo = list()
    for comment_text, timestamp in zip(comment_texts, timestamps_seconds):
        if "trial" in comment_text.decode():
            #print(comment_text[item])
            commentdict = json.loads(comment_text)
            commentdict['timestamp'] = timestamp
            comments.append(commentdict)
        elif "opsinconstruct1" in comment_text.decode():
            extrainfo.append(json.loads(comment_text))
    tempdata1 = pd.DataFrame(comments)
    tempdata2 = pd.DataFrame(extrainfo)

    tempdata1.to_csv(output_directory + "GPIO2_comments" + file + add_to_title + ".csv", index=None, header=True)
    #Adding some extra info into the comments dataframe
#    repcell1 = tempdata2["reportercelltype1"][0]
#    tempdata1.insert(24, 'reporter_celltype_1', repcell1)
#    
#    repind1 = tempdata2["reporterindicator1"][0]
#    tempdata1.insert(25, 'reporter_indicator_1', repind1)
#    
#    opscell1 = tempdata2["msg_opsincelltype1"][0]
#    tempdata1.insert(26, 'opsin_celltype_1', opscell1)
#    
#    opscon1 = tempdata2["opsinconstruct1"][0]
#    tempdata1.insert(27, 'opsin_construct_1', opscon1)    
#    
#    virusweeks = tempdata2["virusweeks"][0]
#    tempdata1.insert(28, 'virus_weeks', virusweeks)     
    
    
#    print(tempdata1)
    
    if main_or_meta == 'main':

        return tempdata1
    
    if main_or_meta == 'meta':
        
        return tempdata2


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
    mouse_list = ['m322']
elif mouse_group == 'all':
    mouse_list = ['m343', 'm328', 'm322', 'm342', 'm344', 'm349', 'm356', 'm357', 'm358', 'm360', 'm362', 'm363', 'm364',
                  'm347', 'm348', 'm368', 'm369', 'm366', 'm365']
else:
    print ('Mouse group is not valid. The code will now quit, please try again')
    sys.exit()

filename = protocol + '_' + mouse_group + add_to_title

fpath = input_directory

title = filename
           
commentdata_all = pd.DataFrame()
this_commentdata = pd.DataFrame()

for m in range(len(mouse_list)):
    mouse = mouse_list[m]
    
    for week in week_list:
        
        for day in day_list:
            
            file = str(mouse) + '_' + str(protocol) + '_' + str(week) + str(day)
            
            print(file)
            
            this_commentdata = load_comments(mouse = mouse, protocol = protocol, week = week, day = day, fpath = fpath, file = file, main_or_meta = 'main')
            if  type(this_commentdata) == str:
                File_file = ([mouse, mouse_group, protocol, week, day, file, 'not here', 'NA'])
                File_List = np.vstack((File_List, File_file))
                np.savetxt(output_directory + "StimOpenEphys_Comments_" + protocol + '_' + mouse_group + add_to_title + ".csv", File_List, delimiter=",",fmt='%s')
                
                
            else:
                length = len(this_commentdata)
                File_file = ([mouse, mouse_group, protocol, week, day, file, 'here', length])
                File_List = np.vstack((File_List, File_file))
                this_commentdata.to_csv (output_directory + "commentdata_" + file + add_to_title + ".csv", index = None, header=True)
                np.savetxt(output_directory + "StimOpenEphys_Comments_" + protocol  + '_' + mouse_group + add_to_title + ".csv", File_List, delimiter=",",fmt='%s')
                this_commentdata = load_comments(mouse = mouse, protocol = protocol, week = week, day = day, fpath = fpath, file = file, main_or_meta = 'meta')
                this_commentdata.to_csv (output_directory + "comment_metadata_" + file + add_to_title + ".csv", index = None, header=True)
