#!/usr/bin/python
# -*- coding: ISO-8859-1 -*-

"""
ansi2html

by BlackJack @ python-forum.de

http://python.sandtner.org/viewtopic.php?p=16273#16273
"""


import re

ansi_re = re.compile(
    '\033\\[' '([\\d;]*)' '([a-zA-Z])'  # Escape characters.  # Parameters.
)  # Command.
#
# Map ANSI colors to HTML 3.2 color names.
#
ansi_color = ('black', 'red', 'green', 'yellow', 'blue', 'purple', 'teal', 'white')


class Ansi2HtmlWriter:
    def __init__(self, normalColor=('black', 'white')):
        self.ret = ''
        self.foreground, self.background = normalColor
        self.open_span = False
        self.ret += '<pre style="color:%s;background:%s">' % normalColor

    def _close_span_tag(self):
        if self.open_span:
            self.ret += '</span>'
            self.open_span = False

    def _write_span_tag(self, style):
        self._close_span_tag()
        if style:
            style_str = ';'.join(
                ['%s:%s' % (name, value) for name, value in style.iteritems()]
            )
            self.ret += '<span style="%s">' % style_str
            self.open_span = True

    def _write(self, data):
        for character, html_escape in (('&', '&amp;'), ('<', '&lt;'), ('>', '&gt;')):
            data = data.replace(character, html_escape)
        self.ret += data

    def writeline(self, line):
        last_end = 0
        for match in ansi_re.finditer(line):
            #
            # Write string before match.
            #
            self._write(line[last_end : match.start()])
            last_end = match.end()

            #
            # Process escape sequence.
            #
            parameters, command = match.groups()

            try:
                parameters = map(int, parameters.split(';'))
            except ValueError:
                parameters = [0]

            #
            # *Set Graphics Rendition* is the only command to handle.
            # The 'blink' effect is not supported.
            #
            if command in 'mM':
                attributes = dict()
                for param in parameters:
                    if param == 0:
                        attributes.clear()
                    elif param == 1:
                        attributes['font-weight'] = 'bold'
                    elif param == 4:
                        attributes['text-decoration'] = 'underline'
                    elif param == 7:
                        attributes['color'] = self.background
                        attributes['background'] = self.foreground
                        self.background, self.foreground = (
                            self.foreground,
                            self.background,
                        )
                    elif 30 <= param <= 37:
                        color = ansi_color[param - 30]
                        attributes['color'] = color
                        self.foreground = color
                    elif 40 <= param <= 47:
                        color = ansi_color[param - 40]
                        attributes['background'] = color
                        self.background = color
                self._write_span_tag(attributes)
        #
        # Write string after last match.
        #
        self._write(line[last_end:])
        self._close_span_tag()
        self.ret += '</pre>'
        return self.ret

    write = writeline

    def writelines(self, lines):
        for line in lines:
            self.write(line)


if __name__ == '__main__':
    testString = '''\033[00m\033[01;34mbin\033[00m
\033[01;34mboot\033[00m
\033[01;36mcdrom\033[00m
\033[01;34mdaten\033[00m
\033[01;34mdev\033[00m
\033[01;34metc\033[00m
\033[01;34mhome\033[00m
\033[01;34minitrd\033[00m
\033[01;36minitrd.img\033[00m
\033[01;36minitrd.img.old\033[00m
\033[01;34mlib\033[00m
\033[01;34mlost+found\033[00m
\033[01;34mmedia\033[00m
\033[01;34mmnt\033[00m
\033[01;34mopt\033[00m
\033[01;34mproc\033[00m
\033[01;34mroot\033[00m
\033[01;34msbin\033[00m
\033[01;34msrv\033[00m
\033[01;34msys\033[00m
\033[01;34mtmp\033[00m
\033[01;34musr\033[00m
\033[01;34mvar\033[00m
\033[01;36mvmlinuz\033[00m
\033[01;36mvmlinuz.old\033[00m'''

    import sys

    try:
        testString = open(sys.argv[1]).read()
    except:
        print('filename as first argument needed')
        sys.exit(0)
    s = Ansi2HtmlWriter()
    print(s.write(testString))
