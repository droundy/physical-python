#!/usr/bin/python

import physical, time, numpy

s = physical.sphere()
s2 = physical.sphere()
origin = physical.sphere(radius=0.1*physical.meter, color=physical.red)

s.pos.x = 1.1

s2.pos.x = -1.1

exit(1)
t = 0
dt = 0.001
while t < 10:
    s.pos.x = 2*numpy.sin(2*numpy.pi*t)
    s2.pos.z = 2*numpy.cos(numpy.pi*t)
    physical.timestep(dt)
    t += dt
