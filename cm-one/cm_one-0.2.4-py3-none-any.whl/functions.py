import argparse


def create_parser():
    """ Создать и вернуть парсер для аргументов, передаваемых при запуске
    приложения"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-ar_ip', nargs='?')
    parser.add_argument('-ar_port', nargs='?', default=52250)
    parser.add_argument('-mirrored', nargs='?', default=0)

    return parser

def draw_version_on_screen(canvas, xpos, ypos, version_text, font):
    """ Рисует на холсте версию приложения """
    canvas.create_text(xpos, ypos, text=version_text, font=font,
                       fill='grey')