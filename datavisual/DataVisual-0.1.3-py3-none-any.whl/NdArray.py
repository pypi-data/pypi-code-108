#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import copy
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import rcParams



from DataVisual.Tools.utils       import FormatStr, _ToList
from DataVisual.Tools.PlotsUtils  import ExperimentPlot
from DataVisual.Tools.Tables      import _XTable, _YTable

mpl.style.use('ggplot')
rcParams['font.family'] = 'serif'
rcParams['axes.edgecolor'] = 'black'
rcParams['axes.linewidth'] = 1.5


class DataV(object):
    def __init__(self, array, Xtable, Ytable):

        self.Data   = array

        self.Xtable = _XTable(Xtable)

        self.Ytable = _YTable(Ytable)



    @FormatStr
    def Cost(self, arg = 'max'):
        """Method return cost function evaluated as defined in the ___ section
        of the documentation.

        Parameters
        ----------
        arg : :class:`str`
            String representing the cost function.

        Returns
        -------
        :class:`float`
            The evaluated cost.

        """

        arg = arg.lower().split('+', 2)

        if len(arg) == 1:
            if   'max'  in arg : return np.max(self)
            elif 'min'  in arg : return np.min(self)
            elif 'mean' in arg : return np.mean(self)

        if len(arg) == 2:
            if   arg[0] == 'rsd'          : func = self.rsd
            elif arg[0] == 'monotonic'    : func = self.Monotonic

            if   arg[1] == 'ri'           : return np.mean( func(self.Data, axis = 4) )
            elif arg[1] == 'diameter'     : return np.mean( func(self.Data, axis = 3) )
            elif arg[1] == 'polarization' : return np.mean( func(self.Data, axis = 2) )
            elif arg[1] == 'wavelength'   : return np.mean( func(self.Data, axis = 1) )
            elif arg[1] == 'detector'     : return np.mean( func(self.Data, axis = 0) )

        raise ValueError(f"Invalid metric input. \nList of metrics: {MetricList}")



    def Monotonic(self, axis):
        """Method compute and the monotonic value of specified axis.
        The method then return a new DataV daughter object compressed in
        the said axis.

        Parameters
        ----------
        axis : :class:`str`
            Axis for which to perform the operation.

        Returns
        -------
        :class:`DataV`
            New DataV instance containing the monotonic metric value of axis.

        """

        arr  = np.gradient(self.Data,
                           axis = self.Table[axis]).std( axis = self.Table[axis])

        return DataV(arr, Xtable=self.Xtable, Ytable=self.Ytable)



    def Mean(self, axis):
        """Method compute and the mean value of specified axis.
        The method then return a new DataV daughter object compressed in
        the said axis.

        Parameters
        ----------
        axis : :class:`str`
            Axis for which to perform the operation.

        Returns
        -------
        :class:`DataV`
            New DataV instance containing the mean value of axis.

        """
        arr          = np.mean(self.Data, axis=self.Xtable.NameTable[axis] )

        newTable     = self.Xtable.Remove(axis)

        return DataV(arr, Xtable=newTable, Ytable=self.Ytable)



    def Std(self, axis):
        """Method compute and the std value of specified axis.
        The method then return a new DataV daughter object compressed in
        the said axis.

        Parameters
        ----------
        axis : :class:`str`
            Axis for which to perform the operation.

        Returns
        -------
        :class:`DataV`
            New DataV instance containing the std value of axis.

        """

        arr          = np.std(self.Data, axis=self.Xtable.NameTable[axis] )

        newTable     = self.Xtable.Remove(axis)
        Array        = DataV(array=arr, Xtable=newTable, Ytable=self.Ytable)

        return Array


    def Weights(self, Weight, axis):
        """Method add weight to array in the said axis.

        Parameters
        ----------
        axis : :class:`str`
            Axis for which to perform the operation.

        Returns
        -------
        :class:`DataV`
            New DataV instance containing the std value of axis.

        """


        arr          = np.multiply(self.Data, Weight, axis =self.Xtable.NameTable[axis])
        Array        = DataV(array=arr, Xtable=newTable, Ytable=self.Ytable)

        return Array


    def Rsd(self, axis):
        """Method compute and the rsd value of specified axis.
        The method then return a new DataV daughter object compressed in
        the said axis.
        rsd is defined as std/mean.

        Parameters
        ----------
        axis : :class:`str`
            Axis for which to perform the operation.

        Returns
        -------
        :class:`DataV`
            New DataV instance containing the rsd value of axis.

        """

        arr  = np.std(self.Data, axis=self.Xtable.NameTable[axis] ) \
              /np.mean(self.Data, axis=self.Xtable.NameTable[axis] )

        newTable     = self.Xtable.Remove(axis)
        Array        = DataV(array=arr, Xtable=newTable, Ytable=self.Ytable)

        return Array

    @ExperimentPlot
    def Plot(self, y, x, figure=None, ax=None, Polar=False, Normalize=False, Std=None):
        """Method plot the multi-dimensional array with the x key as abscissa.
        args and kwargs can be passed as standard input to matplotlib.pyplot.

        Parameters
        ----------
        x : str
            Key of the self dict which represent the abscissa.
        Scale : str
            Options allow to switch between log and linear scale ['log', 'linear'].

        """
        if Std:
            return self._PlotSTD(y, x, figure=figure, ax=ax, Polar=Polar, Normalize=Normalize, Std=Std)

        else:
            return self._PlotNormal(y, x, figure=figure, ax=ax, Polar=Polar, Normalize=Normalize)


    def _PlotNormal(self, y, x, figure=None, ax=None, Polar=False, Normalize=False):
        """Method plot the multi-dimensional array with the x key as abscissa.
        args and kwargs can be passed as standard input to matplotlib.pyplot.

        Parameters
        ----------
        x : str
            Key of the self dict which represent the abscissa.
        Scale : str
            Options allow to switch between log and linear scale ['log', 'linear'].

        """
        y = _ToList(y)
        X = self.Xtable[x].Value

        for order, Yparameter in enumerate(self.Ytable):
            print(Yparameter.Name, y[0].Name, Yparameter in y, Yparameter.Name ==y[0].Name)
            if Yparameter not in y: continue

            for axis, (idx, XVar) in enumerate( self.Xtable.GetSlicer(x) ):
                idx = list(idx) + [order]

                label, commonLabel = self.Xtable.GetLabels(idx, Exclude=[self.Xtable[x]] )


                Y = self.Data[tuple(idx)]

                if Polar:                X = X / 180*np.pi
                if any(np.iscomplex(Y)): Y = np.abs(Y)
                if Normalize:            Y /= Y.max()

                self._Plot(ax, X, Y, Yparameter.Label + label, self.Xtable[x], Yparameter)

        plt.gcf().text(0.13,
                       0.91,
                       commonLabel,
                       fontsize  = 8,
                       bbox      = dict(facecolor='none', edgecolor = 'black', boxstyle  = 'round'))



    def _PlotSTD(self, y, x, figure, ax, Polar, Normalize, Std):
        y = _ToList(y)
        X = self.Xtable[x].Value


        STD = self.Std(Std)
        MEAN = self.Mean(Std)

        for order, Yparameter in enumerate(self.Ytable):
            for axis, (idx, XVar) in enumerate( MEAN.Xtable.GetSlicer(x) ):

                M = MEAN.Data[tuple(idx)].squeeze()
                S = STD.Data[tuple(idx)].squeeze()

                label, commonLabel = MEAN.Xtable.GetLabels(idx, Exclude=[MEAN.Xtable[x]] )

                p = self._Plot(ax, X, M, Yparameter.Label + label, MEAN.Xtable[x], Yparameter)

                ax.fill_between(X, M-S, M+S, alpha=0.3, color=p[-1].get_color())


        plt.gcf().text(0.13,
                       0.91,
                       commonLabel,
                       fontsize  = 8,
                       bbox      = dict(facecolor='none', edgecolor = 'black', boxstyle  = 'round'))


    def _Plot(self, ax,  X, Y, label, Xparameter, Yparameter):
        p = ax.plot(X, Y, label=label)
        ax.set_xlabel(Xparameter.Legend, fontsize=15)
        ax.set_ylabel(Yparameter.Legend, fontsize=15)
        ax.xaxis.set_tick_params(labelsize=12)
        ax.yaxis.set_tick_params(labelsize=12)
        ax.grid(True)
        return p


    def SaveFig(self, Directory='newFig', dpi=200, *args, **kwargs):
        dir = os.path.join(ZeroPath, Directory) + '.png'
        fig = self._Plot(*args, **kwargs)
        print(f'Saving figure in {dir}...')
        fig.savefig(dir, dpi=dpi)



    def GetLegend(self, axis, idx, Yparameter):
        """Method generate and return the legend text for the specific plot.

        Parameters
        ----------
        axis : :class:`str`
            Axis which is used for x-axis of the specific plot
        idx : :class:`tuple`
            Dimension indices of the specific plot

        Returns
        -------
        :class:`str`
            Text for the legend

        """

        diff = Yparameter.Legend

        common = ''

        for order, Parameter in enumerate(self.Xtable):

            if axis == Parameter.Name: continue

            val = Parameter.Value[idx[order]]

            if Parameter.GetSize() != 1:
                diff += Parameter.str(idx[order])
            else:
                common += Parameter.str(idx[order])

        return diff, common



    def __str__(self):
        name = [parameter.Name for parameter in self.Ytable]

        newLine = '\n' + '=' * 120 + '\n'

        text =  f'PyMieArray \nVariable: {name.__str__()}' + newLine

        text += "Parameter" + newLine

        for xParameter in self.Xtable:
            text += f"""| {xParameter.Label:40s}\
            | dimension = {xParameter.Name:30s}\
            | size      = {xParameter.GetSize()}\
            \n"""

        text += newLine

        text += "Numpy data are accessible via the <.Data> attribute"

        return text



class Opt5DArray(np.ndarray):
    def __new__(cls, *args, **kwargs):
        this = np.array(*args, **kwargs, copy=False)
        this = np.asarray(this).view(cls)

        return this


    def __array_finalize__(self, obj):
        pass


    def __init__(self, arr, Name=''):
        self.Name         = Name

        self.dim = { 'detector'     : True,
                     'wavelength'   : True,
                     'polarization' : True,
                     'diameter'     : True,
                     'index'        : True}

    @FormatStr
    def DefineCostFunc(self, arg):
        arg = arg.lower().split('+', 2)

        if len(arg) == 1:
            if   'max'  in arg : self.CostFunc = np.max
            elif 'min'  in arg : self.CostFunc = np.min
            elif 'mean' in arg : self.CostFunc = np.mean

        if len(arg) == 2:
            if   arg[0] == 'rsd'       : func = self.rsd
            elif arg[0] == 'monotonic' : func = self.Monotonic
            elif arg[0] == 'max'       : func = np.max
            elif arg[0] == 'min'       : func = np.min
            elif arg[0] == 'mean'      : func = np.mean


            if   arg[1] == 'all'          : self.CostFunc = np.mean( func(self) )
            elif arg[1] == 'ri'           : self.CostFunc = np.mean( func(self, axis = 4) )
            elif arg[1] == 'diameter'     : self.CostFunc = np.mean( func(self, axis = 3) )
            elif arg[1] == 'polarization' : self.CostFunc = np.mean( func(self, axis = 2) )
            elif arg[1] == 'wavelength'   : self.CostFunc = np.mean( func(self, axis = 1) )
            elif arg[1] == 'detector'     : self.CostFunc = np.mean( func(self, axis = 0) )

            raise ValueError(f"Invalid metric input. \nList of metrics: {MetricList}")

    def Cost(self):

        return self.CostFunc(self)

    def Monotonic(self, axis):

        Grad = np.gradient(self, axis = axis)

        STD = Grad.std( axis = axis)

        return STD[0]


    def rsd(self, array, axis):
        return np.std(array, axis)/np.mean(array, axis)


    def RIMonotonic(self):

        Grad = np.gradient(self, axis = 0)

        STD = Grad.std( axis = 0)

        return STD[0]
