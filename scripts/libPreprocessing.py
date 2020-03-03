# -*- coding:utf-8 -*-

__version__ = '0.1.0'
__maintainer__ = 'Niklas Wulff 24.02.2020'
__email__ = 'Niklas.Wulff@dlr.de'
__birthdate__ = '24.02.2020'
__status__ = 'test'  # options are: dev, test, prod

# This file holds the function definitions for preprocessing after data input for VencoPy.

import warnings
from .libLogging import logit
from .libLogging import logger

@logit
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

@logit
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

