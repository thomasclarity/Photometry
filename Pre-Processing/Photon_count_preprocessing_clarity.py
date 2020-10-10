# Inputs Oceanview output text files whose timestamp column has been adjusted to contain...
# ...numbers with no decimal places and saved as CSV
# Creates new "TRIM" CSV that lacks header and is compatible with Spectral Unmixing R Code
# Graphs photon counts across different wavelengths
# Graphs photon counts within different wavelength bands across time
# Generates excel output file required for next step in data analysis/visualization pipeline

#%%

# import relevant modules
import os
import pandas as pd
from matplotlib import pyplot as plt
# or import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib import rcParams
import numpy as np
from scipy.optimize import curve_fit
import glob
#import matplotlib.mlab as mlab
#from scipy import optimize, polyfit
#from scipy.optimize import minimize
#from mdgpy.optimize import fsolve

# specify graph style features
style.use('seaborn-poster')
rcParams.update({'figure.autolayout': True})
#rcParams.update({'font.size':34})

# set directory of folder containing only CSV files to be pre-processed
#os.chdir('/Volumes/DK_backup_drive/vHPC_PFC_plasticity_preprocessing/NEW_CSV_data_files')       
os.chdir('/Users/clarityt2/Documents/Gordon Lab/Photometry Preprocessing/CSV Preprocessed')


# call all CSVs in folder, renaming certain titles to have fewer characters
# could also say "for file in glob.glob('m*.csv'):" ?
for file in list(glob.glob('m*.csv')): 
       
    sep = '_Subt'
    titleName = file.rsplit(sep, 1)[0]
    # I think the [0] gets rid of the string that is split to the right
    
    basePlasticity = "basePlasticity"
    if basePlasticity in titleName:
        titleName = titleName.replace("basePlasticity", "base")
       
    baseIO = "baseIO"
    if baseIO in titleName:
        titleName = titleName.replace("baseIO", "base")
         
    # set directories for writing folders
    #writeFoldFig = '/Volumes/DK_backup_drive/vHPC_PFC_plasticity_preprocessing/Saved_figures'
    #writeFoldData = '/Volumes/DK_backup_drive/vHPC_PFC_plasticity_preprocessing/Saved_excel_output'    
    writeFoldFig = '/Users/clarityt2/Documents/Gordon Lab/Photometry Preprocessing/Preprocessing Output'
    writeFoldData = '/Users/clarityt2/Documents/Gordon Lab/Photometry Preprocessing/Preprocessing Output'
    
    # read CSV for raw data output
    rawOutput = pd.read_csv(file)
    
    # trim header off of raw output file (PC iloc requires different ranges)
    trimOutput = rawOutput.iloc[13:,1:]
    
    # write trimmed CSV to folder (TRIM file required for spectral unmixing step in R)
    # index and header = false removes the axis labels
    trimOutputCSV = trimOutput.to_csv(('TRIM_' + file), index = False, header = False)

    # read CSV of trimmed output
    # header = none indicates there are no column labels so panda should make some up and not use the top row
    trimInput = pd.read_csv(('TRIM_' + file), header = None)

    #%%

    # create dataframes of green and red photon count ranges
    # modify first range pcG, pcR and pcRelev to select the time window to analyze
    # note iloc is exclusive of high end of range. Default is [1:,#:#)]
    # modify second range of pcG & freqValG, pcR & freqValR, or pcRelev & freqValRelev to modify frequency ranges
    # default values: Green 197:251, Red 297:351, Relev 132:527
    # if red values are low, replace red range values with green range values to prevent issues stemming from negative values
    
    pcG = trimInput.iloc[1:, 197:251]  
    pcColMeanG = pcG.mean(axis = 0)         # axis = 0 takes the mean down the columns; axis = 1 mean of rows
    freqValG = trimInput.iloc[0, 197:251]

    # 197:251 refers to column numbers not wavelengths
    
    pcR = trimInput.iloc[1:, 297:351] #default 297:351 for dual-filter setup 
    pcColMeanR = pcR.mean(axis = 0)
    freqValR = trimInput.iloc[0, 297:351] #default 297:351 for dual-filter setup
    
    pcRelev = trimInput.iloc[1:, 132:527]
    pcColMeanRelev = pcRelev.mean(axis = 0)
    freqValRelev = trimInput.iloc[0, 132:527]
    
    # plot photon counts vs wavelength, separated into green, red and overall components
    fig1, ax1 = plt.subplots()
    ax1.plot(freqValRelev, pcColMeanRelev, label = 'Overall', color = 'grey')
    ax1.plot(freqValG, pcColMeanG, label = 'GCaMP', color = 'green')
    ax1.plot(freqValR, pcColMeanR, label = 'TdTomato', color = 'red')
    ax1.set_xlabel('Wavelength (nm)', size=20)
    ax1.set_ylabel('Photon Count', size=20)
    ax1.set_title(titleName, size=20)
    ax1.legend(loc = 'upper right', prop = dict(size=16))
    ax1.tick_params(axis='x', labelsize=16)
    ax1.tick_params(axis='y', labelsize=16)
    plt.savefig(os.path.join(writeFoldFig, titleName + ' Spectrum Photon Count 450-750nm w G and R overlay.pdf'))

    #%%
    
    # create dataframe with timestamps of selected data
    timestamps_raw = trimInput.iloc[1:,:1]
    # zero timestamps and convert from ms to seconds
    # divides timestamp by the first time value (1562692237070) then divides by 1000
    timestamps_zero_sec = ((timestamps_raw - timestamps_raw.iloc[0,0])/1000)
    # convert timestamps to a flattened array (needed for subsequent linear regression)
    timestamps_zero_sec_array = timestamps_zero_sec.values.flatten()

    # summed photon counts across wavelengths, separated into green and red, and their ratio
    pcRowSumG = pcG.sum(axis = 1)
    pcRowSumR = pcR.sum(axis = 1)
    # ratioGRrowSum = greenPCrowSum/redPCrowSum
    
    # plot photon counts vs time, separated into green and red components
    fig2, ax2 = plt.subplots()
    ax2.plot(timestamps_zero_sec, pcRowSumG, label = 'GCaMP', color = 'green')
    ax2.plot(timestamps_zero_sec, pcRowSumR, label = 'TdTomato', color = 'red')
    ax2.set_xlabel('Time (sec)', size=20)
    ax2.set_ylabel('Photon Count', size=20)
    ax2.set_title(titleName, fontsize=20)
    ax2.tick_params(axis='x', labelsize=16)
    ax2.tick_params(axis='y', labelsize=16)
    ax2.legend(prop= dict(size=16))
    #ax2.set_xlim(0,200)
    #ax2.set_ylim(0,30000)
    plt.savefig(os.path.join(writeFoldFig, titleName + ' Photon Count vs Time G and R.pdf'))
    
    #%%

    # perform linear regression on G and R photon counts to correct for within-session bleaching
    def LRgreen(x, m, b):
        return m * timestamps_zero_sec_array + b 
    poptG, pcovG = curve_fit(LRgreen, timestamps_zero_sec_array, pcRowSumG, bounds = ([-np.inf, -np.inf], [0,np.inf]))
    LRpcG = LRgreen(timestamps_zero_sec_array, *poptG)
    
    def LRred(x, m, b):
        return m * timestamps_zero_sec_array + b 
    poptR, pcovR = curve_fit(LRred, timestamps_zero_sec_array, pcRowSumR, bounds = ([-np.inf, -np.inf], [0,np.inf]))
    LRpcR = LRred(timestamps_zero_sec_array, *poptR)
    # [m1,b1], [x=m2 b2]; don't want x > 0 because you the slope should not be positive
    # function(x, *popt) is a simpler way to call to the function with the best fit parameters

    # plot result of linear regression with G and R photon counts vs time
    fig3, ([ax4, ax5]) = plt.subplots (2,1,figsize = (10,6))
    ax4.set_title(titleName, size = 20)
    ax4.plot(timestamps_zero_sec, pcRowSumG, label = 'GCaMP', color = 'green')
    ax4.plot(timestamps_zero_sec, LRpcG, label = 'Lin Reg', color = 'yellow')
    ax4.set_ylabel('Photon Count', size=20)
    ax4.tick_params(axis='x', labelsize=16)
    ax4.tick_params(axis='y', labelsize=16)
    ax4.legend(loc = 'upper right', prop = dict(size=16))
    #ax4.set_xlim(2000,2200)
    #ax4.set_ylim(0,30000)
    ax5.plot(timestamps_zero_sec, pcRowSumR, label = 'TdTomato', color = 'red')
    ax5.plot(timestamps_zero_sec, LRpcR, label = 'Lin Reg', color = 'yellow')
    ax5.set_xlabel('Time (sec)', size=20)
    ax5.set_ylabel('Photon Count', size=20)
    ax5.tick_params(axis='x', labelsize=16)
    ax5.tick_params(axis='y', labelsize=16)
    ax5.legend(loc = 'upper right', prop = dict(size=16))
    #ax5.set_xlim(2000,2200)
    #ax5.set_ylim(0,30000)
    plt.savefig(os.path.join(writeFoldFig, titleName + ' Lin Reg Photon Counts G and R.pdf'))


#%%
    # correct G and R photon counts using linear regression
    # create dataframe from LRpcG/R and divide the first value by each value to get a correction value for each timepoint
    # multiply the G and R photon counts by their correction factors
    # pcRowSum was indexed to 1, needed to reset index to 0 to properly multiply the two columns
    LRpcG_df = pd.DataFrame(LRpcG)
    LRcorrFactorG = LRpcG_df.iloc[0,0] / LRpcG_df
    LRcorrectionG_df = pd.concat([pcRowSumG.reset_index(),LRcorrFactorG], axis=1)
        # Had to reset index because the first number in the rows was assigned "1" not "0" so to properly multiply each
        # photon sum by its respective coefficient you needed to index
    LRCpcG = (LRcorrectionG_df.iloc[:,1]) * (LRcorrectionG_df.iloc[:,2])

    LRpcR_df = pd.DataFrame(LRpcR)
    LRcorrFactorR = LRpcR_df.iloc[0,0] / LRpcR_df
    LRcorrectionR_df = pd.concat([pcRowSumR.reset_index(),LRcorrFactorR], axis=1)
    LRCpcR = (LRcorrectionR_df.iloc[:,1]) * (LRcorrectionR_df.iloc[:,2])
    
    # plot corrected coefficients
    fig4, ([ax6, ax7]) = plt.subplots(2,1,figsize = (10,6))
    ax6.set_title(titleName, size = 20)
    ax6.plot(timestamps_zero_sec, pcRowSumG, label = 'GCaMP', color = 'green')
    ax6.plot(timestamps_zero_sec, LRCpcG, label = 'LRC GCaMP', color = 'yellow')
    ax6.set_ylabel('Photon Count', size=20)
    ax6.tick_params(axis='x', labelsize=16)
    ax6.tick_params(axis='y', labelsize=16)
    ax6.legend(loc = 'upper right', prop = dict(size=16))
    #ax6.set_xlim(2000,2200)
    #ax6.set_ylim(0,30000)
    ax7.plot(timestamps_zero_sec, pcRowSumR, label = 'TdTomato', color = 'red')
    ax7.plot(timestamps_zero_sec, LRCpcR, label = 'LRC TdTomato', color = 'yellow')
    ax7.set_xlabel('Time (sec)', size=20)
    ax7.set_ylabel('Photon Count', size=20)
    ax7.tick_params(axis='x', labelsize=16)
    ax7.tick_params(axis='y', labelsize=16)
    ax7.legend(loc = 'upper right', prop = dict(size=16))
    #ax7.set_xlim(2000,2200)
    #ax7.set_ylim(0,30000)
    #plt.subplots_adjust(left = 0.1, bottom = 0.1)
    plt.savefig(os.path.join(writeFoldFig, titleName + ' Lin Reg-Corrected Photon Counts G and R.pdf'))

#%%

    # calculate G:R Ratio coefficient from LRC coefficients 
    pcRatio = LRCpcG / LRCpcR
    
    # perform linear regression on G:R ratio (constrained to slope = 0)
    def LRratio(x, m, b):
        return m * timestamps_zero_sec_array + b 
    poptGR, pcovGR = curve_fit(LRratio, timestamps_zero_sec_array, pcRatio, bounds = ([-1e-20, -np.inf], [0, np.inf]))
    LRpcRatio = LRratio(timestamps_zero_sec_array, *poptGR)
    
    # plot ratio coefficient and lin regression result
    fig5, ax8 = plt.subplots()
    ax8.plot(timestamps_zero_sec, pcRatio, label = 'GCaMP:TdTomato', color = 'purple')
    ax8.plot(timestamps_zero_sec, LRpcRatio, label = 'Lin Reg', color = 'yellow')
    ax8.set_xlabel('Time (sec)', size=20)
    ax8.set_ylabel('Photon Count Ratio', size=20)
    ax8.set_title(titleName, size=20)
    ax8.tick_params(axis='x', labelsize=16)
    ax8.tick_params(axis='y', labelsize=16)
    ax8.legend(loc = 'upper right', prop = dict(size=16))
    #ax8.set_xlim(2000,2200)
    #ax8.set_ylim(0,2)
    plt.savefig(os.path.join(writeFoldFig, titleName + ' Lin Reg Photon Counts GR-Ratio.pdf'))

#%%
    
    # calculate and plot %dFoF for G, R and Ratio from linear regressions
    # why don't you do LRCpcG - LRpcG ? why don't you correct for photobleaching then calculate %dfof ?
    pDFoFG = (pcRowSumG - LRpcG) / LRpcG * 100
    pDFoFR = (pcRowSumR - LRpcR) / LRpcR * 100
    pDFoFRatio = (pcRatio - LRpcRatio) / LRpcRatio * 100
    
    # plot %dFoF for G, R and Ratio
    fig6, ax9 = plt.subplots()
    ax9.plot(timestamps_zero_sec, pDFoFG, label = 'GCaMP', color = 'green')
    ax9.plot(timestamps_zero_sec, pDFoFR, label = 'TdTomato', color = 'red')
    #ax9.plot(timestamps_zero_sec, pDFoFRatio, label = 'GCaMP:TdTomato', color = 'purple')
    ax9.set_xlabel('Time (sec)', size=20)
    ax9.set_ylabel('% Delta F/F', size=20)
    ax9.set_title(titleName, size=20)
    ax9.tick_params(axis='x', labelsize=16)
    ax9.tick_params(axis='y', labelsize=16)
    ax9.legend(loc = 'upper right', prop = dict(size=16))
    #ax9.set_xlim(0,1000)
    #ax9.set_ylim(-100,250)
    plt.savefig(os.path.join(writeFoldFig, titleName + ' Photon Counts dFoF vs Time G R and Ratio.pdf'))
    
    #%%

    # calculate Z-scores from %dF/F for green and red components and their ratio
    meanpDFoFG = pDFoFG.mean()
    meanpDFoFR = pDFoFR.mean()
    meanpDFoFRatio = pDFoFRatio.mean()
    stdpDFoFG = pDFoFG.std()
    stdpDFoFR = pDFoFR.std()
    stdpDFoFRatio = pDFoFRatio.std()
    
    zScorepDFoFG = (pDFoFG-meanpDFoFG)/stdpDFoFG
    zScorepDFoFR = (pDFoFR-meanpDFoFR)/stdpDFoFR
    zScorepDFoFRatio = (pDFoFRatio-meanpDFoFRatio)/stdpDFoFRatio
    
    # plot Z-scores from %dF/F for green and red components and their ratio
    fig7, ax10 = plt.subplots()
    ax10.plot(timestamps_zero_sec, zScorepDFoFG, label = 'GCaMP', color = 'green')
    ax10.plot(timestamps_zero_sec, zScorepDFoFR, label = 'TdTomato', color = 'red')
    #ax10.plot(timestamps_zero_sec, zScorepDFoFRatio, label = 'GCaMP:TdTomato', color = 'purple')
    ax10.set_xlabel('Time (sec)', size=20)
    ax10.set_ylabel('Z-Score (from %dF/F)', size=20)
    ax10.set_title(titleName, size=20)
    ax10.legend(loc = 'upper right', prop = dict(size=16))
    ax10.tick_params(axis='x', labelsize=16)
    ax10.tick_params(axis='y', labelsize=16)            
    #ax10.set_xlim(0,1000)
    #ax10.set_ylim(-100,250)
    plt.savefig(os.path.join(writeFoldFig, titleName + ' Photon Counts Z-Scores vs Time G R and Ratio.pdf'))
    
    #%%

    # converting variables to dataframes for excel output
    # columns =... is replacing first row with title?
    # changed rename 0 to Unnamed: 1

    timestamps_raw_df = timestamps_raw.rename(columns = {'Unnamed: 1':'timestampRaw'})
    timestamps_zero_sec_df = timestamps_zero_sec.rename(columns = {'Unnamed: 1':'timestampZeroSec'})
    pcRowSumG_df = pd.DataFrame({'pcRowSumG': pcRowSumG})
    pcRowSumR_df = pd.DataFrame({'pcRowSumR': pcRowSumR})
    LRpcG_df = pd.DataFrame({'LRpcG': LRpcG})
    LRpcR_df = pd.DataFrame({'LRpcR': LRpcR})
    LRCpcG_df = pd.DataFrame({'LRCpcG': LRCpcG})
    LRCpcR_df = pd.DataFrame({'LRCpcR': LRCpcR})
    pcRatio_df = pd.DataFrame({'pcRatio': pcRatio})
    LRpcRatio_df = pd.DataFrame({'LRpcRatio': LRpcRatio})
    pDFoFG_df = pd.DataFrame({'pDFoFG': pDFoFG})
    pDFoFR_df = pd.DataFrame({'pDFoFR': pDFoFR})
    pDFoFRatio_df = pd.DataFrame({'pDFoFRatio': pDFoFRatio})
    zScorepDFoFG_df = pd.DataFrame({'zScorepDFoFG': zScorepDFoFG})
    zScorepDFoFR_df = pd.DataFrame({'zScorepDFoFR': zScorepDFoFR})
    zScorepDFoFRatio_df = pd.DataFrame({'zScorepDFoFRatio': zScorepDFoFRatio})
    
    # outputting key variables to an excel spreadsheet
    # reset and dropped index for some because they began at index 1 instead of 0
    excel_output = pd.concat([timestamps_raw_df.reset_index(drop = True), timestamps_zero_sec_df.reset_index(drop = True), pcRowSumG_df.reset_index(drop = True), 
                              pcRowSumR_df.reset_index(drop = True), 
                              LRpcG_df, LRpcR_df, LRCpcG_df, LRCpcR_df, pcRatio_df, LRpcRatio_df,
                              pDFoFG_df.reset_index(drop = True), pDFoFR_df.reset_index(drop = True), pDFoFRatio_df, 
                              zScorepDFoFG_df.reset_index(drop = True), zScorepDFoFR_df.reset_index(drop = True), 
                              zScorepDFoFRatio_df], axis = 1)
            
    excel_output.to_excel(os.path.join(writeFoldData, titleName + ' photon count output.xlsx'), sheet_name = titleName)
    

    
