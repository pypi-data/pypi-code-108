"""
Names: Peter Mawhorter
Date: 2021-8-28
Purpose: Simple demonstration of wavesynth module.
"""

from wavesynth import *


def arpeggio(startPitch, noteDuration):
    """
    Adds 5 notes to the current track, starting at the given start pitch
    and moving up 4 and then 3 half-steps, and then back down again. Each
    note will have the given duration.
    """
    setPitch(startPitch)
    addNote(noteDuration)
    halfStepUp(4)
    addNote(noteDuration)
    halfStepUp(3)
    addNote(noteDuration)
    halfStepDown(3)
    addNote(noteDuration)
    halfStepDown(4)
    addNote(noteDuration)
