import dataclasses
import math as _math
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum as _Enum, Enum
from typing import Optional

import qm.program.expressions as _exp
from qm import _Program
from qm.ExpressionSerializingVisitor import ExpressionSerializingVisitor
from qm._deprecated import deprecated
from qm.logger import logger
from qm.pb.inc_qua_pb2 import QuaProgram as _Q
from qm.program.StatementsCollection import (
    StatementsCollection as _StatementsCollection,
)
from qm.program._ResultAnalysis import _ResultAnalysis, _ResultSymbol
from qm.qua import AnalogMeasureProcess
from qm.qua import DigitalMeasureProcess
from qm.utils import fix_object_data_type as _fix_object_data_type

_TIMESTAMPS_LEGACY_SUFFIX = "_timestamps"

_block_stack = []


def program():
    """
    Create a QUA program.

    Used within a context manager, the program is defined in the code block
    below ``with`` statement.

    Statements in the code block below are played as soon as possible, meaning that an instruction
    will be played immediately unless it is dependent on a previous instruction.
    Additionally, commands output to the same quantum elements will be played sequentially,
    and to different quantum elements will be played in parallel.
    An exception is that pulses will be implicitly aligned at the end of each :func:`for_` loop iteration.

    The generated ``program_name`` object is used as an input to the execute function of a
    :class:`QuantumMachine<qm.QuantumMachine>` object.

    Example of creating a QUA program::

        with program() as program_name:
            play('pulse1', 'element1')
            wait('element1')

    Example of executing the program on a quantum machine::

        my_qm.execute(program_name)

    where ``my_qm`` is an instance of a :class:`QuantumMachine<qm.QuantumMachine>`
    """
    return _ProgramScope(_Program())


def play(
    pulse, element, duration=None, condition=None, chirp=None, truncate=None, **kwargs
):
    r"""
    Play a `pulse` to an `element`.

    The pulse will be modified according to the properties of the element
    (see detailed explanation about pulse modifications below),
    and then played to the OPX output(s) defined to be connected
    to the input(s) of the element in the configuration.

    :param pulse: Name of the pulse, as defined in the quantum machine configuration.
    :type pulse: str
    :param element: Name of the quantum element, as defined in the quantum machine configuration.
    :type element: str
    :param duration:    The time to play this pulse in units of the clock cycle (4ns).
                        If not provided, the default pulse duration will be used. It is possible to
                        dynamically change the duration of both constant and arbitrary
                        pulses. See `Dynamic pulse duration <https://qm-docs.qualang.io/guides/features#dynamic-pulse-duration>`__
                        in the documentaition for further information.
    :type duration: Union[int,QUA variable of type int]
    :param chirp:   Allows to perform piecewise linear sweep of the element’s
                    intermediate frequency in time. Input should be a tuple, with the
                    1st element being a list of rates and the second should be a string
                    with the units. The units can be either:
                    ‘Hz/nsec’, ’mHz/nsec’, ’uHz/nsec’, ’pHz/nsec’
                    or
                    ‘GHz/sec’, ’MHz/sec’, ’KHz/sec’, ’Hz/sec’, ’mHz/sec’.
                    See the `chirp documentation <https://qm-docs.qualang.io/guides/features#frequency-chirp>`__
                    for more information.
    :type chirp: Union[(list[int], str), (int, str)]
    :param truncate:    Allows playing only part of the pulse, truncating the end.
                        If provided, will play only up to the given time in units of the
                        clock cycle (4ns).
    :type truncate:     Union[int, QUA variable of type int]
    :param condition:   Will play analog pulse only if the condition's value is true.
                        Any digital pulses associated with the operation will always
                        play.
    :type condition: A logical expression to evaluate

    .. note::
        Arbitrary waveforms cannot be compressed and can only be expanded up to
        2\ :sup:`24`-1 clock cycles (67ms). Unexpected output will occur if a duration
        outside of the range is given.

    .. note::
        It is possible to scale the pulse's amplitude dynamically by using the following syntax:

        ``play('pulse_name' * amp(v), 'element')``

        where ``v`` is QUA variable of type fixed. Range of v: -2 to 2 - 2\ :sup:`-16` in steps of 2\ :sup:`-16`.

        Moreover, if the pulse is intended to a mixedInputs element and thus is defined with two waveforms,
        the two waveforms, described as a column vector, can be multiplied by a matrix:

        ``play('pulse_name' * amp(v_00, v_01, v_10, v_11), 'element'),``

        where ``v_ij``, i,j={0,1}, are QUA variables of type fixed.
        Note that ``v_ij`` should satisfy -2 <= ``v_ij`` <= 2 - 2\ :sup:`-16`.

        Note that scaling in this manner, rather than in the configuration, might result
        in a computational overhead.
        See `QUA “Best Practice” Guide <https://qm-docs.qualang.io/guides/best_practices#general>`__ for more information.

    Example::

    >>> with program() as prog:
    >>>     v1 = declare(fixed)
    >>>     assign(v1, 0.3)
    >>>     play('pulse1', 'element1')
    >>>     play('pulse1' * amp(0.5), 'element1')
    >>>     play('pulse1' * amp(v1), 'element1')
    >>>     play('pulse1' * amp(0.9, v1, -v1, 0.9), 'element_iq_pair')
    """
    body = _get_scope_as_blocks_body()
    if duration is not None:
        duration = _unwrap_exp(exp(duration))
    if condition is not None:
        condition = _unwrap_exp(exp(condition))
    if truncate is not None:
        truncate = _unwrap_exp(exp(truncate))
    target = ""
    if "target" in kwargs:
        target = kwargs["target"]

    if chirp is not None:
        if len(chirp) == 2:
            chirp_var, chirp_units = chirp
            chirp_times = None
        elif len(chirp) == 3:
            chirp_var, chirp_times, chirp_units = chirp
        else:
            raise RuntimeError("chirp must be tuple of 2 or 3 values")
        if isinstance(chirp_var, list):
            chirp_var = declare(int, value=chirp_var)
        chirp_var = _unwrap_exp(exp(chirp_var))
        chirp = _Q.Chirp()
        if chirp_times is not None:
            chirp.times.extend(chirp_times)
        if isinstance(chirp_var, _Q.ArrayVarRefExpression):
            chirp.arrayRate.CopyFrom(chirp_var)
        else:
            chirp.scalarRate.CopyFrom(chirp_var)
        if chirp_units == "Hz/nsec" or chirp_units == "GHz/sec":
            chirp.units = _Q.Chirp.HzPerNanoSec
        elif chirp_units == "mHz/nsec" or chirp_units == "MHz/sec":
            chirp.units = _Q.Chirp.mHzPerNanoSec
        elif chirp_units == "uHz/nsec" or chirp_units == "KHz/sec":
            chirp.units = _Q.Chirp.uHzPerNanoSec
        elif chirp_units == "nHz/nsec" or chirp_units == "Hz/sec":
            chirp.units = _Q.Chirp.nHzPerNanoSec
        elif chirp_units == "pHz/nsec" or chirp_units == "mHz/sec":
            chirp.units = _Q.Chirp.pHzPerNanoSec
        else:
            raise RuntimeError(f'unknown units "{chirp[1]}"')

    body.play(
        pulse,
        element,
        duration=duration,
        condition=condition,
        target=target,
        chirp=chirp,
        truncate=truncate,
    )


def pause():
    """
    Pause the execution of the job until :func:`~qm.QmJob.QmJob.resume` is called.

    The quantum machines freezes on its current output state.
    """
    body = _get_scope_as_blocks_body()
    body.pause()


def update_frequency(element, new_frequency, units="Hz", keep_phase=False):
    """
    Dynamically update the frequency of the oscillator associated with a given `element`.

    This changes the frequency from the value defined in the quantum machine configuration.

    The behavior of the phase (continuous vs. coherent) is controlled by the ``keep_phase`` parameter and
    is discussed in :ref:`Introduction/qua_overview:Frequency and phase transformations`.

    :param element: The quantum element associated with the oscillator whose frequency will be changed
    :type element: str
    :param new_frequency: The new frequency value to set in units set by ``units`` parameter. In steps of 1.
    :type new_frequency: int
    :param units: units of new frequency. Useful when sub-Hz precision is required. Allowd units are "Hz", "mHz", "uHz", "nHz", "pHz"
    :type units: str
    :param keep_phase: Determine whether phase will be continuous through the change (if ``True``) or it will be coherent, only the frequency will change (if ``False``).
    :type keep_phase: bool

    Example::

    >>> with program() as prog:
    >>>     update_frequency("q1", 4e6) # will set the frequency to 4 MHz
    >>>
    >>>     ### Example for sub-Hz resolution
    >>>     update_frequency("q1", 100.7) # will set the frequency to 100 Hz (due to casting to int)
    >>>     update_frequency("q1", 100700, units='mHz') # will set the frequency to 100.7 Hz

    """
    body = _get_scope_as_blocks_body()
    body.update_frequency(element, _unwrap_exp(exp(new_frequency)), units, keep_phase)


def update_correction(element, c00, c01, c10, c11):
    """
    Updates the correction matrix used to overcome IQ imbalances of the IQ mixer for the next pulses
    played on the element

    .. note::

        Make sure to update the correction after you called :func:`update_frequency`

    .. warning::

        Calling ``update_correction`` will also reset the frame of the oscillator associated with the quantum element.

    :param element: The quantum element associated with the oscillator whose correction matrix will change
    :param c00: This, together with the subsequent elements, determines the elements of the correction matrix.
    :param c01:
    :param c10:
    :param c11:

    :type element: str
    :type c00: Union[float,QUA variable of type real]
    :type c01: Union[float,QUA variable of type real]
    :type c10: Union[float,QUA variable of type real]
    :type c11: Union[float,QUA variable of type real]

    Example::

    >>> with program() as prog:
    >>>     update_correction("q1", 1.0, 0.5, 0.5, 1.0)

    """
    body = _get_scope_as_blocks_body()
    body.update_correction(
        element,
        _unwrap_exp(exp(c00)),
        _unwrap_exp(exp(c01)),
        _unwrap_exp(exp(c10)),
        _unwrap_exp(exp(c11)),
    )


def set_dc_offset(element, input_reference, offset):
    """
    Set the DC offset of an element input.

    -- Available from QOP 2.20 --

    :param element: quantum element to set DC offset to

    :param input_reference: desired input of the quantum element

    :param offset: offsets to set - one offset for a single element and up to two offsets for a mixed element using the following template (I dc offset, Q dc offset)

    """

    body = _get_scope_as_blocks_body()
    body.set_dc_offset(element, input_reference, _unwrap_exp(exp(offset)))


def measure(pulse, element, stream=None, *outputs):
    """
    Perform a measurement of `element` using `pulse`.

    An element for which a measurement is applied must have outputs defined in the configuration.

    A measurement consists of:

    1. playing a pulse to the element (identical to a :func:`play` statement)

    2. waiting for a duration of time defined as the ``time_of_flight``
       in the configuration of the element, and then sampling
       the returning pulse.
       The OPX input to be sampled is defined in the configuration of the element.

    3. demodulating and the acquired data from the indicated element's output
       at the ``intermediate_frequency`` defined in the configuration of the element,
       using integration weights defined in the configuration of the pulse,
       and storing the result in the provided variables.

    For a more detailed description of the measurement operation, see
    `Measure Statement Features <https://qm-docs.qualang.io/guides/features.html#measure-statement-features>`__


    :param pulse:
        Name of the pulse, as defined in the quantum machine configuration.
        Pulse must have a ``measurement`` operation.

    :param element: name of the element, as defined in the quantum machine configuration. The element must have outputs.

    :param stream:
        The stream variable which the raw ADC data will be saved and will appear in result analysis scope.
        You can receive the results with :func:`~qm.QmJob.result_handles.get("name")`.
        A string name can also be used. In this case, the name of the result handle should be suffixed by ``_input1``
        for data from analog input 1 and ``_input2`` for data from analog input 2.

        If ``stream`` is set to ``None``, raw results will not be saved
        (note: must be explicitly set to ``None``).
        The raw results will be saved as long as the digital pulse that is played with pulse is high.

        .. warning::

            Streaming adc data without declaring the stream with `declare_stream(adc_trace=true)` might cause performance issues

    :param outputs:

        A parameter specifying the processing to be done on the ADC data, there are
        multiple options available, including Demodulation, Integration & TimeTagging.
        See `Measure Statement Features <https://qm-docs.qualang.io/guides/features.html#measure-statement-features>`__
        for more information


    :type pulse: str
    :type element: str
    :type stream: str or _ResultSource or None
    :type outputs: tuple

    Example::

    >>> with program() as prog:
    >>>     I = declare(fixed)
    >>>     Q = declare(fixed)
    >>>     I_stream = declare_stream()
    >>>
    >>>     # measure by playing 'meas_pulse1' to element 'rr1', do not save raw results.
    >>>     # demodulate using 'cos_weights' and store result in I, and also
    >>>     # demodulate using 'sin_weights' and store result in Q
    >>>     measure('meas_pulse1', 'rr1', None, ('cos_weights', I), ('sin_weights', Q))
    >>>
    >>>     # measure by playing 'meas_pulse2' to element 'rr1', save raw results to tag 'samples'.
    >>>     # demodulate data from 'out1' port of 'rr1' using 'optimized_weights' as integration weights
    >>>     # store result in I
    >>>     measure('meas_pulse2', 'rr1', 'samples', ('optimized_weights', 'out1', I))
    >>>
    >>>     # measure by playing 'meas_pulse2' to element 'rr1', save raw results to object 'I_Stream'. Get raw data of
    >>>     # analog input 1.
    >>>     measure('meas_pulse2', 'rr1', I_Stream)
    >>>     with stream_processing():
    >>>         I_stream.input1().save_all("raw_I_stream")
    >>>
    >>> from qm.QuantumMachinesManager import QuantumMachinesManager
    >>> qm = QuantumMachinesManager().open_qm({}) # note: config missing here
    >>> job = qm.execute(prog)
    >>> # ... we wait for the results to be ready...
    >>> # raw results can be retrieved as follows (here job is a QmJob object:
    >>> raw_I_handle = job.result_handles.get("raw_I_stream")
    >>> # raw results can be retrieved as follows (here job is a QmJob object and qe was defined with analog 1):
    >>> samples_result_handle = job.result_handles.get("samples_input1")
    """
    body = _get_scope_as_blocks_body()

    measure_process = []
    for i, output in enumerate(outputs):
        if type(output) == tuple:
            if len(output) == 2:
                measure_process.append(demod.full(output[0], output[1], ""))
            elif len(output) == 3:
                measure_process.append(demod.full(output[0], output[2], output[1]))
            else:
                raise RuntimeError(
                    "Each output must be a tuple of (integration weight, output name, variable name), but output "
                    + str(i + 1)
                    + " is invalid"
                )
        else:
            measure_process.append(output)

    if stream is not None and isinstance(stream, str):
        result_obj = _get_root_program_scope().declare_legacy_adc(stream)
    else:
        if stream is not None and (not isinstance(stream, _ResultSource)):
            raise RuntimeError("stream object is not of the right type")
        result_obj = stream

    if result_obj and not result_obj._configuration.is_adc_trace:
        logger.warning(
            f"Streaming adc data without declaring the stream with `declare_stream(adc_trace=true)` might cause performance issues"
        )

    body.measure(
        pulse,
        element,
        result_obj,
        *[_unwrap_measure_process(x) for x in measure_process],
    )


def align(*elements: str):
    """
    Align several quantum elements together.

    All of the quantum elements referenced in `elements` will wait for all the others to
    finish their currently running statement.

    If no arguments are given, the statement will align all of the elements used in the
    program.

    :param elements: a single quantum element, a list of quantum elements, or none
    :type elements: str
    """
    body = _get_scope_as_blocks_body()
    body.align(*elements)


def reset_phase(element):
    r"""
    Resets the phase of the oscillator associated with `element`, setting the phase of the next pulse to absolute zero.
    This sets the phase of the currently playing intermediate frequency to the value it had at the beginning of the program (t=0).

    .. note::

        * The phase will only be set to zero when the next play or align command is executed on the element.
        * Reset phase will only reset the phase of the intermediate frequency (:math:`\omega_{IF}`) currently in use.

    :param element: a quantum element
    """
    body = _get_scope_as_blocks_body()
    body.reset_phase(element)


def ramp_to_zero(element, duration=None):
    r"""
    Starting from the last DC value, gradually lowers the DC to zero for `duration` \*4nsec

    If `duration` is None, the duration is taken from the element's config

    .. warning::
        This feature does not protect from voltage jumps. Those can still occur, i.e. when the data sent to the
        analog output is outside the range -0.5 to 0.5 - 2\ :sup:`16` and thus will have an overflow.

    :param element: element for ramp to zero
    :param duration: time , `in multiples of 4nsec`. Range: [4, 2\ :sup:`24`] in steps of 1, or `None` to take value from config
    :type element: str
    :type duration: Union[int,None]
    """
    body = _get_scope_as_blocks_body()
    body.ramp_to_zero(element, duration)


def wait(duration, *elements):
    r"""
    Wait for the given duration on all provided elements without outputting anything.
    Duration is in units of the clock cycle (4ns)

    :param duration: time to wait in units of the clock cycle (4ns).
                     Range: [4, 2\ :sup:`32`-1] in steps of 1.
    :param elements: elements to wait on
    :type duration: Union[int,QUA variable of type int]
    :type elements: Union[str,sequence of str]

    .. warning::

        In case the value of this is outside the range above, unexpected results may occur.

    .. note::

        The purpose of the `wait` operation is to add latency. In most cases, the
        latency added will be exactly the same as that specified by the QUA variable or
        the literal used. However, in some cases an additional computational latency may
        be added. If the actual wait time has significance, such as in characterization
        experiments, the actual wait time should always be verified with a simulator.

    """
    body = _get_scope_as_blocks_body()
    body.wait(_unwrap_exp(exp(duration)), *elements)


def wait_for_trigger(element, pulse_to_play=None, trigger_element=None):
    """
    Wait for an external trigger on the provided element.

    During the command the OPX will play the pulse supplied by the ``pulse_to_play`` parameter

    :param element: element to wait on
    :type element: str
    :param pulse_to_play: the name of the pulse to play on the element while waiting for the external trigger. Must
                          be a constant pulse. Default None, no pulse will be played.
    :type pulse_to_play: str
    :param trigger_element: to be used only with an OPD. See further details in the note.
    :type trigger_element: Union[str, tuple]

    .. warning::
        In the OPX - The maximum allowed voltage value for the digital trigger is 1.8V. A voltage higher than this can damage the
        controller.

        In the OPX+ and with the OPD - The maximum allowed voltage is 3.3V.

    .. note::
        Read more about triggering with the OPD `here <https://qm-docs.qualang.io/hardware/dib#wait-for-trigger>`__

    """
    body = _get_scope_as_blocks_body()
    body.wait_for_trigger(pulse_to_play, trigger_element, element)


def save(var, stream_or_tag):
    """
    Stream a QUA variable, a QUA array cell, or a constant scalar.
    the variable is streamed and not immediately saved (see :ref:`Guides/stream_proc:Stream Processing`).
    In case ``result_or_tag`` is a string, the data will be immediately saved to a result handle under the same name.

    If result variable is used, it can be used in results analysis scope see :func:`stream_processing`
    if string tag is used, it will let you receive result with :attr:`qm.QmJob.QmJob.result_handles`.
    The type of the variable determines the stream datatype, according to the following rule:

    - int -> int64
    - fixed -> float64
    - bool -> bool

    .. note::

        Saving arrays as arrays is not currently supported. Please use a QUA for loop to save an array.

    Example::

    >>>     # basic save
    >>>     a = declare(int, value=2)
    >>>     save(a, "a")
    >>>
    >>>     # fetching the results from python (job is a QmJob object):
    >>>     a_handle = job.result_handles.get("a")
    >>>     a_data = a_handle.fetch_all()
    >>>
    >>>     # save the third array cell
    >>>     vec = declare(fixed, value=[0.2, 0.3, 0.4, 0.5])
    >>>     save(vec[2], "ArrayCellSave")
    >>>
    >>>     # array iteration
    >>>     i = declare(int)
    >>>     array = declare(fixed, value=[x / 10 for x in range(30)])
    >>>     with for_(i, 0, i < 30, i + 1):
    >>>         save(array[i], "array")
    >>>
    >>>     # save a constant
    >>>     save(3, "a")

    :param var: A QUA variable or a QUA array cell to save
    :param stream_or_tag: A stream variable or string tag name to save the value under
    :type var: Union[QUA variable, a QUA array cell]
    :type stream_or_tag: Union[str, stream variable]
    """
    if stream_or_tag is not None and type(stream_or_tag) is str:
        result_obj = _get_root_program_scope().declare_legacy_save(stream_or_tag)
    else:
        result_obj = stream_or_tag

    if result_obj._configuration.is_adc_trace:
        raise Exception("adc_trace can't be used in save")

    body = _get_scope_as_blocks_body()
    body.save(_unwrap_save_source(exp(var)), result_obj)


def frame_rotation(angle, *elements: str):
    r"""
    Shift the phase of the oscillator associated with a quantum element by the given angle.

    This is typically used for virtual z-rotations.

    .. note::
        The fixed point format of QUA variables of type fixed is 4.28, meaning the phase
        must be between -8 and 8 - 2\ :sup:`28`. Otherwise the phase value will be invalid.
        It is therefore better to use `frame_rotation_2pi()` which avoids this issue.

    .. warning::
        The phase is accumulated with a resolution of 16 bit.
        Therefore, *N* changes to the phase can result in a phase (and amplitude) inaccuracy of about :math:`N \cdot 2^{-16}`.
        To null out this accumulated error, it is recommended to use `reset_frame(qe)` from time to time.

    :param angle: The angle to to add to the current phase (in radians)
    :param elements:
        A quantum element, or sequence of quantum elements, associated with the oscillator
        whose phase will be shifted

    :type angle: Union[float, QUA variable of type fixed]
    :type elements: str

    """
    frame_rotation_2pi(angle * 0.15915494309189535, *elements)


def frame_rotation_2pi(angle, *elements: str):
    r"""
    Shift the phase of the oscillator associated with a quantum element by the given angle in units of 2pi radians.

    This is typically used for virtual z-rotations.

    .. note::
        Unlike the case of frame_rotation(), this method performs the 2-pi radian wrap around of the angle automatically.

    .. note::
        The phase is accumulated with a resolution of 16 bit.
        Therefore, *N* changes to the phase can result in a phase inaccuracy of about :math:`N \cdot 2^{-16}`.
        To null out this accumulated error, it is recommended to use `reset_frame(qe)` from time to time.

    :param angle: The angle to to add to the current phase (in 2pi radians)
    :param elements:
        A quantum element, or sequence of quantum elements, associated with the oscillator
        whose phase will be shifted

    :type angle: Union[float,QUA variable of type real]
    :type elements: str
    """
    body = _get_scope_as_blocks_body()
    body.z_rotation(_unwrap_exp(exp(angle)), *elements)


def reset_frame(*elements: str):
    """
    Resets the frame of the oscillator associated with a quantum element to 0.

    Used to reset all of the frame updated made up to this statement.

    :param elements:
        A quantum element, or sequence of quantum elements, associated with the oscillator
        whose phase will be reset

    :type elements: str
    """
    body = _get_scope_as_blocks_body()
    body.reset_frame(*elements)


def assign(var, _exp):
    """
    Set the value of a given QUA variable, or of a QUA array cell

    :param var:  A QUA variable or a QUA array cell for which to assign
    :param _exp: An expression for which to set the variable
    :type var: QUA variable
    :type _exp: QUA expression

    Example::

    >>> with program() as prog:
    >>>     v1 = declare(fixed)
    >>>     assign(v1, 1.3)
    >>>     play('pulse1' * amp(v1), 'element1')
    """
    body = _get_scope_as_blocks_body()
    _exp = exp(_exp)
    _var = exp(var)
    body.assign(_unwrap_assign_target(_var), _unwrap_exp(_exp))


def switch_(expression, unsafe=False):
    """
    Part of the switch-case flow control statement in QUA.

    To be used with a context manager.

    The code block inside should be composed of only ``case_()`` and ``default_()``
    statements, and there should be at least one of them.

    The expression given in the ``switch_()`` statement will be evaluated and compared
    to each of the values in the ``case_()`` statements. The QUA code block following
    the ``case_()`` statement which evaulated to true will be executed. If none of the
    statements evaluated to true, the QUA code block following the ``default_()``
    statement (if given) will be executed.

    :param expression:
        An expression to evaluate

    :param unsafe:
        If set to True, then switch-case would be more efficient and would produce less
        gaps. However, if an input which does not match a case is given, unexpected
        behavior will occur. Cannot be used with the ``default_()`` statement.
        Default is false, use with care.


    Example::

    >>> x=declare(int)
    >>> with switch_(x):
    >>>     with case_(1):
    >>>         play('first_pulse', 'element')
    >>>     with case_(2):
    >>>         play('second_pulse', 'element')
    >>>     with case_(3):
    >>>         play('third_pulse', 'element')
    >>>     with default_():
    >>>         play('other_pulse', 'element')
    """
    body = _get_scope_as_blocks_body()
    return _SwitchScope(expression, body, unsafe)


def case_(case_exp):
    """
    Part of the switch-case flow control statement in QUA.

    To be used with a context manager.

    Must be inside a ``switch_()`` statement.

    The expression given in the ``switch_()`` statement will be evaluated and compared
    to each of the values in the ``case_()`` statements. The QUA code block following
    the ``case_()`` statement which evaulated to true will be executed. If none of the
    statements evaluated to true, the QUA code block following the ``default_()``
    statement (if given) will be executed.

    :param case_exp:
        A value (or expression) to compare to the expression in the
        ``switch_()`` statement

    Example::

    >>> x=declare(int)
    >>> with switch_(x):
    >>>     with case_(1):
    >>>         play('first_pulse', 'element')
    >>>     with case_(2):
    >>>         play('second_pulse', 'element')
    >>>     with case_(3):
    >>>         play('third_pulse', 'element')
    >>>     with default_():
    >>>         play('other_pulse', 'element')
    """
    switch = _get_scope_as_switch_scope()
    condition = _unwrap_exp(switch.expression == case_exp)
    if switch.if_statement is None:
        body = switch.container.if_block(condition, switch.unsafe)
        switch.if_statement = switch.container.get_last_statement()
        return _BodyScope(body)
    else:
        ifstatement = getattr(switch.if_statement, "if")
        elseifs = ifstatement.elseifs
        elseif = elseifs.add()
        elseif.loc = ifstatement.loc
        elseif.condition.CopyFrom(condition)
        return _BodyScope(_StatementsCollection(elseif.body))


def default_():
    """
    Part of the switch-case flow control statement in QUA.

    To be used with a context manager.

    Must be inside a ``switch_()`` statement, and there can only be one ``default_()``
    statement.

    The expression given in the ``switch_()`` statement will be evaluated and compared
    to each of the values in the ``case_()`` statements. The QUA code block following
    the ``case_()`` statement which evaulated to true will be executed. If none of the
    statements evaluated to true, the QUA code block following the ``default_()``
    statement (if given) will be executed.

    Example::

    >>> x=declare(int)
    >>> with switch_(x):
    >>>     with case_(1):
    >>>         play('first_pulse', 'element')
    >>>     with case_(2):
    >>>         play('second_pulse', 'element')
    >>>     with case_(3):
    >>>         play('third_pulse', 'element')
    >>>     with default_():
    >>>         play('other_pulse', 'element')
    """
    switch = _get_scope_as_switch_scope()
    if switch.if_statement is None:
        raise Exception("must specify at least one case before 'default'.")
    else:
        ifstatement = getattr(switch.if_statement, "if")
        if ifstatement.HasField("else") is True:
            raise Exception(
                "only a single 'default' statement can follow a 'switch' statement"
            )
        elsestatement = getattr(ifstatement, "else")
        elsestatement.SetInParent()
        return _BodyScope(_StatementsCollection(elsestatement))


def if_(expression, **kwargs):
    """
    If flow control statement in QUA.

    To be used with a context manager.

    The QUA code block following the statement will be
    executed only if the expression given evaluates to true.

    :param expression: A boolean expression to evaluate

    Example::

    >>> x=declare(int)
    >>> with if_(x>0):
    >>>     play('pulse', 'element')
    """
    if type(expression) == bool:
        expression = exp(expression)
    body = _get_scope_as_blocks_body()

    # support unsafe for serializer
    if_kwargs = {}
    unsafe_name = "unsafe"
    if kwargs.get(unsafe_name):
        if_kwargs[unsafe_name] = kwargs.get(unsafe_name)

    if_body = body.if_block(_unwrap_exp(expression), **if_kwargs)
    return _BodyScope(if_body)


def elif_(expression):
    """
    Else-If flow control statement in QUA.

    To be used with a context manager.

    Must appear after an ``if_()`` statement.

    The QUA code block following the statement will be executed only if the expressions
    in the preceding ``if_()`` and ``elif_()`` statements evaluates to false and if the
    expression given in this ``elif_()`` evaluates to true.

    :param expression: A boolean expression to evaluate

    Example::

    >>> x=declare(int)
    >>> with if_(x>2):
    >>>     play('pulse', 'element')
    >>> with elif_(x>-2):
    >>>     play('other_pulse', 'element')
    >>> with else_():
    >>>     play('third_pulse', 'element')
    """
    body = _get_scope_as_blocks_body()
    last_statement = body.get_last_statement()
    if last_statement is None or last_statement.HasField("if") is False:
        raise Exception(
            "'elif' statement must directly follow 'if' statement - Please make sure it is aligned with the corresponding if statement."
        )
    ifstatement = getattr(last_statement, "if")
    if ifstatement.HasField("else") is True:
        raise Exception("'elif' must come before 'else' statement")
    elseifs = ifstatement.elseifs
    elseif = elseifs.add()
    elseif.loc = ifstatement.loc
    elseif.condition.CopyFrom(_unwrap_exp(expression))
    return _BodyScope(_StatementsCollection(elseif.body))


def else_():
    """
    Else flow control statement in QUA.

    To be used with a context manager.

    Must appear after an ``if_()`` statement.

    The QUA code block following the statement will be executed only if the expressions
    in the preceding ``if_()`` and ``elif_()`` statements evaluates to false.

    Example::

    >>> x=declare(int)
    >>> with if_(x>0):
    >>>     play('pulse', 'element')
    >>> with else_():
    >>>     play('other_pulse', 'element')
    """
    body = _get_scope_as_blocks_body()
    last_statement = body.get_last_statement()
    if last_statement is None or last_statement.HasField("if") is False:
        raise Exception(
            "'else' statement must directly follow 'if' statement - Please make sure it is aligned with the corresponding if statement."
        )
    ifstatement = getattr(last_statement, "if")
    if ifstatement.HasField("else") is True:
        raise Exception("only a single 'else' statement can follow an 'if' statement")
    elsestatement = getattr(ifstatement, "else")
    elsestatement.SetInParent()
    return _BodyScope(_StatementsCollection(elsestatement))


def _is_iter(x):
    try:
        iterator = iter(x)
    except TypeError:
        return False
    else:
        return True


def _collection_has_type(collection, type_to_check):
    for i in collection:
        if type(i) in (type_to_check,):
            return True
    return False


def for_each_(var, values):
    """
    Flow control: Iterate over array elements in QUA.

    It is possible to either loop over one variable, or over a tuple of variables,
    similar to the `zip` style iteration in python.

    To be used with a context manager.

    :param var: The iteration variable
    :type var: Union[QUA variable, tuple of QUA variables]
    :param values: A list of values to iterate over or a QUA array.
    :type values: Union[list of literals, tuple of lists of literals, QUA array, tuple of QUA arrays]

    Example::

    >>> x=declare(fixed)
    >>> y=declare(fixed)
    >>> with for_each_(x, [0.1, 0.4, 0.6]):
    >>>     play('pulse' * amp(x), 'element')
    >>> with for_each_((x, y), ([0.1, 0.4, 0.6], [0.3, -0.2, 0.1])):
    >>>     play('pulse1' * amp(x), 'element')
    >>>     play('pulse2' * amp(y), 'element')

    .. warning::

        This behaviour is not exactly consistent with python `zip`.
        Instead of sending a list of tuple as values, the function expects a tuple of
        lists.
        The first list containing the values for the first variable, and so on.

    """
    body = _get_scope_as_blocks_body()
    # normalize the var argument
    if not _is_iter(var) or type(var) is _Expression:
        var = (var,)

    for (i, v) in enumerate(var):
        if type(v) is not _Expression:
            raise Exception("for_each_ var " + i + " must be a variable")

    # normalize the values argument
    if (
        isinstance(values, _Expression)
        or not _is_iter(values)
        or not _is_iter(values[0])
    ):
        values = (values,)

    if _is_iter(values) and len(values) < 1:
        raise Exception("values cannot be empty")

    arrays = []
    for value in values:
        if isinstance(value, _Expression):
            arrays.append(value)
        elif _is_iter(value):
            has_bool = _collection_has_type(value, bool)
            has_int = _collection_has_type(value, int)
            has_float = _collection_has_type(value, float)

            if has_bool:
                if has_int or has_float:
                    raise Exception(
                        "values can not contain both bool and number values"
                    )
                # Only booleans
                arrays.append(declare(bool, value=value))
            else:
                if has_float:
                    # All will be considered as fixed
                    arrays.append(declare(fixed, value=[float(x) for x in value]))
                else:
                    # Only ints
                    arrays.append(declare(int, value=value))
        else:
            raise Exception("value is not a QUA array neither iterable")

    var = [_unwrap_var(exp(v)) for v in var]
    arrays = [a.unwrap() for a in arrays]

    if len(var) != len(arrays):
        raise Exception("number of variables does not match number of array values")

    iterators = [(var[i], ar) for (i, ar) in enumerate(arrays)]

    foreach = body.for_each(iterators)
    return _BodyScope(foreach)


def while_(cond=None):
    """
    While loop flow control statement in QUA.

    To be used with a context manager.

    :param cond: an expression which evaluates to a boolean variable, determines if to continue to next loop iteration
    :type cond: QUA expression

    Example::

    >>> x = declare(fixed)
    >>> assign(x, 0)
    >>> with while_(x<=30):
    >>>     play('pulse', 'element')
    >>>     assign(x, x+1)
    """
    return for_(None, None, cond, None)


def for_(var=None, init=None, cond=None, update=None):
    """
    For loop flow control statement in QUA.

    To be used with a context manager.

    :param var: QUA variable used as iteration variable
    :type var: QUA variable
    :param init: an expression which sets the initial value of the iteration variable
    :type init: QUA expression
    :param cond: an expression which evaluates to a boolean variable, determines if to continue to next loop iteration
    :type cond: QUA expression
    :param update: an expression to add to ``var`` with each loop iteration
    :type update: QUA expression

    Example::

    >>> x = declare(fixed)
    >>> with for_(var=x, init=0, cond=x<=1, update=x+0.1):
    >>>     play('pulse', 'element')
    """
    if var is None and init is None and cond is None and update is None:
        body = _get_scope_as_blocks_body()
        for_statement = body.for_block()
        return _ForScope(for_statement)
    else:
        body = _get_scope_as_blocks_body()
        for_statement = body.for_block()
        if var is not None and init is not None:
            _StatementsCollection(for_statement.init).assign(
                _unwrap_assign_target(exp(var)), _unwrap_exp(exp(init))
            )
        if var is not None and update is not None:
            _StatementsCollection(for_statement.update).assign(
                _unwrap_assign_target(exp(var)), _unwrap_exp(exp(update))
            )
        if cond is not None:
            for_statement.condition.CopyFrom(_unwrap_exp(exp(cond)))
        return _BodyScope(_StatementsCollection(for_statement.body))


def infinite_loop_():
    """
    Infinite loop flow control statement in QUA.

    To be used with a context manager.

    Optimized for zero latency between iterations,
    provided that no more than a single quantum element appears in the loop.

    .. note::
        In case multiple quantum elements need to be used in an infinite loop, it is possible to add several loops
        in parallel (see example).
        Two infinite loops cannot share a quantum element nor can they share variables.

    Example::

    >>> with infinite_loop_():
    >>>     play('pulse1', 'element1')
    >>> with infinite_loop_():
    >>>     play('pulse2', 'element2')
    """
    body = _get_scope_as_blocks_body()
    for_statement = body.for_block()
    for_statement.condition.CopyFrom(_unwrap_exp(exp(True)))
    return _BodyScope(_StatementsCollection(for_statement.body))


def for_init_():
    for_statement = _get_scope_as_for()
    return _BodyScope(_StatementsCollection(for_statement.init))


def for_update_():
    for_statement = _get_scope_as_for()
    return _BodyScope(_StatementsCollection(for_statement.update))


def for_body_():
    for_statement = _get_scope_as_for()
    return _BodyScope(_StatementsCollection(for_statement.body))


def for_cond(_exp):
    for_statement = _get_scope_as_for()
    for_statement.condition.CopyFrom(_unwrap_exp(exp(_exp)))


IO1 = object()
IO2 = object()


def L(value):
    """
    Creates an expression with a literal value

    :param value: int, float or bool to wrap in a literal expression
    """
    if type(value) is bool:
        return _exp.literal_bool(value)
    elif type(value) is int:
        return _exp.literal_int(value)
    elif type(value) is float:
        return _exp.literal_real(value)
    else:
        raise Exception("literal can be bool, int or float")


class fixed(object):
    pass


class DeclarationType(_Enum):
    EmptyScalar = 0
    InitScalar = 1
    EmptyArray = 2
    InitArray = 3


def _declare(t, is_input_stream, **kwargs):
    size = kwargs.get("size", None)
    value = kwargs.get("value", None)

    dim = 0
    if size is not None:
        if not (isinstance(size, int) and size > 0):
            raise ValueError("size must be a positive integer")
        if value is not None:
            raise ValueError("size declaration cannot be made if value is declared")
        dec_type = DeclarationType.EmptyArray
    else:
        if value is None:
            dec_type = DeclarationType.EmptyScalar
        elif isinstance(value, Iterable):
            dec_type = DeclarationType.InitArray
        else:
            dec_type = DeclarationType.InitScalar

    if dec_type == DeclarationType.InitArray:
        memsize = len(value)
        new_value = []
        for val in value:
            new_value.append(_to_expression(val).literal)
        value = new_value
        dim = 1
    elif dec_type == DeclarationType.InitScalar:
        memsize = 1
        value = _to_expression(value).literal
        dim = 0
    elif dec_type == DeclarationType.EmptyArray:
        memsize = size
        dim = 1
    else:
        memsize = 1
        dim = 0

    scope = _get_root_program_scope()

    if dec_type == DeclarationType.EmptyArray or dec_type == DeclarationType.InitArray:
        scope.array_index += 1
        var = "a" + str(scope.array_index)
        result = _Q.ArrayVarRefExpression()
        result.name = var
    else:
        scope.var_index += 1
        var = "v" + str(scope.var_index)
        result = _Q.AnyScalarExpression()
        result.variable.name = var

    prog = scope.program()
    if t == int:
        prog.declare_int(var, memsize, value, dim, is_input_stream)
    elif t == bool:
        prog.declare_bool(var, memsize, value, dim, is_input_stream)
    elif t == float:
        prog.declare_real(var, memsize, value, dim, is_input_stream)
    elif t == fixed:
        prog.declare_real(var, memsize, value, dim, is_input_stream)
    else:
        raise Exception("only int, float, bool or seed variables are supported")

    return _Expression(result)


def declare(t, **kwargs):
    r"""
    Declare a single QUA variable or QUA vector to be used in subsequent expressions and assignments.

    Declaration is performed by declaring a python variable with the return value of this function.

    :param t:
        The type of QUA variable. Possible values: ``int``, ``fixed``, ``bool``, where:

        ``int``
            a signed 32-bit number
        ``fixed``
            a signed 4.28 fixed point number
        ``bool``
            either ``True`` or ``False``
    :key value: An initial value for the variable or a list of initial values for a vector
    :key size:
        If declaring a vector without explicitly specifying a value, this parameter is used to specify the length
        of the array

    :return: The variable or vector

    .. warning::

        some QUA statements accept a variable with a valid range smaller than the full size of the generic
        QUA variable. For example, ``wait()`` accepts numbers between 4 and 2\ :sup:`24`.
        In case the value stored in the variable is larger than the valid input range, unexpected results
        may occur.

    Example::

    >>> a = declare(fixed, value=0.3)
    >>> play('pulse' * amp(a), 'element')
    >>>
    >>> array1 = declare(int, value=[1, 2, 3])
    >>> array2 = declare(fixed, size=5)

    """
    return _declare(t, is_input_stream=False, **kwargs)


def declare_input_stream(t, **kwargs):
    """
    Declare a single QUA variable or QUA vector to be used as an input stream from the job to the QUA program.

    Declaration is performed by declaring a python variable with the return value of this function.

    Declaration is identical to the declare() statement.

    -- Available from QOP 2.20 --

    """
    return _declare(t, is_input_stream=True, **kwargs)


def advance_input_stream(input_stream):
    """
    advances the input stream pointer to the next variable/vector.

    The variable/vector can then be used as a normal QUA variable.

    -- Available from QOP 2.20 --

    """

    body = _get_scope_as_blocks_body()
    body.advance_input_stream(_unwrap_exp(input_stream))


def declare_stream(**kwargs):
    """
    Declare a QUA output stream to be used in subsequent statements
    To retrieve the result - it must be saved in the stream processing block.

    Declaration is performed by declaring a python variable with the return value of this function.

    .. note::
        if the stream is an ADC trace, declaring it with the syntax ``declare_stream(adc_trace=True)``
        will add a buffer of length corresponding to the pulse length.

    :return: A :class:`_ResultSource` object to be used in :func:`stream_processing`

    Example::

    >>> a = declare_stream()
    >>> measure('pulse', 'element', a)
    >>>
    >>> with stream_processing():
    >>>     a.save("tag")
    >>>     a.save_all("another tag")
    """
    is_adc_trace = kwargs.get("adc_trace", False)

    scope = _get_root_program_scope()
    scope.result_index += 1
    var = "r" + str(scope.result_index)
    if is_adc_trace:
        var = "atr_" + var

    return _ResultSource(
        _ResultSourceConfiguration(
            var_name=var,
            timestamp_mode=_ResultSourceTimestampMode.Values,
            is_adc_trace=is_adc_trace,
            input=-1,
            auto_reshape=False,
        )
    )


def _to_expression(other, index_exp=None):
    other = _fix_object_data_type(other)
    if index_exp is not None and type(index_exp) is not _Q.AnyScalarExpression:
        index_exp = _to_expression(index_exp, None)

    if index_exp is not None and type(other) is not _Q.ArrayVarRefExpression:
        raise Exception(str(other) + " is not an array")

    if type(other) is _Expression:
        return other.unwrap()
    if type(other) is _Q.VarRefExpression:
        return other
    if type(other) is _Q.ArrayVarRefExpression:
        return _exp.array(other, index_exp)
    elif type(other) is int:
        return _exp.literal_int(other)
    elif type(other) is bool:
        return _exp.literal_bool(other)
    elif type(other) is float:
        return _exp.literal_real(other)
    elif other == IO1:
        return _exp.io1()
    elif other == IO2:
        return _exp.io2()
    else:
        raise Exception("Can't handle " + str(other))


class _Expression(object):
    def __init__(self, exp):
        self._exp = exp

    def __getitem__(self, item):
        return _Expression(_to_expression(self._exp, item))

    def unwrap(self):
        return self._exp

    def empty(self):
        return self._exp is None

    def length(self):
        unwrapped_element = self.unwrap()
        if type(unwrapped_element) is _Q.ArrayVarRefExpression:
            array_exp = _Q.ArrayLengthExpression()
            array_exp.array.CopyFrom(unwrapped_element)
            result = _Q.AnyScalarExpression()
            result.arrayLength.CopyFrom(array_exp)
            return _Expression(result)
        else:
            raise Exception(str(unwrapped_element) + " is not an array")

    def __add__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, "+", other))

    def __radd__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(other, "+", self._exp))

    def __sub__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, "-", other))

    def __rsub__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(other, "-", self._exp))

    def __neg__(self):
        other = _to_expression(0)
        return _Expression(_exp.binary(other, "-", self._exp))

    def __gt__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, ">", other))

    def __ge__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, ">=", other))

    def __lt__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, "<", other))

    def __le__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, "<=", other))

    def __eq__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, "==", other))

    def __mul__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, "*", other))

    def __rmul__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(other, "*", self._exp))

    def __truediv__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, "/", other))

    def __rtruediv__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(other, "/", self._exp))

    def __lshift__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, "<<", other))

    def __rlshift__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(other, "<<", self._exp))

    def __rshift__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, ">>", other))

    def __rrshift__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(other, ">>", self._exp))

    def __and__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, "&", other))

    def __rand__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(other, "&", self._exp))

    def __or__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, "|", other))

    def __ror__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(other, "|", self._exp))

    def __xor__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(self._exp, "^", other))

    def __rxor__(self, other):
        other = _to_expression(other)
        return _Expression(_exp.binary(other, "^", self._exp))

    def __invert__(self):
        other = _to_expression(True)
        return _Expression(_exp.binary(self._exp, "^", other))

    def __str__(self) -> str:
        return ExpressionSerializingVisitor.serialize(self._exp)

    def __bool__(self):
        raise Exception(
            """Attempted to use a Python logical operator in a QUA
         expression, please use QUA operators: '~' for 'not', '|' for 'or', '&' for
         'and', and `^` for `xor`."""
        )


class _PulseAmp(object):
    def __init__(self, v1, v2, v3, v4):
        super(_PulseAmp, self).__init__()
        if v1 is None:
            raise Exception("amp can be one value or a matrix of 4")
        if v2 is None and v3 is None and v4 is None:
            pass
        elif v2 is not None and v3 is not None and v4 is not None:
            pass
        else:
            raise Exception("amp can be one value or a matrix of 4.")

        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.v4 = v4

    def value(self):
        return self.v1, self.v2, self.v3, self.v4

    def __rmul__(self, other):
        if type(other) is not str:
            raise Exception("you can multiply only a pulse")
        return other, self.value()

    def __mul__(self, other):
        if type(other) is not str:
            raise Exception("you can multiply only a pulse")
        return other, self.value()


def amp(v1, v2=None, v3=None, v4=None):
    vars = [_unwrap_exp(exp(v)) if v is not None else None for v in [v1, v2, v3, v4]]
    return _PulseAmp(*vars)


def _assert_scalar_expression(value):
    if type(_unwrap_exp(value)) is not _Q.AnyScalarExpression:
        raise TypeError(
            "invalid expression: '" + str(value) + "' is not a scalar expression"
        )


def _assert_not_lib_expression(value):
    exp = _unwrap_exp(value)
    if (
        type(exp) is _Q.AnyScalarExpression
        and exp.WhichOneof("expression_oneof") == "libFunction"
    ):
        raise TypeError(
            f"library expression {str(value)} is not a valid save source."
            f" Assign the value to a variable before saving it"
        )


def ramp(v):
    result = _Q.RampPulse()
    value = _unwrap_exp(exp(v))
    _assert_scalar_expression(exp(v))
    result.value.CopyFrom(value)
    return result


def exp(value):
    return _Expression(_to_expression(value))


def _exp_or_none(value):
    if value is None:
        return None
    return exp(value)


class _BaseScope(object):
    def __init__(self):
        super(_BaseScope, self).__init__()

    def __enter__(self):
        global _block_stack
        _block_stack.append(self)
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _block_stack
        if _block_stack[-1] != self:
            raise Exception("Unexpected stack structure")
        _block_stack.remove(self)
        return False


class _BodyScope(_BaseScope):
    def __init__(self, body):
        super(_BodyScope, self).__init__()
        self._body = body

    def body(self):
        return self._body


class _ProgramScope(_BodyScope):
    def __init__(self, program: _Program):
        super().__init__(program.body)
        self._program = program
        self.var_index = 0
        self.array_index = 0
        self.result_index = 0
        self._declared_streams = {}

    def __enter__(self):
        super().__enter__()
        self._program.set_in_scope()
        return self._program

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._program.result_analysis.generate_proto()
        self._program.set_exit_scope()
        return super().__exit__(exc_type, exc_val, exc_tb)

    def program(self):
        return self._program

    def declare_legacy_adc(self, tag: str) -> "_ResultSource":
        result_object = self._declared_streams.get(tag, None)
        if result_object is None:
            result_object = declare_stream(adc_trace=True)
            self._declared_streams[tag] = result_object

            ra = _get_scope_as_result_analysis()
            ra.auto_save_all(tag + "_input1", result_object.input1())
            ra.auto_save_all(
                tag + "_input1" + _TIMESTAMPS_LEGACY_SUFFIX,
                result_object.input1().timestamps(),
            )
            ra.auto_save_all(tag + "_input2", result_object.input2())
            ra.auto_save_all(
                tag + "_input2" + _TIMESTAMPS_LEGACY_SUFFIX,
                result_object.input2().timestamps(),
            )

        return result_object

    def declare_legacy_save(self, tag: str) -> "_ResultSource":
        result_object = self._declared_streams.get(tag, None)
        if result_object is None:
            result_object = declare_stream()
            self._declared_streams[tag] = result_object
            result_object.save_all(tag)
            result_object.timestamps().save_all(tag + _TIMESTAMPS_LEGACY_SUFFIX)
        return result_object


class _ForScope(_BodyScope):
    def __init__(self, forst):
        super(_ForScope, self).__init__(None)
        self._forst = forst

    def body(self):
        raise Exception(
            "for must be used with for_init, for_update, for_body and for_cond"
        )

    def for_statement(self):
        return self._forst


class _SwitchScope(_BaseScope):
    def __init__(self, expression: _Expression, container, unsafe):
        super().__init__()
        self.expression = expression
        self.if_statement = None
        self.container = container
        self.unsafe = unsafe


def qrun_():
    """
    QRun statement in QUA.
    """

    body = _get_scope_as_blocks_body()
    qrun_statement = body.qrun_block()
    return _BodyScope(_StatementsCollection(qrun_statement.body))


class _RAScope(_BaseScope):
    def __init__(self, ra: _ResultAnalysis):
        super().__init__()
        self._ra = ra

    def __enter__(self):
        super().__enter__()
        return self._ra

    def result_analysis(self):
        return self._ra


def _get_root_program_scope() -> _ProgramScope:
    global _block_stack
    if type(_block_stack[0]) != _ProgramScope:
        raise Exception("Expecting program scope")
    return _block_stack[0]


def _get_scope_as_program() -> _Program:
    global _block_stack
    if type(_block_stack[-1]) != _ProgramScope:
        raise Exception("Expecting program scope")
    return _block_stack[-1].program()


def _get_scope_as_for() -> _ForScope:
    global _block_stack
    if type(_block_stack[-1]) != _ForScope:
        raise Exception("Expecting for scope")
    return _block_stack[-1].for_statement()


def _get_scope_as_blocks_body():
    global _block_stack
    if not issubclass(type(_block_stack[-1]), _BodyScope):
        raise Exception("Expecting scope with body.")
    return _block_stack[-1].body()


def _get_scope_as_switch_scope() -> _SwitchScope:
    global _block_stack
    if type(_block_stack[-1]) != _SwitchScope:
        raise Exception("Expecting switch scope")
    return _block_stack[-1]


def _get_scope_as_result_analysis() -> _ResultAnalysis:
    global _block_stack
    return _get_root_program_scope().program().result_analysis


def _unwrap_exp(exp):
    if type(exp) is not _Expression:
        raise Exception("invalid expression: " + str(exp))
    return exp.unwrap()


def _unwrap_var(exp):
    var = _unwrap_exp(exp)
    if type(var) is not _Q.AnyScalarExpression:
        raise Exception("invalid expression: " + str(exp))
    return var.variable


def _unwrap_array_cell(exp):
    var = _unwrap_exp(exp)
    if type(var) is not _Q.AnyScalarExpression:
        raise Exception("invalid expression: " + str(exp))
    return var.arrayCell


def _unwrap_assign_target(exp):
    result = _Q.AssignmentStatement.Target()

    target = _unwrap_exp(exp)
    if type(target) is _Q.AnyScalarExpression:
        one_of = target.WhichOneof("expression_oneof")
        if one_of == "arrayCell":
            result.arrayCell.CopyFrom(target.arrayCell)
        elif one_of == "variable":
            result.variable.CopyFrom(target.variable)
        else:
            raise Exception("invalid target expression: " + str(exp))
    # We don't support whole array assignment for now
    # elif type(target) is _Q.ArrayVarRefExpression:
    #     result.arrayVar.CopyFrom(target.arrayVar)
    else:
        raise Exception("invalid target expression: " + str(exp))

    return result


def _unwrap_save_source(exp):
    result = _Q.SaveStatement.Source()

    source = _unwrap_exp(exp)
    _assert_scalar_expression(exp)
    _assert_not_lib_expression(exp)
    one_of = source.WhichOneof("expression_oneof")
    if one_of == "arrayCell":
        result.arrayCell.CopyFrom(source.arrayCell)
    elif one_of == "variable":
        result.variable.CopyFrom(source.variable)
    elif one_of == "literal":
        result.literal.CopyFrom(source.literal)
    else:
        raise Exception("invalid source expression: " + str(exp))

    return result


def _unwrap_outer_target(analog_process_target):
    outer_target = _Q.AnalogProcessTarget()
    if type(analog_process_target) == AnalogMeasureProcess.ScalarProcessTarget:
        target = _Q.AnalogProcessTarget.ScalarProcessTarget()
        target_exp = _unwrap_exp(analog_process_target.target)
        if type(target_exp) is not _Q.AnyScalarExpression:
            raise Exception()
        target_type = target_exp.WhichOneof("expression_oneof")
        if target_type == "variable":
            target.variable.CopyFrom(target_exp.variable)
        elif target_type == "arrayCell":
            target.arrayCell.CopyFrom(target_exp.arrayCell)
        else:
            raise Exception()
        outer_target.scalarProcess.CopyFrom(target)
    elif type(analog_process_target) == AnalogMeasureProcess.VectorProcessTarget:
        target = _Q.AnalogProcessTarget.VectorProcessTarget()
        target.array.CopyFrom(_unwrap_exp(analog_process_target.target))
        target.timeDivision.CopyFrom(
            _unwrap_time_division(analog_process_target.time_division)
        )
        outer_target.vectorProcess.CopyFrom(target)
    else:
        raise Exception()
    return outer_target


def _unwrap_analog_process(analog_process):
    result = _Q.AnalogMeasureProcess()
    result.loc = analog_process.loc

    if type(analog_process) == AnalogMeasureProcess.BareIntegration:
        result.bareIntegration.integration.name = analog_process.iw
        result.bareIntegration.elementOutput = analog_process.element_output
        result.bareIntegration.target.CopyFrom(
            _unwrap_outer_target(analog_process.target)
        )
    elif type(analog_process) == AnalogMeasureProcess.DualBareIntegration:
        result.dualBareIntegration.integration1.name = analog_process.iw1
        result.dualBareIntegration.integration2.name = analog_process.iw2
        result.dualBareIntegration.elementOutput1 = analog_process.element_output1
        result.dualBareIntegration.elementOutput2 = analog_process.element_output2
        result.dualBareIntegration.target.CopyFrom(
            _unwrap_outer_target(analog_process.target)
        )
    elif type(analog_process) == AnalogMeasureProcess.DemodIntegration:
        result.demodIntegration.integration.name = analog_process.iw
        result.demodIntegration.elementOutput = analog_process.element_output
        result.demodIntegration.target.CopyFrom(
            _unwrap_outer_target(analog_process.target)
        )
    elif type(analog_process) == AnalogMeasureProcess.DualDemodIntegration:
        result.dualDemodIntegration.integration1.name = analog_process.iw1
        result.dualDemodIntegration.integration2.name = analog_process.iw2
        result.dualDemodIntegration.elementOutput1 = analog_process.element_output1
        result.dualDemodIntegration.elementOutput2 = analog_process.element_output2
        result.dualDemodIntegration.target.CopyFrom(
            _unwrap_outer_target(analog_process.target)
        )
    elif type(analog_process) == AnalogMeasureProcess.RawTimeTagging:
        result.rawTimeTagging.target.CopyFrom(_unwrap_exp(analog_process.target))
        result.rawTimeTagging.elementOutput = analog_process.element_output
        result.rawTimeTagging.maxTime = int(analog_process.max_time)
        if analog_process.targetLen is not None:
            result.rawTimeTagging.targetLen.CopyFrom(
                _unwrap_exp(analog_process.targetLen).variable
            )

    return result


def _unwrap_digital_process(digital_process):
    result = _Q.DigitalMeasureProcess()
    result.loc = digital_process.loc

    if type(digital_process) == DigitalMeasureProcess.RawTimeTagging:
        result.rawTimeTagging.target.CopyFrom(_unwrap_exp(digital_process.target))
        if digital_process.targetLen is not None:
            result.rawTimeTagging.targetLen.CopyFrom(
                _unwrap_exp(digital_process.targetLen).variable
            )
        result.rawTimeTagging.maxTime = int(digital_process.max_time)
        result.rawTimeTagging.elementOutput = digital_process.element_output
    elif type(digital_process) == DigitalMeasureProcess.Counting:
        result.counting.target.CopyFrom(_unwrap_exp(digital_process.target).variable)
        result.counting.maxTime = int(digital_process.max_time)
        if type(digital_process.element_outputs) == tuple:
            result.counting.elementOutputs.extend(digital_process.element_outputs)
        elif type(digital_process.element_outputs) == str:
            result.counting.elementOutputs.append(digital_process.element_outputs)

    return result


def _unwrap_measure_process(process):
    result = _Q.MeasureProcess()

    if isinstance(process, AnalogMeasureProcess.AnalogMeasureProcess):
        result.analog.CopyFrom(_unwrap_analog_process(process))
    elif isinstance(process, DigitalMeasureProcess.DigitalMeasureProcess):
        result.digital.CopyFrom(_unwrap_digital_process(process))

    return result


def _unwrap_time_division(time_division):
    result = _Q.AnalogProcessTarget.TimeDivision()

    if type(time_division) == AnalogMeasureProcess.SlicedAnalogTimeDivision:
        result.sliced.samplesPerChunk = time_division.samples_per_chunk
    elif type(time_division) == AnalogMeasureProcess.AccumulatedAnalogTimeDivision:
        result.accumulated.samplesPerChunk = time_division.samples_per_chunk
    elif type(time_division) == AnalogMeasureProcess.MovingWindowAnalogTimeDivision:
        result.movingWindow.samplesPerChunk = time_division.samples_per_chunk
        result.movingWindow.chunksPerWindow = time_division.chunks_per_window

    return result


class AccumulationMethod:
    def __init__(self):
        self.loc = ""
        self.return_func = None

    def _full_target(self, target):
        return AnalogMeasureProcess.ScalarProcessTarget(self.loc, target)

    def _sliced_target(self, target, samples_per_chunk: int):
        analog_time_division = AnalogMeasureProcess.SlicedAnalogTimeDivision(
            self.loc, samples_per_chunk
        )
        return AnalogMeasureProcess.VectorProcessTarget(
            self.loc, target, analog_time_division
        )

    def _accumulated_target(self, target, samples_per_chunk: int):
        analog_time_division = AnalogMeasureProcess.AccumulatedAnalogTimeDivision(
            self.loc, samples_per_chunk
        )
        return AnalogMeasureProcess.VectorProcessTarget(
            self.loc, target, analog_time_division
        )

    def _moving_window_target(
        self, target, samples_per_chunk: int, chunks_per_window: int
    ):
        analog_time_division = AnalogMeasureProcess.MovingWindowAnalogTimeDivision(
            self.loc, samples_per_chunk, chunks_per_window
        )
        return AnalogMeasureProcess.VectorProcessTarget(
            self.loc, target, analog_time_division
        )


class RealAccumulationMethod(AccumulationMethod):
    """
    A base class for specifying accumulation method in ``measure`` statement. Not to be instantiated.
    """

    def __init__(self):
        super().__init__()

    def __new__(cls):
        if cls is AccumulationMethod:
            raise TypeError("base class may not be instantiated")
        return object.__new__(cls)

    def full(self, iw, target, element_output=""):
        """
        Perform an ordinary demodulation/integration. See :ref:`Guides/features:Full demodulation`.

        :param iw: integration weights
        :type iw: str
        :param target: variable to which demod result is saved
        :type target: QUA variable
        :param element_output: (optional) the output of a quantum element from which to get ADC results
        """
        return self.return_func(self.loc, element_output, iw, self._full_target(target))

    def sliced(self, iw, target, samples_per_chunk: int, element_output=""):
        """
        Perform a demodulation/integration in which the demodulation/integration process is split into chunks
        and the value of each chunk is saved in an array cell. See :ref:`Guides/features:Sliced demodulation`.

        :param iw: integration weights
        :type iw: str
        :param target: variable to which demod result is saved
        :type target: QUA array
        :param samples_per_chunk:
            The number of ADC samples to be used for each chunk is this number times 4.
            Minimal value: 7
        :type samples_per_chunk: int
        :param element_output: (optional) the output of a quantum element from which to get ADC results
        """
        return self.return_func(
            self.loc, element_output, iw, self._sliced_target(target, samples_per_chunk)
        )

    def accumulated(self, iw, target, samples_per_chunk: int, element_output=""):
        """
        Same as ``sliced()``, however the accumulated result of the demodulation/integration
        is saved in each array cell. See :ref:`Guides/features:Accumulated demodulation`.

        :param iw: integration weights
        :type iw: str
        :param target: variable to which demod result is saved
        :type target: QUA array
        :param samples_per_chunk:
            The number of ADC samples to be used for each chunk is this number times 4.
            Minimal value: 7
        :type samples_per_chunk: int
        :param element_output: (optional) the output of a quantum element from which to get ADC results
        """
        return self.return_func(
            self.loc,
            element_output,
            iw,
            self._accumulated_target(target, samples_per_chunk),
        )

    def moving_window(
        self,
        iw,
        target,
        samples_per_chunk: int,
        chunks_per_window: int,
        element_output="",
    ):
        """
        Same as ``sliced()``, however the several chunks are accumulated and saved to each array cell.
        See :ref:`Guides/features:Accumulated demodulation`.

        :param iw: integration weights
        :type iw: str
        :param target: variable to which demod result is saved
        :type target: QUA array
        :param samples_per_chunk:
            The number of ADC samples to be used for each chunk is this number times 4.
            Minimal value: 7
        :type samples_per_chunk: int
        :param chunks_per_window: The number of chunks to use in the moving window
        :type chunks_per_window: int
        :param element_output: (optional) the output of a quantum element from which to get ADC results
        """
        return self.return_func(
            self.loc,
            element_output,
            iw,
            self._moving_window_target(target, samples_per_chunk, chunks_per_window),
        )


class DualAccumulationMethod(AccumulationMethod):
    """
    A base class for specifying accumulation method in ``measure`` statement. Not to be instantiated.
    """

    def __init__(self):
        super().__init__()

    def __new__(cls):
        if cls is AccumulationMethod:
            raise TypeError("base class may not be instantiated")
        return object.__new__(cls)

    def full(self, iw1, element_output1, iw2, element_output2, target):
        """
        Perform an ordinary dual demodulation/integration. See :ref:`Guides/demod:Dual demodulation`.

        :param iw1: integration weights to be applied to element_output1
        :type iw1: str
        :param element_output1: the output of a quantum element from which to get ADC results
        :type element_output1: str
        :param iw2: integration weights to be applied to element_output2
        :type iw2: str
        :param element_output2: the output of a quantum element from which to get ADC results
        :type element_output2: str
        :param target: variable to which demod result is saved
        :type target: QUA variable

        """
        return self.return_func(
            self.loc,
            element_output1,
            element_output2,
            iw1,
            iw2,
            self._full_target(target),
        )

    def sliced(
        self, iw1, element_output1, iw2, element_output2, samples_per_chunk, target
    ):
        """
        This feature is currently not supported in QUA
        """

        return self.return_func(
            self.loc,
            element_output1,
            element_output2,
            iw1,
            iw2,
            self._sliced_target(target, samples_per_chunk),
        )

    def accumulated(
        self, iw1, element_output1, iw2, element_output2, samples_per_chunk, target
    ):
        """
        This feature is currently not supported in QUA
        """

        return self.return_func(
            self.loc,
            element_output1,
            element_output2,
            iw1,
            iw2,
            self._accumulated_target(target, samples_per_chunk),
        )

    def moving_window(
        self,
        iw1,
        element_output1,
        iw2,
        element_output2,
        samples_per_chunk: int,
        chunks_per_window: int,
        target,
    ):
        """
        This feature is currently not supported in QUA
        """
        return self.return_func(
            self.loc,
            element_output1,
            element_output2,
            iw1,
            iw2,
            self._moving_window_target(target, samples_per_chunk, chunks_per_window),
        )


class _Demod(RealAccumulationMethod):
    def __init__(self):
        super().__init__()
        self.loc = ""
        self.return_func = AnalogMeasureProcess.DemodIntegration


class _BareIntegration(RealAccumulationMethod):
    def __init__(self):
        super().__init__()
        self.loc = ""
        self.return_func = AnalogMeasureProcess.BareIntegration


class _DualDemod(DualAccumulationMethod):
    def __init__(self):
        super().__init__()
        self.loc = ""
        self.return_func = AnalogMeasureProcess.DualDemodIntegration


class _DualBareIntegration(DualAccumulationMethod):
    def __init__(self):
        super().__init__()
        self.loc = ""
        self.return_func = AnalogMeasureProcess.DualBareIntegration


class _TimeTagging:
    def __init__(self):
        self.loc = ""

    @deprecated("use time_tagging.analog instead", "0.8", "0.9")
    def raw(self, target, max_time, targetLen=None, element_output=""):
        return self.analog(target, max_time, targetLen, element_output)

    def analog(self, target, max_time, targetLen=None, element_output=""):
        return AnalogMeasureProcess.RawTimeTagging(
            self.loc, element_output, target, targetLen, max_time
        )


class _Counting:
    def __init__(self):
        self.loc = ""

    def digital(self, target, max_time, element_outputs=""):
        return DigitalMeasureProcess.Counting(
            self.loc, element_outputs, target, max_time
        )


demod = _Demod()
dual_demod = _DualDemod()
integration = _BareIntegration()
dual_integration = _DualBareIntegration()
time_tagging = _TimeTagging()
counting = _Counting()


def stream_processing():
    """
    A context manager for the creation of :ref:`Guides/stream_proc:Stream Processing` pipelines.

    Each pipeline defines an analysis process that is applied to every stream item.
    A pipeline must be terminated with a save/save_all terminal, and then can be retrieved with
    :attr:`QmJob.result_handles<qm.QmJob.QmJob.result_handles>`.

    There are two save options: ``save_all`` will save every stream item, ``save`` will save only last item.

    A pipeline can be assigned to python variable, and then reused on other pipelines. It is ensured that the
    common part of the pipeline is processed only once.

    Example of creating a results analysis::

        with stream_processing():
            a.save("tag")
            a.save_all("another tag")

    Example of retrieving saved result::

        QmJob.result_handles.get("tag")

    """
    prog = _get_scope_as_program()
    return _RAScope(prog.result_analysis)


class _Functions(object):
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def average(axis=None):
        """
        Perform a running average on a stream item. The Output of this operation is the
        running averageof the values in the stream starting from the beginning of the
        QUA program.

        :param axis: optional Axis or axes along which to average.
        :return: stream object
        """
        if axis is None:
            return ["average"]
        else:
            if hasattr(axis, "__len__"):
                # vector
                return [
                    "average",
                    ["@array"] + [str(item) for item in list(axis)],
                ]
            else:
                # scalar
                return ["average", str(axis)]

    @staticmethod
    def dot_product(vector):
        """
        Computes dot product of the given vector and an item of the input stream

        :param vector: constant vector of numbers
        :return: stream object
        """
        return ["dot", ["@array"] + [str(item) for item in list(vector)]]

    @staticmethod
    def tuple_dot_product():
        """
        Computes dot product between the two vectors of the input stream

        :return: stream object
        """
        return ["dot"]

    @staticmethod
    def multiply_by(scalar_or_vector):
        """
        Multiply the input stream item by a constant scalar or vector.
        the input item can be either scalar or vector.

        :param scalar_or_vector: either a scalar number, or a vector of scalars.
        :return: stream object
        """
        if hasattr(scalar_or_vector, "__len__"):
            # vector
            return [
                "vmult",
                ["@array"] + [str(item) for item in list(scalar_or_vector)],
            ]
        else:
            # scalar
            return ["smult", str(scalar_or_vector)]

    @staticmethod
    def tuple_multiply():
        """
        Computes multiplication between the two elements of the input stream.
        Can be any combination of scalar and vectors.

        :return: stream object
        """
        return ["tmult"]

    @staticmethod
    def convolution(constant_vector, mode=None):
        """
        Computes discrete, linear convolution of one-dimensional constant vector and
        one-dimensional vector item of the input stream.

        :param constant_vector: vector of numbers
        :param mode: "full", "same" or "valid"
        :return: stream object
        """
        if mode is None:
            mode = ""
        return [
            "conv",
            str(mode),
            ["@array"] + [str(item) for item in list(constant_vector)],
        ]

    @staticmethod
    def tuple_convolution(mode=None):
        """
        Computes discrete, linear convolution of two one-dimensional vectors of the
        input stream

        :param mode: "full", "same" or "valid"
        :return: stream object
        """
        if mode is None:
            mode = ""
        return ["conv", str(mode)]

    @staticmethod
    def fft(output=None):
        """
        Computes one-dimensional discrete fourier transform for every item in the
        stream.
        Item can be a vector of numbers, in this case fft will assume all imaginary
        numbers are 0.
        Item can also be a vector of number pairs - in this case for each pair - the
        first will be real and second imaginary.

        :param output:  supported from QOP 1.30 and QOP 2.20, options are "normal",
                        "abs" and "angle":

                        *   "normal" - Same as default (none), returns a 2d array of
                            size Nx2, where N is the length of the original vector.
                            The first item in each pair is the real part, and the 2nd
                            is the imaginary part.
                        *   "abs" - Returns a 1d array of size N with the abs of the fft.
                        *   "angle" - Returns the angle between the imaginary and real
                            parts in radians.
        :return: stream object
        """
        if output is None:
            return ["fft"]
        else:
            return ["fft", str(output)]

    @staticmethod
    def boolean_to_int():
        """
        Converts boolean to integer number - 1 for true and 0 for false

        :return: stream object
        """
        return ["booleancast"]

    @staticmethod
    def demod(frequency, iw_cos, iw_sin, *, integrate: Optional[bool] = None):
        """
        Demodulates the acquired data from the indicated stream at the given frequency
        and integration weights.
        If operating on a stream of tuples, assumes that the 2nd item is the timestamps
        and uses them for the demodulation, reproducing the demodulation performed
        in real time.
        If operated on a single stream, assumes that the first item is at time zero and
        that the elements are separated by 1ns.

        :param frequency: frequency for demodulation calculation
        :param iw_cos:  cosine integration weight. Integration weight can be either a
                        scalar for constant integration weight, or a python iterable for
                        arbitrary integration weights.
        :param iw_sin:  sine integration weight. Integration weight can be either a
                        scalar for constant integration weight, or a python iterable for
                        arbitrary integration weights.
        :param integrate: sum the demodulation result and returns a scalar if True (default),
                        else the demodulated stream without summation is returned
        :return: stream object

        Example::

        >>>     with stream_processing():
        >>>         adc_stream.input1().with_timestamps().map(FUNCTIONS.demod(freq, 1.0, 0.0, integrate=False)).average().save('cos_env')
        >>>         adc_stream.input1().with_timestamps().map(FUNCTIONS.demod(freq, 1.0, 0.0)).average().save('cos_result')  # Default is integrate=True


        """
        if hasattr(iw_cos, "__len__"):
            iw_cos = ["@array"] + [str(item) for item in list(iw_cos)]
        else:
            iw_cos = str(iw_cos)
        if hasattr(iw_sin, "__len__"):
            iw_sin = ["@array"] + [str(item) for item in list(iw_sin)]
        else:
            iw_sin = str(iw_sin)
        out = ["demod", str(frequency), iw_cos, iw_sin]
        if type(integrate) is bool:
            out.append("1" if integrate else "0")
        return out


FUNCTIONS = _Functions()


class _ResultStream:
    def __init__(self, input_stream, operator_array):
        super().__init__()
        if operator_array is not None:
            self._operator_array = [*operator_array]
            self._operator_array.append(input_stream)
        else:
            self._operator_array = input_stream

    def average(self) -> "_ResultStream":
        """
        Perform a running average on a stream item. The Output of this operation is the running average
        of the values in the stream starting from the beginning of the QUA program.
        """
        return _ResultStream(self, ["average"])

    def buffer(self, *args) -> "_ResultStream":
        """
        Gather items into vectors - creates an array of input stream items and outputs the array as one item.
        only outputs full buffers.

        :param length: number of items to gather
        """
        int_args = [str(int(arg)) for arg in args]
        return _ResultStream(self, ["buffer"] + int_args)

    def buffer_and_skip(self, length, skip) -> "_ResultStream":
        """
        Gather items into vectors - creates an array of input stream items and outputs
        the array as one item.
        Skips the number of given elements. Note that length and skip start from the
        same index, so the `buffer(n)` command is equivalent to `buffer_and_skip(n, n)`.

        Only outputs full buffers.

        Example::

        >>>     # The stream input is [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        >>>     with stream_processing():
        >>>         stream.buffer(3).save_all("example1")
        >>>         stream.buffer_and_skip(3, 3).save_all("example2")
        >>>         stream.buffer_and_skip(3, 2).save_all("example3")
        >>>         stream.buffer_and_skip(3, 5).save_all("example4")
        >>>    # example1 -> [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        >>>    # example2 -> [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        >>>    # example3 -> [[1, 2, 3], [3, 4, 5], [5, 6, 7], [7, 8, 9]]
        >>>    # example4 -> [[1, 2, 3], [6, 7, 8]]


        :param length: number of items to gather
        :param skip: number of items to skip for each buffer, starting from the same
                     index as length
        """
        return _ResultStream(self, ["bufferAndSkip", str(int(length)), str(int(skip))])

    def map(self, function) -> "_ResultStream":
        """
        Transform the item by applying a
        `function <https://qm-docs.qualang.io/api_references/qua/result_stream.html#qm.qua._dsl._Functions>`__ to it

        :param function: a function to transform each item to a different item.
                         For example, to compute an average between elements in a buffer
                         you should write ".buffer(len).map(FUNCTIONS.average())"
        """
        return _ResultStream(self, ["map", function])

    def flatten(self) -> "_ResultStream":
        """
        Deconstruct an array item - and send its elements one by one as items
        """
        return _ResultStream(self, ["flatten"])

    def skip(self, length) -> "_ResultStream":
        """
        Suppress the first n items of the stream

        :param length: number of items to skip
        """
        return _ResultStream(self, ["skip", str(int(length))])

    def skip_last(self, length) -> "_ResultStream":
        """
        Suppress the last n items of the stream

        :param length: number of items to skip
        """
        return _ResultStream(self, ["skipLast", str(int(length))])

    def take(self, length) -> "_ResultStream":
        """
        Outputs only the first n items of the stream

        :param length: number of items to take
        """
        return _ResultStream(self, ["take", str(int(length))])

    def histogram(self, bins) -> "_ResultStream":
        """
        Compute the histogram of all items in stream

        :param bins: vector or pairs. each pair indicates the edge of each bin.
            example: [[1,10],[11,20]] - two bins, one between 1 and 10, second between 11 and 20
        """
        converted_bins = []
        for sub_list in list(bins):
            converted_bins = converted_bins + [
                ["@array"] + [str(item) for item in list(sub_list)]
            ]
        return _ResultStream(self, ["histogram", ["@array"] + converted_bins])

    def zip(self, other) -> "_ResultStream":
        """
        Combine the emissions of two streams to one item that is a tuple of items of input streams

        :param other: second stream to combine with self
        """
        return _ResultStream(self, ["zip", other._to_proto()])

    def save_all(self, tag):
        """
        Save all items received in stream.
        This will add to :class:`~qm._results.JobResults` a :class:`~qm._results.SingleNamedJobResult` object.

        :param tag: result name
        """
        ra = _get_scope_as_result_analysis()
        ra.save_all(tag, self)

    def save(self, tag):
        """
        Save only the last item received in stream
        This will add to :class:`~qm._results.JobResults` a :class:`~qm._results.MultipleNamedJobResult` object.

        :param tag: result name
        """
        ra = _get_scope_as_result_analysis()
        ra.save(tag, self)

    def dot_product(self, vector) -> "_ResultStream":
        """
        Computes dot product of the given vector and each item of the input stream

        :param vector: constant vector of numbers
        """
        return self.map(FUNCTIONS.dot_product(vector))

    def tuple_dot_product(self) -> "_ResultStream":
        """
        Computes dot product of the given item of the input stream - that should include two vectors
        """
        return self.map(FUNCTIONS.tuple_dot_product())

    def multiply_by(self, scalar_or_vector) -> "_ResultStream":
        """
        Multiply the input stream item by a constant scalar or vector.
        The input item can be either scalar or vector.

        :param scalar_or_vector: either a scalar number, or a vector of scalars.
        """
        return self.map(FUNCTIONS.multiply_by(scalar_or_vector))

    def tuple_multiply(self) -> "_ResultStream":
        """
        Computes multiplication of the given item of the input stream - that can be any
        combination of scalar and vectors.
        """
        return self.map(FUNCTIONS.tuple_multiply())

    def convolution(self, constant_vector, mode=None) -> "_ResultStream":
        """
        Computes discrete, linear convolution of one-dimensional constant vector and one-dimensional vector
        item of the input stream.

        :param constant_vector: vector of numbers
        :param mode: "full", "same" or "valid"
        """
        return self.map(FUNCTIONS.convolution(constant_vector, mode))

    def tuple_convolution(self, mode=None) -> "_ResultStream":
        """
        Computes discrete, linear convolution of two one-dimensional vectors that received as the one item from the input stream

        :param mode: "full", "same" or "valid"
        """
        return self.map(FUNCTIONS.tuple_convolution(mode))

    def fft(self, output=None) -> "_ResultStream":
        """
        Computes one-dimensional discrete fourier transform for every item in the
        stream.
        Item can be a vector of numbers, in this case fft will assume all imaginary
        numbers are 0.
        Item can also be a vector of number pairs - in this case for each pair - the
        first will be real and second imaginary.

        :param output:  supported from QOP 1.30 and QOP 2.20, options are "normal",
                        "abs" and "angle":

                        *   "normal" - Same as default (none), returns a 2d array of
                            size Nx2, where N is the length of the original vector.
                            The first item in each pair is the real part, and the 2nd
                            is the imaginary part.
                        *   "abs" - Returns a 1d array of size N with the abs of the fft.
                        *   "angle" - Returns the angle between the imaginary and real
                            parts in radians.
        :return: stream object
        """
        return self.map(FUNCTIONS.fft(output))

    def boolean_to_int(self) -> "_ResultStream":
        """
        converts boolean to an integer number - 1 for true and 0 for false
        """
        return self.map(FUNCTIONS.boolean_to_int())

    def _array_to_proto(self, array):
        res = []
        for x in array:
            if isinstance(x, str):
                res.append(x)
            elif isinstance(x, list):
                res.append(self._array_to_proto(x))
            elif isinstance(x, _ResultSource):
                res.append(x._to_proto())
            elif isinstance(x, _ResultStream):
                res.append(x._to_proto())
        return res

    def _to_proto(self):
        res = self._array_to_proto(self._operator_array)
        return res

    def add(self, other):
        """Allows addition between streams. The addition is done element-wise.
        Can also be performed on buffers and other operators, but they must have the
        same dimensions.

        Example::

        >>>     i = declare(int)
        >>>     j = declare(int)
        >>>     k = declare(int, value=5)
        >>>     stream = declare_stream()
        >>>     stream2 = declare_stream()
        >>>     stream3 = declare_stream()
        >>>     with for_(j, 0, j < 30, j + 1):
        >>>         with for_(i, 0, i < 10, i + 1):
        >>>             save(i, stream)
        >>>             save(j, stream2)
        >>>             save(k, stream3)
        >>>
        >>>     with stream_processing():
        >>>         (stream1 + stream2 + stream3).save_all("example1")
        >>>         (stream1.buffer(10) + stream2.buffer(10) + stream3.buffer(10)).save_all("example2")
        >>>         (stream1 + stream2 + stream3).buffer(10).average().save("example3")
        """
        return self.__add__(other)

    def subtract(self, other):
        """Allows substraction between streams. The substraction is done element-wise.
        Can also be performed on buffers and other operators, but they must have the
        same dimensions.

        Example::

        >>>     i = declare(int)
        >>>     j = declare(int)
        >>>     k = declare(int, value=5)
        >>>     stream = declare_stream()
        >>>     stream2 = declare_stream()
        >>>     stream3 = declare_stream()
        >>>     with for_(j, 0, j < 30, j + 1):
        >>>         with for_(i, 0, i < 10, i + 1):
        >>>             save(i, stream)
        >>>             save(j, stream2)
        >>>             save(k, stream3)
        >>>
        >>>     with stream_processing():
        >>>         (stream1 - stream2 - stream3).save_all("example1")
        >>>         (stream1.buffer(10) - stream2.buffer(10) - stream3.buffer(10)).save_all("example2")
        >>>         (stream1 - stream2 - stream3).buffer(10).average().save("example3")
        """
        return self.__sub__(other)

    def multiply(self, other):
        """Allows multiplication between streams. The multiplication is done element-wise.
        Can also be performed on buffers and other operators, but they must have the
        same dimensions.

        Example::

        >>>     i = declare(int)
        >>>     j = declare(int)
        >>>     k = declare(int, value=5)
        >>>     stream = declare_stream()
        >>>     stream2 = declare_stream()
        >>>     stream3 = declare_stream()
        >>>     with for_(j, 0, j < 30, j + 1):
        >>>         with for_(i, 0, i < 10, i + 1):
        >>>             save(i, stream)
        >>>             save(j, stream2)
        >>>             save(k, stream3)
        >>>
        >>>     with stream_processing():
        >>>         (stream1 * stream2 * stream3).save_all("example1")
        >>>         (stream1.buffer(10) * stream2.buffer(10) * stream3.buffer(10)).save_all("example2")
        >>>         (stream1 * stream2 * stream3).buffer(10).average().save("example3")
        """
        return self.__mul__(other)

    def divide(self, other):
        """Allows division between streams. The division is done element-wise.
        Can also be performed on buffers and other operators, but they must have the
        same dimensions.

        Example::

        >>>     i = declare(int)
        >>>     j = declare(int)
        >>>     k = declare(int, value=5)
        >>>     stream = declare_stream()
        >>>     stream2 = declare_stream()
        >>>     stream3 = declare_stream()
        >>>     with for_(j, 0, j < 30, j + 1):
        >>>         with for_(i, 0, i < 10, i + 1):
        >>>             save(i, stream)
        >>>             save(j, stream2)
        >>>             save(k, stream3)
        >>>
        >>>     with stream_processing():
        >>>         (stream1 / stream2 / stream3).save_all("example1")
        >>>         (stream1.buffer(10) / stream2.buffer(10) / stream3.buffer(10)).save_all("example2")
        >>>         (stream1 / stream2 / stream3).buffer(10).average().save("example3")
        """
        return self.__truediv__(other)

    def __add__(self, other):
        if isinstance(other, _ResultStream):
            return _ResultStream(["+", self, other], None)
        elif isinstance(other, (int, float)) and not isinstance(other, bool):
            return _ResultStream(["+", self, str(other)], None)
        elif hasattr(other, "__len__"):
            return _ResultStream(
                ["+", self, ["@array"] + [str(item) for item in list(other)]], None
            )

    def __radd__(self, other):
        if isinstance(other, (int, float)) and not isinstance(other, bool):
            return _ResultStream(["+", str(other), self], None)
        elif hasattr(other, "__len__"):
            return _ResultStream(
                ["+", ["@array"] + [str(item) for item in list(other)], self], None
            )

    def __sub__(self, other):
        if isinstance(other, _ResultStream):
            return _ResultStream(["-", self, other], None)
        elif isinstance(other, (int, float)) and not isinstance(other, bool):
            return _ResultStream(["-", self, str(other)], None)
        elif hasattr(other, "__len__"):
            return _ResultStream(
                ["-", self, ["@array"] + [str(item) for item in list(other)]], None
            )

    def __rsub__(self, other):
        if isinstance(other, (int, float)) and not isinstance(other, bool):
            return _ResultStream(["-", str(other), self], None)
        elif hasattr(other, "__len__"):
            return _ResultStream(
                ["-", ["@array"] + [str(item) for item in list(other)], self], None
            )

    def __gt__(self, other):
        raise Exception("Can't use this operator on results")

    def __ge__(self, other):
        raise Exception("Can't use this operator on results")

    def __lt__(self, other):
        raise Exception("Can't use this operator on results")

    def __le__(self, other):
        raise Exception("Can't use this operator on results")

    def __eq__(self, other):
        raise Exception("Can't use this operator on results")

    def __mul__(self, other):
        if isinstance(other, _ResultStream):
            return _ResultStream(["*", self, other], None)
        elif isinstance(other, (int, float)) and not isinstance(other, bool):
            return _ResultStream(["*", self, str(other)], None)
        elif hasattr(other, "__len__"):
            return _ResultStream(
                ["*", self, ["@array"] + [str(item) for item in list(other)]], None
            )

    def __rmul__(self, other):
        if isinstance(other, (int, float)) and not isinstance(other, bool):
            return _ResultStream(["*", str(other), self], None)
        elif hasattr(other, "__len__"):
            return _ResultStream(
                ["*", ["@array"] + [str(item) for item in list(other)], self], None
            )

    def __div__(self, other):
        raise Exception("Can't use this operator on results")

    def __truediv__(self, other):
        if isinstance(other, _ResultStream):
            return _ResultStream(["/", self, other], None)
        elif isinstance(other, (int, float)) and not isinstance(other, bool):
            return _ResultStream(["/", self, str(other)], None)
        elif hasattr(other, "__len__"):
            return _ResultStream(
                ["/", self, ["@array"] + [str(item) for item in list(other)]], None
            )

    def __rtruediv__(self, other):
        if isinstance(other, (int, float)) and not isinstance(other, bool):
            return _ResultStream(["/", str(other), self], None)
        elif hasattr(other, "__len__"):
            return _ResultStream(
                ["/", ["@array"] + [str(item) for item in list(other)], self], None
            )

    def __lshift__(self, other):
        save(other, self)

    def __rshift__(self, other):
        raise Exception("Can't use this operator on results")

    def __and__(self, other):
        raise Exception("Can't use this operator on results")

    def __or__(self, other):
        raise Exception("Can't use this operator on results")

    def __xor__(self, other):
        raise Exception("Can't use this operator on results")


class _ResultSourceTimestampMode(Enum):
    Values = 0
    Timestamps = 1
    ValuesAndTimestamps = 2


@dataclass
class _ResultSourceConfiguration:
    var_name: str
    timestamp_mode: _ResultSourceTimestampMode
    is_adc_trace: bool
    input: int
    auto_reshape: bool


class _ResultSource(_ResultStream):
    """
    A python object representing a source of values that can be processed in a :func:`stream_processing()` pipeline

    This interface is chainable, which means that calling most methods on this object will create a new streaming source

    See the base class :class:`_ResultStream` for operations
    """

    def __init__(self, configuration: _ResultSourceConfiguration):
        super().__init__(None, None)
        self._configuration = configuration

    def _to_proto(self):
        result = [
            _ResultSymbol,
            str(self._configuration.timestamp_mode.value),
            self._configuration.var_name,
        ]
        inputs = (
            ["@macro_input", str(self._configuration.input), result]
            if self._configuration.input != -1
            else result
        )
        auto_reshape = (
            ["@macro_auto_reshape", inputs]
            if self._configuration.auto_reshape
            else inputs
        )
        return (
            ["@macro_adc_trace", auto_reshape]
            if self._configuration.is_adc_trace
            else auto_reshape
        )

    def _get_var_name(self):
        return self._configuration.var_name

    def with_timestamps(self) -> _ResultStream:
        """Get a stream with the relevant timestamp for each stream-item"""
        return _ResultSource(
            dataclasses.replace(
                self._configuration,
                timestamp_mode=_ResultSourceTimestampMode.ValuesAndTimestamps,
            )
        )

    def timestamps(self) -> _ResultStream:
        """Get a stream with only the timestamps of the stream-items"""
        return _ResultSource(
            dataclasses.replace(
                self._configuration,
                timestamp_mode=_ResultSourceTimestampMode.Timestamps,
            )
        )

    def input1(self) -> "_ResultSource":
        """A stream of raw ADC data from input 1. Only relevant when saving data from measure statement."""
        return _ResultSource(dataclasses.replace(self._configuration, input=1))

    def input2(self) -> "_ResultSource":
        """A stream of raw ADC data from input 2. Only relevant when saving data from measure statement."""
        return _ResultSource(dataclasses.replace(self._configuration, input=2))

    def auto_reshape(self) -> "_ResultSource":
        """
        Creates a buffer with dimensions according to the program structure in QUA.

        For example, when running the following program the result "reshaped" will have
        shape of (30,10):

        Example::

        >>>     i = declare(int)
        >>>     j = declare(int)
        >>>     stream = declare_stream()
        >>>     with for_(i, 0, i < 30, i + 1):
        >>>         with for_(j, 0, j < 10, j + 1):
        >>>             save(i, stream)
        >>>
        >>>     with stream_processing():
        >>>         stream.auto_reshape().save_all("reshaped")
        """
        return _ResultSource(
            dataclasses.replace(self._configuration, auto_reshape=True)
        )


def bins(start, end, number_of_bins):
    bin_size = _math.ceil((end - start + 1) / float(number_of_bins))
    binsList = []
    while start < end:
        step_end = start + bin_size - 1
        if step_end >= end:
            step_end = end
        binsList = binsList + [[start, step_end]]
        start += bin_size
    return binsList
