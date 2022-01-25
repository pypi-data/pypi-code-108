import os
from sys import stdout
from time import sleep
from utils import thread_helpers
from utils._internal import depends
depends.attemptImport(packagePythonName='termcolor', packagePip3Name='termcolor')
from termcolor import colored




class animate_iteration:
    def __init__(self, static: str, animationList: list = ('/', '-', '\\', '|'), prefix=None, completion=None,
                 delay=0.2, textColour=None):
        """
        :param animationList:
        Any list of string will be iterated through
        if the animation list is set to ['default'] automatically use ['/', '-', '\\', '|']
        :param static:
        prints right before animation list
        :param prefix:
        prints before static
        :param completion:
        prints after .stop_animation
        :param delay:
        delay between print
        :param textColour:
        color of the animation
        available colors ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
        """
        if animationList[0] == "default":
            animationList = ['/', '-', '\\', '|']

        self.animation = animationList
        self.delay = delay
        self.static = static
        self.prefix = prefix
        self.stop = False
        self.completion = completion
        self.colors = textColour
        self._mutate_animation()

    def _mutate_animation(self, completion=False):
        if self.colors is not None:
            self.static = colored(text=self.static, color=self.colors)

            if self.prefix is not None:
                self.prefix = colored(text=self.prefix, color=self.colors)

            if self.completion is not None and completion:
                self.completion = colored(text=self.completion, color=self.colors)

    def start_animation(self):
        def animate(selfClass):
            while True:
                self._mutate_animation()
                if self.stop:
                    if self.completion is not None:
                        self._clear_screen()
                        self._mutate_animation(completion=True)

                        try:
                            if self.prefix is None:
                                self.prefix = ''
                        except TypeError:
                            self.prefix = ''

                        print('\r' + self.prefix, self.completion)
                    break

                for animation in selfClass.animation:
                    if self.prefix is not None:
                        stdout.write('\r' + self.prefix + ' ' + selfClass.static + ' ' + animation)
                    else:
                        stdout.write('\r' + selfClass.static + ' ' + animation)

                    stdout.flush()
                    sleep(selfClass.delay)


                    try:
                        stdout.write('\r' + str(' ' * os.get_terminal_size()[0]))
                    except OSError:
                        if self.prefix is not None:
                            stdout.write('\r' + ' ' * len(self.prefix + ' ' + selfClass.static + ' ' + animation))
                        else:
                            stdout.write('\r' + ' ' * len(selfClass.static + ' ' + animation))


        thread_helpers.thread(func=animate, args=[self])

    def stop_animation(self):
        self.stop = True
        sleep(1)

    def change_static(self, static: str):
        self._clear_screen()
        self.static = static
        self._mutate_animation()

    def _clear_screen(self):
        try:
            stdout.write('\r' + str(' ' * os.get_terminal_size()[0]))
        except OSError:
            stdout.write('\r' + ' ' * len(self.static))

    def change_animation_list(self, animationList: list):
        self.animation = animationList

    def change_prefix(self, prefix: str):
        self.prefix = prefix
        self._mutate_animation()

    def change_color(self, color):
        self.colors = color


if __name__ == '__main__':
    # for debugging
    # animations = ['/', '-', '\\', '|']
    # a = animate_iteration(animationList=animations, static='Animatingggggg',
    #                       completion='Hello Bye', prefix='[Static]',
    #                       textColour='red')
    # a.start_animation()
    # sleep(1)
    #
    # a.change_color(color='green')
    # a.change_prefix(prefix='[SOOO]')
    # a.change_static('FOoo')
    # a.change_animation_list(animationList=['a', 'b', 'c'])
    #
    # sleep(3)
    #
    # a.stop_animation()
    #
    # sleep(1)
    #
    # print('end')
    pass
