# -*- coding: utf-8 -*-

"""
Created on Wed Sept 16 13:10:24 2020

@author: tclarity - based on Load_All_Comments_OpenEphysTMAZE by mikofskyrm

This script loads raw OpenEphys tracking files, downsamples them, and saves the data into csv files
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
from glob import glob
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
import json
import time
import tkinter as tk
from tkinter.filedialog import askdirectory
import struct
import os
import quantities as pq
import itertools

# import brpylib

sns.set(style="darkgrid")
sns.set_palette('muted')
sns.set_context("notebook")
pd.set_option('display.max_columns', 30)
#np.set_printoptions(threshold=sys.maxsize)

# prevents tkinter root window from popping up with the 'askdirectory' window
root = tk.Tk()
root.attributes('-topmost', True)
root.withdraw()

# %% ========================== COLLECT DATA =======================================================
"""
INSTRUCTIONS:
In this portion you must:
    - set your input directory (for the raw openephys files containing the DLC tracking data) and output directory
    - choose a mouse group (options are in comments)
    - choose a protocol, day(s)
    - the mouse groups must be added to the code at the end of this file

"""

File_List = (['mouse', 'group', 'test', 'day', 'filename', 'here', 'dataframe length'])

################################################ SET INPUT AND OUTPUT DIRECTORIES ################################################
input_directory = "F:\\Clarity\\Gordon Lab\\OpenEphys\\OE_Tracking_Input\\"
output_directory = "F:\\Clarity\\Gordon Lab\\OpenEphys\\Tracking_Data_Output\\"

# set directories for reading folders
# input_directory = askdirectory(title = 'Select Input Folder that contains raw OpenEphys tracking data files') # shows dialog box and returns the path
# if input_directory:
#     print("Input Folder:", input_directory)
# else:
#     print("Please select an input directory")
#     quit()
#
# # set directories for writing folders
# output_directory = askdirectory(title='Select Tracking Data Output Folder')
# if output_directory:
#     print("Tracking Data Output Folder:", output_directory)
# else:
#     print("Please select an output directory")
#     quit()

################################################ CHANGE THESE FOR WHAT YOU WANT TO RUN ################################################
mouse_group = 'test'  # 'all', 'sst_gcamp', 'pv_gcamp', 'camk_gcamp', 'sst_gcamp_nochr', 'sst_egfp'

test_list = ['Train']  # 'Test', 'Delays'
day_list = ['d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7']

downsample = 0.1 #in seconds

add_to_title = ''  # You can optionally add something to the output files


#%% ===================================== Find Sampling Rate ================================================================

def sample_rate(fpath, folder):
    """
    This definition finds and returns the OpenEphys sampling rate of the tracking data. This number can be found in the 'sync_messages.txt' file.

    """

    sync_path = (glob(f'{fpath}/{folder}*/experiment1\\recording*\\'))      # path to folder where "sync_messages.txt" is located
    sync_path = ''.join(sync_path)  # convert list to string

    sync_messagefile = [f for f in os.listdir(sync_path) if 'sync_messages' in f][0]

    with open(os.path.join(sync_path, sync_messagefile), "r") as sync_data:      # 'r' = read only
        while True:
            splice = sync_data.readline().split()
            if not splice:
                break
            if 'Software' in splice:
                stime = splice[-1].split('@')
                hz_start = stime[-1].find('Hz')
                software_sample_rate = float(stime[-1][:hz_start]) * pq.Hz
                #software_start_time = int(stime[0])

    return software_sample_rate


# %% ========================== Load Comments =======================================================
def load_tracking(mouse, test, day, fpath, file, main_or_meta):
    """
    This definition opens the tracking data, averages the timestamps across sources, downsamples the timestamps and x,y data, and outputs as a dataframe

    These commented out variables below can be used for testing this definition
    -- comment in these variables and comment out any time it says 'return', then you can select and run the code from here down to test this definition
    """

    #mouse = 'm123'
    test = 'Train'
    day = 'd1'
    # fpath = "C:\\Users\\mikofskyrm\\Desktop"
    file = "GPIO2_Train_d1"

    folder = file

    tracking_files = (glob(f'{fpath}/{folder}*/experiment1\\recording*\\events\\Tracking_Port-10*\\BINARY_group_*[1,2,3,4,5,6,7,8,9,10]\\data_array.npy'))
    tracking_files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))     #glob does not put the groups in the correct order, this line sorts them 1-10
    print(tracking_files)

    if len(tracking_files) > 10:
        print('error there is more than 10 tracking files starting with ' + str(fpath) + str(tracking_files))
        return 'not here'
    elif len(tracking_files) < 1:
        print('error there is no tracking file for ' + str(fpath) + str(tracking_files))
        return 'not here'
    else:
        print(str(tracking_files[0]))


    timestamp_files = glob(f'{fpath}/{folder}*/experiment1\\recording*\\events\\Tracking_Port-10*\\BINARY_group_*[1,2,3,4,5,6,7,8,9,10]\\timestamps.npy')
    timestamp_files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))  # glob does not put the groups in the correct order, this line sorts them 1-10
    print(timestamp_files)

    if len(timestamp_files) > 10:
        print('error there is more than one tracking timestamp file starting with ' + str(fpath) + str(timestamp_files))
        return 'not here'
    elif len(timestamp_files) < 1:
        print('error there is no tracking timestamp file for ' + str(fpath) + str(timestamp_files))
        return 'not here'
    else:
        print(str(timestamp_files[0]))

# average timestamps across tracking sources
    timestamps = []
    for file in timestamp_files:
        raw_timestamp = np.load(file)
        time_df = pd.DataFrame(raw_timestamp)
        timestamps_seconds = raw_timestamp / sample_rate(fpath, folder)
        time_sec_df = pd.DataFrame(timestamps_seconds)
        timestamps_seconds = timestamps_seconds - timestamps_seconds[0]
        temp_timestamps = pd.DataFrame(timestamps_seconds)
        print(temp_timestamps.to_string())
        timestamps.append(temp_timestamps)

    timestamps_df = pd.concat(timestamps, axis=1)
    #timestamps_df.to_csv(output_directory + "timestamps_test.csv", index=None, header=True)
    avg_timestamps = timestamps_df.mean(axis=1)
    avg_timestamps.to_csv(output_directory + "GPIO2_OE_Tracking_Times.csv", index=None, header=True)

# load tracking data
    source_list = ['nose', 'midpoint', 'baseTail', 'tipTail', 'leftDoor', 'rightDoor', 'startDoor', 'leftSpout',
                   'rightSpout', 'startSpout']  # Change these if you selected different sources to track
    source_number = 0
    tracking_data = pd.DataFrame()

    for tracking_file in tracking_files:
        tracking_array = np.load(tracking_file)
        tracking_positions = np.array([struct.unpack('4f', d) for d in tracking_array])  # convert tracking data from datatype=Uint8 to x,y,width,height data
        tracking_df = pd.DataFrame(tracking_positions)
        tracking_xy = tracking_df.iloc[:, 0:2]

        if len(tracking_xy) != len(avg_timestamps):
            print("ERROR: Dataframes are different lengths for " + tracking_file)
            continue

        source_name = source_list[source_number]
        column_names = [source_name + '_x', source_name + '_y']
        tracking_xy.columns = column_names      # label the columns
        source_number += 1

        RoundTime = round(avg_timestamps, 5)  # change the number of decimal points for rounding

        tracking_x = tracking_xy.iloc[:, 0:1]
        tracking_y = tracking_xy.iloc[:, 1:2]


# ============================================= DOWNSAMPLE THE TRACKING DATA =====================================================

        downsample_x_data = []
        downsample_y_data = []
        downsample_trialtime = []
        downsample_tottime = []
        downsample_index = []
        # trial_start_count = []

        if downsample == 0.1:
            downsample_ms = 100
        elif downsample == 0.05:
            downsample_ms = 50

        i = 0
        time_start = 0
        index_end = len(RoundTime) - 2  # why subtract 2?
        time_end = RoundTime[index_end] * 1000
        for start_i_ms in range(time_start, int(time_end), downsample_ms):
            start_i = start_i_ms / 1000
            end_i = start_i + downsample

            timezone = np.where((RoundTime >= (start_i)) & (RoundTime < (end_i)))[0]

            if timezone.size == 0:
                print('empty')
                # zero = 0

            elif timezone.size > 0:
                tempdata_x = tracking_x.loc[timezone]       # select the tracking data within the 100ms time bin
                tempdata_x = tempdata_x.values.tolist()
                tempdata_x = list(itertools.chain(*tempdata_x))     # flatten the list within the list to use stats.mean

                tempdata_y = tracking_y.loc[timezone]
                tempdata_y = tempdata_y.values.tolist()
                tempdata_y = list(itertools.chain(*tempdata_y))

                average_tempdata_x = statistics.mean(tempdata_x)        # downsample tracking data by averaging
                average_tempdata_y = statistics.mean(tempdata_y)

                downsample_x_data.append(average_tempdata_x)       # append downsampled data to list
                downsample_y_data.append(average_tempdata_y)
                downsample_trialtime.append(start_i)
                downsample_index.append(i)
                downsample_tottime.append(start_i)
                # trial_start_count.append(this_start)

            i += 1
            # print(downsample_tottime)
        total_time = downsample_tottime

        tracking_data[column_names[0]] = downsample_x_data      # add the downsampled data from each source to the df by declaring the list as a new column
        tracking_data[column_names[1]] = downsample_y_data

    tracking_data.insert(0, 'mouse', mouse)     # insert the mouse/trial information at the beginning of the df
    tracking_data.insert(1, 'test', test)
    tracking_data.insert(2, 'day', day)
    tracking_data.insert(3, 'trial_index', downsample_index)
    tracking_data.insert(4, 'total_time', total_time)

    #tracking_data.to_csv(output_directory + "test.csv", index=None, header=True)

    return tracking_data


    #%%
    # source_list = ['nose', 'midpoint', 'baseTail', 'tipTail', 'leftDoor', 'rightDoor', 'startDoor', 'leftSpout',
    #                'rightSpout', 'startSpout']  # Change these if you selected different sources to track
    # source_number = 0
    # tracking_data = []
    # for tracking_file, timestamp_file in zip(tracking_files, timestamp_files):
    #     tracking_array = np.load(tracking_file)
    #     tracking_positions = np.array([struct.unpack('4f', d) for d in tracking_array])     # convert tracking data from datatype=Uint8 to x,y,width,height data
    #     tracking_df = pd.DataFrame(tracking_positions)
    #     # x, y, w, h = tracking_positions[:, 0], tracking_positions[:, 1], tracking_positions[:, 2], tracking_positions[:, 3]
    #     tracking_xy = tracking_df.iloc[:, 0:2]
    #     print(tracking_file, timestamp_file)
    #
    #     timestamp_data = np.load(timestamp_file)
    #     timestamps_seconds = timestamp_data / sample_rate(fpath, folder)
    #     timestamps_seconds = timestamps_seconds - timestamps_seconds[0]
    #     timestamps_df = pd.DataFrame(timestamps_seconds)
    #
    #     if len(tracking_xy) != len(timestamps_df):
    #         print("ERROR: Dataframes are different lengths for " + tracking_file + " and " + timestamp_file)
    #         continue
    #
    #     tracking_timestamps = pd.concat([tracking_xy, timestamps_df], axis=1, ignore_index=True)
    #     source_name = source_list[source_number]
    #     column_names = [source_name+'_x', source_name+'_y', 'timestamp']
    #     tracking_timestamps.columns = column_names
    #
    #     RoundTime = round(tracking_timestamps['timestamp'], 5)  # change the number of decimal points for rounding
    #
    #     tracking_temp = pd.DataFrame()
    #     tracking_temp.insert(0, 'Mouse', mouse)
    #     tracking_temp.insert(1, 'Test', test)
    #     tracking_temp.insert(2, 'Day', day)
    #     tracking_temp.insert(3, column_names[0], tracking_timestamps[column_names[0]])
    #     tracking_temp.insert(4, column_names[1], tracking_timestamps[column_names[1]])
    #     tracking_temp.insert(5, 'TimeStamp', RoundTime)
    #
    #     tracking_times = tracking_temp.iloc[:, 5]
    #     tracking_x = tracking_temp.iloc[:, 3:4]
    #     tracking_y = tracking_temp.iloc[:, 4:5]
    #
    #     new_data = pd.DataFrame()
    #     downsample_x_data = []
    #     downsample_y_data = []
    #     downsample_trialtime = []
    #     downsample_tottime = []
    #     downsample_index = []
    #     #    trial_start_count = []
    #
    #     if downsample == 0.1:
    #         downsample_ms = 100
    #     elif downsample == 0.05:
    #         downsample_ms = 50
    #
    #     i = 0
    #     time_start = 0
    #     index_end = len(tracking_times) - 2     # why subtract 2?
    #     time_end = tracking_times[index_end] * 1000
    #     for start_i_ms in range(time_start, int(time_end), downsample_ms):
    #         start_i = start_i_ms / 1000
    #         end_i = start_i + downsample
    #
    #         timezone = np.where((tracking_times >= (start_i)) & (tracking_times < (end_i)))[0]
    #
    #         if timezone.size == 0:
    #             # print('empty')
    #             zero = 0
    #
    #         elif timezone.size > 0:
    #             tempdata_x = (tracking_x.loc[timezone]).to_numpy()
    #             tempdata_y = (tracking_y.loc[timezone]).to_numpy()
    #
    #             average_tempdata_x = tempdata_x.mean(axis=0)
    #             average_tempdata_y = tempdata_y.mean(axis=0)
    #
    #
    #             downsample_x_data.append(average_tempdata_x)
    #             downsample_y_data.append(average_tempdata_y)
    #             downsample_trialtime.append(start_i)
    #             downsample_index.append(i)
    #             downsample_tottime.append(start_i)
    #             # trial_start_count.append(this_start)
    #         i += 1
    #     # print(downsample_tottime)
    #     total_time = downsample_tottime
    #
    #
    #
    #     # new_data.insert(0, 'trial_index', downsample_index)
    #     # # new_data.insert(1, 'trial_time', downsample_trialtime)
    #     # new_data.insert(1, 'total_time', total_time)
    #     # new_data.insert(2, column_names[0], downsample_x_data)
    #     # new_data.insert(3, column_names[1], downsample_y_data)
    #     # new_data.insert(4, 'test', test)
    #     # new_data.insert(5, 'day', day)
    #     # new_data.insert(6, 'mouse', mouse)
    #     # #    new_data.insert(8, 'trial_start', trial_start_count)
    #
    #     tracking_data.append(new_data)
    #     source_number += 1
    #
    #     # tracking_data.append(tracking_timestamps)
    #
    # tracking_data_df = pd.concat(tracking_data, axis=1)
    # print(tracking_data_df)

    # tempdata1 = tracking_data_df
    #
    # if main_or_meta == 'main':
    #     return tempdata1

#%%
        # tempdata1 = pd.DataFrame(tracking)
        # tempdata2 = pd.DataFrame(extrainfo)
        #
        # tempdata1['t_delay'] = tempdata1['t_delay'].astype(str) + ' sec'
        #
        # for trial_i in tempdata1['trial'].unique():
        #     correct_status_loc = np.where((tempdata1['trial'] == trial_i) & (tempdata1['event'] == 'choice_selection'))[0]
        #     if correct_status_loc.size == 0:
        #         continue
        #     print(correct_status_loc[0])
        #     correct_status = tempdata1['correct_status'][correct_status_loc[0]]
        #     print(correct_status)
        #     trial_indexes = np.where((tempdata1['trial'] == trial_i))[0]
        #     for index in trial_indexes:
        #         tempdata1['correct_status'][index] = correct_status
        #
        # tempdata1['phase_broad'] = ""
        #
        # for row_i in range(len(tempdata1['tmaze_phase'])):
        #     row = tempdata1['tmaze_phase'][row_i]
        #     if 'ITI' in row:
        #         tempdata1['phase_broad'][row_i] = 'ITI'
        #     elif 'sample' in row:
        #         tempdata1['phase_broad'][row_i] = 'sample'
        #     elif 'delay' in row:
        #         tempdata1['phase_broad'][row_i] = 'delay'
        #     elif 'choice' in row:
        #         tempdata1['phase_broad'][row_i] = 'choice'
        #     else:
        #         tempdata1['phase_broad'][row_i] = 'error'
        #     # print(row)
        #
        # tempdata1.rename(columns={"tmaze_phase": "phase_specific"})
        #
        # if main_or_meta == 'main':
        #     return tempdata1
        #
        # if main_or_meta == 'meta':
        #     return tempdata2


# %% ========================== DO NOT CHANGE THIS PART =======================================================

"""
This is where you can add to the mouse groups but be careful about changing anything else!
"""
if mouse_group == 'all':
    mouse_list = []
elif mouse_group == 'test':
    mouse_list = ['spinfulltest']

else:
    print('Mouse group is not valid. The code will now quit, please try again')
    sys.exit()

filename = mouse_group + add_to_title

fpath = input_directory

title = filename

# This is the start and end times of the window to look for the max value -- all trials start at 0s and the stim is at 10s

trackingdata_all = pd.DataFrame()
this_trackingdata = pd.DataFrame()

for m in range(len(mouse_list)):
    mouse = mouse_list[m]

    for test in test_list:

        for day in day_list:

            file = str(mouse) + '_' + str(test) + '_' + str(day)

            print(file)

            this_trackingdata = load_tracking(mouse=mouse, test=test, day=day, fpath=fpath, file=file,
                                             main_or_meta='main')
            if type(this_trackingdata) == str:
                File_file = ([mouse, mouse_group, test, day, file, 'not here', 'NA'])
                File_List = np.vstack((File_List, File_file))
                np.savetxt(output_directory + "TMazeOpenEphys_Tracking_" + mouse_group + add_to_title + ".csv",
                           File_List, delimiter=",", fmt='%s')

            else:
                length = len(this_trackingdata)
                File_file = ([mouse, mouse_group, test, day, file, 'here', length])
                File_List = np.vstack((File_List, File_file))
                this_trackingdata.to_csv(output_directory + "trackingdataNEW_" + file + add_to_title + ".csv", index=None,
                                        header=True)
                np.savetxt(output_directory + "TMazeOpenEphys_NEWTracking_" + mouse_group + ".csv", File_List,
                           delimiter=",", fmt='%s')

                # this_commentdata = load_comments(mouse=mouse, test=test, day=day, fpath=fpath, file=file,
                #                                  main_or_meta='meta')
                # this_commentdata.to_csv(output_directory + "tracking_metadata_" + file + add_to_title + ".csv",
                #                         index=None, header=True)