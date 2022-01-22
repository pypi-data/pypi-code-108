# Programmer: Mr. Devet
# Date: June 11, 2021
# Purpose: Illustrate new features of the superturtle module

from importlib import resources
from pygameplus import *

def main ():
    global screen, ship

    # Set up the screen
    screen = Screen(640, 360, "PyGame Plus")
    screen.open()

    # We can use image files that are not GIFs
    with resources.path("pygameplus.demos.img", "space.jpg") as image_path:
        screen.background_image = image_path

    # # Create a "ship" turtle
    with resources.path("pygameplus.demos.img", "ship.png") as image_path:
        ship_still_image = load_picture(image_path)
    with resources.path("pygameplus.demos.img", "ship2.png") as image_path:
        ship_moving_image = load_picture(image_path)

    ship = Painter(ship_still_image)
    screen.add(ship)

    # We can scale the image of a turtle.  In this example, 
    # the ship's image is scaled by a factor of 0.1 (or 10%)
    ship.smooth = True
    ship.scale_factor = 0.1

    # The image for a turtle can be rotated.  This function
    # sets that the image should rotate whenever the turtle's
    # heading changes
    ship.rotates = True
    ship.anchor = 0, -125

    # Tilt the image so that the ship points in the same direction
    # as the heading
    ship.tilt = -90

    ship.line_width = 5
    ship.fill_color = "red"
    ship.line_color = "white"
    ship.fill_as_moving = True

    # Function that ends the program
    def esc ():
        stop_event_loop()

    # Function that checks if the ship is off the screen and
    # moves it to the other side
    def wrap_around ():
        if ship.x >= 345:
            ship.x = -345
        elif ship.x <= -345:
            ship.x = 345
        if ship.y >= 205:
            ship.y = -205
        elif ship.y <= -205:
            ship.y = 205

    # Function that moves the ship forward
    def on_up ():
        ship.move_forward(2)
        wrap_around()

    # Function that turns the ship left
    def on_left ():
        ship.turn_left(5)

    # Function that turns the ship right
    def on_right ():
        ship.turn_right(5)

    # Function that changes the ship to the moving image
    def start_ship ():
        ship.picture = ship_moving_image

    # Function that changes the ship to the stopped image
    def stop_ship ():
        ship.picture = ship_still_image

    # Function that starts and stops drawing
    def toggle_drawing ():
        ship.filling = not ship.filling
        ship.drawing = not ship.drawing

    def draw_dot ():
        ship.dot(color="gold")

    def draw_stamp ():
        ship.stamp()

    # Bind the functions to keys
    screen.on_key_hold(on_up, "up")
    screen.on_key_hold(on_left, "left")
    screen.on_key_hold(on_right, "right")
    screen.on_key_press(start_ship, "up")
    screen.on_key_release(stop_ship, "up")
    screen.on_key_hold(esc, "escape")
    screen.on_key_press(toggle_drawing, "space")
    screen.on_key_press(draw_dot, "d")
    screen.on_key_press(draw_stamp, "s")

    # Function that moves the ship on dragging it
    def on_drag (x, y):
        ship.position = (x, y)

    # When the user drags the ship it moves
    ship.on_drag(on_drag)

    # Create a "ufo" turtle
    with resources.path("pygameplus.demos.img", "ufo.png") as image_path:
        ufo = Sprite(image_path)
    screen.add(ufo)
    ufo.smooth = True
    ufo.scale_factor = 0.25
    ufo.position = (0, 100)
    ufo.opacity = 0.5

    # Function that moves the ufo forward
    def move_ufo ():
        ufo.move_forward(1)
        if ufo.x >= 332:
            ufo.x = -332
        if ship.is_touching(ufo, method="mask"):
            ship.position = (0, 0)

    ufo.on_update(move_ufo)

    # # Create a turtle to write text to the screen
    writer = Painter()
    screen.add(writer)
    writer.line_width = 5
    writer.line_color = "gold"
    writer.fill_color = (255, 215, 0, 63)
    writer.position = (-250, -110)
    writer.begin_line()
    writer.begin_fill()
    writer.walk_path([(-250, -170), (250, -170), (250, -110), (-250, -110)])
    writer.end_fill()
    writer.end_line()
    writer.position = (0, -140)
    with resources.path("pygameplus.demos.fonts", "Freedom.ttf") as font_path:
        writer.write("Welcome to Space", font=font_path, size=36)

    screen.update()

    # Start the event loop
    start_event_loop(50)


# call the "main" function if running this script
if __name__ == "__main__":
    main()
