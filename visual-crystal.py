#!/usr/bin/python

from __future__ import division, print_function

import time, os
from visual import *

Newton = 1
meter = 1
second = 1
kg = 1

N = 2
kspring = 10*Newton/meter
L = 1*meter
mass = .1*kg

balls = []
all_balls = []
springs = []
for i in range(N):
    balls.append([])
    for j in range(N):
        balls[-1].append([])
        for k in range(N):
            s = sphere(pos=vector(i-N/2,j-N/2,k-N/2)*meter,
                       radius=0.2*meter,
                       color=color.blue)
            s.v = vector(0,0,0)*meter/second
            balls[-1][-1].append(s)
            all_balls.append(s)
            if i > 0:
                h = helix(s.pos, radius=0.1*meter)
                h.thickness = 0.02*meter
                h.pos1 = s
                h.pos2 = balls[i-1][j][k]
                h.axis = h.pos2.pos - h.pos1.pos
                springs.append(h)
            if j > 0:
                h = helix(s.pos, radius=0.1*meter)
                h.thickness = 0.02*meter
                h.pos1 = s
                h.pos2 = balls[i][j-1][k]
                h.axis = h.pos2.pos - h.pos1.pos
                springs.append(h)
            if k > 0:
                h = helix(s.pos, radius=0.1*meter)
                h.thickness = 0.02*meter
                h.pos1 = s
                h.pos2 = balls[i][j][k-1]
                h.axis = h.pos2.pos - h.pos1.pos
                springs.append(h)

#set_range(2*N*meter)

all_balls[0].pos += vector(0.01,0.02,0.03)*meter
all_balls[1].pos -= vector(0.01,0.02,0.03)*meter

last_printed = 0
t = 0*second
dt = 0.001*second
while t < 10.0*second:
    for b in all_balls:
        b.F = vector(0,0,0)*Newton
    for b in all_balls:
        for b2 in all_balls:
            if b.pos != b2.pos:
                dr = b2.pos - b.pos
                dist = abs(dr)
                F = 0.1*L**5*dr/dist**6*Newton
                b2.F += F
                b.F -= F
    for h in springs:
        dr = h.pos2.pos - h.pos1.pos
        dist = abs(dr)
        F = kspring*(dist - L)*dr/dist
        h.pos2.F -= F
        h.pos1.F += F
        h.pos = h.pos1.pos
        h.axis = h.pos2.pos - h.pos
    for b in all_balls:
        b.pos += b.v*dt
        b.v += b.F*dt/mass
    rate(1/dt)
    t += dt
    if int(t/second) > last_printed:
        last_printed = int(t/second)
        print('time is', t)

#exit_visualization()
os.system('killall visual-crystal.py')
