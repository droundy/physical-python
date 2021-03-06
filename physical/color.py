"""The physical.color module defines a few colors, which can be used
to color things.  It also defines an RGB data type, which allows you
to conveniently define your own new colors.

"""

from __future__ import division, print_function

__all__ = ('RGB',
           'red', 'green', 'blue',
           'yellow', 'cyan', 'magenta',
           'black', 'gray', 'white')

class RGB(object):
    """A color stored in the RGB color space.
    """
    def __init__(self, r,g,b):
        """Generate a color from the RGB values provided, which should range
           from 0 to 1.

        """
        self.__r = r; self.__g = g; self.__b = b
    def rgb(self):
        """Return a list containing the RGB triple.

        """
        return [self.__r, self.__g, self.__b]
    def copy(self):
        return RGB(self.__r, self.__g, self.__b)
    def __repr__(self):
        return 'color.RGB({},{},{})'.format(self.__r, self.__g, self.__b)

#: The color red
red = RGB(1,0,0)
#: The color green
green = RGB(0,1,0)
#: The color blue
blue = RGB(0,0,1)
#: The color yellow
yellow = RGB(1,1,0)
#: The color cyan
cyan = RGB(0,1,1)
#: The color magenta
magenta = RGB(1,0,1)
#: The color white
white = RGB(1,1,1)
#: The color black
black = RGB(0,0,0)
#: The color gray
gray = RGB(0.5,0.5,0.5)
