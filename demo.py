#!/usr/bin/python

import physical, time, numpy

s = physical.sphere()
s2 = physical.sphere()

t = 0
dt = 0.001
while True:
    s.x = 2*numpy.sin(t)
    s2.y = 3*numpy.cos(t)
    time.sleep(dt)
    t += dt
