#!/usr/bin/python

import time, numpy
from physical import *

cyl = cylinder(vector(0,0,0), vector(1,0,0)*meter,
               radius=0.05*meter, color=color.green)

s = sphere()
s2 = sphere()
s.color = color.blue
origin = sphere(radius=0.1*meter, color=color.red)

print(s.pos)
s.pos.x = 1.1*meter

s2.pos.x = -1.1*meter

h = helix(s, s2)

savepng('demo.png')

t = 0*second
dt = 0.001*second
omega = numpy.pi/second
while t < 9.5*second:
    s.pos.x = 3*meter*sin(2*omega*t)
    s2.pos.z = 3*meter*cos(omega*t)
    timestep(dt)
    t += dt
