__version__ = '0.1.0'
__maintainer__ = 'Niklas Wulff'
__email__ = 'Niklas.Wulff@dlr.de'
__birthdate__ = '03.11.2019'
__status__ = 'dev'  # options are: dev, test, prod


#----- imports & packages ------
from scripts.libInput import *
from scripts.libPreprocessing import *
from scripts.libProfileCalculation import *
from scripts.libOutput import *
from scripts.plotting import *


#ToDO: Write an action to write processed scalars to scalarsProc after filtering to write meta-information to file
#ToDo: Maybe consolidate selection actions to one aggregation and one filtering action

if __name__ == '__main__':
    #----- data and config read-in -----
    # REVIEW (resolved) this should be a relative path as an absolute will not work on other peoples computers.
    # Have you considered to use the pathlib? So far not, lets discuss!
    linkConfig = './config/VencoPy_conf.yaml'
    # REVIEW (resolved) the variable names both use camel case and snake case. I suggest sticking with one for the
    # publication, as this can be irritating when reading the code
    linkDict, scalars, driveProfilesRaw, plugProfilesRaw = readVencoInput(linkConfig)
    indices = ['CASEID', 'PKWID']
    driveProfiles, plugProfiles = indexProfile(driveProfilesRaw, plugProfilesRaw, indices)
    scalarsProc = procScalars(driveProfilesRaw, plugProfilesRaw, driveProfiles, plugProfiles)

    # REVIEW (resolved) the return value of the function implies multiple profiles while the function name implies
    # only one is calculated. I suggest changing the naming to reflect the real situation
    consumptionProfiles = calcConsumptionProfiles(driveProfiles, scalars)

    # REVIEW (resolved) the return value of the function implies multiple profiles while the function name implies
    # only one is calculated. I suggest changing the naming to reflect the real situation
    chargeProfiles = calcChargeProfiles(plugProfiles, scalars)

    chargeMaxProfiles = calcChargeMaxProfiles(chargeProfiles,
                                              consumptionProfiles,
                                              scalars,
                                              scalarsProc,
                                              nIter=20)

    chargeProfilesUncontrolled = calcChargeProfilesUncontrolled(chargeMaxProfiles,
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

    # Review (resolved) randNoPerProfile is not telling a lot about what the variable contains. It implies for me,
    # that there are random numbers stored into this variable. Can this variable named more precisely
    randNoPerProfile = createRandNo(driveProfiles)

    # Review naming variables after data types is unusual in Python as it is not a strongly typed language.
    # Can this be named more precisely in the context of the domain?
    profileSelectors = calcProfileSelectors(chargeProfiles,
                                            consumptionProfiles,
                                            driveProfiles,
                                            driveProfilesFuelAux,
                                            randNoPerProfile,
                                            scalars,
                                            fuelDriveTolerance=0.001,
                                            isBEV=True)

    electricPowerProfiles = calcElectricPowerProfiles(consumptionProfiles,
                                                      driveProfilesFuelAux,
                                                      scalars,
                                                      profileSelectors,
                                                      scalarsProc,
                                                      filterIndex='indexCons')

    chargeMaxProfilesDSM, chargeMinProfilesDSM = setUnconsideredBatProfiles(chargeMaxProfiles, chargeMinProfiles,
                                                                            profileSelectors, minValue=0,
                                                                            maxValue=9999)

    profilesFilterConsMin, \
    profilesFilterConsMax, \
    profilesFilterDSMMin, \
    profilesFilterDSMMax = indexFilter(chargeMaxProfiles,
                                       chargeMinProfiles,
                                       profileSelectors)

    SOCMin, SOCMax = socProfileSelection(profilesFilterConsMin, profilesFilterConsMax,
                                         filter='singleValue', alpha=1)

    socMinNorm, socMaxNorm = normalizeProfiles(scalars, SOCMin, SOCMax,
                                               normReference='Battery size')

    plugProfilesCons = filterConsProfiles(plugProfiles, profileSelectors, critCol='indexCons')
    electricPowerProfilesCons = filterConsProfiles(electricPowerProfiles, profileSelectors, critCol='indexCons')
    chargeProfilesUncontrolledCons = filterConsProfiles(chargeProfilesUncontrolled, profileSelectors, critCol='indexCons')
    driveProfilesFuelAuxCons = filterConsProfiles(driveProfilesFuelAux, profileSelectors, critCol='indexCons')

    plugProfilesAgg = aggregateProfiles(plugProfilesCons)
    electricPowerProfilesAgg = aggregateProfiles(electricPowerProfilesCons)
    chargeProfilesUncontrolledAgg = aggregateProfiles(chargeProfilesUncontrolledCons)
    driveProfilesFuelAuxAgg = aggregateProfiles(driveProfilesFuelAuxCons)

    chargeProfilesUncontrolledCorr = correctProfiles(scalars, chargeProfilesUncontrolledAgg, 'electric')
    electricPowerProfilesCorr = correctProfiles(scalars, electricPowerProfilesAgg, 'electric')
    driveProfilesFuelAuxCorr = correctProfiles(scalars, driveProfilesFuelAuxAgg, 'fuel')

    # review (resolved) the next calls all seem to write a file to disc, however, the function name itself does not
    # reflect this as cloning usually does not imply a write operation. Could this function be named more precisely?
    cloneAndWriteProfiles(socMinNorm, linkDict, 8760, technologyLabel='BEV-S',
                          filename='BEV_S_SOCMin_VencoPy_MR1_alpha1_batCap40_cons15')

    cloneAndWriteProfiles(socMaxNorm, linkDict, 8760, technologyLabel='BEV-S',
                          filename='BEV_S_SOCMax_VencoPy_MR1_alpha1_batCap40_cons15')

    cloneAndWriteProfiles(chargeProfilesUncontrolledCorr, linkDict, 8760, technologyLabel='BEV-S',
                          filename='BEV_S_chargeUncontrolled_VencoPy_MR1_alpha1_batCap40_cons15')

    cloneAndWriteProfiles(electricPowerProfilesCorr, linkDict, 8760, technologyLabel='BEV-S',
                          filename='BEV_S_drivePower_VencoPy_MR1_alpha1_batCap40_cons15')

    cloneAndWriteProfiles(driveProfilesFuelAuxCorr, linkDict, 8760, technologyLabel='BEV-S',
                          filename='BEV_S_driveAuxFuel_VencoPy_MR1_alpha1_batCap40_cons15')

    cloneAndWriteProfiles(plugProfilesAgg, linkDict, 8760, technologyLabel='BEV-S',
                          filename='BEV_S_plugProfile_VencoPy_MR1_alpha1_batCap40_cons15')

    #linePlot(profiles, show=True, write=True, stradd='MR1_alpha1_batCap40_cons15')

