# -*- coding:utf-8 -*-

__version__ = '0.1.0'
__maintainer__ = 'Niklas Wulff 24.02.2020'
__email__ = 'Niklas.Wulff@dlr.de'
__birthdate__ = '24.02.2019'
__status__ = 'test'  # options are: dev, test, prod

# This script holds the function definitions for output processing of calaculated profiles from VencoPy.

import numpy as np
import yaml
import pandas as pd


def cloneAndWriteProfiles(profile, linkDict, noOfHoursOutput, technologyLabel, filename):
    """
    This action clones daily profiles to cover the specified time horizon given in noOfHoursOutput.

    :param profile: A VencoPy profile.
    :param linkDict: A VencoPy link dictionary.
    :param noOfHoursOutput: Number of hours to clone the daily profile to (for 1 (non-gap-)year set to 8760)
    :param technologyLabel: Technology (e.g. vehicle segment "BEV-S") label for the filename that is written.
    :param filename: Name of the file to be written.
    :return: None.
    """

    dfProfile = pd.DataFrame(profile).iloc[:, 0]

    # initialize config
    cfg = yaml.load(open(linkDict['linkTSConfig']))
    linkRmx = linkDict['linkTSREMix']

    df = createEmptyDataFrame(technologyLabel, noOfHoursOutput, cfg['Nodes'])
    # review is this correct? What happens when noOfHoursOutput/len(profile) is smaller then 0? Then noOfClones
    # would be negative and I am not sure if this would be coerced to 0 by the following int type cast later on.
    # Is this handled upstream in the call chain?
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

