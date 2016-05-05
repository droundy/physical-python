from __future__ import division, print_function

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys, math, atexit, time, numpy

def units(value, m, kg, s):
    if m == 0 and kg == 0 and s == 0:
        return value
    return Units(value, m, kg, s)
def has_dimensions(a,b):
    if type(a) != Units and type(b) != Units:
        return True
    if type(a) != type(b):
        return False
    return a.m == b.m and a.kg == b.kg and a.s == b.s
def is_vector(v):
    if type(v) == Units:
        v = v.value
    return type(v) == vector
def is_scalar(s):
    return not is_vector(s)
class Units(object):
    def __init__(self, value, m, kg, s):
        self.value = value
        self.m = m
        self.kg = kg
        self.s = s
    def __add__(self, b):
        if type(b) != Units or self.m != b.m or self.kg != b.kg or self.s != b.s:
            raise Exception('you cannot add quantities with differing units: {} + {}'.format(self,b))
        return units(self.value + b.value, self.m, self.kg, self.s)
    def __sub__(self, b):
        if self.m != b.m or self.kg != b.kg or self.s != b.s:
            raise Exception('you cannot subtract quantities with differing units:')
        return units(self.value - b.value, self.m, self.kg, self.s)
    def __mul__(self, b):
        if type(b) == Units:
            return units(self.value*b.value, self.m+b.m, self.kg+b.kg, self.s+b.s)
        return units(self.value*b, self.m, self.kg, self.s)
    def __rmul__(self, b):
        if type(b) == Units:
            return units(b.value*self.value, self.m+b.m, self.kg+b.kg, self.s+b.s)
        return units(b*self.value, self.m, self.kg, self.s)
    def __pow__(self, b):
        if type(b) == Units:
            raise Exception('you can only raise a quantity to a dimensionless power')
        return units(self.value**b, self.m*b, self.kg*b, self.s*b)
    def __eq__(self, b):
        return self.value == b.value and self.m == b.m and self.kg == b.kg and self.s == b.s
    def __repr__(self):
        s = repr(self.value)
        if self.m == 1:
            s += '*meter'
        elif self.m != 0:
            s += '*meter**({})'.format(self.m)
        if self.kg == 1:
            s += '*kg'
        elif self.kg != 0:
            s += '*kg**({})'.format(self.kg)
        if self.s == 1:
            s += '*second'
        elif self.s != 0:
            s += '*second**({})'.format(self.s)
        return s
    def copy(self):
        return units(self.value.copy(), self.m, self.kg, self.s)
    def __getattr__(self, name):
        if name == 'x':
            return self.value.x

meter = units(1, 1, 0, 0)
kg = units(1, 0, 1, 0)
second = units(1, 0, 0, 1)

class vector(object):
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z
    # def __init__(self,x,y,z):
    #     object.__setattr__(self, '_vector__v', numpy.array([x,y,z]))
    # def __getattr__(self, name):
    #     if name == 'x':
    #         return self.__v[0]
    #     if name == 'y':
    #         return self.__v[1]
    #     if name == 'z':
    #         return self.__v[2]
    # def __setattr__(self, name, value):
    #     if name == 'x':
    #         self.__v[0] = value
    #     if name == 'y':
    #         self.__v[1] = value
    #     if name == 'z':
    #         self.__v[2] = value
    def cross(self,b):
        return vector(self.y*b.z - self.z*b.y,
                      self.z*b.x - self.x*b.z,
                      self.x*b.y - self.y*b.x)
    def dot(self,b):
        return self.x*b.x + self.y*b.y + self.z*b.z
    def abs(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    def normalized(self):
        return self / self.abs()
    def __add__(self, b):
        return vector(self.x+b.x, self.y + b.y, self.z + b.z)
    def __sub__(self, b):
        return vector(self.x-b.x, self.y - b.y, self.z - b.z)
    def __mul__(self, s):
        if not is_scalar(s):
            raise Exception('can only multipy vectors with scalars')
        if type(s) == Units:
            return units(self*s.value, s.m, s.kg, s.s)
        return vector(self.x*s, self.y*s, self.z*s)
    def __rmul__(self, s):
        if not is_scalar(s):
            raise Exception('can only multipy vectors with scalars')
        return vector(self.x*s, self.y*s, self.z*s)
    def __truediv__(self, s):
        if not is_scalar(s):
            raise Exception('can only divide vectors by scalars')
        return vector(self.x/s, self.y/s, self.z/s)
    def __repr__(self):
        return '<%g,%g,%g>' % (self.x, self.y, self.z)
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

class _Color(object):
    def __init__(self, r,g,b):
        self.r = r; self.g = g; self.b = b
    def asarray(self):
        return [self.r, self.g, self.b]
    def copy(self):
        return _Color(self.r, self.g, self.b)

class _Sphere(object):
    def __init__(self, pos, radius, color):
        # if not has_dimensions(pos, meter):
        #     raise Exception('position must have dimensions of distance')
        # if not has_dimensions(radius, meter):
        #     raise Exception('radius must have dimensions of distance')
        self.pos = pos
        self.radius = radius
        self.color = color
    def __str__(self):
        return 'sphere(%s, %s)' % (self.pos, self.radius)
    def _draw(self):
        # use a fresh transformation matrix
        glPushMatrix()
        # position object
        glTranslate(self.pos.x, self.pos.y, self.pos.z)
        glMaterialfv(GL_FRONT,GL_DIFFUSE,self.color.asarray())
        glutSolidSphere(self.radius, 60, 60)
        glPopMatrix()
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
        glPushMatrix()
        gluLookAt(self.__camera.x, self.__camera.y, self.__camera.z,
                  self.__center.x, self.__center.y, self.__center.z,
                  self.__up.x, self.__up.y, self.__up.z)

        lightZeroPosition = [10.,4.,10.,1.]
        lightZeroColor = [0.8,1.0,0.8,1.0] #green tinged
        glLightfv(GL_LIGHT0, GL_POSITION, lightZeroPosition)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor)
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
        glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
        glEnable(GL_LIGHT0)

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        # glPushMatrix()
        # color = [1.0,0.,0.,1.]
        # glMaterialfv(GL_FRONT,GL_DIFFUSE,color)
        # glutSolidSphere(.5,20,20)

        # glTranslate(0,5,0)
        # glutSolidSphere(.5,20,20)
        # glPopMatrix()

        for o in self.__objects:
            o._draw()

        glPopMatrix()
        glutSwapBuffers()

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
        if btn == GLUT_LEFT_BUTTON:
            if state == GLUT_DOWN:
                self.__am_rotating = True
                self.__x_origin = x
                self.__y_origin = y
            elif state == GLUT_UP:
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
            glutPostRedisplay()

    def init(self):
        if not self.__is_initialized:
            self.__is_initialized = True
            sys.argv = glutInit(sys.argv)
            glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
            self.__windowsize = (400,400)
            glutInitWindowSize(self.__windowsize[0],self.__windowsize[1])
            glutCreateWindow(self.__name)

            glClearColor(0.,0.,0.,1.)
            glShadeModel(GL_SMOOTH)
            glEnable(GL_CULL_FACE)
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_LIGHTING)

            glutDisplayFunc(self.__display)
            glutMouseFunc(self.__onMouse)
            glutMotionFunc(self.__onMouseMotion)

            glMatrixMode(GL_PROJECTION)
            gluPerspective(40.,1.,1.,40.)
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            def sleep_forever():
                if not self.__window_closed:
                    print('program complete, but still running visualization...')
                    while True:
                        glutMainLoopEvent()
            atexit.register(sleep_forever)

    def timestep(self, dt):
        self.__current_time += dt
        now = time.time()
        if now < self.__current_time:
            glutPostRedisplay()
            # print('waiting', self.__current_time - now)
            time.sleep(self.__current_time - now)
            # print('one frame took', time.time() - self.__last_time)
            self.__last_time = time.time()
        else:
            # print('I am late!')
            pass
        glutMainLoopEvent()
    def create_sphere(self, pos, radius, color):
        s = _Sphere(pos, radius, color)
        self.__objects.append(s)
        self.init()
        return s

__x = __display()

def timestep(dt):
    return __x.timestep(dt)

def sphere(pos = vector(0,0,0), radius=1.0, color=_Color(1,1,1)):
    # if not has_dimensions(pos, meter):
    #     print(pos)
    #     raise Exception('position must have dimensions of distance')
    # if not has_dimensions(radius, meter):
    #     raise Exception('radius must have dimensions of distance')

    # the "copy" bit below is needed to ensure that each sphere has
    # its own position.
    return __x.create_sphere(pos.copy(), radius, color.copy())

red = _Color(1,0,0)
