#%%
#from os.path import expanduser as eu

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as patches
import scipy
from scipy import stats
import statistics 
sys.path.append("F:\\Clarity\\Gordon Lab\\Photometry Processing\\Python Scripts\\")
from glob import glob
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
import Photometry_Analysis_Stim_utils_TC as Analysis
import json
sns.set(style="darkgrid")
sns.set_palette('muted')
sns.set_context("poster")
pd.set_option('display.max_columns', 30)


#%% ========================== COLLECT DATA =======================================================
"""
INSTRUCTIONS:
In this portion you must:
    - set your input directory (for the commentdata and photodata files) and output directory (for output files) 
    - graphs will go in the folder where the code is stored
    - choose a mouse group (options are in comments)
    - the mouse groups must be added to the code at the end of this file
    - choose a protocol, week(s), day(s)
    
    - Choose "graphtype" (lines, peaks, heatmap, peaks_average)
    - Change yvalue to correspond with graph_type
    - For peaks and peaks_average choose a time window 'prestim' or 'poststim'
    - Choose items in "categories" ('plasticity', 'before_after', 'week', 'day', 'mouse' for Plasticity and 'frequency', 'pulsenum', 'day', 'laserpower, 'mouse' for IO)
    
"""
################################################ CHANGE THESE ONCE FOR YOUR COMPUTER ################################################

comment_input_directory = "F:\\Clarity\\Gordon Lab\\Photometry Processing\\TEST2\\Test Output\\"
photo_input_directory = "F:\\Clarity\\Gordon Lab\\Photometry Processing\\TEST2\\Test Output\\"
fig_output_directory = "F:\\Clarity\\Gordon Lab\\Photometry Processing\\TEST2\\Test Output\\"
csv_output_directory = "F:\\Clarity\\Gordon Lab\\Photometry Processing\\TEST2\\Test Output\\"

################################################ CHANGE THESE FOR WHAT YOU WANT TO RUN ################################################
mouse_group = 'example' #'sst_gcamp', 'pv_gcamp', 'camk_gcamp', 'sst_gcamp_nochr', 'sst_egfp' , 'example'

protocol = 'Plasticity' #'Plasticity' or 'IO'
week_list = ['w1'] #, 'w2', 'w3', 'w4'] #'w0', 'w1', 'w2', 'w3', 'w4'
day_list = ['d1']#,'d2'] #, 'd2'
photometry_filetype = 'photon count output' #'photon count output' or 'unmix coeff output'

graphtype = "peaks" #'peaks' or 'lines' or 'heatmap' or 'peaks_average'

#If you are graphing a peak plot, set this to select a time period to look for max value
prestim_or_poststim = 'poststim' #options are 'prestim' (7.5 to 2.5 seconds before stim) or 'poststim' (0 to 5 seconds after stim)


#You must change this value to match what type of graph you are making:
yvalue = 'pDFoFG'    #For lines and peaks_average, photon count output file
#yvalue = 'pDCoCG'    #For lines, unmix coeff output file 
#yvalue = 'raw_photoncounts'
#yvalue = 'peak_dFoFG'  #For peaks, photon count output file
#yvalue = 'peak_dCoCG'  #For peaks, unmix coeff output file 
#yvalue = 'peak_SNRG'  #For peaks,


# Pick Graphing categories: 'frequency', 'laserpower', 'pulsenum', 'day', 'week', 'plasticity', 'before_after', 'mouse' 
    # for mouse, lines will automatically split by mouse but peaks will automatically pool mice -- if you want mice separated for peaks, add mouse to categories
categories = ['plasticity', 'before_after', 'week', 'day']
#['frequency', 'pulsenum', 'day']

#['plasticity', 'before_after', 'week', 'day']

add_to_title = ''

ymin = None
ymax = None


#%% ========================== DO NOT CHANGE THIS PART =======================================================
if mouse_group == 'camk_gcamp': 
    mouse_list = ['m343', 'm328', 'm322', 'm342', 'm344', 'm349'] #Cohort 1 (camk gcamp, sst geco, hpc chrimson)
elif mouse_group == 'sst_gcamp':
    mouse_list = ['m356', 'm357', 'm358', 'm360', 'm362', 'm363', 'm364']
    #['m356', 'm357', 'm358', 'm360', 'm362', 'm363', 'm364'] #Cohort 2 (sst gcamp)
elif mouse_group == 'sst_gcamp_nochr':
    mouse_list = ['m347', 'm348']
elif mouse_group == 'pv_gcamp':
    mouse_list = ['m368', 'm369']
elif mouse_group == 'sst_egfp':
    mouse_list = ['m366', 'm365']
elif mouse_group == 'example':
    mouse_list = ['m357']
else:
    print ('Mouse group is not valid. The code will now quit, please try again')
    sys.exit()

filename = protocol + '_' + mouse_group + add_to_title

comment_fpath = comment_input_directory
photo_fpath = photo_input_directory
timestamps_yes_or_no = 'no' #'yes' or 'no' this will change the way comments are processed, default to no

#if not mouse_list[0] in filename:
#    print('error filename is incorrect')
#    g = input('try again with the filename: \n')
#    filename = g
    
if graphtype == 'peaks':
    filename = filename + '_peaks_' + prestim_or_poststim    
elif graphtype == 'lines':    
    filename = filename + "_line"
elif graphtype == 'heatmap':    
    filename = filename + "_heatmap"
elif graphtype == "peaks_average":
    filename = filename + "_peaks_average_" + prestim_or_poststim

title = filename

cat = 0
for cat in range(len(categories)):
    if categories[cat] != ('pulsenum'):
        if  categories[cat] != ('frequency'):
            if categories[cat] != ('laserpower'):
                if categories[cat] != ('stimtype'):
                    if categories[cat] != ('day'):
                        if categories[cat] != ('week'):
                            if categories[cat] != ('plasticity'):
                                if categories[cat] != ('mouse'):
                                    if categories[cat] != ('before_after'):
                                        print ('Some element of categories is incorrect, there may be a typo. The code will now quit, please try again')
                                        sys.exit()


#This is the start and end times of the window to look for the max value -- all trials start at 0s and the stim is at 10s
if prestim_or_poststim == 'poststim':
    t_start = 10
    t_end = 15
if prestim_or_poststim == 'prestim':
    t_start = 2.5
    t_end = 7.5

commentdata_all = pd.DataFrame()
photodata_all = pd.DataFrame()

for m in range(len(mouse_list)):
    mouse = mouse_list[m]
    
    for week in week_list:
        
        for day in day_list:
            
            file = str(mouse) + '_' + str(protocol) + '_' + str(week) + str(day)
            
            print(file)
            
            commentdata_all = commentdata_all.append(Analysis.load_comments(mouse = mouse, protocol = protocol, week = week, day = day, fpath = comment_fpath, file = file), ignore_index=True)
            
            if graphtype == 'peaks':
                photodata_all = photodata_all.append(Analysis.Peaks_photometry_data(mouse = mouse, protocol = protocol, photometry_filetype = photometry_filetype, week = week, day = day, fpath = photo_fpath, file = file, t_start = t_start, t_end = t_end), ignore_index=True)
            elif graphtype == 'lines':
                photodata_all = photodata_all.append(Analysis.Lines_photometry_data(mouse = mouse, protocol = protocol, photometry_filetype = photometry_filetype, week = week, day = day, fpath = photo_fpath, file = file), ignore_index=True)
            elif graphtype == 'heatmap':
                photodata_all = photodata_all.append(Analysis.Lines_photometry_data(mouse = mouse, protocol = protocol, photometry_filetype = photometry_filetype, week = week, day = day, fpath = photo_fpath, file = file), ignore_index=True)
            elif graphtype == "peaks_average":
                photodata_all = photodata_all.append(Analysis.PrepAverage_photometry_data(mouse = mouse, protocol = protocol, photometry_filetype = photometry_filetype, week = week, day = day, fpath = photo_fpath, file = file, t_start = t_start, t_end = t_end), ignore_index=True)
            else:
                print('error graph type is incorrect')

if graphtype == 'peaks':
    all_data = Analysis.Combine_Comments_Photometry_Peaks(yvalue, commentdata_all, photodata_all, mouse_list, protocol, filename, categories)
elif graphtype == 'lines':
    all_data = Analysis.Combine_Comments_Photometry_Lines(yvalue, commentdata_all, photodata_all, mouse_list, protocol, filename, categories, timestamps_yes_or_no)
elif graphtype == 'heatmap':
    all_data = Analysis.Combine_Comments_Photometry_Lines(yvalue, commentdata_all, photodata_all, mouse_list, protocol, filename, categories, timestamps_yes_or_no)
elif graphtype == "peaks_average":
    all_data = Analysis.Combine_Comments_Photometry_Peaks_Average(yvalue, commentdata_all, photodata_all, mouse_list, week_list, day_list, protocol, filename, categories, timestamps_yes_or_no)

mouse_name = '_'
for mouse in mouse_list:
    mouse_name = mouse + mouse_name 
        
photodata_all.to_csv (csv_output_directory + "output_photodata_" + mouse_name + filename + ".csv", index = None, header=True)
commentdata_all.to_csv (csv_output_directory + "output_commentdata_" + mouse_name + filename + ".csv", index = None, header=True)
all_data.to_csv (csv_output_directory + "output_graphdata_" + mouse_name + filename + ".csv", index = None, header=True)

if graphtype == 'peaks':
    Analysis.GraphPeaksAndSave(all_data, yvalue, filename, categories, ymin, ymax, mouse_list, fig_output_directory)
elif graphtype == 'lines':
    Analysis.GraphLineAndSave(all_data, yvalue, filename, categories, ymin, ymax, mouse_list, fig_output_directory)
elif graphtype == 'heatmap':
    Analysis.GraphHeatMap(all_data, yvalue, filename, categories, ymin, ymax, mouse_list, day_list, week_list, fig_output_directory)
elif graphtype == "peaks_average":
    Analysis.GraphPeaksAndSave(all_data, yvalue, filename, categories, ymin, ymax, mouse_list, fig_output_directory)
    
#%% ========================== This part can be rerun to generate new graphs from the same dataset and of the same type (ie lines) =======================================================
"""
This can be used to run additional graphs (only of the same type) based on the same loaded data, by using different/additional categories
"""
msg1 = input("Would you like to run additional graphs (of the same type) with different categories? (yes or no) This will save as a new pdf file. \n")

filename_default = filename

while msg1 == 'yes':
    msg2 = input("What would you like to add to the filename?\n")
    filename = filename_default + msg2
    msg3 = input("What do you want to include in categories? ('frequency', 'laserpower', 'pulsenum', 'day', 'week', 'plasticity', 'mouse') \n")
    
    catlist = ['frequency', 'laserpower', 'pulsenum', 'day', 'week', 'plasticity', 'before_after', 'mouse' ]
    categories = []
    
    for cat_item in catlist:
        if cat_item in msg3:
            categories.append(cat_item)
            print (categories)
            
    if graphtype == 'peaks':
        Analysis.GraphPeaksAndSave(all_data, yvalue, filename, categories, ymin, ymax, mouse_list, fig_output_directory)
    elif graphtype == 'lines':
        Analysis.GraphLineAndSave(all_data, yvalue, filename, categories, ymin, ymax, mouse_list, fig_output_directory)
    elif graphtype == 'heatmap':
        Analysis.GraphHeatMap(all_data, yvalue, filename, categories, ymin, ymax, mouse_list, day_list, week_list, fig_output_directory)
    elif graphtype == "peaks_average":
        Analysis.GraphPeaksAndSave(all_data, yvalue, filename, categories, ymin, ymax, mouse_list, fig_output_directory)
        
    print("Graphs completed and saved. \n")
    
    msg1 = input("Would you like to run additional graphs? (yes or no) This will save as a new pdf file.\n")

            
    

#
## Pick Graphing categories: 'frequency', 'laserpower', 'pulsenum', 'day', 'week', 'plasticity', 'mouse' 
#    # for mouse, lines will automatically split by mouse but peaks will automatically pool mice -- if you want mice separated for peaks, add mouse to categories
#categories = ['pulsenum', 'plasticity', 'day', 'week', 'mouse']
#
#
## ------------------------------------------ Don't change this part: -----------------------------------------------------------------------------------
#cat = 0
#for cat in range(len(categories)):
#    if categories[cat] != ('pulsenum'):
#        if  categories[cat] != ('frequency'):
#            if categories[cat] != ('laserpower'):
#                if categories[cat] != ('stimtype'):
#                    if categories[cat] != ('day'):
#                        if categories[cat] != ('week'):
#                            if categories[cat] != ('plasticity'):
#                                if categories[cat] != ('mouse'):
#                                    print ('Some element of categories is incorrect, there may be a typo. The code will now quit, please try again')
#                                    sys.exit()
#
#if lines_or_peaks == 'peaks':
#    Analysis.GraphPeaksAndSave(all_data, yvalue, filename, categories, ymin, ymax, mouse_list)
#elif lines_or_peaks == 'lines':
#    Analysis.GraphLineAndSave(all_data, yvalue, filename, categories, ymin, ymax, mouse_list)            
#      