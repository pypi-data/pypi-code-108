
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

"""Module for the exitator classes"""

from abc import ABC, abstractmethod
import warnings

from openwind.continuous import NetlistConnector


def create_excitator(player, label, scaling, convention):
    """
    Instanciate the right excitator according to the player information

    Parameters
    ----------
    player : :py:class:`Player<openwind.technical.player.Player>`
        The object with the excitator information.
    label : str
        The label of the connector.
    scaling : :py:class: `Scaling <openwind.continuous.scaling.Scaling>`
        Nondimensionalization coefficients.
    convention : str, optional
        Must be one out of {'PH1', 'VH1'} \
        The convention used in this component. The default is 'PH1'.

    Returns
    -------
    :py:class:`Excitator<Excitator>`
        The rigth excitator object.

    """
    exc_type = player.excitator_type

    if exc_type == "Flow":
        return Flow(player.control_parameters, label, scaling, convention)
    elif exc_type == "Reed1dof":
        return Reed1dof(player.control_parameters, label, scaling, convention)
    else:
        raise ValueError("Could not convert excitator type '{:s}'; please chose"
                         " between {}".format(exc_type, ["Flow", "Reed1dof"]))

class ExcitatorParameter(ABC):
    """
    Abstract class for excitator parameter

    An excitator parameter can be any parameter asociated to the model of
    the excitator. It can be stationnary or evolving with respect to time.

    """
    @abstractmethod
    def get_value(self,t):
        """
        Method which returns the curve value for a given time t

        Parameters
        ----------
        t : float
            The time at which we want to get the curve value

        Returns
        -------
        float
            the value of the parameter at the time t
        """
        pass


class VariableExcitatorParameter(ExcitatorParameter):
    """
    Class for any excitator parameter which varies with respect to time.

    Parameters
    ----------
    curve : callable
        time dependant function. For example, you can use a curve from the
        module :py:mod:`Temporal Curve <openwind.technical.temporal_curves>`.

    """
    def __init__(self,curve):
        self._variable_value = curve

    def get_value(self,t):
        return self._variable_value(t)


class FixedExcitatorParameter(ExcitatorParameter):
    """
    Class for stationnary excitator parameter

    Parameters
    ----------
    curve : float
        Fixed value for the parameter
    """
    def __init__(self, curve):
        self._fixed_value = curve


    def get_value(self,t):
        return self._fixed_value


class Excitator(ABC, NetlistConnector):
    """
    One excitator, a source of the acoustic oscillations.

    It a component of a :py:class:`Netlist<openwind.continuous.netlist.Netlist>`
    which interacts with a :py:class:`PipeEnd<openwind.continuous.netlist.PipeEnd>`.

    The excitator is typically an oscillator coupled with the acoustic fields.
    It brings the energy into the acoustical system. It is generally described
    trough a set of ODE, the coefficients of which can vary with time.

    Parameters
    ----------
    control_parameters : dict
        Associate each controle parameter (coefficient of the ODE) to its value
        and the evolution with respect to time. It must have all the keys
        necessary to instanciate the right excitator.
    label : str
        the label of the connector
    scaling : :py:class:`Scaling<openwind.continuous.scaling.Scaling>`
        object which knows the value of the coefficient used to scale the
        equations
    convention : {'PH1', 'VH1'}
        The basis functions for our finite elements must be of regularity
        H1 for one variable, and L2 for the other.
        Regularity L2 means that some degrees of freedom are duplicated
        between elements, whereas they are merged in H1.
        Convention chooses whether P (pressure) or V (flow) is the H1
        variable.

    """
    def __init__(self, control_parameters, label, scaling, convention):
        super().__init__(label, scaling, convention)
        self._update_fields(control_parameters)


    @abstractmethod
    def _update_fields(self, control_parameters):
        """
        This method update all the attributes according to the
        control_parameters fields attributes

        Parameters
        ----------
        control_parameters : dict
            Associate each controle parameter (coefficient of the ODE) to its value
            and the evolution with respect to time. It must have all the keys
            necessary to instanciate the right excitator.
        """

    @staticmethod
    def _create_parameter(curve):
        if callable(curve):
            return VariableExcitatorParameter(curve)
        else:
            return FixedExcitatorParameter(curve)


class Flow(Excitator):
    """
    Flow excitator: imposes the value of the flow at the connected pipe-end.

    This excitator simply imposes the flow at the pipe-end connected to it. The
    only parameter is the flow in m^3/s


    See Also
    --------
    :py:class:`FrequentialSource\
        <openwind.frequential.frequential_source.FrequentialSource>`
        The frequential version of this excitator (only has a sense for dirac flow)
    :py:class:`TemporalFlowCondition\
        <openwind.temporal.tflow_condition.TemporalFlowCondition>`
        The temporal version of this excitator

    Parameters
    ----------
    control_parameters : dict
        Associate each controle parameter (coefficient of the ODE) to its value
        and the evolution with respect to time. It must have only the key
        "input_flow".
    label : str
        the label of the connector
    scaling : :py:class:`Scaling<openwind.continuous.scaling.Scaling>`
        object which knows the value of the coefficient used to scale the
        equations
    convention : {'PH1', 'VH1'}
        The basis functions for our finite elements must be of regularity
        H1 for one variable, and L2 for the other.
        Regularity L2 means that some degrees of freedom are duplicated
        between elements, whereas they are merged in H1.
        Convention chooses whether P (pressure) or V (flow) is the H1
        variable.

    Attributes
    ----------
    input_flow : float or callable
        The value in m^3/s of the flow at the entrance of the instrument or its
        evolution with time
    """

    def _update_fields(self, control_parameters):
        self.input_flow = self._create_parameter(control_parameters["input_flow"])


# TODO : write this class methods
class Flute(Excitator):
    """class for a flute excitator, to define"""
    def __init__(self, player, label, scaling, convention):
        raise NotImplementedError()


class Reed1dof(Excitator):
    """
    Reed excitator (cane or lips): non-linear excitator

    A reed excitator is used to model both brass (lips-reeds) and woodwind
    (cane-reed) instruments. It can be, following [Fletcher]_ nomeclature, an:

    - outwards valve (lips-reeds) for brass: the reed opens when the supply \
    pressure is higher than the pressure inside the instrument
    - inwards valve (cane-reed) for simple or double reed instruments: the reed \
    opens when the supply pressure is smaller than the pressure inside the\
    instrument

    The reed is modelled by a 1D damped mass-spring oscillator following
    [Bilbao]_. The contact at closure is modelled through a penalizating term.

    .. math::
        \\begin{align}
        &\\ddot{y} + 2 \\sigma \\dot{y} + \\omega_0^2 (y - y_0) - \
            \\frac{\\omega_1^{\\alpha+1}}{y_0^{\\alpha-1}}(|[y]^{-}|)^{\\alpha}\
            = - \\epsilon \\frac{S_r \\Delta p}{M_r} \\\\
        &\\Delta p = p_m - p \\\\
        & u = w [y]^{+} \\sqrt{\\frac{2 |\\Delta p|}{\\rho}} sign(\\Delta p) \
            - Sr \\dot{y}
        \\end{align}

    With :math:`y` the position of the reed, :math:`[y]^{\\pm}` the positive
    or negative part of :math:`y`, :math:`p,u` the acoustic fields inside the
    instrument and :math:`\\rho` the air density.

    The other coefficients must be specified by the user. They are:

    - "opening" :math:`y_0` : the resting opening height of the reed (in m)
    - "mass" :math:`M_r` : the effective mass of the reed (in kg)
    - "section" :math:`S_r` : the effective vibrating surface of the reed  \
    (and not the opening) (in m²)
    - "pulsation" :math:`\\omega_0` : the resonant angular frequency of the reed
    - "dissip" :math:`\\sigma` : the damping coefficient
    - "width" :math:`w` : the effective width of the reed channel opening (in m)
    - "mouth_pressure" :math:`p_m` : the supply pressure (in Pa)
    - "model" : string coefficient that specifies if it is a "cane" (inwards)\
        or "lips" (inwards) reed. It fixes the value of :math:`\\epsilon` to \
        1 (cane) or -1 (lips)
    - "contact_pulsation" :math:`\\omega_1` : the angular frequency associated\
        to the contact law when the reed is closed.
    - "contact_exponent" :math:`\\alpha` : the exponent associated to the \
        contact law when the reed is closed.


    .. warning::
        This excitator can be used only in temporal domain

    See Also
    --------
    :py:class:`TemporalReed1dof\
        <openwind.temporal.treed.TemporalReed1dof>`
        The temporal version of this excitator

    References
    ----------
    .. [Bilbao] Bilbao, S. (2009). Direct simulation of reed wind instruments.\
        Computer Music Journal, 33(4), 43-55.
    .. [Fletcher] Fletcher, N H. 1979. “Excitation Mechanisms in Woodwind and \
        Brass Instruments.” Acustica 43: 10.


    Parameters
    ----------
    control_parameters : dict
        Associate each controle parameter (coefficient of the ODE) to its value
        and the evolution with respect to time. It must have the keys
        `["opening", "mass", "section", "pulsation", "dissip", "width",
        "mouth_pressure", "model", "contact_pulsation", "contact_exponent"]`.
    label : str
        the label of the connector
    scaling : :py:class:`Scaling<openwind.continuous.scaling.Scaling>`
        object which knows the value of the coefficient used to scale the
        equations
    convention : {'PH1', 'VH1'}
        The basis functions for our finite elements must be of regularity
        H1 for one variable, and L2 for the other.
        Regularity L2 means that some degrees of freedom are duplicated
        between elements, whereas they are merged in H1.
        Convention chooses whether P (pressure) or V (flow) is the H1
        variable.

    Attributes
    ----------
    opening : float or callable
        :math:`y_0` : the resting opening height of the reed (in m)
    mass : float or callable
        :math:`M_r` : the effective mass of the reed (in kg)
    section : float or callable
        :math:`S_r` : the effective vibrating surface of the reed
        (and not the opening) (in m²)
    pulsation : float or callable
        :math:`\\omega_0` : the resonant angular frequency of the reed
    dissip : float or callable
        :math:`\\sigma` : the damping coefficient
    width : float or callable
        :math:`w` : the effective width of the reed channel opening (in m)
    mouth_pressure : float or callable
        :math:`p_m` : the supply pressure (in Pa)
    model : -1 or 1
        :math:`\\epsilon` the opening sens of the reed: 1 (cane,\
        inwards) or -1 (lips, outwards)
    contact_pulsation : float or callable
        :math:`\\omega_1` : the angular frequency associated to the contact \
        law when the reed is closed.
    contact_exponent : float or callable
        :math:`\\alpha` : the exponent associated to the contact law when the\
        reed is closed.
    """

    def _update_fields(self, control_parameters):

        self.mouth_pressure = self._create_parameter(control_parameters["mouth_pressure"])

        # currently only constant value are accepted for other parameters
        # the numerical schemes are not compatible with varaible coefficients.
        self.opening = self._create_cst_param(control_parameters["opening"])
        self.mass = self._create_cst_param(control_parameters["mass"])
        self.section = self._create_cst_param(control_parameters["section"])
        self.pulsation = self._create_cst_param(control_parameters["pulsation"])
        self.dissip = self._create_cst_param(control_parameters["dissip"])
        self.width = self._create_cst_param(control_parameters["width"])
        self.contact_pulsation =  self._create_cst_param(control_parameters["contact_pulsation"])
        self.contact_exponent =  self._create_cst_param(control_parameters["contact_exponent"])

        # the value of epsilon is set by interpreting the keyword in "model"
        model = control_parameters['model']
        if model in ["lips","outwards"]:
            model_value = 1
        elif model in ["cane","inwards"]:
            model_value= -1
        else:
            warnings.warn("WARNING : your model is %s, but it must "
                  "be in {'lips', 'outwards', 'cane', 'inwards'}, it "
                  "will be set to default (lips)"
                  %model)
            model_value = 1
        self.model = FixedExcitatorParameter(model_value)


    @staticmethod
    def _create_cst_param(curve):
        if callable(curve):
            raise ValueError("Except 'mouth_pressure', evolving parameters of "
                             "Reed1dof Excitator are not supported yet, must be a"
                             " constant value")
        else:
            return FixedExcitatorParameter(curve)


    def get_all_values(self, t):
        """
        Method that returns the values of all the parameters at a given time

        Parameters
        ----------
        t : int
            The given time we want to get the curves values from

        Returns
        -------
        Sr : float
            the effective cross section area of the reed (in m²)
        Mr: float
            the effecitve mass of the read (in kg)
        g: float
            the damping coefficient
        omega02: float
             the squared resonant angular frequency
        w: float
            the effective width of the reed channel opening (in m)
        y0: float
            the resting opening of the reed (in m)
        epsilon: float
            1 (for lips/outwards) or -1 (cane/inwards) following the model
        pm: float
            the supply pressure (in Pa)
        """
        Sr = self.section.get_value(t)
        Mr = self.mass.get_value(t)
        g = self.dissip.get_value(t)
        omega02 = self.pulsation.get_value(t)**2
        w = self.width.get_value(t)
        y0 = self.opening.get_value(t)
        epsilon = self.model.get_value(t)
        pm= self.mouth_pressure.get_value(t)

        return (Sr, Mr, g, omega02, w, y0, epsilon, pm)
