

from colorthief import ColorThief
from PIL import Image as PILImage

from kivy.uix.image import Image

from .colors import BackgroundColorMixin

from kivy.graphics.opengl import glGetIntegerv
from kivy.graphics.opengl import GL_MAX_TEXTURE_SIZE
_image_max_size = glGetIntegerv(GL_MAX_TEXTURE_SIZE)[0]


class SizeProofImage(Image):
    def __init__(self, **kwargs):
        source = kwargs.get('source', None)
        if source:
            PILImage.MAX_IMAGE_PIXELS = None
            im = PILImage.open(source)
            size = im.size
            sf = max([float(s) / _image_max_size for s in size])
            if sf > 1:
                target = [int(s / sf) for s in size]
                print("Resizing image {1} to {2} {0}"
                      "".format(source, size, target))
                im = im.resize(target, PILImage.ANTIALIAS)
                im.save(source)
            im.close()
            del im
        Image.__init__(self, **kwargs)


StandardImage = SizeProofImage


class BleedImage(BackgroundColorMixin, StandardImage):
    def __init__(self, **kwargs):
        bgcolor = kwargs.pop('bgcolor', 'auto')
        StandardImage.__init__(self, **kwargs)
        BackgroundColorMixin.__init__(self)
        if bgcolor == 'auto':
            self._autoset_bg_color()
            self.bind(source=self._autoset_bg_color)
        else:
            self.bgcolor = bgcolor

    def _autoset_bg_color(self, *_):
        color = ColorThief(self.source).get_color(5)
        self.bgcolor = (x/255 for x in color)
