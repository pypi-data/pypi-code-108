import time
from zumi.protocol import Note


def calibrated_sound(zumi):
    tempo = 60
    zumi.play_note(41, tempo)
    zumi.play_note(43, tempo)
    zumi.play_note(45, tempo)


def happy_sound(zumi):
    time.sleep(1)
    tempo = 75
    zumi.play_note(Note.C5, tempo)
    zumi.play_note(Note.G5, tempo)
    zumi.play_note(Note.E5, tempo)
    time.sleep(0.5)


def try_calibrate_sound(zumi):
    for i in range(2):
        tempo = 75
        zumi.play_note(Note.G5, tempo)
        time.sleep(0.1)
        zumi.play_note(Note.G5, tempo)
        time.sleep(0.1)
        zumi.play_note(Note.D6, tempo)
        time.sleep(0.1)
        zumi.play_note(Note.D6, tempo)
        time.sleep(1.5)


def celebrate_sound(zumi):
    time.sleep(.25)
    zumi.play_note(48, 100)
    time.sleep(.005)
    zumi.play_note(52, 100)
    time.sleep(.005)
    zumi.play_note(55, 100)
    time.sleep(.005)
    zumi.play_note(55, 100)
    time.sleep(.20)
    zumi.play_note(52, 125)
    time.sleep(.005)
    zumi.play_note(55, 125)


def wake_up_sound(zumi):
    note = 36
    tempo = 100
    zumi.play_note(note, tempo + 20)
    zumi.play_note(note, tempo)
    time.sleep(0.10)
    zumi.play_note(note + 5, tempo)
    time.sleep(0.1)
    zumi.play_note(note + 5, tempo)
    time.sleep(0.05)
    zumi.play_note(note + 7, tempo)
    time.sleep(0.15)
    zumi.play_note(note + 12, tempo)
