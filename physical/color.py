from __future__ import division, print_function

__all__ = ('RGB',
           'red', 'green', 'blue',
           'yellow', 'cyan', 'magenta',
           'black', 'white')

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

red = RGB(1,0,0)
green = RGB(0,1,0)
blue = RGB(0,0,1)
yellow = RGB(1,1,0)
cyan = RGB(0,1,1)
magenta = RGB(1,0,1)
white = RGB(1,1,1)
black = RGB(0,0,0)
