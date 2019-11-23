__version__ = '0.0.1'
__maintainer__ = 'Niklas Wulff 16.04.2019'
__email__ = 'Niklas.Wulff@dlr.de'
__birthdate__ = '16.05.2019'
__status__ = 'dev'  # options are: dev, test, prod

# This script holds the plotting functionalities and actions for VencoPy. It is free and open software and licensed
# under GPLv3.
# df = dataframe, dmgr = data manager,

import os
import sys

sys.path.append(os.path.abspath('C:/REMix-OaM/OptiMo/projects/REMix-tools/remixPlotting'))

from ioproc.tools import action
from ioproc.logger import mainlogger, datalogger
from plotsStochastic import plotStochBox
import numpy as np
import yaml
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import reportlab as repl
from reportlab.pdfgen import canvas
from functools import reduce
from random import seed
from random import random


# ToDo: Write more statistic information below plots

def createPlot(data, x, y, hue, link, showplot):
    plt.figure()
    sns.lineplot(x=x, y=y, hue=hue, sort=False,
                 data=data)
    plt.savefig(link, dpi=300)
    if showplot:
        plt.show()


def writePlotsPlusInfo(canv, filenamePlot, header, statisticalInfo):
    canv.drawString(50, 750, header)
    canv.drawImage(image=filenamePlot,
                   x=0, y=-200, width=600,
                   preserveAspectRatio=True)
    canv.drawString(50, 280, statisticalInfo)
    return (canv)


def getStatisticalInfo(data, column):
    dfHead = data.head()
    statDict = {'head': [dfHead.columns[:, ].values.astype(str).tolist()] + dfHead.values.tolist(),
                'index': data.index,
                'length': len(data),
                'ndim': data.ndim,
                'describe': data.describe(),
                'collength': len(data[column])}

    return (statDict)


# So far it's only possible to write explicit strings to the PDF using Reportlab. Possibly, flowables or tables
# (chapters 7 + 8 in the guide) could be used to write tabular data such as the header of the input profiles
# or df.describe() directly.
@action('VencoPy')
def plotting(dmgr, config, params):
    canvasPlots = canvas.Canvas(dmgr['linkDict']['linkPlots'] + params['data'] + '.pdf')
    for y in params['y']:
        filenamePlot = dmgr['linkDict']['linkPlots'] + 'plot_' + y + '.jpeg'
        createPlot(x=params['x'],
                   y=y,
                   hue=params['hue'],
                   data=dmgr[params['data']],
                   link=filenamePlot,
                   showplot=params['showplot'])
        statDict = getStatisticalInfo(dmgr[params['data']], y)
        canvasPlots = writePlotsPlusInfo(canv=canvasPlots,
                                         filenamePlot=filenamePlot,
                                         header='Statistical summary of input data given in MiD 2008, differentiated by '
                                                + params['hue'],
                                         statisticalInfo='The column ' + y + ' contains ' + str(statDict['collength']) +
                                                         ' elements, resulting in ' +
                                                         str(len(dmgr[params['data']]) / len(
                                                             set(dmgr[params['data']]['hour']))) +
                                                         ' profiles.')
        canvasPlots.showPage()
    canvasPlots.save()


@action('VencoPy')
def violinplot(dmgr, config, params):
    dataRaw = dmgr[params['data']]

    x = params['x']
    y = params['y']  # multiple columns

    data = dataRaw.copy()

    if 'xfilt' in params.keys():
        data = dataRaw.loc[dataRaw[x].isin(params['xfilt']), :]

    vplot = {}
    for yidx in y:
        if 'yfilt' in params.keys():
            data = data.loc[:, dataRaw[yidx].isin(params['yfilt'])]

        print(yidx)
        vplot[yidx] = plt.figure()

        if 'sticks' in params.keys():
            if params['sticks']:
                vplot[yidx] = sns.violinplot(x=x, y=yidx, data=data, inner='stick', cut=0)
            else:
                vplot[yidx] = sns.violinplot(x=x, y=yidx, data=data, cut=0)
        else:
            vplot[yidx] = sns.violinplot(x=x, y=yidx, data=data, cut=0)

        if 'write' in params.keys():
            print(dmgr['linkDict']['linkPlots'] + yidx + '_violinplot.png')
            if 'stradd' in params.keys():
                vplot[yidx].figure.savefig(
                    dmgr['linkDict']['linkPlots'] + yidx + '_violinplot' + params['stradd'] + '.png')
            else:
                vplot[yidx].figure.savefig(dmgr['linkDict']['linkPlots'] + yidx + '_violinplot.png')

    if params['show']:
        plt.show()


@action('VencoPy')
def linePlot(dmgr, config, params):
    '''
    This action takes in x profiles, orders them into a x-column DataFrame and plots them in x line plots.
    It can be specified if the plot is shown and/or written to plotting directory.

    :param dmgrKeys: List of keys as strings to access data stored in the DataManager.
    :param show: Boolean, should the plot be shown in a seperate window?
    :param write: Boolean, should the plot be written to the plotting directory?
    :return: None
    '''

    length = {}
    length_ref = len(dmgr[params['dmgrKeys'][0]])

    # if not all(length.values() == length_ref):
    # some abort / break statement or some NA-filling

    data = []
    for ident in params['dmgrKeys']:
        data.append(dmgr[ident])
        length[ident] = len(dmgr[ident])

    data_df = pd.concat(data, axis=1)
    data_df.columns = params['dmgrKeys']

    plt.figure()
    data_df.plot()
    ax = plt.subplot(111)

    # Shrink axis
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1,
                 box.width, box.height * 0.8])

    # Put a legend to the right of the current axis
    ax.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
                mode="expand", borderaxespad=0, ncol=2)

    if 'write' in params.keys():
        datalogger.info(dmgr['linkDict']['linkOutput'] + 'multiprofile_lineplot.png')
        if 'stradd' in params.keys():
            plt.savefig(dmgr['linkDict']['linkOutput'] + 'multiprofile_lineplot_' + params['stradd'] + '.png')
        else:
            plt.savefig(dmgr['linkDict']['linkOutput'] + 'multiprofile_lineplot.png')

    if params['show']:
        plt.show()