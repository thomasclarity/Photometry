# %%
# from os.path import expanduser as eu

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
import json
import time

sns.set(style="darkgrid")
sns.set_palette('muted')
sns.set_context("poster")
pd.set_option('display.max_columns', 30)


# %% ============================================= LOAD COMMENTS =====================================================
def load_comments(mouse, protocol, week, day, fpath, file):
    """
    This definition processed comments into a dataframe. There must be only one copy of each unique comment.
    """


    # mouse = 'm357'
    # test = 'Plasticity'
    # fpath = "C:\\Users\\clarityt2\\Documents\\Gordon Lab\\Photometry Processing\\TEST2\\Test Output\\"
    # file = "m357_Plasticity_w1d1"

    file1 = glob(f'{fpath}/commentdata*{file}*.csv')

    if len(file1) > 1:
        print('error there is more than one comment file starting with ' + str(fpath) + str(file1))
        return
    elif len(file1) < 1:
        print('error there is no comment file for ' + str(fpath) + str(file1))
        return
    else:
        print(str(file1[0]))
        file_to_load1 = file1[0]

    tempdata1 = pd.read_csv(file_to_load1)

    return tempdata1


# %% ============================================= LOAD PHOTOMETRY - PEAKS =====================================================
def Peaks_photometry_data(mouse, protocol, photometry_filetype, week, day, fpath, file, t_start, t_end):
    """
    Loads processed photometry file, calculates dFoF and finds the max value for each trial within a given window of time (t_start, t_end)
    """
    #    mouse = 'm363'
    #    protocol = 'Plasticity'
    #    fpath = "D:\\Plasticity"
    #    file = 'm363_Plasticity_w2d2'
    #    week = 'w2'
    #    day = 'd2'
    #    t_start = 10
    #    t_end = 15

    input_yvalue = 'downsample_photoncounts'
    output_yvalue = 'peak_dFoFG'

    photofile = glob(f'{fpath}/photodata*{file}.csv')

    if len(photofile) > 1:
        print('error there is more than one photometry file starting with ' + fpath + '\\' + file)
        return
    elif len(photofile) < 1:
        print('error, no photometry file exists for ' + fpath + "\\" + file)
        return
    else:
        fid2 = str(glob(f'{fpath}/photodata*{file}.csv')[0])
        print(fid2)

    photometry_temp = pd.read_csv(fid2)
    photo_times = photometry_temp['total_time']
    photo_data = photometry_temp['downsample_photoncounts']

    #    mouselist = [mouse] * len(photometry_all['TimeStampsZerod'])
    photometry_temp.insert(0, 'Mouse', mouse)
    photometry_temp.insert(1, 'Protocol', protocol)
    photometry_temp.insert(2, 'TimeStamp', photo_times)
    photometry_temp.insert(3, 'photon counts', photo_data)
    photometry_temp.insert(4, 'Week', week)
    photometry_temp.insert(5, 'Day', day)
    #    photometry_temp.insert(4, 'pDFoFRatio', photometry_all['pDFoFRatio'] )
    #    photometry_temp.insert(5, 'zScorepDFoFRatio', photometry_all['zScorepDFoFRatio'] )
    #    photometry_temp.insert(6, 'pDFoFG', photometry_all['pDFoFG'] )
    #    photometry_temp.insert(7, 'zScorepDFoFG', photometry_all['zScorepDFoFG'] )
    #    photometry_temp.insert(8, 'pcRowSumG', photometry_all['pcRowSumG'])

    # This portion finds the trials by a two second gap

    trial_ends = []
    trial_starts = []
    trial_starts.append(0)
    for time_i in range(1, len(photometry_temp)):
        current_time = photo_times[time_i]
        last_time = photo_times[time_i - 1]
        # print (current_time)
        # print (next_time)
        if (current_time - last_time) > 1.5:
            # print('gap is at' + str(time_i) + ' time is ' + str(current_time) + ' and ' + str(last_time))
            trial_ends.append(time_i - 1)
            trial_starts.append(time_i)
    trial_ends.append(len(photometry_temp) - 1)

    #    print (trial_ends)
    #    print(trial_starts)

    trial_base_avgs = []
    trial_base_stdevs = []
    for trial_start_i in range(len(trial_starts)):
        starttime_index = trial_starts[trial_start_i]
        starttime_time = photo_times[starttime_index]
        # print (starttime_time)

        baseline_indices = np.where(
            (photo_times >= (starttime_time)) &
            (photo_times <= (starttime_time + 9.5)))[0]
        if baseline_indices.shape[0] < 50:
            import warnings
            warnings.warn(f'data loss: baseline_indices= {baseline_indices}')
            continue
        # print(baseline_indices)
        event = photo_times.loc[baseline_indices]
        basedata = list(photometry_temp[input_yvalue].loc[baseline_indices])
        average_basedata = statistics.mean(basedata)
        stdev_basedata = statistics.stdev(basedata)

        # print(average_basedata)
        trial_base_avgs.append(average_basedata)
        trial_base_stdevs.append(stdev_basedata)

    # It says "photoncounts" but this works for coeffs too. photoncounts ~ coeffs ~ raw
    new_data = pd.DataFrame(
        columns=['data_i', 'mouse', 'protocol', 'peak_raw', output_yvalue, 'peak_SNR', 'day', 'week'])
    peak_raw_list = []
    peak_dFoF_list = []
    peak_SNR_list = []
    data_i_list1 = []
    data_i_list2 = []

    for data_i in range(len(trial_base_avgs)):
        this_avg = trial_base_avgs[data_i]
        this_stdev = trial_base_stdevs[data_i]
        this_start = photo_times[trial_starts[data_i]]
        this_end = photo_times[trial_ends[data_i]]

        new_data_index = []
        new_data_pDFoFG = []
        new_data_SNRG = []
        new_data_time = []
        old_data_photoncounts = []
        trial_avgbaselines = []
        trial_stdevbaselines = []

        data_indices = np.where(
            (photo_times >= (this_start + t_start)) &
            (photo_times <= (this_start + t_end)))[0]

        for data_point in range(len(data_indices)):
            data_point_index = data_indices[data_point]
            data_point_time = photo_times[data_point_index]
            old_data_point = photo_data[data_point_index]

            new_datapoint_pDFoFG = ((old_data_point - this_avg) / this_avg) * 100
            new_datapoint_SNRG = (old_data_point - this_avg) / this_stdev

            new_data_pDFoFG.append(new_datapoint_pDFoFG)
            new_data_SNRG.append(new_datapoint_SNRG)

            new_data_index.append(data_point_index)
            new_data_time.append(data_point_time)
            old_data_photoncounts.append(old_data_point)
            trial_avgbaselines.append(this_avg)
            trial_stdevbaselines.append(this_stdev)
            data_i_list1.append(data_i)

        peak_raw = max(old_data_photoncounts)
        peak_dFoF = max(new_data_pDFoFG)
        peak_SNR = max(new_data_SNRG)
        data_i_list2.append(data_i)
        peak_raw_list.append(peak_raw)
        peak_dFoF_list.append(peak_dFoF)
        peak_SNR_list.append(peak_SNR)

        new_data = new_data.append(
            {'data_i': data_i, 'mouse': mouse, 'protocol': protocol, 'peak_raw': peak_raw, output_yvalue: peak_dFoF,
             'peak_SNRG': peak_SNR, 'day': day, 'week': week}, ignore_index=True)
    #
    #    new_data2 = new_data
    #    new_data2.insert(7, 'index', new_data_index)
    #    new_data2.insert(8, 'time', new_data_time)
    #    new_data2.insert(9, 'pDFoFG', new_data_pDFoFG)
    #    new_data2.insert(10, 'SNRG', new_data_SNRG)
    #    new_data2.insert(11, 'protocol', protocol)
    #    new_data2.insert(12, 'photon_counts_green', old_data_photoncounts)
    #    new_data2.insert(13, 'trial_baseline_avg', trial_avgbaselines)
    #    new_data2.insert(14, 'trial_baseline_stdev', trial_stdevbaselines)
    #    new_data2.insert(15, 'data_i', data_i_list1)
    #
    #    new_data2.to_csv ("C:\\Users\\mikofskyrm\\Desktop\\Photometry\\photodata_peaks_long.csv", index = None, header=True)

    #    print(photometry_temp)
    return new_data


# %% ============================================= LOAD PHOTOMETRY - Lines =====================================================
def Lines_photometry_data(mouse, protocol, photometry_filetype, week, day, fpath, file):
    """
    Loads processed photometry file, calculates dFoF
    """
    #    mouse = 'm356'
    #    protocol = 'Plasticity'
    #    fpath = "C:\\Users\\mikofskyrm\\Desktop\\DATA_OUT\\Processed_Files"
    #    file = 'm356_Plasticity_w1d1'
    #    week = 'w1'
    #    day = 'd1'

    photofile = glob(f'{fpath}/photodata*{file}.csv')
    if len(photofile) > 1:
        print('error there is more than one photometry file starting with ' + fpath + '/' + file)
        return
    elif len(photofile) < 1:
        print('error, no photometry file exists for ' + fpath + '/' + file)
        return
    else:
        fid2 = str(glob(f'{fpath}/photodata*{file}.csv')[0])
        print(fid2)

    photometry_temp = pd.read_csv(fid2)

    photo_times = photometry_temp['total_time']
    photo_data = photometry_temp['downsample_photoncounts']

    # This portion finds the trials by a two second gap
    trial_ends = []
    trial_starts = []
    trial_starts.append(0)
    for time_i in range(1, len(photometry_temp)):
        current_time = photo_times[time_i]
        last_time = photo_times[time_i - 1]
        # print (current_time)
        # print (next_time)
        if (current_time - last_time) > 1.5:
            # print('gap is at' + str(time_i) + ' time is ' + str(current_time) + ' and ' + str(last_time) + ' gap length is ' + str(current_time - last_time))
            trial_ends.append(time_i - 1)
            trial_starts.append(time_i)
        # elif (current_time - last_time) > 4.5:
        # print('extra large gap at ' + str(time_i) + ' gap is ' + str(current_time - last_time) )
    trial_ends.append(len(photometry_temp) - 1)

    #    print (trial_ends)
    #    print(trial_starts)

    #    for start, end in zip(trial_starts, trial_ends):
    #        plt.plot(photo_data[start:end])
    #        plt.show()
    #

    # We start with linear corrected photon counts, and calculate our own baseline for each trial, then calculate pDFoFG and SNRG (these will be called this even if they are based on coeffs)
    trial_base_avgs = []
    trial_base_stdevs = []
    for trial_start_i in range(len(trial_starts)):
        starttime_index = trial_starts[trial_start_i]
        starttime_time = photo_times[starttime_index]
        # print (starttime_time)

        baseline_indices = np.where(
            (photo_times >= (starttime_time)) &
            (photo_times <= (starttime_time + 9.5)))[0]
        if baseline_indices.shape[0] < 50:
            import warnings
            warnings.warn(f'data loss: baseline_indices= {baseline_indices}')
            continue
        # print(baseline_indices)
        event = photo_times.loc[baseline_indices]
        basedata = list(photometry_temp['downsample_photoncounts'].loc[baseline_indices])

        average_basedata = statistics.mean(basedata)
        # try:
        stdev_basedata = statistics.stdev(basedata)
        # except Exception:
        #    import pdb;pdb.set_trace()

        # print(average_basedata)
        trial_base_avgs.append(average_basedata)
        trial_base_stdevs.append(stdev_basedata)

    #    print(trial_base_avgs)

    new_data = pd.DataFrame()
    new_data_index = []
    new_data_pDFoFG = []
    new_data_SNRG = []
    new_data_time = []
    old_data_photoncounts = []
    trial_avgbaselines = []
    trial_stdevbaselines = []
    data_i_list = []

    for data_i in range(len(trial_base_avgs)):
        this_avg = trial_base_avgs[data_i]
        this_stdev = trial_base_stdevs[data_i]
        this_start = photo_times[trial_starts[data_i]]
        this_end = photo_times[trial_ends[data_i]]

        data_indices = np.where(
            (photo_times >= (this_start)) &
            (photo_times <= (this_start + 30)))[0]

        #        if len(data_indices) >= 1250:
        #            #print('trial with start time ' + str(this_start) + ' and end time ' + str(this_end) + ' is too long (likely plasticity) and will be trimmed for graphing')
        #            data_indices = np.where(
        #            (photo_times >= (this_start)) &
        #            (photo_times <= (this_start+30)))[0]

        for data_point in range(len(data_indices)):
            data_point_index = data_indices[data_point]
            data_point_time = photo_times[data_point_index]
            old_data_point = photo_data[data_point_index]

            new_datapoint_pDFoFG = ((old_data_point - this_avg) / this_avg) * 100
            new_datapoint_SNRG = (old_data_point - this_avg) / this_stdev

            new_data_pDFoFG.append(new_datapoint_pDFoFG)
            new_data_SNRG.append(new_datapoint_SNRG)

            new_data_index.append(data_point_index)
            new_data_time.append(data_point_time)
            old_data_photoncounts.append(old_data_point)
            trial_avgbaselines.append(this_avg)
            trial_stdevbaselines.append(this_stdev)
            data_i_list.append(data_i)

    # print(new_data_list)
    # print(new_data_index)

    new_data.insert(0, 'index', new_data_index)
    new_data.insert(1, 'time', new_data_time)
    new_data.insert(2, 'pDFoFG', new_data_pDFoFG)
    new_data.insert(3, 'SNRG', new_data_SNRG)
    new_data.insert(4, 'protocol', protocol)
    new_data.insert(5, 'photon_counts_green', old_data_photoncounts)
    new_data.insert(6, 'trial_baseline_avg', trial_avgbaselines)
    new_data.insert(7, 'trial_baseline_stdev', trial_stdevbaselines)
    new_data.insert(8, 'data_i', data_i_list)
    new_data.insert(9, 'day', day)
    new_data.insert(10, 'week', week)
    new_data.insert(11, 'mouse', mouse)

    #   new_data.to_csv ("C:\\Users\\mikofskyrm\\Desktop\\Photometry\\photodata_test.csv", index = None, header=True)

    #    print(photometry_temp)
    return new_data


# %% ============================================= LOAD PHOTOMETRY - Lines =====================================================
def PrepAverage_photometry_data(mouse, protocol, photometry_filetype, week, day, fpath, file, t_start, t_end):
    """
    This definition loads processed photometry file, calcualtes dFoF and prepares for averaging later
    """

    #    mouse = 'm356'
    #    protocol = 'Plasticity'
    #    fpath = "C:\\Users\\mikofskyrm\\Desktop\\DATA_OUT\\Processed_Files"
    #    file = 'm356_Plasticity_w1d1'
    #    week = 'w1'
    #    day = 'd1'

    photofile = glob(f'{fpath}/photodata*{file}.csv')
    # print(nev_file)
    if len(photofile) > 1:
        print('error there is more than one photometry file starting with ' + fpath + '/' + file)
        return
    elif len(photofile) < 1:
        print('error, no photometry file exists for ' + fpath + '/' + file)
        return
    else:
        fid2 = str(glob(f'{fpath}/photodata*{file}.csv')[0])
        print(fid2)

    photometry_temp = pd.read_csv(fid2)

    photo_times = photometry_temp['total_time']
    photo_data = photometry_temp['downsample_photoncounts']

    # This portion finds the trials by a two second gap
    trial_ends = []
    trial_starts = []
    trial_starts.append(0)
    for time_i in range(1, len(photometry_temp)):
        current_time = photo_times[time_i]
        last_time = photo_times[time_i - 1]
        # print (current_time)
        # print (next_time)
        if (current_time - last_time) > 1.5:
            # print('gap is at' + str(time_i) + ' time is ' + str(current_time) + ' and ' + str(last_time) + ' gap length is ' + str(current_time - last_time))
            trial_ends.append(time_i - 1)
            trial_starts.append(time_i)
        # elif (current_time - last_time) > 4.5:
        # print('extra large gap at ' + str(time_i) + ' gap is ' + str(current_time - last_time) )
    trial_ends.append(len(photometry_temp) - 1)

    #    print (trial_ends)
    #    print(trial_starts)

    #    for start, end in zip(trial_starts, trial_ends):
    #        plt.plot(photo_data[start:end])
    #        plt.show()
    #

    # We start with corrected photon counts, and calculate our own baseline for each trial, then calculate pDFoFG and SNRG (these will be called this even if they are based on coeffs)
    trial_base_avgs = []
    trial_base_stdevs = []
    for trial_start_i in range(len(trial_starts)):
        starttime_index = trial_starts[trial_start_i]
        starttime_time = photo_times[starttime_index]
        # print (starttime_time)

        baseline_indices = np.where(
            (photo_times >= (starttime_time)) &
            (photo_times <= (starttime_time + 9.5)))[0]
        if baseline_indices.shape[0] < 50:
            import warnings
            warnings.warn(f'data loss: baseline_indices= {baseline_indices}')
            continue
        # print(baseline_indices)
        event = photo_times.loc[baseline_indices]
        basedata = list(photometry_temp['downsample_photoncounts'].loc[baseline_indices])

        average_basedata = statistics.mean(basedata)
        # try:
        stdev_basedata = statistics.stdev(basedata)
        # except Exception:
        #    import pdb;pdb.set_trace()

        # print(average_basedata)
        trial_base_avgs.append(average_basedata)
        trial_base_stdevs.append(stdev_basedata)

    #    print(trial_base_avgs)

    new_data = pd.DataFrame()
    new_data_index = []
    new_data_pDFoFG = []
    new_data_SNRG = []
    new_data_time = []
    old_data_photoncounts = []
    trial_avgbaselines = []
    trial_stdevbaselines = []
    data_i_list = []

    for data_i in range(len(trial_base_avgs)):
        this_avg = trial_base_avgs[data_i]
        this_stdev = trial_base_stdevs[data_i]
        this_start = photo_times[trial_starts[data_i]]
        this_end = photo_times[trial_ends[data_i]]

        data_indices = np.where(
            (photo_times >= (this_start + t_start)) &
            (photo_times <= (this_start + t_end)))[0]

        #        if len(data_indices) >= 1250:
        #            #print('trial with start time ' + str(this_start) + ' and end time ' + str(this_end) + ' is too long (likely plasticity) and will be trimmed for graphing')
        #            data_indices = np.where(
        #            (photo_times >= (this_start)) &
        #            (photo_times <= (this_start+30)))[0]

        for data_point in range(len(data_indices)):
            data_point_index = data_indices[data_point]
            data_point_time = photo_times[data_point_index]
            old_data_point = photo_data[data_point_index]

            new_datapoint_pDFoFG = ((old_data_point - this_avg) / this_avg) * 100
            new_datapoint_SNRG = (old_data_point - this_avg) / this_stdev

            new_data_pDFoFG.append(new_datapoint_pDFoFG)
            new_data_SNRG.append(new_datapoint_SNRG)

            new_data_index.append(data_point_index)
            new_data_time.append(data_point_time)
            old_data_photoncounts.append(old_data_point)
            trial_avgbaselines.append(this_avg)
            trial_stdevbaselines.append(this_stdev)
            data_i_list.append(data_i)

    # print(new_data_list)
    # print(new_data_index)

    new_data.insert(0, 'index', new_data_index)
    new_data.insert(1, 'time', new_data_time)
    new_data.insert(2, 'pDFoFG', new_data_pDFoFG)
    new_data.insert(3, 'SNRG', new_data_SNRG)
    new_data.insert(4, 'protocol', protocol)
    new_data.insert(5, 'photon_counts_green', old_data_photoncounts)
    new_data.insert(6, 'trial_baseline_avg', trial_avgbaselines)
    new_data.insert(7, 'trial_baseline_stdev', trial_stdevbaselines)
    new_data.insert(8, 'data_i', data_i_list)
    new_data.insert(9, 'day', day)
    new_data.insert(10, 'week', week)
    new_data.insert(11, 'mouse', mouse)

    #   new_data.to_csv ("C:\\Users\\mikofskyrm\\Desktop\\Photometry\\photodata_test.csv", index = None, header=True)

    #    print(photometry_temp)
    return new_data


# %% ========================== COMBINE DATA - PEAKS =======================================================
def Combine_Comments_Photometry_Peaks(yvalue, commentdata_all, photodata_all, mouse_list, test_list, title, categories):
    """
    This definition combines photometry data and comment data in preparation for peaks graphs
    """
    #    yvalue = 'peak_dFoF'

    all_data = []

    starttrial_index_tuple = np.where(
        (commentdata_all['stim_event'].str.contains('off_pre')) & commentdata_all['s_or_e_of_event'].str.contains(
            'end'))
    starttrial_index_array = starttrial_index_tuple[0]
    print(str(len(starttrial_index_array)) + ' trials in dataframe')

    for trialindex in starttrial_index_array:
        comment_trial = commentdata_all.loc[trialindex, 'trial_inday']
        #            print ('trial is ' + str(trial) + 'and comment trial is ' + str(comment_verify))

        mouse_data = commentdata_all.loc[trialindex, 'mouse']
        protocol_data = commentdata_all.loc[trialindex, 'protocol']
        week_data = commentdata_all.loc[trialindex, 'week']
        day_data = commentdata_all.loc[trialindex, 'dayinweek']
        laserpower_data = commentdata_all.loc[trialindex, 'pulse_laserpower']
        frequency_data = commentdata_all.loc[trialindex, 'pulse_frequency']
        npulse_data = commentdata_all.loc[trialindex, 'pulse_n']
        stimtype_data = commentdata_all.loc[trialindex, 'stim_type']
        pulsewidth_data = commentdata_all.loc[trialindex, 'pulse_width']
        round_data = commentdata_all.loc[trialindex, 'round']
        sex_data = commentdata_all.loc[trialindex, 'sexmouse']
        mutant_data = commentdata_all.loc[trialindex, 'mutant_mouse']
        phase_data = commentdata_all.loc[trialindex, 'stim_type']
        plasticity_data = commentdata_all.loc[trialindex, 'plasticity_type']
        test_pulse_data = commentdata_all.loc[trialindex, 'test_pulse_type']

        event_indices = np.where(
            (photodata_all['data_i'] == comment_trial) &
            (photodata_all['protocol'] == protocol_data) &
            (photodata_all['mouse'] == mouse_data) &
            (photodata_all['day'] == day_data) &
            (photodata_all['week'] == week_data))[0]
        #           print(trial)
        #           print(comment_trial)
        #           print(day_data)
        event = photodata_all.loc[event_indices, :]
        # print(event)
        DeltaTimes = list(event['data_i'])
        CoEfs = list(event[yvalue])

        # print(DeltaTimes)
        # print(CoEfs)

        if yvalue == 'peak_dFoFG':
            data_c = pd.DataFrame.from_dict(dict(Trial=DeltaTimes, peak_dFoFG=CoEfs))
        elif yvalue == 'peak_SNRG':
            data_c = pd.DataFrame.from_dict(dict(Trial=DeltaTimes, peak_SNRG=CoEfs))

        # print(data_c)

        data_c.insert(0, 'Protocol', protocol_data)
        data_c.insert(3, 'Stim Laser Power', laserpower_data)
        data_c.insert(4, 'Stim Frequency', frequency_data)
        data_c.insert(5, 'Stim nPulses', npulse_data)
        data_c.insert(6, 'Stim Pulse Width', pulsewidth_data)
        data_c.insert(7, 'Mouse', mouse_data)
        data_c.insert(8, 'Genotype', mutant_data)
        data_c.insert(9, 'Stim Type', stimtype_data)
        data_c.insert(10, 'Trial_i', comment_trial)
        data_c.insert(11, 'Round', round_data)
        data_c.insert(12, 'Sex', sex_data)
        data_c.insert(13, 'Week', week_data)
        data_c.insert(14, 'Day', day_data)
        data_c.insert(15, 'Phase', phase_data)
        data_c.insert(16, 'Plasticity Condition', plasticity_data)
        data_c.insert(17, 'Test Pulse Condition', test_pulse_data)

        # print(data_c)
        all_data.append(data_c)

    # print(all_data)
    all_data = pd.concat(all_data)
    # print(all_data)

    # NOTE: Need to force all integers to be strings, so they can be loaded into seaborn as categorial values instead of continuous
    all_data['Stim Laser Power'] = all_data['Stim Laser Power'].astype(str) + 'mW '
    all_data['Stim nPulses'] = all_data['Stim nPulses'].astype(str) + 'n'
    all_data['Stim Frequency'] = all_data['Stim Frequency'].astype(str) + 'Hz'

    return (all_data)


# %% =================================== COMBINE DATA - LINES =======================================================
def Combine_Comments_Photometry_Lines(yvalue, commentdata_all, photodata_all, mouse_list, test_list, title, categories,
                                      timestamps_yes_or_no):
    """
    This definition combines photometry data and comment data in preparation for line graphs and heatmaps
    """
    #    yvalue = 'pDFoFG'

    all_data = []
    #
    #    if timestamps_yes_or_no == 'yes':
    #        timepost = 30
    #        starttrial_index_tuple = np.where((commentdata_all['stim_event'].str.contains('off_pre')) & commentdata_all['s_or_e_of_event'].str.contains('start'))
    #        starttrial_index_array = starttrial_index_tuple[0]
    #        starttrial_times = list(commentdata_all.loc[starttrial_index_array, 'times'])
    #
    #        for trial in range(0, len(starttrial_times)):
    #            trialtimestamp = starttrial_times[trial]
    #            trialindex = starttrial_index_array[trial]
    #
    #            mouse_data = commentdata_all.loc[trialindex, 'Mouse']
    #            day_data = commentdata_all.loc[trialindex, 'Day']
    #            genotype_data = commentdata_all.loc[trialindex, 'Genotype']
    #            laserpower_data = commentdata_all.loc[trialindex, 'laserpow']
    #            frequency_data = commentdata_all.loc[trialindex, 'frequency']
    #            npulse_data = commentdata_all.loc[trialindex, 'n_of_pulses']
    #            stimtype_data = commentdata_all.loc[trialindex, 'stim_type']
    #            pulsewidth_data = commentdata_all.loc[trialindex, 'width']
    #
    #
    #            event_indices = np.where(
    #                    (photodata_all['time'] >= (trialtimestamp)) &
    #                    (photodata_all['time'] <= (trialtimestamp + timepost)) &
    #                    (photodata_all['day'] == day_data ))[0]
    #            event = photodata_all.loc[event_indices,:]
    #    #        print(event)
    #            RawTimes = list(event['time'])
    #            CoEfs = list(event[yvalue])
    #
    #            if Time_Type == 'DeltaTimes':
    #                DeltaTimes = []
    #                for oldtime in range(len(RawTimes)):
    #                    newtime = RawTimes[oldtime] - trialtimestamp
    #                    newtime_round = round(newtime,1)
    #                    #print(newtime)
    #                    DeltaTimes.append(newtime_round)
    ##            print(DeltaTimes)
    ##            Time = DeltaTimes
    #
    #
    #            elif Time_Type == 'RawTimes':
    #                print('average requires DeltaTimes')
    #
    #            else:
    #                print('!!!! incorrect Time_Type !!!! Try again with either "RawTimes" or "DeltaTimes"')
    #
    #            if yvalue == 'pDFoFG':
    #                data_c = pd.DataFrame.from_dict(dict(DeltaTimes = DeltaTimes, pDFoFG = CoEfs, RawTimes = RawTimes))
    #            elif yvalue == 'SNRG':
    #                data_c = pd.DataFrame.from_dict(dict(DeltaTimes = DeltaTimes, SNRG = CoEfs, RawTimes = RawTimes))
    #            else:
    #                print('The yvalue selection is incorrect, defaulted to pDFoFG')
    #                data_c = pd.DataFrame.from_dict(dict(DeltaTimes = DeltaTimes, pDFoFG = CoEfs, RawTimes = RawTimes))
    #
    #            #print(data_c)
    #
    #
    #            data_c.insert(0,'Day', day_data)
    #            data_c.insert(3,'Stim Laser Power', laserpower_data)
    #            data_c.insert(4,'Stim Frequency', frequency_data)
    #            data_c.insert(5,'Stim nPulses', npulse_data)
    #            data_c.insert(6,'Stim Pulse Width', pulsewidth_data)
    #            data_c.insert(7,'Mouse', mouse_data)
    #            data_c.insert(8,'Genotype', genotype_data)
    #            data_c.insert(9,'Stim Type', stimtype_data)
    #            #print(data_c)
    #            all_data.append(data_c)
    #            #print (all_data)

    #    if timestamps_yes_or_no == 'no':
    starttrial_index_tuple = np.where(
        (commentdata_all['stim_event'].str.contains('off_pre')) & commentdata_all['s_or_e_of_event'].str.contains(
            'end'))     # find the indices of when the stimulation part of trial begins
    starttrial_index_array = starttrial_index_tuple[0]
    print(str(len(starttrial_index_array)) + ' trials in dataframe, now starting combining comments and photometry')

    i_percent = 0
    for trialindex in starttrial_index_array:
        percent = int((i_percent / len(starttrial_index_array)) * 1000)
        if percent % 100 == 0:
            print(str(percent / 10) + ' percent done')
        i_percent += 1

        comment_trial = commentdata_all.loc[trialindex, 'trial_inday']      # find the comment "trial in day" number that is associated with the start stimulation index
        #            print ('trial is ' + str(trial) + 'and comment trial is ' + str(comment_verify))
        mouse_data = commentdata_all.loc[trialindex, 'mouse']
        protocol_data = commentdata_all.loc[trialindex, 'protocol']
        week_data = commentdata_all.loc[trialindex, 'week']
        day_data = commentdata_all.loc[trialindex, 'dayinweek']
        laserpower_data = commentdata_all.loc[trialindex, 'pulse_laserpower']
        frequency_data = commentdata_all.loc[trialindex, 'pulse_frequency']
        npulse_data = commentdata_all.loc[trialindex, 'pulse_n']
        stimtype_data = commentdata_all.loc[trialindex, 'stim_type']
        pulsewidth_data = commentdata_all.loc[trialindex, 'pulse_width']
        round_data = commentdata_all.loc[trialindex, 'round']
        sex_data = commentdata_all.loc[trialindex, 'sexmouse']
        mutant_data = commentdata_all.loc[trialindex, 'mutant_mouse']
        phase_data = commentdata_all.loc[trialindex, 'stim_type']
        plasticity_data = commentdata_all.loc[trialindex, 'plasticity_type']
        test_pulse_data = commentdata_all.loc[trialindex, 'test_pulse_type']

        event_indices = np.where(
            (photodata_all['data_i'] == comment_trial) &
            (photodata_all['protocol'] == protocol_data) &
            (photodata_all['mouse'] == mouse_data) &
            (photodata_all['day'] == day_data) &
            (photodata_all['week'] == week_data))[0]        # find the indices of the photometry data that correspond with the trial in day number

        #        print(trial)
        #        print(comment_trial)
        #        print(event

        event = photodata_all.loc[event_indices, :]     # collect all the photometry data that goes with those indices (this is the all the photometry data for that particular trial in the day)

        RawTimes = list(event['time'])
        CoEfs = list(event[yvalue])

        DeltaTimes = []     # zero the raw times for that trial
        for oldtime in range(len(RawTimes)):
            newtime = RawTimes[oldtime] - RawTimes[0]
            newtime_round = round(newtime, 1)
            # print(newtime)
            DeltaTimes.append(newtime_round)
        #            print(DeltaTimes)
        #            Time = DeltaTimes

        if yvalue == 'pDFoFG':
            data_c = pd.DataFrame.from_dict(dict(DeltaTimes=DeltaTimes, pDFoFG=CoEfs, RawTimes=RawTimes))
        elif yvalue == 'SNRG':
            data_c = pd.DataFrame.from_dict(dict(DeltaTimes=DeltaTimes, SNRG=CoEfs, RawTimes=RawTimes))
        elif yvalue == 'pDCoCG':
            data_c = pd.DataFrame.from_dict(dict(DeltaTimes=DeltaTimes, pDCoCG=CoEfs, RawTimes=RawTimes))
        else:
            print('The yvalue selection is incorrect, defaulted to pDFoFG')
            data_c = pd.DataFrame.from_dict(dict(DeltaTimes=DeltaTimes, pDFoFG=CoEfs, RawTimes=RawTimes))

        # print(data_c)

        data_c.insert(0, 'Protocol', protocol_data)
        data_c.insert(3, 'Stim Laser Power', laserpower_data)
        data_c.insert(4, 'Stim Frequency', frequency_data)
        data_c.insert(5, 'Stim nPulses', npulse_data)
        data_c.insert(6, 'Stim Pulse Width', pulsewidth_data)
        data_c.insert(7, 'Mouse', mouse_data)
        data_c.insert(8, 'Genotype', mutant_data)
        data_c.insert(9, 'Stim Type', stimtype_data)
        data_c.insert(10, 'Trial_i', comment_trial)
        data_c.insert(11, 'Round', round_data)
        data_c.insert(12, 'Sex', sex_data)
        data_c.insert(13, 'Week', week_data)
        data_c.insert(14, 'Day', day_data)
        data_c.insert(15, 'Phase', phase_data)
        data_c.insert(16, 'Plasticity Condition', plasticity_data)
        data_c.insert(17, 'Test Pulse Condition', test_pulse_data)

        # print(data_c)
        all_data.append(data_c)

    # print(all_data)
    all_data = pd.concat(all_data)
    # print (all_data)

    # NOTE: Need to force all integers to be strings, so they can be loaded into seaborn as categorial values instead of continuous
    all_data['Stim Laser Power'] = all_data['Stim Laser Power'].astype(str) + 'mW '
    all_data['Stim nPulses'] = all_data['Stim nPulses'].astype(str) + 'n'
    all_data['Stim Frequency'] = all_data['Stim Frequency'].astype(str) + 'Hz'

    return (all_data)


# %% ========================== COMBINE DATA - CALCULATE AVERAGE AND PEAKS =======================================================
def Combine_Comments_Photometry_Peaks_Average(yvalue, commentdata_all, photodata_all, mouse_list, week_list, day_list,
                                              protocol, filename, categories, timestamps_yes_or_no):
    """
    This definition combines photometry data and comment data and averages photometry data for all repeats of similar trials, in preparation for average peak graphs
    """
    all_data = []

    starttrial_index_tuple = np.where(
        (commentdata_all['stim_event'].str.contains('off_pre')) & commentdata_all['s_or_e_of_event'].str.contains(
            'end'))
    starttrial_index_array = starttrial_index_tuple[0]
    print(str(len(starttrial_index_array)) + ' trials in dataframe, now starting combining comments and photometry')

    i_percent = 0
    for trialindex in starttrial_index_array:
        percent = int((i_percent / len(starttrial_index_array)) * 1000)
        if percent % 100 == 0:
            print(str(percent / 10) + ' percent done')
        i_percent += 1

        comment_trial = commentdata_all.loc[trialindex, 'trial_inday']
        #            print ('trial is ' + str(trial) + 'and comment trial is ' + str(comment_verify))
        mouse_data = commentdata_all.loc[trialindex, 'mouse']
        protocol_data = commentdata_all.loc[trialindex, 'protocol']
        week_data = commentdata_all.loc[trialindex, 'week']
        day_data = commentdata_all.loc[trialindex, 'dayinweek']
        laserpower_data = commentdata_all.loc[trialindex, 'pulse_laserpower']
        frequency_data = commentdata_all.loc[trialindex, 'pulse_frequency']
        npulse_data = commentdata_all.loc[trialindex, 'pulse_n']
        stimtype_data = commentdata_all.loc[trialindex, 'stim_type']
        pulsewidth_data = commentdata_all.loc[trialindex, 'pulse_width']
        round_data = commentdata_all.loc[trialindex, 'round']
        sex_data = commentdata_all.loc[trialindex, 'sexmouse']
        mutant_data = commentdata_all.loc[trialindex, 'mutant_mouse']
        phase_data = commentdata_all.loc[trialindex, 'stim_type']
        plasticity_data = commentdata_all.loc[trialindex, 'plasticity_type']
        test_pulse_data = commentdata_all.loc[trialindex, 'test_pulse_type']

        event_indices = np.where(
            (photodata_all['data_i'] == comment_trial) &
            (photodata_all['protocol'] == protocol_data) &
            (photodata_all['mouse'] == mouse_data) &
            (photodata_all['day'] == day_data) &
            (photodata_all['week'] == week_data))[0]

        #        print(trial)
        #        print(comment_trial)
        #        print(event

        event = photodata_all.loc[event_indices, :]

        RawTimes = list(event['time'])
        CoEfs = list(event[yvalue])

        DeltaTimes = []
        for oldtime in range(len(RawTimes)):
            newtime = RawTimes[oldtime] - RawTimes[0]
            newtime_round = round(newtime, 1)
            # print(newtime)
            DeltaTimes.append(newtime_round)
        #            print(DeltaTimes)
        #            Time = DeltaTimes

        if yvalue == 'pDFoFG':
            data_c = pd.DataFrame.from_dict(dict(DeltaTimes=DeltaTimes, pDFoFG=CoEfs, RawTimes=RawTimes))
        elif yvalue == 'SNRG':
            data_c = pd.DataFrame.from_dict(dict(DeltaTimes=DeltaTimes, SNRG=CoEfs, RawTimes=RawTimes))
        elif yvalue == 'pDCoCG':
            data_c = pd.DataFrame.from_dict(dict(DeltaTimes=DeltaTimes, pDCoCG=CoEfs, RawTimes=RawTimes))
        else:
            print('The yvalue selection is incorrect, defaulted to pDFoFG')
            data_c = pd.DataFrame.from_dict(dict(DeltaTimes=DeltaTimes, pDFoFG=CoEfs, RawTimes=RawTimes))

        # print(data_c)

        data_c.insert(0, 'Protocol', protocol_data)
        data_c.insert(3, 'Stim Laser Power', laserpower_data)
        data_c.insert(4, 'Stim Frequency', frequency_data)
        data_c.insert(5, 'Stim nPulses', npulse_data)
        data_c.insert(6, 'Stim Pulse Width', pulsewidth_data)
        data_c.insert(7, 'Mouse', mouse_data)
        data_c.insert(8, 'Genotype', mutant_data)
        data_c.insert(9, 'Stim Type', stimtype_data)
        data_c.insert(10, 'Trial_i', comment_trial)
        data_c.insert(11, 'Round', round_data)
        data_c.insert(12, 'Sex', sex_data)
        data_c.insert(13, 'Week', week_data)
        data_c.insert(14, 'Day', day_data)
        data_c.insert(15, 'Phase', phase_data)
        data_c.insert(16, 'Plasticity Condition', plasticity_data)
        data_c.insert(17, 'Test Pulse Condition', test_pulse_data)

        # print(data_c)
        all_data.append(data_c)

    # print(all_data)
    all_data = pd.concat(all_data)
    # print (all_data)

    # NOTE: Need to force all integers to be strings, so they can be loaded into seaborn as categorial values instead of continuous
    all_data['Stim Laser Power'] = all_data['Stim Laser Power'].astype(str) + 'mW '
    all_data['Stim nPulses'] = all_data['Stim nPulses'].astype(str) + 'n'
    all_data['Stim Frequency'] = all_data['Stim Frequency'].astype(str) + 'Hz'

    ## This part makes averages:
    new_average_all_data = []

    all_data_whole = all_data

    stim_type_list = all_data['Stim Type'].unique()
    stim_TP_phase_list = all_data['Test Pulse Condition'].unique()
    stim_laser_power_list = all_data['Stim Laser Power'].unique()
    stim_frequency_list = all_data['Stim Frequency'].unique()
    stim_nPulses_list = all_data['Stim nPulses'].unique()

    for mouse in mouse_list:

        for week in week_list:

            for day in day_list:

                for stim_type in stim_type_list:

                    if stim_type == 'TP':

                        for stim_TP_phase in stim_TP_phase_list:

                            for stim_laser_power in stim_laser_power_list:

                                for stim_frequency in stim_frequency_list:

                                    for stim_nPulses in stim_nPulses_list:

                                        all_data1 = all_data_whole.loc[(all_data_whole['Mouse'] == mouse) &
                                                                       (all_data_whole['Week'] == week) &
                                                                       (all_data_whole['Day'] == day) &
                                                                       (all_data_whole['Stim Type'] == stim_type) &
                                                                       (all_data_whole[
                                                                            'Test Pulse Condition'] == stim_TP_phase) &
                                                                       (all_data_whole[
                                                                            'Stim Laser Power'] == stim_laser_power) &
                                                                       (all_data_whole[
                                                                            'Stim Frequency'] == stim_frequency) &
                                                                       (all_data_whole['Stim nPulses'] == stim_nPulses)]

                                        if len(all_data1) == 0:
                                            continue

                                        Time_list = all_data1['DeltaTimes'].unique()

                                        avg_list = []

                                        # average yvalues for all similar trials at each point in time
                                        for time_for_avg in Time_list:
                                            all_data2 = all_data1.loc[(all_data1['DeltaTimes'] == time_for_avg)]

                                            time_data = all_data2[yvalue].tolist()
                                            avg_at_time = statistics.mean(time_data)

                                            avg_list.append(avg_at_time)

                                        # Find peak in averaged yvalues
                                        trial_peak = max(avg_list)

                                        data_temp = pd.DataFrame()

                                        data_temp.insert(0, 'Protocol', all_data2['Protocol'].unique())
                                        data_temp.insert(1, 'Stim Laser Power', stim_laser_power)
                                        data_temp.insert(2, 'Stim Frequency', stim_frequency)
                                        data_temp.insert(3, 'Stim nPulses', stim_nPulses)
                                        data_temp.insert(4, 'Stim Pulse Width', all_data2['Stim Pulse Width'].unique())
                                        data_temp.insert(5, 'Mouse', mouse)
                                        data_temp.insert(6, 'Genotype', all_data2['Genotype'].unique())
                                        data_temp.insert(7, 'Stim Type', stim_type)
                                        data_temp.insert(8, 'Sex', all_data2['Sex'].unique())
                                        data_temp.insert(9, 'Week', week)
                                        data_temp.insert(10, 'Day', day)
                                        data_temp.insert(11, 'Phase', all_data2['Phase'].unique())
                                        data_temp.insert(12, 'Plasticity Condition',
                                                         all_data2['Plasticity Condition'].unique())
                                        data_temp.insert(13, 'Test Pulse Condition', stim_TP_phase)
                                        data_temp.insert(14, 'peak_dFoFG', trial_peak)

                                        new_average_all_data.append(data_temp)



                    else:
                        stim_TP_phase = 'NA'
                        # print(stim_type)
                        # print(stim_type_list)

                        for stim_laser_power in stim_laser_power_list:

                            for stim_frequency in stim_frequency_list:

                                for stim_nPulses in stim_nPulses_list:

                                    all_data1 = all_data_whole.loc[(all_data_whole['Mouse'] == mouse) &
                                                                   (all_data_whole['Week'] == week) &
                                                                   (all_data_whole['Day'] == day) &
                                                                   (all_data_whole['Stim Type'] == stim_type) &
                                                                   (all_data_whole[
                                                                        'Stim Laser Power'] == stim_laser_power) &
                                                                   (all_data_whole[
                                                                        'Stim Frequency'] == stim_frequency) &
                                                                   (all_data_whole['Stim nPulses'] == stim_nPulses)]

                                    if len(all_data1) == 0:
                                        continue

                                    Time_list = all_data1['DeltaTimes'].unique()

                                    avg_list = []

                                    # average yvalues for all similar trials at each point in time
                                    for time_for_avg in Time_list:
                                        all_data2 = all_data1.loc[(all_data1['DeltaTimes'] == time_for_avg)]

                                        time_data = all_data2[yvalue].tolist()
                                        avg_at_time = statistics.mean(time_data)

                                        avg_list.append(avg_at_time)

                                    # Find peak in averaged yvalues
                                    trial_peak = max(avg_list)

                                    data_temp = pd.DataFrame()

                                    data_temp.insert(0, 'Protocol', all_data2['Protocol'].unique())
                                    data_temp.insert(1, 'Stim Laser Power', stim_laser_power)
                                    data_temp.insert(2, 'Stim Frequency', stim_frequency)
                                    data_temp.insert(3, 'Stim nPulses', stim_nPulses)
                                    data_temp.insert(4, 'Stim Pulse Width', all_data2['Stim Pulse Width'].unique())
                                    data_temp.insert(5, 'Mouse', mouse)
                                    data_temp.insert(6, 'Genotype', all_data2['Genotype'].unique())
                                    data_temp.insert(7, 'Stim Type', stim_type)
                                    data_temp.insert(8, 'Sex', all_data2['Sex'].unique())
                                    data_temp.insert(9, 'Week', week)
                                    data_temp.insert(10, 'Day', day)
                                    data_temp.insert(11, 'Phase', all_data2['Phase'].unique())
                                    data_temp.insert(12, 'Plasticity Condition',
                                                     all_data2['Plasticity Condition'].unique())
                                    data_temp.insert(13, 'Test Pulse Condition', stim_TP_phase)
                                    data_temp.insert(14, 'peak_dFoFG', trial_peak)

                                    new_average_all_data.append(data_temp)

    new_average_all_data = pd.concat(new_average_all_data)

    return (new_average_all_data)


# %% ========================== Facet Line =======================================================
def facet_line(data, x='x', y='y', hue=None, col=None, row=None, hue_order=None, height=None, aspect=None, title=None,
               kind_of_plot=None, **kwargs):
    """
    This definition sets up face grid plots to better display multiple comparisons. It was originally written by Max.

    facet plot with shaded line. Catplot can't handle line
    :param data:         dataframe to plot
    :param x:       (optional) string, name of x axis variable
    :param y:       (optional) string, name of y axis variable
    :param hue:          (optional) string, hue variable
    :param col:          (optional) string, column variable
    :param row:          (optional) string, column variable
    :param kind_of_plot: (optional) default is shaded line
    :return:
    """

    #        hue_order = data[hue].unique()[::-1]
    # default is lineplot but can be anything - box, swarm, bar...
    if kind_of_plot is None:
        kind_of_plot = sns.lineplot
    # Set up facetgrid:
    g = sns.FacetGrid(data=data, hue=hue, col=col, row=row, hue_order=hue_order, palette='muted', height=height,
                      aspect=aspect, **kwargs)
    # plot:

    if kind_of_plot == sns.pointplot:
        g.map(kind_of_plot, x, y, ci=95, join=False, legend=False)
    else:
        g.map(kind_of_plot, x, y, ci=95)
    # (optional) get rid of the annoying "row_title = row_name"-style titles. Instead, show only row_name
    g.set_titles(row_template='{row_name}', col_template='{col_name}').add_legend()
    # plt.subplots_adjust(top=0.9)
    g.fig.suptitle(title, y=1.05)


#        labels = hue_order
#        colors=sns.color_palette("muted").as_hex()[:len(labels)]
#        handles=[patches.Patch(color=col, label=lab) for col, lab in zip(colors, labels)]

#        plt.legend(handles=handles, title=hue, loc='center left', bbox_to_anchor=(1,0.75))
#        plt.ylim(-20)


# %% ========================== GRAPH =======================================================
def PeakPlot(graph_type, all_data, yvalue, filename, categories, ymin, ymax, join_TF, pdf, xvalue, hue=None, col=None,
             row=None):
    """
    This definition has everything to make pointplots and factorplots with customizations and save them to a pdf
    """

    # ymax = 100
    # ymin = 0

    if graph_type == 'pointplot':
        ax1 = sns.pointplot(data=all_data, x=xvalue, y=yvalue, hue=hue, title=filename, ci=95, join=join_TF)
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.title(filename)
        plt.ylim(ymin, ymax)
        pdf.savefig(bbox_inches='tight')
        plt.close()

    elif graph_type == 'factorplot':
        g = sns.catplot(data=all_data, x=xvalue, y=yvalue, hue=hue, col=col, row=row, title=filename, ci=95, height=5,
                        aspect=1, kind='point', join=join_TF)
        #        plt.title(filename, y=1.05)
        g.fig.suptitle(filename, y=1.05)
        plt.ylim(ymin, ymax)
        pdf.savefig(bbox_inches='tight')
        plt.close()


# %% ========================== GRAPH =======================================================
def GraphPeaksAndSave(all_data, yvalue, filename, categories, ymin, ymax, mouse_list, fig_output_directory):
    """
    This definition graphs a bunch of peak plots (and average peak plots) based on the selected categories
    """

    if yvalue == 'pDFoFG':
        yvalue = 'peak_dFoFG'

    join_TF = 'True'

    filename_default = filename
    all_data_whole = all_data

    mouse_name = '_'
    for mouse in mouse_list:
        mouse_name = mouse + mouse_name

    #  If this is plasticity dataset, it will separate into test pulses and plasticity, and then graph the plasticity graphs
    if 'plasticity' in categories:

        # Graph plasticity vs TP

        #        PeakPlot(graph_type='pointplot', all_data=all_data, yvalue=yvalue, filename=filename, categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF ='True', xvalue='Stim nPulses', hue='Phase', col=None, row=None)

        # Split the data into plasticity and TP portions
        subset_plasticity = all_data.loc[(all_data['Phase'] == 'plasticity')]
        plasticity_status = subset_plasticity['Plasticity Condition'].unique()[0]

        all_data = all_data.loc[(all_data['Phase'] == 'TP')]

        filename = mouse_name + plasticity_status + '_' + filename_default
        pdf = PdfPages(fig_output_directory + filename + ".pdf")

        if 'day' in categories and 'week' in categories:
            PeakPlot(graph_type='pointplot', all_data=subset_plasticity, yvalue=yvalue,
                     filename=filename + ' - Plasticity', categories=categories, ymin=ymin, ymax=ymax, pdf=pdf,
                     join_TF='True', xvalue='Day', hue='Plasticity Condition', col=None, row=None)
            PeakPlot(graph_type='pointplot', all_data=subset_plasticity, yvalue=yvalue,
                     filename=filename + ' - Plasticity', categories=categories, ymin=ymin, ymax=ymax, pdf=pdf,
                     join_TF='True', xvalue='Week', hue='Plasticity Condition', col=None, row=None)
            PeakPlot(graph_type='factorplot', all_data=subset_plasticity, yvalue=yvalue,
                     filename=filename + ' - Plasticity', categories=categories, ymin=ymin, ymax=ymax, pdf=pdf,
                     join_TF='True', xvalue='Day', hue='Plasticity Condition', col='Week', row=None)

            PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename + ' - TP',
                     categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Day',
                     hue='Plasticity Condition', col=None, row='Stim nPulses')
            PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename + ' - TP',
                     categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Week',
                     hue='Plasticity Condition', col=None, row='Stim nPulses')
            PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename + ' - TP',
                     categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Day',
                     hue='Plasticity Condition', col='Week', row='Stim nPulses')

            PeakPlot(graph_type='pointplot', all_data=all_data, yvalue=yvalue, filename=filename + ' - TP',
                     categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim nPulses',
                     hue='Plasticity Condition', col=None, row=None)
            PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename + ' - TP',
                     categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim nPulses',
                     hue='Plasticity Condition', col='Day', row='Week')
            PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename + ' - TP',
                     categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim nPulses',
                     hue='Plasticity Condition', col='Week', row=None)

            if 'before_after' in categories:
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename + ' - TP',
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True',
                         xvalue='Test Pulse Condition', hue='Plasticity Condition', col='Week', row='Stim nPulses')
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename + ' - TP',
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True',
                         xvalue='Test Pulse Condition', hue='Plasticity Condition', col='Day', row='Stim nPulses')
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename + ' - TP',
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True',
                         xvalue='Test Pulse Condition', hue='Plasticity Condition', col=None, row='Stim nPulses')


        elif 'day' in categories:
            PeakPlot(graph_type='pointplot', all_data=subset_plasticity, yvalue=yvalue,
                     filename=filename + ' - Plasticity', categories=categories, ymin=ymin, ymax=ymax, pdf=pdf,
                     join_TF='True', xvalue='Day', hue='Plasticity Condition', col=None, row=None)
            PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename + ' - TP',
                     categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim nPulses',
                     hue='Plasticity Condition', col='Day', row=None)

            if 'before_after' in categories:
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename + ' - TP',
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True',
                         xvalue='Test Pulse Condition', hue='Plasticity Condition', col='Day', row='Stim nPulses')
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename + ' - TP',
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True',
                         xvalue='Test Pulse Condition', hue='Plasticity Condition', col=None, row='Stim nPulses')

        elif 'week' in categories:
            PeakPlot(graph_type='pointplot', all_data=subset_plasticity, yvalue=yvalue,
                     filename=filename + ' - Plasticity', categories=categories, ymin=ymin, ymax=ymax, pdf=pdf,
                     join_TF='True', xvalue='Week', hue='Plasticity Condition', col=None, row=None)
            PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename + ' - TP',
                     categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim nPulses',
                     hue='Plasticity Condition', col='Week', row=None)
            PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename + ' - TP',
                     categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim nPulses',
                     hue='Plasticity Condition', col='Week', row='Test Pulse Condition')

            if 'before_after' in categories:
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename + ' - TP',
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True',
                         xvalue='Test Pulse Condition', hue='Plasticity Condition', col='Week', row='Stim nPulses')
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename + ' - TP',
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True',
                         xvalue='Test Pulse Condition', hue='Plasticity Condition', col=None, row='Stim nPulses')

    else:
        filename = mouse_name + '_' + filename_default
        pdf = PdfPages(fig_output_directory + filename + ".pdf")

        # For week, split by frequnecy on different graphs and pulsenum with hue

        if 'day' in categories and 'week' in categories:
            PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                     categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim nPulses',
                     hue='Day', col=None, row=None)
            PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                     categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim nPulses',
                     hue='Week', col=None, row=None)
            PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                     categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim nPulses',
                     hue='Day', col='Week', row=None)
            PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                     categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Week',
                     hue='Stim nPulses', col=None, row=None)

            if 'pulsenum' in categories and 'frequency' in categories:
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim nPulses',
                         hue='Stim Frequency', col='Day', row='Week')
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim nPulses',
                         hue='Stim Frequency', col='Week', row=None)
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim Frequency',
                         hue='Stim nPulses', col='Day', row='Week')
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim Frequency',
                         hue='Stim nPulses', col='Week', row=None)
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Week',
                         hue='Stim nPulses', col='Stim Frequency', row=None)

            if 'pulsenum' in categories and 'laserpower' in categories:
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim nPulses',
                         hue='Stim Laser Power', col='Day', row='Week')
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim nPulses',
                         hue='Stim Laser Power', col='Week', row=None)
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True',
                         xvalue='Stim Laser Power', hue='Stim nPulses', col='Day', row='Week')
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True',
                         xvalue='Stim Laser Power', hue='Stim nPulses', col='Week', row=None)
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Week',
                         hue='Stim nPulses', col='Stim Laser Power', row=None)


        elif 'day' in categories:
            PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                     categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim nPulses',
                     hue='Day', col=None, row=None)
            # PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename, categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF ='True', xvalue='Stim nPulses', hue='Day', col='Week', row=None)

            if 'pulsenum' in categories and 'frequency' in categories:
                #                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename, categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF ='True', xvalue='Stim nPulses', hue='Stim Frequency', col='Day', row='Week')
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim nPulses',
                         hue='Stim Frequency', col='Day', row=None)
                # PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename, categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF ='True', xvalue='Stim Frequency', hue='Stim nPulses', col='Day', row='Week')
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim Frequency',
                         hue='Stim nPulses', col='Day', row=None)
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Day',
                         hue='Stim nPulses', col='Stim Frequency', row=None)

            if 'pulsenum' in categories and 'laserpower' in categories:
                # PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename, categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF ='True', xvalue='Stim nPulses', hue='Stim Laser Power', col='Day', row='Week')
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim nPulses',
                         hue='Stim Laser Power', col='Day', row=None)
                # PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename, categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF ='True', xvalue='Stim Laser Power', hue='Stim nPulses', col='Day', row='Week')
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True',
                         xvalue='Stim Laser Power', hue='Stim nPulses', col='Week', row=None)
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Day',
                         hue='Stim nPulses', col='Stim Laser Power', row=None)


        elif 'week' in categories:
            PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                     categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim nPulses',
                     hue='Week', col=None, row=None)

            if 'pulsenum' in categories and 'frequency' in categories:
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim nPulses',
                         hue='Stim Frequency', col='Week', row=None)
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim Frequency',
                         hue='Stim nPulses', col='Week', row=None)
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Week',
                         hue='Stim nPulses', col='Stim Frequency', row=None)

            if 'pulsenum' in categories and 'laserpower' in categories:
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim nPulses',
                         hue='Stim Laser Power', col='Week', row=None)
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True',
                         xvalue='Stim Laser Power', hue='Stim nPulses', col='Week', row=None)
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Week',
                         hue='Stim nPulses', col='Stim Laser Power', row=None)

        else:
            PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                     categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim nPulses',
                     hue='Stim Frequency', col=None, row=None)
            PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                     categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim Frequency',
                     hue='Stim nPulses', col=None, row=None)

            if 'mouse' in categories:
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim nPulses',
                         hue='Mouse', col='Stim Frequency', row=None)
                PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename,
                         categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF='True', xvalue='Stim Frequency',
                         hue='Mouse', col='Stim nPulses', row=None)

    #    if 'mouse' in categories:
    #        mouse_name = '_'
    #        for mouse in mouse_list:
    #            mouse_name = mouse + mouse_name
    #
    #        PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename, categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF ='True', xvalue='Stim nPulses', hue='Stim Frequency', col=None, row=None)
    #        PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename, categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF ='True', xvalue='Stim Frequency', hue='Stim nPulses', col=None, row=None)
    #
    #        PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename, categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF ='True', xvalue='Stim nPulses', hue='Mouse', col='Stim Frequency', row=None)
    #        PeakPlot(graph_type='factorplot', all_data=all_data, yvalue=yvalue, filename=filename, categories=categories, ymin=ymin, ymax=ymax, pdf=pdf, join_TF ='True', xvalue='Stim Frequency', hue='Mouse', col='Stim nPulses', row=None)

    pdf.close()


# %% ========================== GRAPH =======================================================
def GraphLineAndSave(all_data, yvalue, filename, categories, ymin, ymax, mouse_list, fig_output_directory):
    """
    This definition graphs a bunch of line plots based on the selected categories
    """
    filename_default = filename
    all_data_whole = all_data

    mouse_i = 1

    for mouse in mouse_list:
        all_data = all_data_whole.loc[(all_data_whole['Mouse'] == mouse)]
        print('starting mouse ' + str(mouse_i) + ' of ' + str(len(mouse_list)))

        #  If this is plasticity dataset, it will separate into test pulses and plasticity, and then graph the plasticity graphs
        if 'plasticity' in categories:
            plasticity_status = all_data.iloc[0, 16]

            filename = mouse + '_' + plasticity_status + '_' + filename_default
            pdf = PdfPages(fig_output_directory + filename + ".pdf")

            facet_line(x='DeltaTimes', y=yvalue, hue='Stim nPulses', row='Phase', data=all_data, title=filename,
                       height=5, aspect=1.3)
            pdf.savefig(bbox_inches='tight')
            plt.close()

            subset_plasticity = all_data.loc[(all_data['Phase'] == 'plasticity')]

            all_data = all_data.loc[(all_data['Phase'] == 'TP')]

            facet_line(x='DeltaTimes', y=yvalue, hue='Stim nPulses', col='Plasticity Condition', data=subset_plasticity,
                       title=filename, height=5, aspect=1.3)
            pdf.savefig(bbox_inches='tight')
            plt.close()

            facet_line(x='DeltaTimes', y=yvalue, hue='Stim nPulses', col='Plasticity Condition', data=all_data,
                       title=filename, height=5, aspect=1.3)
            pdf.savefig(bbox_inches='tight')
            plt.close()

            if 'day' in categories and 'week' in categories:
                facet_line(x='DeltaTimes', y=yvalue, hue='Stim nPulses', col='Day', row='Week', data=subset_plasticity,
                           title=filename, height=5, aspect=1.3)
                pdf.savefig(bbox_inches='tight')
                plt.close()

                facet_line(x='DeltaTimes', y=yvalue, hue='Stim nPulses', col='Week', data=subset_plasticity,
                           title=filename, height=5, aspect=1.3)
                pdf.savefig(bbox_inches='tight')
                plt.close()

            elif 'week' in categories:
                facet_line(x='DeltaTimes', y=yvalue, hue='Stim nPulses', col='Week', data=subset_plasticity,
                           title=filename, height=5, aspect=1.3)
                pdf.savefig(bbox_inches='tight')
                plt.close()
        else:
            filename = mouse + '_' + filename_default
            pdf = PdfPages(fig_output_directory + filename + ".pdf")

        # For IO and test pulses from Plasticity, graphs will be made based on category cues:

        if 'day' in categories and 'week' in categories:
            #            facet_line(x='DeltaTimes', y=yvalue, hue= 'Stim nPulses', col = 'Day', data=all_data, title=filename, height=5, aspect=1.3)
            #            pdf.savefig(bbox_inches='tight')
            facet_line(x='DeltaTimes', y=yvalue, hue='Stim nPulses', col='Day', row='Week', data=all_data,
                       title=filename, height=5, aspect=1.3)
            pdf.savefig(bbox_inches='tight')
            plt.close()
            facet_line(x='DeltaTimes', y=yvalue, hue='Stim nPulses', col='Week', data=all_data, title=filename,
                       height=5, aspect=1.3)
            pdf.savefig(bbox_inches='tight')
            plt.close()
            facet_line(x='DeltaTimes', y=yvalue, hue='Test Pulse Condition', col='Stim nPulses', row='Week',
                       data=all_data, title=filename, height=5, aspect=1.3)
            pdf.savefig(bbox_inches='tight')
            plt.close()

            if 'pulsenum' in categories and 'frequency' in categories:
                #                facet_line(x='DeltaTimes', y=yvalue, hue= 'Stim nPulses', col = 'Day', row = 'Stim Frequency', data=all_data, title=filename, height=5, aspect=1.3)
                #                pdf.savefig(bbox_inches='tight')
                facet_line(x='DeltaTimes', y=yvalue, hue='Stim nPulses', col='Week', row='Stim Frequency',
                           data=all_data, title=filename, height=5, aspect=1.3)
                pdf.savefig(bbox_inches='tight')
                plt.close()
                facet_line(x='DeltaTimes', y=yvalue, hue='Stim Frequency', col='Day', row='Week', data=all_data,
                           title=filename, height=5, aspect=1.3)
                pdf.savefig(bbox_inches='tight')
                plt.close()

            if 'pulsenum' in categories and 'laserpower' in categories:
                facet_line(x='DeltaTimes', y=yvalue, hue='Stim nPulses', col='Day', row='Stim Laser Power',
                           data=all_data, title=filename, height=5, aspect=1.3)
                pdf.savefig(bbox_inches='tight')
                plt.close()
                facet_line(x='DeltaTimes', y=yvalue, hue='Stim nPulses', col='Week', row='Stim Laser Power',
                           data=all_data, title=filename, height=5, aspect=1.3)
                pdf.savefig(bbox_inches='tight')
                plt.close()

        elif 'day' in categories:
            facet_line(x='DeltaTimes', y=yvalue, hue='Stim nPulses', col='Day', data=all_data, title=filename, height=5,
                       aspect=1.3)
            pdf.savefig(bbox_inches='tight')
            plt.close()

            if 'before_after' in categories:
                facet_line(x='DeltaTimes', y=yvalue, hue='Test Pulse Condition', col='Stim nPulses', row='day',
                           data=all_data, title=filename, height=5, aspect=1.3)
                pdf.savefig(bbox_inches='tight')
                plt.close()

            if 'pulsenum' in categories and 'frequency' in categories:
                facet_line(x='DeltaTimes', y=yvalue, hue='Stim nPulses', col='Stim Frequency', row='Day', data=all_data,
                           title=filename, height=5, aspect=1.3)
                pdf.savefig(bbox_inches='tight')
                plt.close()
                facet_line(x='DeltaTimes', y=yvalue, hue='Stim Frequency', col='Day', row='Stim nPulses', data=all_data,
                           title=filename, height=5, aspect=1.3)
                pdf.savefig(bbox_inches='tight')
                plt.close()

            if 'pulsenum' in categories and 'laserpower' in categories:
                facet_line(x='DeltaTimes', y=yvalue, hue='Stim nPulses', col='Day', row='Stim Laser Power',
                           data=all_data, title=filename, height=5, aspect=1.3)
                pdf.savefig(bbox_inches='tight')
                plt.close()

        elif 'week' in categories:
            facet_line(x='DeltaTimes', y=yvalue, hue='Stim nPulses', col='Week', data=all_data, title=filename,
                       height=5, aspect=1.3)
            pdf.savefig(bbox_inches='tight')
            plt.close()

            if 'pulsenum' in categories and 'frequency' in categories:
                facet_line(x='DeltaTimes', y=yvalue, hue='Stim nPulses', col='Week', row='Stim Frequency',
                           data=all_data, title=filename, height=5, aspect=1.3)
                pdf.savefig(bbox_inches='tight')
                plt.close()
                facet_line(x='DeltaTimes', y=yvalue, hue='Stim Frequency', col='Week', row='Stim nPulses',
                           data=all_data, title=filename, height=5, aspect=1.3)
                pdf.savefig(bbox_inches='tight')
                plt.close()

            if 'pulsenum' in categories and 'laserpower' in categories:
                facet_line(x='DeltaTimes', y=yvalue, hue='Stim nPulses', col='Week', row='Stim Laser Power',
                           data=all_data, title=filename, height=5, aspect=1.3)
                pdf.savefig(bbox_inches='tight')
                plt.close()

        else:  # No day or week comparison, all multiple recordings of the same protocol are pooled

            if 'pulsenum' in categories and 'frequency' in categories:
                facet_line(x='DeltaTimes', y=yvalue, hue='Stim nPulses', col='Stim Frequency', data=all_data,
                           title=filename, height=5, aspect=1.3)
                pdf.savefig(bbox_inches='tight')
                plt.close()
                facet_line(x='DeltaTimes', y=yvalue, hue='Stim Frequency', col='Stim nPulses', data=all_data,
                           title=filename, height=5, aspect=1.3)
                pdf.savefig(bbox_inches='tight')
                plt.close()

            if 'pulsenum' in categories and 'laserpower' in categories:
                facet_line(x='DeltaTimes', y=yvalue, hue='Stim nPulses', col='Stim Laser Power', data=all_data,
                           title=filename, height=5, aspect=1.3)
                pdf.savefig(bbox_inches='tight')
                plt.close()

            if 'pulsenum' in categories:
                facet_line(x='DeltaTimes', y=yvalue, hue='Stim nPulses', data=all_data, title=filename, height=5,
                           aspect=1.3)
                pdf.savefig(bbox_inches='tight')
                plt.close()

            if 'laserpower' in categories:
                facet_line(x='DeltaTimes', y=yvalue, hue='Stim Laser Power', row='Stim nPulses', data=all_data,
                           title=filename, height=5, aspect=1.3)
                pdf.savefig(bbox_inches='tight')
                plt.close()

            if 'frequency' in categories:
                facet_line(x='DeltaTimes', y=yvalue, hue='Stim Frequency', row='Stim nPulses', data=all_data,
                           title=filename, height=5, aspect=1.3)
                pdf.savefig(bbox_inches='tight')
                plt.close()

        print('done mouse ' + str(mouse_i) + ' of ' + str(len(mouse_list)))

        mouse_i += 1
        pdf.close()


# %% ========================== HEATMAP (can run with line graphs) =======================================================
def GraphHeatMap(all_data, yvalue, filename, categories, ymin, ymax, mouse_list, day_list, week_list):
    """
    This definition graphs a bunch of heatmaps based on the selected categories
    """
    filename_default = filename
    all_data_whole = all_data

    mouse_i = 0

    #    mouse = 'm356'
    #    week = 'w3'
    #    day = 'd1'

    for mouse in mouse_list:
        all_data1 = all_data_whole.loc[(all_data_whole['Mouse'] == mouse)]
        mouse_i += 1

        if 'plasticity' in categories:
            plasticity_status = all_data1.iloc[0, 16]
            filename = mouse + '_' + plasticity_status + '_' + filename_default
            pdf = PdfPages(fig_output_directory + filename + ".pdf")

        else:
            filename = mouse + '_' + filename_default
            pdf = PdfPages(fig_output_directory + filename + ".pdf")

        week_i = 0
        for week in week_list:
            all_data2 = all_data1.loc[(all_data1['Week'] == week)]
            week_i += 1
            #            print ('starting mouse ' + str(mouse_i) + ' of ' + str(len(mouse_list)) + ' and week ' + str(week_i) + ' of ' + str(len(week_list)))

            day_i = 0
            for day in day_list:
                all_data3 = all_data2.loc[(all_data2['Day'] == day)]
                day_i += 1

                if len(all_data3) == 0:
                    continue

                print('starting mouse ' + str(mouse_i) + ' of ' + str(len(mouse_list)) + ' and week ' + str(
                    week_i) + ' of ' + str(len(week_list)) + ' and day ' + str(day_i) + ' of ' + str(len(day_list)))
                print('starting mouse ' + str(mouse) + ' and week ' + str(week) + ' and day ' + str(day))

                #  If this is plasticity dataset, it will separate into test pulses and plasticity, and then graph the plasticity graphs
                if 'plasticity' in categories:
                    print('plasticity')
                    plasticity_status = all_data3.iloc[0, 16]

                    subset_plasticity = all_data3.loc[(all_data3['Phase'] == 'plasticity')]
                    subset_TP = all_data3.loc[(all_data3['Phase'] == 'TP')]
                    subset_TP_before = subset_TP.loc[(subset_TP['Test Pulse Condition'] == 'before')]
                    subset_TP_after = subset_TP.loc[(subset_TP['Test Pulse Condition'] == 'after')]

                    subset1a = pd.concat(
                        [subset_plasticity["DeltaTimes"], subset_plasticity["Trial_i"], subset_plasticity["pDFoFG"]],
                        axis=1)
                    subset1b = subset1a.pivot("Trial_i", "DeltaTimes", "pDFoFG")
                    ax1 = sns.heatmap(subset1b, linewidths=0.0, yticklabels=5, xticklabels=50, rasterized=True,
                                      vmin=-20, vmax=150)
                    plt.title(filename + '_Plasticity_' + week + ' ' + day)
                    #        plt.savefig("test.png", bbox_inches='tight', dpi=1000)
                    pdf.savefig(bbox_inches='tight')
                    plt.close()

                    print('TP')
                    subset1a = pd.concat([subset_TP["DeltaTimes"], subset_TP["Trial_i"], subset_TP["pDFoFG"]], axis=1)
                    subset1b = subset1a.pivot("Trial_i", "DeltaTimes", "pDFoFG")
                    ax2 = sns.heatmap(subset1b, linewidths=0.0, yticklabels=5, xticklabels=50, rasterized=True,
                                      vmin=-20, vmax=130)
                    plt.title(filename + '_TP_' + week + ' ' + day)
                    # plt.savefig("test.png", bbox_inches='tight', dpi=1000)
                    pdf.savefig(bbox_inches='tight')
                    plt.close()
                #
                #                    subset1a=pd.concat([subset_TP_before["DeltaTimes"], subset_TP_before["Trial_i"], subset_TP_before["pDFoFG"]], axis=1)
                #                    subset1b = subset1a.pivot("Trial_i","DeltaTimes", "pDFoFG")
                #                    ax2 = sns.heatmap(subset1b, linewidths=0.0, rasterized=True)
                #                    plt.title(filename + '_TP before_' + week + ' ' + day)
                #            #        plt.savefig("test.png", bbox_inches='tight', dpi=1000)
                #                    pdf.savefig(bbox_inches='tight')
                #                    plt.close()
                #
                #                    subset1a=pd.concat([subset_TP_after["DeltaTimes"], subset_TP_after["Trial_i"], subset_TP_after["pDFoFG"]], axis=1)
                #                    subset1b = subset1a.pivot("Trial_i","DeltaTimes", "pDFoFG")
                #                    ax3 = sns.heatmap(subset1b, linewidths=0.0, rasterized=True)
                #                    plt.title(filename + '_TP after_' + week + ' ' + day)
                #            #        plt.savefig("test.png", bbox_inches='tight', dpi=1000)
                #                    pdf.savefig(bbox_inches='tight')
                #                    plt.close()
                #
                else:
                    print('IO')

                    subset1a = pd.concat([all_data3["DeltaTimes"], all_data3["Trial_i"], all_data3["pDFoFG"]], axis=1)
                    subset1b = subset1a.pivot("Trial_i", "DeltaTimes", "pDFoFG")
                    ax2 = sns.heatmap(subset1b, linewidths=0.0, yticklabels=5, xticklabels=50, rasterized=True)
                    plt.title(filename + week + ' ' + day)
                    # plt.savefig("test.png", bbox_inches='tight', dpi=1000)
                    pdf.savefig(bbox_inches='tight')
                    plt.close()

        pdf.close()
