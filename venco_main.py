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


#----- data and config read-in -----
linkConfig = 'C:/vencopy_repo/config/VencoPy_conf.yaml'
linkDict, scalars, driveProfiles_raw, plugProfiles_raw = readVencoInput(linkConfig)

#print(linkDict, scalars, driveProfiles_raw.head, plugProfiles_raw.head)

indices = ['CASEID', 'PKWID']
driveProfiles, plugProfiles = indexProfile(driveProfiles_raw, plugProfiles_raw, indices)

# print(driveProfiles.head, plugProfiles.head)
# print(driveProfiles.index)
# print(driveProfiles.info)


#  - action2b:
#      project: VencoPy
#      call: indexProfiles
#      profilesInput: ['driveProfiles_raw', 'plugProfiles_raw']
#      indices: ['CASEID', 'PKWID']
#      profilesDmgr: ['driveProfiles', 'plugProfiles']


scalarsProc = procScalars(driveProfiles_raw, plugProfiles_raw, driveProfiles, plugProfiles)
print(scalarsProc)

#  - action3:
#      project: VencoPy
#      call: procScalars

consumptionProfiles = calcConsumptionProfile(driveProfiles, scalars)

#  - action4:
#      project: VencoPy
#      call: calcConsumptionProfiles

##  - actionCheck:
##      project: general
##      call: checkpoint
##      tag: test

chargeProfiles = calcChargeProfile(plugProfiles, scalars)

#  - action5:
#      project: VencoPy
#      call: calcChargeProfile


chargeMaxProfiles = calcChargeMaxProfiles(chargeProfiles,
                                          consumptionProfiles,
                                          scalars,
                                          scalarsProc,
                                          nIter=20)
#  - action6:
#      project: VencoPy
#      call: calcChargeMaxProfiles
#      nIter: 10

chargeProfilesUncontrolled = calcChargeProfileUncontrolled(chargeMaxProfiles,
                                                           scalarsProc)

#  - action7:
#      project: VencoPy
#      call: calcChargeProfileUncontrolled

driveProfilesFuelAux = calcDriveProfilesFuelAux(chargeMaxProfiles,
                                                chargeProfilesUncontrolled,
                                                driveProfiles,
                                                scalars,
                                                scalarsProc)

#  - action8:
#      project: VencoPy
#      call: calcDriveProfilesFuelAux

chargeMinProfiles = calcChargeMinProfiles(chargeProfiles,
                                          consumptionProfiles,
                                          driveProfilesFuelAux,
                                          scalars,
                                          scalarsProc,
                                          nIter=20)

#  - action9:
#      project: VencoPy
#      call: calcChargeMinProfiles
#      nIter: 10

randNos = createRandNo(driveProfiles)

#  - action10:
#      project: VencoPy
#      call: createRandNo

boolIndices = calcIndices(chargeProfiles,
                          consumptionProfiles,
                          driveProfiles,
                          driveProfilesFuelAux,
                          randNos,
                          scalars,
                          fuelDriveTolerance=0.001,
                          isBEV=True)


#  - action11:
#      project: VencoPy
#      call: calcIndices
#      fuelDriveTolerance: 0.001
#      isBEV2030: True


electricPowerProfiles = calcElectricPowerProfiles(consumptionProfiles,
                                                  driveProfilesFuelAux,
                                                  scalars,
                                                  boolIndices,
                                                  scalarsProc,
                                                  filterIndex='indexCons')

#  - action16:
#      project: VencoPy
#      call: calcElectricPowerProfiles
#      dmgrName: 'electricPowerProfiles'
#      filterIndex: indexCons

chargeMaxProfilesDSM, chargeMinProfilesDSM = filterConsBatProfiles(chargeMaxProfiles, chargeMinProfiles, boolIndices,
                                                                   minValue=0, maxValue=9999)


#  - action12:
#      project: VencoPy
#      call: filterConsBatProfiles
#      maxValue: 9999
#      minValue: 0

profilesFilterConsMin, \
profilesFilterConsMax, \
profilesFilterDSMMin, \
profilesFilterDSMMax = indexFilter(chargeMaxProfiles,
                                   chargeMinProfiles,
                                   boolIndices)

#  - action13:
#      project: VencoPy
#      call: indexFilter
#      profiles: ['chargeMaxProfilesDSM', 'chargeMinProfilesDSM']

SOCMin, SOCMax = socProfileSelection(profilesFilterConsMin, profilesFilterConsMax,
                                     filter='singleValue', alpha=1)

#  - action14:
#      project: VencoPy
#      call: socProfileSelection
#      filter: singleValue
#      filterMax:
#            - chargeMinProfilesDSM
#      filterMin:
#            - chargeMaxProfilesDSM
#      alpha: 1


socMinNorm, socMaxNorm = normalizeProfiles(scalars, SOCMin, SOCMax,
                                           normReference='Battery size')

#  - action15:
#      project: VencoPy
#      call: normalizeProfiles
#      profiles: ['SOCMax', 'SOCMin']
#      normReference: ['Battery size']
#      dmgrNames: ['SOCMax_out', 'SOCMin_out']

plugProfilesCons = filterConsProfiles(plugProfiles, boolIndices, critCol='indexCons')
electricPowerProfilesCons = filterConsProfiles(electricPowerProfiles, boolIndices, critCol='indexCons')
chargeProfilesUncontrolledCons = filterConsProfiles(chargeProfilesUncontrolled, boolIndices, critCol='indexCons')
driveProfilesFuelAuxCons = filterConsProfiles(driveProfilesFuelAux, boolIndices, critCol='indexCons')

#  - action17:
#      project: VencoPy
#      call: filterConsProfiles
#      profiles: ['plugProfiles', 'electricPowerProfiles', 'chargeProfilesUncontrolled', 'driveProfilesFuelAux']
#      dmgrNames: ['plugProfilesCons', 'electricPowerProfilesCons',
#                  'chargeProfilesUncontrolledCons', 'driveProfilesFuelAuxCons']

plugProfilesAgg = aggregateProfiles(plugProfilesCons)
electricPowerProfilesAgg = aggregateProfiles(electricPowerProfilesCons)
chargeProfilesUncontrolledAgg = aggregateProfiles(chargeProfilesUncontrolledCons)
driveProfilesFuelAuxAgg = aggregateProfiles(driveProfilesFuelAuxCons)

#  - action18:
#      project: VencoPy
#      call: aggregatePlugProfiles
#      profiles: ['plugProfilesCons']


chargeProfilesUncontrolledCorr = correctProfiles(scalars, chargeProfilesUncontrolledAgg, 'electric')
electricPowerProfilesCorr = correctProfiles(scalars, electricPowerProfilesAgg, 'electric')
driveProfilesFuelAuxCorr = correctProfiles(scalars, driveProfilesFuelAuxAgg, 'fuel')

#  - action19:
#      project: VencoPy
#      call: correctProfiles
#      profiles: ['chargeProfilesUncontrolledCons', 'electricPowerProfilesCons', 'driveProfilesFuelAuxCons']
#      profType: ['electric', 'electric', 'fuel']
#      dmgrNames: ['chargeProfilesUncontrolledCorr', 'electricPowerProfilesCorr','driveProfilesFuelAuxCorr']


# dont know why this is redundantly implemented here..
#  - action20:
#      project: VencoPy
#      call: aggregateProfiles
#      profiles: ['plugProfilesCons', 'chargeProfilesUncontrolledCorr',
#                 'electricPowerProfilesCorr', 'driveProfilesFuelAuxCorr']
#      dmgrNames: ['plugProfilesCons_out', 'chargeProfilesUncontrolled_out',
#                  'electricPowerProfiles_out', 'driveProfilesFuelAux_out']

cloneProfilesToYear(socMinNorm, linkDict, 8760, technologyLabel='BEV-S',
                    filename='BEV_S_SOCMax_VencoPy_MR1_alpha1_batCap40_cons15')

cloneProfilesToYear(socMaxNorm, linkDict, 8760, technologyLabel='BEV-S',
                    filename='BEV_S_SOCMax_VencoPy_MR1_alpha1_batCap40_cons15')

cloneProfilesToYear(chargeProfilesUncontrolledCorr, linkDict, 8760, technologyLabel='BEV-S',
                    filename='BEV_S_SOCMax_VencoPy_MR1_alpha1_batCap40_cons15')

cloneProfilesToYear(electricPowerProfilesCorr, linkDict, 8760, technologyLabel='BEV-S',
                    filename='BEV_S_SOCMax_VencoPy_MR1_alpha1_batCap40_cons15')

cloneProfilesToYear(driveProfilesFuelAuxCorr, linkDict, 8760, technologyLabel='BEV-S',
                    filename='BEV_S_SOCMax_VencoPy_MR1_alpha1_batCap40_cons15')

cloneProfilesToYear(plugProfilesAgg, linkDict, 8760, technologyLabel='BEV-S',
                    filename='BEV_S_SOCMax_VencoPy_MR1_alpha1_batCap40_cons15')



#  - action21:
#      project: VencoPy
#      call: cloneProfilesToYear
#      profiles: ['plugProfilesCons_out', 'chargeProfilesUncontrolled_out',
#                 'electricPowerProfiles_out', 'driveProfilesFuelAux_out',
#                 'SOCMax_out', 'SOCMin_out']
#      technology_label: BEV_S
#      nodes: ['Germany_North', 'Germany_South']
#      outputStrPre: BEV-S_
#      outputStrPost: _Venco_MR1_alpha1_batCap40_cons15



#  - plottingAction1:
#      project: VencoPy
#      call: linePlot
#      dmgrKeys: ['plugProfilesCons_out', 'chargeProfilesUncontrolled_out',
#                 'electricPowerProfiles_out', 'driveProfilesFuelAux_out',
#                 'SOCMax_out', 'SOCMin_out']
#      show: True
#      write: True
#      stradd: 'MR1_alpha1_batCap40_cons15'
#
#  - action22:
#      project: VencoPy
#      call: appendOutputProfiles
#      link: 'D:/Users/wulf_ni/Documents/02 Research/Paper/Coupling energy and transport models/calculations/VencoPy/MR1/output'
#      pre: [BEV-S_, BEV-M_, BEV-L_]
#      names: [batMin_Venco_MR1, batMax_Venco_MR1, chargeAvail_Venco_MR1,
#              drivePower_Venco_MR1, uncontrCharge_Venco_MR1]
#      post: [_alpha1_batCap40_cons15, _alpha1_batCap70_cons20, _alpha1_batCap100_cons25]
#      outputPre: 'eCarsDtl_'
#      outputDir: 'D:/Users/wulf_ni/Documents/02 Research/Paper/Coupling energy and transport models/calculations/VencoPy/MR1/output/REMix_profiles/'
#      outputPost: '_40_70_100'

################################################################################
#           DEBUG ACTIONS
################################################################################

#
#  - debugAction1:
#      project: VencoPy
#      call: setPrintOptions
#      display.max_rows: 100
#      display.max_columns: 30
#      display.width: 300
#
#  - debugAction2:
#      project: VencoPy
#      call: printProfiles
#      profiles: ['driveProfiles_raw', 'plugProfiles_raw', 'consumptionProfiles', 'chargeProfiles',
#      'chargeMaxProfiles', 'chargeProfilesUncontrolled', 'driveProfilesFuelAux', 'chargeMinProfiles', 'boolIndices']
#      #'SOCMax', 'SOCMin', 'electricPowerProfiles',
#      caseIDs: ['4803', '84490', '93345', '112106']


################################################################################
#           PLOTTING ACTIONS
################################################################################

#  - plottingAction18:
#      project: VencoPy
#      call: linePlot
#      dmgrKeys: ['plugProfiles_out', 'chargeProfilesUncontrolled_out', 'driveProfilesFuelAux_out', 'SOCMax_out', 'SOCMin_out']
#      show: True
#      write: True
#      stradd: 'hakunamatata'