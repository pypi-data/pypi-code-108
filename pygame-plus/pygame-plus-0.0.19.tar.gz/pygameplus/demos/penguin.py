# Copyright 2021 Casey Devet
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from importlib import resources
from pygameplus import *

# Use this variable to adjust the size of the screen and its contents
SIZE_MULTIPLIER = 1

# Set up the screen
screen_width = 1280 * SIZE_MULTIPLIER
screen_height = 720 * SIZE_MULTIPLIER
screen = Screen(screen_width, screen_height, "PyGame Plus Penguin")

# Lists to hold the background sprites
left_backgrounds = []
right_backgrounds = []

# The default speed of each background layer when moving (in pixels/frame)
background_speeds = [0, 0, 0.1875, 0.375, 0.1875, 0.375, 0.5, 2]
background_speeds = [SIZE_MULTIPLIER * x for x in background_speeds]

# Dictionary to hold the penguin images
penguin_images = {}

# The penguin sprite (it currently doesn't have a picture)
penguin = Sprite()

# Function that ends the program
def quit ():
    stop_event_loop()

screen.on_key_press(quit, "escape")

# Function that makes the penguin stand still
def stand ():
    penguin.state = "stand"
    penguin.picture = penguin_images["stand"]

    # Remove animation from penguin and background
    penguin.on_update(None)
    for index in range(4, 8):
        left_backgrounds[index].on_update(None)
        right_backgrounds[index].on_update(None)

# Function that moves a left background sprite left on update
def move_left_background_left (sprite):
    sprite.x -= sprite.speed
    if sprite.x <= -screen_width:
        sprite.x += screen_width

# Function that moves a right background sprite left on update
def move_right_background_left (sprite):
    sprite.x -= sprite.speed
    if sprite.x < 0:
        sprite.x += screen_width

# Function that moves a left background sprite right on update
def move_left_background_right (sprite):
    sprite.x += sprite.speed
    if sprite.x > 0:
        sprite.x -= screen_width

# Function that moves a right background sprite right on update
def move_right_background_right (sprite):
    sprite.x += sprite.speed
    if sprite.x >= screen_width:
        sprite.x -= screen_width

# Function that animates the penguin walking by changing images
def animate_penguin_walk ():
    # Every 10 frames, change the picture
    new_state = "walk" + str(penguin.animate_count // 10 % 4)
    if penguin.state != new_state:
        penguin.state = new_state
        penguin.picture = penguin_images[new_state]
    penguin.animate_count += 1

# Function that starts the penguin walking
def start_walking ():
    penguin.state = "walk0"
    penguin.picture = penguin_images["walk0"]

    # Turn on animation for the penguin
    penguin.animate_count = 0
    penguin.on_update(animate_penguin_walk)

    # Turn on animation for the background
    for index in range(4, 8):
        left_backgrounds[index].speed = background_speeds[index]
        right_backgrounds[index].speed = background_speeds[index]
        if penguin.flipped_horizontally:
            left_backgrounds[index].on_update(move_left_background_right)
            right_backgrounds[index].on_update(move_right_background_right)
        else:
            left_backgrounds[index].on_update(move_left_background_left)
            right_backgrounds[index].on_update(move_right_background_left)

# Function that animates the penguin slide
def animate_penguin_slide ():
    # For 400 frames, slide but gradually slow down
    if penguin.animate_count < 400:
        multiplier = (1 - penguin.animate_count / 400) ** 0.5
        for index in range(4, 8):
            left_backgrounds[index].speed = multiplier * background_speeds[index]
            right_backgrounds[index].speed = multiplier * background_speeds[index]
        penguin.animate_count += 1

    # After 400 frames, end the slide by removing animations
    else:
        for index in range(4, 8):
            left_backgrounds[index].on_update(None)
            right_backgrounds[index].on_update(None)
        penguin.on_update(None)

# Function that starts the penguin sliding
def start_sliding ():
    penguin.state = "slide"
    penguin.picture = penguin_images["slide"]

    # Turn on animation for the penguin
    penguin.animate_count = 0
    penguin.on_update(animate_penguin_slide)

# Function that animates the penguin jumping
def animate_penguin_jump ():
    # Change the penguin's height using this quadratic function
    penguin.y = (-0.0512 * penguin.animate_count * (penguin.animate_count - 100) - 200) * SIZE_MULTIPLIER;

    # If the jump is done, determine what should happen next and do it.
    if penguin.animate_count >= 100:
        if key_down["down"]:
            start_sliding()
        elif key_down["left"] or key_down["right"]:
            start_walking()
        else:
            stand()

    # If the jump is still going, determine the correct picture to show
    else:
        if key_down["down"]:
            new_state = "jumpslide"
        elif penguin.animate_count >= 90:
            new_state = "jump2"
        elif penguin.animate_count >= 10:
            new_state = "jump1"
        else:
            new_state = "jump0"
        if new_state != penguin.state:
            penguin.state = new_state
            penguin.picture = penguin_images[new_state]
        penguin.animate_count += 1

# Function that starts the penguin jumping
def start_jumping ():
    penguin.state = "jump0"
    penguin.picture = penguin_images["jump0"]

    # Turn on animation for the penguin
    penguin.animate_count = 0
    penguin.on_update(animate_penguin_jump)

# Keeps track whether or not the arrow keys are down
key_down = {"left": False, "right": False, "up": False, "down": False}

# Function called when the left or right arrows are pressed
def left_or_right_pressed (key):
    key_down[key] = True

    # Flip the original picture if the left arrow is down
    penguin.flipped_horizontally = key == "left"

    # Only walk if currently standing or walking
    if penguin.state == "stand" or penguin.state.startswith("walk"):
        start_walking()

screen.on_key_press(left_or_right_pressed, ["right", "left"])

# Function called when the left or right arrows are released
def left_or_right_released (key):
    key_down[key] = False

    # If the other horizontal arrow is down, reverse direction
    if key_down["left"]:
        penguin.flipped_horizontally = True
    elif key_down["right"]:
        penguin.flipped_horizontally = False

    # Determine the next state
    if penguin.state.startswith("walk"):
        if key_down["left"] or key_down["right"]:
            start_walking()
        else:
            stand()

screen.on_key_release(left_or_right_released, ["right", "left"])

# Function called when the up arrow is pressed
def up_pressed ():
    key_down["up"] = True

    # Only jump if currently standing or walking
    if penguin.state == "stand" or penguin.state.startswith("walk"):
        start_jumping()

screen.on_key_press(up_pressed, "up")

# Function called when the up arrow is released
def up_released ():
    key_down["up"] = False

screen.on_key_release(up_released, "up")

# Function called when the down arrow is pressed
def start_slide ():
    key_down["down"] = True

    # Only slide if not currently jumping
    if not penguin.state.startswith("jump"):
        start_sliding()

screen.on_key_press(start_slide, "down")

# Function called the the down arrow is released
def down_released ():
    key_down["down"] = False

    # Determine which state is next
    if not penguin.state.startswith("jump"):
        if key_down["left"] or key_down["right"]:
            start_walking()
        else:
            stand()

screen.on_key_release(down_released, "down")

# Function to start the program
def main ():
    # Open the screen
    screen.open()

    # Load the background images
    for i in range(1, 9):
        with resources.path("pygameplus.demos.img", f"snow{i}.png") as image_path:
            picture = load_picture(image_path)

        # Create the left image
        left_background = Sprite(picture)
        left_background.scale_factor = SIZE_MULTIPLIER * 2 / 3
        left_background.speed = background_speeds[i - 1]
        # Only the clouds move at the beginning
        if i == 3 or i == 4:
            left_background.on_update(move_left_background_left)
        left_backgrounds.append(left_background)
        screen.add(left_background)

        # Create the right image
        right_background = Sprite(picture)
        right_background.scale_factor = SIZE_MULTIPLIER * 2 / 3
        right_background.x = screen_width
        right_background.speed = background_speeds[i - 1]
        # Only the clouds move at the beginning
        if i == 3 or i == 4:
            right_background.on_update(move_right_background_left)
        right_backgrounds.append(right_background)
        screen.add(right_background)

    # Load the penguin images
    penguin_states = ["stand", "walk0", "walk1", "walk2", "walk3", "slide",
                      "jump0", "jump1", "jump2", "jumpslide"]
    for state in penguin_states:
        with resources.path("pygameplus.demos.img", f"penguin_{state}.png") as image_path:
            penguin_images[state] = load_picture(image_path)

    # Set the penguins initial picture
    penguin.state = "stand"
    penguin.picture = penguin_images["stand"]

    # Config the penguin
    penguin.y = -200 * SIZE_MULTIPLIER
    penguin.scale_factor = SIZE_MULTIPLIER
    screen.add(penguin)

    screen.update()

    # Start the event loop
    start_event_loop(60)


# call the "main" function if running this script
if __name__ == "__main__":
    main()
