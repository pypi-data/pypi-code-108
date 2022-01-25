"""
Names: Peter Mawhorter
Date: 2021-8-28
Purpose: Tests for simple demonstration of wavesynth module.
"""

# Tests using printTrack
import optimism as opt

import arpeggio

import wavesynth

m = opt.testFunction(wavesynth.printTrack)

arpeggio.arpeggio(wavesynth.C4, 0.5)
m.case().expectOutputLines(
    "a 0.5s keyboard note at C4",
    "and a 0.5s keyboard note at E4",
    "and a 0.5s keyboard note at G4",
    "and a 0.5s keyboard note at E4",
    "and a 0.5s keyboard note at C4",
)


wavesynth.eraseTrack()

arpeggio.arpeggio(wavesynth.B3, 0.3)
m.case().expectOutputLines(
    "a 0.3s keyboard note at B3",
    "and a 0.3s keyboard note at Eb4",
    "and a 0.3s keyboard note at Gb4",
    "and a 0.3s keyboard note at Eb4",
    "and a 0.5s keyboard note at B3",
)
