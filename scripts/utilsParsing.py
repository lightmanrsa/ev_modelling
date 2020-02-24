__version__ = '0.0.1'
__maintainer__ = 'Niklas Wulff 31.12.2019'
__email__ = 'Niklas.Wulff@dlr.de'
__birthdate__ = '31.12.2019'
__status__ = 'dev'  # options are: dev, test, prod


import pandas as pd
import numpy as np

def assignMultiColToDType(dataFrame, cols, dType):
    dictDType = dict.fromkeys(cols, dType)
    dfOut = dataFrame.astype(dictDType)
    return(dfOut)


def assignTSToCol(df, colYear, colMonth, colDay, colHour, colMin, colName):
    dfOut = df.copy()
    dfOut[colName] = [pd.Timestamp(year=dfOut.loc[x, colYear],
                                           month=dfOut.loc[x, colMonth],
                                           day=dfOut.loc[x, colDay],
                                           hour=dfOut.loc[x, colHour],
                                           minute=dfOut.loc[x, colMin]) for x in dfOut.index]
    return(dfOut)


def assignTSAndDuration(df, colYear, colMonth, colDay, colHour_st, colMin_st, colHour_en, colMin_en):

    dfOutRaw = df.copy()
    dfOutSt = assignTSToCol(dfOutRaw, colYear, colMonth, colDay, colHour_st, colMin_st, 'timestamp_st')
    dfOut = assignTSToCol(dfOutSt, colYear, colMonth, colDay, colHour_en, colMin_en, 'timestamp_en')

    # manipulation of timestamps if the trip starts or ends at the day after the collection day
    for idx in dfOut.index:
        if dfOut.loc[idx, 'st_dat'] == 1:
            dfOut.loc[idx, 'timestamp_st'] = dfOut.loc[idx, 'timestamp_st'] + pd.Timedelta(days=1)

        if dfOut.loc[idx, 'en_dat'] == 1:
            dfOut.loc[idx, 'timestamp_en'] = dfOut.loc[idx, 'timestamp_en'] + pd.Timedelta(days=1)

    dfOut['duration'] = [dfOut.loc[x, 'timestamp_en'] - dfOut.loc[x, 'timestamp_st'] for x in dfOut.index]
    return(dfOut)


def initiateHourArray(df, columns, nHours):
    """
    Sets up an empty dataframe to be filled with hourly data.

    :param df: DataFrame from MiD results
    :param columns: List of column names
    :param nHours: integer giving the number of columns that should be added to the dataframe
    :return: dataframe with columns given and nHours additional columns appended with 0s
    """
    df_h = df.copy()
    df_h.reset_index(levels=0, inplace=True)
    df_h = df_h.loc[:, columns]
    df_emptyArray = pd.DataFrame(np.zeros((df.shape[0], nHours)))  # create an empty array and transform to dataframe
    df_h = pd.concat([df_h, df_emptyArray], axis=1, ignore_index=True)
    return(df_h)


def fillInHourlyTrips(dfData, dfZeros, colVal='wegkm_k', nHours=24):
    """
    Fills in an array with hourly columns in a given dfZeros with values from dfData's column colVal.

    :param dfData: Dataframe containing travel survey data
    :param dfZeros: Dataframe based on dfData with the same length but only limited columns containing id Data and hour columns
    :param colVal: Column name to retrieve values for columns from. Default:
    :param nHours: Number of hour columns to loop over for filling. If
    :return:
    """
    dfZerosOut = dfZeros.copy()
    for hour in range(nHours):
        rowsHourTrip = dfData.loc[:, 'st_std'] == hour
        rowsSameDayStart = rowsHourTrip & dfData.loc[:, 'st_dat'] == 0
        dfZerosOut.loc[rowsSameDayStart, hour] = dfData.loc[rowsSameDayStart, colVal]
        if hour + 24 < nHours:
            rowsNextDayStart = rowsHourTrip & dfData.loc[:, 'st_dat'] == 1
            dfZerosOut.loc[rowsNextDayStart, hour + 24] = dfData.loc[rowsNextDayStart, colVal]

    return(dfZerosOut)


def fillInMultiHourTrips(dfFill, dfData):
    pass
    for idx in dfFill.index:
        if dfFill.loc[idx, 'duration'] > pd.Timedelta(Hours=1):
            distance = dfFill.loc[idx, 'wegkm_k']
            durationInHours = dfFill.loc[idx, 'duration'] / pd.Timedelta(hours=1)
            startHour =  dfFill.loc[idx, 'st_std']
            stopFullHour = dfFill.loc[idx, 'st_std'] + round(durationInHours, 0)
            stopLastHour = stopFullHour + 1
            for hour in range(startHour, stopFullHour):
                dfFill.loc[idx, hour] = distance / round(durationInHours, 0)

            dfFill.loc[idx, stopLastHour] = distance / (durationInHours - round(durationInHours, 0))
