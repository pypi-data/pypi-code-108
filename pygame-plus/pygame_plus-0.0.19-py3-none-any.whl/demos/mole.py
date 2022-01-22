
import code
from importlib import resources
from pygameplus import *
from random import *

def main ():
    ### START SCREEN

    # Create the start screen
    start_screen = Screen(640, 360, "Whack-A-Mole")
    start_screen.background_color = "white"
    with resources.path("pygameplus.demos.img", "mole.png") as image_path:
        mole_image = image_path
    start_screen.background_image = mole_image
    start_screen.open()
    
    start_painter = Painter()
    start_painter.position = (0, -80)
    start_screen.add(start_painter)
    start_painter.write("Whack-A-Mole", size=36, color="white")
    start_painter.position = (0, -160)
    start_painter.write("Hit any key to continue")
    
    def open_main_screen ():
        screen.open()
        music_stream.play(loops=-1)
    
    start_screen.on_key_press(open_main_screen)
    
    
    ### MAIN SCREEN
    
    # Creating a screen
    screen = Screen(640, 360, "Whack-A-Mole")
    screen.background_color = "lightgreen"

    # Load the background music
    with resources.path("pygameplus.demos.audio", "hampster-march.mp3") as audio_path:
        music_stream.load(audio_path)
    
    # Create a POW sprite
    with resources.path("pygameplus.demos.img", "pow.png") as image_path:
        pow_image = image_path
    pow_flash = Sprite(pow_image)
    pow_flash.scale_factor = 0.6
    
    # Function that moves the mole to a random location 
    # on the screen
    def move_mole ():
        pow_flash.kill()
        mole.x = randint(-320, 320)
        mole.y = randint(-180, 180)
    
    # Create a mole sprite
    mole = Sprite(mole_image)
    mole.scale_factor = 0.2
    move_mole()
    screen.add(mole)
    
    # Start a timer that moves the mole every 2 seconds
    screen.on_timer(move_mole, 2000, repeat=True)
    
    # Create a mallet sprite
    with resources.path("pygameplus.demos.img", "mallet.png") as image_path:
        mallet_image = image_path
    mallet = Sprite(mallet_image)
    mallet.rotates = True
    mallet.scale_factor = 0.4
    screen.add(mallet, layer=1)
    
    # Function that moves the mallet with the mouse
    def move_mallet (x, y):
        mallet.x = x + 10
        mallet.y = y + 30
    
    # Bind the function to mouse movement on the screen.
    screen.on_mouse_move(move_mallet)

    # Load the sound effects
    with resources.path("pygameplus.demos.audio", "whack-mole.mp3") as audio_path:
        hit_sound = Sound(audio_path)
    with resources.path("pygameplus.demos.audio", "whack-wood.mp3") as audio_path:
        miss_sound = Sound(audio_path)
    
    # Function that whacks the mallet when the mouse is
    # clicked
    def whack_mallet (pos):
        miss_sound.play()
        mallet.turn_left(60)
    
    # Bind the function to mouse clicks
    screen.on_click(whack_mallet)
    
    # Function that reverts the mallet to its original
    # state
    def revert_mallet ():
        mallet.turn_right(60)
    
    # Bind the function to mouse releases
    screen.on_release(revert_mallet)
    
    # Function that pops up the POW when the mole
    # is hit
    def mole_hit (pos):
        hit_sound.play()
        pow_flash.position = pos
        screen.add(pow_flash)
    
    # Bind the function to clicks on the mole
    mole.on_click(mole_hit, method="mask")

    def pause_game ():
        pause_screen.open()
        music_stream.pause()

    screen.on_key_press(pause_game, "space")
    
    
    ### PAUSE SCREEN
    
    # Create the start screen
    pause_screen = Screen(640, 360, "Whack-A-Mole")
    pause_screen.background_color = "black"
    
    pause_painter = Painter()
    pause_screen.add(pause_painter)
    pause_painter.position = (0, 0)
    pause_painter.write("Paused", size=72, color="white")
    pause_painter.position = (0, -160)
    pause_painter.write("Hit space to resume the game", color="white")

    def resume_game ():
        screen.open()
        music_stream.unpause()
        move_mole()
        screen.on_timer(move_mole, 2000, repeat=True)
    
    pause_screen.on_key_press(resume_game, "space")
    
    
    main_vars = locals()

    def interact ():
        code.interact(local=main_vars)

    screen.on_key_press(interact, "escape")
    
    
    # Event loop
    start_event_loop()


# call the "main" function if running this script
if __name__ == "__main__":
    main()