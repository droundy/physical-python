#!/usr/bin/python

import time, numpy
from physical import *

cyl = cylinder(vector(0,0,0), vector(1,0,0)*meter,
               radius=0.05*meter, color=color.green)

s = sphere()
s2 = sphere()
s.color = color.blue
origin = sphere(radius=0.1*meter, color=color.red)

b = box(vector(0, 0, -1)*meter, 3*meter, 3*meter, 0.2*meter, color.yellow)

s.pos.x = 1.1*meter

inch = 0.0254*meter

print(s.pos/inch,'inches')

s2.pos.x = -1.1*meter

h = helix(s, s2)

savepng('/tmp/demo.png')

xplot = plot(color.white)
hline(0*meter, color.RGB(0.3,0.3,0.3))

camera.center = s
camera.range = 20*meter

t = 0*second
dt = 0.001*second
omega = numpy.pi/second/5

tr = trail(s2)
tr.duration = 3.5*second
tr = trail(s)
tr.duration = 3.25*second
while t < 9.8*second:
    s.pos.x = 3*meter*sin(2*omega*t)
    s2.pos.z = 3*meter*cos(omega*t)
    timestep(dt)
    t += dt
    xplot.plot(t, s.pos.x)
