# -*- coding:utf-8 -*-

__version__ = '0.1.0'
__maintainer__ = 'Niklas Wulff 04.02.2020'
__email__ = 'Niklas.Wulff@dlr.de'
__birthdate__ = '15.04.2019'
__status__ = 'test'  # options are: dev, test, prod

# This file holds the function definitions for VencoPy input functions.

import os
import sys

sys.path.append(os.path.abspath('C:/REMix-OaM/OptiMo/projects/REMix-tools/remixPlotting'))

import yaml
import pandas as pd

# ToDo: Explicit strings from current Excel file in the code. Is it possible to implement that better???

# -----INPUT-----------------------------------
# review (RESOLVED) have you considered splitting this file up into different files, named after the captions in this
# file? It would make it easier to navigate and search the code base

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
