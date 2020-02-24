# -*- coding:utf-8 -*-

__version__ = '0.1.0'
__maintainer__ = 'Niklas Wulff 04.02.2020'
__email__ = 'Niklas.Wulff@dlr.de'
__birthdate__ = '15.04.2019'
__status__ = 'test'  # options are: dev, test, prod

# This script holds the function definitions for VencoPy.
# df = dataframe

import os
import sys
import warnings

sys.path.append(os.path.abspath('C:/REMix-OaM/OptiMo/projects/REMix-tools/remixPlotting'))

import numpy as np
import yaml
import pandas as pd
from functools import reduce
from random import seed
from random import random

# review: general remark for publication: can we rename scripts into tools or libs? It is not really a script what is saved in this folder and seems a bit missleading

# shutil: Link library
# pathlib: Objectoriented path mannipulation
# glob: Linux path syntax



####-------------------GENERAL------------------------------####
# ToDo: Explicit strings from current Excel file in the code. Is it possible to implement that better???

# -----INPUT-----------------------------------
# review have you considered splitting this file up into different files, named after the captions in this file? It would make it easier to navigate and search the code base

def readVencoConfig(cfgLink):
    config = yaml.load(open(cfgLink), Loader=yaml.SafeLoader)
    # review: the brackets around config are not necessary as they will be removed by python anyway. Return is not a function but a statement
    return (config)

def initializeLinkMgr(vencoConfig):
    linkDict_out = {'linkScalars': vencoConfig['linksAbsolute']['inputData'] + vencoConfig['files']['inputDataScalars'],
                    'linkDriveProfiles': vencoConfig['linksAbsolute']['inputData'] + vencoConfig['files'][
                        "inputDataDriveProfiles"],
                    'linkPlugProfiles': vencoConfig['linksAbsolute']['inputData'] + vencoConfig['files'][
                        "inputDataPlugProfiles"],
                    'linkTSConfig': vencoConfig['linksRelative']['tsConfig'],
                    'linkTSREMix': vencoConfig['linksAbsolute']['REMixTimeseriesPath'],
                    'linkPlots': vencoConfig['linksRelative']['plots'],
                    'linkOutput': vencoConfig['linksAbsolute']['OutputPath']}
    # review: the brackets around config are not necessary as they will be removed by python anyway. Return is not a function but a statement
    return (linkDict_out)

def readInputScalar(fileLink):
    # review general remark, a file link implies a sym link on the disk. Have you considered renaming the variable to filePath for example, which would imply a path to a file on the disk
    input_raw = pd.read_excel(fileLink,
                              header=5,
                              usecols="A:E",
                              skiprows=0)
    df_scalar = input_raw.loc[:, ~input_raw.columns.str.match('Unnamed')]
    df_out = df_scalar.set_index('parameter')
    # review: the brackets around config are not necessary as they will be removed by python anyway. Return is not a function but a statement
    return (df_out)

def readInputCSV(file_link):
    input_raw = pd.read_csv(file_link, header=4)
    df_out = input_raw.loc[:, ~input_raw.columns.str.match('Unnamed')]
    # review: the brackets around config are not necessary as they will be removed by python anyway. Return is not a function but a statement
    return (df_out)

def stringToBoolean(df):
    dict_bol = {'WAHR': True,
                'FALSCH': False}
    df_out = df.replace(to_replace=dict_bol, value=None)
    # review: the brackets around config are not necessary as they will be removed by python anyway. Return is not a function but a statement
    return (df_out)

def readInputBoolean(file_link):
    input_raw = readInputCSV(file_link)
    df_out = stringToBoolean(input_raw)
    # review: the brackets around config are not necessary as they will be removed by python anyway. Return is not a function but a statement
    return (df_out)

def readVencoInput(linkConfig):
    '''
    Initializing action for VencoPy-specific config-file, link dictionary and data read-in. The config file has
    to be a dictionary in a .yaml file containing three categories: linksRelative, linksAbsolute and files. Each c
    category must contain itself a dictionary with the linksRelative to data, functions, plots, scripts, config and
    tsConfig. Absolute links should contain the path to the output folder. Files should contain a link to scalar input
    data, and the two timeseries files inputDataDriveProfiles and inputDataPlugProfiles.

    :param linkConfig: The config link where all links are given.
    :return: Returns four dataframes: A link dictionary, scalars, drive profile data and plug profile
    data, the latter three ones in a raw data format.
    '''

    # print(params['linkConfig'])
    linkDict = initializeLinkMgr(readVencoConfig(linkConfig))
    # dmgr['linkDict'] = linkDict

    # review: have you considered using the logging module for these kind of outputs?
    print('Reading Venco input scalars, drive profiles and boolean plug profiles')

    scalars = readInputScalar(linkDict['linkScalars'])
    driveProfiles_raw = readInputCSV(linkDict['linkDriveProfiles'])
    plugProfiles_raw = readInputBoolean(linkDict['linkPlugProfiles'])

    print('There are ' + str(len(driveProfiles_raw)) + ' drive profiles and ' +
                    str(len(driveProfiles_raw)) + ' plug profiles.')

    return linkDict, scalars, driveProfiles_raw, plugProfiles_raw


    # dmgr['scalars'] = scalars
    # dmgr['driveProfilesRaw'] = driveProfilesRaw
    # dmgr['plugProfilesRaw'] = plugProfilesRaw


# -----PRE-PROCESSING---------------------------------
def indexProfile(driveProfiles_raw, plugProfiles_raw, indices):
    '''
    Takes raw data as input and indices different profiles with the specified index columns und an unstacked form.

    :param driveProfiles_raw: Raw drive profiles.
    :param plugProfiles_raw: Raw plug profiles.
    :param indices: Index columns that are assigned as indices.
    :return: Two indexed dataframes with index columns as given in argument indices separated from data columns

    '''

    driveProfile = driveProfiles_raw.set_index(list(indices))
    plugProfile = plugProfiles_raw.set_index(list(indices))
    # review: the brackets around config are not necessary as they will be removed by python anyway. Return is not a function but a statement
    return (driveProfile, plugProfile)

def procScalars(driveProfiles_raw, plugProfiles_raw, driveProfiles, plugProfiles):
    '''
    Calculates some scalars from the input data such as the number of hours of drive and plug profiles, the number of
    profiles etc.

    :return: Returns a dataframe of processed scalars including number of profiles and number of hours per profile.

    '''

    noHoursDrive = len(driveProfiles.columns)
    noHoursPlug = len(plugProfiles.columns)
    noDriveProfiles_in = len(driveProfiles_raw)
    noPlugProfiles_in = len(plugProfiles_raw)
    scalarsProc = {'noHoursDrive': noHoursDrive,
                   'noHoursPlug': noHoursPlug,
                   'noDriveProfiles_in': noDriveProfiles_in,
                   'noPlugProfiles_in': noPlugProfiles_in}
    if noHoursDrive == noHoursPlug:
        scalarsProc['noHours'] = noHoursDrive
    else:
        warnings.warn('Length of drive and plug input data differ! This will at the latest crash in calculating '
                      'profiles for SoC max')
    return scalarsProc

# -----CALCULATION OF PROFILES-------------------------------------------------------


def calcConsumptionProfiles(driveProfiles, scalars):
    '''
    Calculates electrical consumption profiles from drive profiles assuming specific consumption (in kWh/100 km)
    given in scalar input data file.

    :return: Returns the consumption profile in same format and length as driveProfiles but scaled with the specific
    consumption assumption.

    '''

    consumptionProfiles = driveProfiles.copy()
    # review have you considered the pandas .astype() method? It is more performant than a direct float type cast.
    # review the division by int 100 can be changed to float 100. which would force python above 2.7 to use float division and thus a typecast might not even be necessary
    consumptionProfiles = consumptionProfiles * float(scalars.loc['Verbrauch NEFZ CD', 'value']) / 100
    return consumptionProfiles


def calcChargeProfiles(plugProfiles, scalars):
    '''
    Calculates the maximum possible charge power based on the plug profile assuming the charge column power
    given in the scalar input data file (so far under Panschluss).

    :return: Returns scaled plugProfile in the same format as plugProfiles.

    '''

    chargeProfiles = plugProfiles.copy()
    # review have you considered the pandas .astype() method? It is more performant than a direct float type cast.
    chargeProfiles = chargeProfiles * float(scalars.loc['Panschluss', 'value'])
    return chargeProfiles


def calcChargeMaxProfiles(chargeProfiles, consumptionProfiles, scalars, scalarsProc, nIter):
    '''
    Calculates all maximum SoC profiles under the assumption that batteries are always charged as soon as they
    are plugged to the grid. Values are assured to not fall below SoC_min * battery capacity or surpass
    SoC_max * battery capacity. Relevant profiles are chargeProfile and consumptionProfile. An iteration assures
    the boundary condition of chargeMaxProfile(0) = chargeMaxProfile(len(profiles)). The number of iterations
    is given as parameter.

    :param chargeProfiles: Indexed dataframe of charge profiles.
    :param consumptionProfiles: Indexed dataframe of consumptionProfiles.
    :param scalars: DataFrame holding techno-economic assumptions.
    :param scalarsProc: DataFrame holding information about profile length and number of hours.
    :param nIter: Number of iterations to assure that the minimum and maximum value are approximately the same
    :return: Returns an indexed DataFrame with the same length and form as chargProfiles and consumptionProfiles,
    containing single-profile SOC max values for each hour in each profile.

    '''

    chargeMaxProfiles = chargeProfiles.copy()
    chargeProfiles = chargeProfiles.copy()
    consumptionProfiles = consumptionProfiles.copy()
    batCapMin = scalars.loc['Battery size', 'value'] * scalars.loc['SoCmin', 'value']
    batCapMax = scalars.loc['Battery size', 'value'] * scalars.loc['SoCmax', 'value']
    nHours = scalarsProc['noHours']
    idxIt = 1
    for idxIt in range(nIter):
        # ToDo: np.where() replace by pd.something(),
        # ToDo: prohibit typecasting str(idx) in data preparation step colnames as integers {smell} in function indexProfiles()
        for idx in range(nHours):
            # testing line
            # chargeMaxProfiles.ix[3, '0'] = 15.0
            if idx == 0:
                chargeMaxProfiles[str(idx)] = np.where(chargeMaxProfiles[str(idx)] <= batCapMax,
                                                      chargeMaxProfiles[str(nHours - 1)],
                                                      batCapMax)
            else:
                # Calculate and append column with new SoC Max value for comparison and cleaner code
                chargeMaxProfiles['newCharge'] = chargeMaxProfiles[str(idx - 1)] + \
                                                chargeProfiles[str(idx)] - \
                                                consumptionProfiles[str(idx)]

                # Ensure that chargeMaxProfiles values are between batCapMin and batCapMax
                chargeMaxProfiles[str(idx)] = np.where(chargeMaxProfiles['newCharge'] <= batCapMax,
                                                      chargeMaxProfiles['newCharge'],
                                                      batCapMax)
                chargeMaxProfiles[str(idx)] = np.where(chargeMaxProfiles[str(idx)] >= batCapMin,
                                                      chargeMaxProfiles[str(idx)],
                                                      batCapMin)

        # review: general remark instead of str(0) which is a performance heavy operation, one could write "0" which is equivalent and less performance heavy (performance impact is however negligible I guess)
        devCrit = chargeMaxProfiles[str(nHours - 1)].sum() - chargeMaxProfiles[str(0)].sum()
        print(devCrit)
        idxIt += 1
    chargeMaxProfiles.drop(labels='newCharge', axis='columns', inplace=True)
    return chargeMaxProfiles


def calcChargeProfilesUncontrolled(chargeMaxProfiles, scalarsProc):
    '''
    Calculates the uncontrolled electric charging based on SoC Max profiles for each hour for each profile.

    :return: Returns profiles for uncontrolled charging under the assumption that charging occurs as soon as a
    vehicle is connected to the grid up to the point that the maximum battery SOC is reached or the connection
    is interrupted. DataFrame has the same format as chargeMaxProfiles.

    '''

    chargeMaxProfiles = chargeMaxProfiles.copy()
    chargeProfilesUncontrolled = chargeMaxProfiles.copy()
    nHours = scalarsProc['noHours']

    for idx in range(nHours):

        # testing line
        # chargeMaxProfile.ix[3, '0'] = 15.0
        # if idx == 0:
        #     chargeProfilesUncontrolled[str(0)] = np.where(
        #         chargeMaxProfiles[str(0)] >= chargeMaxProfiles[str(nHours-1)],
        #         chargeMaxProfiles[str(0)] - chargeMaxProfiles[str(nHours-1)],
        #         0)

        if idx != 0:
            chargeProfilesUncontrolled[str(idx)] = np.where(
                chargeMaxProfiles[str(idx)] >= chargeMaxProfiles[str(idx - 1)],
                chargeMaxProfiles[str(idx)] - chargeMaxProfiles[str(idx - 1)],
                0)

    # set value of uncontrolled charging for first hour to average between hour 1 and hour 23
    # because in calcChargeMax iteration the difference is minimized.
    chargeProfilesUncontrolled[str(0)] = \
        (chargeProfilesUncontrolled[str(1)] + chargeProfilesUncontrolled[str(nHours - 1)])/2
    return chargeProfilesUncontrolled
    # datalogger.info(chargeProfilesUncontrolled)


def calcDriveProfilesFuelAux(chargeMaxProfiles, chargeProfilesUncontrolled, driveProfiles, scalars, scalarsProc):
    #ToDo: alternative vectorized format for looping over columns? numpy, pandas: broadcasting-rules
    '''
    Calculates necessary fuel consumption profile of a potential auxilliary unit (e.g. a gasoline motor) based
    on gasoline consumption given in scalar input data (in l/100 km). Auxilliary fuel is needed if an hourly
    mileage is higher than the available SoC Max in that hour.

    :return: Returns a DataFrame with single-profile values for back-up fuel demand in the case a profile cannot
    completely be fulfilled with electric driving under the given consumption and battery size assumptions.

    '''

    # review: the hardcoding of the column names can cause a lot of problems for people later on if we do not ship the date with the tool. I would recommend to move these column names to a config file similar to i18n strategies
    consumptionPower = scalars.loc['Verbrauch NEFZ CD', 'value']
    consumptionFuel = scalars.loc['Verbrauch NEFZ CS', 'value']

    # initialize data set for filling up later on
    driveProfilesFuelAux = chargeMaxProfiles.copy()
    nHours = scalarsProc['noHours']

    # review: have you considered naming idx into ihour as it actually contains the currently processed hour and would make the code more readable
    for idx in range(nHours):
        # review as far as I can tell, the hour 0 is never filled or added as a column to driveProfilesFuelAux. But this should raise an error in line 336 for idx 1. Why does this work anyhow?
        if idx != 0:
            driveProfilesFuelAux[str(idx)] = (consumptionFuel / consumptionPower) * \
                                             (driveProfiles[str(idx)] * consumptionPower / 100 -
                                              chargeProfilesUncontrolled[str(idx)] -
                                              (chargeMaxProfiles[str(idx - 1)] - chargeMaxProfiles[str(idx)]))
    # Setting value of hour=0 equal to the average of hour=1 and last hour
    driveProfilesFuelAux[str(0)] = (driveProfilesFuelAux[str(nHours - 1)] + driveProfilesFuelAux[str(1)])/2
    driveProfilesFuelAux = driveProfilesFuelAux.round(4)
    return driveProfilesFuelAux


def calcChargeMinProfiles(chargeProfiles, consumptionProfiles, driveProfilesFuelAux, scalars, scalarsProc, nIter):
    #ToDo param minSecurityFactor
    '''
    Calculates minimum SoC profiles assuming that the hourly mileage has to exactly be fulfilled but no battery charge
    is kept inspite of fulfilling the mobility demand. It represents the minimum charge that a vehicle battery has to
    contain in order to fulfill all trips.
    An iteration is performed in order to assure equality of the SoCs at beginning and end of the profile.

    :param chargeProfiles: Charging profiles with techno-economic assumptions on connection power.
    :param consumptionProfiles: Profiles giving consumed electricity for each trip in each hour assuming specified
    consumption.
    :param driveProfilesFuelAux: Auxilliary fuel demand for fulfilling trips if purely electric driving doesn't suffice.
    :param scalars: Techno-economic input assumptions such as consumption, battery capacity etc.
    :param scalarsProc: Number of profiles and number of hours of each profile.
    :param nIter: Gives the number of iterations to fulfill the boundary condition of the SoC equalling in the first
    and in the last hour of the profile.
    :return: Returns an indexed DataFrame containing minimum SOC values for each profile in each hour in the same
    format as chargeProfiles, consumptionProfiles and other input parameters.

    '''

    # review general remark: white spaces in column names give me the creeps as it is easy to mistype and create all kind of wired errors. Especially if there are columns with similar names only differing in whitespaces. This is clearly not the case here, but did you consider naming columns with underscores for easier reference?
    chargeMinProfiles = chargeProfiles.copy()
    batCapMin = scalars.loc['Battery size', 'value'] * scalars.loc['SoCmin', 'value']
    batCapMax = scalars.loc['Battery size', 'value'] * scalars.loc['SoCmax', 'value']
    consElectric = scalars.loc['Verbrauch NEFZ CD', 'value']
    consGasoline = scalars.loc['Verbrauch NEFZ CS', 'value']
    nHours = scalarsProc['noHours']
    idxIt = 1
    while idxIt <= nIter:
        for idx in range(nHours):

            # testing line
            # chargeMinProfiles.ix[3, '0'] = 15.0

            # review the above nHours implies, that the number of hours can vary based on user input or the underlying data. It seems to me risky to hardcode 23 here if the last hour is meant. Would it not be more prudent to use a variable lastHour that is nHours-1?
            if idx == 23:
                chargeMinProfiles[str(idx)] = np.where(batCapMin <= chargeMinProfiles[str(idx)],
                                                       chargeMinProfiles[str(0)],
                                                       batCapMin)
            else:
                # Calculate and append column with new SOC Max value for comparison and nicer code
                chargeMinProfiles['newCharge'] = chargeMinProfiles[str(idx + 1)] + \
                                                 consumptionProfiles[str(idx + 1)] - \
                                                 chargeProfiles[str(idx + 1)] - \
                                                 (driveProfilesFuelAux[str(idx + 1)] * consElectric / consGasoline)

                # Ensure that chargeMinProfiles values are between batCapMin and batCapMax
                chargeMinProfiles[str(idx)] = np.where(chargeMinProfiles['newCharge'] >= batCapMin,
                                                       chargeMinProfiles['newCharge'],
                                                       batCapMin)
                chargeMinProfiles[str(idx)] = np.where(chargeMinProfiles[str(idx)] <= batCapMax,
                                                       chargeMinProfiles[str(idx)],
                                                       batCapMax)

        devCrit = chargeMinProfiles[str(nHours - 1)].sum() - chargeMinProfiles[str(0)].sum()
        print(devCrit)
        idxIt += 1
    chargeMinProfiles.drop('newCharge', axis='columns', inplace=True)
    return chargeMinProfiles


def createRandNo(driveProfiles, setSeed=1):
    # review for me the function name is not precise. The function creates to my understanding a random profile. If this is the case, I would name it accordingly.
    '''
    Creates a random number between 0 and 1 for each profile based on driving profiles.

    :return: Returns an indexed series with the same indices as dirveProfiles with a random number between 0 and 1 for
    each index.

    '''
    idxData = driveProfiles.copy()
    seed(setSeed)  # seed random number generator for reproducibility
    idxData['randNo'] = np.random.random(len(idxData))
    idxData['randNo'] = [random() for _ in range(len(idxData))]  # generate one random number for each profile / index
    randNos = idxData.loc[:, 'randNo']
    return randNos


def calcProfileSelectors(chargeProfiles,
                         consumptionProfiles,
                         driveProfiles,
                         driveProfilesFuelAux,
                         randNos,
                         scalars,
                         fuelDriveTolerance,
                         isBEV):
    # FIXME Maybe make this function neater by giving filtering functions as params or in a separate file??

    '''
    This function calculates two filters. The first filter, filterCons, excludes profiles that depend on auxiliary
    fuel with an option of a tolerance and those that don't reach a minimum daily average for mileage.
    A second filter filterDSM excludes profiles where the battery doesn't suffice the mileage and those where charging
    throughout the day supplies less energy than necessary for the respective trips.

    :param chargeProfiles: Indexed DataFrame giving hourly charging profiles
    :param consumptionProfiles: Indexed DataFrame giving hourly consumption profiles
    :param driveProfiles:  Indexed DataFrame giving hourly electricity demand profiles for driving.
    :param driveProfilesFuelAux: Indexed DataFrame giving auxiliary fuel demand.
    :param randNos: Indexed Series giving a random number between 0 and 1 for each profiles.
    :param scalars: Techno-economic assumptions
    :param fuelDriveTolerance: Give a threshold value how many liters may be needed throughout the course of a day
    in order to still consider the profile.
    :param isBEV: Boolean value. If true, more 2030 profiles are taken into account (in general).
    :return: The bool indices are written to one DataFrame in the DataManager with the columns randNo, indexCons and
    indexDSM and the same indices as the other profiles.

    '''

    boolBEV = scalars.loc['EREV oder BEV?', 'value']
    minDailyMileage = scalars.loc['Minimum daily mileage', 'value']
    batSize = scalars.loc['Battery size', 'value']
    socMax = scalars.loc['SoCmax', 'value']
    socMin = scalars.loc['SoCmin', 'value']
    filterCons = driveProfiles.copy()
    filterCons['randNo'] = randNos
    filterCons['bolFuelDriveTolerance'] = driveProfilesFuelAux.sum(axis='columns') * \
                                           boolBEV < fuelDriveTolerance
    filterCons['bolMinDailyMileage'] = driveProfiles.sum(axis='columns') > \
                                        (2 * randNos * minDailyMileage +
                                         (1 - randNos) * minDailyMileage *
                                         isBEV)
    filterCons['indexCons'] = filterCons.loc[:, 'bolFuelDriveTolerance'] & \
                               filterCons.loc[:, 'bolMinDailyMileage']
    filterCons['bolConsumption'] = consumptionProfiles.sum(axis=1) < \
                                    chargeProfiles.sum(axis=1)
    filterCons['bolSuffBat'] = consumptionProfiles.sum(axis=1) < \
                                batSize * (socMax - socMin)
    filterCons['indexDSM'] = filterCons['indexCons'] & filterCons['bolConsumption'] & filterCons['bolSuffBat']

    print('There are ' + str(sum(filterCons['indexCons'])) + ' considered profiles and ' + \
                    str(sum(filterCons['indexDSM'])) + ' DSM eligible profiles.')
    filterCons_out = filterCons.loc[:, ['randNo', 'indexCons', 'indexDSM']]
    return filterCons_out


def calcElectricPowerProfiles(consumptionProfiles, driveProfilesFuelAux, scalars, filterCons, scalarsProc,
                              filterIndex):
    '''
    Calculates electric power profiles that serve as outflow of the fleet batteries.

    :param consumptionProfiles: Indexed DataFrame containing electric vehicle consumption profiles.
    :param driveProfilesFuelAux: Indexed DataFrame containing
    :param scalars:
    :param filterCons:
    :param scalarsProc:
    :param filterIndex:
    :return:
    :param dmgrName: 'electricPowerProfiles'
    :param filterIndex: Can be either 'indexCons' or 'indexDSM' so far. 'indexDSM' applies stronger filters and results
    are thus less representative.
    :return: Returns electric demand from driving filtered and aggregated to one fleet. Stores the profile in the
    Data Manager under the key specified by dmgrName.
    '''

    consumptionPower = scalars.loc['Verbrauch NEFZ CD', 'value']
    consumptionFuel = scalars.loc['Verbrauch NEFZ CS', 'value']
    indexCons = filterCons.loc[:, 'indexCons']
    indexDSM = filterCons.loc[:, 'indexDSM']
    # datalogger.info(indexCons)
    nHours = scalarsProc['noHours']
    electricPowerProfiles = consumptionProfiles.copy()
    for idx in range(nHours):
        electricPowerProfiles[str(idx)] = (consumptionProfiles[str(idx)] - driveProfilesFuelAux[str(idx)] *
                                           (consumptionPower / consumptionFuel))

        if filterIndex == 'indexCons':
            electricPowerProfiles[str(idx)] = electricPowerProfiles[str(idx)] * indexCons
        elif filterIndex == 'indexDSM':
            electricPowerProfiles[str(idx)] = electricPowerProfiles[str(idx)] * indexDSM
    return electricPowerProfiles
    # datalogger.info(electricPowerProfiles)


def setUnconsideredBatProfiles(chargeMaxProfiles, chargeMinProfiles, filterCons, minValue, maxValue):
    '''
    Sets all profile values with indexDSM = False to extreme values. For SoC max profiles, this means a value
    that is way higher than SoC max capacity. For SoC min this means usually 0. This setting is important for the
    next step of filtering out extreme values.

    :param maxValue: Value that non-reasonable values of SoC max profiles should be set to.
    :param minValue: Value that non-reasonable values of SoC min profiles should be set to.
    :return: Writes the two profiles files 'chargeMaxProfilesDSM' and 'chargeMinProfilesDSM' to the DataManager.
    '''

    chargeMinProfilesDSM = chargeMinProfiles.copy()
    chargeMaxProfilesDSM = chargeMaxProfiles.copy()
    # if len(chargeMaxProfilesCons) == len(filterCons): #len(chargeMaxProfilesCons) = len(chargeMinProfilesCons) by design
    # How can I catch pandas.core.indexing.IndexingError ?
    try:
        chargeMinProfilesDSM.loc[~filterCons['indexDSM'].astype('bool'), :] = minValue
        chargeMaxProfilesDSM.loc[~filterCons['indexDSM'].astype('bool'), :] = maxValue
    except:
        print("Declaration doesn't work. "
              "Maybe the length of filterCons differs from the length of chargeMaxProfiles")
    return chargeMaxProfilesDSM, chargeMinProfilesDSM


def indexFilter(chargeMaxProfiles, chargeMinProfiles, filterCons):
    """
    Filters out profiles where indexCons is False.

    :param profiles: Profile keys in DataManager given as list of strings.
    :return: Writes filtered profiles to DataManager under the key 'profilesCons' in a dictionary with keys given
    by parameter profiles.
    """

    profilesFilterConsMin = chargeMinProfiles.loc[filterCons['indexCons'], :]
    profilesFilterConsMax = chargeMaxProfiles.loc[filterCons['indexCons'], :]
    profilesFilterDSMMin = chargeMinProfiles.loc[filterCons['indexDSM'], :]
    profilesFilterDSMMax = chargeMinProfiles.loc[filterCons['indexDSM'], :]
    return profilesFilterConsMin, profilesFilterConsMax, profilesFilterDSMMin, profilesFilterDSMMax


def socProfileSelection(profilesMin, profilesMax, filter, alpha):
    '''
    Selects the nth highest value for each hour for min (max profiles based on the percentage given in parameter
    'alpha'. If alpha = 10, the 10%-biggest (10%-smallest) value is selected, all other values are disregarded.
    Currently, in the Venco reproduction phase, the hourly values are selected independently of each other. min and max
    profiles have to have the same number of columns.

    :param profilesMin: Profiles giving minimum hypothetic SOC values to supply the driving demand at each hour
    :param profilesMax: Profiles giving maximum hypothetic SOC values if vehicle is charged as soon as possible
    :param filter: Filter method. Currently implemented: 'singleValue'
    :param alpha: Percentage, giving the amount of profiles whose mobility demand can not be fulfilled after selection.
    :return: Returns the two profiles 'SOCMax' and 'SOCMin' in the same time resolution as input profiles.
    '''

    noProfiles = len(profilesMin)
    noProfilesFilter = int(alpha / 100 * noProfiles)
    if filter == 'singleValue':
        profileMinOut = profilesMin.iloc[0, :].copy()
        for col in profilesMin:
            profileMinOut[col] = min(profilesMin[col].nlargest(noProfilesFilter))

        profileMaxOut = profilesMax.iloc[0, :].copy()
        for col in profilesMax:
            profileMaxOut[col] = max(profilesMax[col].nsmallest(noProfilesFilter))

    # elif params['filter'] == "profile"
    # ToDo: Profile specific filtering
    else:
        # review have you considered implementing your own error like class FilterError(Exception): pass which would give the user an additional hint on what went wrong?
        raise ValueError('You selected a filter method that is not implemented.')
    return profileMinOut, profileMaxOut


def normalizeProfiles(scalars, socMin, socMax, normReference):
    # ToDo: Implement a normalization to the maximum of a given profile

    '''
    Normalizes given profiles with a given scalar reference.

    :param scalars: Input scalars for VencoPy for e.g. battery capacity
    :param socMin: Minimum SOC profile subject to normalization
    :param socMax: Minimum SOC profile subject to normalization
    :param normReference: Reference that is taken for normalization. This has to be given in scalar input data.
    :return: Writes the normalized profiles to the DataManager under the specified keys
    '''

    normReference = scalars.loc[normReference, 'value']
    try:
        socMinNorm = socMin.div(float(normReference))
        socMaxNorm = socMax.div(float(normReference))

    except ValueError:
        # review general if " is used instead of ' the escaping of \' is not necessary
        # review general so is this not a problem at all if this happens? As I understand this code, socMin and socMax would be unchanged by this function call
        print('There was a value error. I don\'t know what to tell you.')
    return socMinNorm, socMaxNorm


def filterConsProfiles(profile, filterCons, critCol):
    '''
    Filter out all profiles from given profile types whose boolean indices (so far DSM or cons) are FALSE.

    :param profiles: profile identifiers given as list of strings referencing to DataManager keys
    :param dmgrNames: Identifiers given as list of string to store filtered profiles back into the DataManager
    :return: Stores filtered profiles in the DataManager under keys given in dmgrNames
    '''

    # review general could the filterCons and critCol not be hardcoded or sotred in a hidden data structure, so that it has not to be passed directly between functions? A class could achieve this goal easily (providing a hidden data structure in the shape of an attribute) making the code more structured?
    outputProfile = profile.loc[filterCons[critCol], :]
    return outputProfile


# so far not used. Plug profiles are aggregated in the action aggregateProfiles.
def considerProfiles(profiles, consider, colStart, colEnd, colCons):
    profilesOut = profiles.copy()

    try:
            profilesOut = profiles[consider[colCons].astype('bool'), colStart: colEnd]
    except KeyError:
        # review general: these are silent fails. How should the user react? Can this create a data problem downstream? Is this invalidating your results or is this nothing to bother at all? It is not clear from the error message. Also key is a bit unclear in this context.
        print("Key Error. "
            "The key {} is not part of {}".format(colCons, consider))
    return profilesOut


def aggregateProfiles(profilesIn):
    '''
    This action aggregates all single-vehicle profiles that are considered to one fleet profile. There is a separate
    action for the aggregation of plug profiles since it is not corrected by another driving cycle such as consumption
    related profiles.

    :param profiles: DataManager key of the plug profiles subject to aggregation
    :return: Writes profile to DataManager under the key 'chargeAvailProfile_out'
    '''

    # Typecasting is necessary for aggregation of boolean profiles
    profilesOut = profilesIn.iloc[0, :].astype('float64', copy=True)
    lenProfiles = len(profilesIn)

    # review have you considered using pandas dataframe .T to transpose, use sum to get the sum of each column and then divide by lenProfiles? This would be more concise in writing and more performant than a python loop
    for colidx in profilesIn:
        profilesOut[colidx] = sum(profilesIn.loc[:, colidx]) / lenProfiles
    return profilesOut


def correctProfiles(scalars, profiles, profType):
    '''
    This action scales given profiles by a correction factor. It was written for VencoPy scaling consumption data
    with the more realistic ARTEMIS driving cycle.

    :param profiles: A list of strings giving the keys of the profile types that should be corrected according to the
    ARTEMIS drive cycle.
    :param profType: A list of strings specifying if the given profile type is an electric or a fuel profile.
    profType has to have the same length as profiles.
    :param dmgrNames: List of strings specifying the keys under which the resulting profile types will be written to
    the DataManager.
    :return: Writes the corrected profiles to the DataManager under the keys given in dmgrNames
    '''

    profilesOut = profiles.copy()
    if profType == 'electric':
        consumptionElectricNEFZ = scalars.loc['Verbrauch NEFZ CD', 'value']
        consumptionElectricArtemis = scalars.loc['Verbrauch Artemis mit NV CD', 'value']
        corrFactor = consumptionElectricArtemis / consumptionElectricNEFZ

    elif profType == 'fuel':
        consumptionFuelNEFZ = scalars.loc['Verbrauch NEFZ CS', 'value']
        consumptionFuelArtemis = scalars.loc['Verbrauch Artemis mit NV CS', 'value']
        corrFactor = consumptionFuelArtemis / consumptionFuelNEFZ

    else:
        # review I expect raising an exception here. Would it not be a problem if the processing continues silently?
        print('Either parameter "profType" is not given or not assigned to either "electric" or "fuel".')

    # review same like above:
    # review have you considered using pandas dataframe .T to transpose, use sum to get the sum of each column and then divide by lenProfiles? This would be more concise in writing and more performant than a python loop
    for colIdx in profiles.index:
        profilesOut[colIdx] = corrFactor * profiles[colIdx]
    return profilesOut



# -----OUTPUT PROCESSING-------------------------------------------------------

def cloneAndWriteProfiles(profile, linkDict, noOfHoursOutput, technologyLabel, filename):
    '''
    This action clones daily profiles to cover a whole year.

    :param profiles: List of strings specifying the DataManager keys referencing the profile types for cloning
    :param technologies: List of strings of technologies that are taken into account for cloning (so far just copying)
    :param nodes: Data nodes that the profiles are copied to.
    :return: Writes the data to the specified REMix directory
    '''

    dfProfile = pd.DataFrame(profile).iloc[:, 0]

    # initialize config
    cfg = yaml.load(open(linkDict['linkTSConfig']))
    linkRmx = linkDict['linkTSREMix']

    df = createEmptyDataFrame(technologyLabel, noOfHoursOutput, cfg['Nodes'])
    # review is this correct? What happens when noOfHoursOutput/len(profile) is smaller then 0? Then noOfClones would be negative and I am not sure if this would be coerced to 0 by the following int type cast later on. Is this handled upstream in the call chain?
    noOfClones = noOfHoursOutput / len(profile) - 1

    # review the int type cast could have a nasty side effect, as it is behaving like a floor operation for the float division above. Is this intended?
    profileCloned = profile.append([profile] * int(noOfClones), ignore_index=True)

    if len(profileCloned) < noOfHoursOutput:
        subHours = noOfHoursOutput - len(profileCloned)
        profileCloned = profileCloned.append(profile[range(subHours)], ignore_index=True)

    # review this .copy() seems to be redundant if createEmptyDataFrame above indeed creates a fresh new empty
    # dataframe. Am I missing something here?
    profilesOut = df.copy()

    for i in cfg['NonNullNodes']:
        profilesOut.loc[:, i] = np.round(profileCloned, 3)

    profilesOut.to_csv(linkRmx + '/' + filename + '.csv', index=False)


def createEmptyDataFrame(technologyLabel, numberOfHours, nodes):
    df = pd.concat([pd.DataFrame([i], columns=['']) for i in range(1, numberOfHours + 1)], ignore_index=True)
    df[' '] = technologyLabel  # Add technology column
    df = df[[' ', '']]  # Re-arrange columns order

    # review if nodes is a list of column labels then one could also write it like this: df[nodes] = 0 instead of the explicit loop. I am not 100% sure of the syntax but there is a way to write this without a loop. Should be detailed in pandas indexing docu
    for i in nodes:
        df[i] = 0

    s = df[''] < 10
    s1 = (df[''] >= 10) & (df[''] < 100)
    s2 = (df[''] >= 100) & (df[''] < 1000)
    s3 = df[''] >= 1000

    # review: there exists the python string formatting mini language which provides padding of strings (also leading).
    # see here: https://docs.python.org/3.4/library/string.html#format-specification-mini-language
    #  I think with a format string of the shape 't'+'{0:0<4.0d}'.format(x) would result for all four lines below in
    #  the correct output. Then also lines 894 to 897 would be superfluous.

    df.loc[s, ''] = df.loc[s, ''].apply(lambda x: "{}{}".format('t000', x))
    df.loc[s1, ''] = df.loc[s1, ''].apply(lambda x: "{}{}".format('t00', x))
    df.loc[s2, ''] = df.loc[s2, ''].apply(lambda x: "{}{}".format('t0', x))
    df.loc[s3, ''] = df.loc[s3, ''].apply(lambda x: "{}{}".format('t', x))
    return df


def writeProfilesToCSV(dmgr, config, params):
    '''
    Writes the profiles specified in parameter profiles to a csv file.
    :param dmgrKeys: Data Manager Keys under which the profiles for writing are stored.
    :param outputFormat: Specification of output format. Can be either "singleFile" or "multiFile".
    :param strAdd: Adds a string to the written .csv files.
    :return: -
    '''

    length = {}
    data = []
    for iprof in params['dmgrKeys']:
        data.append(dmgr[iprof])
        length[iprof] = len(dmgr[iprof])

    data_df = pd.concat(data, axis=1)
    data_df.columns = params['dmgrKeys']

    if params['outputFormat'] == 'singleFile':
        data_df.to_csv(dmgr['linkDict']['linkOutput'] + 'vencoOutput_' + params['stradd'] + '.csv')
    elif params['outputFormat' == 'multiFile']:
        for iprof in params['dmgrKeys']:
            prof = dmgr[iprof]
            prof.to_csv(dmgr['linkDict']['linkOutput'] + '/vencoOutput' + iprof + params['stradd'] + '.csv')


def appendOutputProfiles(dmgr, config, params):
    """

    :param dmgr:
    :param config:
    :param params:
    :return:
    """
    strDict = composeStringDict(params['pre'], params['names'], params['post'])
    # review general these kind of prints can distract the user if the code is published, as there is no context
    # to hint on what is displayed and why. Would it make sense to provide additional information or to remove it
    # entirely?
    print(strDict)
    dataDict = {}
    for key, strList in strDict.items():
        dfList = []
        for strIdx in strList:
            df = pd.read_csv(params['link'] + '/' + strIdx)
            df.ix[df.iloc[:, 0] == 'BEV', 0] = strIdx[0:5]
            df.rename(columns={'Unnamed: 1':' '}, inplace=True)
            dfList.append(df)
        dataDict[key] = dfList
    print(dataDict)

    resultDict = {}
    for key, value in dataDict.items():
        resultDict[key] = pd.concat(value)
        resultDict[key].to_csv(index=False,
                               path_or_buf=params['outputDir'] + params['outputPre'] +
                                           key + params['outputPost'] + '.csv',
                               float_format = '%.3f')

def composeStringDict(pre, name, post):
    dict = {}
    # review name implies a single string name or alike, however the loop implies it to be a list of names. Would it be more precise if name would be renamed into names?
    for nIdx in name:
        listStr = []
        for preIdx, postIdx in zip(pre, post):
            str = preIdx + nIdx + postIdx + '.csv'
            listStr.append(str)
        dict[nIdx] = listStr
    return dict

