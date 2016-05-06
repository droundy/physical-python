#!/usr/bin/python

import time, numpy
from physical import *

s = sphere()
s2 = sphere()
origin = sphere(radius=0.1*meter, color=red)

print(s.pos)
s.pos.x = 1.1*meter

s2.pos.x = -1.1*meter

t = 0
dt = 0.001
while t < 10:
    s.pos.x = 2*meter*numpy.sin(2*numpy.pi*t)
    s2.pos.z = 2*meter*numpy.cos(numpy.pi*t)
    timestep(dt)
    t += dt
