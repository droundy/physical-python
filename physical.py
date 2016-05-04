from __future__ import division, print_function

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys, math

class __display(object):
    '''
    The private class __display exists to conveniently hide our
    "global" variables relating to camera state, etc.  In principle,
    this could allow us to support multiple windows, but in practice
    it is only intended for name-spacing.
    '''
    def __display(self):
        glPushMatrix()
        gluLookAt(self.__camera[0], self.__camera[1], self.__camera[2],
                  self.__center[0], self.__center[1], self.__center[2],
                  0, 0, 1)

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
        self.__center = [0,0,0]
        self.__camera = [0,10,0]

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
            sinphi = dx/self.__windowsize[0]
            if abs(sinphi) > 1:
                sinphi = sinphi/abs(sinphi)
            cosphi = math.sqrt(1 - sinphi**2)
            cx = self.__camera[0]*cosphi + self.__camera[1]*sinphi
            cy = -self.__camera[0]*sinphi + self.__camera[1]*cosphi
            r = math.sqrt(cx**2 + cy**2)
            sintheta = dx/self.__windowsize[1]
            if abs(sintheta) > 1:
                sintheta = sintheta/abs(sintheta)
            costheta = math.sqrt(1 - sintheta**2)
            cz = self.__camera[2]*costheta - r*sintheta
            cr = r*costheta + self.__camera[2]*sintheta
            cx = cx*cr/r
            cy = cy*cr/r
            self.__camera[0] = cx
            self.__camera[1] = cy
            self.__camera[2] = cz
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
