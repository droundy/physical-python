"""
.. image :: figures/falling.png
    :align: right

A python package aimed at teaching students physics through having
them program using 3d simulation. A key goal is to provide clear error
messages for mistakes common among intro physics students. Physical is
inspired by the visual package, but aims to provide improved error
messages and assignment semantics.

.. testsetup:: *

    from physical import *


.. testcleanup:: *

    exit_visualization()



"""

from __future__ import division, print_function

__all__ = ('vector',
           'color', 'display',
           'check_units', 'dimensionless',
           'sqrt', 'exp', 'sin', 'cos', 'tan', 'atan2',
           'pi',
           'sphere', 'helix', 'cylinder', 'box',
           'trail',
           'plot', 'hline',
           'timestep', 'savepng',
           'minimum_fps', 'exit_visualization',
           'camera', 'Camera',
           'meter', 'second', 'kg', 'Newton', 'Joule')

try:
    import OpenGL.GLUT as glut
    import OpenGL.GLU as glu
    import OpenGL.GLE as gle
    import OpenGL.GL as gl
except:
    print('Unable to load opengl, things will break')
try:
    import numpy
except:
    print('Using math instead of numpy, things may break')
    import math as numpy
import os, sys, math, atexit, time
import functools

import physical.color

def is_vector(v):
    if type(v) == Units:
        v = v.value
    return type(v) == vector
def is_scalar(s):
    return not is_vector(s)
class Units(object):
    def __init__(self, m, kg, s):
        self._mks = (m,kg,s)
    def _add(self, b):
        if self._mks != units(b):
            raise Exception('you cannot add quantities with differing units: {} + {}'.format(self,b))
        return self._mks
    def _sub(self, b):
        if self._mks != units(b):
            raise Exception('you cannot subtract quantities with differing units: {} + {}'.format(self,b))
        return self._mks
    def _mul(self, b):
        a = self._mks
        b = units(b)
        return (a[0]+b[0], a[1]+b[1], a[2]+b[2])
    def _div(self, b):
        a = self._mks
        b = units(b)
        return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
    def _rdiv(self, b):
        a = self._mks
        b = units(b)
        return (b[0]-a[0], b[1]-a[1], b[2]-a[2])
    def _pow(self, b):
        if units(b) != (0,0,0):
            raise Exception('you cannot take quantity to a power with dimensions %s' % Units.__repr__(b))
        a = self._mks
        return (a[0]*b, a[1]*b, a[2]*b)
    def _eq(self, b):
        return self._mks == b._mks
    def _repr(self):
        (m,kg,s) =self._mks
        r = []
        if m == 1:
            r.append('meter')
        elif m != 0:
            r.append('meter**({})'.format(m))
        if kg == 1:
            r.append('kg')
        elif kg != 0:
            r.append('kg**({})'.format(kg))
        if s == 1:
            r.append('second')
        elif s != 0:
            r.append('second**({})'.format(s))
        return '*'.join(r)

def units(v):
    return getattr(v, '_mks', (0,0,0))
def value(v):
    return getattr(v, 'v', v)
def position(v):
    return getattr(v, 'pos', v)
def check_units(err, *vals):
    """Verifies that the arguments have the same units.

    Args:
        err: a string giving the error message when units fail to match.
    Raises:
        Exception: the units do not match
    """
    # values of zero do not need units
    def is_not_boring(v):
        return not ((not hasattr(v, '_mks') and v == 0)
                    or (type(v) == vector and v._mks == (0,0,0) and
                        v.x == 0 and v.y == 0 and v.z == 0))
    vals = list(filter(is_not_boring, vals))
    if len(vals) >= 2:
        mks = units(vals[0])
        for v in vals[1:]:
            if units(v) != mks:
                raise Exception(err + ': %s vs %s' % (v, vals[0]))
    return True

def check_units_pair(err, a, b):
    """Verifies that the arguments have the same units.

    Args:
        err: a string giving the error message when units fail to match.
    Raises:
        Exception: the units do not match
    """
    # values of zero do not need units
    def is_boring(v):
        return ((not hasattr(v, '_mks') and v == 0)
                or (type(v) == vector and v._mks == (0,0,0) and
                    v._x == 0 and v._y == 0 and v._z == 0))
    if is_boring(a) or is_boring(b):
        return True
    if units(a) != units(b):
        raise Exception(err + ': %s vs %s' % (v, vals[0]))
    return True

def check_units_pair_vectors(err, a, b):
    """Verifies that the arguments have the same units.

    Args:
        err: a string giving the error message when units fail to match.
    Raises:
        Exception: the units do not match
    """
    # values of zero do not need units
    if type(b) != vector:
        raise Exception('need vector')
    if (a._mks == (0,0,0) and a._x == 0 and a._y == 0 and a._z == 0) or (b._mks == (0,0,0) and b._x == 0 and b._y == 0 and b._z == 0):
        return True
    if a._mks != b._mks:
        raise Exception(err + ': %s vs %s' % (v, vals[0]))
    return True

def __is_not_boring(v):
    return not ((not hasattr(v, '_mks') and v == 0)
                or (type(v) == vector and v._mks == (0,0,0) and
                    v.x == 0 and v.y == 0 and v.z == 0)
                or type(v) == type(None))
def units_match(err):
    def decorator(func):
        @functools.wraps(func)
        def unit_checking(*args, **kwargs):
            vals = list(filter(__is_not_boring, list(args) + list(kwargs.values())))
            if len(vals) >= 2:
                mks = units(vals[0])
                for v in vals[1:]:
                    if units(v) != mks:
                        raise Exception(err + ': %s vs %s' % (v, vals[0]))
            return func(*args, **kwargs)
        return unit_checking
    return decorator

def dimensionless(err):
    r'''
    A decorator for declaring that a function expects dimensionless
    input, such as :math:`\sin` and :math:`\cos`.  The single
    argument is the error message to be presented to a user who
    accidentally provides this function with a value having units.

    .. testcode :: dimensionless

        @dimensionless('arguments to myfunction should be dimensionless')
        def myfunction(x):
            return 4*x

    .. doctest :: dimensionless

        >>> myfunction(4)
        16
        >>> myfunction(4*meter)
        Traceback (most recent call last):
          ...
        Exception: arguments to myfunction should be dimensionless: 4 meter
    '''
    def decorator(func):
        @functools.wraps(func)
        def is_dimensionless(*args, **kwargs):
            for v in list(args) + list(kwargs.values()):
                if units(v) != (0,0,0):
                    raise Exception(err + ': %s' % v)
            return func(*args, **kwargs)
        return is_dimensionless
    return decorator

class scalar(Units):
    '''A scalar value with units attached.
    '''
    def __init__(self,v, mks=(0,0,0)):
        """Construct a new 'scalar' object.

        Args:
           v: The value of the object, usually a float or an int
           mks: A triple containing the units in terms of meters, kg, and seconds
        Returns:
           returns nothing
        """
        self._mks = mks
        self.v = v
    def __abs__(self):
        return scalar(abs(self.v), self._mks)
    def __neg__(self):
        return scalar(-self.v, self._mks)
    def __add__(self, b):
        mks = Units._add(self, b)
        return scalar(self.v + value(b), mks)
    def __sub__(self, b):
        mks = Units._sub(self, b)
        return scalar(self.v - value(b), mks)
    def __pow__(self, b):
        if units(b) != (0,0,0):
            raise Exception('you cannot take quantity to a power with dimensions %s' % Units.__repr__(b))
        a = self._mks
        return scalar(self.v **value(b), (a[0]*b, a[1]*b, a[2]*b))
    def __mul__(self, b):
        smks = self._mks; bmks = getattr(b, '_mks', (0,0,0))
        mks = (smks[0]+bmks[0], smks[1]+bmks[1], smks[2]+bmks[2])
        if type(b) == vector:
            return b*self
        else:
            if mks == (0,0,0):
                return self.v*getattr(b,'v',b)
            return scalar(self.v*getattr(b,'v',b), mks)
    def __rmul__(self, b):
        '''We assume here than any object with units (or that is a vector)
        will implement __mul__, so __rmul__ will only be invoked with
        a scalar type as input.

        '''
        return scalar(self.v*b, self._mks)
    def __div__(self,b):
        return self.__truediv__(b)
    def __truediv__(self, b):
        mks = Units._div(self, b)
        if type(b) == vector:
            raise Exception('cannot divide scalar by vector')
        else:
            if mks == (0,0,0):
                return self.v/value(b)
            return scalar(self.v/value(b), mks)
    def __rdiv__(self,b):
        return self.__rtruediv__(b)
    def __rtruediv__(self, b):
        mks = Units._rdiv(self,b)
        return scalar(value(b)/self.v, mks)
    @units_match('can only compare values with same dimensions')
    def __eq__(self, b):
        return value(b) == self.v
    @units_match('can only compare values with same dimensions')
    def __ne__(self, b):
        return value(b) != self.v
    @units_match('can only compare values with same dimensions')
    def __lt__(self, b):
        return self.v < value(b)
    @units_match('can only compare values with same dimensions')
    def __gt__(self, b):
        return self.v > value(b)
    @units_match('can only compare values with same dimensions')
    def __ge__(self, b):
        return self.v >= value(b)
    @units_match('can only compare values with same dimensions')
    def __le__(self, b):
        return self.v <= value(b)
    def __repr__(self):
        return '%s %s' % (self.v, Units._repr(self))

def sqrt(v):
    r'''Compute :math:`\sqrt{x}`.

    .. doctest :: math

        >>> sqrt(4*second**2)
        2.0 second
'''
    return v**0.5

@dimensionless('argument to exp must be dimensionless')
def exp(x):
    '''Compute :math:`e^x`.

    Raises:
        Exception: x is not dimensionless

    .. doctest :: math

        >>> exp(0)
        1.0
        >>> exp(2*second) # bad units!
        Traceback (most recent call last):
          ...
        Exception: argument to exp must be dimensionless: 2 second
    '''
    return numpy.exp(value(x))

@dimensionless('argument to sin must be dimensionless')
def sin(x):
    r'''Compute :math:`\sin(x)`.

    Raises:
        Exception: x is not dimensionless

    .. doctest :: math

        >>> sin(pi/2)
        1.0
        >>> sin(2*second) # bad units!
        Traceback (most recent call last):
          ...
        Exception: argument to sin must be dimensionless: 2 second
    '''
    return numpy.sin(value(x))

@dimensionless('argument to cos must be dimensionless')
def cos(x):
    r'''Compute :math:`\cos(x)`.

    Raises:
        Exception: x is not dimensionless

    .. doctest :: math

        >>> cos(pi)
        -1.0
        >>> cos(2*second) # bad units!
        Traceback (most recent call last):
          ...
        Exception: argument to cos must be dimensionless: 2 second
    '''
    return numpy.cos(value(x))

@dimensionless('argument to tan must be dimensionless')
def tan(x):
    r'''Compute :math:`\tan(x)`.

    Raises:
        Exception: x is not dimensionless

    .. doctest :: math

        >>> print('%g' % tan(pi/4))
        1
        >>> tan(2*second) # bad units!
        Traceback (most recent call last):
          ...
        Exception: argument to tan must be dimensionless: 2 second
    '''
    return numpy.tan(value(x))

@units_match('arguments to atan2 must have the same units')
def atan2(y,x):
    r'''Compute :math:`\tan^{-1}\left(\frac{y}{x}\right)`.

    Args:
        y: the "vertical" component of a vector
        x: the "horizontal" component of the vector
    Raises:
        Exception: x and y do not have the same dimensions

    You should almost always prefer 'atan2' over any other inverse
    trig functions, because it can (and does) properly determine the
    quadrant of the point described by the angle, so it can give you
    an unambiguous answer.  For this reason we do not export any of
    the other inverse trig functions.

    .. doctest :: math

        >>> atan2(5.0*meter, 0.0*meter)
        1.5707963267948966
        >>> atan2(2*second, 3) # units don't match!
        Traceback (most recent call last):
          ...
        Exception: arguments to atan2 must have the same units: 3 vs 2 second
    '''
    return numpy.arctan2(value(y),value(x))

class vector(Units):
    def __new(self,x,y,z,mks):
        ''' A faster version of __init__ that does zero checking. '''
        v = vector.__new__(vector)
        v._mks = mks
        v._x = x
        v._y = y
        v._z = z
        return v
    def __init__(self,x,y,z, mks=(0,0,0)):
        ux = units(x)
        if ux != units(y) or ux != units(z):
            raise Exception('vector components must have same dimensions')
        self._mks = mks
        if mks == (0,0,0):
            if units(x) != mks:
                self._mks = units(x)
            elif units(y) != mks:
                self._mks = units(y)
            elif units(z) != mks:
                self._mks = units(z)
        self._x = value(x)
        self._y = value(y)
        self._z = value(z)
    @property
    def x(self):
        return scalar(self._x, self._mks)
    @x.setter
    def x(self,v):
        if self._mks != units(v):
            raise Exception('x component must have dimensions of vector: %s vs %s'
                            % (self, v))
        self._x = value(v)

    @property
    def y(self):
        return scalar(self._y, self._mks)
    @y.setter
    def y(self,v):
        if self._mks != units(v):
            raise Exception('y component must have dimensions of vector: %s vs %s'
                            % (self, v))
        self._y = value(v)

    @property
    def z(self):
        return scalar(self._z, self._mks)
    @z.setter
    def z(self,v):
        if self._mks != units(v):
            raise Exception('z component must have dimensions of vector: %s vs %s'
                            % (self, v))
        self._z = value(v)
    def cross(self,b):
        if type(b) != vector:
            raise Exception('cannot take cross product of vector with %s' % type(b))
        sx = self._x; sy = self._y; sz = self._z
        bx = b._x; by = b._y; bz = b._z
        smks = self._mks; bmks = b._mks
        return self.__new(sy*bz - sz*by, sz*bx - sx*bz, sx*by - sy*bx,
                          (smks[0]+bmks[0], smks[1]+bmks[1], smks[2]+bmks[2]))
    def dot(self,b):
        if type(b) != vector:
            raise Exception('cannot take dot product of vector with %s' % type(b))
        smks = self._mks; bmks = b._mks
        return scalar(self._x*b._x + self._y*b._y + self._z*b._z,
                      (smks[0]+bmks[0], smks[1]+bmks[1], smks[2]+bmks[2]))
    def abs(self):
        return abs(self)
    def __abs__(self):
        return scalar(math.sqrt(self.x.v**2 + self.y.v**2 + self.z.v**2), self._mks)
    def normalized(self):
        return self / abs(self)

    def __neg__(self):
        return self.__new(-self._x, -self._y, -self._z, self._mks)
    def __add__(self, b):
        if type(b) != vector:
            raise Exception('cannot add vector to %s' % type(b))
        if self._mks != b._mks:
            raise Exception('dimensions do not match in vector addition: %s vs %s'
                            % (self, b))
        return self.__new(self._x+b._x, self._y + b._y, self._z + b._z, self._mks)
    def __sub__(self, b):
        if type(b) != vector:
            raise Exception('cannot subtract %s from vector' % type(b))
        if self._mks != b._mks:
            raise Exception('dimensions do not match in vector subtraction: %s vs %s'
                            % (self, b))
        return self.__new(self._x-b._x, self._y - b._y, self._z - b._z, self._mks)
    def __mul__(self, b):
        if not is_scalar(b):
            raise Exception('can only multipy vectors with scalars')
        smks = self._mks; bmks = getattr(b, '_mks', (0,0,0))
        mks = (smks[0]+bmks[0], smks[1]+bmks[1], smks[2]+bmks[2])
        s = getattr(b,'v',b)
        return self.__new(s*self._x, s*self._y, s*self._z, mks)
    def __rmul__(self, s):
        '''We assume here than any object with units (or that is a vector)
        will implement __mul__, so __rmul__ will only be invoked with
        a scalar type as input.

        '''
        return self.__new(self._x*s, self._y*s, self._z*s, self._mks)
    def __div__(self,b):
        return self.__truediv__(b)
    def __truediv__(self, b):
        if not is_scalar(b):
            raise Exception('can only divide vectors by scalars')
        smks = self._mks; bmks = getattr(b, '_mks', (0,0,0))
        mks = (smks[0]-bmks[0], smks[1]-bmks[1], smks[2]-bmks[2])
        s = getattr(b,'v',b)
        return self.__new(self._x/s, self._y/s, self._z/s, mks)
    def __eq__(self,b):
        return type(b) == vector and self._mks == b._mks and self._x == b._x and self._y == b._y and self._z == b._z
    def __repr__(self):
        return '<%s,%s,%s> %s' % (self._x, self._y, self._z, Units._repr(self))
    def copy(self):
        return self.__new(self._x, self._y, self._z, self._mks)

meter = scalar(1, (1, 0, 0))
kg = scalar(1, (0, 1, 0))
second = scalar(1, (0, 0, 1))
Newton = kg*meter/second**2
Joule = Newton*meter
pi = math.pi

class _rotation(object):
    def __init__(self,angle,axis):
        self.angle = angle
        self.axis = axis.normalized()
    def rotate(self,v):
        vpar = v.dot(self.axis)*self.axis
        vperp = v - vpar
        cosalpha = math.cos(self.angle)
        sinalpha = math.sin(self.angle)
        return vperp*cosalpha + self.axis.cross(v)*sinalpha + vpar

class _Plot(object):
    def __init__(self, color, display):
        self._x = []
        self._y = []
        self.__ymax = None
        self.__xmax = None
        self.__ymin = None
        self.__xmin = None
        self.color = color
        self.__display = display
    def __str__(self):
        return 'plot(%s)' % (self.color)
    def __repr__(self):
        return 'color(%s)' % (self.color)
    def _ymax(self):
        return self.__ymax
    def _xmax(self):
        return self.__xmax
    def _ymin(self):
        return self.__ymin
    def _xmin(self):
        return self.__xmin
    def plot(self,x,y):
        if len(self._x) > 1:
            check_units('y coordinates must all have same units',
                        y, self._y[0])
            check_units('x coordinates must all have same units',
                        x, self._x[0])
            self.__xmax = max(x, self.__xmax)
            self.__xmin = min(x, self.__xmin)
            self.__ymax = max(y, self.__ymax)
            self.__ymin = min(y, self.__ymin)
        else:
            yu = self.__display._y_units()
            if yu is not None:
                check_units('y coordinates must all have same units', y, yu)
            xu = self.__display._x_units()
            if xu is not None:
                check_units('x coordinates must all have same units', x, xu)
            self.__xmax = x
            self.__xmin = x
            self.__ymax = y
            self.__ymin = y
        self._x.append(x)
        self._y.append(y)
    def _draw(self, xmin, xmax, ymin, ymax):
        if len(self._y) < 2:
            return
        gl.glColor3f(*self.color.rgb())
        gl.glLineWidth(1.3)
        gl.glBegin(gl.GL_LINES)
        xs = self._x
        ys = self._y
        skip = int(len(xs)/800)+1
        def x(i):
            v = xs[i]
            if xmax == xmin:
                return 0
            return 2*(v - xmin)/(xmax-xmin) - 1
        def y(i):
            v = ys[i]
            if ymax == ymin:
                return 0
            return 2*(v - ymin)/(ymax-ymin) - 1
        for i in range(0,len(ys)-skip,skip):
            gl.glVertex2f(x(i), y(i));
            gl.glVertex2f(x(i+skip), y(i+skip));
        gl.glEnd()

class _Hline(object):
    def __init__(self, value, color, display):
        self._y = value
        self.color = color
        self.__display = display
    def __str__(self):
        return 'hline(%s, %s)' % (self._y, self.color)
    def __repr__(self):
        return self.__str__()
    def _ymax(self):
        return self._y
    def _xmax(self):
        return None
    def _ymin(self):
        return self._y
    def _xmin(self):
        return None
    def plot(self,y):
        yu = self.__display._y_units()
        if yu is not None:
            check_units('y coordinates must all have same units', y, yu)
        self._y = y
    def _draw(self, xmin, xmax, ymin, ymax):
        gl.glColor3f(*self.color.rgb())
        gl.glLineWidth(1.3)
        if ymax == ymin:
            y_on_screen = 0
        else:
            y_on_screen = 2*(self._y - ymin)/(ymax-ymin) - 1
        gl.glBegin(gl.GL_LINES)
        gl.glVertex2f(-1, y_on_screen);
        gl.glVertex2f( 1, y_on_screen);
        gl.glEnd()

class _Trail(object):
    def __init__(self, object, color=None, duration=None, dash_time=0.2*second):
        check_units('dash_time must be a time', dash_time, second)
        if duration is not None:
            check_units('duration must be a time', duration, second)
        self.__object = object
        self.__stats = []
        self.color = color
        self.duration = duration
        self.dash_time = dash_time
    def __str__(self):
        return 'trail(%s)' % (self.__object)
    def _pass_time(self, t):
        if self.duration is not None:
            too_old = t - self.duration.v
            while len(self.__stats) > 1 and self.__stats[0][0] < too_old:
                self.__stats = self.__stats[2:]
        if self.__stats == []:
            self.__stats.append((t, self.__object.pos.copy()))
            return
        if t > max(self.__stats)[0] + self.dash_time.v:
            p = self.__object.pos
            if p != self.__stats[-1][1]:
                self.__stats.append((t,p.copy()))
            # else:
            #     print("rejecting", self.__object, "at", p,
            #           'versus', self.__stats[-1][1])
    def _draw(self):
        if self.__stats == []:
            return
        if self.color is not None:
            c = self.color.rgb()
        else:
            c = self.__object.color.rgb()
        gl.glColor3f(*c)
        gl.glMaterialfv(gl.GL_FRONT_AND_BACK,gl.GL_EMISSION,c)
        gl.glLineWidth(2.0)
        gl.glBegin(gl.GL_LINES)
        for i in range(1, len(self.__stats), 2):
            old = self.__stats[i-1][1]
            new = self.__stats[i][1]
            gl.glVertex3f(old.x.v, old.y.v, old.z.v);
            gl.glVertex3f(new.x.v, new.y.v, new.z.v);
        gl.glEnd()
        gl.glMaterialfv(gl.GL_FRONT_AND_BACK,gl.GL_EMISSION,(0,0,0))
    def __repr__(self):
        return str(self)

class _Sphere(object):
    def __init__(self, pos, radius, color):
        check_units('position must have dimensions of distance', pos, meter)
        self.pos = pos
        self.radius = radius
        self.color = color
        self.glows = False
    def __str__(self):
        return 'sphere(%s, %s)' % (self.pos, self.radius)
    def _pass_time(self,t):
        pass
    def _draw(self):
        # use a fresh transformation matrix
        gl.glPushMatrix()
        # position object
        gl.glTranslate(value(self.pos.x), value(self.pos.y), value(self.pos.z))
        c = self.color.rgb()
        if self.glows:
            gl.glMaterialfv(gl.GL_FRONT,gl.GL_EMISSION,c)
            gl.glMaterialfv(gl.GL_FRONT,gl.GL_DIFFUSE,(0,0,0))
        else:
            gl.glMaterialfv(gl.GL_FRONT,gl.GL_DIFFUSE,c)
        check_units('radius must have dimensions of distance', self.radius, meter)
        q = glu.gluNewQuadric()
        glu.gluSphere(q, value(self.radius), 60, 60)
        gl.glPopMatrix()
        if self.glows:
            gl.glMaterialfv(gl.GL_FRONT,gl.GL_EMISSION,(0,0,0))
    def __repr__(self):
        return 'sphere(%s, %s)' % (self.pos, self.radius)

class _Helix(object):
    def __init__(self, pos1, pos2, radius, color, length, twists):
        self.pos1 = pos1
        self.pos2 = pos2
        self.length = length
        self.radius = radius
        self.color = color
        self.twists = twists
    def _pass_time(self,t):
        pass
    def _draw(self):
        # use a fresh transformation matrix
        gl.glPushMatrix()
        gle.gleSetJoinStyle (gle.TUBE_NORM_EDGE | gle.TUBE_JN_ANGLE | gle.TUBE_JN_CAP)
        # position object
        pos1 = position(self.pos1)
        pos2 = position(self.pos2)
        gl.glTranslate(value(pos1.x), value(pos1.y), value(pos1.z))
        gl.glMaterialfv(gl.GL_FRONT,gl.GL_DIFFUSE,self.color.rgb())
        check_units('radius must have dimensions of distance', self.radius, meter)
        check_units('position must be a distance', pos1, pos2, meter)
        dr = pos2 - pos1
        dist = abs(dr)
        if dist < self.length:
            radius = sqrt(self.length**2 - dist**2)/self.twists/2/math.pi
        else:
            radius = 0.5*self.radius
        dzdtheta = dist/self.twists
        axis = dr.cross(vector(0,0,1))
        mysin = abs(axis)/dist
        mycos = dr.z/dist
        angle = -atan2(mysin,mycos)*180/math.pi
        gl.glRotate(angle, value(axis.x),value(axis.y),value(axis.z))
        gle.gleHelicoid(value(self.radius), # rToroid
                        value(radius), # startRadius
                        0, # drdTheta
                        0, # startz
                        value(dist/self.twists), # dzdTheta
                        None, # startXform
                        None, # dXformdTheta
                        0.0, # startTheta
                        360.0*self.twists # sweepTheta
        )
        gl.glPopMatrix()
    def __str__(self):
        return 'helix(%s, %s, %s)' % (self.pos1, self.pos2, self.radius)
    def __repr__(self):
        return 'helix(%s, %s, %s)' % (self.pos1, self.pos2, self.radius)

class _Cylinder(object):
    def __init__(self, pos1, pos2, radius, color):
        self.pos1 = pos1
        self.pos2 = pos2
        self.radius = radius
        self.color = color
    def _pass_time(self,t):
        pass
    def _draw(self):
        # use a fresh transformation matrix
        gl.glPushMatrix()
        gle.gleSetJoinStyle (gle.TUBE_NORM_EDGE | gle.TUBE_JN_ANGLE | gle.TUBE_JN_CAP)
        # position object
        pos1 = position(self.pos1)
        pos2 = position(self.pos2)
        gl.glTranslate(value(pos1.x), value(pos1.y), value(pos1.z))
        gl.glMaterialfv(gl.GL_FRONT,gl.GL_DIFFUSE,self.color.rgb())
        check_units('radius must have dimensions of distance', self.radius, meter)
        check_units('position must be a distance', pos1, pos2, meter)
        dr = pos2 - pos1
        dist = abs(dr)
        axis = dr.cross(vector(0,0,1))
        mysin = abs(axis)/dist
        mycos = dr.z/dist
        angle = -atan2(mysin,mycos)*180/math.pi
        gl.glRotate(angle, value(axis.x),value(axis.y),value(axis.z))
        gle.gleHelicoid(value(self.radius), # rToroid
                        0, # startRadius
                        0, # drdTheta
                        0, # startz
                        value(dist), # dzdTheta
                        None, # startXform
                        None, # dXformdTheta
                        0.0, # startTheta
                        360.0 # sweepTheta
        )
        gl.glPopMatrix()
    def __str__(self):
        return 'cylinder(%s, %s, %s)' % (self.pos1, self.pos2, self.radius)
    def __repr__(self):
        return 'cylinder(%s, %s, %s)' % (self.pos1, self.pos2, self.radius)

class _Box(object):
    '''A box is a rectangular prism oriented along the x, y, and z axes.

    While it would be reasonable to be able to rotate the orientation
    of a box, we do not currently permit this.

    '''
    def __init__(self, pos, wx, wy, wz, color):
        check_units('box dimensions must be distances', pos, wx, wy, wz)
        self.pos = pos
        self.wx = wx
        self.wy = wy
        self.wz = wz
        self.color = color
    def _pass_time(self,t):
        pass
    def _draw(self):
        # use a fresh transformation matrix
        gl.glPushMatrix()
        # position object
        gl.glTranslate(value(self.pos.x), value(self.pos.y), value(self.pos.z))
        gl.glMaterialfv(gl.GL_FRONT,gl.GL_DIFFUSE,self.color.rgb())
        check_units('box dimensions must be distances', self.wx, self.wy, self.wz, meter)
        gl.glBegin(gl.GL_QUADS)
        gl.glNormal3f(-1,0,0)
        gl.glVertex3f(-0.5*self.wx.v, -0.5*self.wy.v,  0.5*self.wz.v);
        gl.glVertex3f(-0.5*self.wx.v,  0.5*self.wy.v,  0.5*self.wz.v);
        gl.glVertex3f(-0.5*self.wx.v,  0.5*self.wy.v, -0.5*self.wz.v);
        gl.glVertex3f(-0.5*self.wx.v, -0.5*self.wy.v, -0.5*self.wz.v);

        gl.glNormal3f(1,0,0)
        gl.glVertex3f(0.5*self.wx.v, -0.5*self.wy.v, -0.5*self.wz.v);
        gl.glVertex3f(0.5*self.wx.v,  0.5*self.wy.v, -0.5*self.wz.v);
        gl.glVertex3f(0.5*self.wx.v,  0.5*self.wy.v,  0.5*self.wz.v);
        gl.glVertex3f(0.5*self.wx.v, -0.5*self.wy.v,  0.5*self.wz.v);

        gl.glNormal3f(0,1,0)
        gl.glVertex3f( 0.5*self.wx.v, 0.5*self.wy.v, -0.5*self.wz.v);
        gl.glVertex3f(-0.5*self.wx.v, 0.5*self.wy.v, -0.5*self.wz.v);
        gl.glVertex3f(-0.5*self.wx.v, 0.5*self.wy.v,  0.5*self.wz.v);
        gl.glVertex3f( 0.5*self.wx.v, 0.5*self.wy.v,  0.5*self.wz.v);

        gl.glNormal3f(0,-1,0)
        gl.glVertex3f( 0.5*self.wx.v, -0.5*self.wy.v,  0.5*self.wz.v);
        gl.glVertex3f(-0.5*self.wx.v, -0.5*self.wy.v,  0.5*self.wz.v);
        gl.glVertex3f(-0.5*self.wx.v, -0.5*self.wy.v, -0.5*self.wz.v);
        gl.glVertex3f( 0.5*self.wx.v, -0.5*self.wy.v, -0.5*self.wz.v);

        gl.glNormal3f(0,0,1)
        gl.glVertex3f( 0.5*self.wx.v,  0.5*self.wy.v,  0.5*self.wz.v);
        gl.glVertex3f(-0.5*self.wx.v,  0.5*self.wy.v,  0.5*self.wz.v);
        gl.glVertex3f(-0.5*self.wx.v, -0.5*self.wy.v,  0.5*self.wz.v);
        gl.glVertex3f( 0.5*self.wx.v, -0.5*self.wy.v,  0.5*self.wz.v);

        gl.glNormal3f(0,0,-1)
        gl.glVertex3f( 0.5*self.wx.v, -0.5*self.wy.v, -0.5*self.wz.v);
        gl.glVertex3f(-0.5*self.wx.v, -0.5*self.wy.v, -0.5*self.wz.v);
        gl.glVertex3f(-0.5*self.wx.v,  0.5*self.wy.v, -0.5*self.wz.v);
        gl.glVertex3f( 0.5*self.wx.v,  0.5*self.wy.v, -0.5*self.wz.v);

        gl.glEnd()
        gl.glPopMatrix()
    def __str__(self):
        return 'box(%s, %s, %s, %s)' % (self.pos, self.wx, self.wy, self.wz)
    def __repr__(self):
        return 'box(%s, %s, %s, %s)' % (self.pos, self.wx, self.wy, self.wz)

class __display(object):
    '''
    The private class __display exists to conveniently hide our
    "global" variables relating to camera state, etc.  In principle,
    this could allow us to support multiple windows, but in practice
    it is only intended for name-spacing.
    '''
    def _y_units(self):
        for y in filter(lambda x: x is not None, map(lambda p: p._ymax(), self.__plots)):
            return y
        return None
    def _x_units(self):
        for x in filter(lambda x: x is not None, map(lambda p: p._xmax(), self.__plots)):
            return x
        return None
    def __drawstuff(self):
        # we are sloppy and reset the viewport to window size each
        # time, and reset the perspective each time as well.
        ws = camera.windowsize
        gl.glViewport(0,0,ws[0],ws[1])
        if self.__am_slow:
            gl.glClearColor(0.2,0.,0.,1.)
        else:
            gl.glClearColor(self.__background[0],self.__background[1],self.__background[2],1.)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT|gl.GL_DEPTH_BUFFER_BIT)

        if len(self.__plots) > 0:
            try:
                ymax = max(filter(lambda x: x is not None, map(lambda p: p._ymax(), self.__plots)))
                ymin = min(filter(lambda x: x is not None, map(lambda p: p._ymin(), self.__plots)))
            except:
                ymax = 1
                ymin = -1
            try:
                xmax = max(filter(lambda x: x is not None, map(lambda p: p._xmax(), self.__plots)))
                xmin = min(filter(lambda x: x is not None, map(lambda p: p._xmin(), self.__plots)))
            except:
                xmax = 1
                xmin = -1
            # Now let us do the 2D underlay.  We begin by saving the
            # existing projection matrix.
            gl.glMatrixMode(gl.GL_PROJECTION)
            gl.glPushMatrix()
            gl.glLoadIdentity()

            # set up a temporary and blank model matrix
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glPushMatrix()
            gl.glLoadIdentity()

            # set visualization parameters for 2D
            gl.glPushAttrib( gl.GL_DEPTH_BUFFER_BIT | gl.GL_LIGHTING_BIT )
            gl.glDisable( gl.GL_DEPTH_TEST )
            gl.glDisable( gl.GL_LIGHTING )
            # put 2D stuff in here...

            # I am not sure why setting the clear color here makes any difference...
            gl.glClearColor(0.,0.,0.,1.)

            for p in self.__plots:
                p._draw(xmin, xmax, ymin, ymax)

            # Done with 2D drawing, so now we restore our previous
            # model view and projection matrix.
            gl.glPopAttrib()
            gl.glPopMatrix()
            gl.glMatrixMode(gl.GL_PROJECTION)
            gl.glPopMatrix()


        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        ws = camera.windowsize
        glu.gluPerspective(400., ws[0]/ws[1], 1., 10000.)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        gl.glPushMatrix()
        center = position(camera.center)
        mycamera = position(camera.position)
        glu.gluLookAt(mycamera._x, mycamera._y, mycamera._z,
                      center._x, center._y, center._z,
                      value(camera.up.x), value(camera.up.y), value(camera.up.z))

        lightZeroPosition = [10.,4.,10.,0]
        lightZeroColor = [1,1,1,1.0]
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, lightZeroPosition)
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE, lightZeroColor)
        gl.glLightf(gl.GL_LIGHT0, gl.GL_CONSTANT_ATTENUATION, 0.1)
        gl.glLightf(gl.GL_LIGHT0, gl.GL_LINEAR_ATTENUATION, 0.05)
        gl.glEnable(gl.GL_LIGHT0)

        lightOnePosition = [6.,4.,10.,0]
        lightOneColor = [0.2,0.2,0.4,1.0] # blue-tinged shadows
        gl.glLightfv(gl.GL_LIGHT1, gl.GL_POSITION, lightOnePosition)
        gl.glLightfv(gl.GL_LIGHT1, gl.GL_AMBIENT, lightOneColor)
        gl.glLightf(gl.GL_LIGHT1, gl.GL_CONSTANT_ATTENUATION, 0.1)
        gl.glLightf(gl.GL_LIGHT1, gl.GL_LINEAR_ATTENUATION, 0.05)
        gl.glEnable(gl.GL_LIGHT1)

        for o in self.__objects:
            o._pass_time(self.__current_time)
            o._draw()

        gl.glPopMatrix()

    def __display(self):
        self.__drawstuff()
        glut.glutSwapBuffers()

    def _save(self, fname):
        from PIL import Image
        self.__drawstuff()
        gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)
        width, height = camera.windowsize
        data = gl.glReadPixels(0, 0, width, height, gl.GL_RGB, gl.GL_UNSIGNED_BYTE)
        Image.frombuffer("RGB", (width, height), data, 'raw', 'RGB', 0, -1).save(fname)

    def __init__(self, name = b'physical python'):
        self.__name = name
        self.__x_origin = 0
        self.__y_origin = 0
        self._window_closed = False
        self.__objects = []
        self.__plots = []
        self.__last_time = time.time()
        self.__start_time = time.time()
        self.__current_time = time.time()
        self.__is_initialized = False
        self.__am_rotating = False
        self.__am_translating = False
        self.__am_slow = False
        self.__background = color.black.rgb()
    @property
    def background(self):
        '''the background color
        '''
        return color.RGB(self.__background[0], self.__background[1], self.__background[2])
    @background.setter
    def background(self, c):
        self.__background = c.rgb()

    def __onMouse(self, btn, state, x, y):
        zoom_factor = 1.1
        if btn == glut.GLUT_LEFT_BUTTON:
            if state == glut.GLUT_DOWN:
                self.__am_rotating = True
                self.__x_origin = x
                self.__y_origin = y
            elif state == glut.GLUT_UP:
                self.__am_rotating = False
        elif btn == glut.GLUT_RIGHT_BUTTON:
            if state == glut.GLUT_DOWN:
                self.__am_translating = True
                self.__x_origin = x
                self.__y_origin = y
            elif state == glut.GLUT_UP:
                self.__am_translating = False
        elif btn == 3: # scroll up
            if state == glut.GLUT_DOWN:
                camera.range = camera.range/zoom_factor
            self.__glutPostRedisplay()
        elif btn == 4: # scroll down
            if state == glut.GLUT_DOWN:
                camera.range = camera.range*zoom_factor
            self.__glutPostRedisplay()
        else:
            print('mouse', btn, state)
    def __onWheel(self, button, direction, x, y):
        print('scroll', button, direction, x, y)
    def __onMouseMotion(self, x, y):
        dx = x - self.__x_origin
        dy = y - self.__y_origin
        self.__x_origin = x
        self.__y_origin = y
        if dx == 0 and dy == 0:
            return
        yhat = camera.up.normalized()
        xhat = camera.up.cross(position(camera.center) - position(camera.position)).normalized()
        if self.__am_rotating:
            direction = (dy*xhat - dx*yhat).normalized()
            angle = 3*math.sqrt(dx**2 + dy**2)/camera.windowsize[1]
            R = _rotation(angle, direction)
            camera.position = R.rotate(position(camera.position))
            camera.up = R.rotate(camera.up)
            self.__glutPostRedisplay()
        elif self.__am_translating:
            move = 0.6*(dx*xhat + dy*yhat)/camera.windowsize[1]*abs(position(camera.position) - position(camera.center))
            camera.position = position(camera.position) + move
            camera.center = position(camera.center) + move
            self.__glutPostRedisplay()
    def __onReshape(self, width, height):
        camera.windowsize = (width, height)
        self.__glutPostRedisplay()

    def init(self):
        if not self.__is_initialized:
            self.__is_initialized = True
            ws = camera.windowsize
            if os.environ.get('PYOPENGL_PLATFORM','') == 'osmesa':
                import OpenGL.arrays as glarrays
                import OpenGL.osmesa as osmesa
                ctx = osmesa.OSMesaCreateContext(gl.GL_RGBA, None)
                self.__buf = glarrays.GLubyteArray.zeros((ws[1], ws[0], 4))
                osmesa.OSMesaMakeCurrent(ctx, self.__buf, gl.GL_UNSIGNED_BYTE,
                                         ws[0], ws[1])
                def nullpost():
                    for o in self.__objects:
                        o._pass_time(self.__current_time)
                self.__glutPostRedisplay = nullpost
                self.__glutMainLoopEvent = nullpost
            else:
                sys.argv = glut.glutInit(sys.argv)
                glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH)
                glut.glutInitWindowSize(ws[0],ws[1])
                glut.glutCreateWindow(self.__name)
                self.__glutPostRedisplay = glut.glutPostRedisplay
                self.__glutMainLoopEvent = glut.glutMainLoopEvent

            gl.glShadeModel(gl.GL_SMOOTH)
            gl.glEnable(gl.GL_CULL_FACE)
            gl.glEnable(gl.GL_DEPTH_TEST)
            gl.glEnable(gl.GL_LIGHTING)

            if os.environ.get('PYOPENGL_PLATFORM','') != 'osmesa':
                glut.glutDisplayFunc(self.__display)
                glut.glutMouseFunc(self.__onMouse)
                glut.glutMotionFunc(self.__onMouseMotion)
                glut.glutMouseWheelFunc(self.__onWheel)
                glut.glutReshapeFunc(self.__onReshape)

            self.__onReshape(ws[0],ws[1])
            def sleep_forever():
                self.__am_slow = False
                if not self._window_closed:
                    print('program complete, but still running visualization...')
                    while True:
                        self.__glutMainLoopEvent()
            if os.environ.get('PYOPENGL_PLATFORM','') != 'osmesa':
                atexit.register(sleep_forever)
    def timestep(self, dt):
        self.init()
        self.__current_time += dt.v
        now = time.time()
        if now < self.__current_time:
            self.__am_slow = False
            self.__glutPostRedisplay()
            # print('waiting', self.__current_time - now, 'out of', dt)
            if os.environ.get('PYOPENGL_PLATFORM','') != 'osmesa':
                time.sleep(self.__current_time - now)
            # print('one frame took', time.time() - self.__last_time)
            self.__last_time = time.time()
        elif now > self.__last_time + 0.1:
            self.__am_slow = True
            self.__glutPostRedisplay()
            self.__last_time = time.time()
        else:
            pass
        self.__glutMainLoopEvent()
    def create_plot(self, c):
        if type(c) != color.RGB:
            raise Exception('plot must be given a color')
        s = _Plot(c, self)
        self.__plots.append(s)
        self.init()
        return s
    def create_hline(self, y, c):
        if type(c) != color.RGB:
            raise Exception('plot must be given a color')
        s = _Hline(y, c, self)
        self.__plots.append(s)
        self.init()
        return s
    def create_trail(self, object, duration, dash_time):
        s = _Trail(object, duration=duration, dash_time=dash_time)
        self.__objects.append(s)
        self.init()
        return s
    def create_sphere(self, pos, radius, color):
        s = _Sphere(pos, radius, color)
        self.__objects.append(s)
        self.init()
        return s
    def create_helix(self, pos1, pos2, radius, color, length, twists):
        h = _Helix(pos1, pos2, radius, color, length, twists)
        self.__objects.append(h)
        self.init()
        return h
    def create_cylinder(self, pos1, pos2, radius, color):
        h = _Cylinder(pos1, pos2, radius, color)
        self.__objects.append(h)
        self.init()
        return h
    def create_box(self, pos, wx, wy, wz, color):
        h = _Box(pos, wx, wy, wz, color)
        self.__objects.append(h)
        self.init()
        return h

class Camera(object):
    '''The camera'''
    __center = vector(0,0,0)*meter
    __position = vector(0,10,0)*meter
    __up = vector(0,0,1)*meter
    __windowsize = (400,400)
    def __str__(self):
        return str('{} {} {}'.format(self.__center, self.__position, self.__up))
    @property
    def position(self):
        '''the position of the camera.

        .. testcode :: camera_position

           s = sphere(vector(3,3,3)*meter, color=color.yellow)
           camera.position = s
        '''
        return self.__position
    @position.setter
    def position(self, v):
        if units(position(v)) != (1,0,0):
            raise Exception('position must have dimensions of distance: %s' % (v))
        self.__position = v
    @property
    def up(self):
        '''the vertical direction of the camera.

        .. testcode :: camera_position

           camera.up = vector(0,1,0)
        '''
        return self.__up
    @up.setter
    def up(self, v):
        if type(v) != vector:
            raise Exception('up be a vector: %s' % (v))
        self.__up = v
        self.__up._mks = (1,0,0)
    @property
    def center(self):
        '''the position at which the camera points

        .. testcode :: camera_center

           s = sphere(vector(3,3,3)*meter, color=color.yellow)
           camera.center = s
        '''
        return self.__center
    @center.setter
    def center(self,v):
        if units(position(v)) != (1,0,0):
            raise Exception('center must have dimensions of distance: %s' % (v))
        self.__center = v

    @property
    def range(self):
        '''the distance between the camera and the center

        The distance can be assigned to, which has the effect of shifting
        the camera towards or away from the center.

        .. testcode :: camera_range

           camera.range = 5*meter
        '''
        return abs(position(self.__center) - position(self.__position))
    @range.setter
    def range(self,v):
        if units(v) != (1,0,0):
            raise Exception('range must be a distance: %s' % (v))
        if type(v) == vector:
            raise Exception('range must be a scalar: %s' % (v))
        dr = position(self.__position) - position(self.__center)
        if abs(dr) == 0*meter:
            self.__position = vector(0,10,0)*meter
            return
        self.__position = position(self.__center) + v*dr/abs(dr)

    @property
    def windowsize(self):
        '''the size of the window in pixels

        The windowsize can be assigned to, but only prior to creating
        any objects.

        .. testcode :: windowsize

           camera.windowsize = (200,200)

        '''
        return self.__windowsize
    @windowsize.setter
    def windowsize(self,v):
        self.__windowsize = v

camera = Camera()
__x = __display()
display = __x

def timestep(dt):
    """Advance the simulation by time dt.

    Args:
        dt: the time in seconds (as a scalar) to advance
    Raises:
        Exception: dt is not a time

    You *must* call `timestep` regularly in order for your simulation
    to be animated.  `timestep` also performs a number of cleanup
    tasks, such as allowing user interaction with the visualization.


    .. testcode ::

        t = 0*second
        dt = 0.01*second
        while t < 5*second:
            # do something useful here
            t += dt
            timestep(dt)
    """
    check_units('time step dt must be a time', dt, second)
    return __x.timestep(dt)

def sphere(pos = vector(0,0,0)*meter, radius=1.0*meter, color=color.RGB(1,1,1)):
    """
    Create a sphere object.

    .. image :: figures/sphere.png
         :align: right

    Args:
        pos: the initial position of the sphere in meters (defaults
            to the origin)
        radius: the radius of the sphere in meters
        color: the color of the sphere
    Raises:
        Exception: the dimensions are not distances

    .. literalinclude:: sphere.py
        :start-after: start
        :end-before: done
    """
    check_units('position must have dimensions of distance', pos, meter)
    check_units('radius must have dimensions of distance', radius, meter)
    return __x.create_sphere(pos.copy(), radius, color.copy())

def helix(pos1, pos2,
          radius=0.1*meter, color=color.RGB(1,1,1),
          length=None,
          twists=5):
    """Create a helix object.

    .. image :: figures/helix.png
         :align: right

    Args:
        pos1: the initial position of one end of the helix.  This may
            be an object that has a position, in which case the helix
            will be attached to that object as it moves.
        pos2: the initial position of the other end of the helix.
            This may be an object that has a position, in which case
            the helix will be attached to that object as it moves.
        radius: the radius of the wire in meters
        color: the color of the helix
        length: the length of the wire forming the helix.  If not
            specified, this defaults to 2*twists*the distance between
            the two ends.
        twists: the number of twists in the wire
    Raises:
        Exception: the dimensions are not distances

    .. literalinclude:: helix.py
        :start-after: start
        :end-before: done
    """
    check_units('position must be a distance',
                position(pos1), position(pos2), meter)
    pos1._mks = (1,0,0) # in case it is the zero vector
    pos2._mks = (1,0,0) # in case it is the zero vector
    check_units('radius must have dimensions of distance', radius, meter)
    if length == None:
        d = abs(position(pos2) - position(pos1))
        length = sqrt(d**2 + (5*2*math.pi*radius*twists)**2)
    check_units('length must have dimensions of distance', length, meter)
    return __x.create_helix(pos1, pos2,
                            radius, color.copy(), length=length,
                            twists=twists)

def cylinder(pos1, pos2,
             radius=0.1*meter, color=color.RGB(1,1,1)):
    """Create a cylinder object.

    .. image :: figures/cylinder.png
         :align: right

    Args:
        pos1: the initial position of one end of the cylinder.  This may
            be an object that has a position, in which case the cylinder
            will be attached to that object as it moves.
        pos2: the initial position of the other end of the cylinder.
            This may be an object that has a position, in which case
            the cylinder will be attached to that object as it moves.
        radius: the radius of the cylinder in meters
        color: the color of the cylinder
    Raises:
        Exception: the dimensions are not distances

    The properties of the cylinder may be accessed and later modified
    as member variables of the object returned.

    .. literalinclude :: cylinder.py
        :start-after: start
        :end-before: done
    """
    check_units('position must be a distance',
                position(pos1), position(pos2), meter)
    pos1._mks = (1,0,0) # in case it is the zero vector
    pos2._mks = (1,0,0) # in case it is the zero vector
    check_units('radius must have dimensions of distance', radius, meter)
    return __x.create_cylinder(pos1, pos2,
                               radius, color.copy())

def box(pos, wx, wy, wz, color=color.RGB(1,1,1)):
    """Create a box object.

    .. image :: figures/box.png
         :align: right

    Args:
        pos: the initial position of the center of the box
        wx: the width of the box in the x direction
        wy: the width of the box in the y direction
        wz: the width of the box in the z direction
        color: the color of the cylinder
    Raises:
        Exception: the dimensions are not distances

    .. literalinclude:: box.py
        :start-after: start
        :end-before: done
    """
    check_units('box dimensions must be distances',
                pos, wx, wy, wz, meter)
    return __x.create_box(pos, wx, wy, wz, color.copy())

def trail(object, duration=None, dash_time=0.2*second):
    """Add a trail to an object.

    .. image :: figures/trail.png
         :align: right

    Args:
        object: the object that is trailed, which must have a "pos" attribute
        duration: how long in seconds the trail should last before disappearing
        dash_time: time between when the trail turns on and off, leading to a dashed-line effect
    Raises:
        Exception: the duration or dash_time are not times.

    .. literalinclude:: trail.py
        :start-after: start
        :end-before: done
    """
    return __x.create_trail(object, duration, dash_time)

def plot(color):
    """Create a plot object.

    .. image :: figures/plot.png
         :align: right


    Args:
        color: the color of the curve
    Raises:
        Exception: the color is not a color

    This function returns a plot object.  You can add values to the
    plot as :math:`xy` pairs using code such as:

    .. literalinclude:: fig-plot.py
        :start-after: start
        :end-before: done
    """
    return __x.create_plot(color)

def hline(y, color):
    """Create a horizontal line object.

    Args:
        y: the y value of the line
        color: the color of the line
    Raises:
        Exception: the color is not a color

    .. testcode :: plot

        # the y value must have same units as any other quantities
        # plotted on vertical axis (e.g. example code for `plot`)
        hline(0*Joule, color.blue)

    """
    yu = __x._y_units()
    if yu is not None:
        check_units('y coordinates must all have same units', y, yu)
    return __x.create_hline(y, color)

def savepng(fname):
    '''Save the current image to a file.

    This is useful for creating documentation, or for creating
    instructional materials.  If you are using this command, you may
    also be interested in rendering without displaying a window (for
    scripting), which can be done with:

    PYOPENGL_PLATFORM=osmesa python3 helix.py

    provided you have libosmesa installed, and PyOpenGL >= 3.1.0.

    '''
    __x._save(fname)

#: the minimum frames per second that the renderer will draw.
minimum_fps = 0.1/second

def exit_visualization():
    global __x
    __x._window_closed = True
    __x = __display()

