
#%%
# Find the peak fluorescence/coefficient values for photon count and linear unmixing files

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

#import matplotlib.mlab as mlab
#from scipy import optimize, polyfit
#from scipy.optimize import minimize
#from scipy.optimize import fsolve

# import graph style
style.use('ggplot')
rcParams.update({'figure.autolayout': True})
rcParams.update({'figure.max_open_warning': 0})
#rcParams.update({'font.size':34})

# prevents tkinter root window from popping up with the 'askdirectory' window
root = tk.Tk()
root.attributes('-topmost', True)
root.withdraw()

# set directories for reading folders
read_fold = askdirectory(title = 'Select Input Folder that contains Photon Count or Lin Unmixing data (Ex. m189_delays1_07_09_19 photon count output)') # shows dialog box and returns the path
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

# select GCaMP or tdTomato data
while True:
    color_inp = input('Are you analyzing GCaMP or tdTomato data? Type "green" or "red"')
    if color_inp in ('green', 'red'):
        print("Initiating data analysis...")
        break

    else:
        print("Input error: you must type 'green' or 'red'")
        continue


#%%

# call all Lin Unmix Output Files in folder, renaming certain titles to have fewer characters
for file in glob.glob(read_fold + '/m*'):

    file_name = os.path.basename(file)
    input_file = pd.read_excel(os.path.join(read_fold, file_name))
    # select time period to analyze by adjusting first range. Note, iloc is EXCLUSIVE of the high end of the range
    input_file_sel = input_file.iloc[:,:].reset_index()

    print(file_name)

    # determine if tmaze data or plasticity data then parse file name

    tmaze = ['delays', 'test', 'train']
    plasticity = ['base', 'IO', 'Plasticity']

    if any (i in file_name for i in tmaze):
        if 'photon count output' in file_name:
            sep = ' photon count output'
            title_name = file_name.rsplit(sep, 1)[0]
            mouse_id = title_name[0:4]
            file_date = title_name[-10:]
            phase_day = title_name.split('_')[1]
            phase = phase_day[:-1]
            week = 'NaN'
            day = float(phase_day[-1:])

        elif 'unmix coeff output' in file_name:
            sep = ' unmix coeff output'
            title_name = file_name.rsplit(sep, 1)[0]
            mouse_id = title_name[0:4]
            file_date = title_name[-10:]
            phase_day = title_name.split('_')[1]
            phase = phase_day[:-1]
            week = 'NaN'
            day = float(phase_day[-1:])

        else:
            print("Error in", file_name)
            quit()

    elif any (i in file_name for i in plasticity):
        if 'photon count output' in file_name:
            sep = ' photon count output'
            title_name = file_name.rsplit(sep, 1)[0]
            mouse_id = title_name[0:4]
            file_date = title_name[-10:]
            phase = title_name.split('_')[1]
            week_day = title_name.split('_')[2]
            week = float(week_day[1:2])
            day = float(week_day[-1:])

        elif 'unmix coeff output' in file_name:
            sep = ' unmix coeff output'
            title_name = file_name.rsplit(sep, 1)[0]
            mouse_id = title_name[0:4]
            file_date = title_name[-10:]
            phase = title_name.split('_')[1]
            week_day = title_name.split('_')[2]
            week = float(week_day[1:2])
            day = float(week_day[-1:])

        else:
            print("Error in", file_name)
            quit()
    else:
        print("Error in", file_name)
        quit()


    # select data column
    if 'photon count output' in file_name:
        if color_inp == 'green':
            data_column_name = 'pDFoFG'
            data_color = 'g'
        else:
            data_column_name = 'pDFoFR'
            data_color = 'r'
        y_axis_label = '% Delta F/F'

    elif 'unmix coeff output' in file_name:
        if color_inp == 'green':
            data_column_name = 'pDCoCG'
            data_color = 'g'
        else:
            data_column_name = 'pDCoCR'
            data_color = 'r'
        y_axis_label = '% Delta C/C'

    data_column = input_file_sel[data_column_name]

    # create dataframe with timestamps of selected data (timestamps_raw = universal time)
    timestamps_raw = input_file_sel.iloc[:,2:3]
    # zero timestamps and convert from ms to seconds
    timestamps_zero_sec = (timestamps_raw - timestamps_raw.iloc[0,0])/1000


#%%
     
    prom_multiplier = 2.91
    width_min = 5
    width_max = 100
    distance_min = 10
    wlen_limit = 160

# ================================= pDCoCG PEAK DETECTION ================================= 

    threshold_prom = prom_multiplier*(data_column.mad()) 
    peak_ind, properties = find_peaks(data_column, prominence = threshold_prom, width = (width_min, width_max), distance = distance_min)
    peak_raw_times = timestamps_raw.iloc[peak_ind].values
    peak_times = timestamps_zero_sec.iloc[peak_ind].values
    peak_times_norm = peak_times / float(timestamps_zero_sec.iloc[-1])
    peak_yval = data_column[peak_ind]
    peak_prom = peak_prominences(data_column, peak_ind, wlen = wlen_limit)[0]
    peak_prom_norm = peak_prom / max(peak_prom)
    contour_min = peak_yval - peak_prom
    hwidths = peak_widths(data_column, peak_ind, rel_height = 0.5, wlen=wlen_limit)
        # hwidths ouputs 4 arrays: (1) the widths for each peak in samples (2) width heights (3&4) interpolated positions
        # of left and right intersection points of a horizontal line at the respective evaluation height
    hwidths_yval = (hwidths[1])
    hwidths_start_ind = (np.round(hwidths[2])).astype(int)
    hwidths_end_ind = (np.round(hwidths[3])).astype(int)
    hwidths_start_times = timestamps_zero_sec.iloc[hwidths_start_ind].values
    hwidths_end_times = timestamps_zero_sec.iloc[hwidths_end_ind].values
    hwidths_durations = hwidths_end_times - hwidths_start_times
    hwidths_durations_norm = hwidths_durations / max(hwidths_durations)
    
    ratio_hwidths_prom = hwidths_durations.flatten() / peak_prom
    ratio_hwidths_prom_norm = ratio_hwidths_prom / max(ratio_hwidths_prom)


    # convert variables to dataframes for excel output

    peak_raw_times_df = pd.DataFrame({'peak_raw_times':peak_raw_times[:,0]})
    peak_ind_df = pd.DataFrame({'peak_ind':peak_ind})
    peak_times_df = pd.DataFrame({'peak_times':peak_times[:,0]})
    peak_times_norm_df = pd.DataFrame({'peak_times_norm':peak_times_norm[:,0]})
    peak_yval_df = peak_yval.to_frame('peak_yval').reset_index(drop = True)
    peak_prom_df = pd.DataFrame({'peak_prom':peak_prom})
    peak_prom_norm_df = pd.DataFrame({'peak_prom_norm':peak_prom_norm})
    hwidths_yval_df = pd.DataFrame({'hwidths_yval':hwidths_yval})
    hwidths_start_times_df = pd.DataFrame({'hwidths_start_times':hwidths_start_times[:,0]})
    hwidths_end_times_df = pd.DataFrame({'hwidths_end_times':hwidths_end_times[:,0]})
    hwidths_durations_df = pd.DataFrame({'hwidths_durations':hwidths_durations[:,0]})
    hwidths_durations_norm_df = pd.DataFrame({'hwidths_durations_norm':hwidths_durations_norm[:,0]})
    ratio_hwidths_prom_df = pd.DataFrame({'ratio_hwidths_prom':ratio_hwidths_prom})
    
    mouse_id_col = []
    file_date_col = []
    phase_col = []
    week_col = []
    day_col = []
    
    for i in peak_ind_df["peak_ind"].unique():
        mouse_id_name = mouse_id
        file_date_name = file_date
        phase_name = phase
        week_name = week
        day_name = day
        mouse_id_col.append(mouse_id_name)
        file_date_col.append(file_date_name)
        phase_col.append(phase_name)
        week_col.append(week_name)
        day_col.append(day_name)
        
    mouse_id_col_df = pd.DataFrame({'mouse_id':mouse_id_col})
    file_date_col_df = pd.DataFrame({'file_date':file_date_col})
    phase_col_df = pd.DataFrame({'phase':phase_col})
    week_col_df = pd.DataFrame({'week':week_col})
    day_col_df = pd.DataFrame({'day':day_col})


    # Variables for Thomas's figures
    peak_time_dif = np.diff(peak_times.flatten(), axis=0)
    peak_prom_trunc = peak_prom[1:]
    prom_peak_time_ratio = peak_prom_trunc / peak_time_dif
    peak_times_trunc = peak_times[1:].flatten()
    hwidths_durations_trunc = hwidths_durations[1:].flatten()
    hwidths_peak_time_ratio = hwidths_durations_trunc / peak_time_dif


    peak_time_dif_df = pd.DataFrame({'peak_time_dif':peak_time_dif})
    peak_prom_trunc_df = pd.DataFrame({'peak_prom_trunc':peak_prom_trunc})
    prom_peak_time_ratio_df = pd.DataFrame({'prom_peak_time_ratio':prom_peak_time_ratio})
    peak_times_trunc_df = pd.DataFrame({'peak_times_trunc':peak_times_trunc})
    hwidths_durations_trunc_df = pd.DataFrame({'hwidths_durations_trunc':hwidths_durations_trunc})
    hwidths_peak_time_ratio_df = pd.DataFrame({'hwidths_peak_time_ratio':hwidths_peak_time_ratio})

    # Add NaN row to beginning of dataframes
    nan = {'peak_time_dif': ["NaN"]}
    nan_df = pd.DataFrame(nan)
    #nan_df['peak_time_dif'] = nan_df['peak_time_dif'].astype(float)
    peak_time_dif_nan_df = pd.concat([nan_df, peak_time_dif_df]).reset_index(drop=True)

    nan = {'peak_prom_trunc' : ["NaN"]}
    nan_df = pd.DataFrame(nan)
    #nan_df['peak_prom_trunc'] = nan_df['peak_prom_trunc'].astype(float)
    peak_prom_trunc_nan_df = pd.concat([nan_df, peak_prom_trunc_df]).reset_index(drop = True)

    nan = {'prom_peak_time_ratio' : ["NaN"]}
    nan_df = pd.DataFrame(nan)
    #nan_df['prom_peak_time_ratio'] = nan_df['prom_peak_time_ratio'].astype(float)
    prom_peak_time_ratio_nan_df = pd.concat([nan_df, prom_peak_time_ratio_df]).reset_index(drop = True)

    nan = {'peak_times_trunc': ["NaN"]}
    nan_df = pd.DataFrame(nan)
    #nan_df['peak_times_trunc'] = nan_df['peak_times_trunc'].astype(float)
    peak_times_trunc_nan_df = pd.concat([nan_df, peak_times_trunc_df]).reset_index(drop = True)

    nan = {'hwidths_durations_trunc': ["NaN"]}
    nan_df = pd.DataFrame(nan)
    #nan_df['hwidths_durations_trunc'] = nan_df['hwidths_durations_trunc'].astype(float)
    hwidths_durations_trunc_nan_df = pd.concat([nan_df, hwidths_durations_trunc_df]).reset_index(drop = True)

    nan = {'hwidths_peak_time_ratio': ["NaN"]}
    nan_df = pd.DataFrame(nan)
    #nan_df['hwidths_peak_time_ratio'] = nan_df['hwidths_peak_time_ratio'].astype(float)
    hwidths_peak_time_ratio_nan_df = pd.concat([nan_df, hwidths_peak_time_ratio_df]).reset_index(drop = True)

    # create second peak_analysis_output data frame that excludes the first row (containing NaN values) to use for graphing
    peak_analysis_output_trunc = pd.concat([mouse_id_col_df[1:].reset_index(drop=True), file_date_col_df[1:].reset_index(drop=True),
                              phase_col_df[1:].reset_index(drop=True), week_col_df[1:].reset_index(drop=True), day_col_df[1:].reset_index(drop=True),
                              peak_raw_times_df[1:].reset_index(drop=True), peak_ind_df[1:].reset_index(drop=True), peak_times_df[1:].reset_index(drop=True),
                              peak_times_norm_df[1:].reset_index(drop=True), peak_yval_df[1:].reset_index(drop=True), peak_prom_df[1:].reset_index(drop=True),
                              peak_prom_norm_df[1:].reset_index(drop=True), hwidths_yval_df[1:].reset_index(drop=True),
                              hwidths_start_times_df[1:].reset_index(drop=True), hwidths_end_times_df[1:].reset_index(drop=True),
                              hwidths_durations_df[1:].reset_index(drop=True), hwidths_durations_norm_df[1:].reset_index(drop=True),
                              ratio_hwidths_prom_df[1:].reset_index(drop=True), peak_time_dif_df, peak_prom_trunc_df, prom_peak_time_ratio_df, peak_times_trunc_df,
                                      hwidths_durations_trunc_df, hwidths_peak_time_ratio_df], axis = 1)


#%%


# ================================= pDCoCG PEAK ANALYSIS EXCEL OUTPUT ================================= 

    peak_analysis_output = pd.concat([mouse_id_col_df, file_date_col_df, phase_col_df, week_col_df, day_col_df,
                              peak_raw_times_df, peak_ind_df, peak_times_df, peak_times_norm_df, 
                              peak_yval_df, peak_prom_df, peak_prom_norm_df,
                              hwidths_yval_df, hwidths_start_times_df, hwidths_end_times_df, 
                              hwidths_durations_df, hwidths_durations_norm_df, 
                              ratio_hwidths_prom_df, peak_time_dif_nan_df, peak_prom_trunc_nan_df, prom_peak_time_ratio_nan_df, peak_times_trunc_nan_df,
                                      hwidths_durations_trunc_nan_df, hwidths_peak_time_ratio_nan_df], axis = 1)
    
    peak_analysis_output.to_excel(os.path.join(write_fold_data, title_name + ' ' + data_column_name + ' peak analysis.xlsx'), sheet_name = title_name)

#%%
    
# ================================= linear regression of scatterplots ================================= 

    scatter_xy = [(peak_times_df, peak_prom_df), (peak_times_df, hwidths_durations_df), (peak_prom_df, hwidths_durations_df), (peak_times_df, ratio_hwidths_prom_df)]
    
    Slope = []
    Intercept = []
    Std_Err = []
    R_Value = []
    P_Value = []
    Mouse_ID = []
    File_date = []
    Phase = []
    Week = []
    Day = []
    base_or_stim = []
    IO_or_plast = []

    
    for x, y in scatter_xy:
        slope, intercept, r_value, p_value, std_err = scipy.stats.mstats.linregress(x, y)
        Slope.append(slope)
        Intercept.append(intercept)
        Std_Err.append(std_err)
        R_Value.append(r_value)
        P_Value.append(p_value)
        Mouse_ID.append(mouse_id)
        File_date.append(file_date)
        Phase.append(phase)
        Week.append(week)
        Day.append(day)

        # create empty list and append to form "baseline" or "stimulation" excel column and IO or Plasticity column
        if any(i in file_name for i in tmaze):
            base_or_stim.append("NaN")
            IO_or_plast.append("NaN")

        elif "base" in file_name:
            if week == 0:
                base_or_stim.append("baseline")
                IO_or_plast.append("IO")
            elif week > 0:
                base_or_stim.append("baseline")
                IO_or_plast.append("plasticity")

        elif "IO" in file_name:
            base_or_stim.append("stimulation")
            IO_or_plast.append("IO")

        elif "Plasticity" in file_name:
            base_or_stim.append("stimulation")
            IO_or_plast.append("plasticity")

    scatter_xy_names = ['peak_times vs peak_prom','peak_times vs hwidths_durations','peak_prom vs hwidths_durations',
                   'peak_times vs ratio_hwidths_prom']


    summary_stats_scatter_plots = pd.DataFrame({'mouse_id':Mouse_ID, 'file_date':File_date,'phase':Phase, 'base_or_stim':base_or_stim, 'IO_or_plast':IO_or_plast, 'week':Week,'day':Day,
                                                'x_axis_vs_y_axis':scatter_xy_names,'slope':Slope,'intercept':Intercept,
                                                'std_err':Std_Err,'r_value':R_Value,'p_value':P_Value})
    
    summary_stats_scatter_plots.to_excel(os.path.join(write_fold_data, title_name + ' ' + data_column_name + ' scatterplot stats.xlsx'), sheet_name = title_name)

#%%

# ================================= pDCoCG PEAK SUMMARY STATISTICS EXCEL OUTPUT =================================

    # create empty list and append to form "baseline" or "stimulation" excel column
    base_or_stim = []
    IO_or_plast = []

    if any (i in file_name for i in tmaze):
        base_or_stim.append("NaN")
        IO_or_plast.append("NaN")

    elif "base" in file_name:
        if week == 0:
            base_or_stim.append("baseline")
            IO_or_plast.append("IO")
        elif week > 0:
            base_or_stim.append("baseline")
            IO_or_plast.append("plasticity")

    elif "IO" in file_name:
        base_or_stim.append("stimulation")
        IO_or_plast.append("IO")

    elif "Plasticity" in file_name:
        base_or_stim.append("stimulation")
        IO_or_plast.append("plasticity")


    peak_ind_df_count = float(peak_ind_df.count())
    peak_ind_df_freq = peak_ind_df_count / float(timestamps_zero_sec.iloc[-1])
    peak_yval_df_mean = float(peak_yval_df.mean())
    peak_prom_df_mean = float(peak_prom_df.mean())
    peak_prom_df_std = float(peak_prom_df.std())
    hwidths_durations_df_mean = float(hwidths_durations_df.mean())
    hwidths_durations_df_std = float(hwidths_durations_df.std())
    ratio_hwidths_prom_df_mean = float(ratio_hwidths_prom_df.mean())    
    
    summary_stats = pd.DataFrame({'mouse_id':mouse_id, 'file_date':file_date, 'phase':phase, 'base_or_stim':base_or_stim, 'IO_or_plast':IO_or_plast, 'week':week, 'day':day,
                                        'count_peak':peak_ind_df_count,
                                        'freq_peak':peak_ind_df_freq,
                                        'mean_peak_yval':peak_yval_df_mean, 
                                        'mean_peak_prom':peak_prom_df_mean, 
                                        'std_peak_prom':peak_prom_df_std,
                                        'mean_peak_hwidths':hwidths_durations_df_mean,
                                        'std_peak_hwidths':hwidths_durations_df_std,
                                        'mean_ratio_hwidths_prom':ratio_hwidths_prom_df_mean},index = [0])
    
    summary_stats.to_excel(os.path.join(write_fold_data, title_name + ' ' + data_column_name + ' peak summary stats.xlsx'), sheet_name = title_name)

#%%

# ================================= pDCoCG PEAK PLOTS ================================= 

#peak_analysis_output_trunc = peak_analysis_output.iloc[1:].reset_index(drop=True)
    
    with PdfPages(write_fold_fig + "/" + title_name + ' ' + data_column_name + " peak analysis.pdf") as export_pdf:

        # plot timecourse of pDCoCG with peaks, peak prominences and peak half widths

        plt.figure()
        plt.plot(timestamps_zero_sec, data_column, label = 'GCaMP', color = data_color)
        plt.plot(peak_times, data_column[peak_ind], 'o', label = 'Peaks', color = 'purple')
        plt.vlines(x = peak_times, ymin = contour_min, ymax = peak_yval, color = 'purple')
        plt.hlines(y = hwidths_yval, xmin = hwidths_start_times, xmax = hwidths_end_times, color = 'orange')
        plt.xlabel('Time (sec)', fontsize = 12)
        plt.ylabel(y_axis_label, fontsize = 12)
        plt.title(title_name)
        plt.legend(loc = 'upper right', prop = dict(size = 12))
        plt.tick_params(axis = 'x', labelsize = 8)
        plt.tick_params(axis = 'y', labelsize = 8)
        #plt.xlim(650,700)
        #plt.ylim(-30,30)
        export_pdf.savefig()

        # plot histograms of pDCoCG peak analysis variables
        
        plt.figure()
        sns.distplot(peak_analysis_output["peak_times_norm"], rug = True, kde = False, color = data_color)
        plt.xlim(0,1)
        plt.title(title_name)
        export_pdf.savefig()
        
        plt.figure()
        sns.distplot(peak_analysis_output["peak_prom"], rug = True, kde = False, color = data_color)
        plt.title(title_name)
        export_pdf.savefig()

        plt.figure()
        sns.distplot(peak_analysis_output["hwidths_durations"], rug = True, kde = False, color = data_color)
        plt.title(title_name)
        export_pdf.savefig()
        
        plt.figure()
        sns.distplot(peak_analysis_output["ratio_hwidths_prom"], rug = True, kde = False, color = data_color)
        plt.title(title_name)
        export_pdf.savefig()
        
        plt.figure()        
        sns.distplot(peak_analysis_output["peak_prom_norm"], rug = True, kde = False, color = data_color)
        plt.xlim(0,1)
        plt.title(title_name)
        export_pdf.savefig()
        
        plt.figure()
        sns.distplot(peak_analysis_output["hwidths_durations_norm"], rug = True, kde = False, color = data_color)
        plt.xlim(0,1)
        plt.title(title_name)
        export_pdf.savefig()
    
        # plot cumulative histograms of pDCoCG peak analysis variables
                
        plt.figure()
        sns.distplot(peak_analysis_output["peak_prom"], hist_kws={'cumulative': True}, rug = True, kde_kws={'cumulative': True}, color = data_color)
        plt.xlim(left = 0)
        plt.title(title_name)
        export_pdf.savefig()

        plt.figure()
        sns.distplot(peak_analysis_output["hwidths_durations"], hist_kws={'cumulative': True}, rug = True, kde_kws={'cumulative': True}, color = data_color)
        plt.xlim(left = 0)
        plt.title(title_name)
        export_pdf.savefig()
        
        plt.figure()
        sns.distplot(peak_analysis_output["ratio_hwidths_prom"], hist_kws={'cumulative': True}, rug = True, kde_kws={'cumulative': True}, color = data_color)
        plt.xlim(left = 0)
        plt.title(title_name)
        export_pdf.savefig()
        
        plt.figure()
        sns.distplot(peak_analysis_output["peak_prom_norm"], hist_kws={'cumulative': True}, rug = True, kde_kws={'cumulative': True}, color = data_color)
        plt.xlim(0,1)
        plt.title(title_name)
        export_pdf.savefig()

        plt.figure()
        sns.distplot(peak_analysis_output["hwidths_durations_norm"], hist_kws={'cumulative': True}, rug = True, kde_kws={'cumulative': True}, color = data_color)
        plt.xlim(0,1)
        plt.title(title_name)
        export_pdf.savefig()

        # plot scatterplots of pDCoCG peak analysis variables

        plt.figure()
        sns.lmplot(x = "peak_times", y = "peak_prom", data = peak_analysis_output, scatter_kws={'color': data_color}, line_kws={'color': data_color})
        plt.title(title_name)
        export_pdf.savefig()

        plt.figure()
        sns.lmplot(x = "peak_times", y = "hwidths_durations", data = peak_analysis_output, scatter_kws={'color': data_color}, line_kws={'color': data_color})
        plt.title(title_name)
        export_pdf.savefig()
        
        plt.figure()
        sns.lmplot(x = "peak_prom", y = "hwidths_durations", data = peak_analysis_output, scatter_kws={'color': data_color}, line_kws={'color': data_color})
        plt.title(title_name)
        export_pdf.savefig()
        
        plt.figure()
        sns.lmplot(x = "peak_times", y = "ratio_hwidths_prom", data = peak_analysis_output, scatter_kws={'color': data_color}, line_kws={'color': data_color})
        plt.title(title_name)
        export_pdf.savefig()

        # Figures added by Thomas:
        # Peak Y value vs Peak times
        plt.figure()
        sns.lmplot(x = "peak_times", y = "peak_yval", data = peak_analysis_output, scatter_kws={'color': data_color}, line_kws={'color': data_color})
        plt.title(title_name)
        export_pdf.savefig()

        # Peak Y value vs Peak prominence
        plt.figure()
        sns.lmplot(x="peak_prom", y="peak_yval", data=peak_analysis_output, scatter_kws={'color': data_color}, line_kws={'color': data_color})
        plt.title(title_name)
        export_pdf.savefig()

        # Prominence vs Difference in peak times
        plt.figure()
        sns.lmplot(x="peak_time_dif", y="peak_prom_trunc", data = peak_analysis_output_trunc, scatter_kws={'color': data_color}, line_kws={'color': data_color})
        plt.title(title_name)
        export_pdf.savefig()

        # Peak widths vs Difference in peak times
        plt.figure()
        sns.lmplot(x="peak_time_dif", y="hwidths_durations_trunc", data = peak_analysis_output_trunc, scatter_kws={'color': data_color}, line_kws={'color': data_color})
        plt.title(title_name)
        export_pdf.savefig()

        # peak prominence/peak time difference ratio vs time
        plt.figure()
        sns.lmplot(x="peak_times_trunc", y="prom_peak_time_ratio", data = peak_analysis_output_trunc, scatter_kws={'color': data_color}, line_kws={'color': data_color})
        plt.title(title_name)
        export_pdf.savefig()

        # peak widths/peak time difference ratio vs time
        plt.figure()
        sns.lmplot(x="peak_times_trunc", y="hwidths_peak_time_ratio", data = peak_analysis_output_trunc, scatter_kws={'color': data_color}, line_kws={'color': data_color})
        plt.title(title_name)
        export_pdf.savefig()

        # Peak time difference vs time
        plt.figure()
        sns.lmplot(x="peak_times_trunc", y="peak_time_dif", data = peak_analysis_output_trunc, scatter_kws={'color': data_color}, line_kws={'color': data_color})
        plt.title(title_name)
        export_pdf.savefig()

        # Histogram of Peak time difference
        plt.figure()
        sns.distplot(peak_analysis_output["peak_time_dif"].dropna(), rug=True, kde=False, color=data_color)
        plt.title(title_name)
        export_pdf.savefig()

        # Histogram of Prominence / Peak time difference ratio
        plt.figure()
        sns.distplot(peak_analysis_output["prom_peak_time_ratio"].dropna(), rug=True, kde=False, color=data_color)
        plt.title(title_name)
        export_pdf.savefig()

        # Histogram of Peak width / Peak time difference ratio
        plt.figure()
        sns.distplot(peak_analysis_output["hwidths_peak_time_ratio"].dropna(), rug=True, kde=False, color=data_color)
        plt.title(title_name)
        export_pdf.savefig()













