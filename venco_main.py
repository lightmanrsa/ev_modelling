__version__ = '0.1.0'
__maintainer__ = 'Niklas Wulff'
__email__ = 'Niklas.Wulff@dlr.de'
__birthdate__ = '03.11.2019'
__status__ = 'dev'  # options are: dev, test, prod


#----- imports & packages ------
# import numpy as np
import yaml
import pandas as pd
from functools import reduce
from random import seed
from random import random
from scripts.venco import *
from scripts.plotting import *


#ToDO: Write an action to write processed scalars to scalarsProc after filtering to write meta-information to file
#ToDo: Maybe consolidate selection actions to one aggregation and one filtering action

if __name__ == '__main__':
    #----- data and config read-in -----
    # REVIEW this should be a relative path as an absolute will not work on other peoples computers. Have you considered to use the pathlib
    linkConfig = 'C:/vencopy_repo/config/VencoPy_conf.yaml'
    # REVIEW the variable names both use camel case and snake case. I suggest sticking with one for the publication, as this can be irritating when reading the code
    linkDict, scalars, driveProfiles_raw, plugProfiles_raw = readVencoInput(linkConfig)

    indices = ['CASEID', 'PKWID']
    driveProfiles, plugProfiles = indexProfile(driveProfiles_raw, plugProfiles_raw, indices)

    scalarsProc = procScalars(driveProfiles_raw, plugProfiles_raw, driveProfiles, plugProfiles)

    # REVIEW the return value of the function implies multiple profiles while the function name implies only one is calculated. I suggest changing the naming to reflect the real situation
    consumptionProfiles = calcConsumptionProfile(driveProfiles, scalars)

    # REVIEW the return value of the function implies multiple profiles while the function name implies only one is calculated. I suggest changing the naming to reflect the real situation
    chargeProfiles = calcChargeProfile(plugProfiles, scalars)

    chargeMaxProfiles = calcChargeMaxProfiles(chargeProfiles,
                                              consumptionProfiles,
                                              scalars,
                                              scalarsProc,
                                              nIter=20)

    chargeProfilesUncontrolled = calcChargeProfileUncontrolled(chargeMaxProfiles,
                                                               scalarsProc)

    driveProfilesFuelAux = calcDriveProfilesFuelAux(chargeMaxProfiles,
                                                    chargeProfilesUncontrolled,
                                                    driveProfiles,
                                                    scalars,
                                                    scalarsProc)

    chargeMinProfiles = calcChargeMinProfiles(chargeProfiles,
                                              consumptionProfiles,
                                              driveProfilesFuelAux,
                                              scalars,
                                              scalarsProc,
                                              nIter=20)

    # Review randNos is not telling a lot about what the variable contains. It implies for me, that there are random numbers stored into this variable. Can this variable named more precisely
    randNos = createRandNo(driveProfiles)

    # Review naming variables after data types is unusual in Python as it is not a strongly typed language. Can this be named more precisely in the context of the domain?
    boolIndices = calcIndices(chargeProfiles,
                              consumptionProfiles,
                              driveProfiles,
                              driveProfilesFuelAux,
                              randNos,
                              scalars,
                              fuelDriveTolerance=0.001,
                              isBEV=True)

    electricPowerProfiles = calcElectricPowerProfiles(consumptionProfiles,
                                                      driveProfilesFuelAux,
                                                      scalars,
                                                      boolIndices,
                                                      scalarsProc,
                                                      filterIndex='indexCons')

    chargeMaxProfilesDSM, chargeMinProfilesDSM = filterConsBatProfiles(chargeMaxProfiles, chargeMinProfiles, boolIndices,
                                                                       minValue=0, maxValue=9999)

    profilesFilterConsMin, \
    profilesFilterConsMax, \
    profilesFilterDSMMin, \
    profilesFilterDSMMax = indexFilter(chargeMaxProfiles,
                                       chargeMinProfiles,
                                       boolIndices)

    SOCMin, SOCMax = socProfileSelection(profilesFilterConsMin, profilesFilterConsMax,
                                         filter='singleValue', alpha=1)

    socMinNorm, socMaxNorm = normalizeProfiles(scalars, SOCMin, SOCMax,
                                               normReference='Battery size')

    plugProfilesCons = filterConsProfiles(plugProfiles, boolIndices, critCol='indexCons')
    electricPowerProfilesCons = filterConsProfiles(electricPowerProfiles, boolIndices, critCol='indexCons')
    chargeProfilesUncontrolledCons = filterConsProfiles(chargeProfilesUncontrolled, boolIndices, critCol='indexCons')
    driveProfilesFuelAuxCons = filterConsProfiles(driveProfilesFuelAux, boolIndices, critCol='indexCons')

    plugProfilesAgg = aggregateProfiles(plugProfilesCons)
    electricPowerProfilesAgg = aggregateProfiles(electricPowerProfilesCons)
    chargeProfilesUncontrolledAgg = aggregateProfiles(chargeProfilesUncontrolledCons)
    driveProfilesFuelAuxAgg = aggregateProfiles(driveProfilesFuelAuxCons)

    chargeProfilesUncontrolledCorr = correctProfiles(scalars, chargeProfilesUncontrolledAgg, 'electric')
    electricPowerProfilesCorr = correctProfiles(scalars, electricPowerProfilesAgg, 'electric')
    driveProfilesFuelAuxCorr = correctProfiles(scalars, driveProfilesFuelAuxAgg, 'fuel')

    # review the next calls all seem to write a file to disc, however, the function name itself does not reflect this as cloning usually does not imply a write operation. Could this function be named more precisely?
    cloneProfilesToYear(socMinNorm, linkDict, 8760, technologyLabel='BEV-S',
                        filename='BEV_S_SOCMin_VencoPy_MR1_alpha1_batCap40_cons15')

    cloneProfilesToYear(socMaxNorm, linkDict, 8760, technologyLabel='BEV-S',
                        filename='BEV_S_SOCMax_VencoPy_MR1_alpha1_batCap40_cons15')

    cloneProfilesToYear(chargeProfilesUncontrolledCorr, linkDict, 8760, technologyLabel='BEV-S',
                        filename='BEV_S_chargeUncontrolled_VencoPy_MR1_alpha1_batCap40_cons15')

    cloneProfilesToYear(electricPowerProfilesCorr, linkDict, 8760, technologyLabel='BEV-S',
                        filename='BEV_S_drivePower_VencoPy_MR1_alpha1_batCap40_cons15')

    cloneProfilesToYear(driveProfilesFuelAuxCorr, linkDict, 8760, technologyLabel='BEV-S',
                        filename='BEV_S_driveAuxFuel_VencoPy_MR1_alpha1_batCap40_cons15')

    cloneProfilesToYear(plugProfilesAgg, linkDict, 8760, technologyLabel='BEV-S',
                        filename='BEV_S_plugProfile_VencoPy_MR1_alpha1_batCap40_cons15')

    #linePlot(profiles, show=True, write=True, stradd='MR1_alpha1_batCap40_cons15')

