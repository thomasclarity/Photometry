#%%
# Graph the Find Peaks summary data with Seaborn

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
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory

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

# select input file
read_file = askopenfilename(title = 'Select a Summary Stats Input File', filetypes = [("Excel file", "*.xlsx")])
if read_file:
    data = pd.read_excel(read_file)
    print("Input File:", read_file)
else:
    print("Please select an input file")
    quit()

# set output folder
output_folder = askdirectory(title='Select Output Folder')
if output_folder:
    print("Output Folder:", output_folder)
else:
    print("Please select an output directory")
    quit()

#%%

x = "day"
#hue = "phase"
col = "phase"
kind = "violin"
data = data
title_name = "Phase by Day"

with PdfPages(output_folder + "/" + title_name + ".pdf") as export_pdf:

    for column in data.columns[8:]:     # loop over relevant data columns
        fig = sns.catplot(x = x, y = column, col = col, kind = kind, data = data, legend=True)
        fig.set_ylabels(column)
        plt.subplots_adjust(top=0.9)
        plt.suptitle('Phase by Day')
        export_pdf.savefig()    # graph a sns plot for each column


#%%
# determine if the input file is a Plasticity file and then select the Baseline/stimulation and IO/Plasticity data

if 'plasticity' in read_file:
    for row in data["base_or_stim"]:

        if "baseline" in row:
            baseline_df = data[data["base_or_stim"] == "baseline"]

            for row in baseline_df["IO_or_plast"]:
                if "IO" in row:
                    baseline_IO_df = baseline_df[baseline_df["IO_or_plast"] == "IO"]
                elif "plasticity" in row:
                    baseline_plast_df = baseline_df[baseline_df["IO_or_plast"] == "plasticity"]
                else:
                    print("'IO' or 'plasticity' is not in the file name")

        elif "stimulation" in row:
            stimulation_df = data[data["base_or_stim"] == "stimulation"]

            for row in stimulation_df["IO_or_plast"]:
                if "IO" in row:
                    stimulation_IO_df = stimulation_df[stimulation_df["IO_or_plast"] == "IO"]
                elif "plasticity" in row:
                    stimulation_plast_df = stimulation_df[stimulation_df["IO_or_plast"] == "plasticity"]
                else:
                    print("'IO' or 'plasticity' is not in the file name")

        else:
            print("'baseline' or 'stimulation' is not in the file name")


    x = "day"
    #hue = "phase"
    col = "day"
    kind = "violin"
    data = baseline_IO_df
    title_name = "Baseline IO data by day"

    with PdfPages(output_folder + "/" + title_name + ".pdf") as export_pdf:

        for column in data.columns[8:]:     # loop over relevant data columns
            fig = sns.catplot(x = x, y = column, col = None, kind = kind, data = data, legend=True)
            fig.set_ylabels(column)
            plt.subplots_adjust(top=0.92)
            plt.suptitle('Baseline IO data by day')
            export_pdf.savefig()    # graph a sns plot for each column

#%%

    x = "day"
    # hue = "phase"
    col = "week"
    kind = "violin"
    data = baseline_plast_df
    title_name = "Baseline Plasticity by day"

    with PdfPages(output_folder + "/" + title_name + ".pdf") as export_pdf:

        for column in data.columns[8:]:  # loop over relevant data columns
            fig = sns.catplot(x=x, y=column, col=col, kind=kind, data=data, legend=True)
            fig.set_ylabels(column)
            plt.subplots_adjust(top=0.92)
            plt.suptitle('Baseline Plasticity by day')
            export_pdf.savefig()  # graph a sns plot for each column

#%%
    x = "day"
    # hue = "phase"
    col = "day"
    kind = "violin"
    data = stimulation_IO_df
    title_name = "Stimulation IO data by day"

    with PdfPages(output_folder + "/" + title_name + ".pdf") as export_pdf:

        for column in data.columns[8:]:  # loop over relevant data columns
            fig = sns.catplot(x=x, y=column, col=None, kind=kind, data=data, legend=True)
            fig.set_ylabels(column)
            plt.subplots_adjust(top=0.92)
            plt.suptitle('Stimulation IO data by day')
            export_pdf.savefig()  # graph a sns plot for each column

#%%
    x = "day"
    # hue = "phase"
    col = "week"
    kind = "violin"
    data = stimulation_plast_df
    title_name = "Stimulation Plasticity by day"

    with PdfPages(output_folder + "/" + title_name + ".pdf") as export_pdf:

        for column in data.columns[8:]:  # loop over relevant data columns
            fig = sns.catplot(x=x, y=column, col=col, kind=kind, data=data, legend=True)
            fig.set_ylabels(column)
            plt.subplots_adjust(top=0.92)
            plt.suptitle('Stimulation Plasticity by day')
            export_pdf.savefig()  # graph a sns plot for each column

#%%
    base_stim_IO_df = pd.concat([baseline_IO_df, stimulation_IO_df], ignore_index=True)

    x = "day"
    hue = "base_or_stim"
    col = "week"
    kind = "violin"
    data = base_stim_IO_df
    title_name = "Baseline IO vs Stimulation IO by day"

    # x = "base_or_stim"
    # hue = "week"
    # col = "day"
    # kind = "violin"
    # data = base_stim_IO_df
    # title_name = "Baseline IO vs Stimulation IO by day"

    with PdfPages(output_folder + "/" + title_name + ".pdf") as export_pdf:

        for column in data.columns[8:]:  # loop over relevant data columns
            fig = sns.catplot(x=x, y=column, hue=hue, col=col, kind=kind, data=data, legend=True)
            fig.set_ylabels(column)
            plt.subplots_adjust(top=0.92)
            plt.suptitle('Baseline IO vs Stimulation IO by day')
            export_pdf.savefig()  # graph a sns plot for each column

#%%
    base_stim_plast_df = pd.concat([baseline_plast_df, stimulation_plast_df], ignore_index=True)

    x = "day"
    hue = "base_or_stim"
    col = "week"
    kind = "violin"
    data = base_stim_plast_df
    title_name = "Baseline Plasticity vs Stimulation Plasticity by day"

    with PdfPages(output_folder + "/" + title_name + ".pdf") as export_pdf:

        for column in data.columns[8:]:  # loop over relevant data columns
            fig = sns.catplot(x=x, y=column, hue=hue, col=col, kind=kind, data=data, legend=True)
            fig.set_ylabels(column)
            plt.subplots_adjust(top=0.9)
            plt.suptitle('Baseline Plasticity vs Stimulation Plasticity by day')
            export_pdf.savefig()  # graph a sns plot for each column

#%%
# replace baseline IO week 0 day 2 sessions as baseline IO week 5 day 2
    # for row in baseline_IO_df["day"]:
    #     if row == 2:
    #         baseline_IO_d2_df = baseline_IO_df[baseline_IO_df["day"] == 2]
    #         baseline_IO_d2_df['week'].replace({0:5}, inplace=True)
    #     else:
    #         continue
    #
    # for row in baseline_IO_df["day"]:
    #     if row == 1:
    #         baseline_IO_d1_df = baseline_IO_df[baseline_IO_df["day"] == 1]

    baseline_IO_d2_df = baseline_IO_df[baseline_IO_df["day"] == 2]
    print(baseline_IO_d2_df.to_string())
    baseline_IO_d2_df.loc[:,'week'].replace({0:5}, inplace=True)
    print(baseline_IO_d2_df.to_string())
    baseline_IO_d1_df = baseline_IO_df[baseline_IO_df["day"] == 1]

    #baseline_IO_df.loc[baseline_IO_df["day"] == 2, "week"] = 5

# concatenate the base IO sessions (week 0 and week 5) and the baseline plasticity sessions to create the full Baseline data
    baseline_data = pd.concat([baseline_IO_d2_df, baseline_IO_d1_df, baseline_plast_df])

    x = "day"
    # hue = "base_or_stim"
    col = "week"
    kind = "violin"
    data = baseline_data
    title_name = "Baseline data across experiment"

    with PdfPages(output_folder + "/" + title_name + ".pdf") as export_pdf:

        for column in data.columns[8:]:  # loop over relevant data columns
            fig = sns.catplot(x=x, y=column, col=col, kind=kind, data=data, legend=True)
            fig.set_ylabels(column)
            plt.subplots_adjust(top=0.9)
            plt.suptitle('Baseline data across experiment')
            export_pdf.savefig()  # graph a sns plot for each column

#%%
# replace Stimulation IO week 0 day 2 sessions as Stimulation IO week 5 day 2
#         for row in stimulation_IO_df["day"]:
#             if row == 2:
#                 stimulation_IO_d2_df = stimulation_IO_df[stimulation_IO_df["day"] == 2]
#                 stimulation_IO_d2_df['week'].replace({0: 5}, inplace=True)
#             else:
#                 continue
#
#         for row in stimulation_IO_df["day"]:
#             if row == 1:
#                 stimulation_IO_d1_df = stimulation_IO_df[stimulation_IO_df["day"] == 1]

    stimulation_IO_d2_df = stimulation_IO_df[stimulation_IO_df["day"] == 2]
    print(stimulation_IO_d2_df.to_string())
    stimulation_IO_d2_df['week'].replace({0: 5}, inplace=True)
    print(stimulation_IO_d2_df.to_string())
    stimulation_IO_d1_df = stimulation_IO_df[stimulation_IO_df["day"] == 1]

# concatenate the Stimulation IO sessions (week 0 and week 5) and the stiimulation plasticity sessions to create the full stimulation data
    stimulation_data = pd.concat([stimulation_IO_d2_df, stimulation_IO_d1_df, stimulation_plast_df])
    x = "day"
    # hue = "base_or_stim"
    col = "week"
    kind = "violin"
    data = stimulation_data
    title_name = "Stimulation data across experiment"

    with PdfPages(output_folder + "/" + title_name + ".pdf") as export_pdf:

        for column in data.columns[8:]:  # loop over relevant data columns
            fig = sns.catplot(x=x, y=column, col=col, kind=kind, data=data, legend=True)
            fig.set_ylabels(column)
            plt.subplots_adjust(top=0.9)
            plt.suptitle('Stimulation data across experiment')
            export_pdf.savefig()  # graph a sns plot for each column


