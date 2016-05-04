from __future__ import division, print_function

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys, math

class vector(object):
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z
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
        s = float(s)
        return vector(self.x*s, self.y*s, self.z*s)
    def __rmul__(self, s):
        s = float(s)
        return vector(self.x*s, self.y*s, self.z*s)
    def __truediv__(self, s):
        s = float(s)
        return vector(self.x/s, self.y/s, self.z/s)

print(vector(1,2,3)/10)

class _quaternion(object):
    def __init__(self,w,v):
        norm = math.sqrt(w**2 + v.dot(v))
        self.w = w/norm
        self.v = v/norm # v is a vector
    def rotate(self,v):
        u = self.v.normalized()
        vpar = v.dot(u)*u
        vperp = v - vpar
        cosalpha = self.w
        sinalpha = self.v.abs()
        return vperp*cosalpha + u.cross(v)*sinalpha + vpar
    def __div__(self, s):
        s = float(s)
        return _quaternion(self.w/s, self.v/s)

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
        glPushMatrix()
        color = [1.0,0.,0.,1.]
        glMaterialfv(GL_FRONT,GL_DIFFUSE,color)
        glutSolidSphere(2,20,20)

        glTranslate(0,5,0)
        glutSolidSphere(2,20,20)
        glPopMatrix()
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

    def __onMouse(self, btn, state, x, y):
        print(btn, state, x, y)
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
            rotation = math.sqrt((dx**2 + dy**2)
                                 /
                                 (self.__windowsize[0]**2 + self.__windowsize[1]**2))
            print('rotation', rotation)
            q = _quaternion(1-rotation, direction*rotation)
            self.__camera = q.rotate(self.__camera)
            self.__up = q.rotate(self.__up)
            self.__x_origin = x
            self.__y_origin = y
            glutPostRedisplay()

    def init(self):
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

    def run(self):
        while True:
            # glutPostRedisplay()
            glutMainLoopEvent()

__x = __display()
__x.init()
__x.run()
