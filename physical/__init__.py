"""
A python package aimed at teaching students physics through having
them program using 3d simulation. A key goal is to provide clear error
messages for mistakes common among intro physics students. Physical is
inspired by the visual package, but aims to provide improved error
messages and assignment semantics.
"""

from __future__ import division, print_function

__all__ = ('vector',
           'color',
           'check_units', 'dimensionless',
           'sqrt', 'exp', 'sin', 'cos', 'tan', 'atan2',
           'sphere', 'helix', 'cylinder', 'box',
           'timestep', 'savepng',
           'minimum_fps',
           'meter', 'second', 'kg')

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
import sys, math, atexit, time, traceback
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
    if hasattr(v, '_mks'):
        return v._mks
    return (0,0,0)
def value(v):
    if hasattr(v, 'v'):
        return v.v
    return v
def position(v):
    if hasattr(v, 'pos'):
        return v.pos
    return v
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
    '''
    A decorator for declaring that a function expects dimensionless
    input. This is used in functions like 'sin' and 'cos'.  The single
    argument is the error message to be presented to a user who
    accidentally provides this function with a value having units.
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

@functools.total_ordering
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
    def __add__(self, b):
        mks = Units._add(self, b)
        return scalar(self.v + value(b), mks)
    def __sub__(self, b):
        mks = Units._sub(self, b)
        return scalar(self.v - value(b), mks)
    def __pow__(self, b):
        mks = Units._pow(self, b)
        return scalar(self.v **value(b), mks)
    def __mul__(self, b):
        mks = Units._mul(self, b)
        if type(b) == vector:
            return vector(b.x*self.v, b.y*self.v, b.z*self.v, mks)
        else:
            return scalar(self.v*value(b), mks)
    def __rmul__(self, b):
        return scalar(b*self.v, self._mks)
    def __div__(self,b):
        return self.__truediv__(b)
    def __truediv__(self, b):
        mks = Units._div(self, b)
        if type(b) == vector:
            raise Exception('cannot divide scalar by vector')
        else:
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
    def __lt__(self, b):
        return self.v < value(b)
    def __repr__(self):
        return '%s %s' % (self.v, Units._repr(self))

def sqrt(v):
    r'''Compute :math:`\sqrt{x}`.'''
    return v**0.5

@dimensionless('argument to exp must be dimensionless')
def exp(x):
    '''Compute :math:`e^x`.

    Raises:
        Exception: x is not dimensionless
    '''
    return numpy.exp(value(x))

@dimensionless('argument to sin must be dimensionless')
def sin(x):
    r'''Compute :math:`\sin(x)`.

    Raises:
        Exception: x is not dimensionless
    '''
    return numpy.sin(value(x))

@dimensionless('argument to cos must be dimensionless')
def cos(x):
    r'''Compute :math:`\cos(x)`.

    Raises:
        Exception: x is not dimensionless
    '''
    return numpy.cos(value(x))

@dimensionless('argument to tan must be dimensionless')
def tan(x):
    r'''Compute :math:`\tan(x)`.

    Raises:
        Exception: x is not dimensionless
    '''
    return numpy.cos(value(x))

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

    '''
    return numpy.arctan2(value(y),value(x))

meter = scalar(1, (1, 0, 0))
kg = scalar(1, (0, 1, 0))
second = scalar(1, (0, 0, 1))

class vector(Units):
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
        return vector(self._y*b._z - self._z*b._y,
                      self._z*b._x - self._x*b._z,
                      self._x*b._y - self._y*b._x, Units._mul(self, b))
    def dot(self,b):
        if type(b) != vector:
            raise Exception('cannot take dot product of vector with %s' % type(b))
        return scalar(self._x*b._x + self._y*b._y + self._z*b._z, Units._mul(self, b))
    def abs(self):
        return abs(self)
    def __abs__(self):
        return scalar(math.sqrt(self.x.v**2 + self.y.v**2 + self.z.v**2), self._mks)
    def normalized(self):
        return self / self.abs()

    def __add__(self, b):
        if type(b) != vector:
            raise Exception('cannot add vector to %s' % type(b))
        if self._mks != b._mks:
            raise Exception('dimensions do not match in vector addition: %s vs %s'
                            % (self, b))
        return vector(self._x+b._x, self._y + b._y, self._z + b._z, self._mks)
    def __sub__(self, b):
        if type(b) != vector:
            raise Exception('cannot subtract %s from vector' % type(b))
        if self._mks != b._mks:
            raise Exception('dimensions do not match in vector subtraction: %s vs %s'
                            % (self, b))
        return vector(self._x-b._x, self._y - b._y, self._z - b._z, self._mks)
    def __mul__(self, s):
        if not is_scalar(s):
            raise Exception('can only multipy vectors with scalars')
        mks = Units._mul(self, s)
        return vector(self.x.v*value(s), self.y.v*value(s), self.z.v*value(s), mks)
    def __rmul__(self, s):
        if not is_scalar(s):
            raise Exception('can only multipy vectors with scalars')
        mks = Units._mul(self, s)
        return vector(self.x*value(s), self.y*value(s), self.z*value(s), mks)
    def __div__(self,b):
        return self.__truediv__(b)
    def __truediv__(self, s):
        if not is_scalar(s):
            raise Exception('can only divide vectors by scalars')
        return vector(self.x/s, self.y/s, self.z/s)
    def __eq__(self,b):
        return type(b) == vector and self._mks == b._mks and self._x == b._x and self._y == b._y and self._z == b._z
    def __repr__(self):
        return '<%s,%s,%s> %s' % (self._x, self._y, self._z, Units._repr(self))
    def copy(self):
        return vector(self.x, self.y, self.z)

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

class _Sphere(object):
    def __init__(self, pos, radius, color):
        check_units('position must have dimensions of distance', pos, meter)
        self.pos = pos
        self.radius = radius
        self.color = color
    def __str__(self):
        return 'sphere(%s, %s)' % (self.pos, self.radius)
    def _draw(self):
        # use a fresh transformation matrix
        gl.glPushMatrix()
        # position object
        gl.glTranslate(value(self.pos.x), value(self.pos.y), value(self.pos.z))
        gl.glMaterialfv(gl.GL_FRONT,gl.GL_DIFFUSE,self.color.rgb())
        check_units('radius must have dimensions of distance', self.radius, meter)
        glut.glutSolidSphere(value(self.radius), 60, 60)
        gl.glPopMatrix()
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
    def _draw(self):
        # use a fresh transformation matrix
        gl.glPushMatrix()
        # position object
        gl.glTranslate(value(self.pos.x), value(self.pos.y), value(self.pos.z))
        gl.glMaterialfv(gl.GL_FRONT,gl.GL_DIFFUSE,self.color.rgb())
        check_units('box dimensions must be distances', self.wx, self.wy, self.wz, meter)
        gl.glScale(value(self.wx), value(self.wy), value(self.wz))
        glut.glutSolidCube(1)
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
    def __drawstuff(self):
        gl.glPushMatrix()
        glu.gluLookAt(value(self.__camera.x), value(self.__camera.y), value(self.__camera.z),
                  value(self.__center.x), value(self.__center.y), value(self.__center.z),
                  value(self.__up.x), value(self.__up.y), value(self.__up.z))

        lightZeroPosition = [10.,4.,10.,1.]
        lightZeroColor = [1,1,1,1.0]
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, lightZeroPosition)
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE, lightZeroColor)
        gl.glLightf(gl.GL_LIGHT0, gl.GL_CONSTANT_ATTENUATION, 0.1)
        gl.glLightf(gl.GL_LIGHT0, gl.GL_LINEAR_ATTENUATION, 0.05)
        gl.glEnable(gl.GL_LIGHT0)

        lightOnePosition = [6.,4.,10.,1.]
        lightOneColor = [0.2,0.2,0.4,1.0] # blue-tinged shadows
        gl.glLightfv(gl.GL_LIGHT1, gl.GL_POSITION, lightOnePosition)
        gl.glLightfv(gl.GL_LIGHT1, gl.GL_AMBIENT, lightOneColor)
        gl.glLightf(gl.GL_LIGHT1, gl.GL_CONSTANT_ATTENUATION, 0.1)
        gl.glLightf(gl.GL_LIGHT1, gl.GL_LINEAR_ATTENUATION, 0.05)
        gl.glEnable(gl.GL_LIGHT1)

        if self.__am_slow:
            gl.glClearColor(0.2,0.,0.,1.)
        else:
            gl.glClearColor(0.,0.,0.,1.)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT|gl.GL_DEPTH_BUFFER_BIT)

        for o in self.__objects:
            o._draw()

        gl.glPopMatrix()

    def __display(self):
        self.__drawstuff()
        glut.glutSwapBuffers()

    def _save(self, fname):
        from PIL import Image
        self.__drawstuff()
        gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)
        width = self.__windowsize[0]
        height = self.__windowsize[1]
        data = gl.glReadPixels(0, 0, width, height, gl.GL_RGB, gl.GL_UNSIGNED_BYTE)
        Image.fromstring("RGB", (width, height), data).save(fname)

    def __init__(self, name = b'physical python'):
        self.__name = name
        self.__x_origin = 0
        self.__y_origin = 0
        self.__center = vector(0,0,0)
        self.__camera = vector(0,10,0)
        self.__up = vector(0,0,1)
        self.__window_closed = False
        self.__objects = []
        self.__last_time = time.time()
        self.__start_time = time.time()
        self.__current_time = time.time()
        self.__is_initialized = False
        self.__am_rotating = False
        self.__am_translating = False
        self.__am_slow = False

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
                self.__camera = self.__center + (self.__camera - self.__center)/1.1
            glut.glutPostRedisplay()
        elif btn == 4: # scroll down
            if state == glut.GLUT_DOWN:
                self.__camera = self.__center + (self.__camera - self.__center)*1.1
            glut.glutPostRedisplay()
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
        yhat = self.__up.normalized()
        xhat = self.__up.cross((self.__center - self.__camera).normalized())
        if self.__am_rotating:
            direction = (dy*xhat - dx*yhat).normalized()
            angle = 3*math.sqrt(dx**2 + dy**2)/self.__windowsize[1]
            R = _rotation(angle, direction)
            self.__camera = R.rotate(self.__camera)
            self.__up = R.rotate(self.__up)
            glut.glutPostRedisplay()
        elif self.__am_translating:
            move = 0.6*(dx*xhat + dy*yhat)/self.__windowsize[1]*abs(self.__camera - self.__center)
            self.__camera = self.__camera + move
            self.__center = self.__center + move
            glut.glutPostRedisplay()
    def __onReshape(self, width, height):
        self.__windowsize = (width, height)
        gl.glViewport(0,0,width,height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        glu.gluPerspective(40.,width/height,1.,1000.)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        glut.glutPostRedisplay()

    def init(self):
        if not self.__is_initialized:
            self.__is_initialized = True
            sys.argv = glut.glutInit(sys.argv)
            glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH)
            self.__windowsize = (400,400)
            glut.glutInitWindowSize(self.__windowsize[0],self.__windowsize[1])
            glut.glutCreateWindow(self.__name)

            gl.glShadeModel(gl.GL_SMOOTH)
            gl.glEnable(gl.GL_CULL_FACE)
            gl.glEnable(gl.GL_DEPTH_TEST)
            gl.glEnable(gl.GL_LIGHTING)

            glut.glutDisplayFunc(self.__display)
            glut.glutMouseFunc(self.__onMouse)
            glut.glutMotionFunc(self.__onMouseMotion)
            glut.glutMouseWheelFunc(self.__onWheel)
            glut.glutReshapeFunc(self.__onReshape)

            self.__onReshape(400,400)
            def sleep_forever():
                self.__am_slow = False
                if not self.__window_closed:
                    print('program complete, but still running visualization...')
                    while True:
                        glut.glutMainLoopEvent()
            atexit.register(sleep_forever)

    def timestep(self, dt):
        self.__current_time += dt.v
        now = time.time()
        if now < self.__current_time:
            self.__am_slow = False
            glut.glutPostRedisplay()
            # print('waiting', self.__current_time - now, 'out of', dt)
            time.sleep(self.__current_time - now)
            # print('one frame took', time.time() - self.__last_time)
            self.__last_time = time.time()
        elif now > self.__last_time + 0.1:
            self.__am_slow = True
            glut.glutPostRedisplay()
            self.__last_time = time.time()
        else:
            pass
        glut.glutMainLoopEvent()
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

__x = __display()

def timestep(dt):
    """Advance the simulation by time dt.

    Args:
        dt: the time in seconds (as a scalar) to advance
    Raises:
        Exception: dt is not a time

    You *must* call 'timestep' regularly in order for your simulation
    to be animated.  'timestep' also performs a number of cleanup
    tasks, such as allowing user interaction with the visualization.

    """
    check_units('time step dt must be a time', dt, second)
    return __x.timestep(dt)

def sphere(pos = vector(0,0,0)*meter, radius=1.0*meter, color=color.RGB(1,1,1)):
    """
    Create a sphere object.

    Args:
        pos: the initial position of the sphere in meters (defaults
            to the origin)
        radius: the radius of the sphere in meters
        color: the color of the sphere
    Raises:
        Exception: the dimensions are not distances
    """
    check_units('position must have dimensions of distance', pos, meter)
    check_units('radius must have dimensions of distance', radius, meter)
    return __x.create_sphere(pos.copy(), radius, color.copy())

def helix(pos1, pos2,
          radius=0.1*meter, color=color.RGB(1,1,1),
          length=None,
          twists=10):
    """Create a helix object.

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

    Args:
        pos: the initial position of the center of the box
        wx: the width of the box in the x direction
        wy: the width of the box in the y direction
        wz: the width of the box in the z direction
        color: the color of the cylinder
    Raises:
        Exception: the dimensions are not distances
    """
    check_units('box dimensions must be distances',
                pos, wx, wy, wz, meter)
    return __x.create_box(pos, wx, wy, wz, color.copy())

def savepng(fname):
    __x._save(fname)

#: the minimum frames per second that the renderer will draw.
minimum_fps = 0.1/second
