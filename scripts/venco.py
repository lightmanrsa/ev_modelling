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



# shutil: Link library
# pathlib: Objectoriented path mannipulation
# glob: Linux path syntax



####-------------------GENERAL------------------------------####
# ToDo: Explicit strings from current Excel file in the code. Is it possible to implement that better???

# -----INPUT-----------------------------------

def readVencoConfig(cfgLink):
    config = yaml.load(open(cfgLink), Loader=yaml.SafeLoader)
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
    return (linkDict_out)

def readInputScalar(fileLink):
    input_raw = pd.read_excel(fileLink,
                              header=5,
                              usecols="A:E",
                              skiprows=0)
    df_scalar = input_raw.loc[:, ~input_raw.columns.str.match('Unnamed')]
    df_out = df_scalar.set_index('parameter')
    return (df_out)

def readInputCSV(file_link):
    input_raw = pd.read_csv(file_link, header=4)
    df_out = input_raw.loc[:, ~input_raw.columns.str.match('Unnamed')]
    return (df_out)

def stringToBoolean(df):
    dict_bol = {'WAHR': True,
                'FALSCH': False}
    df_out = df.replace(to_replace=dict_bol, value=None)
    return (df_out)

def readInputBoolean(file_link):
    input_raw = readInputCSV(file_link)
    df_out = stringToBoolean(input_raw)
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

    print('Reading Venco input scalars, drive profiles and boolean plug profiles')

    scalars = readInputScalar(linkDict['linkScalars'])
    driveProfiles_raw = readInputCSV(linkDict['linkDriveProfiles'])
    plugProfiles_raw = readInputBoolean(linkDict['linkPlugProfiles'])

    print('There are ' + str(len(driveProfiles_raw)) + ' drive profiles and ' +
                    str(len(driveProfiles_raw)) + ' plug profiles.')

    return linkDict, scalars, driveProfiles_raw, plugProfiles_raw


    # dmgr['scalars'] = scalars
    # dmgr['driveProfiles_raw'] = driveProfiles_raw
    # dmgr['plugProfiles_raw'] = plugProfiles_raw


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

    return(scalarsProc)

# -----CALCULATION OF PROFILES-------------------------------------------------------


def calcConsumptionProfile(driveProfiles, scalars):
    '''
    Calculates electrical consumption profiles from drive profiles assuming specific consumption (in kWh/100 km)
    given in scalar input data file.

    :return: Returns the consumption profile in same format and length as driveProfiles but scaled with the specific
    consumption assumption.

    '''

    consumptionProfiles = driveProfiles.copy()
    consumptionProfiles = consumptionProfiles * float(scalars.loc['Verbrauch NEFZ CD', 'value']) / 100
    return(consumptionProfiles)


def calcChargeProfile(plugProfiles, scalars):
    '''
    Calculates the maximum possible charge power based on the plug profile assuming the charge column power
    given in the scalar input data file (so far under Panschluss).

    :return: Returns scaled plugProfile in the same format as plugProfiles.

    '''

    chargeProfiles = plugProfiles.copy()
    chargeProfiles = chargeProfiles * float(scalars.loc['Panschluss', 'value'])
    return(chargeProfiles)


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
        devCrit = chargeMaxProfiles[str(nHours - 1)].sum() - chargeMaxProfiles[str(0)].sum()
        print(devCrit)
        idxIt += 1

    chargeMaxProfiles.drop(labels='newCharge', axis='columns', inplace=True)
    return(chargeMaxProfiles)


def calcChargeProfileUncontrolled(chargeMaxProfiles, scalarsProc):
    '''
    Calculates the uncontrolled electric charging based on SoC Max profiles for each hour for each profile.

    :return: Returns profiles for uncontrolled charging under the assumption that charging occurs as soon as a
    vehicle is connected to the grid up to the point that the maximum battery SOC is reached or the connection
    is interrupted. DataFrame has the same format as chargeMaxProfiles.

    '''

    chargeMaxProfiles = chargeMaxProfiles.copy()
    chargeProfilesUncontrolled = chargeMaxProfiles.copy()
    nHours = scalarsProc['noHours']
    # ToDo: lastHour
    # ToDo: erradicate else-statement by indexing -1

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

    return(chargeProfilesUncontrolled)
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
    consumptionPower = scalars.loc['Verbrauch NEFZ CD', 'value']
    consumptionFuel = scalars.loc['Verbrauch NEFZ CS', 'value']

    # initialize data set for filling up later on
    driveProfilesFuelAux = chargeMaxProfiles.copy()
    nHours = scalarsProc['noHours']
    for idx in range(nHours):
        if idx != 0:
            driveProfilesFuelAux[str(idx)] = (consumptionFuel / consumptionPower) * \
                                             (driveProfiles[str(idx)] * consumptionPower / 100 -
                                              chargeProfilesUncontrolled[str(idx)] -
                                              (chargeMaxProfiles[str(idx - 1)] - chargeMaxProfiles[str(idx)]))
    # Setting value of hour=0 equal to the average of hour=1 and last hour
    driveProfilesFuelAux[str(0)] = (driveProfilesFuelAux[str(nHours - 1)] + driveProfilesFuelAux[str(1)])/2
    driveProfilesFuelAux = driveProfilesFuelAux.round(4)
    return(driveProfilesFuelAux)


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

    # For validation
    # pd.set_option('display.max_columns', 30)
    # pd.set_option('display.width', 500)
    # caseids = [4803, 84490, 93345, 112106]
    # print(chargeMinProfiles.ix[np.isin(chargeMinProfiles['CASEID'], caseids), :nHours + 2], flush=True)

    chargeMinProfiles.drop('newCharge', axis='columns', inplace=True)
    return(chargeMinProfiles)
    # datalogger.info(chargeMinProfiles)


def createRandNo(driveProfiles, setSeed=1):
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

    return(randNos)


def calcIndices(chargeProfiles,
                consumptionProfiles,
                driveProfiles,
                driveProfilesFuelAux,
                randNos,
                scalars,
                fuelDriveTolerance,
                isBEV):
    # Maybe make this function neater by giving filtering functions as params or in a separate file??

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

    return(filterCons_out)

    # Debugging and Checking
    # pd.set_option('display.max_columns', None, 'display.max_rows', 20)
    # print(filterCons.iloc[0:20, :])
    # print(len(np.where(filterCons['indexCons'])))


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

    # consumptionProfiles = dmgr['consumptionProfiles'].copy()
    # driveProfilesFuelAux = dmgr['driveProfilesFuelAux'].copy()
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

    return(electricPowerProfiles)
    # datalogger.info(electricPowerProfiles)


def filterConsBatProfiles(chargeMaxProfiles, chargeMinProfiles, filterCons, minValue, maxValue):
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

    return(chargeMaxProfilesDSM, chargeMinProfilesDSM)

    # datalogger.info(len(chargeMaxProfilesDSM))

    # pd.set_option('display.width', 300)
    # pd.set_option('display.max_rows', None)
    # print(filterCons.iloc[1:50, :])
    # print(chargeMaxProfilesDSM.iloc[1:50, :])
    # print(chargeMinProfilesDSM.iloc[1:50, :])
    # print(chargeMaxProfilesDSM.ix[~filterCons['indexDSM'].astype('bool'),:])


def indexFilter(chargeMaxProfiles, chargeMinProfiles, filterCons):
    '''
    Filters out profiles where indexCons is False.

    :param profiles: Profile keys in DataManager given as list of strings.
    :return: Writes filtered profiles to DataManager under the key 'profilesCons' in a dictionary with keys given
    by parameter profiles.
    '''

    profilesFilterConsMin = chargeMinProfiles.loc[filterCons['indexCons'], :]
    profilesFilterConsMax = chargeMaxProfiles.loc[filterCons['indexCons'], :]
    profilesFilterDSMMin = chargeMinProfiles.loc[filterCons['indexDSM'], :]
    profilesFilterDSMMax = chargeMinProfiles.loc[filterCons['indexDSM'], :]

    return(profilesFilterConsMin, profilesFilterConsMax, profilesFilterDSMMin, profilesFilterDSMMax)


def socProfileSelection(profilesMin, profilesMax, filter, alpha):
    '''
    Selects the nth highest value for each hour for min (max) profiles based on the percentage given in parameter
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
        raise ValueError('You selected a filter method that is not implemented.')

    return(profileMinOut, profileMaxOut)


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
        # for key, value in profiles.items():
        #     outputProfiles.append(value.div(float(normReference)))
        socMinNorm = socMin.div(float(normReference))
        socMaxNorm = socMax.div(float(normReference))

    except ValueError:
        print('There was a value error. I don\'t know what to tell you.')

    return(socMinNorm, socMaxNorm)
    # datalogger.info(outputProfiles)


def filterConsProfiles(profile, filterCons, critCol):
    '''
    Filter out all profiles from given profile types whose boolean indices (so far DSM or cons) are FALSE.

    :param profiles: profile identifiers given as list of strings referencing to DataManager keys
    :param dmgrNames: Identifiers given as list of string to store filtered profiles back into the DataManager
    :return: Stores filtered profiles in the DataManager under keys given in dmgrNames
    '''

    outputProfile = profile.loc[filterCons[critCol], :]
    return(outputProfile)


# so far not used. Plug profiles are aggregated in the action aggregateProfiles.
def considerProfiles(profiles, consider, colStart, colEnd, colCons):
    profilesOut = profiles.copy()

    try:
            profilesOut = profiles[consider[colCons].astype('bool'), colStart: colEnd]
    except KeyError:
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

    for colidx in profilesIn:
        profilesOut[colidx] = sum(profilesIn.loc[:, colidx]) / lenProfiles

    return(profilesOut)
    # datalogger.info(profiles_out)


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
        print('Either parameter "profType" is not given or not assigned to either "electric" or "fuel".')

    for colIdx in profiles.index:
        profilesOut[colIdx] = corrFactor * profiles[colIdx]

    return(profilesOut)




##### DEPRECATED? ######
# @action('VencoPy')
# def aggregateProfiles(dmgr, config, params):
#
#     # TODO: Set column name to pname or use list instead of dataframe as looping data type
#     '''
#     This action aggregates profiles based on building the arithmetic mean for each hour. It thus transforms
#     single-vehicle profiles to one fleet profile per profile type.
#
#     :param profiles: List of strings of DataManager keys referencing to profiles for aggregation.
#     :param dmgrNames: List of strings that results get written to.
#
#     :return: Writes aggregated profiles to DataManager under the keys specified in dmgrNames.
#     '''
#
#     profiles = {}
#     for prof in params['profiles']:
#         profiles[prof] = pd.DataFrame(dmgr[prof])
#
#     profiles_out = []
#     for pname, prof in profiles.items():
#         # initiating looping dataframe
#         profiles_loop = pd.DataFrame(data = profiles[next(iter(profiles))].iloc[0, :],
#                                         dtype = float,
#                                         copy = True)
#         profiles_loop.columns = [pname] # renaming the 1-column DataFrame
#         noProfiles = len(prof)
#
#         # aggregation
#         for colidx in prof:  # colidx: column index
#             # profiles_loop.iloc[int(colidx), :] = sum(prof.loc[:, colidx]) / len(prof.loc[:, colidx])
#             profiles_loop.iloc[int(colidx), :] = sum(prof.loc[:, colidx]) / noProfiles
#
#         profiles_out.append(profiles_loop)
#
#     # Write profiles to datamanager for given profile names
#     for idx in range(len(params['dmgrNames'])):
#         dmgr[params['dmgrNames'][idx]] = profiles_out[idx]

# -----OUTPUT PROCESSING-------------------------------------------------------

# @action('VencoPy')
def cloneProfilesToYear(profile, linkDict, noOfHoursOutput, technologyLabel, filename):
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

    # df = pd.DataFrame(columns=['technologies', 'timestep', nodes])
    # df = df.set_index(['technologies', 'timestep'])

    # df = pd.concat([pd.DataFrame([i], columns=['']) for i in range(1, 8761)], ignore_index=True)
    # df[' '] = technologyLabel  # Add technology column
    # df = df[[' ', '']]  # Re-arrange columns order
    #
    # for i in cfg['Nodes']:
    #     df[i] = 0
    #
    # s = df[''] < 10
    # s1 = (df[''] >= 10) & (df[''] < 100)
    # s2 = (df[''] >= 100) & (df[''] < 1000)
    # s3 = df[''] >= 1000
    #
    # df.loc[s, ''] = df.loc[s, ''].apply(lambda x: "{}{}".format('t000', x))
    # df.loc[s1, ''] = df.loc[s1, ''].apply(lambda x: "{}{}".format('t00', x))
    # df.loc[s2, ''] = df.loc[s2, ''].apply(lambda x: "{}{}".format('t0', x))
    # df.loc[s3, ''] = df.loc[s3, ''].apply(lambda x: "{}{}".format('t', x))

    df = createEmptyDataFrame(technologyLabel, noOfHoursOutput, cfg['Nodes'])
    noOfClones = noOfHoursOutput / len(profile) - 1

    # for name, prof in profiles.items():
    #     profiles[name] = prof.append([prof] * 364, ignore_index=True)

    profileCloned = profile.append([profile] * int(noOfClones), ignore_index=True)

    if len(profileCloned) < noOfHoursOutput:
        subHours = noOfHoursOutput - len(profileCloned)
        profileCloned = profileCloned.append(profile[range(subHours)], ignore_index=True)

    # print(profiles)

    profilesOut = df.copy()
    # df_chargeAv = df.copy()
    # df_BatMax = df.copy()
    # df_BatMin = df.copy()
    # df_DrivePow = df.copy()
    # df_UncontrCharge = df.copy()

    for i in cfg['NonNullNodes']:
        profilesOut.loc[:, i] = np.round(profileCloned, 3)
        # df_chargeAv[i] = np.round(profiles['plugProfilesCons_out'] , 3)
        # df_BatMax.loc[:, i] = np.round(profiles['SOCMax_out'], 3)
        # df_BatMin.loc[:, i] = np.round(profiles['SOCMin_out'], 3)
        # df_DrivePow.loc[:, i] = np.round(profiles['electricPowerProfiles_out'], 3)
        # df_UncontrCharge.loc[:, i] = np.round(profiles['chargeProfilesUncontrolled_out'], 3)

    # datalogger.info(df_chargeAv)

    profilesOut.to_csv(linkRmx + '/' + filename + '.csv', index=False)
    # df_chargeAv.to_csv(linkRmx + '/' + params['outputStrPre'] + 'chargeAvail' + params['outputStrPost'] + '.csv',
    #                    index=False)
    # df_BatMax.to_csv(linkRmx + '/' + params['outputStrPre'] + 'batMax' + params['outputStrPost'] + '.csv',
    #                  index=False)
    # df_BatMin.to_csv(linkRmx + '/' + params['outputStrPre'] + 'batMin' + params['outputStrPost'] + '.csv',
    #                  index=False)
    # df_DrivePow.to_csv(linkRmx + '/' + params['outputStrPre'] + 'drivePower' + params['outputStrPost'] + '.csv',
    #                    index=False)
    # df_UncontrCharge.to_csv(linkRmx + '/' + params['outputStrPre'] + 'uncontrCharge' + params['outputStrPost'] + '.csv',
    #                         index=False)


def createEmptyDataFrame(technologyLabel, numberOfHours, nodes):
    df = pd.concat([pd.DataFrame([i], columns=['']) for i in range(1, numberOfHours + 1)], ignore_index=True)
    df[' '] = technologyLabel  # Add technology column
    df = df[[' ', '']]  # Re-arrange columns order

    for i in nodes:
        df[i] = 0

    s = df[''] < 10
    s1 = (df[''] >= 10) & (df[''] < 100)
    s2 = (df[''] >= 100) & (df[''] < 1000)
    s3 = df[''] >= 1000

    df.loc[s, ''] = df.loc[s, ''].apply(lambda x: "{}{}".format('t000', x))
    df.loc[s1, ''] = df.loc[s1, ''].apply(lambda x: "{}{}".format('t00', x))
    df.loc[s2, ''] = df.loc[s2, ''].apply(lambda x: "{}{}".format('t0', x))
    df.loc[s3, ''] = df.loc[s3, ''].apply(lambda x: "{}{}".format('t', x))

    return(df)


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
    for nIdx in name:
        listStr = []
        for preIdx, postIdx in zip(pre, post):
            str = preIdx + nIdx + postIdx + '.csv'
            listStr.append(str)
        dict[nIdx] = listStr
    return(dict)


### Questions to Ben ###
# GENERAL
# Does it make sense to read and write a lot within functions/actions or rather to read once at the beginning of
# a function and write it to a function-specific variable?

# Does it make sense to give run specific parameters as param to the action or rather in the input_data file?

# in readInputScalar(): Why doesn't df_scalar.set_index('parameter') doesn't set the parameter column as the index column?

# in procProfiles(): Why does the following line yield a DataFrame with correct columns and indices but with only
# NaNs in the data columns?
# profiles = pd.DataFrame(data=df_profilesRaw, index=df_profilesRaw.index, columns=params['profiles'])

# in printProfiles(): The function gets a number of strings as identifiers for profiles stored in the dmgr. Thus, in
# the action decorator, the required profiles cannot be specified. Is this OK? Can I access the parameters already in
# the action call?


## SANDBOX ##

# @action('VencoPy', ['driveProfiles', 'plugProfiles_raw'], ['profilesInput'])
# def procProfiles_old (dmgr, config, params):
#
#
#     driveProfiles = dmgr['driveProfiles'].set_index(['CASEID', 'PKWID'])
#     plugProfiles = dmgr['plugProfiles_raw'].set_index(['CASEID', 'PKWID'])
#     driveProfiles = driveProfiles.stack() # outputs an indexed series
#     plugProfiles = plugProfiles.stack() # outputs an indexed series
#
#     driveProfiles.index.names = ['CASEID', 'PKWID', 'hour']
#     plugProfiles.index.names = ['CASEID', 'PKWID', 'hour']
#     df_driveProfiles = pd.DataFrame(data=driveProfiles,
#                                     index=driveProfiles.index,
#                                     columns=["value"])
#     df_plugProfiles = pd.DataFrame(data=plugProfiles,
#                                     index=plugProfiles.index,
#                                     columns=["value"])
#
#     # Merging both data frames into one frame with two columns since both series share the three indices
#     # 'CASEID', 'PKWID' and 'hour'
#     df_profilesRaw = pd.merge(df_driveProfiles, df_plugProfiles, on=['CASEID', 'PKWID', 'hour'], how='outer')
#     df_profiles = df_profilesRaw.rename(index=str, columns={'value_x': 'driveProfile',
#                                                             'value_y': 'plugProfile'})
#     df_profiles = df_profiles.reset_index(level=['CASEID', 'PKWID', 'hour'])
#     df_profiles.loc[:,'CASEID'] = df_profiles.CASEID.astype(np.int)
#     df_profiles.loc[:, 'PKWID'] = df_profiles.PKWID.astype(np.int)
#     df_profiles.loc[:, 'hour'] = df_profiles.hour.astype(np.int)
#     dmgr['profilesInput'] = df_profiles
#     # print(df_profiles.info())
#     # print(df_profiles.head)

# FOR LOOP FROM calcIndices()
# for ridx in range(len(boolIndices)):
#     boolIndices.ix[ridx, 'bolFuelDriveTolerance'] = sum(driveProfilesFuelAux.ix[ridx, dataColStart : dataColEnd]) \
#                                                      * boolBEV < fuelDriveTolerance
#     boolIndices.ix[ridx, 'bolMinDailyMileage'] = (sum(driveProfiles.ix[ridx, dataColStart : dataColEnd]) >
#          2 * randNos.ix[ridx, 'randNo'] * minDailyMileage +
#          (1-randNos.ix[ridx, 'randNo']) * minDailyMileage * params['isBEV2030'])
#     boolIndices.ix[ridx, 'indexCons'] = boolIndices.ix[ridx,  'bolFuelDriveTolerance'] and \
#                            boolIndices.ix[ridx, 'bolMinDailyMileage']
#     boolIndices.ix[ridx, 'bolConsumption'] = sum(consumptionProfiles.ix[ridx, dataColStart : dataColEnd]) < \
#                                      sum(chargeProfiles.ix[ridx, dataColStart : dataColEnd])
#     boolIndices.ix[ridx, 'bolSuffBat'] = sum(consumptionProfiles.ix[ridx, dataColStart: dataColEnd]) < \
#                                              batSize * (socMax - socMin)
#     boolIndices.ix[ridx, 'indexDSM'] = boolIndices.ix[ridx,  'bolConsumption'] and \
#                            boolIndices.ix[ridx, 'bolSuffBat']