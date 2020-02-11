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
    linkConfig = 'C:/vencopy_repo/config/VencoPy_conf.yaml'
    linkDict, scalars, driveProfiles_raw, plugProfiles_raw = readVencoInput(linkConfig)

    indices = ['CASEID', 'PKWID']
    driveProfiles, plugProfiles = indexProfile(driveProfiles_raw, plugProfiles_raw, indices)

    scalarsProc = procScalars(driveProfiles_raw, plugProfiles_raw, driveProfiles, plugProfiles)

    consumptionProfiles = calcConsumptionProfile(driveProfiles, scalars)

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

    randNos = createRandNo(driveProfiles)

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

