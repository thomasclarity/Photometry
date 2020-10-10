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
sns.set(style="darkgrid")
sns.set_context("poster")

#%% ========================== Face Line =======================================================
def facet_line(data, x='x', y='y', hue=None, col=None, row=None, height=None, aspect=None, title=None, kind_of_plot=None,  ylabeltext=None, **kwargs):
        """
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
        # default is lineplot but can be anything - box, swarm, bar...
        if kind_of_plot is None:
            kind_of_plot = sns.lineplot
        # Set up facetgrid:
        g = sns.FacetGrid(data=data, col=col, row=row, height=height, aspect=aspect)
        # plot:
        g.map(kind_of_plot, x, y, hue, ci= 95, **kwargs)#, ci=68
        # (optional) get rid of the annoying "row_title = row_name"-style titles. Instead, show only row_name
        g.set_titles(row_template='{row_name}', col_template='{col_name}').add_legend()
        
#        plt.subplots_adjust(top=0.9)
        g.fig.suptitle(title, y=1.05)
        
        g.map(plt.axvline, x=0, ls="--", c=".6")
        #g.map(plt.ylabel, '% dC/C G')
#        for ax in g.axes[0]:
#            ax1 = ax
#            ax1.plt.ylabel('% dC/C G')
#            ax1.axvline(ls="--", c=".6")
        #plt.ylim(-5,5)
        plt.ylabel('% dC/C G')
        g.add_legend()
        
        
#%% ========================== PEP AVERAGE GRAPH =======================================================
def combine_data(PEPcue, PEP_timeA, PEP_timeB, PEP_name, Time_Type, yvalue, commentdata_all, photodata_all, mouse_list, test_list, filename):
    """
    This definition combines photometry data and comment data
    """           
    if yvalue == 'pDCoCRatio':
        ylabeltext = 'percent dC/C ratio G/R'
        
    elif yvalue == 'zScorepDCoCRatio':
        ylabeltext = 'z-score dC/C ratio G/R'
        
    elif yvalue == 'pDCoCG':
        yvalue = 'downsample_coeffs'
        ylabeltext = 'pDCoCG'
#    PEPcue = '\nChoice'
#    PEP_timeA = 5
#    PEP_timeB = 5
#    PEP_name = ' '
#    Time_Type = 'DeltaTimes'
    
#    PEPevents_index = np.where(commentdata_all['event'] == PEPcue)[0]
        
    
    PEPevents_index = np.where(commentdata_all['event'].str.contains(PEPcue))[0]
    PEPtimestamps = list(commentdata_all.loc[PEPevents_index, 'timestamp'])
    all_data = []
    
    
    #print(PEPtimestamps)
    
    for PEPnum in range(0, len(PEPtimestamps),1):
        PEPtimestamp = PEPtimestamps[PEPnum]
        PEPindex = PEPevents_index[PEPnum]

        trial_PEP = commentdata_all.loc[PEPindex, 'trial']
        test_PEP = commentdata_all.loc[PEPindex, 'protocol']
        day_PEP = commentdata_all.loc[PEPindex, 'day']
        correct_PEP = commentdata_all.loc[PEPindex, 'result']
        phase_PEP = commentdata_all.loc[PEPindex, 'phase_broad']
        mouse_PEP = commentdata_all.loc[PEPindex, 'mouse']
        delay_PEP = commentdata_all.loc[PEPindex, 't_delay']
               
        if PEPcue == 'delay_start':
            
            if delay_PEP == '10 sec':
                PEP_timeA = 0
                PEP_timeB = 10
            elif delay_PEP == '30 sec':
                PEP_timeA = 0
                PEP_timeB = 30
            elif delay_PEP == '60 sec':
                PEP_timeA = 0
                PEP_timeB = 60
        event_indices = np.where(
                (photodata_all['total_time'] >= (PEPtimestamp - PEP_timeA)) &
                (photodata_all['total_time'] <= (PEPtimestamp + PEP_timeB)) & 
                (photodata_all['test'] == test_PEP) &
                (photodata_all['day'] == day_PEP ))[0]
        event = photodata_all.loc[event_indices,:]
        RawTimes = list(event['total_time'])
        CoEfs = list(event[yvalue]) 
        
        if Time_Type == 'DeltaTimes':            
            DeltaTimes = []    
            for oldtime in range(len(RawTimes)):
                newtime = RawTimes[oldtime] - PEPtimestamp
                #newtime_round = round(newtime,1)
                #print(newtime)
                #DeltaTimes.append(newtime_round)
                DeltaTimes.append(round(newtime,1))
#            print(DeltaTimes)
#            Time = DeltaTimes
            
                
        elif Time_Type == 'RawTimes':
            print('average requires DeltaTimes')
            
        else:
            print('!!!! incorrect Time_Type !!!! Try again with either "RawTimes" or "DeltaTimes"')
       
        
        data_c = pd.DataFrame.from_dict(dict(DeltaTimes = DeltaTimes, CoEfs = CoEfs))
        
        #print(data_c)

        
        data_c.insert(0,'PEPnum', PEPnum)
        data_c.insert(3,'result', correct_PEP)
        data_c.insert(4,'phase', phase_PEP)
        data_c.insert(5,'trial', trial_PEP)
        data_c.insert(6,'test', test_PEP)
        data_c.insert(7,'day', day_PEP)
        data_c.insert(8,'mouse', mouse_PEP)        
        data_c.insert(9,'PEPindex', PEPindex)
        data_c.insert(10,'PEPcue', PEPcue)
        data_c.insert(11,'delay', delay_PEP)
        #print(data_c)
        all_data.append(data_c)
        #print (all_data)
        
    #print(all_data)
    all_data = pd.concat(all_data)
    
    #print(len(all_data))

    all_data=all_data.rename({'CoEfs':ylabeltext},axis=1)

    return(all_data)
        
        
#%% ============================================= LOAD BLACKROCK =====================================================
def graph_PEPcue(PEPcue, PEP_timeA, PEP_timeB, PEP_name, Time_Type, yvalue, all_data, mouse_list, test_list, day_list, filename, categories, pdf, test):
    """
    This definition graphs peri-event period line plots
    """   
    
    if yvalue == 'pDCoCRatio':
        ylabeltext = 'percent dC/C ratio G/R'
        
    elif yvalue == 'zScorepDCoCRatio':
        ylabeltext = 'z-score dC/C ratio G/R'
        
    elif yvalue == 'pDCoCG':
        ylabeltext = '% dC/C G'
#    PEPcue = '\nChoice'
    
    if PEPcue == '\nChoice ':
        titlecue = "Choice selection"
    elif PEPcue == 'Choice ':
        titlecue = "Choice selection"
    elif PEPcue == 'sample_r':
        titlecue = 'Sample run'
    elif PEPcue == 'return_s':
        titlecue = "Sample selection"
    elif PEPcue == 'test_run':
        titlecue = "Choice run"
    else:
        titlecue = PEPcue
        
    title_final = PEP_name + ' ' + titlecue
    
    
    if 'sample vs choice' in categories:
        facet_line(x='DeltaTimes', y=yvalue, hue= 'PEPcue', data=all_data, title=title_final, height=5, aspect=1.3)
        pdf.savefig(bbox_inches='tight')

        facet_line(x='DeltaTimes', y=yvalue, hue= 'PEPcue', data=all_data, title=title_final, row='result', height=5, aspect=1.3)
        pdf.savefig(bbox_inches='tight')

        
#    facet_line(x='DeltaTimes', y=ylabeltext, hue= 'PEPcue', data=all_data, title=title_final, row='result', col='delay', height=5, aspect=1.3)
#    pdf.savefig(bbox_inches='tight')


#    facet_line(x='DeltaTimes', y=ylabeltext, hue= 'result', data=all_data, title=title_final, row='PEPcue', col='delay', height=5, aspect=1.3)
#    pdf.savefig(bbox_inches='tight')    
    
    
    
    
    elif 'cue' in categories:
        if test == 'test':
            facet_line(x='DeltaTimes', y=yvalue, hue= 'result', data=all_data, title=title_final, hue_order= ('Correct', 'Incorrect'), height=5, aspect=1.3)
            plt.axvline(ls="--", c=".6")
            pdf.savefig(bbox_inches='tight')
            
            if 'mouse' in categories and 'day' in categories:
                facet_line(x='DeltaTimes', y=yvalue, hue= 'result', data=all_data, title=title_final, col='day', row= 'mouse', hue_order= ('Correct', 'Incorrect'), height=5, aspect=1.3)
                plt.axvline(ls="--", c=".6")
                pdf.savefig(bbox_inches='tight')
                
            elif 'day' in categories:
                facet_line(x='DeltaTimes', y=yvalue, hue= 'result', data=all_data, title=title_final, col='day', hue_order= ('Correct', 'Incorrect'), height=5, aspect=1.3)
                plt.axvline(ls="--", c=".6")
                pdf.savefig(bbox_inches='tight')
            
            elif 'mouse' in categories:
                facet_line(x='DeltaTimes', y=yvalue, hue= 'result', data=all_data, title=title_final, row= 'mouse', hue_order= ('Correct', 'Incorrect'), height=5, aspect=1.3)
                plt.axvline(ls="--", c=".6")
                pdf.savefig(bbox_inches='tight')
            
            if 'phase' in categories:
                facet_line(x='DeltaTimes', y=yvalue, hue= 'phase', data=all_data, title=title_final, col = 'result', row= 'mouse', height=5, aspect=1.3)
                plt.axvline(ls="--", c=".6")
                pdf.savefig(bbox_inches='tight')
                
                

            
        elif test == 'train':
            facet_line(x='DeltaTimes', y=yvalue, hue= 'result', data=all_data, title=title_final, col='day', hue_order= ('Correct', 'Incorrect'), height=5, aspect=1.3)
            plt.axvline(ls="--", c=".6")
            pdf.savefig(bbox_inches='tight')
            
            if 'mouse' in categories:
                facet_line(x='DeltaTimes', y=yvalue, hue= 'result', data=all_data, title=title_final, col='day', row= 'mouse', hue_order= ('Correct', 'Incorrect'), height=5, aspect=1.3)
                plt.axvline(ls="--", c=".6")
                pdf.savefig(bbox_inches='tight')
        
    #pdf.savefig(bbox_inches='tight')
    
#    facet_line(x='DeltaTimes', y=ylabeltext, hue= 'delay', data=all_data, title=title_final, row='PEPcue', col = 'result', height=5, aspect=1.3)
#    pdf.savefig(bbox_inches='tight')
#    facet_line(x='DeltaTimes', y=ylabeltext, hue= 'mouse', data=graph, title=title_final, col='delay', height=5, aspect=1.3)
#    pdf.savefig(bbox_inches='tight')
#
#    facet_line(x='DeltaTimes', y=ylabeltext, hue= 'result', data=all_data, title=title_final, col = 'delay', row='mouse', hue_order= ('correct', 'incorrect'), height=5, aspect=1.3)
#    pdf.savefig(bbox_inches='tight')
    
#%% ============================================= LOAD COMMENTS =====================================================
def load_comment_data(mouse, test, day, fpath, file):
    """
    This definition loads processed comment files
    """
        
#    mouse = 'm189'
#    test = 'train7'
#    fpath = "C:\\Users\\mikofskyrm\\Desktop\\Photometry\\Data"
#    file = 'm189_train7'
#    
    file1 = glob(f'{fpath}/commentdataNEW*{mouse}*{test}*{day}.csv')

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
    
    tempdata1 = tempdata1.rename({'correct_status': 'result'}, axis=1) 
    tempdata1 = tempdata1.rename({'tmaze_phase': 'phase_specific'}, axis=1)      

    

    return tempdata1

#%% ============================================= LOAD PHOTOMETRY =====================================================
def load_photometry_data(mouse, test, day, fpath, file):
    """
    This definition loads processed comment files
    """
#    mouse = 'm189'
#    test = 'train3'
#    fpath = "C:\\Users\\mikofskyrm\\Desktop\\Photometry\\Data"
#    file2 = 'm189_train3'
    
    
    photofile = glob(f'{fpath}/photodata*{file}.csv')
    if len(photofile) > 1:
        print('error there is more than one photometry file starting with ' + fpath +  '/' + file)
        return
    elif len(photofile) < 1:
        print('error, no photometry file exists for ' + fpath + '/' + file)
        return 
    else: 
        fid2 = str(glob(f'{fpath}/photodata*{file}.csv')[0])
        print(fid2) 
        
    photometry_temp = pd.read_csv(fid2)
    photometry_temp['day'] = 'd' + photometry_temp['day'].astype(str)
    
#    print(photometry_temp)
    return photometry_temp

#%% ============================================= LOAD PHOTOMETRY =====================================================
def averaging(categories, cue, yvalue, all_data, mouse, test, pre_or_post):
    """
    For a given cue and time window, this definition averages all similar trials, then within that time window calculates the mean or max
    """    
    
    print('averaging'+ ' ' + mouse + ' ' +cue+ ' ' +pre_or_post)
    if pre_or_post == 'pre':
        if cue == 'delay_start':
            time_a = 0
            time_b = 2
        else:    
            time_a = -2
            time_b = -1
    elif pre_or_post == 'post':
        if cue == 'delay_start':
            time_a = 8
            time_b = 10
        else:    
            time_a = 1
            time_b = 2
    
    new_average_data = []
    print('making subsets')
    
    subset1a = all_data.loc[(all_data['PEPcue'] == cue)]
    
    subset2a = subset1a.loc[(subset1a['DeltaTimes'] >= time_a) & (subset1a['DeltaTimes'] <= time_b)]
    
    subset3c = subset2a.loc[(subset2a['result'] == 'Correct')]
    
    subset3i = subset2a.loc[(subset2a['result'] == 'Incorrect')]
    
    time_list_c = subset3c['DeltaTimes'].unique()
    time_list_i = subset3i['DeltaTimes'].unique()
    time_list_b = subset2a['DeltaTimes'].unique()
    
    #print(subset1a['phase'].unique())
    phase = subset1a['phase'].unique()[0]
    
    
    
    #Find averages of correct
    if subset3c.empty:
        print('there are no correct trials, skipping')
    elif not subset3c.empty:
        avg_list = []
        data_temp = pd.DataFrame()
        print('averaging corrects')
        for time_for_avg in time_list_c:
            
            process_data = subset3c.loc[(subset3c['DeltaTimes'] == time_for_avg)]
            
            time_data = process_data[yvalue].tolist()
            avg_at_time = statistics.mean(time_data)
            
            avg_list.append(avg_at_time)
            #print(avg_at_time)
    
        #Find peak in averaged yvalues
        if 'max' in categories:
            c_trial_peak = max(avg_list)
        if 'mean' in categories:
            c_trial_peak = statistics.mean(avg_list)
        
        data_temp = pd.DataFrame(columns=['mouse', 'test', 'cue', 'phase', 'result', 'period', 'peak_pDCoCG'])    
        data_temp = data_temp.append({'mouse' : mouse, 'test' : test,  'cue':cue, 'phase':phase, 'result': 'correct', 'period':pre_or_post, 'peak_pDCoCG': c_trial_peak}, ignore_index=True)
        
        new_average_data.append(data_temp)
    
       
    
    
    #Find averages of incorrect
    if subset3i.empty:
        print('there are no incorrect trials, skipping')
    elif not subset3i.empty:
        avg_list = []
        data_temp = pd.DataFrame()
        print('averaging incorrects')
        for time_for_avg in time_list_i:
            
            process_data = subset3i.loc[(subset3i['DeltaTimes'] == time_for_avg)]
            
            time_data = process_data[yvalue].tolist()
            avg_at_time = statistics.mean(time_data)
            
            avg_list.append(avg_at_time)
    
        #Find peak in averaged yvalues
        if 'max' in categories:
            i_trial_peak = max(avg_list)
        if 'mean' in categories:
            i_trial_peak = statistics.mean(avg_list)
        
        data_temp = pd.DataFrame(columns=['mouse', 'test', 'cue', 'phase', 'result', 'period', 'peak_pDCoCG'])    
        data_temp = data_temp.append({'mouse' : mouse, 'test' : test,  'cue':cue, 'phase':phase, 'result': 'incorrect', 'period':pre_or_post, 'peak_pDCoCG': i_trial_peak}, ignore_index=True)
        new_average_data.append(data_temp)   
    
    
    #Find averages of incorrect/correct together
    avg_list = []
    data_temp = pd.DataFrame()
    for time_for_avg in time_list_b:
        
        process_data = subset2a.loc[(subset2a['DeltaTimes'] == time_for_avg)]
        
        time_data = process_data[yvalue].tolist()
        avg_at_time = statistics.mean(time_data)
        
        avg_list.append(avg_at_time)

    #Find peak in averaged yvalues
    if 'max' in categories:
        b_trial_peak = max(avg_list)
    if 'mean' in categories:
        b_trial_peak = statistics.mean(avg_list)
        print('for cue ' + str(cue) + ' ' + str(pre_or_post) + ' start time ' + str(time_a) + ' end time ' + str(time_b) + ' mean of avg for all corr&incorr trials is ' +  str(b_trial_peak) )
        #print(avg_list)
        
    data_temp = pd.DataFrame(columns=['mouse', 'test', 'cue', 'phase', 'result', 'period', 'peak_pDCoCG'])    
    data_temp = data_temp.append({'mouse' : mouse, 'test' : test,  'cue':cue, 'phase':phase, 'result': 'both', 'period':pre_or_post, 'peak_pDCoCG': b_trial_peak}, ignore_index=True)
    new_average_data.append(data_temp)    
    


    
    #print(new_average_data)
    
    return new_average_data

