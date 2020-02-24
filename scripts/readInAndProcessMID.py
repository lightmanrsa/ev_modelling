__version__ = '0.0.0'
__maintainer__ = 'Niklas Wulff 31.12.2019'
__email__ = 'Niklas.Wulff@dlr.de'
__birthdate__ = '31.12.2019'
__status__ = 'dev'  # options are: dev, test, prod

import numpy as np
import yaml
import pandas as pd
import pyreadstat
from utilsParsing import *
import time
import matplotlib.pyplot as plt

linkToDataFolder = 'C:/Users/wulf_ni/Documents/11 Data/Transport data/Germany/MiD/2008/MiD 2008_DVD/Daten/SPSS/SPSS_Public Use File/'
filenameCar = 'MiD2008_PUF_Auto.sav'
filenameHoushold = 'MiD2008_PUF_Haushalt.sav'
filenamePerson = 'MiD2008_PUF_Personen.sav'
filenameTrip = 'MiD2008_PUF_Wege.sav'
filenameTravel = 'MiD2008_PUF_Reisen.sav'


timeMeasure_t0 = time.time()
# apparently read in as double with one digit behind the comma making typecasting to int necessary
dfTrip_raw, metaTrip = pyreadstat.read_sav(linkToDataFolder + filenameTrip)
dfCar_raw, metaCar = pyreadstat.read_sav(linkToDataFolder + filenameCar)

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 150)

# Eliminating observations where no time is given
dfTrip_woNulls = dfTrip_raw[(dfTrip_raw['stich_j'] != 0) &
                            (dfTrip_raw['stich_j'].notna()) &
                            (dfTrip_raw['st_min'].notna())]


cols = ['hhid', 'pid', 'wid', 'stich_j', 'stich_m', 'stichtag', 'st_std', 'st_min', 'en_std', 'en_min']
dfTrip = assignMultiColToDType(dfTrip_woNulls, cols=cols, dType='int32')

dfTrip_wTSCols = assignTSAndDuration(df=dfTrip,
                                     colYear='stich_j',
                                     colMonth='stich_m',
                                     colDay='stichtag',
                                     colHour_st='st_std',
                                     colMin_st='st_min',
                                     colHour_en='en_std',
                                     colMin_en='en_min')

listCols = ['hhid', 'pid', 'wid', 'wsid']
dfHours = initiateHourArray(dfTrip_wTSCols, columns=listCols, nHours=48)
dfHours_filled = fillInHourlyTrips(dfData=dfTrip_wTSCols, dfZeros=dfHours, colVal='wegkm_k', nHours=26)



timeMeasure_t1 = time.time()
timeElapsed = timeMeasure_t1 - timeMeasure_t0

print('timing: ', str(timeElapsed) + ' seconds', sep='\n')
print('Result: ', dfHours_filled.head, sep='\n')
