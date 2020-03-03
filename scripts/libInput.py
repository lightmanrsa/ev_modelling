# -*- coding:utf-8 -*-

__version__ = '0.1.0'
__maintainer__ = 'Niklas Wulff 24.02.2020'
__email__ = 'Niklas.Wulff@dlr.de'
__birthdate__ = '24.02.2020'
__status__ = 'test'  # options are: dev, test, prod

# This file holds the function definitions for VencoPy input functions.

import yaml
import pandas as pd
from .libLogging import logit
from .libLogging import logger

# ToDo: Explicit strings from current Excel file in the code. Is it possible to implement that better???
# review (RESOLVED) have you considered splitting this file up into different files, named after the captions in this
# file? It would make it easier to navigate and search the code base


@logit
def readVencoConfig(cfgLink):
    config = yaml.load(open(cfgLink), Loader=yaml.SafeLoader)
    return config


@logit
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
    return linkDict_out


@logit
def readInputScalar(filePath):
    # review general remark (RESOLVED), a file link implies a sym link on the disk. Have you considered renaming the
    # variable to filePath for example, which would imply a path to a file on the disk
    inputRaw = pd.read_excel(filePath,
                              header=5,
                              usecols="A:E",
                              skiprows=0)
    scalar = inputRaw.loc[:, ~inputRaw.columns.str.match('Unnamed')]
    scalarsOut = scalar.set_index('parameter')
    return scalarsOut


@logit
def readInputCSV(file_link):
    inputRaw = pd.read_csv(file_link, header=4)
    inputData = inputRaw.loc[:, ~inputRaw.columns.str.match('Unnamed')]
    return inputData


@logit
def stringToBoolean(df):
    dictBol = {'WAHR': True,
                'FALSCH': False}
    outBool = df.replace(to_replace=dictBol, value=None)
    return (outBool)


@logit
def readInputBoolean(filePath):
    inputRaw = readInputCSV(filePath)
    inputData = stringToBoolean(inputRaw)
    return inputData


@logit
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

    linkDict = initializeLinkMgr(readVencoConfig(linkConfig))

    # review: have you considered using the logging module for these kind of outputs?
    print('Reading Venco input scalars, drive profiles and boolean plug profiles')

    scalars = readInputScalar(linkDict['linkScalars'])
    driveProfiles_raw = readInputCSV(linkDict['linkDriveProfiles'])
    plugProfiles_raw = readInputBoolean(linkDict['linkPlugProfiles'])

    print('There are ' + str(len(driveProfiles_raw)) + ' drive profiles and ' +
                    str(len(driveProfiles_raw)) + ' plug profiles.')

    return linkDict, scalars, driveProfiles_raw, plugProfiles_raw