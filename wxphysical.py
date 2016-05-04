import numpy
import wx
import numpy
import threading
import time
import sys
import atexit

from wx import glcanvas
import OpenGL.GL as gl
import OpenGL.GLUT as glut

class _wxThread(threading.Thread):
    """Run the MainLoop as a thread. Access the frame with self.frame."""
    def __init__(self, autoStart=True):
        threading.Thread.__init__(self)
        self.setDaemon(1)
        self.start_orig = self.start
        self.start = self.start_local
        self.frame = None #to be defined in self.run
        if autoStart:
            self.start() #automatically start thread on init
    def run(self):
        app = _PhysicalApp()

        app.MainLoop()

    def start_local(self):
        self.start_orig()

# the following global variable tells the main thread whether the
# window was intentionally closed by the user.
_window_closed = False

def _runWxThread():
    """MainLoop run as a thread. SetData function is returned."""

    vt = _wxThread() #run wx MainLoop as thread

    # The following enables the window to stay open after the user's
    # program has completed.
    def sleep_forever():
        if not _window_closed:
            print('program complete, but still running visualization...')
            while True:
                time.sleep(60)
    atexit.register(sleep_forever)

class _PhysicalCanvas(glcanvas.GLCanvas):
    def __init__(self, parent):
        # the attribList is hardly documented, but the following seems
        # to work.
        attribList=(glcanvas.WX_GL_RGBA,
                    glcanvas.WX_GL_DOUBLEBUFFER,
                    glcanvas.WX_GL_DEPTH_SIZE, 24)
        glcanvas.GLCanvas.__init__(self, parent, -1, attribList=attribList)
        self.init = False
        self.context = glcanvas.GLContext(self)
        self.timer = wx.Timer(self)
        self.timer.Start(100)
        self.Bind(wx.EVT_TIMER, self.OnTimer) # just repaint ever so often

        # initial mouse position
        self.lastx = self.x = 30
        self.lasty = self.y = 30
        self.size = None
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)

    def OnEraseBackground(self, event):
        pass # Do nothing, to avoid flashing on MSW.

    def OnSize(self, event):
        wx.CallAfter(self.DoSetViewport)
        event.Skip()

    def DoSetViewport(self):
        size = self.size = self.GetClientSize()
        self.SetCurrent(self.context)
        gl.glViewport(0, 0, size.width, size.height)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        self.SetCurrent(self.context)
        self.OnDraw()

    def OnTimer(self, event):
        self.Refresh()

    def OnMouseDown(self, evt):
        self.CaptureMouse()
        self.x, self.y = self.lastx, self.lasty = evt.GetPosition()

    def OnMouseUp(self, evt):
        self.ReleaseMouse()

    def OnMouseMotion(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            self.lastx, self.lasty = self.x, self.y
            self.x, self.y = evt.GetPosition()
            self.Refresh(False)

    def InitGL( self ):
        gl.glMatrixMode(gl.GL_PROJECTION)
        # camera frustrum setup
        gl.glFrustum(-0.5, 0.5, -0.5, 0.5, 1, 10.0)
        gl.glMaterial(gl.GL_FRONT, gl.GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        gl.glMaterial(gl.GL_FRONT, gl.GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        gl.glMaterial(gl.GL_FRONT, gl.GL_SPECULAR, [1.0, 0.0, 1.0, 1.0])
        gl.glMaterial(gl.GL_FRONT, gl.GL_SHININESS, 50.0)
        gl.glLight(gl.GL_LIGHT0, gl.GL_AMBIENT, [1.0, 1.0, 1.0, 1.0])
        gl.glLight(gl.GL_LIGHT0, gl.GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        gl.glLight(gl.GL_LIGHT0, gl.GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        gl.glLight(gl.GL_LIGHT0, gl.GL_POSITION, [1.0, 1.0, 1.0, 0.0])
        gl.glLightModelfv(gl.GL_LIGHT_MODEL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        gl.glEnable(gl.GL_LIGHTING)
        gl.glEnable(gl.GL_LIGHT0)
        gl.glDepthFunc(gl.GL_LESS)

        gl.glClearDepth(1.0) # enables clearing of the depth buffer?
        gl.glShadeModel(gl.GL_SMOOTH)

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # position viewer
        gl.glMatrixMode(gl.GL_MODELVIEW)
        # position viewer
        gl.glTranslate(0.0, 0.0, -3.0);
        #
        glut.glutInit(sys.argv)


    def OnDraw(self):
        if not self.init:
            self.InitGL()
            self.init = True
        #self.InitGL()
        # clear color and depth buffers
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

                # use a fresh transformation matrix
        gl.glPushMatrix()
        # # position object
        # #gl.glTranslate(0.0, 0.0, -2.0)
        # gl.glRotate(30.0, 1.0, 0.0, 0.0)
        # gl.glRotate(30.0, 0.0, 1.0, 0.0)

        # gl.glTranslate(0, -1, 0)
        # gl.glRotate(250, 1, 0, 0)
        glut.glutSolidCone(0.5, 1, 30, 5)
        gl.glPopMatrix()

        for s in _spheres:
            # use a fresh transformation matrix
            gl.glPushMatrix()
            # position object
            gl.glTranslate(s.x, s.y, s.z)
            glut.glutSolidSphere(s.radius, 60, 60)
            gl.glPopMatrix()

        # rotate the camera
        gl.glRotate((self.y - self.lasty), 0.0, 0.0, 1.0);
        gl.glRotate((self.x - self.lastx), 1.0, 0.0, 0.0);
        # push into visible buffer
        self.SwapBuffers()

#----------------------------------------------------------------------
class _PhysicalApp(wx.App):
    def __init__(self):
        wx.App.__init__(self, redirect=False)

    def OnInit(self):
        frame = wx.Frame(None, -1, "Physical Python", pos=(0,0),
                        style=wx.DEFAULT_FRAME_STYLE, name="run simulation")
        #frame.CreateStatusBar()

        frame.Show(True)
        frame.Bind(wx.EVT_CLOSE, self.OnCloseFrame)

        win = _PhysicalCanvas(frame)

        # set the frame to a good size
        frame.SetSize((600,600))
        win.SetFocus()
        self.window = win
        frect = frame.GetRect()

        self.SetTopWindow(frame)
        self.frame = frame

        return True

    def OnExitApp(self, evt):
        self.frame.Close(True)

    def OnCloseFrame(self, evt):
        print('All done!')
        global _window_closed
        _window_closed = True
        exit(0)
        evt.Skip()

class Sphere(object):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.radius = 1


_spheres = []

def sphere():
    s = Sphere()
    _spheres.append(s)
    return s

_runWxThread()
