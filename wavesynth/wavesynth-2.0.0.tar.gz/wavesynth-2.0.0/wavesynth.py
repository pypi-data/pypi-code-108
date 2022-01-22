# -*- coding: utf-8 -*-
"""
A simple (and cheesy-sounding) sound-synthesis library for playing with
some basic sounds. This library does not by default play any sounds using
your system's speakers. It just generates lists of numbers between 0 and
1, which it can save as .wav files to be played by another program. If
you have the `simpleaudio` package installed, however, you will be able
to play sounds directly.

wavesynth.py

This module defines constants named C0 though B9 which hold the frequency
values of notes in scientific pitch notation, and it also defines
constants P0 through P14 which hold three octaves worth of notes from a
pentatonic scale where the middle octave starts with P5 == C4.

The system remembers the current track, time-point, instrument, pitch,
and volume, and notes are added given a specific duration using those
values. However, it's not like playing an instrument, where time is
continuous and irreversible: it's possible to change the current
time-point to write multiple notes that overlap each other.

A current key is tracked, and you can change the fundamental note and
select from a few different scale types including major, minor, and
pentatonic scales.
"""

__version__ = "2.0.0"

import math, random, struct, wave

# Import simpleaudio if it's available, but don't make a fuss if it isn't.
try:
    import simpleaudio
except Exception:
    simpleaudio = None


DEBUG = False
"""
Controls whether debugging messages get printed or not.
"""


def _debug(*args, **kwargs):
    """
    Debugging function; supply same arguments as for `print`.
    """
    if DEBUG:
        print(*args, **kwargs)
    # else do nothing


#-----------#
# Constants #
#-----------#

SOUND_SPEED = 340.29
"""
The speed of sound, in meters/second. Useful for computing reverb delays.
"""

SAMPLE_RATE = 44100
"""
We do all of our processing at this sample rate.
"""

DT = 1 / SAMPLE_RATE
"""
From the sample rate we can compute the time delta between samples.
"""

SAMPLE_WIDTH = 2
"""
Bytes per sample.
"""

DEFAULT_LIMITER_DELAY = 44100 // 100 # 1/100th of a second
"""
Default delay for the limiter, in frames.
"""

DEFAULT_LIMITER_RELAX_DURATION = 44100 // 4 # 1/4 of a second
"""
Default relax duration for the limiter, in frames.
"""

#----------------#
# Tone Constants #
#----------------#

SEMITONE = 2 ** (1 / 12)

PITCH_NAMES = [
    "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"
]
SHARP_NAMES = {
    "Db": "Cs",
    "Eb": "Ds",
    "Gb": "Fs",
    "Ab": "Gs",
    "Bb": "As"
}
PIANO_KEYS = []

# see: https://en.wikipedia.org/wiki/Scientific_pitch_notation
BASE_FREQUENCY = 16.352
"""
The frequency of C0, the lowest note in scientific pitch notation.
"""

# Set extra global variables based on pitch names:
_freq = BASE_FREQUENCY
for _octave in range(10):
    for _pitch in PITCH_NAMES:
        _rounded = round(_freq, 4)
        globals()[_pitch + str(_octave)] = _rounded
        PIANO_KEYS.append((_pitch + str(_octave), _rounded))
        if _pitch in SHARP_NAMES:
            globals()[SHARP_NAMES[_pitch] + str(_octave)] = _rounded
        _freq *= SEMITONE


# Pentatonic scale with a more limited octave range than the piano keys
# See: https://en.wikipedia.org/wiki/Pentatonic_scale
PENTATONIC_NOTES = [
    ("P0", C3), # noqa F821
    ("P1", D3), # noqa F821
    ("P2", E3), # noqa F821
    ("P3", G3), # noqa F821
    ("P4", A3), # noqa F821
    ("P5", C4), # noqa F821
    ("P6", D4), # noqa F821
    ("P7", E4), # noqa F821
    ("P8", G4), # noqa F821
    ("P9", A4), # noqa F821
    ("P10", C5), # noqa F821
    ("P11", D5), # noqa F821
    ("P12", E5), # noqa F821
    ("P13", G5), # noqa F821
    ("P14", A5), # noqa F821
]

for _name, _freq in PENTATONIC_NOTES:
    globals()[_name] = _freq


#----------------#
# Key management #
#----------------#


def currentKey():
    """
    Returns the current key as a pair of fundamental note name plus
    scale type (see `CURRENT_KEY`).
    """
    return CURRENT_KEY


def currentFundamentalName():
    """
    Returns the name of the current fundamental note, which by default
    is C0.
    """
    return CURRENT_KEY[0] + "0"


def currentFundamental():
    """
    Returns the numeric pitch value for the fundamental note of the
    current key. This is based on the key's fundamental note name string
    in the octave 0. Raises an error if the key string is invalid.
    """
    noteName = CURRENT_KEY[0] + "0"
    g = globals()
    if noteName not in g:
        raise ValueError(
            "Current key's fundamental note '{}' is invalid.".format(
                noteName
            )
        )
    return g[noteName]


def setFundamental(noteName):
    """
    Sets the fundamental pitch for the current key, leaving the scale
    type unchanged. The given noteName must be a valid pitch name, which
    is one of:

           A    B C    D    E F    G
        Ab   Bb     Db   Eb     Gb
             As     Cs   Ds     Fs   Gs

    A trailing 'b' or 's' indicates flat ('b') or sharp ('s'). If a name
    with 's' is given, it will be converted into the equivalent 'b'
    name.
    """
    global CURRENT_KEY

    if not isinstance(noteName, str):
        raise TypeError("The note name must be a string.")

    if noteName not in PITCH_NAMES and noteName not in SHARP_NAMES.values():
        raise ValueError(
            (
                "Invalid fundamental note name: '{}'. A note name must"
                " start with a letter A-G and may be followed by 'b'"
                " for flat or 's' for sharp; Cb/Bs and Fb/Es are not"
                " allowed."
            ).format(noteName)
        )

    # Convert to canonical form
    if noteName in SHARP_NAMES.values():
        # Lazy dictionary inversion
        for name in SHARP_NAMES:
            if SHARP_NAMES[name] == noteName:
                noteName = name
                break

    CURRENT_KEY = (noteName, CURRENT_KEY[1])


def currentScaleType():
    """
    Returns a string describing the current scale type, or for custom
    scales, either a list of semitone intervals or a pair of such lists.
    """
    return CURRENT_KEY[1]


def ascendingScaleIntervals():
    """
    Returns the list of semitone intervals in the current ascending
    scale.
    """
    if isinstance(CURRENT_KEY[1], str):
        if CURRENT_KEY[1] not in SCALE_TYPES:
            raise ValueError(
                (
                    "Invalid scale type '{}': named scale types must be"
                    " one of:\n  {}"
                ).format(
                    CURRENT_KEY[1],
                    '\n  '.join(SCALE_TYPES.keys())
                )
            )
        intervals = SCALE_TYPES[CURRENT_KEY[1]]
    else:
        intervals = CURRENT_KEY[1]

    if isinstance(intervals, tuple):
        return intervals[0]
    elif isinstance(intervals, list):
        return intervals
    else:
        raise TypeError(
            (
                "Custom scale types must be lists or tuples (the"
                " current scale type is a {})."
            ).format(type(intervals))
        )


def descendingScaleIntervals():
    """
    Returns the list of semitone intervals in the current descending
    scale.
    """
    if isinstance(CURRENT_KEY[1], str):
        if CURRENT_KEY[1] not in SCALE_TYPES:
            raise ValueError(
                (
                    "Invalid scale type '{}': named scale types must be"
                    " one of:\n  {}"
                ).format(
                    CURRENT_KEY[1],
                    '\n  '.join(SCALE_TYPES.keys())
                )
            )
        intervals = SCALE_TYPES[CURRENT_KEY[1]]
    else:
        intervals = CURRENT_KEY[1]

    if isinstance(intervals, tuple):
        return intervals[1]
    elif isinstance(intervals, list):
        return intervals
    else:
        raise TypeError(
            (
                "Custom scale types must be lists or tuples (the"
                " current scale type is a {})."
            ).format(type(intervals))
        )


def setScaleType(scaleType):
    """
    Sets the current scale type, leaving the fundamental note for the
    current key unchanged. The `SCALE_TYPES` variable defines available
    scale types, and one of the keys from that dictionary should be
    used. For a custom scale type, a list of integers may be provided
    instead, defining the semitones between successive notes in the
    scale. If different ascending/descending note sequences are desired,
    a pair of such lists may be provided specifying first the ascending
    and then the descending note sequences.
    """
    if not isinstance(scaleType, (list, tuple, str)):
        raise TypeError(
            (
                "The scale type must be a string, list, or tuple (you"
                " provided a/an {})"
            ).format(type(scaleType))
        )

    if isinstance(scaleType, str) and scaleType not in SCALE_TYPES:
        raise ValueError(
            (
                "Invalid scale type '{}': named scale types must be"
                " one of:\n  {}"
            ).format(
                scaleType,
                '\n  '.join(SCALE_TYPES.keys())
            )
        )


#-----------------#
# Tone management #
#-----------------#

def halfStepUpFrom(pitch, nSteps=1):
    """
    Returns the tone that's `nSteps` (default 1) half-step(s) above the
    given pitch (`nSteps` may be negative).
    """
    if not isinstance(pitch, (int, float)):
        raise TypeError("Pitch must be a number.")

    return pitch * SEMITONE**nSteps


def halfStepDownFrom(pitch, nSteps=1):
    """
    Returns the tone that's `nSteps` (default 1) half-step(s) below the
    given pitch.
    """
    return halfStepUpFrom(pitch, -nSteps)


def pianoIndex(pitch):
    """
    Finds the index within the piano keys of the pitch that's closest to
    the given pitch, or returns None if the pitch is too high or low.
    """
    linear = math.log(pitch / C0) / math.log(SEMITONE) # noqa F821
    nearest = C0 * math.pow(SEMITONE, round(linear)) # noqa F821
    match = round(nearest, 4)

    for i, (name, freq) in enumerate(PIANO_KEYS):
        if abs(match - freq) < 0.01:
            return i

    # No matches found
    return None


def pentatonicIndex(pitch):
    """
    Finds the index within the pentatonic tones of the pitch that's
    closest to the given pitch. Returns one end of the scale if the given
    pitch is too high or too low.
    """
    mindist = None
    best = None
    for i, (name, freq) in enumerate(PENTATONIC_NOTES):
        dist = abs(math.log(freq) - math.log(pitch))
        if mindist is None or mindist > dist:
            mindist = dist
            best = i

    return best


def climbUpFrom(pitch, nRungs=1):
    """
    Returns the tone that's nRungs (default 1) scale-degrees above the
    given pitch based on the current key (see `CURRENT_KEY`). Detects
    the nearest in-key pitch and gives the tone nRungs degrees above
    that pitch.

    If nRungs is negative, returns a lower pitch, and uses the
    descending scale intervals instead of the ascending ones if they're
    different.
    """
    if not isinstance(pitch, (int, float)):
        raise TypeError("Pitch must be a number.")

    if not isinstance(nRungs, int):
        raise TypeError("nRungs must be an integer.")

    if nRungs == 0:
        return pitch

    # Compute how many octaves above or below our scale base we are
    fundamental = currentFundamental()

    # Multiplier between the fundamental pitch and the given pitch
    multiplier = pitch / fundamental

    # Compute number of half-steps above/below the fundamental, rounded
    # to the nearest half-step.
    halfSteps = round(math.log(multiplier) / math.log(SEMITONE))

    # Get intervals for the current key
    if nRungs > 0:
        intervals = ascendingScaleIntervals()
    else: # must be < 0, as == 0 was handled above
        intervals = descendingScaleIntervals()

    # Compute what counts as an octave (normally this should be 12)
    octaveHalfSteps = sum(intervals)

    # Compute which octave we're in
    octave = halfSteps // octaveHalfSteps

    # Compute how many steps along that octave we are
    stepsInOctave = halfSteps % octaveHalfSteps

    # Find nearest rung of the current key -- our starting rung
    stepsSoFar = 0
    stepsAboveFundamental = octave * octaveHalfSteps
    for rung in range(len(intervals)):
        intHere = intervals[rung]
        if stepsSoFar + intHere > stepsInOctave:
            below = stepsInOctave - stepsSoFar
            above = stepsSoFar + intHere - stepsInOctave
            if below < above:
                stepsAboveFundamental += stepsSoFar
                break
            else:
                stepsAboveFundamental += stepsSoFar + intHere
                rung += 1
                break
        stepsSoFar += intHere
    else:
        # if we reach the end of the loop without breaking, we must have
        # hit highest end of octave
        stepsAboveFundamental += octaveHalfSteps

    # Loop upwards through intervals to increase the pitch
    if nRungs > 0:
        for climb in range(rung, rung + nRungs):
            stepsAboveFundamental += intervals[climb % len(intervals)]
    else: # must be < 0, since == 0 was handled above
        for climb in range(rung, rung + nRungs, -1):
            stepsAboveFundamental -= intervals[(climb - 1) % len(intervals)]

    return halfStepUpFrom(fundamental, stepsAboveFundamental)


def climbDownFrom(pitch, nRungs=1):
    """
    The opposite of `climbUpFrom`. Equivalent to calling that function
    with the same pitch and -nRungs as the argument.
    """
    return climbUpFrom(pitch, -nRungs)


#-----------------#
# Basic waveforms #
#-----------------#

def silence(t):
    """
    Zero-amplitude silence.
    """
    return 0


def sine(t):
    """
    A 1-hertz sine wave as a function of time in seconds.
    """
    return math.sin(t * 2 * math.pi)


def triangle(t):
    """
    A 1-hertz triangle wave as a function of time in seconds.
    """
    tt = t % 1.0
    if tt < 0.25:
        return tt / 0.25
    elif tt < 0.75:
        return 1 - 2 * ((tt - 0.25) / 0.5)
    else:
        return -1 + (tt - 0.75) / 0.25


def sawtooth(t):
    """
    A 1-hertz sawtooth wave as a function of time in seconds.
    """
    tt = t % 1.0
    if tt < 0.5:
        return tt / 0.5
    else:
        return -1 + (tt - 0.5) / 0.5


def square(t):
    """
    A 1-hertz square wave as a function of time in seconds.
    """
    tt = t % 1.0
    if tt < 0.5:
        return 1
    else:
        return -1


def whiteNoise(_):
    """
    White noise. Pure (pseudo-)random samples from the entire domain. The
    parameter is ignored, but exists so that whiteNoise is a valid signal
    function. Note that this gives whiteNoise an infinitely fractal
    nature: it cannot be distorted or paced as the result will still be
    the original noise.
    """
    return 1 - 2 * random.random()


def lfsr(x):
    """
    A tiny chaos engine: a linear-feedback shift register.

    See: https://en.wikipedia.org/wiki/Linear-feedback_shift_register
    """
    lsb = x & 1
    r = x >> 1
    # pseudo-if
    r ^= lsb * 0xe800000000000000 # 64, 63, 61, 60
    return r & ((1 << 64) - 1) # mask to 64 bits


def prng(x):
    """
    Repeated application of an lfsr to get pseudo-random values.

    Empirically, 12 rounds seems to be enough mixing to scramble all 64
    bits when results are observed from sequential seeds. This is not by
    any means a high-quality prng.
    """
    for i in range(12):
        x = lfsr(x * 37 + i * 31)
    return x


def fval(pval):
    """
    Converts a PRNG output into a floating-point number between 0 and 1.
    """
    return pval / ((1 << 64) - 1)


def ival(fval):
    """
    Converts a floating-point value into an integer useable as a prng
    value (but there's no obvious relationship between the float that
    goes in and the int that comes out.
    """
    b = struct.pack("d", fval)
    return struct.unpack("q", b)[0]


BROWN_NOISE_INTERVAL = 8 * DT
"""
Rate at which we let the brown noise wander.
"""


def brownishNoise(t):
    """
    Brown noise, via Brownian motion in the sample domain with steps
    every BROWN_NOISE_INTERVAL seconds, fixed to pass through a
    pseudo-random target value every second.

    See: https://en.wikipedia.org/wiki/Brownian_noise
    """
    before = math.floor(t)
    after = math.ceil(t)
    anchor1 = 1 - 2 * fval(prng(before))
    anchor2 = 1 - 2 * fval(prng(after))

    tt = t % 1

    stepsForward = int(tt / BROWN_NOISE_INTERVAL)
    stepsBackward = int((1 - tt) / BROWN_NOISE_INTERVAL)

    # TODO: This is untenably time-consuming!

    # Compute Brownian noise forward from the first anchor
    thread = ival(anchor2)
    sample1 = anchor1
    for i in range(stepsForward):
        thread = prng(thread)
        r = fval(thread)
        sample1 += 0.1 * (1 - 2 * r)
        if sample1 > 1:
            sample1 = 1 - (sample1 - 1)
        elif sample1 < -1:
            sample1 = (-1 + (sample1 + 1))

    # Compute Brownian noise backward from the second anchor
    thread = ival(anchor1)
    sample2 = anchor2
    for i in range(stepsBackward):
        thread = prng(thread)
        r = fval(thread)
        sample2 += 0.1 * (1 - 2 * r)
        if sample2 > 1:
            sample2 = 1 - (sample2 - 1)
        elif sample2 < -1:
            sample2 = (-1 + (sample2 + 1))

    # Interpolate between the sequence from either extreme so that we get
    # a smooth signal.
    return (1 - tt) * sample1 + tt * sample2


# Note: originally, there was a plan to have equalization functionality
# including low-, high-, and band-pass filters. However, these things
# require either the ability to integrate signals, or working with
# discrete samples, and the current architecture makes it impossible to
# integrate and incredibly costly to discretize things. So we don't
# support these things, even though they'd allow us to do much
# higher-quality synthesis.


#-------------------#
# Wave modification #
#-------------------#

def reverb(signal, gain, delay):
    """
    Applies reverb at the given gain level with the given delay (in
    seconds). You can use SOUND_SPEED to compute delay for a given room
    size in meters:

        delay = roomSize / SOUND_SPEED

    This applies three jumps of reverb, gain should normally be less than
    1 or things will get weird.
    """
    def reverberant(t):
        """A reverberating signal."""
        back3 = signal(t - delay * 3)
        back2 = signal(t - delay * 2)
        back1 = signal(t - delay * 1)

        totalWeight = 1 + gain + gain**2 + gain**3

        return (
            signal(t)
          + back1 * gain
          + back2 * gain**2
          + back3 * gain**3
        ) / totalWeight
    return reverberant


def distort(signal, distortion, distortionMagnitude):
    """
    Distorts the given stream values using the given distortion signal.
    The distortion signal is scaled to the given distortion magnitude in
    seconds.
    """
    def distorted(t):
        """A distorted signal."""
        tt = t + distortion(t) * distortionMagnitude
        return signal(tt)
    return distorted


def gain(signal, amount):
    """
    Amplifies or attenuates the given signal by the given gain amount.
    """
    def gained(t):
        """An amplified or attenuated signal."""
        return signal(t) * amount
    return gained


def pace(signal, tempo):
    """
    Sets the speed of the given signal to the given tempo (in Hertz).
    Negative tempos result in a backwards signal.
    """
    def paced(t):
        """A signal with a specified tempo."""
        tt = t * tempo
        return signal(tt)
    return paced


def shift(signal, delay):
    """
    Shifts the signal in time by the given delay amount (in seconds). A
    negative delay can shift a signal backward in time.
    """
    def shifted(t):
        """A signal shifted in time."""
        return signal(t - delay)
    return shifted


#------------------#
# Wave Combination #
#------------------#

def modulate(*signals):
    """
    Multiplies multiple signals.
    """
    def modulated(t):
        """The product of several signals."""
        result = 1
        for signal in signals:
            result *= signal(t)
        return result
    modulated.__doc__ = (
        "The product of several signals:\n"
        "    {}\n"
    ).format(
        '\n    '.join(
            signal.__doc__
            for signal in signals
        )
    )
    return modulated


def mix(*gainedSignals, normalize=False):
    """
    Mixes multiple signals together. Each argument should be a tuple
    containing a floating point number for the gain of that signal, and a
    signal (a function of time in seconds), or it can be just a signal
    function, in which case the default gain of 1.0 is used.

    Each signal is multiplied by the associated gain before being added
    to the overall result, and if normalize is set to true, after adding
    the signals together the resulting signal will be divided by the sum
    of their gains.

    An example:

        mix(
            pace(sine, 440),
            (0.2, pace(sine, 880))
        )

    """
    withGains = [
        (1.0, pair) if not isinstance(pair, (list, tuple)) else pair
        for pair in gainedSignals
    ]

    def mixed(t):
        """The result of mixing several signals together."""
        result = 0
        combinedWeight = 0
        for gainSignal in withGains:
            gain, signal = gainSignal
            combinedWeight += gain
            result += gain * signal(t)

        if normalize:
            return result / combinedWeight
        else:
            return result
    mixed.__doc__ = (
        "A {}mix of several signals at different volume levels:\n"
        "    {}\n"
    ).format(
        'normalized ' if normalize else '',
        '\n    '.join(
            '({:.2f}) {}'.format(gain, signal.__doc__)
            for (gain, signal) in withGains
        )
    )
    return mixed


def crossfade(before, after, delay, fadeDuration, fadeShape=lambda x: x):
    """
    Fades between two signals, from the before signal (full volume until
    the delay has elapsed) to the after signals (full volume after the
    delay + the fade duration). In between, the shape of the fade is
    controlled by the fadeShape function, which gets the fraction of the
    fade elapsed as an input (0-1) and should return the fraction of the
    after stream to include (0-1; should start at 0 and end at 1).
    """
    def crossfaded(t):
        """A crossfade between two signals."""
        if t < delay:
            return before(t)
        elif t < delay + fadeDuration:
            interp = (t - delay) / fadeDuration
            interp = fadeShape(interp)
            return (1 - interp) * before(t) + interp * after(t)
        else:
            return after(t)
    crossfaded.__doc__ = (
        "A crossfade between two signals at {:.2f}s for {:.3f}s:\n"
        "  The first signal is:\n    {}\n"
        "  The second signal is:\n    {}\n"
    ).format(
        delay,
        fadeDuration,
        before.__doc__,
        after.__doc__
    )
    return crossfaded


def splice(base, signal, when, duration):
    """
    Splices the given signal onto the given base signal, cutting
    with no transition to the given signal at the given time, and after
    the given duration, cutting back to the base signal.

    Unless the sample values match up at the endpoints of the splice,
    this may create clicking sounds.

    The spliced-in signal's time will be shifted so that t=0 is aligned
    to the beginning of the splice.
    """
    def spliced(t):
        """A base signal with a different signal spliced into it."""
        if t < when:
            return base(t)
        elif t < when + duration:
            return signal(t - when)
        else:
            return base(t)
    spliced.__doc__ = (
        "A spliced signal at {:.2f}s for {:.3f}s:\n"
        "  The base signal is:\n    {}\n"
        "  The spliced signal is:\n    {}\n"
    ).format(
        when,
        duration,
        base.__doc__,
        signal.__doc__
    )
    return spliced


def stack(base, signal, when, duration):
    """
    Stacks the given signal onto the given base signal, starting the
    stacked signal's t=0 at the given when value, and ending the stacking
    after the given duration.

    Stacking signals may cause out-of-range values, which will be handled
    during limiting.

    If the signal values at the endpoints of the stacked region aren't
    zero, this may create clicking sounds.
    """
    def stacked(t):
        """A base signal with a different signal stacked into it."""
        if t < when:
            return base(t)
        elif t < when + duration:
            return base(t) + signal(t - when)
        else:
            return base(t)
    stacked.__doc__ = (
        "A stacked signal at {:.2f}s for {:.3f}s:\n"
        "  The base signal is:\n    {}\n"
        "  The stacked signal is:\n    {}\n"
    ).format(
        when,
        duration,
        base.__doc__,
        signal.__doc__
    )
    return stacked


#-----------------------#
# Finite-energy signals #
#-----------------------#

def attack(signal, duration, shape=lambda x: x):
    """
    A version of the given signal with gain 0 at t=0, and 1 after the
    given duration, but in between it's the result of a linear gradient
    passed into the given shape function.
    """
    def attacked(t):
        """A signal that starts silent and ramps up at t=0."""
        if t <= 0:
            return 0
        elif t < duration:
            tt = t / duration
            return shape(tt) * signal(t)
        else:
            return signal(t)
    attacked.__doc__ = (
        "A signal which starts from silence and swells over {:.3f} seconds:\n"
        "    {}\n"
    ).format(
        duration,
        signal.__doc__
    )
    return attacked


def fade(signal, delay, duration, shape=lambda x: x):
    """
    A version of the given signal with gain 1 at t<=delay, gain 0 after
    the given duration, and in between it's 1 - the result of a linear
    gradient passed into the given shape function.
    """
    def faded(t):
        """A fade signal."""
        if t <= delay:
            return signal(t)
        elif t < delay + duration:
            tt = (t - delay) / duration
            return (1 - shape(tt)) * signal(t)
        else:
            return 0
    faded.__doc__ = (
        "A signal which fades into silence over {:.3f}s at {:.2f}s:\n"
        "    {}\n"
    ).format(
        duration,
        delay,
        signal.__doc__
    )
    return faded


def note(
    waveform,
    duration=0.5,
    attackFraction=0.07,
    fadeFraction=0.5,
    attackShape=lambda x: x,
    fadeShape=lambda x: x
):
    """
    Combines an infinite waveform with attack and fade shapes and a
    finite duration to produce a finite-energy note signal. The note
    always starts at t = 0.
    """
    result = attack(waveform, duration * attackFraction, attackShape)
    result = fade(
        result,
        duration * (1 - fadeFraction),
        duration * fadeFraction,
        fadeShape
    )
    return result


#-------------#
# Instruments #
#-------------#

def beep(hz, duration, volume):
    """
    Generates a relatively pure sine-wave-based note.
    """
    waveform = mix(
        pace(triangle, hz),
        (0.2, pace(sine, hz * 2)),
        (0.1, pace(sine, hz * 4)),
        normalize=True
    )
    waveform = gain(waveform, volume)
    return note(waveform, duration)


def harmonica(hz, duration, volume):
    """
    Generates a sawtooth-based note with a odd overtones and a bit of
    reverb.
    """
    waveform = mix(
        pace(sawtooth, hz),
        (0.2, pace(sawtooth, hz * 3)),
        (0.1, pace(sawtooth, hz * 5)),
        (0.05, pace(sawtooth, hz * 7)),
        normalize=True
    )
    waveform = reverb(waveform, 0.2, 0.17 / SOUND_SPEED)
    waveform = gain(waveform, volume)
    return note(
        waveform,
        duration,
        attackFraction=0.2,
        fadeFraction=0.6,
        attackShape=lambda x: x ** 2,
        fadeShape=lambda x: x ** 2
    )


def keyboard(hz, duration, volume):
    """
    Generates a triangle-based note with even overtones.
    """
    waveform = mix(
        pace(triangle, hz),
        (0.2, pace(triangle, hz * 2)),
        (0.1, pace(triangle, hz * 4)),
        (0.05, pace(triangle, hz * 6)),
        normalize=True
    )
    waveform = gain(waveform, volume)
    return note(
        waveform,
        duration,
        attackFraction=0.04,
        fadeFraction=0.8,
        attackShape=lambda x: x ** 0.5,
        fadeShape=lambda x: x
    )


def snare(duration, volume):
    """
    Generates wave-modulated white noise with an instant attack.
    """
    waveform = mix(
        modulate(whiteNoise, pace(sine, 193)),
        (0.3, modulate(whiteNoise, pace(triangle, 182))),
        normalize=True
    )
    waveform = gain(waveform, volume)
    return note(
        waveform,
        duration,
        attackFraction=0,
        fadeFraction=0.9,
        fadeShape=lambda x: x ** 0.5 # sqrt fade is faster than linear
    )


def kick(duration, volume):
    """
    Generates an impulse plus some low-frequency waves like a kick drum.
    """
    pulseAttack = duration / 192
    click = fade(
        pace(triangle, 1 / (2 * pulseAttack)),
        0,
        pulseAttack,
        lambda x: 0
    )
    vibrate = mix(
        (0.7, pace(sine, 52)),
        (0.2, pace(sine, 52 * SEMITONE)),
        (0.1, pace(sine, 52 * SEMITONE**3)),
        normalize=True
    )

    clickThenVibrate = crossfade(
        click,
        vibrate,
        pulseAttack * 0.95,
        pulseAttack * 0.3
    )

    waveform = gain(clickThenVibrate, volume)
    return note(
        waveform,
        duration,
        attackFraction=0,
        fadeFraction=0.3,
        fadeShape=lambda x: x ** 0.5 # sqrt fade is faster than linear
    )


#--------------#
# Global state #
#--------------#


CURRENT_INSTRUMENT = keyboard
"""
The instrument to be used when `addNote` is called. Change this using
`setInstrument`.
"""


def setInstrument(instrument):
    """
    Sets the current instrument, to be used when `addNote` is called.
    The argument must be a function which accepts pitch and duration
    as parameters in that order, examples include `keyboard` and
    `harmonica`, or it may be the name of such a function in this module
    as a string. Note that pitchless instruments like `snare` should be
    handled via `setDrum` instead.
    """
    global CURRENT_INSTRUMENT

    if isinstance(instrument, str):
        name = instrument
        try:
            instrument = globals()[instrument]
        except Exception:
            raise TypeError(
                "'{}' is not a valid instrument name.".format(name)
            )
    elif not isinstance(instrument, type(lambda: 0)):
        raise TypeError(
            (
                "The instrument must be an instrument name string or an"
              + " instrument function (got: {})."
            ).format(repr(instrument))
        )

    if instrument.__code__.co_argcount < 3:
        raise TypeError(
            (
                "The instrument function must accept pitch, duration,"
              + " and volume arguments (function '{}' accepts {}"
              + " positional arguments)."
            ).format(instrument.__name__, instrument.__code__.co_argcount)
        )

    CURRENT_INSTRUMENT = instrument


def currentInstrumentName():
    """
    Returns the name of the current instrument (a string), which
    indicates the particular sound qualities used when `addNote` is
    called. Note that if you're using custom instrument functions, the
    current instrument name is not necessarily a valid argument to
    `setInstrument`.
    """
    return CURRENT_INSTRUMENT.__name__


def currentInstrument():
    """
    Returns the current instrument function (as a function, not a
    string; use `currentInstrumentName` to get the name).
    """
    return CURRENT_INSTRUMENT


CURRENT_DRUM = snare
"""
The drum to be used when `addBeat` is called. Change this using
`setDrum`.
"""


def setDrum(drum):
    """
    Sets the current drum type, to be used when `addBeat` is called. The
    argument must be a function which accepts a duration as a parameter,
    examples include `snare` and `kick`, or it may be the name of such a
    function in this module as a string. Note that pitched instruments
    like `keyboard` should be handled via `setInstrument` instead.
    """
    global CURRENT_DRUM

    if isinstance(drum, str):
        name = drum
        try:
            drum = globals()[drum]
        except Exception:
            raise TypeError("'{}' is not a valid drum name.".format(name))
    elif not isinstance(drum, type(lambda: 0)):
        raise TypeError(
            (
                "The drum must be an drum name string or an"
              + " drum function (got: {})."
            ).format(repr(drum))
        )

    if drum.__code__.co_argcount < 2:
        raise TypeError(
            (
                "The drum function must accept duration and volume"
              + " arguments (function '{}' accepts {} positional"
              + " arguments)."
            ).format(drum.__name__, drum.__code__.co_argcount)
        )

    CURRENT_DRUM = drum


def currentDrumName():
    """
    Returns the name of the current drum (a string), which indicates the
    particular sound qualities used when `addBeat` is called. Note that if
    you're using custom drum functions, the current drum name is not
    necessarily a valid argument to `setDrum`.
    """
    return CURRENT_DRUM.__name__


def currentDrum():
    """
    Returns the current drum function (as a function, not a string; use
    `currentDrumName` to get the name).
    """
    return CURRENT_DRUM


CURRENT_PITCH = A3 # noqa F821
"""
The pitch to use when `addNote` is called. Change using `setPitch`, or
`climbUp` and related functions.
"""

CURRENT_KEY = ("C", "Major")
"""
The key to use when moving pitches up or down using `climbUp` or
`climbDown`. Includes the first note of the scale as a string, and then
the type of scale (another string). Alternatively, a list of semitone
differences or a pair of such lists can take the place of the scale type
to use a custom scale. The `SCALE_TYPES` variable lists pre-defined scale
types that you can use.

TODO: More diverse scale types; non-semitone based tunings?
"""

SCALE_TYPES = {
    "Major": [2, 2, 1, 2, 2, 2, 1],
    "Minor-Natural": [2, 1, 2, 2, 1, 2, 2],
    "Minor-Harmonic": [2, 1, 2, 2, 1, 3, 1],
    "Minor-Melodic": ([2, 1, 2, 2, 2, 2, 1], [2, 2, 1, 2, 2, 1, 2]),
    "Pentatonic-Major": [2, 2, 3, 2, 3],
    "Pentatonic-Minor": [3, 2, 2, 3, 2],
    "Pentatonic-Yo": [2, 3, 2, 2, 3],
    "Pentatonic-In": [1, 4, 2, 3, 2],
}
"""
A mapping from scale types to lists of semitone gaps between notes in
that scale, or in some cases, pairs of lists for ascending and descending
gap lists when these are different.
"""


def setPitch(pitch):
    """
    Sets the current pitch value to the given pitch (an integer or
    floating-point number in Hertz). This pitch value will be used for
    subsequent calls to `addNote` until `setPitch` is called again or
    some other pitch-modifying function is used (e.g., `climbUp`,
    `halfStepDown`, etc.).

    You can use the constants defined in this module as pitch values,
    such as `A3` or `B5` for scientific notation pitches, or values like
    `P3` or `P10` for notes from (several octaves of) a pentatonic scale.
    """
    global CURRENT_PITCH

    if not isinstance(pitch, (int, float)):
        raise ValueError("Pitch value must be a number (int or float).")

    CURRENT_PITCH = float(pitch)


def currentPitch():
    """
    Returns the current pitch value, as a floating-point number expressed
    in Hertz.
    """
    return CURRENT_PITCH


def pitchName(pitch):
    """
    Returns the name of a given pitch, as a string in scientific pitch
    notation. If the given pitch is not a near match to a scientific
    pitch notation note, either because it is in between notes or too low
    or too high (i.e., below C0 or above B9) the string returned will
    simply include the Hertz value of the pitch as a number, followed by
    a space and the letters 'Hz'. If the pitch is close to a scientific
    notation note, it will also include in parentheses the word "just"
    and then "above" or "below", followed by a space and then the name of
    the note it is close to.
    """
    pi = pianoIndex(pitch)
    if pi is None:
        if pitch < 0.01:
            return "{:.3g} Hz".format(pitch)
        else:
            return "{:.2f} Hz".format(pitch)
    else:
        nearName, nearValue = PIANO_KEYS[pi]
        if abs(pitch - nearValue) < 0.01: # close enough
            return nearName
        elif pitch < nearValue:
            return "{:.2f} Hz (just below {})".format(pitch, nearName)
        else:
            return "{:.2f} Hz (just above {})".format(pitch, nearName)


def currentPitchName():
    """
    Returns the name of the current pitch as a string (see `pitchName`
    for details).
    """
    return pitchName(CURRENT_PITCH)


def halfStepUp(nSteps=1):
    """
    Raises the current pitch value by `nSteps` half-steps (i.e.,
    semitones). If `nSteps` isn't provided, the default is 1.
    """
    global CURRENT_PITCH
    CURRENT_PITCH = halfStepUpFrom(CURRENT_PITCH, nSteps)


def halfStepDown(nSteps=1):
    """
    Lowers the current pitch value by `nSteps` half steps (i.e.,
    semitones). `nSteps` defaults to 1.
    """
    halfStepUp(-nSteps)


def climbUp(nRungs=1):
    """
    Modifies the current pitch value to be `nRungs` notes higher on the
    current scale than the old value. Uses `climbUpFrom` to compute the
    new pitch. `nRungs` defaults to 1 if no argument is provided.
    """
    global CURRENT_PITCH
    CURRENT_PITCH = climbUpFrom(CURRENT_PITCH, nRungs)


def climbDown(nRungs=1):
    """
    The opposite of `climbUp`: reduces the current pitch value. `nRungs`
    defaults to 1.
    """
    climbUp(-nRungs)


CURRENT_TIME = 0
"""
The point in time at which a note, beat, or rest will be added when
`addNote`, `addBeat`, or `addRest` is called. These functions also
advance this value by the duration they used.
"""


def rewind(seconds):
    """
    Subtracts the given number of seconds from the current time, so that
    the next note, beat, or rest added will be added that many seconds
    earlier that it would have been otherwise (and the current time will
    continue from that point as well). The argument must be an integer or
    floating-point number in seconds.

    If the rewind would cause the current time to be less than 0, it will
    simply be set to 0, as 0 always marks the beginning of a track, and
    nothing can be added before that time.
    """
    global CURRENT_TIME

    if not isinstance(seconds, (int, float)):
        raise ValueError("Time must be given as a number (in seconds).")

    if CURRENT_TIME - seconds < 0:
        CURRENT_TIME = 0
    else:
        CURRENT_TIME -= seconds


def fastforward(seconds):
    """
    The opposite of `rewind`, this function moves the current time
    forward, so that subsequent notes, beats, or rests happen the given
    number of seconds later. The difference between `addRest` and
    `fastforward` is that `addRest` adds an entry to the current track's
    log, whereas `fastforward` does not. Also, `addRest` can be used to add
    silence at the end of a track, while `fastforward` has no effect on the
    current track at all.

    If you provide a negative amount of seconds and the result would be a
    current time less than 0, the current time will just be set to 0.
    """
    global CURRENT_TIME

    if not isinstance(seconds, (int, float)):
        raise ValueError("Time must be given as a number (in seconds).")

    if CURRENT_TIME + seconds < 0:
        CURRENT_TIME = 0
    else:
        CURRENT_TIME += seconds


def setTime(seconds):
    """
    Sets the current time value in seconds. A `ValueError` will occur if
    you provide a non-number value, or a negative number, as the current
    time must always be at least 0 (which represents the start of the
    current track).
    """
    global CURRENT_TIME

    if not isinstance(seconds, (int, float)):
        raise ValueError("Time must be given as a number (in seconds).")

    if seconds < 0:
        raise ValueError(
            (
                "You cannot set the time to a time before 0 seconds (you"
              + " provided the value {:.3g})"
            ).format(seconds)
        )

    CURRENT_TIME = float(seconds)


def currentTime():
    """
    Returns the current time, as a non-negative floating-point number in
    seconds.
    """
    return CURRENT_TIME


CURRENT_VOLUME = 0.6
"""
The current volume level, used when `addNote` or `addBeat` is called.
Change this using `increaseVolume`, `decraseVolume`, or `setVolume`.

The default volume level is 0.6, not 1.0.
"""


def louder(steps=1):
    """
    Increases the current volume by one "step", which is a factor of 1.5
    (up to the maximum volume). Does nothing if the volume is already
    maxed out. A number of steps may be provided to take multiple steps
    at once.
    """
    global CURRENT_VOLUME
    if not isinstance(steps, (int, float)):
        raise ValueError(
            "Steps must be a number (got {}).".format(repr(steps))
        )

    CURRENT_VOLUME = min(1, CURRENT_VOLUME * 1.5 ** steps)


def quieter(steps=1):
    """
    Decreases the current volume by one "step", which is a factor of 2/3
    (will never actually reach 0). Does nothing if the volume is at 0. A
    number of steps may be provided to take multiple steps at once.
    """
    global CURRENT_VOLUME
    if not isinstance(steps, (int, float)):
        raise ValueError(
            "Steps must be a number (got {}).".format(repr(steps))
        )

    CURRENT_VOLUME = min(1, CURRENT_VOLUME * (1 / 1.5) ** steps)


def setVolume(volume):
    """
    Sets the volume level to the given volume value, which must be a
    number between 0 (silence) and 1.0 (full volume). Notes and beats
    created using `addNote` or `addBeat` will use this volume value.
    """
    global CURRENT_VOLUME

    if not isinstance(volume, (int, float)) or volume < 0 or volume > 1:
        raise ValueError(
            "Volume must be given as a number between 0 and 1 (inclusive)."
        )

    CURRENT_VOLUME = float(volume)


def currentVolume():
    """
    Returns the current volume level, as a floating point number between
    0 (silence) and 1 (full volume).
    """
    return CURRENT_VOLUME


#-----------------#
# Data conversion #
#-----------------#

def stream(signal, start=0, end=None):
    """
    Converts a signal to a stream of samples, starting at t=0, or the
    given start time. This function is an infinite generator for samples
    from the given stream, unless end= is provided, in which case the
    generator is exhausted when time reaches that point.
    """
    t = start
    if end is None:
        while True:
            yield signal(t)
            t += DT
    else:
        while t < end:
            yield signal(t)
            t += DT


# These variables correspond to the three limiter states (see limited_stream)
LIMITER_STATE_UNCOMPRESSED = 0
LIMITER_STATE_COMPRESSING = 1
LIMITER_STATE_RELAXING = 2


def limited_stream(stream, threshold, release_delay, release_duration):
    """
    Returns samples from the given stream with values limited to the
    [-threshold, threshold] range. The limiter remembers the peak value
    observed and compresses at the necessary ratio to clip that value
    ratio for the given release_delay number of frames afterwards, and
    after that the compression ratio scales linearly back down to 1 over
    the given release_duration.
    """
    ratio = 1.0
    frames_since_peak = 0
    frames_since_relax = 0
    peak_value = 0
    peak_ratio = 0
    state = LIMITER_STATE_UNCOMPRESSED
    for sample in stream: # process all of the (perhaps infinite) samples
        sabs = abs(sample)

        # Update our frame counters
        frames_since_peak += 1
        frames_since_relax += 1

        # Figure out whether the sample is in-range, in-compressed-range,
        # or out-of-range.
        if sabs <= threshold:
            # No compression needed, and no adjustments to make
            pass
        elif sabs * ratio <= threshold:
            # An exact re-peak (ratio nudging will leave it < threshold)
            if sabs == peak_value:
                frames_since_peak = 0
        else: # out-of-range sample!
            frames_since_peak = 0
            peak_value = sabs
            peak_ratio = round(threshold / peak_value, 8) - 1e-8
            state = LIMITER_STATE_COMPRESSING
            # We nudge the ratio down ever-so-slightly to ensure that
            # floating point weirdness with multiplication still leaves
            # our result value strictly <= the threshold.
            ratio = peak_ratio

        # Yield one sample at the current ratio
        yield sample * ratio

        # Check for delay-based state transitions
        if (
            state == LIMITER_STATE_COMPRESSING
        and frames_since_peak >= release_delay
        ):
            # Enter relaxation period after release_delay
            frames_since_relax = 0
            state = LIMITER_STATE_RELAXING
        elif (
            state == LIMITER_STATE_RELAXING
        and frames_since_relax >= release_duration
        ):
            # Return to uncompressed state after relax timeout
            ratio = 1.0
            state = LIMITER_STATE_UNCOMPRESSED

        # Update compression ratio during relaxation period
        if state == LIMITER_STATE_RELAXING:
            progress = frames_since_relax / release_duration
            ratio = peak_ratio * (1 - progress) + progress

        # And now the loop continues...


def bytestream(stream):
    """
    Converts a stream into a byte stream with SAMPLE_WIDTH bytes per
    sample. Yields bytes objects of length equal to the sample width.
    """
    limit = 2 ** (8 * SAMPLE_WIDTH - 1) - 1

    for sample in stream:
        quantized = int(sample * limit)
        yield quantized.to_bytes(SAMPLE_WIDTH, byteorder='little', signed=True)


def bytestring(signal, duration, start=0):
    """
    Turns a finite timespan of the given signal into a bytes object. Runs
    from t=start to t=(start + duration), where start defaults to 0.
    """
    return b''.join(
        bytestream(
            limited_stream(
                stream(signal, start=start, end=start + duration),
                1.0,
                DEFAULT_LIMITER_DELAY,
                DEFAULT_LIMITER_RELAX_DURATION,
            )
        )
    )


#--------#
# Tracks #
#--------#

TRACKS = None
"""
The various active tracks. Each track name maps to a dictionary
containing the waveform function for that track and a time value
representing the current end-time of the track. The track dictionary also
has a log that contains a list of tuples which logs each note, rest, or
beat that gets added to the track using addNote, addRest, or addBeat.
Each log entry is a triple recording the time at which the note/rest/beat
begins, the duration of the note/rest/beat, and a string describing the
note/rest/beat. When tracks are mixed, log entries are sorted by start
time, then duration, and then description.
"""


ACTIVE_TRACK = None
"""
The currently-active track. After a reset, this is the track named
'default'.
"""


def setActiveTrack(name):
    """
    Creates a new track with the given name and switches to that track,
    or switches to the existing track with that name if there is one.
    """
    global TRACKS, ACTIVE_TRACK
    if name not in TRACKS:
        TRACKS[name] = { "waveform": silence, "duration": 0, "log": [] }
    ACTIVE_TRACK = name


def resetTracks():
    """
    Completely erases and deletes ALL tracks, and uses `resetState` to
    reset to a clean state.
    """
    global TRACKS, ACTIVE_TRACK
    TRACKS = {
        "default": {
            "waveform": silence,
            "duration": 0,
            "log": []
        }
    }
    ACTIVE_TRACK = "default"
    resetState()


def resetState():
    """
    Resets the current instrument, drum, time, pitch, and volume back to
    their default values. Does not affect track data (see `resetTracks`).
    """
    global CURRENT_INSTRUMENT, CURRENT_DRUM, CURRENT_TIME, CURRENT_PITCH,\
        CURRENT_VOLUME
    # Reset things to defaults
    CURRENT_INSTRUMENT = keyboard
    CURRENT_DRUM = snare
    CURRENT_TIME = 0
    CURRENT_PITCH = A3 # noqa F821
    CURRENT_VOLUME = 0.6


# Reset on import to initialize default track
resetTracks()


def eraseTrack():
    """
    Completely erases the current track, erasing any old contents and
    setting the duration back to zero.
    """
    TRACKS[ACTIVE_TRACK] = { "waveform": silence, "duration": 0, "log": [] }


def addRest(duration):
    """
    Adds a rest at the current time of the given (non-negative) duration.
    This doesn't actually produce or erase any sound, but it can extend
    the duration of the current track which will add silence (that may
    later have notes added on top of it, of course). The rest will also
    be noted in the track log, and the current time is advanced to the
    end of the rest. This function uses `addRestAt` to make the track
    changes it needs to make.
    """
    addRestAt(CURRENT_TIME, duration)
    fastforward(duration)


def addRestAt(startAt, duration):
    """
    Adds a period of silence to the currently active track at a specific
    moment in time. If the 'startAt' argument is the string 'end' instead
    of a non-negative number (in seconds), the rest will be added to the
    end of the track.

    In addition to potentially moving the track's end-time forward, this
    will add a rest entry to the track's log, but it doesn't actually
    change the track's signal, and if notes are added on top of the rest,
    or if the rest is added on top of the notes, those notes will still
    play.

    This function does not use or advance the current time value (see
    `addRest`).
    """
    thisTrack = TRACKS[ACTIVE_TRACK]
    if startAt == "end":
        startAt = thisTrack['duration']

    elif not isinstance(startAt, (int, float)) or startAt < 0:
        raise TypeError(
            "The start time must be a non-negative number or the string"
            " 'end'."
        )

    if not isinstance(duration, (int, float)) or duration < 0:
        raise TypeError("The duration must be a non-negative number.")

    # No need to alter the waveform, which is silent outside of active
    # notes in any case.
    thisTrack['log'].append(
        ( startAt, duration, "a {:0.3g}s rest".format(duration) )
    )
    restEnd = startAt + duration
    thisTrack['duration'] = max(thisTrack['duration'], restEnd)


def addNote(duration):
    """
    Adds a note with the given duration to the current track, and
    advances the current time by that same duration value. The duration
    must be a positive number and is measured in seconds.

    The specific sound used is determined by the current instrument,
    pitch, and volume values (see e.g., `currentInstrumentName`,
    `currentPitchName`, and `currentVolume`). Use `setInstrument`,
    `setPitch`, and/or `setVolume` or related functions like `climbUp` or
    `louder` to adjust these values before calling `addNote`.

    Note that `addSpecificNote` is used to do the heavy lifting here.
    """
    addSpecificNote(
        CURRENT_TIME,
        CURRENT_INSTRUMENT,
        CURRENT_PITCH,
        duration,
        CURRENT_VOLUME
    )
    fastforward(duration)


def addSpecificNote(startAt, instrument, pitch, duration, volume):
    """
    Adds a note at the given moment using the given instrument at the
    given pitch and volume for the given duration to the currently active
    track. The first argument should be a number of seconds, but may also
    be the string "end" to start the note at the end of the current
    track. Note that this function does not affect the current time
    value, and it does not make use of the current pitch, instrument, or
    volume values.

    The second argument must be a function which accepts a pitch, a
    duration, and a volume as parameters, examples include `keyboard` and
    `harmonica`, or it may be the name of such a function in this module
    as a string. Note that pitched instruments should be handled via
    `addNote` instead.
    """
    thisTrack = TRACKS[ACTIVE_TRACK]
    if startAt == "end":
        startAt = thisTrack['duration']
    elif not isinstance(startAt, (int, float)) or startAt < 0:
        raise TypeError(
            "The start time must be a non-negative number or the string 'end'."
        )

    if not isinstance(pitch, (int, float)):
        raise TypeError(
            "The pitch must be a number (you may use the numerical"
          + " constants included in this module like P1 and C4)."
        )

    if not isinstance(duration, (int, float)) or duration <= 0:
        raise TypeError("The duration must be a positive number.")

    if not isinstance(volume, (int, float)) or volume < 0 or volume > 1:
        raise TypeError(
            "The volume must be a number between 0 and 1 (inclusive)."
        )

    if isinstance(instrument, str):
        name = instrument
        try:
            instrument = globals()[instrument]
        except Exception:
            raise TypeError(
                "'{}' is not a valid instrument name.".format(name)
            )
    elif not isinstance(instrument, type(lambda: 0)):
        raise TypeError(
            (
                "The instrument must be an instrument name string or an"
              + " instrument function (got: {})."
            ).format(repr(instrument))
        )

    if instrument.__code__.co_argcount < 3:
        raise TypeError(
            (
                "The instrument function must accept pitch, duration,"
              + " and volume arguments (function '{}' accepts {}"
              + " positional arguments)."
            ).format(instrument.__name__, instrument.__code__.co_argcount)
        )

    signal = instrument(pitch, duration, volume)
    wf = thisTrack['waveform']
    thisTrack['waveform'] = stack(wf, signal, startAt, duration)
    thisTrack['log'].append(
        (
            startAt,
            duration,
            "a {:0.3g}s {} note at {} ({:.0f}% vol)".format(
                duration,
                instrument.__name__,
                pitchName(pitch),
                100 * volume
            )
        )
    )
    noteEnd = startAt + duration
    thisTrack['duration'] = max(thisTrack['duration'], noteEnd)


def addBeat(duration):
    """
    Adds a beat with the given duration to the current track, and
    advances the current time by that same duration value. The duration
    must be a positive number and is measured in seconds.

    The specific sound used is determined by the current drum instrument,
    volume values (see e.g., `currentDrumName` and `currentVolume`). Use
    `setDrum` and/or `setVolume` or related functions like `louder` to
    adjust these values before calling `addBeat`.

    Note that `addSpecificBeat` is used to do the heavy lifting here.
    """
    addSpecificBeat(
        CURRENT_TIME,
        CURRENT_DRUM,
        duration,
        CURRENT_VOLUME
    )
    fastforward(duration)


def addSpecificBeat(startAt, instrument, duration, volume):
    """
    Adds a beat at the given time using the given instrument at the given
    volume for the given duration to the currently active track. The
    first argument should be a number in seconds, or it may be the string
    'end' in which case the beat will be added to the end of the current
    track.

    The second argument must be a function which accepts a duration and a
    volume as parameters, examples include `snare` and `kick`, or it may
    be the name of such a function in this module as a string. Note that
    pitched instruments should be handled via `addNote` instead.
    """
    thisTrack = TRACKS[ACTIVE_TRACK]
    if startAt == "end":
        startAt = thisTrack['duration']
    elif not isinstance(startAt, (int, float)) or startAt < 0:
        raise TypeError(
            "The start time must be a non-negative number or the string 'end'."
        )

    if not isinstance(duration, (int, float)) or duration <= 0:
        raise TypeError("The duration must be a positive number.")

    if isinstance(instrument, str):
        name = instrument
        try:
            instrument = globals()[instrument]
        except Exception:
            raise TypeError(
                "'{}' is not a valid instrument name.".format(name)
            )
    elif not isinstance(instrument, type(lambda: 0)):
        raise TypeError(
            (
                "The instrument must be an instrument name string or an"
              + " instrument function (got: {})."
            ).format(repr(instrument))
        )

    if instrument.__code__.co_argcount < 2:
        raise TypeError(
            (
                "The instrument function must accept duration and volume"
              + " arguments (function '{}' accepts {} positional"
              + " arguments)."
            ).format(instrument.__name__, instrument.__code__.co_argcount)
        )

    signal = instrument(duration, volume)
    wf = thisTrack['waveform']
    thisTrack['waveform'] = stack(wf, signal, startAt, duration)
    thisTrack['log'].append(
        (
            startAt,
            duration,
            "a {:0.3g}s {} beat ({:.0f}% vol)".format(
                duration,
                instrument.__name__,
                100 * volume
            )
        )
    )
    beatEnd = startAt + duration
    thisTrack['duration'] = max(thisTrack['duration'], beatEnd)


def trackDuration():
    """
    Returns the duration of the current track, in seconds.
    """
    track = TRACKS[ACTIVE_TRACK]
    return track['duration']


def mixTracks(track1, track2, newName):
    """
    Creates a new track with the given new name, and mixes the two
    provided tracks into the new track. Note that this may cause
    out-of-range values to occur which will be handled during limiting.

    The name for the new track must not already be used by an existing
    track.
    """
    if newName in TRACKS:
        raise ValueError(
            "Track '{}' already exists: cannot mix tracks.".format(newName)
        )

    if track1 not in TRACKS:
        raise ValueError(
            "Can't mix tracks: no track name '{}'.".format(track1)
        )

    if track2 not in TRACKS:
        raise ValueError(
            "Can't mix tracks: no track name '{}'.".format(track2)
        )

    track1 = TRACKS[track1]
    track2 = TRACKS[track2]

    wf1 = track1['waveform']
    wf2 = track2['waveform']

    TRACKS[newName] = {
        "waveform": mix(wf1, wf2),
        "duration": max(track1['duration'], track2['duration']),
        "log": sorted(track1['log'] + track2['log'])
    }


def renderTrack(track):
    """
    Renders the given track, adding a 'rendered' key that contains a
    tuple of a bytestring with the track data, and a duration value
    indicating how long the render is. If there's an existing render,
    only the part of the track after the end of that will be rendered,
    and this will be added onto what is already there. Accordingly,
    functions that edit existing parts of a track should remove the
    track's 'rendered' entry.

    This function will construct a WaveObject for the track as well if
    the simpleaudio module is available.
    """
    _debug("Rendering track...")
    if 'rendered' in track:
        _debug("  ...incrementally...")
        partial, finishedUntil = track['rendered']
    else:
        _debug("  ...from scratch...")
        partial = b''
        finishedUntil = 0

    trackEnd = track['duration']
    if trackEnd == finishedUntil:
        _debug("  ...nothing new to render.")
        return # no work needs to be done; the existing render is up-to-date

    _debug("  ...rendering from {} to {}...".format(finishedUntil, trackEnd))
    newData = bytestring(
        track['waveform'],
        trackEnd - finishedUntil,
        finishedUntil
    )
    _debug("  ...compiled {} bytes...".format(len(newData)))

    data = partial + newData
    track['rendered'] = (data, trackEnd)
    _debug("  ...stored new render data.")

    # Pre-construct a WaveObject if simpleaudio is available.
    if simpleaudio is not None:
        _debug("Creating wave object...")
        _debug(
            (
                "We have {} bytes of data ({} seconds of audio at {}"
              + " bytes/frame and {} frames/second)."
            ).format(
                len(data),
                round((len(data) / SAMPLE_WIDTH) / SAMPLE_RATE, 3),
                SAMPLE_WIDTH,
                SAMPLE_RATE
            )
        )
        if len(data) > 0:
            track['wave_object'] = simpleaudio.WaveObject(
                data,
                1,
                SAMPLE_WIDTH,
                SAMPLE_RATE
            )
        else:
            track['wave_object'] = None
        _debug("  ...done.")


def saveTrack(target):
    """
    Saves the currently active track in .wav format in the named file.
    Overwrites that file if it already exists!

    If a file-like object is provided instead of a file name string, data
    will be written directly to that object. Any cleanup for a file-like
    object is the responsibility of the caller.
    """
    track = TRACKS[ACTIVE_TRACK]
    renderTrack(track) # make sure render is up-to-date
    rendered = track.get('rendered')
    if rendered is None:
        tdata = b''
    else:
        tdata = rendered[0]

    with wave.open(target, mode='wb') as fout:
        fout.setnchannels(1)
        fout.setsampwidth(SAMPLE_WIDTH)
        fout.setframerate(SAMPLE_RATE)
        fout.writeframes(tdata)


class ZeroLengthTrack:
    """
    Object for representing a 0-duration track. Supports same operations
    as a WaveObject.play() result.
    """
    def wait_done(self):
        """
        Returns immediately, because the track's duration is 0.
        """
        return


def trackDescription():
    """
    Returns a list of strings describing the notes and/or beats in the
    current track. Each entry describes one note or beat. When notes
    overlap, includes their start times, but otherwise just includes an
    entry for each note with the implication that it starts at the end of
    the previous note.
    """
    thisTrack = TRACKS[ACTIVE_TRACK]
    skip = 0
    log = thisTrack["log"]
    result = []
    first = True
    lastSkip = False
    prevEnd = None
    for i, entry in enumerate(log):
        if skip > 0:
            lastSkip = True
            skip -= 1
            continue
        describe = [ entry ]
        start, duration, description = entry
        now = start
        until = start + duration

        # Check for a gap after end of previous entry
        gap = None
        if start != prevEnd and prevEnd is not None:
            gap = start - prevEnd
        prevEnd = until

        offset = 1
        while now < until and i + offset < len(log):
            nextEntry = log[i + offset]
            nextStart, nextDuration, nextDescription = nextEntry
            if nextStart < until: # an overlapping note
                # rests don't alter the "end" time of overlapping stuff
                if not nextDescription.endswith("rest"):
                    until = max(until, nextStart + nextDuration)
                describe.append(nextEntry)
            now = nextStart + nextDuration
            offset += 1

        if len(describe) == 1:
            if first:
                first = False
                result.append(describe[0][2])
            elif lastSkip:
                lastSkip = False
                result.append(
                    "at {:.3g}s {}".format(
                        describe[0][0],
                        describe[0][2]
                    )
                )
            elif gap is not None:
                result.append("and a {:0.3g}s rest".format(gap))
                result.append("and " + describe[0][2])
            else:
                result.append("and " + describe[0][2])
        else:
            first = False
            skip = len(describe) - 1
            if gap is not None:
                result.append("and a {:0.3g}s rest".format(gap))
            for start, duration, description in describe:
                if not description.endswith("rest"):
                    result.append(
                        "at {:.3g}s {}".format(start, description)
                    )
                # overlapping rests are not described

    return result


def printTrack():
    """
    Prints out the description of the current track (see
    `trackDescription`).
    """
    for entry in trackDescription():
        print(entry)


def prepareTrack():
    """
    Force the current track to be rendered, so that playback with
    playTrack can start immediately instead of needing to render the
    track which may take some time.
    """
    renderTrack(TRACKS[ACTIVE_TRACK])


def playTrack(wait=True):
    """
    Plays the currently active track. By default, this also waits until
    the track is done playing, but if wait is set to False, playback is
    asynchronous and starts as soon as the track is finished rendering.
    This function only works if the `simpleaudio` package is available,
    and raises a NotImplementedError if it isn't.

    When playing asynchronously, it returns a `WaveObject` instance,
    which has a `wait_done` method that can be used to wait until the
    playback is finished. When playing synchronously, it returns None.

    Note that there may be some processing delay before the track starts
    playing; call `prepareTrack` beforehand to get the processing out of
    the way earlier.
    """
    if simpleaudio is None:
        raise NotImplementedError(
            "You must have the `simpleaudio` package installed in order"
          + " to play sounds.\n"
          + "You should be able to use your package manager (or maybe"
          + " `pip`) to install the `simpleaudio` package."
        )

    track = TRACKS[ACTIVE_TRACK]
    renderTrack(track) # make sure render is up-to-date
    wo = track.get('wave_object')
    if wo is None:
        result = ZeroLengthTrack()
    else:
        result = wo.play()

    if wait:
        result.wait_done()
        return None
    else:
        return result


#---------#
# Testing #
#---------#

def test_name():
    """
    A test function that tests the `currentPitchName` function.
    """
    failed = False
    for pname in ["A4", "Ab3", "C0", "B9"]:
        pitchValue = globals()[pname]
        result = pitchName(pitchValue)
        if result != pname:
            print(
                "FAILED: Set pitch to '{}' but name was '{}'."
                .format(pname, result)
            )
            failed = True
        assert result == pname

        above = pitchName(pitchValue + 0.05)
        fl, hz, just, ab, result = above.split()
        if (
            float(fl) != round(pitchValue + 0.05, 2)
         or hz != "Hz"
         or just != "(just"
         or ab != "above"
         or result != pname + ")"
        ):
            print(
                "FAILED: Set pitch to just above '{}' but name was '{}'."
                .format(pname, above)
            )
            failed = True
        assert float(fl) == round(pitchValue + 0.05, 2)
        assert hz == "Hz"
        assert just == "(just"
        assert ab == "above"
        assert result == pname + ")"

        below = pitchName(pitchValue - 0.05)
        fl, hz, just, bl, result = below.split()
        if (
            float(fl) != round(pitchValue - 0.05, 2)
         or hz != "Hz"
         or just != "(just"
         or bl != "below"
         or result != pname + ")"
        ):
            print(
                "FAILED: Set pitch to just below '{}' but name was '{}'."
                .format(pname, below)
            )
            failed = True
        assert float(fl) == round(pitchValue - 0.05, 2)
        assert hz == "Hz"
        assert just == "(just"
        assert bl == "below"
        assert result == pname + ")"
    high = B9 + 1000 # noqa F821
    result = pitchName(high)
    fl, hz = result.split()
    if float(fl) != round(high, 2) or hz != "Hz":
        print(
            "FAILED: Set pitch to '{:.2f}' but name was '{}'."
            .format(high, result)
        )
        failed = True
    assert float(fl) == round(high, 2)
    assert hz == "Hz"

    if not failed:
        print("All tests passed.")
    assert True


def test_scales():
    """
    A test function that produces a few different kinds of scales.
    """
    eraseTrack()
    setInstrument(keyboard)

    for f, st, n in [
        ("C", "Major", 8),
        ("Ab", "Minor-Natural", 8),
        ("E", "Minor-Melodic", 8),
        ("Fs", "Major", 8),
        ("C", "Pentatonic-Major", 6),
        ("A", "Pentatonic-Yo", 6),
        ("A", "Pentatonic-In", 6),
    ]:
        setFundamental(f)
        setScaleType(st)
        setPitch(currentFundamental())
        climbUp(n * 3)
        p = currentPitch()
        for i in range(n):
            addNote(0.05)
            climbUp()
        for i in range(n):
            climbDown()
            addNote(0.05)
        addRest(0.25)
        assert currentPitch() == p

    printTrack()
    playTrack()


def test_tune():
    """
    A test function that produces a drums-and-keyboard two-track tune,
    prints the log, and plays it.
    """
    eraseTrack()
    setActiveTrack("drums")
    eraseTrack()
    setDrum(snare)

    for i in range(3):
        addBeat(0.1)
        addRest(0.1)
        addBeat(0.1)
        addRest(0.1)
        setDrum(kick)
        addBeat(0.2)
        setDrum(snare)
        addBeat(0.1)
        addRest(0.1)

    for i in range(8):
        addBeat(0.1)

    for i in range(5):
        addBeat(0.1)
        addRest(0.1)
        addRest(0.2)
        setDrum(kick)
        addBeat(0.2)
        setDrum(snare)
        addBeat(0.1)
        addRest(0.1)

    addRest(0.2)
    addBeat(0.2)

    setActiveTrack("tones")
    eraseTrack()
    setInstrument(keyboard)
    setTime(0) # back to the beginning

    addRest(0.8 * 4) # wait for drums

    #for freq in (C4, D4, E4, G4, A4, C5, A4, G4, E4, D4, C4): # noqa F821
    for freq in (P4, P5, P6, P7, P8, P9, P8, P7, P6, P5, P4): # noqa F821
        setPitch(freq)
        addNote(0.2)
        addRest(0.2)

    mixTracks("tones", "drums", "mixed")

    setActiveTrack("mixed")
    printTrack()
    playTrack()


def test_poly():
    """
    A simple test for polyphonic music in a single track, relying on the
    limiter to handle compression. Also establishes a gradual crescendo
    followed by a diminuendo.
    """
    eraseTrack()
    setInstrument(keyboard)
    setVolume(0.1)
    chords = ((P3, P4), (P3, P5), (P4, P6), (P6, P7), (P7, P8)) # noqa F821
    for lower, higher in chords:
        louder()

        setPitch(lower)
        addNote(0.3)
        rewind(0.3)

        setPitch(higher)
        addNote(0.3)
        rewind(0.1)

    for lower, higher in chords[-2::-1]:
        quieter()

        setPitch(lower)
        addNote(0.3)
        rewind(0.3)

        setPitch(higher)
        addNote(0.3)
        rewind(0.1)

    printTrack()
    playTrack()


def test_limit():
    """
    A test designed to exercise the limiter.
    """
    eraseTrack()
    setInstrument(keyboard)
    setPitch(P5) # noqa F821
    setVolume(1.0)

    addNote(0.5)
    rewind(0.5)
    addNote(0.5)
    rewind(0.5)
    addNote(0.5)

    addRest(0.25)

    addNote(0.5)
    rewind(0.5)
    addNote(0.5)

    addRest(0.25)

    addNote(0.5)

    printTrack()
    playTrack()


if __name__ == "__main__":
    #test_name()
    #test_tune()
    #test_scales()
    test_poly()
    #test_limit()
