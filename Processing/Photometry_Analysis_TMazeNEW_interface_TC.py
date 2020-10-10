#%%
#from os.path import expanduser as eu

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
sys.path.append("C:\\Users\\mikofskyrm\\Desktop\\")
import brpylib
from glob import glob
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
import statistics
import Photometry_Analysis_TMazeNEW_utils_RM2020 as Analysis
sns.set(style="darkgrid")
sns.set_context("poster")


#%% ========================== COLLECT DATA =======================================================
"""
INSTRUCTIONS:
In this portion you must:
    - set your input directory (for the comment and photometry files) and output directory (for the output csvs and averaged data)
    - choose a mouse group (options are in comments)
    - choose test(s), day(s)
    - the mouse groups must be added to the code at the end of this file
    - choose cue(s) and categories to run -- READ CATEGORY RULES

"""

input_directory = "C:\\Users\\mikofskyrm\\Desktop\\DATA_OUT\\Processed_Files_TMaze\\"
output_directory = "C:\\Users\\mikofskyrm\\Desktop\\DATA_OUT\\"

mouse_group = 'sst_gcamp' #'sst_gcamp', 'pv_gcamp', 'example'


test_list = ['train'] #'train, 'test', 'delays'
day_list = ['1', '2', '3', '4', '5', '6', '7']


cue_list = ['sample_start', 'choice_start', 'delay_start', 'choice_selection', 'sample_reward', 'start_reward']

'''
CATEGORY RULES -- Pick categories to decide what to graph.  
To calculate the average value or max value across similar trials within a time period use 'averages' then 'mean' or 'max' (automatically runs pre/post cue)
To make line graphs of time periods around cues use 'cue', 'mouse', 'day', 'phase'
To make special graphs comparing sample and choice us 'sample vs choice'
'''
categories = ['sample vs choice']
#['sample vs choice']
#['cue', 'day', 'mouse', 'phase']
#['averages', 'mean'] 
#options are: 'cue', 'day', 'mouse', 'sample vs choice', 'averages', 'mean', 'max'

add_to_filename = "sample_vs_choice_example"

  
#yvalue = 'pDCoCRatio'
#yvalue = 'zScorepDCoCRatio'
yvalue = 'pDCoCG'


#%%################### DO NOT CHANGE THIS PART: ##########################
if mouse_group == 'sst_gcamp':
    mouse_list = ['m209', 'm176', 'm189', 'm208', 'm178', 'm194', 'm195']
elif mouse_group == 'pv_gcamp':
    mouse_list = ['m259', 'm260', 'm261']
elif mouse_group == 'example':
    mouse_list = ['m209']
else:
    print ('Mouse group is not valid. The code will now quit, please try again')
    sys.exit()


fpath = input_directory
commentdata_all = pd.DataFrame()
photodata_all = pd.DataFrame()
all_data = pd.DataFrame()

test_print = ''

for test in test_list:
    test_print = test_print + test
            
    for mouse in mouse_list:
        
        for day in day_list:
        
            file = str(mouse) + '_' + str(test) + str(day)
            
            print(file)
            
    
            commentdata_all = commentdata_all.append(Analysis.load_comment_data(mouse = mouse, test = test, day = day, fpath = fpath, file = file), ignore_index=True)
            photodata_all = photodata_all.append(Analysis.load_photometry_data(mouse = mouse, test = test, day = day, fpath = fpath, file = file), ignore_index=True)

filename = mouse_group + '_' + test_print + '_' + add_to_filename
title = mouse_group

photodata_all.to_csv (output_directory + "output_photodata_" + filename + ".csv", index = None, header=True)
commentdata_all.to_csv (output_directory+ "output_commentdata_" + filename +  ".csv", index = None, header=True)
        


#combining photo data and comments:
for cue in cue_list:
    if 'delay' in cue:
        a = 0
        b = 10
    else:
        a = 5
        b = 5
    all_data = all_data.append(Analysis.combine_data(cue, a, b, title, 'DeltaTimes', yvalue, commentdata_all, photodata_all, mouse_list, test_list, filename))


all_data.to_csv(output_directory + "output_graphdata_" + filename +  ".csv", index = None, header=True) #change to your directory                         

cat = 0
for cat in range(len(categories)):
    if categories[cat] != ('mouse'):
        if  categories[cat] != ('day'):
            if categories[cat] != ('phase'):
                if categories[cat] != ('cue'):
                    if categories[cat] != ('sample vs choice'):
                        if categories[cat] != ('averages'):
                            if categories[cat] != ('mean'):
                                if categories[cat] != ('max'):
                                    print ('Some element of categories is incorrect, there may be a typo. The code will now quit, please try again')
                                    sys.exit()


print('now graphing')
#%% ========================== PEP AVERAGE GRAPH =======================================================
pdf = PdfPages(filename + ".pdf")

filename_default = filename

avg_data = pd.DataFrame()

for test in test_list:
    print(test)
    subset1 = all_data.loc[(all_data['test'] == test)]
    
    title = mouse_group + '_' + test
    
    if 'averages' in categories:
        print('running avgs')
        
        
        for mouse in mouse_list:
            print(mouse)
            
            subset_m = subset1.loc[(subset1['mouse'] == mouse)]
            
            for cue in cue_list:
                
                avg_data = avg_data.append(Analysis.averaging(categories, cue, yvalue, subset_m, mouse, test, pre_or_post = 'pre'))
                avg_data = avg_data.append(Analysis.averaging(categories, cue, yvalue, subset_m, mouse, test, pre_or_post = 'post'))
                

    
    if 'sample vs choice' in categories:
        subset1 = all_data.loc[
                (all_data['PEPcue'] == 'choice_selection') |
                (all_data['PEPcue'] == 'sample_reward')]
        
        subset2 = all_data.loc[
                (all_data['PEPcue'] == 'choice_start') |
                (all_data['PEPcue'] == 'sample_start')]
        
        #ax = sns.heatmap(subset3)
        
        Analysis.graph_PEPcue('Sample vs Choice Selection', 5,5, title, 'DeltaTimes', yvalue, subset1, mouse_list, test_list, day_list, filename, categories, pdf, test)
        
        
        Analysis.graph_PEPcue('Sample vs Choice Run', 5,5, title, 'DeltaTimes', yvalue, subset2, mouse_list, test_list, day_list, filename, categories, pdf, test)

    elif 'cue' in categories:
        
        for cue in cue_list:
            print('graphing ' + cue)
            
            subset2 = subset1.loc[(subset1['PEPcue'] == cue)]
            
            if 'delay' in cue:
                time_a = 0
                time_b = 30
            else:
                time_a = 5
                time_b = 5
                
            Analysis.graph_PEPcue(cue, time_a, time_b, title, 'DeltaTimes', yvalue, subset2, mouse_list, test_list, day_list, filename, categories, pdf, test)
##          
            
if 'averages' in categories:            
    #print(avg_data)
    avg_data.to_csv("C:\\Users\\mikofskyrm\\Desktop\\DATA_OUT\\TMaze_avgdata" + filename +  ".csv", index = None, header=True) #change to your directory                             
    subset = avg_data.loc[(avg_data['result'] != 'both')]

    sns.catplot(x='result', y='peak_pDCoCG', hue='mouse', col = 'cue', row='period', kind = 'point', data=avg_data, join=True)
    pdf.savefig(bbox_inches='tight')

    sns.catplot(x='result', y='peak_pDCoCG', hue='mouse', col = 'cue', row='period', kind = 'point', data=subset, join=True)
    pdf.savefig(bbox_inches='tight')

    #sns.catplot(x='period', y='peak_pDCoCG', hue='mouse', col = 'result', row='cue', kind = 'point', data=subset, join=True)
    sns.catplot(x='period', y='peak_pDCoCG', col = 'result', row='cue', kind = 'box', data=avg_data)
    pdf.savefig(bbox_inches='tight')
    
    sns.catplot(x='result', y='peak_pDCoCG', col = 'period', row='cue', kind = 'box', data=subset)
    pdf.savefig(bbox_inches='tight')

    #sns.catplot(x='cue', y='peak_pDCoCG', hue='mouse', col = 'period', row='result', kind = 'point', data=subset, join=True)
#    sns.catplot(x='cue', y='peak_pDCoCG', col = 'period', row='result', kind = 'box', data=subset)
#    pdf.savefig(bbox_inches='tight')


pdf.close()        
            

#ax1 = sns.relplot(x='TimeStamp', y='pDCoCRatio', kind = 'line', data = pHerehotodata_all, height=10)
#ax1.fig.suptitle('PEP Averaged Correct and Incorrect Cue is '+ PEPcue + ' ' + PEP_name)
#g1.fig.suptitle('Sample Period Time(s) for M02G, M03 for each day ' + str(test_list[0:7]))