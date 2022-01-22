# Programmer: Mr. Devet
# Date: June 11, 2021
# Purpose: Illustrate new features of the pygameplus.turtle module

import code
from pygameplus import Screen, start_event_loop
from pygameplus.turtle import *

def main ():
    # Set up the screen
    screen = Screen(640, 360, "PyGame Plus")
    screen.open()

    # Create a turtle
    michaelangelo = Turtle()
    screen.add(michaelangelo)

    michaelangelo.begin_line()
    michaelangelo.line_color = "blue"
    michaelangelo.line_width = 5

    michaelangelo.move_forward(99)
    michaelangelo.turn_left(90)

    michaelangelo.speed = 480
    michaelangelo.move_forward(99)
    michaelangelo.turn_left(90)

    michaelangelo.speed = 60
    michaelangelo.animate = False
    michaelangelo.move_forward(99)
    michaelangelo.turn_left(90)
    michaelangelo.move_forward(99)
    michaelangelo.turn_left(180)

    michaelangelo.animate = True

    michaelangelo.fill_color = "red"
    michaelangelo.begin_fill()
    michaelangelo.circle(50)
    michaelangelo.end_fill()

    main_vars = locals()
    main_vars["ma"] = michaelangelo

    def interact ():
        code.interact(local=main_vars)

    screen.on_key_press(interact, "escape")

    start_event_loop()


# call the "main" function if running this script
if __name__ == "__main__":
    main()
