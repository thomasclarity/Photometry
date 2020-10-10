
# Inputs R Spectral Unmixing output and original CSV files
# Graphs linear regression coefficients across time
# Generates excel output file required for next step in data analysis/visualization pipeline

#%%

# import relevant modules
import os
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import style
import numpy as np
from scipy.optimize import curve_fit
from matplotlib import rcParams
import glob                                                                 
#import matplotlib.mlab as mlab
#from scipy import optimize, polyfit
#from scipy.optimize import minimize
#from scipy.optimize import fsolve

# import graph style
style.use('seaborn-poster')
rcParams.update({'figure.autolayout': True})
#rcParams.update({'font.size':34})

# set directories for reading folders
readFoldRoutput = '/Users/clarityt2/Documents/Gordon Lab/Photometry Preprocessing/Spectral Unmixing'
readFoldCSV = '/Users/clarityt2/Documents/Gordon Lab/Photometry Preprocessing/CSV Preprocessed'

# set directories for writing folders
writeFoldFig = '/Users/clarityt2/Documents/Gordon Lab/Photometry Preprocessing/Preprocessing Output Spectral Unmixing'
writeFoldData = '/Users/clarityt2/Documents/Gordon Lab/Photometry Preprocessing/Preprocessing Output Spectral Unmixing'

#%%

# call all Lin Unmix Output Files in folder, renaming certain titles to have fewer characters
for file in glob.glob(readFoldRoutput + '/m*.csv'): 
    
    fileName = os.path.basename(file)
    print(fileName)

    sep = '_Subt'
    titleName = fileName.rsplit(sep, 1)[0]
    
    basePlasticity = "basePlasticity"
    if basePlasticity in titleName:
        titleName = titleName.replace("basePlasticity", "base")
       
    baseIO = "baseIO"
    if baseIO in titleName:
        titleName = titleName.replace("baseIO", "base")

    # read CSV of R output (linear spectral unmixing results)
    unmixRes = pd.read_csv(os.path.join(readFoldRoutput, fileName))
    # why can't you just run pd.read_csv(file)? It does not throw an error
    # because the directory was not defined previously. You don't know what directory you are in right now.
    
    # select time period to analyze by adjusting first range. Note, iloc is EXCLUSIVE of the high end of the range
    unmixResSel = unmixRes.iloc[:,:]
    # I think this is just a line for future files, not necessary here

    # create dataframes for coefficients pertaining to green and red components and their ratio
    coeffG = unmixResSel['Coeff of Green']
    coeffR = unmixResSel['Coeff of Red']

    # read CSV of raw data
    rawOutput = pd.read_csv(os.path.join(readFoldCSV, fileName))

    # extract timestamp from raw data CSV
    timestamps_raw = rawOutput.iloc[14:,1:2]
    # zero timestamps and convert from ms to seconds
    timestamps_zero_sec = ((timestamps_raw - timestamps_raw.iloc[0,0])/1000)
    # convert timestamps to a flattened array (needed for subsequent linear regression)
    timestamps_zero_sec_array = timestamps_zero_sec.values.flatten()

#%%
        
    # plot coefficients vs time, separated into green and red components
    fig1, ax1 = plt.subplots()
    ax1.plot(timestamps_zero_sec, coeffG, label = 'GCaMP', color = 'green')
    ax1.plot(timestamps_zero_sec, coeffR, label = 'TdTomato', color = 'red')
    ax1.set_xlabel('Time (sec)', size=20)
    ax1.set_ylabel('Umixing Coefficient', size=20)
    ax1.set_title(titleName, size=20)
    ax1.legend(prop = dict(size=16))
    ax1.tick_params(axis='x', labelsize=16)
    ax1.tick_params(axis='y', labelsize=16)
    #ax1.set_xlim(0,200)
    #ax1.set_ylim(0,2000)
    plt.savefig(os.path.join(writeFoldFig, titleName + ' Coeff vs Time G R.pdf'))
    
#%%

    # perform linear regression on G and R coefficients to correct for bleaching
    def LRgreen(x, m, b):
        return m * timestamps_zero_sec_array + b 
    
    poptG, pcovG = curve_fit(LRgreen, timestamps_zero_sec_array, coeffG, bounds = ([-np.inf, -np.inf], [0,np.inf]))
    
    LRcoeffG = LRgreen(timestamps_zero_sec_array, *poptG)
    
    def LRred(x, m, b):
        return m * timestamps_zero_sec_array + b 
    
    poptR, pcovR = curve_fit(LRred, timestamps_zero_sec_array, coeffR, bounds = ([-np.inf, -np.inf], [0,np.inf]))
    
    LRcoeffR = LRred(timestamps_zero_sec_array, *poptR)
    
    # plot result of linear regression with G and R coefficients
    fig2, ([ax2, ax3]) = plt.subplots (2,1,figsize = (10,6))
    ax2.set_title(titleName, size = 20)
    ax2.plot(timestamps_zero_sec, coeffG, label = 'GCaMP', color = 'green')
    ax2.plot(timestamps_zero_sec, LRcoeffG, label = 'Lin Reg', color = 'yellow')
    ax2.set_ylabel('Unmixing Coefficient', size=16)
    ax2.tick_params(axis='x', labelsize=16)
    ax2.tick_params(axis='y', labelsize=16)
    #ax2.set_xlim(0,200)
    #ax2.set_ylim(0,2000)
    ax2.legend(loc = 'upper right', prop = dict(size=16))
    ax3.plot(timestamps_zero_sec, coeffR, label = 'TdTomato', color = 'red')
    ax3.plot(timestamps_zero_sec, LRcoeffR, label = 'Lin Reg', color = 'yellow')
    ax3.set_xlabel('Time (sec)', size=16)
    ax3.set_ylabel('Unmixing Coefficient', size=16)
    ax3.tick_params(axis='x', labelsize=16)
    ax3.tick_params(axis='y', labelsize=16)
    #ax3.set_xlim(0,200)
    #ax3.set_ylim(0,2000)
    ax3.legend(loc = 'upper right', prop = dict(size=16))
    plt.savefig(os.path.join(writeFoldFig, titleName + ' Lin Reg G and R.pdf'))

#%%

    # correct G and R coefficients using linear regression
    # create dataframe from LRcoeffG and divide the first value by each value to get a correction value for each timepoint
    # multiply the G and R coefficients by their correction factors
    # coeffG was indexed to 1, needed to reset index to 0 to properly multiply the two columns
    # Had to reset index because the first number in the rows was assigned "1" not "0" so to properly multiply each
    # photon sum by its respective coefficient you needed to index
    # drop = True gets rid of the column with the old index
    # ignore_index =True replaces the column labels with 0 and 1

    LRcoeffG_df = pd.DataFrame(LRcoeffG)
    LRcorrFactorG = LRcoeffG_df.iloc[0,0] / LRcoeffG_df
    LRcorrectionG_df = pd.concat([coeffG.reset_index(drop = True),LRcorrFactorG], axis=1, ignore_index=True)
    LRCcoeffG = (LRcorrectionG_df.iloc[:,0]) * (LRcorrectionG_df.iloc[:,1])
    
    LRcoeffR_df = pd.DataFrame(LRcoeffR)
    LRcorrFactorR = LRcoeffR_df.iloc[0,0] / LRcoeffR_df
    LRcorrectionR_df = pd.concat([coeffR.reset_index(drop = True),LRcorrFactorR], axis=1, ignore_index=True)
    LRCcoeffR = (LRcorrectionR_df.iloc[:,0]) * (LRcorrectionR_df.iloc[:,1])
    
    # plot corrected coefficients
    fig3, ([ax4, ax5]) = plt.subplots(2,1,figsize = (10,6))
    ax4.set_title(titleName, size = 20)
    ax4.plot(timestamps_zero_sec, coeffG, label = 'GCaMP', color = 'green')
    ax4.plot(timestamps_zero_sec, LRCcoeffG, label = 'LRC GCaMP', color = 'yellow')
    ax4.set_ylabel('Unmixing Coefficient', size=16)
    ax4.tick_params(axis='x', labelsize=16)
    ax4.tick_params(axis='y', labelsize=16)
    #ax4.set_xlim(0,200)
    #ax4.set_ylim(0,2000)
    ax4.legend(loc = 'upper right', prop = dict(size=16))
    ax5.plot(timestamps_zero_sec, coeffR, label = 'TdTomato', color = 'red')
    ax5.plot(timestamps_zero_sec, LRCcoeffR, label = 'LRC TdTomato', color = 'yellow')
    ax5.set_xlabel('Time (sec)', size=16)
    ax5.set_ylabel('Unmixing Coefficient', size=16)
    ax5.tick_params(axis='x', labelsize=16)
    ax5.tick_params(axis='y', labelsize=16)
    #ax5.set_xlim(0,200)
    #ax5.set_ylim(0,2000)
    ax5.legend(loc = 'upper right', prop = dict(size=16))
    plt.savefig(os.path.join(writeFoldFig, titleName + ' Lin Reg-Corrected Coefficients G and R.pdf'))

#%%
    
    # calculate G:R Ratio coefficient from LRC coefficients 
    coeffRatio = LRCcoeffG / LRCcoeffR
    
    # perform linear regression on G:R ratio (constrained to slope = 0)
    def LRratio(x, m, b):
        return m * timestamps_zero_sec_array + b 
    
    poptGR, pcovGR = curve_fit(LRratio, timestamps_zero_sec_array, coeffRatio, bounds = ([-1e-20, -np.inf], [0, np.inf]))
    
    LRcoeffRatio = LRratio(timestamps_zero_sec_array, *poptGR)
    
    # plot ratio coefficient and lin regression result
    fig4, ax6 = plt.subplots()
    ax6.plot(timestamps_zero_sec, coeffRatio, label = 'GCaMP:TdTomato', color = 'purple')
    ax6.plot(timestamps_zero_sec, LRcoeffRatio, label = 'Lin Reg', color = 'yellow')
    ax6.set_xlabel('Time (sec)', size=20)
    ax6.set_ylabel('Unmixing Coefficient Ratio', size=20)
    ax6.set_title(titleName, size=20)
    ax6.tick_params(axis='x', labelsize=16)
    ax6.tick_params(axis='y', labelsize=16)
    #ax6.set_xlim(0,200)
    #ax6.set_ylim(0,2000)
    ax6.legend(loc = 'upper right', prop = dict(size=16))
    plt.savefig(os.path.join(writeFoldFig, titleName + ' Lin Reg Coefficients GR-Ratio.pdf'))

#%%
    
    # calculate and plot %dCoC for G, R and Ratio from linear regressions
    pDCoCG = (coeffG - LRcoeffG) / LRcoeffG * 100
    pDCoCR = (coeffR - LRcoeffR) / LRcoeffR * 100
    pDCoCRatio = (coeffRatio - LRcoeffRatio) / LRcoeffRatio * 100
    
    fig5, ax7 = plt.subplots()
    #ax7.plot(timeSec, pDCoCRatio, label = 'GCaMP:TdTomato', color = 'purple')
    ax7.plot(timestamps_zero_sec, pDCoCG, label = 'GCaMP', color = 'green')
    ax7.plot(timestamps_zero_sec, pDCoCR, label = 'TdTomato', color = 'red')
    ax7.set_xlabel('Time (sec)', size=20)
    ax7.set_ylabel('% Delta C/C', size=20)
    ax7.set_title(titleName, size=20)
    ax7.tick_params(axis='x', labelsize=16)
    ax7.tick_params(axis='y', labelsize=16)
    #ax7.set_xlim(0,200)
    #ax7.set_ylim(0,2000)
    ax7.legend(loc = 'upper right', prop = dict(size=16))
    plt.savefig(os.path.join(writeFoldFig, titleName + ' Coeff dCoC vs Time G R and Ratio.pdf'))
    
#%%
    # calculate Z-scores from %dC/C for green and red components and their ratio
    meanpDCoCG = pDCoCG.mean()
    meanpDCoCR = pDCoCR.mean()
    meanpDCoCRatio = pDCoCRatio.mean()
    stdpDCoCG = pDCoCG.std()
    stdpDCoCR = pDCoCR.std()
    stdpDCoCRatio = pDCoCRatio.std()
    
    zScorepDCoCG = (pDCoCG-meanpDCoCG)/stdpDCoCG
    zScorepDCoCR = (pDCoCR-meanpDCoCR)/stdpDCoCR
    zScorepDCoCRatio = (pDCoCRatio-meanpDCoCRatio)/stdpDCoCRatio
    
    # plot Z-scores from %dC/C for green, red, ratio
    fig8, ax8 = plt.subplots()
    #ax8.plot(timeSec, zScorepDCoCRatio, label = 'GCaMP:TdTomato', color = 'purple')
    ax8.plot(timestamps_zero_sec, zScorepDCoCG, label = 'GCaMP', color = 'green')
    ax8.plot(timestamps_zero_sec, zScorepDCoCR, label = 'TdTomato', color = 'red')
    ax8.set_xlabel('Time (sec)', size=20)
    ax8.set_ylabel('Z-Score (from %dC/C)', size=20)
    ax8.set_title(titleName, size=20)
    ax8.tick_params(axis='x', labelsize=16)
    ax8.tick_params(axis='y', labelsize=16)
    #ax8.set_xlim(0,200)
    #ax8.set_ylim(0,2000)
    ax8.legend(loc = 'upper right', prop = dict(size=16))
    plt.savefig(os.path.join(writeFoldFig, titleName + ' Coeff Z-Scores vs Time G:R Ratio.pdf'))

#%%

    # convert variables to dataframes for excel output
    # Renaming did not work originally, changed '0' to 'Unnamed: 1'
    # Also I added 'coeffG_df' as a column in the excel file

    timestamps_raw_df = timestamps_raw.rename(columns = {'Unnamed: 1':' timestampRaw'})
    timestamps_zero_sec_df = timestamps_zero_sec.rename(columns = {'Unnamed: 1':'timestampZeroSec'})
    coeffG_df = pd.DataFrame({'coeffG': coeffG})
    coeffR_df = pd.DataFrame({'coeffR': coeffR})
    LRcoeffG_df = pd.DataFrame({'LRcoeffG': LRcoeffG})
    LRcoeffR_df = pd.DataFrame({'LRcoeffR': LRcoeffR})
    LRCcoeffG_df = pd.DataFrame({'LRCcoeffG': LRCcoeffG})
    LRCcoeffR_df = pd.DataFrame({'LRCcoeffR': LRCcoeffR})
    coeffRatio_df = pd.DataFrame({'coeffRatio': coeffRatio})
    LRcoeffRatio_df = pd.DataFrame({'LRcoeffRatio': LRcoeffRatio})
    pDCoCG_df = pd.DataFrame({'pDCoCG': pDCoCG})
    pDCoCR_df = pd.DataFrame({'pDCoCR': pDCoCR})
    pDCoCRatio_df = pd.DataFrame({'pDCoCRatio': pDCoCRatio})
    zScorepDCoCG_df = pd.DataFrame({'zScorepDCoCG': zScorepDCoCG})
    zScorepDCoCR_df = pd.DataFrame({'zScorepDCoCR': zScorepDCoCR})
    zScorepDCoCRatio_df = pd.DataFrame({'zScorepDCoCRatio': zScorepDCoCRatio})
    
    excel_output = pd.concat([timestamps_raw_df.reset_index(drop = True), timestamps_zero_sec_df.reset_index(drop = True),
                              coeffG_df.reset_index(drop = True), coeffR_df.reset_index(drop = True),
                              LRcoeffG_df, LRcoeffR_df, LRCcoeffG_df, LRCcoeffR_df, coeffRatio_df, LRcoeffRatio_df, 
                              pDCoCG_df.reset_index(drop = True), pDCoCR_df.reset_index(drop = True), pDCoCRatio_df, 
                              zScorepDCoCG_df.reset_index(drop = True), zScorepDCoCR_df.reset_index(drop = True), zScorepDCoCRatio_df], axis = 1)
    
    excel_output.to_excel(os.path.join(writeFoldData, titleName + ' unmix coeff output.xlsx'), sheet_name = titleName)