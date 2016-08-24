from __future__ import division, print_function

from physical import *
import physical

import random

random.seed(0)

Rsun = 1000*meter
Rstar = 10*Rsun

day = 30*second

camera.windowsize=(400,300)

Rplanet = 200*meter
planet = sphere(vector(0*meter, 0*meter, 0*meter), radius=Rplanet, color=color.green)

sun = sphere(vector(-1,1,0)*Rsun, radius=0.02*Rsun, color=color.yellow)
trail(sun, duration=5*day, dash_time = 1*second)
sun.glows = True

longitude = 45*pi/180

camera.position = Rplanet*1.01*vector(cos(longitude),0,sin(longitude))
camera.center = sun.pos

north = sphere( 2*vector(0,0,1)*Rsun, radius = .15*Rsun, color=color.red)
south = sphere(-2*vector(0,0,1)*Rsun, radius = .15*Rsun, color=color.magenta)
east = sphere( 2*vector(0,1,0)*Rsun, radius = .15*Rsun, color=color.RGB(.5,.5,0))
west = sphere(-2*vector(0,1,0)*Rsun, radius = .15*Rsun, color=color.cyan)
north.glows = True
south.glows = True
east.glows = True
west.glows = True

stars = []

for i in range(50):
    pos = vector(random.gauss(0.0, 1.0), random.gauss(0.0, 1.0), random.gauss(0.0, 1.0))
    pos = pos*Rstar/abs(pos)

    s = sphere(pos, radius=0.002*Rstar, color=color.RGB(random.random(), random.random(), random.random()))
    s.glows = True
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
skipiter = 1
dt=second/60.0/skipiter

omegaz = 2*pi/day
anisotropy = 1 # = (I3 - I1)/I1, assume I3 = 2*I1, a slightly football-shaped planet
Omega = omegaz*anisotropy
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

iter = 0
is_night = True
last_event = t
while True:
    camera.position = Rplanet*1.01*camera.position/abs(camera.position)

    west.pos = 2*vector(0,1,0)*Rsun
    north.pos = camera.position.cross(west.pos)/abs(camera.position)
    south.pos = -north.pos
    east.pos = -west.pos

    lightness = camera.position.dot(sun.pos)/abs(camera.position)/abs(sun.pos)

    camera.center = sun.pos
    if lightness < 0:
        looking = camera.center - camera.position
        looking = -looking.cross(camera.position).cross(camera.position)/abs(camera.position)**2
        #looking += 1.5*camera.position
        camera.center = looking

    camera.up = camera.position

    omega = vector(omegaz*tantheta*cos(Omega*t), omegaz*tantheta*sin(Omega*t), omegaz)
    R = rotation(abs(omega*dt).v, omega)

    sun.pos = R.rotate(sun.pos)
    for s in stars:
        s.pos = R.rotate(s.pos)

    thetime = '%d:%02d' % (int(t/day*24) % 24, int(t/day*24*60) % 60)
    daytime = '%d:%02d' % (int((t-last_event)/day*24) % 24, int((t-last_event)/day*24*60) % 60)
    northness = sun.pos.dot(north.pos)
    eastness = sun.pos.dot(east.pos)
    if northness > 0:
        nsdirection = 'north'
    else:
        nsdirection = 'south'
    if eastness > 0:
        ewdirection = 'east'
    else:
        ewdirection = 'west'
    if abs(eastness) > 1.4*abs(northness):
        direction = ewdirection
    elif abs(northness) > 1.4*abs(eastness):
        direction = nsdirection
    else:
        direction = nsdirection+ewdirection
    if lightness > 0 and is_night:
        if last_event != 0*second:
            print('sunrise at', thetime, 'in', direction, 'after', daytime)
        is_night = False
        last_event = t
    if lightness < 0 and not is_night:
        if last_event != 0*second:
            print('sunset at', thetime, 'in', direction, 'after', daytime)
        is_night = True
        last_event = t
    if lightness > .5:
        display.background = color.RGB(lightness-.5, lightness-.5, 1)
    elif lightness > .3:
        display.background = color.RGB(0, 0, lightness*2)
    elif lightness > 0:
        display.background = color.RGB(.3 - lightness, 0, lightness*2)
    elif lightness > -.3:
        display.background = color.RGB(.3 + lightness, 0, 0)
    else:
        display.background = color.black
    sunrise_print_delay = 1.5*second
    if not is_night and (t-last_event) > sunrise_print_delay and (t-last_event) < sunrise_print_delay + dt:
        print('saving png')

    iter += 1
    if iter % skipiter == 0:
        timestep(10*dt)
    t += dt
