#!/usr/bin/python

import physical, time, numpy

s = physical.sphere()
s2 = physical.sphere()
origin = physical.sphere()
origin.radius = 0.1

s.x = 1.1

s2.x = -1.1

# t = 0
# dt = 0.001
# while True:
#     s.x = 2*numpy.sin(t)
#     s2.z = 3*numpy.cos(t)
#     time.sleep(dt)
#     t += dt
