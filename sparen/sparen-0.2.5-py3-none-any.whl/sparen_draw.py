#!/usr/bin/env python3

from __future__ import print_function
import math

try:
    import sparen
    Log = sparen.Log
except:
    Log = print

class Canvas:

    ''' Constructor
        @param [in] width   - Width of the canvas
        @param [in] height  - Height of the canvas
        @param [in] charset - Index of active characterset
    '''
    def __init__(self, width=70, height=15, charset=0):
        self.sErr = ""
        self.charsets = [
            {'lines': '-|.|--+|xx----', 'plot': '.', 'fill': '#'},
            {'lines': '─│·├┬┴┼┤xx┌┐└┘', 'plot': '·', 'fill': '█'},
            {'lines': '═║·╠╦╩╬╣xx╔╗╚╝', 'plot': '·', 'fill': '█'}
        ]
        if charset >= len(self.charsets):
            charset = len(self.charsets) - 1
        self.charset = self.charsets[charset]
        self.create(width=width, height=height)

    ''' Destructor
    '''
    def __del__(self):
        self.destroy()

    ''' Cast object to string
    '''
    def __repr__(self):
        return self.toString()

    ''' Returns a string representation of the canvas
    '''
    def toString(self):
        if 0 < self.nSize:
            return ''.join(self.buf)
        return ''

    ''' Returns a description of the last error
    '''
    def getError(self):
        return self.sErr

    ''' Sets arbitrary character set
        @param [in] cs  - Dictionary defining the character set
    '''
    def setCharset(self, cs):
        if not isinstance(cs, dict) or (
                'lines' not in cs
                or 'corners' not in cs
                or 'plot' not in cs
                or 'fill' not in cs
            ):
            self.sErr = 'Invalid parameter'
            return False
        self.charset = cs

    ''' Selects one of the predefined drawing charsets
        @param [in] cs  - Index to a predefined character set
    '''
    def setCharsetIdx(self, cs):
        if cs >= len(self.charsets):
            cs = 0
        self.setCharset(self.charsets[cs])

    ''' Returns the canvas width
    '''
    def getWidth(self):
        return self.nWidth

    ''' Returns the canvas height
    '''
    def getHeight(self):
        return self.nHeight


    ''' Destroys the class instance
    '''
    def destroy(self):
        self.nWidth = 0
        self.nHeight = 0
        self.nSize = 0
        self.buf = []


    ''' Initializes the class instance
        @param [in] width   - Width of the canvas
        @param [in] height  - Height of the canvas
    '''
    def create(self, width=70, height=15):

        self.destroy()

        if 0 >= width or 0 >= height:
            self.sErr = "Invalid canvas size"
            return False

        self.nWidth = width
        self.nHeight = height
        self.nSize = self.nWidth * self.nHeight + self.nHeight

        self.buf = [' '] * self.nSize
        for i in range(0, self.nHeight):
            self.buf[i + (i+1) * self.nWidth] = '\n'

        return True


    ''' Gets a single point on the canvas
        @param [in] x   - X coord of the point to set
        @param [in] y   - Y coord of the point to set
    '''
    def getPoint(self, x, y):
        if 0 > x or self.nWidth <= x or 0 > y or self.nHeight <= y:
            return None
        return self.buf[y * (self.nWidth + 1) + x]


    ''' Sets a single point on the canvas
        @param [in] x   - X coord of the point to set
        @param [in] y   - Y coord of the point to set
        @param [in] ch  - Character value to set
    '''
    def setPoint(self, x, y, ch):
        if None == ch:
            ch = self.charset['plot']
        if 0 > x or self.nWidth <= x or 0 > y or self.nHeight <= y:
            return False
        self.buf[y * (self.nWidth + 1) + x] = ch
        return True

    ''' Substitute character based on a translation mapping
        @param [in] src - Source character (to be written)
        @param [in] dst - Destination character (that already exists at that spot)
        @param [in] cm  - Character map
        @param [in] tm  - Translation map
    '''
    def subChar(self, src, dst, cm, tm):
        if not dst or ' '[0] >= dst:
            return src
        for i in range(0, len(tm)):
            if dst == cm[i]:
                return src if 0 > tm[i] else cm[tm[i]]
        return src


    ''' Draws a line
        @param [in] x1  - X coord of the line starting point
        @param [in] y1  - Y coord of the line starting point
        @param [in] x2  - X coord of the line ending point
        @param [in] y2  - Y coord of the line ending point
        @param [in] cm  - Character map
                            '─│·├┬┴┼┤xx┌┐└┘'
                            '01234567xx0123'
                             ||||||||  ||||
                             ||||||||  |||+---> 13: Bottom right corner
                             ||||||||  ||+----> 12: Bottom left corner
                             ||||||||  |+-----> 11: Top right corner
                             ||||||||  +------> 10: Top left corner
                             |||||||+--------->  7: Right Junction
                             ||||||+---------->  6: All Junction
                             |||||+----------->  5: Bottom Junction
                             ||||+------------>  4: Top Junction
                             |||+------------->  3: Left Junction
                             ||+-------------->  2: Arbitrary line
                             |+--------------->  1: Vertical line
                             +---------------->  0: Horizontal line
    '''
    def line(self, x1, y1, x2, y2, cm=None):

        if not cm:
            cm = self.charset['lines']
        if len(cm) < 14:
            cm = cm.ljust(14, cm[len(cm)-1])

        x1 = int(x1)
        y1 = int(y1)
        x2 = int(x2)
        y2 = int(y2)
        xd = 1 if x1 < x2 else -1
        yd = 1 if y1 < y2 else -1
        w = self.nWidth
        h = self.nHeight

        # Horz line?
        if y1 == y2:
            x1 = max(0,min(x1, w))
            x2 = max(0,min(x2, w))
            for x in range(x1, x2+xd, xd):
                if x == x1:
                    m = [0, 3, -1, 3, 4, 5, 6, 6, -1, -1, 10, 4, 12, 5]
                elif x == x2:
                    m = [0, 7, -1, 6, 4, 5, 6, 7, -1, -1, 4, 11, 5, 13]
                else:
                    m = [0, 6, -1, 6, 4, 5, 6, 6, -1, -1, 4, 4, 5, 5]
                self.setPoint(x, y1, self.subChar(cm[0], self.getPoint(x, y1), cm, m))

        # Vert line?
        elif x1 == x2:
            y1 = max(0,min(y1, h))
            y2 = max(0,min(y2, h))
            for y in range(y1, y2+yd, yd):
                if y == y1:
                    m = [4, 1, -1, 3, 4, 6, 6, 7, -1, -1, 10, 11, 3, 7]
                elif y == y2:
                    m = [5, 1, -1, 3, 6, 5, 6, 7, -1, -1, 3, 7, 12, 13]
                else:
                    m = [6, 1, -1, 3, 6, 6, 6, 7, -1, -1, 3, 7, 3, 7]
                self.setPoint(x1, y, self.subChar(cm[1], self.getPoint(x1, y), cm, m))

        # Arbitrary line
        else:
            mx = 0
            my = 0
            xl = abs(x2 - x1)
            yl = abs(y2 - y1)

            done = False
            while not done:

                if x1 == x2 and y1 == y2:
                    done = True

                if 0 <= x1 and x1 < w and 0 <= y1 and y1 < h:
                    self.setPoint(x1, y1, cm[2])

                mx += xl
                if x1 != x2 and mx > yl:
                    x1 += xd
                    mx -= yl

                my += yl
                if y1 != y2 and my > xl:
                    y1 += yd
                    my -= xl


    ''' Fills a rectangle with the specified character value
        @param [in] x1  - X coord of the upper left point
        @param [in] y1  - Y coord of the upper left point
        @param [in] x2  - X coord of the lower right point
        @param [in] y2  - Y coord of the lower right point
        @param [in] ch  - Character to fill the rectangle with
    '''
    def fillRect(self, x1, y1, x2, y2, ch=None):

        if not ch:
            ch = self.charset['fill']

        if x1 > x2:
            x1,x2 = x2,x1
        if y1 > y2:
            y1,y2 = y2,y1

        for y in range(y1, y2):
            for x in range(x1, x2):
                self.setPoint(x, y, ch)


    ''' Fills the entire canvas with the specified character
        @param [in] ch  - Character to fill the canvas with
    '''
    def erase(self, ch=' '):
        self.fillRect(0, 0, self.nWidth, self.nHeight, ch)


    ''' Draws a rectangle outline with the specified character map
        @param [in] x1  - X coord of the upper left point
        @param [in] y1  - Y coord of the upper left point
        @param [in] x2  - X coord of the lower right point
        @param [in] y2  - Y coord of the lower right point
        @param [in] cm  - Character map
                            '─│·├┬┴┼┤xx┌┐└┘'
                            '01234567xx0123'
                             ||||||||  ||||
                             ||||||||  |||+---> 13: Bottom right corner
                             ||||||||  ||+----> 12: Bottom left corner
                             ||||||||  |+-----> 11: Top right corner
                             ||||||||  +------> 10: Top left corner
                             |||||||+--------->  7: Right Junction
                             ||||||+---------->  6: All Junction
                             |||||+----------->  5: Bottom Junction
                             ||||+------------>  4: Top Junction
                             |||+------------->  3: Left Junction
                             ||+-------------->  2: Arbitrary line
                             |+--------------->  1: Vertical line
                             +---------------->  0: Horizontal line
    '''
    def rect(self, x1, y1, x2, y2, cm = None):

        if not cm:
            cm = self.charset['lines']
        if len(cm) < 14:
            cm = cm.ljust(14, cm[len(cm)-1])

        # Read corners
        c0 = self.getPoint(x1, y1)
        c1 = self.getPoint(x2, y1)
        c2 = self.getPoint(x1, y2)
        c3 = self.getPoint(x2, y2)

        # Draw lines
        self.line(x1, y1, x2, y1, cm)
        self.line(x2, y1, x2, y2, cm)
        self.line(x2, y2, x1, y2, cm)
        self.line(x1, y2, x1, y1, cm)

        # Choose correct corner
        self.setPoint(x1, y1, self.subChar(cm[10], c0, cm, [4, 3, -1, 3, 4, 6, 6, 6, -1, -1, 10, 4, 3, 6]))
        self.setPoint(x2, y1, self.subChar(cm[11], c1, cm, [4, 7, -1, 6, 4, 6, 6, 7, -1, -1, 4, 11, 6, 7]))
        self.setPoint(x1, y2, self.subChar(cm[12], c2, cm, [5, 3, -1, 3, 6, 5, 6, 6, -1, -1, 3, 6, 12, 5]))
        self.setPoint(x2, y2, self.subChar(cm[13], c3, cm, [5, 7, -1, 6, 6, 5, 6, 7, -1, -1, 6, 7, 5, 13]))


    ''' Draws an arc
        @param [in] x   - X coord of the arc focus point
        @param [in] y   - Y coord of the arc focus point
        @param [in] r   - Arc radius
        @param [in] s   - Starting angle in degrees
        @param [in] e   - Ending angle in degrees
        @param [in] ch  - Character to plot
        @param [in] ar  - Aspect ratio, to make circles look a
                          bit rounder, this can be set to 2,
                          use 1 for a precision circle
    '''
    def arc(self, x, y, r, s, e, ch=None, ar=2):

        if not ch:
            ch = self.charset['plot']

        pi2 = math.pi * 2
        s = math.radians(s)
        e = math.radians(e)
        if e < s:
            e,s = s,e

        a = e - s
        pts = int((r * 8) * a / pi2)

        for i in range(0, pts):
            px = int(x + r * math.cos(s + i * a / pts) * ar)
            py = int(y + r * math.sin(s + i * a / pts))
            self.setPoint(px, py, ch)


    ''' Draws a circle
        @param [in] x   - X coord of the circle focus point
        @param [in] y   - Y coord of the circle focus point
        @param [in] r   - Circle radius
        @param [in] ch  - Character to plot
        @param [in] ar  - Aspect ratio, to make circles look a
                          bit rounder, this can be set to 2,
                          use 1 for a precision circle
    '''
    def circle(self, x, y, r, ch=None, ar=2):
        self.arc(x, y, r, 0, 360, ch, ar)


    ''' Draw text at the specified position
        @param [in] x   - X coord of the text
        @param [in] y   - Y coord of the text
        @param [in] txt - Text to plot
    '''
    def text(self, x, y, txt):
        for i in range(0, len(txt)):
            if not self.setPoint(x + i, y, txt[i]):
                break


    ''' Splits a string to the specified length on whitespace when possible
        @param [in] txt     - Text to split
        @param [in] mx      - Maximum length of a single line

        @returns Returns an array of rows of split text
    '''
    def splitText(self, txt, mx):

        if 0 >= mx:
            return [txt]

        # Fix tabs and crlf's and split lines
        lines = txt.replace('\t', ' ').replace('\r\n', '\n').replace('\r', '\n').split("\n")

        rows = []
        for ln in lines:

            ln = ln.strip()
            while mx < len(ln):

                l = 0
                sp = 0
                while l < mx:
                    if ln[l] <= ' '[0]:
                        sp = l
                    l += 1

                # Soft break
                if 0 < sp:
                    rows.append(ln[:sp])
                    ln = ln[sp+1:]
                    ln = ln.strip()

                # Hard break
                else:
                    rows.append(ln[:mx-1])
                    ln = ln[mx-1:]
                    ln = ln.strip()

            if 0 < len(ln):
                rows.append(ln)

        return rows


    ''' Draw text and contain it in the specified box
        @param [in] x1          - X coord of the upper left point
        @param [in] y1          - Y coord of the upper left point
        @param [in] x2          - X coord of the lower right point
        @param [in] y2          - Y coord of the lower right point
        @param [in] txt         - Text to plot
        @param [in] xjustify    - How to justify the text on the X axis
                                    Can be: center, left, right
        @param [in] yjustify    - How to justify the text on the Y axis
                                    Can be: center, top, bottom
    '''
    def textBox(self, x1, y1, x2, y2, txt, xjustify='center', yjustify='center'):

        if x1 > x2:
            x1,x2 = x2,x1
        if y1 > y2:
            y1,y2 = y2,y1

        w = x2 - x1
        h = y2 - y1

        # Split the text into rows
        rows = self.splitText(txt, w)

        x1 += 1
        y1 += 1

        # Drop rows that don't fit
        if len(rows) >= h:
            rows = rows[:h-1]

        # Y axis justification
        if 'top' == yjustify:
            pass
        elif 'bottom' == yjustify:
            y1 = y1 + h - len(rows) - 1
        else:
            y1 = math.ceil(y1 + (h - len(rows)) / 2 - 1)

        # Draw each row of text
        for r in rows:

            if y1 >= y2:
                break

            # X axis justification
            if 'left' == xjustify:
                x = x1
            elif 'right' == xjustify:
                x = x2 - len(r)
            else:
                x = math.ceil(x1 + (w - len(r)) / 2 - 1)

            self.text(x, y1, r)
            y1 += 1


