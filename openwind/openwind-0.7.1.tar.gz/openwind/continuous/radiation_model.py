# Copyright (C) 2019-2021, INRIA
#
# This file is part of Openwind.
#
# Openwind is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Openwind is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openwind.  If not, see <https://www.gnu.org/licenses/>.
#
# For more informations about authors, see the CONTRIBUTORS file

from openwind.continuous import Scaling
from openwind.continuous import (PhysicalRadiation,
                                 RadiationPulsatingSphere,
                                 RadiationPerfectlyOpen,
                                 RadiationPade,
                                 RadiationPade2ndOrder,
                                 RadiationNoncausal,
                                 radiation_from_data)


def radiation_model(model_name, label=None, scaling=Scaling(),
                    convention='PH1'):
    """
    Get a physical radiation corresponding to the given model name.

    This method is able to associate a keyword to a specific
    :py:class:`PhysicalRadiation\
    <openwind.continuous.physical_radiation.PhysicalRadiation>`.
    The keywords can be:

    - the ones specified in :py:attr:`RadiationPade\
        <openwind.continuous.physical_radiation.RadiationPade.COEFS>`
    - the ones specified in :py:attr:`RadiationPade2ndOrder\
        <openwind.continuous.radiation_silva.RadiationPade2ndOrder.COEFS>`
    - the ones specified in :py:attr:`RadiationNoncausal\
        <openwind.continuous.radiation_silva.RadiationNoncausal.COEFS>`
    - "perfectly_open" giving a :py:class:`RadiationPerfectlyOpen\
        <openwind.continuous.physical_radiation.RadiationPerfectlyOpen>`
    - "pulsating_sphere" giving a :py:class:`RadiationPulsatingSphere\
        <openwind.continuous.radiation_pulsating_sphere.RadiationPulsatingSphere>`
    - a tuple with "from_data" and some additional parameters \
        giving a :py:class:`RadiationFromData\
        <openwind.continuous.radiation_from_data.RadiationFromData>`


    Parameters
    ----------
    model_name : str, tuple or :class:`PhysicalRadiation\
        <openwind.continuous.physical_radiation.PhysicalRadiation>`
        The name of a radiation model, its name and the corresponding
        parameters, or an actual :class:`PhysicalRadiation\
        <openwind.continuous.physical_radiation.PhysicalRadiation>`.
        In that case, it is returned unchanged.
    label : str, optional
        the label of the radiation component. The default is None.
    scaling : :py:class:`Scaling<openwind.continuous.scaling.Scaling>`, optional
        object which knows the value of the coefficient used to scale the
        equations. The default is `Scaling()`.
    convention : {'PH1', 'VH1'}
        The basis functions for our finite elements must be of regularity
        H1 for one variable, and L2 for the other.
        Regularity L2 means that some degrees of freedom are duplicated
        between elements, whereas they are merged in H1.
        Convention chooses whether P (pressure) or V (flow) is the H1
        variable.
        The default is 'PH1'

    Returns
    -------
    :py:class:`PhysicalRadiation <openwind.continuous.physical_radiation.PhysicalRadiation>`
        The object corresponding to the **model_name**.
    """

    if isinstance(model_name, tuple):
        category, params = model_name
    else:
        category = model_name
        params = None
    args = (label, scaling, convention)

    if label is None and type(category) is str:
        label = category
    if isinstance(category, PhysicalRadiation):
        return category
    if category == 'pulsating_sphere':
        return RadiationPulsatingSphere(params, *args)
    if category == "perfectly_open":
        return RadiationPerfectlyOpen(*args)
    if category in RadiationPade2ndOrder.COEFS.keys():
        return RadiationPade2ndOrder(category, *args)
    if category in RadiationNoncausal.COEFS.keys():
        return RadiationNoncausal(category, *args)
    if category in RadiationPade.COEFS.keys():
        return RadiationPade(category, *args)
    if category == 'from_data':
        return radiation_from_data(*params, *args)
    possibilities = (list(RadiationPade.COEFS.keys()) +
                     list(RadiationPade2ndOrder.COEFS.keys()) +
                     list(RadiationNoncausal.COEFS.keys()) +
                     ['pulsating_sphere', "perfectly_open", 'from_data'])
    raise ValueError("Unknown radiation type '{}'. Chose between: "
                     "{}".format(category, possibilities))
