# -*- coding:utf-8 -*-

__version__ = '0.1.0'
__maintainer__ = 'Niklas Wulff 16.04.2019'
__email__ = 'Niklas.Wulff@dlr.de'
__birthdate__ = '15.04.2019'
__status__ = 'dev'  # options are: dev, test, prod

# This script holds the function definitions and actions for VencoPy.
# df = dataframe, dmgr = data manager,

import os
import sys

sys.path.append(os.path.abspath('C:/REMix-OaM/OptiMo/projects/REMix-tools/remixPlotting'))

import numpy as np
import yaml
import pandas as pd
from functools import reduce
from random import seed
from random import random


class VencoError(Exception):
    pass

# shutil: Link library
# pathlib: Objectoriented path mannipulation
# glob: Linux path syntax



####-------------------GENERAL------------------------------####
# ToDo: Explicit strings from current Excel file in the code. Is it possible to implement that better???

# -----INPUT-----------------------------------

def readVencoConfig(cfgLink):
    config = yaml.load(open(cfgLink))
    # print(config)
    return (config)

def initializeLinkMgr(vencoConfig):     # allocate explicit types to documentation, dict = manager
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
                              skiprows=0) # ,skipfooter=12
    df_scalar = input_raw.loc[:, ~input_raw.columns.str.match('Unnamed')]
    df_out = df_scalar.set_index('parameter')
    return (df_out)

def readInputCSV(file_link):
    input_raw = pd.read_csv(file_link, header=4) #

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


# @action('VencoPy')
def readVencoInput(linkConfig):
    '''
    Initializing action for VencoPy-specific config-file, link dictionary and data read-in. The config file has
    to be a dictionary in a .yaml file with the format
    linksRelative:
        data:
        functions:
        plots:
        scripts:
        tsConfig:
    linksAbsolute:
        REMixTimeseriesPath:
    files:
        inputDataScalars:
        inputDataDriveProfiles:
        inputDataPlugProfiles:

    :param linkConfig: The config link where all other links are in.

    :return: Writes four files to the DataManager: A link dictionary, scalars, drive profile data and plug profile
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
# @action('VencoPy')
def procProfiles(dmgr, config, params):
    # ToDo: generalize more so any data format can be taken in not just CASEID, PKWID etc.
    '''
    Binds profiles given in parameter "profiles" in one DataFrame in a stacked form. So far,
    column names are explicitly given as "CASEID", "PKWID" and "hour". Additionally one column per
    given profile will be added.


    :param profiles: Profiles to be written in the DataFrame
    :param dmgrName: Name under which the resulting DataFrame is stored in the DataManager
    :return: Writes a DataFrame of the form CASEID PKWID hour prof1 prof2 ... under the specified name into the
    DataManager
    '''
    ls_profiles = []

    for prof in params['profiles']:
        profiles = dmgr[prof].copy().set_index(['CASEID', 'PKWID'])
        profiles = profiles.stack()  # outputs an indexed series

        profiles.index.names = ['CASEID', 'PKWID', 'hour']
        df_profiles = pd.DataFrame(data=profiles,
                                   index=profiles.index,
                                   columns=["value"])
        ls_profiles.append(df_profiles)

    # Merging data frames into one frame with two columns since all series share the three indices
    # 'CASEID', 'PKWID' and 'hour' right now -> to be generalized in future
    df_profilesRaw = reduce(lambda x, y: pd.merge(x, y, on=['CASEID', 'PKWID', 'hour'], how='outer'), ls_profiles)
    df_profiles = pd.DataFrame(data=df_profilesRaw, index=df_profilesRaw.index, columns=params['profiles'])
    for prof in range(len(params['profiles'])):
        df_profiles.loc[:, params['profiles'][prof]] = df_profilesRaw.iloc[:, prof]
    df_profiles = df_profiles.reset_index(level=['CASEID', 'PKWID', 'hour'])
    df_profiles.loc[:, 'CASEID'] = df_profiles.CASEID.astype(np.int)
    df_profiles.loc[:, 'PKWID'] = df_profiles.PKWID.astype(np.int)
    df_profiles.loc[:, 'hour'] = df_profiles.hour.astype(np.int)
    dmgr[params['dmgrName']] = df_profiles
    datalogger.debug(df_profiles)


# @action('VencoPy')
def indexProfile(driveProfile_raw, plugProfiles_raw, indices):
    '''
    Takes raw data as input and indices different profiles with the specified index columns und an unstacked form.

    :param profilesInput: The profiles that should be indexed.
    :param indices: Index columns that are assigned as indices.
    :return: Indexed profiles are written to the DataManager under tha names specified by param profilesDmgr
    '''

    # for iprof in range(len(params['profilesInput'])):  # input profiles
    #         profiles = dmgr[params['profilesInput'][iprof]].copy()
    #         profiles_new = profiles.set_index(list(params['indices']))
    #         profiles_new = profiles_new.set_index(profiles_new.groupby(level=0).cumcount(),
    #                                               append=True)
    #         # profiles.index.names = params['indices']
    #         return(profiles_new)
    #         dmgr[params['profilesDmgr'][iprof]] = profiles_new

    driveProfile = driveProfile_raw.set_index(list(indices))
#    driveProfile = driveProfile_raw.set_index(driveProfile.groupby(level=0).cumcount(),
#                                          append=True)

    plugProfile = plugProfiles_raw.set_index(list(indices))
    # plugProfile = plugProfiles_raw.set_index(plugProfile.groupby(level=0).cumcount(),
    #                                       append=True)

    return (driveProfile, plugProfile)

    # else:
    #     raise VencoError("The length of input profiles doesn't match the length of profile names. "
    #                      "Please check you parameters given in user.yaml")


# @action('VencoPy')
def procScalars(driveProfiles_raw, plugProfiles_raw, driveProfiles, plugProfiles):
    #ToDo: Other scalars derived from input??
    '''
    Calculates some scalars from the input data such as the number of hours of drive and plug profiles, the number of
    profiles etc.

    :return: Writes a dictionary to the DataManager under the key 'scalarsProc'
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
    # else:
        #datalogger.warn('Length of drive and plug input data differ! This will at the latest crash in calculating'
        #                'profiles for SoC max')

    return(scalarsProc)

# -----CALCULATION OF PROFILES-------------------------------------------------------

# @action('VencoPy')
def calcConsumptionProfile(driveProfiles, scalars):
    '''
    Calculates electrical consumption profiles from drive profiles assuming specific consumption (in kWh/100 km)
    given in scalar input data file.

    :return: Writes the calculated profiles to the DataManager under the key 'consumptionProfiles'
    '''

    consumptionProfiles = driveProfiles.copy()
    consumptionProfiles = consumptionProfiles * float(scalars.loc['Verbrauch NEFZ CD', 'value']) / 100
    return(consumptionProfiles)


# @action('VencoPy')
def calcChargeProfile(plugProfiles, scalars):
    '''
    Calculates the maximum possible charge power based on the plug profile assuming the charge column power
    given in the scalar input data file (so far under Panschluss).

    :return: Writes the resulting profiles to the DataManager under the key 'chargeProfiles'
    '''

    chargeProfiles = plugProfiles.copy()
    chargeProfiles = chargeProfiles * float(scalars.loc['Panschluss', 'value'])
    return(chargeProfiles)


# @action('VencoPy')
def calcChargeMaxProfiles(chargeProfiles, scalars, nIter):
    '''
    Calculates all maximum SoC profiles under the assumption that batteries are always charged as soon as they
    are plugged to the grid. Values are assured to not fall below SoC_min * battery capacity or surpass
    SoC_max * battery capacity. Relevant profiles are chargeProfile and consumptionProfile. An iteration assures
    the boundary condition of chargeMaxProfile(0) = chargeMaxProfile(len(profiles)). The number of iterations
    is given as parameter.

    :param nIter: Number of iterations to assure that the minimum and maximum value are approximately the same
    :return: Writes SoC max profiles to DataManager under the key 'chargeMaxProfiles'
    '''

    chargeMaxProfiles = dmgr['chargeProfiles'].copy()
    chargeProfiles = dmgr['chargeProfiles'].copy()
    consumptionProfiles = dmgr['consumptionProfiles'].copy()
    batCapMin = dmgr['scalars'].loc['Battery size', 'value'] * dmgr['scalars'].loc['SoCmin', 'value']
    batCapMax = dmgr['scalars'].loc['Battery size', 'value'] * dmgr['scalars'].loc['SoCmax', 'value']
    nHours = dmgr['scalarsProc']['noHours']
    nIter = params['nIter']

    idxIt = 1
    while idxIt <= nIter: #ToDo implement as for-loop
        # ToDo: np.where() replace by pd.something(),
        # ToDo: prohibit typecasting str(idx) in data preparation step colnames as integers {smell}
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
        # datalogger.info(devCrit)
        idxIt += 1

    # print(chargeMaxProfile.ix[0:20, :], flush=True)
    chargeMaxProfiles.drop(labels='newCharge', axis='columns', inplace=True)
    dmgr['chargeMaxProfiles'] = chargeMaxProfiles


# @action('VencoPy')
def calcChargeProfileUncontrolled(dmgr, config, params):
    '''
    Calculates the uncontrolled electric charging based on SoC Max profiles for each hour for each profile.

    :return: Writes uncontrolled charging profiles to Data Manager under the key 'chargeProfilesUncontrolled'
    '''

    chargeMaxProfiles = dmgr['chargeMaxProfiles'].copy()
    chargeProfilesUncontrolled = chargeMaxProfiles.copy()
    nHours = dmgr['scalarsProc']['noHours']
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

    dmgr['chargeProfilesUncontrolled'] = chargeProfilesUncontrolled
    # datalogger.info(chargeProfilesUncontrolled)


# @action('VencoPy')
def calcDriveProfilesFuelAux(dmgr, config, params):

    #ToDo: alternative vectorized format for looping over columns? numpy, pandas: broadcasting-rules
    #Profile is negative - is this on purpose? Does it make sense?

    '''
    Calculates necessary fuel consumption profile of a potential auxilliary unit (e.g. a gasoline motor) based
    on gasoline consumption given in scalar input data (in l/100 km). Auxilliary fuel is needed if an hourly
    mileage is higher than the available SoC Max in that hour.

    :return: Writes the auxilliary fuel demand to the DataManager under the key 'driveProfilesFuelAux'.
    '''

    chargeMaxProfiles = dmgr['chargeMaxProfiles'].copy()
    chargeProfilesUncontrolled = dmgr['chargeProfilesUncontrolled'].copy()
    driveProfiles = dmgr['driveProfiles'].copy()
    consumptionPower = dmgr['scalars'].loc['Verbrauch NEFZ CD', 'value']
    consumptionFuel = dmgr['scalars'].loc['Verbrauch NEFZ CS', 'value']

    # initialize data set for filling up later on
    driveProfilesFuelAux = dmgr['chargeMaxProfiles'].copy()

    nHours = dmgr['scalarsProc']['noHours']
    # datalogger.info(nHours, range(nHours))

    for idx in range(nHours):
        # testing line
        # chargeMaxProfile.ix[3, '0'] = 15.0

        # if idx == 0:
        #     driveProfilesFuelAux[str(idx)] = (consumptionFuel / consumptionPower) * \
        #                                      (driveProfiles[str(idx)] * consumptionPower / 100 -
        #                                       chargeProfilesUncontrolled[str(idx)] -
        #                                       (chargeMaxProfiles[str(nHours - 1)] - chargeMaxProfiles[str(idx)]))
        if idx != 0:
            driveProfilesFuelAux[str(idx)] = (consumptionFuel / consumptionPower) * \
                                             (driveProfiles[str(idx)] * consumptionPower / 100 -
                                              chargeProfilesUncontrolled[str(idx)] -
                                              (chargeMaxProfiles[str(idx - 1)] - chargeMaxProfiles[str(idx)]))

    # Setting value of hour=0 equal to the average of hour=1 and last hour
    driveProfilesFuelAux[str(0)] = (driveProfilesFuelAux[str(nHours - 1)] + driveProfilesFuelAux[str(1)])/2

    driveProfilesFuelAux = driveProfilesFuelAux.round(4)

    dmgr['driveProfilesFuelAux'] = driveProfilesFuelAux
    # datalogger.info(driveProfilesFuelAux)


# @action('VencoPy')
def calcChargeMinProfiles(dmgr, config, params):
    '''
    Calculates minimum SoC profiles assuming that the hourly mileage has to exactly be fulfilled but no battery charge
    is kept inspite of fulfilling the mobility demand. It represents the minimum charge that a vehicle battery has to
    contain in order to fulfill all trips.
    An iteration is performed in order to assure equality of the SoCs at beginning and end of the profile.

    :param nIter: Gives the number of iterations to fulfill the boundary condition of the SoC equalling in the first
    and in the last hour of the profile.
    ToDo param minSecurityFactor
    :return: The SoC Min profiles are written to the DataManager under the key of 'chargeMinProfiles'.
    '''

    chargeMinProfiles = dmgr['chargeProfiles'].copy()
    chargeProfiles = dmgr['chargeProfiles'].copy()
    consumptionProfiles = dmgr['consumptionProfiles'].copy()
    driveProfilesFuelAux = dmgr['driveProfilesFuelAux'].copy()
    batCapMin = dmgr['scalars'].loc['Battery size', 'value'] * dmgr['scalars'].loc['SoCmin', 'value']
    batCapMax = dmgr['scalars'].loc['Battery size', 'value'] * dmgr['scalars'].loc['SoCmax', 'value']
    consElectric = dmgr['scalars'].loc['Verbrauch NEFZ CD', 'value']
    consGasoline = dmgr['scalars'].loc['Verbrauch NEFZ CS', 'value']
    nHours = dmgr['scalarsProc']['noHours']
    nIter = params['nIter']

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
        # datalogger.info(devCrit)
        idxIt += 1

    # For validation
    # pd.set_option('display.max_columns', 30)
    # pd.set_option('display.width', 500)
    # caseids = [4803, 84490, 93345, 112106]
    # print(chargeMinProfiles.ix[np.isin(chargeMinProfiles['CASEID'], caseids), :nHours + 2], flush=True)

    chargeMinProfiles.drop('newCharge', axis='columns', inplace=True)
    dmgr['chargeMinProfiles'] = chargeMinProfiles
    # datalogger.info(chargeMinProfiles)


# @action('VencoPy')
def createRandNo(dmgr, config, params):
    '''
    Creates a random number between 0 and 1 for each profile based on driving profiles.

    :return: Write a series with the same indices as the input driving profiles in the Data Manager.
    Use the key 'randNos'
    '''
    idxData = dmgr['driveProfiles'].copy() # preparing data with the indices, next(iter(dmgr['driveProfiles'].columns))

    # print(profiles)
    # noIdxCols = len(driveProfiles.columns) - \
    #             (dmgr['scalarsProc']['dataColEnd'] - dmgr['scalarsProc']['dataColStart'])
    # print(noIdxCols)
    # df = driveProfiles.iloc[:, :noIdxCols]
    seed(1)  # seed random number generator for reproducibility

    idxData['randNo'] = np.random.random(len(idxData))
    idxData['randNo'] = [random() for _ in range(len(idxData))]  # generate one random number for each profile
    randNos = idxData.loc[:, 'randNo']

    dmgr['randNos'] = randNos


# @action('VencoPy')
def calcIndices(dmgr, config, params):
    # Maybe make this function neater by giving filtering functions as params or in a seperate file??

    '''
    This action calculates filtering indices. In the Venco reproduction stage, this is mainly if no fuel (except for
    a small number) is needed and if a minimum daily average is reached. A second index gives the value if the battery
    is large enough to fulfill the whole driving demand and if charging throughout the day supplies more energy than
    required for the trips.

    :param fuelDriveTolerance: Give a threshold value how many liters may be needed throughout the course of a day
    in order to still consider the profile.
    :param isBEV2030: Boolean value. If true, more 2030 profiles are taken into account (in general).
    :return: The bool indices are written to one DataFrame in the DataManager with the columns randNo, indexCons and
    indexDSM and the same indices as the other profiles.
    '''

    chargeProfiles = dmgr['chargeProfiles'].copy()
    consumptionProfiles = dmgr['consumptionProfiles'].copy()
    driveProfiles = dmgr['driveProfiles'].copy()
    driveProfilesFuelAux = dmgr['driveProfilesFuelAux'].copy()
    randNos = dmgr['randNos'].copy()
    boolBEV = dmgr['scalars'].loc['EREV oder BEV?', 'value']
    minDailyMileage = dmgr['scalars'].loc['Minimum daily mileage', 'value']
    batSize = dmgr['scalars'].loc['Battery size', 'value']
    socMax = dmgr['scalars'].loc['SoCmax', 'value']
    socMin = dmgr['scalars'].loc['SoCmin', 'value']
    fuelDriveTolerance = params['fuelDriveTolerance']

    boolIndices = driveProfiles.copy()

    boolIndices['randNo'] = randNos

    boolIndices['bolFuelDriveTolerance'] = driveProfilesFuelAux.sum(axis='columns') * \
                                           boolBEV < fuelDriveTolerance
    boolIndices['bolMinDailyMileage'] = driveProfiles.sum(axis='columns') > \
                                        (2 * randNos * minDailyMileage +
                                         (1 - randNos) * minDailyMileage * #.loc[:, 'randNo']
                                         params['isBEV2030'])
    boolIndices['indexCons'] = boolIndices.loc[:, 'bolFuelDriveTolerance'] & \
                               boolIndices.loc[:, 'bolMinDailyMileage']
    boolIndices['bolConsumption'] = consumptionProfiles.sum(axis=1) < \
                                    chargeProfiles.sum(axis=1)
    boolIndices['bolSuffBat'] = consumptionProfiles.sum(axis=1) < \
                                batSize * (socMax - socMin)
    boolIndices['indexDSM'] = boolIndices['indexCons'] & boolIndices['bolConsumption'] & boolIndices['bolSuffBat']

    mainlogger.info('There are ' + str(sum(boolIndices['indexCons'])) + ' considered profiles and ' + \
                    str(sum(boolIndices['indexDSM'])) + ' DSM eligible profiles.')
    boolIndices_out = boolIndices.loc[:, ['randNo', 'indexCons', 'indexDSM']]
    dmgr['boolIndices'] = boolIndices_out

    # datalogger.info(boolIndices_out)

    # print(consumptionProfiles)
    # print(dmgr['profilesInput'])

    # Debugging and Checking
    # pd.set_option('display.max_columns', None, 'display.max_rows', 20)
    # print(boolIndices.iloc[0:20, :])
    # print(len(np.where(boolIndices['indexCons'])))
    # print(dmgr['boolIndices'])


# @action('VencoPy')
def calcElectricPowerProfiles(dmgr, config, params):
    '''
    Calculates electric power profiles that serve as outflow of the fleet batteries.

    :param dmgrName: 'electricPowerProfiles'
    :param filterIndex: Can be either 'indexCons' or 'indexDSM' so far. 'indexDSM' applies stronger filters and results
    are thus less representative.
    :return: Returns electric demand from driving filtered and aggregated to one fleet. Stores the profile in the
    Data Manager under the key specified by dmgrName.
    '''

    consumptionProfiles = dmgr['consumptionProfiles'].copy()
    driveProfilesFuelAux = dmgr['driveProfilesFuelAux'].copy()
    consumptionPower = dmgr['scalars'].loc['Verbrauch NEFZ CD', 'value']
    consumptionFuel = dmgr['scalars'].loc['Verbrauch NEFZ CS', 'value']
    indexCons = dmgr['boolIndices'].loc[:, 'indexCons']
    indexDSM = dmgr['boolIndices'].loc[:, 'indexDSM']
    # datalogger.info(indexCons)

    nHours = dmgr['scalarsProc']['noHours']
    electricPowerProfiles = consumptionProfiles.copy()

    for idx in range(nHours):
        electricPowerProfiles[str(idx)] = (consumptionProfiles[str(idx)] - driveProfilesFuelAux[str(idx)] *
                                           (consumptionPower / consumptionFuel))

        if params['filterIndex'] == 'indexCons':
            electricPowerProfiles[str(idx)] = electricPowerProfiles[str(idx)] * indexCons
        elif params['filterIndex'] == 'indexCons':
            electricPowerProfiles[str(idx)] = electricPowerProfiles[str(idx)] * indexDSM

    dmgr[params['dmgrName']] = electricPowerProfiles
    # datalogger.info(electricPowerProfiles)


# @action('VencoPy')
def filterConsBatProfiles(dmgr, config, params):
    '''
    Sets all profile values with indexDSM = False to extreme values. For SoC max profiles, this means a value
    that is way higher than SoC max capacity. For SoC min this means usually 0. This setting is important for the
    next step of filtering out extreme values.

    :param maxValue: Value that non-reasonable values of SoC max profiles should be set to.
    :param minValue: Value that non-reasonable values of SoC min profiles should be set to.
    :return: Writes the two profiles files 'chargeMaxProfilesDSM' and 'chargeMinProfilesDSM' to the DataManager.
    '''

    chargeMaxProfilesDSM = dmgr['chargeMaxProfiles'].copy()
    chargeMinProfilesDSM = dmgr['chargeMinProfiles'].copy()
    boolIndices = dmgr['boolIndices']

    # if len(chargeMaxProfilesCons) == len(boolIndices): #len(chargeMaxProfilesCons) = len(chargeMinProfilesCons) by design
    # How can I catch pandas.core.indexing.IndexingError ?
    try:
        chargeMaxProfilesDSM.loc[~boolIndices['indexDSM'].astype('bool'), :] = params['maxValue']
        chargeMinProfilesDSM.loc[~boolIndices['indexDSM'].astype('bool'), :] = params['minValue']
    except:
        print("Declaration doesn't work. "
              "Maybe the length of boolIndices differs from the length of chargeMaxProfiles")

    dmgr['chargeMaxProfilesDSM'] = chargeMaxProfilesDSM
    dmgr['chargeMinProfilesDSM'] = chargeMinProfilesDSM

    # datalogger.info(len(chargeMaxProfilesDSM))

    # pd.set_option('display.width', 300)
    # pd.set_option('display.max_rows', None)
    # print(boolIndices.iloc[1:50, :])
    # print(chargeMaxProfilesDSM.iloc[1:50, :])
    # print(chargeMinProfilesDSM.iloc[1:50, :])
    # print(chargeMaxProfilesDSM.ix[~boolIndices['indexDSM'].astype('bool'),:])


# @action('VencoPy')
def indexFilter(dmgr, config, params):
    '''
    Filters out profiles where indexCons is False.

    :param profiles: Profile keys in DataManager given as list of strings.
    :return: Writes filtered profiles to DataManager under the key 'profilesCons' in a dictionary with keys given
    by parameter profiles.
    '''

    profiles = {}
    for prof in params['profiles']:
        profiles[prof] = dmgr[prof].copy()
    boolIndices = dmgr['boolIndices'].copy()
    profilesFilterDSM = {}
    profilesFilterCons = {}

    # try:
    for prof in params['profiles']:
        profilesFilterCons[prof] = profiles[prof].loc[boolIndices['indexCons'], :]
        profilesFilterDSM[prof] = profilesFilterCons[prof].loc[boolIndices['indexDSM'], :]
    # except :
    #     print('Declaration doesnt work. '
    #           'Maybe the length of boolIndices differs from the length of chargeMaxProfiles')

    dmgr['profilesCons'] = profilesFilterCons
    # print(len(profilesFilterDSM[params['profiles'][0]]))
    # print(len(profilesFilterCons[params['profiles'][0]]))


# @action('VencoPy')
def socProfileSelection(dmgr, config, params):
    '''
    Selects the nth highest value for each hour for min (max) profiles based on the percentage given in parameter
    'alpha'. If alpha = 10, the 10%-biggest (10%-smallest) value is selected, all other values are disregarded.
    Currently, in the Venco reproduction phase, the hourly values are selected independently of each other.

    :param filter: Selection method. Currently, only 'singleValues' is available.
    :param filterMax: Liste of DataManager keys pointing to profiles that should be filtered based on nsmallest()
    :param filterMin: Liste of DataManager keys pointing to profiles that should be filtered based on nlargest()
    :param alpha: Percentage, giving the amound of profiles whose mobility demand can not be fulfilled after selection.
    :return: Writes the two profiles 'SOCMax' and 'SOCMin' to the DataManager.
    '''

    profilesRaw = dmgr['profilesCons'].copy()

    noProfiles = len(profilesRaw[next(iter(profilesRaw))])
    noProfilesFilter = int(params['alpha'] / 100 * noProfiles)
    outputProfiles = []

    # try:
    if params['filter'] == 'singleValue':
        for maxp in params['filterMax']:
            profiles = profilesRaw[maxp]
            profileOut = profilesRaw[maxp].iloc[0, :].copy()
            for col in profiles:
                profileOut[col] = min(profiles[col].nlargest(noProfilesFilter))
            outputProfiles.append(profileOut)

        for minp in params['filterMin']:
            profiles = profilesRaw[minp]
            profileOut = profilesRaw[minp].iloc[0, :].copy()
            for col in profiles:
                profileOut[col] = max(profiles[col].nsmallest(noProfilesFilter))
            outputProfiles.append(profileOut)

    # elif params['filter'] == "profile"
        # to be done
    else:
        datalogger.warn('You selected a filter method that is not implemented.')

    # except KeyError:
    #     print('There was a key error. Check for correct profile declarations in your parameters')

    dmgr['SOCMax'] = outputProfiles[1]
    dmgr['SOCMin'] = outputProfiles[0]

    # print(profilesRaw['chargeMinProfilesDSM'].iloc[:, 12].nlargest(noProfilesFilter))
    # print(profilesRaw['chargeMaxProfilesDSM'].iloc[:, 12].nsmallest(noProfilesFilter))


# @action('VencoPy')
def normalizeProfiles(dmgr, config, params):
    # ToDo: Implement a normalization to the maximum of a given profile

    '''
    Normalizes given profiles with a given scalar reference.

    :param profiles: DataManager keys pointing towards profiles that should be normalized
    :param normReference: Reference that is taken for normalization. This has to be given in scalar input data.
    :param dmgrNames: Keys, under which the normalized profiles will be written to the DataManager
    :return: Writes the normalized profiles to the DataManager under the specified keys
    '''

    profiles = {}
    for prof in params['profiles']:
        profiles[prof] = pd.DataFrame(dmgr[prof])

    normReference = dmgr['scalars'].loc[params['normReference'], 'value']

    print(profiles['SOCMax'].div(float(normReference)))
    outputProfiles = []

    try:
        for key, value in profiles.items():
            outputProfiles.append(value.div(float(normReference)))
        for idx in range(len(params['dmgrNames'])):
            dmgr[params['dmgrNames'][idx]] = outputProfiles[idx]

    except ValueError:
        print('There was a value error. I don\'t know what to tell you.')

    # datalogger.info(outputProfiles)


# @action('VencoPy')
def filterConsProfiles(dmgr, config, params):
    '''
    Filter out all profiles from given profile types whose boolean indices (so far DSM or cons) are FALSE.

    :param profiles: profile identifiers given as list of strings referencing to DataManager keys
    :param dmgrNames: Identifiers given as list of string to store filtered profiles back into the DataManager
    :return: Stores filtered profiles in the DataManager under keys given in dmgrNames
    '''

    profiles = {}
    for prof in params['profiles']:
        profiles[prof] = pd.DataFrame(dmgr[prof])
    boolIndices = dmgr['boolIndices']
    outputProfiles = []

    for pname, prof in profiles.items():
        outputProfiles.append(prof.loc[boolIndices['indexCons'], :])

    # datalogger.info(outputProfiles)

    for idx in range(len(params['dmgrNames'])):
        dmgr[params['dmgrNames'][idx]] = outputProfiles[idx]


def considerProfiles(profiles, consider, colStart, colEnd, colCons):
    profilesOut = profiles.copy()

    try:
            profilesOut = profiles[consider[colCons].astype('bool'), colStart: colEnd]
    except KeyError:
        print("Key Error. "
            "The key {} is not part of {}".format(colCons, consider))
    return profilesOut

# so far not used. Plug profiles are aggregated in the action aggregateProfiles.
# @action('VencoPy')
def aggregatePlugProfiles(dmgr, config, params):
    '''
    This action aggregates all single-vehicle profiles that are considered to one fleet profile. There is a separate
    action for the aggregation of plug profiles since it is not corrected by another driving cycle such as consumption
    related profiles.

    :param profiles: DataManager key of the plug profiles subject to aggregation
    :return: Writes profile to DataManager under the key 'chargeAvailProfile_out'
    '''

    profiles = dmgr['plugProfilesCons'].copy()

    # Typecasting is necessary for aggregation of boolean profiles
    profiles_out = profiles.iloc[0, :].astype('float64', copy=True)
    lenProfiles = len(profiles)

    for colidx in profiles:
        profiles_out[colidx] = sum(profiles.loc[:, colidx]) / lenProfiles

    dmgr['chargeAvailProfile_out'] = profiles_out
    # datalogger.info(profiles_out)


# @action('VencoPy')
def correctProfiles(dmgr, config, params):
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

    profiles = {}
    for prof in params['profiles']:
        profiles[prof] = pd.DataFrame(dmgr[prof])
    consumptionElectricNEFZ = dmgr['scalars'].loc['Verbrauch NEFZ CD', 'value']
    consumptionFuelNEFZ = dmgr['scalars'].loc['Verbrauch NEFZ CS', 'value']
    consumptionElectricArtemis = dmgr['scalars'].loc['Verbrauch Artemis mit NV CD', 'value']
    consumptionFuelArtemis = dmgr['scalars'].loc['Verbrauch Artemis mit NV CS', 'value']
    corrFactorElectric = consumptionElectricArtemis / consumptionElectricNEFZ
    corrFactorFuel = consumptionFuelArtemis / consumptionFuelNEFZ

    profiles_corr = []

    for idx, key in enumerate(profiles):
        # print(idx)
        # print(profiles[key].head())

        profiles_loop = profiles[key].copy()

        if params['profType'][idx] == 'electric':
                for colidx in profiles[key]:
                    profiles_loop[colidx] = corrFactorElectric * profiles[key][colidx]

        elif params['profType'][idx] == 'fuel':
                for colidx in profiles[key]:
                    profiles_loop[colidx] = corrFactorFuel * profiles[key][colidx]
        else:
            print('Either parameter "profType" is not given or not assigned to either "electric" or "fuel".')

        # print(profiles_loop)
        profiles_corr.append(profiles_loop)

    # datalogger.info(profiles_corr)
    for idx in range(len(params['dmgrNames'])):
        dmgr[params['dmgrNames'][idx]] = profiles_corr[idx]


# @action('VencoPy')
def aggregateProfiles(dmgr, config, params):

    # TODO: Set column name to pname or use list instead of dataframe as looping data type
    '''
    This action aggregates profiles based on building the arithmetic mean for each hour. It thus transforms
    single-vehicle profiles to one fleet profile per profile type.

    :param profiles: List of strings of DataManager keys referencing to profiles for aggregation.
    :param dmgrNames: List of strings that results get written to.

    :return: Writes aggregated profiles to DataManager under the keys specified in dmgrNames.
    '''

    profiles = {}
    for prof in params['profiles']:
        profiles[prof] = pd.DataFrame(dmgr[prof])

    profiles_out = []
    for pname, prof in profiles.items():
        # initiating looping dataframe
        profiles_loop = pd.DataFrame(data = profiles[next(iter(profiles))].iloc[0, :],
                                        dtype = float,
                                        copy = True)
        profiles_loop.columns = [pname] # renaming the 1-column DataFrame
        noProfiles = len(prof)

        # aggregation
        for colidx in prof:  # colidx: column index
            # profiles_loop.iloc[int(colidx), :] = sum(prof.loc[:, colidx]) / len(prof.loc[:, colidx])
            profiles_loop.iloc[int(colidx), :] = sum(prof.loc[:, colidx]) / noProfiles

        profiles_out.append(profiles_loop)

    # Write profiles to datamanager for given profile names
    for idx in range(len(params['dmgrNames'])):
        dmgr[params['dmgrNames'][idx]] = profiles_out[idx]

# -----OUTPUT PROCESSING-------------------------------------------------------

# @action('VencoPy')
def cloneProfilesToYear(dmgr, config, params):
    '''
    This action clones daily profiles to cover a whole year.

    :param profiles: List of strings specifying the DataManager keys referencing the profile types for cloning
    :param technologies: List of strings of technologies that are taken into account for cloning (so far just copying)
    :param nodes: Data nodes that the profiles are copied to.
    :return: Writes the data to the specified REMix directory
    '''

    # read profiles from dmgr given in action call
    profiles = {}
    for prof in params['profiles']:
        profiles[prof] = pd.DataFrame(dmgr[prof]).iloc[:, 0]
    # datalogger.info(profiles)

    # tech = params['technologies']
    # nodes = params['nodes']

    # initialize config
    cfg = yaml.load(open(dmgr['linkDict']['linkTSConfig']))
    linkRmx = dmgr['linkDict']['linkTSREMix']

    # df = pd.DataFrame(columns=['technologies', 'timestep', nodes])
    # df = df.set_index(['technologies', 'timestep'])

    df = pd.concat([pd.DataFrame([i], columns=['']) for i in range(1, 8761)], ignore_index=True)
    df[' '] = params['technology_label']  # Add technology column
    df = df[[' ', '']]  # Re-arrange columns order

    for i in cfg['Nodes']:
        df[i] = 0

    s = df[''] < 10
    s1 = (df[''] >= 10) & (df[''] < 100)
    s2 = (df[''] >= 100) & (df[''] < 1000)
    s3 = df[''] >= 1000

    df.loc[s, ''] = df.loc[s, ''].apply(lambda x: "{}{}".format('t000', x))
    df.loc[s1, ''] = df.loc[s1, ''].apply(lambda x: "{}{}".format('t00', x))
    df.loc[s2, ''] = df.loc[s2, ''].apply(lambda x: "{}{}".format('t0', x))
    df.loc[s3, ''] = df.loc[s3, ''].apply(lambda x: "{}{}".format('t', x))

    for name, prof in profiles.items():
        profiles[name] = prof.append([prof] * 364, ignore_index=True)

    # print(profiles)

    df_chargeAv = df.copy()
    df_BatMax = df.copy()
    df_BatMin = df.copy()
    df_DrivePow = df.copy()
    df_UncontrCharge = df.copy()

    for i in cfg['NonNullNodes']:
        df_chargeAv[i] = np.round(profiles['plugProfilesCons_out'] , 3)
        df_BatMax.loc[:, i] = np.round(profiles['SOCMax_out'], 3)
        df_BatMin.loc[:, i] = np.round(profiles['SOCMin_out'], 3)
        df_DrivePow.loc[:, i] = np.round(profiles['electricPowerProfiles_out'], 3)
        df_UncontrCharge.loc[:, i] = np.round(profiles['chargeProfilesUncontrolled_out'], 3)

    # datalogger.info(df_chargeAv)

    df_chargeAv.to_csv(linkRmx + '/' + params['outputStrPre'] + 'chargeAvail' + params['outputStrPost'] + '.csv',
                       index=False)
    df_BatMax.to_csv(linkRmx + '/' + params['outputStrPre'] + 'batMax' + params['outputStrPost'] + '.csv',
                     index=False)
    df_BatMin.to_csv(linkRmx + '/' + params['outputStrPre'] + 'batMin' + params['outputStrPost'] + '.csv',
                     index=False)
    df_DrivePow.to_csv(linkRmx + '/' + params['outputStrPre'] + 'drivePower' + params['outputStrPost'] + '.csv',
                       index=False)
    df_UncontrCharge.to_csv(linkRmx + '/' + params['outputStrPre'] + 'uncontrCharge' + params['outputStrPost'] + '.csv',
                            index=False)

    # dmgr['chargeAv'] = df_chargeAv
    # dmgr['batMax'] = df_BatMax
    # dmgr['batMin'] = df_BatMin
    # dmgr['drivePower'] = df_DrivePow
    # dmgr['uncCharge'] = df_UncontrCharge


# @action('VencoPy')
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


# @action('VencoPy')
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