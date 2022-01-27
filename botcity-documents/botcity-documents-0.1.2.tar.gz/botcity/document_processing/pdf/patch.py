from pdfminer import layout
from pdfminer.utils import apply_matrix_pt, bbox2str, matrix2str


def patch_ltchar():
    class LTChar(layout.LTComponent, layout.LTText):
        """Actual letter in the text as a Unicode string."""

        def __init__(self, matrix, font, fontsize, scaling, rise,
                     text, textwidth, textdisp, ncs, graphicstate):
            layout.LTText.__init__(self)
            self._text = text
            self.matrix = matrix
            self.font = font
            self.rise = rise
            self.fontsize = fontsize
            self.fontname = font.fontname
            self.ncs = ncs
            self.graphicstate = graphicstate
            self.adv = textwidth * fontsize * scaling
            # compute the boundary rectangle.
            if font.is_vertical():
                # vertical
                (vx, vy) = textdisp
                if vx is None:
                    vx = fontsize * 0.5
                else:
                    vx = vx * fontsize * .001
                vy = (1000 - vy) * fontsize * .001
                bbox_lower_left = (-vx, vy + rise + self.adv)
                bbox_upper_right = (-vx + fontsize, vy + rise)
            else:
                # horizontal
                descent = font.get_descent() * fontsize
                bbox_lower_left = (0, descent + rise)
                bbox_upper_right = (self.adv, descent + rise + fontsize)
            self.descent = descent
            self.ascent = font.get_ascent() * fontsize
            (a, b, c, d, e, f) = self.matrix
            self.upright = (0 < a*d*scaling and b*c <= 0)
            (x0, y0) = apply_matrix_pt(self.matrix, bbox_lower_left)
            (x1, y1) = apply_matrix_pt(self.matrix, bbox_upper_right)
            if x1 < x0:
                (x0, x1) = (x1, x0)
            if y1 < y0:
                (y0, y1) = (y1, y0)
            layout.LTComponent.__init__(self, (x0, y0, x1, y1))
            if font.is_vertical():
                self.size = self.width
            else:
                self.size = self.height
            return

        def __repr__(self):
            return ('<%s %s matrix=%s font=%r adv=%s text=%r>' %
                    (self.__class__.__name__, bbox2str(self.bbox),
                     matrix2str(self.matrix), self.fontname, self.adv,
                     self.get_text()))

        def get_text(self):
            return self._text

        def is_compatible(self, obj):
            """Returns True if two characters can coexist in the same line."""
            return True
    layout.LTChar = LTChar
