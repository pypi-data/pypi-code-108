from PIL import Image as PILImage

""" A simple image library that is built on top of pillow. For details, see
    https://python-pillow.org
"""

# Constants that represent the first (X) and second (Y) tuple in a location
# coordinate (X, Y)
X = 0
Y = 1

# Constants that represent the red (R), green (G), and blue (B) portions of
# a pixel color
R = 0
G = 1
B = 2


class ImageInitializationError(Exception):
    """ Exception used when initializing an image without a required filename """
    def __init__(self, message="Must supply a filename"):
        self.message = message
        super().__init__(self.message)


class Pixel:
    """ The Pixel class is used to represent a single pixel in an image. It
        has a location (X,Y) coordinate and references the image in which
        it is located. Users can get or set the RGB values of a pixel.
    """
    def __init__(self, location, image):
        """ Initialize a pixel with location (X,Y) coordinate and an image """
        self.location = location
        self.image = image

    @property
    def red(self):
        """ gets the red portion of the pixel value """
        rgb = self.image.getpixel(self.location)
        return rgb[R]

    @red.setter
    def red(self, value):
        """ sets the red portion of the pixel value """
        rgb = self.image.getpixel(self.location)
        self.image.putpixel(self.location, (int(value), rgb[G], rgb[B]))

    @property
    def green(self):
        """ gets the green portion of the pixel value """
        rgb = self.image.getpixel(self.location)
        return rgb[G]

    @green.setter
    def green(self, value):
        """ sets the green portion of the pixel value """
        rgb = self.image.getpixel(self.location)
        self.image.putpixel(self.location, (rgb[R], int(value), rgb[B]))

    @property
    def blue(self):
        """ gets the blue portion of the pixel value """
        rgb = self.image.getpixel(self.location)
        return rgb[B]

    @blue.setter
    def blue(self, value):
        """ sets the blue portion of the pixel value """
        rgb = self.image.getpixel(self.location)
        self.image.putpixel(self.location, (rgb[R], rgb[G], int(value)))


class Image:
    """ The SimpleImage class provides a simplified interface to interact with
        images. Users can iterate over the pixels in the image, get the pixel at
        a particular (X, Y) coordinate, and get image properties such as height
        and width. Users interact with the Pixel class to get or change the RGB
        values of individual pixels.
    """
    def __init__(self, filename: str, image=None):
        """ Initialize an image with either a filename or an image. If given a
            filename, the image is initialized from the file. If given an image,
            the image is initialized as a copy of this image. If neither a
            filename or an image is supplied, an exception is raised.

            image - a reference to a pillow image
            pixels - the pixels in the image
            location - the (X, Y) coordinate of the current pixel, used when
                iterating over all pixels; initialized to (0, 0)
        """
        if filename:
            self.image = PILImage.open(filename)
        elif image:
            self.image = image
        else:
            raise ImageInitializationError
        self.pixels = self.image.load()
        self.location = (0, 0)

    @property
    def height(self):
        """ Get the height of the image in pixels """
        return self.image.height

    @property
    def width(self):
        """ Get the width of the image in pixels """
        return self.image.width

    def __iter__(self):
        """ Return an iterator """
        return self

    def __next__(self):
        """ Get the next pixel in the image, based on the (X, Y) coordinate of
            the current pixel. Used for an iterator.
            """
        loc = self.location
        self.location = (self.location[X] + 1, self.location[Y])
        if self.location[X] >= self.width:
            self.location = (0, self.location[Y] + 1)
        if self.location[Y] >= self.height:
            raise StopIteration
        return Pixel(loc, self.image)

    def show(self):
        """ Shows the image in a window. """
        self.image.show()

    def get_pixel(self, x, y):
        """ Returns the pixel at the given (X, Y) coordinate """
        return Pixel((x, y), self.image)

    @staticmethod
    def blank(width, height):
        """ Creates a blank (white) image of a given width and height. Can
            be passed an optional color to make an image of the desired color.
        """
        image = PILImage.new(mode="RGB", size=(width, height), color="white")
        i = Image(filename=None, image=image)
        return i
