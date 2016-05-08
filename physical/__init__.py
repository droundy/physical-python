from __future__ import division, print_function

__all__ = ('scalar', 'vector',
           'color',
           'check_units', 'dimensionless',
           'sqrt', 'sin', 'cos', 'tan', 'atan2',
           'sphere',
           'timestep',
           'meter', 'second', 'kg')

import OpenGL.GLUT as glut
import OpenGL.GLU as glu
import OpenGL.GL as gl
import sys, math, atexit, time, numpy, traceback
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
        self.mks = (m,kg,s)
    def _add(self, b):
        if self.mks != units(b):
            raise Exception('you cannot add quantities with differing units: {} + {}'.format(self,b))
        return self.mks
    def _sub(self, b):
        if self.mks != units(b):
            raise Exception('you cannot subtract quantities with differing units: {} + {}'.format(self,b))
        return self.mks
    def _mul(self, b):
        a = self.mks
        b = units(b)
        return (a[0]+b[0], a[1]+b[1], a[2]+b[2])
    def _div(self, b):
        a = self.mks
        b = units(b)
        return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
    def _rdiv(self, b):
        a = self.mks
        b = units(b)
        return (b[0]-a[0], b[1]-a[1], b[2]-a[2])
    def _pow(self, b):
        if units(b) != (0,0,0):
            raise Exception('you cannot take quantity to a power with dimensions %s' % Units.__repr__(b))
        a = self.mks
        return (a[0]*b, a[1]*b, a[2]*b)
    def _eq(self, b):
        return self.mks == b.mks
    def _repr(self):
        (m,kg,s) =self.mks
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
    if hasattr(v, 'mks'):
        return v.mks
    return (0,0,0)
def value(v):
    if hasattr(v, 'v'):
        return v.v
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
        return not ((not hasattr(v, 'mks') and v == 0)
                    or (type(v) == vector and v.mks == (0,0,0) and
                        v.x == 0 and v.y == 0 and v.z == 0))
    vals = list(filter(is_not_boring, vals))
    if len(vals) >= 2:
        mks = units(vals[0])
        for v in vals[1:]:
            if units(v) != mks:
                raise Exception(err + ': %s vs %s' % (v, vals[0]))
    return True

def __is_not_boring(v):
    return not ((not hasattr(v, 'mks') and v == 0)
                or (type(v) == vector and v.mks == (0,0,0) and
                    v.x == 0 and v.y == 0 and v.z == 0))
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
        self.mks = mks
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
        return scalar(b*self.v, self.mks)
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
    '''The square root of a value.'''
    return v**0.5

@dimensionless('argument to sin must be dimensionless')
def sin(x):
    '''The sine of a value.'''
    return numpy.sin(value(x))

@dimensionless('argument to cos must be dimensionless')
def cos(x):
    '''The cosine of a value.'''
    return numpy.cos(value(x))

@dimensionless('argument to tan must be dimensionless')
def tan(x):
    '''The tangent of a value.'''
    return numpy.cos(value(x))

@units_match('arguments to atan2 must have the same units')
def atan2(y,x):
    '''The inverse tangent of a y/x.

    You should almost always prefer 'atan2' over any other inverse
    trig functions, because it can (and does) properly determine the
    quadrant of the point described by the angle, so it can give you
    an unambiguous answer.  For this reason we do not export any of
    the other inverse trig functions.

    '''
    return numpy.atan2(value(y)/value(x))

meter = scalar(1, (1, 0, 0))
kg = scalar(1, (0, 1, 0))
second = scalar(1, (0, 0, 1))

class vector(Units):
    def __init__(self,x,y,z, mks=(0,0,0)):
        check_units('vector components must have same dimensions', x,y,z)
        self.mks = mks
        if mks == (0,0,0):
            if units(x) != mks:
                self.mks = units(x)
            elif units(y) != mks:
                self.mks = units(y)
            elif units(z) != mks:
                self.mks = units(z)
        self._x = value(x)
        self._y = value(y)
        self._z = value(z)
    @property
    def x(self):
        return scalar(self._x, self.mks)
    @x.setter
    @units_match('x component must have dimensions of vector')
    def x(self,v):
        self._x = value(v)

    @property
    def y(self):
        return scalar(self._y, self.mks)
    @y.setter
    @units_match('y component must have dimensions of vector')
    def y(self,v):
        self._y = value(v)

    @property
    def z(self):
        return scalar(self._z, self.mks)
    @z.setter
    @units_match('z component must have dimensions of vector')
    def z(self,v):
        self._z = value(v)
    def cross(self,b):
        return vector(self.y*b.z - self.z*b.y,
                      self.z*b.x - self.x*b.z,
                      self.x*b.y - self.y*b.x, Units._mul(self, b))
    def dot(self,b):
        return self.x*b.x + self.y*b.y + self.z*b.z
    def abs(self):
        return scalar(math.sqrt(self.x.v**2 + self.y.v**2 + self.z.v**2), self.mks)
    def normalized(self):
        return self / self.abs()
    def __add__(self, b):
        check_units('can only add vectors with same dimensions', b, self)
        return vector(self._x+b._x, self._y + b._y, self._z + b._z, self.mks)
    def __sub__(self, b):
        return vector(self.x-b.x, self.y - b.y, self.z - b.z)
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
        return type(b) == vector and self.mks == b.mks and self._x == b._x and self._y == b._y and self._z == b._z
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

class __display(object):
    '''
    The private class __display exists to conveniently hide our
    "global" variables relating to camera state, etc.  In principle,
    this could allow us to support multiple windows, but in practice
    it is only intended for name-spacing.
    '''
    def __display(self):
        gl.glPushMatrix()
        glu.gluLookAt(value(self.__camera.x), value(self.__camera.y), value(self.__camera.z),
                  value(self.__center.x), value(self.__center.y), value(self.__center.z),
                  value(self.__up.x), value(self.__up.y), value(self.__up.z))

        lightZeroPosition = [10.,4.,10.,1.]
        lightZeroColor = [0.8,1.0,0.8,1.0] #green tinged
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, lightZeroPosition)
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE, lightZeroColor)
        gl.glLightf(gl.GL_LIGHT0, gl.GL_CONSTANT_ATTENUATION, 0.1)
        gl.glLightf(gl.GL_LIGHT0, gl.GL_LINEAR_ATTENUATION, 0.05)
        gl.glEnable(gl.GL_LIGHT0)

        gl.glClear(gl.GL_COLOR_BUFFER_BIT|gl.GL_DEPTH_BUFFER_BIT)
        # gl.glPushMatrix()
        # color = [1.0,0.,0.,1.]
        # gl.glMaterialfv(gl.GL_FRONT,gl.GL_DIFFUSE,color)
        # glut.glutSolidSphere(.5,20,20)

        # gl.glTranslate(0,5,0)
        # glut.glutSolidSphere(.5,20,20)
        # gl.glPopMatrix()

        for o in self.__objects:
            o._draw()

        gl.glPopMatrix()
        glut.glutSwapBuffers()

    def __init__(self, name = b'physical python'):
        self.__name = name
        self.__am_rotating = False
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

    def __onMouse(self, btn, state, x, y):
        if btn == glut.GLUT_LEFT_BUTTON:
            if state == glut.GLUT_DOWN:
                self.__am_rotating = True
                self.__x_origin = x
                self.__y_origin = y
            elif state == glut.GLUT_UP:
                self.__am_rotating = False
    def __onMouseMotion(self, x, y):
        if self.__am_rotating:
            dx = x - self.__x_origin
            dy = y - self.__y_origin
            if dx == 0 and dy == 0:
                return
            yhat = self.__up.normalized()
            xhat = self.__up.cross((self.__center - self.__camera).normalized())
            direction = (dy*xhat - dx*yhat).normalized()
            angle = 5*math.sqrt((dx**2 + dy**2)
                                /
                                (self.__windowsize[0]**2 + self.__windowsize[1]**2))
            R = _rotation(angle, direction)
            self.__camera = R.rotate(self.__camera)
            self.__up = R.rotate(self.__up)
            self.__x_origin = x
            self.__y_origin = y
            glut.glutPostRedisplay()

    def init(self):
        if not self.__is_initialized:
            self.__is_initialized = True
            sys.argv = glut.glutInit(sys.argv)
            glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH)
            self.__windowsize = (400,400)
            glut.glutInitWindowSize(self.__windowsize[0],self.__windowsize[1])
            glut.glutCreateWindow(self.__name)

            gl.glClearColor(0.,0.,0.,1.)
            gl.glShadeModel(gl.GL_SMOOTH)
            gl.glEnable(gl.GL_CULL_FACE)
            gl.glEnable(gl.GL_DEPTH_TEST)
            gl.glEnable(gl.GL_LIGHTING)

            glut.glutDisplayFunc(self.__display)
            glut.glutMouseFunc(self.__onMouse)
            glut.glutMotionFunc(self.__onMouseMotion)

            gl.glMatrixMode(gl.GL_PROJECTION)
            glu.gluPerspective(40.,1.,1.,40.)
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glPushMatrix()
            def sleep_forever():
                if not self.__window_closed:
                    print('program complete, but still running visualization...')
                    while True:
                        glut.glutMainLoopEvent()
            atexit.register(sleep_forever)

    def timestep(self, dt):
        self.__current_time += dt.v
        now = time.time()
        if now < self.__current_time:
            glut.glutPostRedisplay()
            # print('waiting', self.__current_time - now)
            time.sleep(self.__current_time - now)
            # print('one frame took', time.time() - self.__last_time)
            self.__last_time = time.time()
        else:
            # print('I am late!')
            pass
        glut.glutMainLoopEvent()
    def create_sphere(self, pos, radius, color):
        s = _Sphere(pos, radius, color)
        self.__objects.append(s)
        self.init()
        return s

__x = __display()

def timestep(dt):
    """Advance the simulation by time dt.

    Args:
        dt: the time in seconds (as a scalar) to advance

    You *must* call 'timestep' regularly in order for your simulation
    to be animated.  'timestep' also performs a number of cleanup
    tasks, such as allowing user interaction with the visualization.

    """
    check_units('time step dt must be a time', dt, second)
    return __x.timestep(dt)

def sphere(pos = vector(0,0,0)*meter, radius=1.0*meter, color=color.RGB(1,1,1)):
    """Create a sphere object.

    Args:
        pos: the initial position of the sphere in meters (defaults
            to the origin)
        radius: the radius of the sphere in meters
        color: the color of the sphere
    """
    check_units('position must have dimensions of distance', pos, meter)
    check_units('radius must have dimensions of distance', radius, meter)
    return __x.create_sphere(pos.copy(), radius, color.copy())
