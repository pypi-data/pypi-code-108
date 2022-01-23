import curses, random, time, sys

VERSION = "0.0.1"

SNAKE_BODY = ""
BORDER = "█"
FOOD = "■"
PADDING = 0

BORDER_LOOP = False
SLEEP_SECONDS = 0.1

score = 0


def game_over(scr: curses.window):
    height, width = scr.getmaxyx()
    scr.timeout(-1)
    scr.insstr(
        0,
        0,
        "  GAME OVER  | Score: " + str(score) + (" " * width),
        curses.color_pair(2),
    )
    scr.refresh()
    while True:
        time.sleep(9999999)


def pause_game(scr: curses.window):
    scr.timeout(-1)
    height, width = scr.getmaxyx()
    scr.move(height - 1, 0)
    scr.deleteln()
    scr.insstr(
        height - 1, 0, " PAUSED | Continue(p)" + (" " * width), curses.color_pair(2)
    )
    inp = scr.getch()

    scr.timeout(0)


def snake(scr: curses.window):
    curses.cbreak()
    curses.use_default_colors()
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_GREEN, -1)
    curses.curs_set(0)
    curses.noecho()
    scr.timeout(0)

    height, width = scr.getmaxyx()
    body = [[5, 5]]  # x and y position of snake's body, 1st element is head
    direction = "right"
    food = [
        random.randint(1 + PADDING, width - 2 - PADDING),
        random.randint(1 + PADDING, height - 2 - PADDING),
    ]  # food's x and y position
    global score

    while True:
        scr.clear()

        ## draw borders
        scr.addstr(0, 0, BORDER * width)
        scr.insstr(height - 1, 0, BORDER * width)
        for y_index in range(height):
            scr.insstr(y_index, 0, BORDER)
            scr.insstr(y_index, width - 1, BORDER)

        ## score text
        score_text = " Score: " + str(score)
        scr.insstr(0, 0, score_text, curses.color_pair(2))

        ## bottom quit text
        scr.insstr(height - 1, 0, "(Ctrl+c to quit)", curses.color_pair(2))

        ## get input
        inp = scr.getch()
        if inp == curses.KEY_RIGHT and not direction == "left":
            direction = "right"
        elif inp == curses.KEY_LEFT and not direction == "right":
            direction = "left"
        elif inp == curses.KEY_UP and not direction == "down":
            direction = "up"
        elif inp == curses.KEY_DOWN and not direction == "up":
            direction = "down"

        ## update body parts' position (move)
        for body_index in range(len(body) - 1, 0, -1):
            body[body_index] = body[body_index - 1][:]

        ## move head
        if direction == "right":
            body[0][0] += 1
        elif direction == "left":
            body[0][0] -= 1
        elif direction == "up":
            body[0][1] -= 1
        elif direction == "down":
            body[0][1] += 1

        corners = ["║", "╔", "═", "╗", "╝", "╚", "╬"]
        corners = ["┃", "┏", "━", "┓", "┛", "┗", "╋"]

        ## draw snake
        for i, v in enumerate(body):
            scr.delch(v[1], v[0])
            if not SNAKE_BODY:
                if i == 0:
                    scr.insstr(v[1], v[0], corners[-1])
                elif i + 1 < len(body):
                    next_part = body[i + 1]  # next body part
                    prev_part = body[i - 1]  # previous body part
                    if prev_part[0] == v[0]:
                        if prev_part[1] > v[1]:
                            if next_part[0] == v[0]:
                                scr.insstr(v[1], v[0], corners[0])
                            elif next_part[0] > v[0]:
                                scr.insstr(v[1], v[0], corners[1])
                            elif next_part[0] < v[0]:
                                scr.insstr(v[1], v[0], corners[3])
                        elif prev_part[1] < v[1]:
                            if next_part[0] == v[0]:
                                scr.insstr(v[1], v[0], corners[0])
                            elif next_part[0] > v[0]:
                                scr.insstr(v[1], v[0], corners[5])
                            elif next_part[0] < v[0]:
                                scr.insstr(v[1], v[0], corners[4])

                    elif prev_part[1] == v[1]:
                        if prev_part[0] < v[0]:
                            if next_part[1] == v[1]:
                                scr.insstr(v[1], v[0], corners[2])
                            elif next_part[1] < v[1]:
                                scr.insstr(v[1], v[0], corners[4])
                            elif next_part[1] > v[1]:
                                scr.insstr(v[1], v[0], corners[3])
                        elif prev_part[0] > v[0]:
                            if next_part[1] == v[1]:
                                scr.insstr(v[1], v[0], corners[2])
                            elif next_part[1] > v[1]:
                                scr.insstr(v[1], v[0], corners[1])
                            elif next_part[1] < v[1]:
                                scr.insstr(v[1], v[0], corners[5])

                else:
                    if body[i - 1][1] == v[1]:
                        if body[i - 1][0] < v[0]:
                            scr.insstr(v[1], v[0], "╾")
                        else:
                            scr.insstr(v[1], v[0], "╼")
                    else:
                        if body[i - 1][1] < v[1]:
                            scr.insstr(v[1], v[0], "╿")
                        else:
                            scr.insstr(v[1], v[0], "╽")

            else:
                scr.insstr(v[1], v[0], SNAKE_BODY)

        ## check collisions
        # it's body
        if body[0] in body[1:]:
            game_over(scr)
        # borders
        elif body[0][0] in [0, width - 1] or body[0][1] in [0, height - 1]:
            if BORDER_LOOP:
                scr.delch(body[0][1], body[0][0])
                scr.insstr(body[0][1], body[0][0], BORDER)

                if body[0][0] == 0:
                    body[0][0] = width - 2
                elif body[0][0] == width - 1:
                    body[0][0] = 1
                elif body[0][1] == 0:
                    body[0][1] = height - 2
                elif body[0][1] == height - 1:
                    body[0][1] = 1

                scr.delch(body[0][1], body[0][0])
                scr.insstr(body[0][1], body[0][0], SNAKE_BODY)
            else:
                game_over(scr)
        # food
        elif body[0] == food:
            score += 1
            body += [body[-1]]

            while food in body:
                food = [
                    random.randint(1 + PADDING, width - 2 - PADDING),
                    random.randint(1 + PADDING, height - 2 - PADDING),
                ]

        # draw food
        scr.delch(food[1], food[0])
        scr.insstr(food[1], food[0], FOOD, curses.color_pair(3))

        scr.refresh()

        if inp == ord("p"):
            pause_game(scr)

        sleep_sec = SLEEP_SECONDS
        time.sleep(sleep_sec)


HELP_TEXT = """psnake
------
-v --version : show version
-h --help    : show this help text

Game settings
-l           : allow looping
-p<int>      : padding for food(green box) (default 0)
-s<char>     : snake's custom body
-t<float>    : sleep seconds after every frame (default 0.1)

Example:
psnake -l
psnake -p10 -l
psnake -l -sX -p5
"""


def run():
    try:
        argv = sys.argv
        global BORDER_LOOP, PADDING, SNAKE_BODY, SLEEP_SECONDS
        for arg in argv:
            if arg[0] == "-" and arg[1] == "p":
                PADDING = int(arg[2:] or 0)
            elif arg[0] == "-" and arg[1] == "s":
                SNAKE_BODY = arg[2] if len(arg) > 2 else "#"
            elif arg[0] == "-" and arg[1] == "t":
                SLEEP_SECONDS = float(arg[2:])
            elif arg[0] == "-" and arg[1:] in ["h", "-help"]:
                print(HELP_TEXT)
                return
            elif arg[0] == "-" and arg[1:] in ["v", "-version"]:
                print(f"psnake {VERSION}")
                return
            elif arg[0] == "-":
                BORDER_LOOP = "l" in arg

        curses.wrapper(snake)

    except KeyboardInterrupt:
        pass
