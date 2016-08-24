from __future__ import division, print_function

from physical import *
import physical

import random

random.seed(0)

Rsun = 1000*meter
Rstar = 10*Rsun

day = 10*second

camera.windowsize=(400,300)

Rplanet = 200*meter
planet = sphere(vector(0*meter, 0*meter, 0*meter), radius=Rplanet, color=color.green)

sun = sphere(vector(-1,0,0)*Rsun, radius=0.1*Rsun, color=color.yellow)

longitude = 45*pi/180

camera.position = Rplanet*1.01*vector(cos(longitude),0,sin(longitude))
camera.center = sun.pos

stars = []

for i in range(50):
    pos = vector(random.gauss(0.0, 1.0), random.gauss(0.0, 1.0), random.gauss(0.0, 1.0))
    pos = pos*Rstar/abs(pos)

    s = sphere(pos, radius=0.01*Rstar, color=color.RGB(random.random(), random.random(), random.random()))
    stars.append(s)

# trees
for i in range(100):
    pos = vector(random.gauss(0.0, 1.0), random.gauss(0.0, 1.0), random.gauss(0.0, 1.0))
    pos = camera.position + 0.1*Rplanet*pos
    pos = pos*Rplanet/abs(pos)
    h = random.gauss(1.0, 0.5)*meter
    # print(x,y,h)
    sphere(pos + h*pos/abs(pos), radius = h/3, color=color.green)
    cylinder(pos, pos + h*pos/abs(pos), color=color.gray, radius=0.1*meter)

t=0*second
dt=second/60.0

omegaz = 2*pi/day
anisotropy = 1
Omega = omegaz*anisotropy # assume I3 = 2*I1
omega_theta = pi/3
tantheta = tan(omega_theta)

class rotation(object):
    def __init__(self,angle,axis):
        self.angle = angle
        self.axis = axis.normalized()
    def rotate(self,v):
        vpar = v.dot(self.axis)*self.axis
        vperp = v - vpar
        cosalpha = cos(self.angle)
        sinalpha = sin(self.angle)
        return vperp*cosalpha + self.axis.cross(v)*sinalpha + vpar

while t < 10*60*second:
    camera.position = Rplanet*1.01*camera.position/abs(camera.position)

    looking = camera.center - camera.position
    looking = -looking.cross(camera.position).cross(camera.position)/abs(camera.position)**2
    looking += 1.5*camera.position
    camera.center = looking

    camera.up = camera.position

    omega = vector(omegaz*tantheta*cos(Omega*t), omegaz*tantheta*sin(Omega*t), omegaz)
    R = rotation(abs(omega*dt).v, omega)

    sun.pos = R.rotate(sun.pos)
    for s in stars:
        s.pos = R.rotate(s.pos)

    lightness = camera.position.dot(sun.pos)/abs(camera.position)/abs(sun.pos)

    timestep(dt)
    t += dt
