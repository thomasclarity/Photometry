#%%
# Create excel sheets that summarize the data from the Find Peaks analysis

import os
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import style
import numpy as np
#from sklearn.linear_model import LinearRegression
#from scipy.optimize import curve_fit
from matplotlib import rcParams
import glob
import scipy
from scipy.signal import find_peaks, peak_prominences, peak_widths
#from scipy import stats
#from statistics import mean
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import tkinter as tk
from tkinter.filedialog import askdirectory
from tkinter.filedialog import askopenfilename

#import matplotlib.mlab as mlab
#from scipy import optimize, polyfit
#from scipy.optimize import minimize
#from scipy.optimize import fsolve

# import graph style
# style.use('ggplot')
# rcParams.update({'figure.autolayout': True})
rcParams.update({'figure.max_open_warning': 0})
#rcParams.update({'font.size':34})

# prevents tkinter root window from popping up with the 'askdirectory' window
root = tk.Tk()
root.attributes('-topmost', True)
root.withdraw()

# set directories for reading folders
read_fold = askdirectory(title = 'Select Input Folder that contains Peak Summary and Scatterplot Stats (Ex. m189_delays1_07_09_19 pDFoFG peak summary stats)') # shows dialog box and returns the path
if read_fold:
    print("Input Folder:", read_fold)
else:
    print("Please select an input directory")
    quit()

# set directories for writing folders
write_fold_fig = askdirectory(title='Select Figure Output Folder')
if write_fold_fig:
    print("Figure Output Folder:", write_fold_fig)
else:
    print("Please select an output directory")
    quit()

write_fold_data = askdirectory(title='Select Excel Output Folder')
if write_fold_data:
    print("Excel Output Folder:", write_fold_data)
else:
    print("Please select an output directory")
    quit()

#%%
# SUMMARY STATS
# create empty lists for each data sheet
tmaze_pDFoFG = []
tmaze_pDFoFR = []
tmaze_pDCoCG = []
tmaze_pDCoCR = []
plasticity_pDFoFG = []
plasticity_pDFoFR = []
plasticity_pDCoCG = []
plasticity_pDCoCR = []


# call all Find Peaks Summary Stats Files in a folder and append selected data into dictionaries
for file in glob.glob(read_fold + '/m*peak summary stats.xlsx'):
    file_name = os.path.basename(file)
    input_file = pd.read_excel(os.path.join(read_fold, file_name))
    # select time period to analyze by adjusting first range. Note, iloc is EXCLUSIVE of the high end of the range
    input_file_sel = input_file.iloc[0:1, 1:14].reset_index(drop=True)

    print(file_name)

    tmaze = ['delays', 'test', 'train']
    plasticity = ['base', 'IO', 'Plasticity']

    if any (i in file_name for i in tmaze):
        if 'pDFoFG' in file_name:
            tmaze_pDFoFG.append(input_file_sel)
        elif 'pDFoFR' in file_name:
            tmaze_pDFoFR.append(input_file_sel)
        elif 'pDCoCG' in file_name:
            tmaze_pDCoCG.append(input_file_sel)
        elif 'pDCoCR' in file_name:
            tmaze_pDCoCR.append(input_file_sel)
        else:
            print("Error in ", file_name)
            quit()

    elif any (i in file_name for i in plasticity):
        if 'pDFoFG' in file_name:
            plasticity_pDFoFG.append(input_file_sel)
        elif 'pDFoFR' in file_name:
            plasticity_pDFoFR.append(input_file_sel)
        elif 'pDCoCG' in file_name:
            plasticity_pDCoCG.append(input_file_sel)
        elif 'pDCoCR' in file_name:
            plasticity_pDCoCR.append(input_file_sel)
        else:
            print("Error in", file_name)
            quit()

    else:
        print("Error in", file_name)
        quit()


#%%
# try to concatenate the dataframes within the dictionaries and write to excel sheet
try:
    tmaze_pDFoFG_df = pd.concat(tmaze_pDFoFG, ignore_index=True)
    tmaze_pDFoFG_df.to_excel(os.path.join(write_fold_data, 'tmaze pDFoFG peak summary stats.xlsx'), sheet_name='tmaze_pDFoFG', na_rep = "NaN")
    print('tmaze pDFoFG summary data successfully analyzed')
except ValueError:
    print('No tmaze pDFoFG summary data to analyze')

try:
    tmaze_pDFoFR_df = pd.concat(tmaze_pDFoFR, ignore_index=True)
    tmaze_pDFoFR_df.to_excel(os.path.join(write_fold_data, 'tmaze pDFoFR peak summary stats.xlsx'), sheet_name = 'tmaze_pDFoFR', na_rep = "NaN")
    print('tmaze pDFoFR summary data successfully analyzed')
except ValueError:
    print('No tmaze pDFoFR summary data to analyze')

try:
    tmaze_pDCoCG_df = pd.concat(tmaze_pDCoCG, ignore_index=True)
    tmaze_pDCoCG_df.to_excel(os.path.join(write_fold_data, 'tmaze pDCoCG peak summary stats.xlsx'), sheet_name = 'tmaze_pDCoCG', na_rep = "NaN")
    print('tmaze pDCoCG summary data successfully analyzed')
except ValueError:
    print('No tmaze pDCoCG summary data to analyze')

try:
    tmaze_pDCoCR_df = pd.concat(tmaze_pDCoCR, ignore_index=True)
    tmaze_pDCoCR_df.to_excel(os.path.join(write_fold_data, 'tmaze pDCoCR peak summary stats.xlsx'), sheet_name = 'tmaze_pDCoCR', na_rep = "NaN")
    print('tmaze pDCoCR summary data successfully analyzed')
except ValueError:
    print('No tmaze pDCoCR summary data to analyze')

try:
    plasticity_pDFoFG_df = pd.concat(plasticity_pDFoFG, ignore_index=True)
    plasticity_pDFoFG_df.to_excel(os.path.join(write_fold_data, 'plasticity pDFoFG peak summary stats.xlsx'), sheet_name = 'plasticity_pDFoFG', na_rep = "NaN")
    print('plasticity pDFoFG summary data successfully analyzed')
except ValueError:
    print('No plasticity pDFoFG summary data to analyze')

try:
    plasticity_pDFoFR_df = pd.concat(plasticity_pDFoFR, ignore_index=True)
    plasticity_pDFoFR_df.to_excel(os.path.join(write_fold_data, 'plasticity pDFoFR peak summary stats.xlsx'), sheet_name = 'plasticity_pDFoFR', na_rep = "NaN")
    print('plasticity pDFoFR summary data successfully analyzed')
except ValueError:
    print('No plasticity pDFoFR summary data to analyze')

try:
    plasticity_pDCoCG_df = pd.concat(plasticity_pDCoCG, ignore_index=True)
    plasticity_pDCoCG_df.to_excel(os.path.join(write_fold_data, 'plasticity pDCoCG peak summary stats.xlsx'), sheet_name = 'plasticity_pDCoCG', na_rep = "NaN")
    print('plasticity pDCoCG summary data successfully analyzed')
except ValueError:
    print('No plasticity pDCoCG summary data to analyze')

try:
    plasticity_pDCoCR_df = pd.concat(plasticity_pDCoCR, ignore_index=True)
    plasticity_pDCoCR_df.to_excel(os.path.join(write_fold_data, 'plasticity pDCoCR peak summary stats.xlsx'), sheet_name = 'plasticity_pDCoCR', na_rep = "NaN")
    print('plasticity pDCoCR summary data successfully analyzed')
except ValueError:
    print('No plasticity pDCoCR summary data to analyze')


#%%
# SCATTERPLOT STATS
# create empty lists for each data sheet
tmaze_pDFoFG_scatter = []
tmaze_pDFoFR_scatter = []
tmaze_pDCoCG_scatter = []
tmaze_pDCoCR_scatter = []
plasticity_pDFoFG_scatter = []
plasticity_pDFoFR_scatter = []
plasticity_pDCoCG_scatter = []
plasticity_pDCoCR_scatter = []


# call all Find Peaks Scatterplot Stats Files in a folder and append selected data into dictionaries
for file in glob.glob(read_fold + '/m*scatterplot stats.xlsx'):
    file_name = os.path.basename(file)
    input_file = pd.read_excel(os.path.join(read_fold, file_name))
    # select time period to analyze by adjusting first range. Note, iloc is EXCLUSIVE of the high end of the range
    input_file_sel = input_file.iloc[0:4, 1:].reset_index(drop=True)

    print(file_name)

    tmaze = ['delays', 'test', 'train']
    plasticity = ['base', 'IO', 'Plasticity']

    if any (i in file_name for i in tmaze):
        if 'pDFoFG' in file_name:
            tmaze_pDFoFG_scatter.append(input_file_sel)
        elif 'pDFoFR' in file_name:
            tmaze_pDFoFR_scatter.append(input_file_sel)
        elif 'pDCoCG' in file_name:
            tmaze_pDCoCG_scatter.append(input_file_sel)
        elif 'pDCoCR' in file_name:
            tmaze_pDCoCR_scatter.append(input_file_sel)
        else:
            print("Error in ", file_name)
            quit()

    elif any (i in file_name for i in plasticity):
        if 'pDFoFG' in file_name:
            plasticity_pDFoFG_scatter.append(input_file_sel)
        elif 'pDFoFR' in file_name:
            plasticity_pDFoFR_scatter.append(input_file_sel)
        elif 'pDCoCG' in file_name:
            plasticity_pDCoCG_scatter.append(input_file_sel)
        elif 'pDCoCR' in file_name:
            plasticity_pDCoCR_scatter.append(input_file_sel)
        else:
            print("Error in", file_name)
            quit()

    else:
        print("Error in", file_name)
        quit()


#%%
# try to concatenate the dataframes within the dictionaries and write to excel sheet

try:
    tmaze_pDFoFG_scatter_df = pd.concat(tmaze_pDFoFG_scatter, ignore_index=True)
    tmaze_pDFoFG_scatter_df.to_excel(os.path.join(write_fold_data, 'tmaze pDFoFG scatterplot summary stats.xlsx'), sheet_name='tmaze_pDFoFG_scatterplot', na_rep = "NaN")
    print('tmaze pDFoFG scatterplot data successfully analyzed')
except ValueError:
    print('No tmaze pDFoFG scatterplot data to analyze')

try:
    tmaze_pDFoFR_scatter_df = pd.concat(tmaze_pDFoFR_scatter, ignore_index=True)
    tmaze_pDFoFR_scatter_df.to_excel(os.path.join(write_fold_data, 'tmaze pDFoFR scatterplot summary stats.xlsx'), sheet_name = 'tmaze_pDFoFR_scatterplot', na_rep = "NaN")
    print('tmaze pDFoFR scatterplot data successfully analyzed')
except ValueError:
    print('No tmaze pDFoFR scatterplot data to analyze')

try:
    tmaze_pDCoCG_scatter_df = pd.concat(tmaze_pDCoCG_scatter, ignore_index=True)
    tmaze_pDCoCG_scatter_df.to_excel(os.path.join(write_fold_data, 'tmaze pDCoCG scatterplot summary stats.xlsx'), sheet_name = 'tmaze_pDCoCG_scatterplot', na_rep = "NaN")
    print('tmaze pDCoCG scatterplot data successfully analyzed')
except ValueError:
    print('No tmaze pDCoCG scatterplot data to analyze')

try:
    tmaze_pDCoCR_scatter_df = pd.concat(tmaze_pDCoCR_scatter, ignore_index=True)
    tmaze_pDCoCR_scatter_df.to_excel(os.path.join(write_fold_data, 'tmaze pDCoCR scatterplot summary stats.xlsx'), sheet_name = 'tmaze_pDCoCR_scatterplot', na_rep = "NaN")
    print('tmaze pDCoCR scatterplot data successfully analyzed')
except ValueError:
    print('No tmaze pDCoCR scatterplot data to analyze')

try:
    plasticity_pDFoFG_scatter_df = pd.concat(plasticity_pDFoFG_scatter, ignore_index=True)
    plasticity_pDFoFG_scatter_df.to_excel(os.path.join(write_fold_data, 'plasticity pDFoFG scatterplot summary stats.xlsx'), sheet_name = 'plasticity_pDFoFG_scatterplot', na_rep = "NaN")
    print('plasticity pDFoFG scatterplot data successfully analyzed')
except ValueError:
    print('No plasticity pDFoFG scatterplot data to analyze')

try:
    plasticity_pDFoFR_scatter_df = pd.concat(plasticity_pDFoFR_scatter, ignore_index=True)
    plasticity_pDFoFR_scatter_df.to_excel(os.path.join(write_fold_data, 'plasticity pDFoFR scatterplot summary stats.xlsx'), sheet_name = 'plasticity_pDFoFR_scatterplot', na_rep = "NaN")
    print('plasticity pDFoFR scatterplot data successfully analyzed')
except ValueError:
    print('No plasticity pDFoFR scatterplot data to analyze')

try:
    plasticity_pDCoCG_scatter_df = pd.concat(plasticity_pDCoCG_scatter, ignore_index=True)
    plasticity_pDCoCG_scatter_df.to_excel(os.path.join(write_fold_data, 'plasticity pDCoCG scatterplot summary stats.xlsx'), sheet_name = 'plasticity_pDCoCG_scatterplot', na_rep = "NaN")
    print('plasticity pDCoCG scatterplot data successfully analyzed')
except ValueError:
    print('No plasticity pDCoCG scatterplot data to analyze')

try:
    plasticity_pDCoCR_scatter_df = pd.concat(plasticity_pDCoCR_scatter, ignore_index=True)
    plasticity_pDCoCR_scatter_df.to_excel(os.path.join(write_fold_data, 'plasticity pDCoCR scatterplot summary stats.xlsx'), sheet_name = 'plasticity_pDCoCR_scatterplot', na_rep = "NaN")
    print('plasticity pDCoCR scatterplot data successfully analyzed')
except ValueError:
    print('No plasticity pDCoCR scatterplot data to analyze')


#%%
# create dataframes to prevent duplications of data during graphing and stats


# select input file
read_file = askopenfilename(title = 'Select a Plasticity Summary Stats Input File', filetypes = [("Excel file", "*.xlsx")])
if read_file:
    data = pd.read_excel(read_file)
    print("Input File:", read_file)
else:
    print("Please select an input file")
    quit()

# df that contains all baseline data
baseline = []

# baseline df that collapses by day and parses by IO/Plast and week
base_IO_w0 = []
base_plast_w1 = []
base_plast_w2 = []
base_plast_w3 = []
base_plast_w4 = []

for mouse in data["mouse_id"].unique():
    per_mouse = data[data["mouse_id"] == mouse]
    #print(per_mouse.to_string())
    base_per_mouse = per_mouse[per_mouse["base_or_stim"] == "baseline"]
    base_IO_per_mouse = base_per_mouse[base_per_mouse["IO_or_plast"] == "IO"]
    base_plast_per_mouse = base_per_mouse[base_per_mouse["IO_or_plast"] == "plasticity"]
    base_IO_per_mouse_w0 = base_IO_per_mouse[base_IO_per_mouse["week"] == 0]
    base_plast_per_mouse_w1 = base_plast_per_mouse[base_plast_per_mouse["week"] == 1]
    base_plast_per_mouse_w2 = base_plast_per_mouse[base_plast_per_mouse["week"] == 2]
    base_plast_per_mouse_w3 = base_plast_per_mouse[base_plast_per_mouse["week"] == 3]
    base_plast_per_mouse_w4 = base_plast_per_mouse[base_plast_per_mouse["week"] == 4]

    base_IO_per_mouse_w0_info = base_IO_per_mouse_w0.iloc[:1, 1:7]
    base_plast_per_mouse_w1_info = base_plast_per_mouse_w1.iloc[:1, 1:7]
    base_plast_per_mouse_w2_info = base_plast_per_mouse_w2.iloc[:1, 1:7]
    base_plast_per_mouse_w3_info = base_plast_per_mouse_w3.iloc[:1, 1:7]
    base_plast_per_mouse_w4_info = base_plast_per_mouse_w4.iloc[:1, 1:7]

    base_IO_w0_sum_peakCount = [float(base_IO_per_mouse_w0["count_peak"].sum())]
    base_IO_per_mouse_w0_info["count_peak"] = base_IO_w0_sum_peakCount
    base_IO_w0_mean_peakFreq = [float(base_IO_per_mouse_w0["freq_peak"].mean())]
    base_IO_per_mouse_w0_info["freq_peak"] = base_IO_w0_mean_peakFreq
    base_IO_w0_mean_peakYval = [float(base_IO_per_mouse_w0["mean_peak_yval"].mean())]
    base_IO_per_mouse_w0_info["mean_peak_yval"] = base_IO_w0_mean_peakYval
    base_IO_w0_mean_peakProm = [float(base_IO_per_mouse_w0["mean_peak_prom"].mean())]
    base_IO_per_mouse_w0_info["mean_peak_prom"] = base_IO_w0_mean_peakProm
    base_IO_w0_mean_promSTD = [float(base_IO_per_mouse_w0["std_peak_prom"].mean())]
    base_IO_per_mouse_w0_info["std_peak_prom"] = base_IO_w0_mean_promSTD
    base_IO_w0_mean_peakHwidths = [float(base_IO_per_mouse_w0["mean_peak_hwidths"].mean())]
    base_IO_per_mouse_w0_info["mean_peak_hwidths"] = base_IO_w0_mean_peakHwidths

    base_plast_w1_sum_peakCount = [float(base_plast_per_mouse_w1["count_peak"].sum())]
    base_plast_per_mouse_w1_info["count_peak"] = base_plast_w1_sum_peakCount
    base_plast_w1_mean_peakFreq = [float(base_plast_per_mouse_w1["freq_peak"].mean())]
    base_plast_per_mouse_w1_info["freq_peak"] = base_plast_w1_mean_peakFreq
    base_plast_w1_mean_peakYval = [float(base_plast_per_mouse_w1["mean_peak_yval"].mean())]
    base_plast_per_mouse_w1_info["mean_peak_yval"] = base_plast_w1_mean_peakYval
    base_plast_w1_mean_peakProm = [float(base_plast_per_mouse_w1["mean_peak_prom"].mean())]
    base_plast_per_mouse_w1_info["mean_peak_prom"] = base_plast_w1_mean_peakProm
    base_plast_w1_mean_promSTD = [float(base_plast_per_mouse_w1["std_peak_prom"].mean())]
    base_plast_per_mouse_w1_info["std_peak_prom"] = base_plast_w1_mean_promSTD
    base_plast_w1_mean_peakHwidths = [float(base_plast_per_mouse_w1["mean_peak_hwidths"].mean())]
    base_plast_per_mouse_w1_info["mean_peak_hwidths"] = base_plast_w1_mean_peakHwidths

    base_plast_w2_sum_peakCount = [float(base_plast_per_mouse_w2["count_peak"].sum())]
    base_plast_per_mouse_w2_info["count_peak"] = base_plast_w2_sum_peakCount
    base_plast_w2_mean_peakFreq = [float(base_plast_per_mouse_w2["freq_peak"].mean())]
    base_plast_per_mouse_w2_info["freq_peak"] = base_plast_w2_mean_peakFreq
    base_plast_w2_mean_peakYval = [float(base_plast_per_mouse_w2["mean_peak_yval"].mean())]
    base_plast_per_mouse_w2_info["mean_peak_yval"] = base_plast_w2_mean_peakYval
    base_plast_w2_mean_peakProm = [float(base_plast_per_mouse_w2["mean_peak_prom"].mean())]
    base_plast_per_mouse_w2_info["mean_peak_prom"] = base_plast_w2_mean_peakProm
    base_plast_w2_mean_promSTD = [float(base_plast_per_mouse_w2["std_peak_prom"].mean())]
    base_plast_per_mouse_w2_info["std_peak_prom"] = base_plast_w2_mean_promSTD
    base_plast_w2_mean_peakHwidths = [float(base_plast_per_mouse_w2["mean_peak_hwidths"].mean())]
    base_plast_per_mouse_w2_info["mean_peak_hwidths"] = base_plast_w2_mean_peakHwidths

    base_plast_w3_sum_peakCount = [float(base_plast_per_mouse_w3["count_peak"].sum())]
    base_plast_per_mouse_w3_info["count_peak"] = base_plast_w3_sum_peakCount
    base_plast_w3_mean_peakFreq = [float(base_plast_per_mouse_w3["freq_peak"].mean())]
    base_plast_per_mouse_w3_info["freq_peak"] = base_plast_w3_mean_peakFreq
    base_plast_w3_mean_peakYval = [float(base_plast_per_mouse_w3["mean_peak_yval"].mean())]
    base_plast_per_mouse_w3_info["mean_peak_yval"] = base_plast_w3_mean_peakYval
    base_plast_w3_mean_peakProm = [float(base_plast_per_mouse_w3["mean_peak_prom"].mean())]
    base_plast_per_mouse_w3_info["mean_peak_prom"] = base_plast_w3_mean_peakProm
    base_plast_w3_mean_promSTD = [float(base_plast_per_mouse_w3["std_peak_prom"].mean())]
    base_plast_per_mouse_w3_info["std_peak_prom"] = base_plast_w3_mean_promSTD
    base_plast_w3_mean_peakHwidths = [float(base_plast_per_mouse_w3["mean_peak_hwidths"].mean())]
    base_plast_per_mouse_w3_info["mean_peak_hwidths"] = base_plast_w3_mean_peakHwidths

    base_plast_w4_sum_peakCount = [float(base_plast_per_mouse_w4["count_peak"].sum())]
    base_plast_per_mouse_w4_info["count_peak"] = base_plast_w4_sum_peakCount
    base_plast_w4_mean_peakFreq = [float(base_plast_per_mouse_w4["freq_peak"].mean())]
    base_plast_per_mouse_w4_info["freq_peak"] = base_plast_w4_mean_peakFreq
    base_plast_w4_mean_peakYval = [float(base_plast_per_mouse_w4["mean_peak_yval"].mean())]
    base_plast_per_mouse_w4_info["mean_peak_yval"] = base_plast_w4_mean_peakYval
    base_plast_w4_mean_peakProm = [float(base_plast_per_mouse_w4["mean_peak_prom"].mean())]
    base_plast_per_mouse_w4_info["mean_peak_prom"] = base_plast_w4_mean_peakProm
    base_plast_w4_mean_promSTD = [float(base_plast_per_mouse_w4["std_peak_prom"].mean())]
    base_plast_per_mouse_w4_info["std_peak_prom"] = base_plast_w4_mean_promSTD
    base_plast_w4_mean_peakHwidths = [float(base_plast_per_mouse_w4["mean_peak_hwidths"].mean())]
    base_plast_per_mouse_w4_info["mean_peak_hwidths"] = base_plast_w4_mean_peakHwidths

    baseline.append(base_per_mouse)
    base_IO_w0.append(base_IO_per_mouse_w0_info)
    base_plast_w1.append(base_plast_per_mouse_w1_info)
    base_plast_w2.append(base_plast_per_mouse_w2_info)
    base_plast_w3.append(base_plast_per_mouse_w3_info)
    base_plast_w4.append(base_plast_per_mouse_w4_info)

baseline = pd.concat(baseline, ignore_index = True)
baseline.to_excel(os.path.join(write_fold_data, 'baseline summary stats.xlsx'),
                                      sheet_name='baseline_summary_stats', na_rep="NaN")    # save all baseline data

base_IO_w0 = pd.concat(base_IO_w0, ignore_index = True)
base_plast_w1 = pd.concat(base_plast_w1, ignore_index = True)
base_plast_w2 = pd.concat(base_plast_w2, ignore_index = True)
base_plast_w3 = pd.concat(base_plast_w3, ignore_index = True)
base_plast_w4 = pd.concat(base_plast_w4, ignore_index = True)

# drop NaN values in dataframes
# base_IO_w0_df = base_IO_w0.dropna()
# base_plast_w1_df = base_plast_w1.dropna()
# base_plast_w2_df = base_plast_w2.dropna()
# base_plast_w3_df = base_plast_w3.dropna()
# base_plast_w4_df = base_plast_w4.dropna()

baseline_weeks = pd.concat([base_IO_w0, base_plast_w1, base_plast_w2, base_plast_w3, base_plast_w4], ignore_index = True)
print(baseline_weeks.to_string())


# stimulation df that collapses by day and parses by IO/Plast and week
stim_IO_w0 = []
stim_plast_w1 = []
stim_plast_w2 = []
stim_plast_w3 = []
stim_plast_w4 = []

for mouse in data["mouse_id"].unique():
    per_mouse = data[data["mouse_id"] == mouse]
    stim_per_mouse = per_mouse[per_mouse["base_or_stim"] == "stimulation"]
    stim_IO_per_mouse = stim_per_mouse[stim_per_mouse["IO_or_plast"] == "IO"]
    stim_plast_per_mouse = stim_per_mouse[stim_per_mouse["IO_or_plast"] == "plasticity"]
    stim_IO_per_mouse_w0 = stim_IO_per_mouse[stim_IO_per_mouse["week"] == 0]
    stim_plast_per_mouse_w1 = stim_plast_per_mouse[stim_plast_per_mouse["week"] == 1]
    stim_plast_per_mouse_w2 = stim_plast_per_mouse[stim_plast_per_mouse["week"] == 2]
    stim_plast_per_mouse_w3 = stim_plast_per_mouse[stim_plast_per_mouse["week"] == 3]
    stim_plast_per_mouse_w4 = stim_plast_per_mouse[stim_plast_per_mouse["week"] == 4]

    stim_IO_per_mouse_w0_info = stim_IO_per_mouse_w0.iloc[:1, 1:7]
    stim_plast_per_mouse_w1_info = stim_plast_per_mouse_w1.iloc[:1, 1:7]
    stim_plast_per_mouse_w2_info = stim_plast_per_mouse_w2.iloc[:1, 1:7]
    stim_plast_per_mouse_w3_info = stim_plast_per_mouse_w3.iloc[:1, 1:7]
    stim_plast_per_mouse_w4_info = stim_plast_per_mouse_w4.iloc[:1, 1:7]

    stim_IO_w0_sum_peakCount = [float(stim_IO_per_mouse_w0["count_peak"].sum())]
    stim_IO_per_mouse_w0_info["count_peak"] = stim_IO_w0_sum_peakCount
    stim_IO_w0_mean_peakFreq = [float(stim_IO_per_mouse_w0["freq_peak"].mean())]
    stim_IO_per_mouse_w0_info["freq_peak"] = stim_IO_w0_mean_peakFreq
    stim_IO_w0_mean_peakYval = [float(stim_IO_per_mouse_w0["mean_peak_yval"].mean())]
    stim_IO_per_mouse_w0_info["mean_peak_yval"] = stim_IO_w0_mean_peakYval
    stim_IO_w0_mean_peakProm = [float(stim_IO_per_mouse_w0["mean_peak_prom"].mean())]
    stim_IO_per_mouse_w0_info["mean_peak_prom"] = stim_IO_w0_mean_peakProm
    stim_IO_w0_mean_promSTD = [float(stim_IO_per_mouse_w0["std_peak_prom"].mean())]
    stim_IO_per_mouse_w0_info["std_peak_prom"] = stim_IO_w0_mean_promSTD
    stim_IO_w0_mean_peakHwidths = [float(stim_IO_per_mouse_w0["mean_peak_hwidths"].mean())]
    stim_IO_per_mouse_w0_info["mean_peak_hwidths"] = stim_IO_w0_mean_peakHwidths

    stim_plast_w1_sum_peakCount = [float(stim_plast_per_mouse_w1["count_peak"].sum())]
    stim_plast_per_mouse_w1_info["count_peak"] = stim_plast_w1_sum_peakCount
    stim_plast_w1_mean_peakFreq = [float(stim_plast_per_mouse_w1["freq_peak"].mean())]
    stim_plast_per_mouse_w1_info["freq_peak"] = stim_plast_w1_mean_peakFreq
    stim_plast_w1_mean_peakYval = [float(stim_plast_per_mouse_w1["mean_peak_yval"].mean())]
    stim_plast_per_mouse_w1_info["mean_peak_yval"] = stim_plast_w1_mean_peakYval
    stim_plast_w1_mean_peakProm = [float(stim_plast_per_mouse_w1["mean_peak_prom"].mean())]
    stim_plast_per_mouse_w1_info["mean_peak_prom"] = stim_plast_w1_mean_peakProm
    stim_plast_w1_mean_promSTD = [float(stim_plast_per_mouse_w1["std_peak_prom"].mean())]
    stim_plast_per_mouse_w1_info["std_peak_prom"] = stim_plast_w1_mean_promSTD
    stim_plast_w1_mean_peakHwidths = [float(stim_plast_per_mouse_w1["mean_peak_hwidths"].mean())]
    stim_plast_per_mouse_w1_info["mean_peak_hwidths"] = stim_plast_w1_mean_peakHwidths

    stim_plast_w2_sum_peakCount = [float(stim_plast_per_mouse_w2["count_peak"].sum())]
    stim_plast_per_mouse_w2_info["count_peak"] = stim_plast_w2_sum_peakCount
    stim_plast_w2_mean_peakFreq = [float(stim_plast_per_mouse_w2["freq_peak"].mean())]
    stim_plast_per_mouse_w2_info["freq_peak"] = stim_plast_w2_mean_peakFreq
    stim_plast_w2_mean_peakYval = [float(stim_plast_per_mouse_w2["mean_peak_yval"].mean())]
    stim_plast_per_mouse_w2_info["mean_peak_yval"] = stim_plast_w2_mean_peakYval
    stim_plast_w2_mean_peakProm = [float(stim_plast_per_mouse_w2["mean_peak_prom"].mean())]
    stim_plast_per_mouse_w2_info["mean_peak_prom"] = stim_plast_w2_mean_peakProm
    stim_plast_w2_mean_promSTD = [float(stim_plast_per_mouse_w2["std_peak_prom"].mean())]
    stim_plast_per_mouse_w2_info["std_peak_prom"] = stim_plast_w2_mean_promSTD
    stim_plast_w2_mean_peakHwidths = [float(stim_plast_per_mouse_w2["mean_peak_hwidths"].mean())]
    stim_plast_per_mouse_w2_info["mean_peak_hwidths"] = stim_plast_w2_mean_peakHwidths

    stim_plast_w3_sum_peakCount = [float(stim_plast_per_mouse_w3["count_peak"].sum())]
    stim_plast_per_mouse_w3_info["count_peak"] = stim_plast_w3_sum_peakCount
    stim_plast_w3_mean_peakFreq = [float(stim_plast_per_mouse_w3["freq_peak"].mean())]
    stim_plast_per_mouse_w3_info["freq_peak"] = stim_plast_w3_mean_peakFreq
    stim_plast_w3_mean_peakYval = [float(stim_plast_per_mouse_w3["mean_peak_yval"].mean())]
    stim_plast_per_mouse_w3_info["mean_peak_yval"] = stim_plast_w3_mean_peakYval
    stim_plast_w3_mean_peakProm = [float(stim_plast_per_mouse_w3["mean_peak_prom"].mean())]
    stim_plast_per_mouse_w3_info["mean_peak_prom"] = stim_plast_w3_mean_peakProm
    stim_plast_w3_mean_promSTD = [float(stim_plast_per_mouse_w3["std_peak_prom"].mean())]
    stim_plast_per_mouse_w3_info["std_peak_prom"] = stim_plast_w3_mean_promSTD
    stim_plast_w3_mean_peakHwidths = [float(stim_plast_per_mouse_w3["mean_peak_hwidths"].mean())]
    stim_plast_per_mouse_w3_info["mean_peak_hwidths"] = stim_plast_w3_mean_peakHwidths

    stim_plast_w4_sum_peakCount = [float(stim_plast_per_mouse_w4["count_peak"].sum())]
    stim_plast_per_mouse_w4_info["count_peak"] = stim_plast_w4_sum_peakCount
    stim_plast_w4_mean_peakFreq = [float(stim_plast_per_mouse_w4["freq_peak"].mean())]
    stim_plast_per_mouse_w4_info["freq_peak"] = stim_plast_w4_mean_peakFreq
    stim_plast_w4_mean_peakYval = [float(stim_plast_per_mouse_w4["mean_peak_yval"].mean())]
    stim_plast_per_mouse_w4_info["mean_peak_yval"] = stim_plast_w4_mean_peakYval
    stim_plast_w4_mean_peakProm = [float(stim_plast_per_mouse_w4["mean_peak_prom"].mean())]
    stim_plast_per_mouse_w4_info["mean_peak_prom"] = stim_plast_w4_mean_peakProm
    stim_plast_w4_mean_promSTD = [float(stim_plast_per_mouse_w4["std_peak_prom"].mean())]
    stim_plast_per_mouse_w4_info["std_peak_prom"] = stim_plast_w4_mean_promSTD
    stim_plast_w4_mean_peakHwidths = [float(stim_plast_per_mouse_w4["mean_peak_hwidths"].mean())]
    stim_plast_per_mouse_w4_info["mean_peak_hwidths"] = stim_plast_w4_mean_peakHwidths

    stim_IO_w0.append(stim_IO_per_mouse_w0_info)
    stim_plast_w1.append(stim_plast_per_mouse_w1_info)
    stim_plast_w2.append(stim_plast_per_mouse_w2_info)
    stim_plast_w3.append(stim_plast_per_mouse_w3_info)
    stim_plast_w4.append(stim_plast_per_mouse_w4_info)

stim_IO_w0 = pd.concat(stim_IO_w0, ignore_index = True)
stim_plast_w1 = pd.concat(stim_plast_w1, ignore_index = True)
stim_plast_w2 = pd.concat(stim_plast_w2, ignore_index = True)
stim_plast_w3 = pd.concat(stim_plast_w3, ignore_index = True)
stim_plast_w4 = pd.concat(stim_plast_w4, ignore_index = True)

# drop NaN values in dataframes
# stim_IO_w0_df = stim_IO_w0.dropna()
# stim_plast_w1_df = stim_plast_w1.dropna()
# stim_plast_w2_df = stim_plast_w2.dropna()
# stim_plast_w3_df = stim_plast_w3.dropna()
# stim_plast_w4_df = stim_plast_w4.dropna()

stimulation_weeks = pd.concat([stim_IO_w0, stim_plast_w1, stim_plast_w2, stim_plast_w3, stim_plast_w4], ignore_index = True)
print(stimulation_weeks.to_string())


# baseline df that collapses by day and week and parses by IO/Plast
base_IO = []
base_plast = []

for mouse in data["mouse_id"].unique():
    per_mouse = data[data["mouse_id"] == mouse]
    base_per_mouse = per_mouse[per_mouse["base_or_stim"] == "baseline"]
    base_IO_per_mouse = base_per_mouse[base_per_mouse["IO_or_plast"] == "IO"]
    base_plast_per_mouse = base_per_mouse[base_per_mouse["IO_or_plast"] == "plasticity"]

    base_IO_per_mouse_info = base_IO_per_mouse.iloc[:1, 1:6]
    base_plast_per_mouse_info = base_plast_per_mouse.iloc[:1, 1:6]

    base_IO_sum_peakCount = [float(base_IO_per_mouse["count_peak"].sum())]
    base_IO_per_mouse_info["count_peak"] = base_IO_sum_peakCount
    base_IO_mean_peakFreq = [float(base_IO_per_mouse["freq_peak"].mean())]
    base_IO_per_mouse_info["freq_peak"] = base_IO_mean_peakFreq
    base_IO_mean_peakYval = [float(base_IO_per_mouse["mean_peak_yval"].mean())]
    base_IO_per_mouse_info["mean_peak_yval"] = base_IO_mean_peakYval
    base_IO_mean_peakProm = [float(base_IO_per_mouse["mean_peak_prom"].mean())]
    base_IO_per_mouse_info["mean_peak_prom"] = base_IO_mean_peakProm
    base_IO_mean_promSTD = [float(base_IO_per_mouse["std_peak_prom"].mean())]
    base_IO_per_mouse_info["std_peak_prom"] = base_IO_mean_promSTD
    base_IO_mean_peakHwidths = [float(base_IO_per_mouse["mean_peak_hwidths"].mean())]
    base_IO_per_mouse_info["mean_peak_hwidths"] = base_IO_mean_peakHwidths

    base_plast_sum_peakCount = [float(base_plast_per_mouse["count_peak"].sum())]
    base_plast_per_mouse_info["count_peak"] = base_plast_sum_peakCount
    base_plast_mean_peakFreq = [float(base_plast_per_mouse["freq_peak"].mean())]
    base_plast_per_mouse_info["freq_peak"] = base_plast_mean_peakFreq
    base_plast_mean_peakYval = [float(base_plast_per_mouse["mean_peak_yval"].mean())]
    base_plast_per_mouse_info["mean_peak_yval"] = base_plast_mean_peakYval
    base_plast_mean_peakProm = [float(base_plast_per_mouse["mean_peak_prom"].mean())]
    base_plast_per_mouse_info["mean_peak_prom"] = base_plast_mean_peakProm
    base_plast_mean_promSTD = [float(base_plast_per_mouse["std_peak_prom"].mean())]
    base_plast_per_mouse_info["std_peak_prom"] = base_plast_mean_promSTD
    base_plast_mean_peakHwidths = [float(base_plast_per_mouse["mean_peak_hwidths"].mean())]
    base_plast_per_mouse_info["mean_peak_hwidths"] = base_plast_mean_peakHwidths

    base_IO.append(base_IO_per_mouse_info)
    base_plast.append(base_plast_per_mouse_info)

base_IO = pd.concat(base_IO, ignore_index=True)
base_plast = pd.concat(base_plast, ignore_index=True)

# drop NaN values in dataframes
# base_IO_df = base_IO.dropna()
# base_plast_df = base_plast.dropna()

baseline_IO_plast = pd.concat([base_IO, base_plast], ignore_index=True)
print(baseline_IO_plast.to_string())


# stimulation df that collapses by day and week and parses by IO/Plast
stim_IO = []
stim_plast = []

for mouse in data["mouse_id"].unique():
    per_mouse = data[data["mouse_id"] == mouse]
    stim_per_mouse = per_mouse[per_mouse["base_or_stim"] == "stimulation"]
    stim_IO_per_mouse = stim_per_mouse[stim_per_mouse["IO_or_plast"] == "IO"]
    stim_plast_per_mouse = stim_per_mouse[stim_per_mouse["IO_or_plast"] == "plasticity"]

    stim_IO_per_mouse_info = stim_IO_per_mouse.iloc[:1, 1:6]
    stim_plast_per_mouse_info = stim_plast_per_mouse.iloc[:1, 1:6]

    stim_IO_sum_peakCount = [float(stim_IO_per_mouse["count_peak"].sum())]
    stim_IO_per_mouse_info["count_peak"] = stim_IO_sum_peakCount
    stim_IO_mean_peakFreq = [float(stim_IO_per_mouse["freq_peak"].mean())]
    stim_IO_per_mouse_info["freq_peak"] = stim_IO_mean_peakFreq
    stim_IO_mean_peakYval = [float(stim_IO_per_mouse["mean_peak_yval"].mean())]
    stim_IO_per_mouse_info["mean_peak_yval"] = stim_IO_mean_peakYval
    stim_IO_mean_peakProm = [float(stim_IO_per_mouse["mean_peak_prom"].mean())]
    stim_IO_per_mouse_info["mean_peak_prom"] = stim_IO_mean_peakProm
    stim_IO_mean_promSTD = [float(stim_IO_per_mouse["std_peak_prom"].mean())]
    stim_IO_per_mouse_info["std_peak_prom"] = stim_IO_mean_promSTD
    stim_IO_mean_peakHwidths = [float(stim_IO_per_mouse["mean_peak_hwidths"].mean())]
    stim_IO_per_mouse_info["mean_peak_hwidths"] = stim_IO_mean_peakHwidths

    stim_plast_sum_peakCount = [float(stim_plast_per_mouse["count_peak"].sum())]
    stim_plast_per_mouse_info["count_peak"] = stim_plast_sum_peakCount
    stim_plast_mean_peakFreq = [float(stim_plast_per_mouse["freq_peak"].mean())]
    stim_plast_per_mouse_info["freq_peak"] = stim_plast_mean_peakFreq
    stim_plast_mean_peakYval = [float(stim_plast_per_mouse["mean_peak_yval"].mean())]
    stim_plast_per_mouse_info["mean_peak_yval"] = stim_plast_mean_peakYval
    stim_plast_mean_peakProm = [float(stim_plast_per_mouse["mean_peak_prom"].mean())]
    stim_plast_per_mouse_info["mean_peak_prom"] = stim_plast_mean_peakProm
    stim_plast_mean_promSTD = [float(stim_plast_per_mouse["std_peak_prom"].mean())]
    stim_plast_per_mouse_info["std_peak_prom"] = stim_plast_mean_promSTD
    stim_plast_mean_peakHwidths = [float(stim_plast_per_mouse["mean_peak_hwidths"].mean())]
    stim_plast_per_mouse_info["mean_peak_hwidths"] = stim_plast_mean_peakHwidths

    stim_IO.append(stim_IO_per_mouse_info)
    stim_plast.append(stim_plast_per_mouse_info)

stim_IO = pd.concat(stim_IO, ignore_index=True)
stim_plast = pd.concat(stim_plast, ignore_index=True)

# drop NaN values in dataframes
# stim_IO_df = stim_IO.dropna()
# stim_plast_df = stim_plast.dropna()

stimulation_IO_plast = pd.concat([stim_IO, stim_plast], ignore_index=True)
print(stimulation_IO_plast.to_string())


# baseline df that collapses by day, week, and IO/Plast
baseline = []

for mouse in data["mouse_id"].unique():
    per_mouse = data[data["mouse_id"] == mouse]
    base_per_mouse = per_mouse[per_mouse["base_or_stim"] == "baseline"]

    base_per_mouse_info = base_per_mouse.iloc[:1, 1:5]

    base_sum_peakCount = [float(base_per_mouse["count_peak"].sum())]
    base_per_mouse_info["count_peak"] = base_sum_peakCount
    base_mean_peakFreq = [float(base_per_mouse["freq_peak"].mean())]
    base_per_mouse_info["freq_peak"] = base_mean_peakFreq
    base_mean_peakYval = [float(base_per_mouse["mean_peak_yval"].mean())]
    base_per_mouse_info["mean_peak_yval"] = base_mean_peakYval
    base_mean_peakProm = [float(base_per_mouse["mean_peak_prom"].mean())]
    base_per_mouse_info["mean_peak_prom"] = base_mean_peakProm
    base_mean_promSTD = [float(base_per_mouse["std_peak_prom"].mean())]
    base_per_mouse_info["std_peak_prom"] = base_mean_promSTD
    base_mean_peakHwidths = [float(base_per_mouse["mean_peak_hwidths"].mean())]
    base_per_mouse_info["mean_peak_hwidths"] = base_mean_peakHwidths

    baseline.append(base_per_mouse_info)

baseline = pd.concat(baseline, ignore_index=True)

# drop NaN values in dataframes
# baseline_df = baseline.dropna()
print(baseline.to_string())


# stimulation df that collapses by day, week, and IO/Plast
stimulation = []

for mouse in data["mouse_id"].unique():
    per_mouse = data[data["mouse_id"] == mouse]
    stim_per_mouse = per_mouse[per_mouse["base_or_stim"] == "stimulation"]

    stim_per_mouse_info = stim_per_mouse.iloc[:1, 1:5]

    stim_sum_peakCount = [float(stim_per_mouse["count_peak"].sum())]
    stim_per_mouse_info["count_peak"] = stim_sum_peakCount
    stim_mean_peakFreq = [float(stim_per_mouse["freq_peak"].mean())]
    stim_per_mouse_info["freq_peak"] = stim_mean_peakFreq
    stim_mean_peakYval = [float(stim_per_mouse["mean_peak_yval"].mean())]
    stim_per_mouse_info["mean_peak_yval"] = stim_mean_peakYval
    stim_mean_peakProm = [float(stim_per_mouse["mean_peak_prom"].mean())]
    stim_per_mouse_info["mean_peak_prom"] = stim_mean_peakProm
    stim_mean_promSTD = [float(stim_per_mouse["std_peak_prom"].mean())]
    stim_per_mouse_info["std_peak_prom"] = stim_mean_promSTD
    stim_mean_peakHwidths = [float(stim_per_mouse["mean_peak_hwidths"].mean())]
    stim_per_mouse_info["mean_peak_hwidths"] = stim_mean_peakHwidths

    stimulation.append(stim_per_mouse_info)

stimulation = pd.concat(stimulation, ignore_index=True)

# drop NaN values in dataframes
# stimulation_df = stimulation.dropna()
print(stimulation.to_string())

# IO/plast df that collapses by day, week, and baseline/stimulation
IO = []
plasticity = []

for mouse in data["mouse_id"].unique():
    per_mouse = data[data["mouse_id"] == mouse]
    IO_per_mouse = per_mouse[per_mouse["IO_or_plast"] == "IO"]
    plast_per_mouse = per_mouse[per_mouse["IO_or_plast"] == "plasticity"]

    IO_per_mouse_info = IO_per_mouse.iloc[:1, [1,2,3,5]]
    plast_per_mouse_info = plast_per_mouse.iloc[:1, [1,2,3,5]]

    IO_sum_peakCount = [float(IO_per_mouse["count_peak"].sum())]
    IO_per_mouse_info["count_peak"] = IO_sum_peakCount
    IO_mean_peakFreq = [float(IO_per_mouse["freq_peak"].mean())]
    IO_per_mouse_info["freq_peak"] = IO_mean_peakFreq
    IO_mean_peakYval = [float(IO_per_mouse["mean_peak_yval"].mean())]
    IO_per_mouse_info["mean_peak_yval"] = IO_mean_peakYval
    IO_mean_peakProm = [float(IO_per_mouse["mean_peak_prom"].mean())]
    IO_per_mouse_info["mean_peak_prom"] = IO_mean_peakProm
    IO_mean_promSTD = [float(IO_per_mouse["std_peak_prom"].mean())]
    IO_per_mouse_info["std_peak_prom"] = IO_mean_promSTD
    IO_mean_peakHwidths = [float(IO_per_mouse["mean_peak_hwidths"].mean())]
    IO_per_mouse_info["mean_peak_hwidths"] = IO_mean_peakHwidths

    plast_sum_peakCount = [float(plast_per_mouse["count_peak"].sum())]
    plast_per_mouse_info["count_peak"] = plast_sum_peakCount
    plast_mean_peakFreq = [float(plast_per_mouse["freq_peak"].mean())]
    plast_per_mouse_info["freq_peak"] = plast_mean_peakFreq
    plast_mean_peakYval = [float(plast_per_mouse["mean_peak_yval"].mean())]
    plast_per_mouse_info["mean_peak_yval"] = plast_mean_peakYval
    plast_mean_peakProm = [float(plast_per_mouse["mean_peak_prom"].mean())]
    plast_per_mouse_info["mean_peak_prom"] = plast_mean_peakProm
    plast_mean_promSTD = [float(plast_per_mouse["std_peak_prom"].mean())]
    plast_per_mouse_info["std_peak_prom"] = plast_mean_promSTD
    plast_mean_peakHwidths = [float(plast_per_mouse["mean_peak_hwidths"].mean())]
    plast_per_mouse_info["mean_peak_hwidths"] = plast_mean_peakHwidths

    IO.append(IO_per_mouse_info)
    plasticity.append(plast_per_mouse_info)

IO = pd.concat(IO, ignore_index=True)
plasticity = pd.concat(plasticity, ignore_index=True)

# drop NaN values in dataframes
# IO_df = IO.dropna()
# plasticity_df = plasticity.dropna()

IO_plasticity = pd.concat([IO, plasticity], ignore_index=True)
print(IO_plasticity.to_string())


# baseline and stimulation dataframe that collapses by day and parses by IO/plast and week
base_stim_weeks = pd.concat([baseline_weeks, stimulation_weeks], ignore_index = True)
print(base_stim_weeks.to_string())


# baseline and stimulation dataframe that collapses by day and week and parses by IO/plast
base_stim_IO_plast = pd.concat([baseline_IO_plast, stimulation_IO_plast], ignore_index = True)
print(base_stim_IO_plast.to_string())


# baseline and stimulation dataframe that collapses by day, week, and IO/plast
base_stim = pd.concat([baseline_df, stimulation_df], ignore_index = True)
print(base_stim.to_string())