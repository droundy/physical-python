from __future__ import division, print_function

from physical import *
import random

height = 960*meter
delay_time = 5*second

mph = 0.44704*meter/second

wizard = sphere(vector(0*meter, 0*meter, height), radius=1*meter, color=color.red)
victim = sphere(vector(3*meter, 0*meter, height), radius=1*meter, color=color.blue)

for i in range(100):
    x, y = random.gauss(0.0, 1.0)*height/8, random.gauss(0.0, 1.0)*height/8
    h = random.gauss(10.0, 5.0)*meter
    # print(x,y,h)
    sphere(vector(x,y,h), radius = h/3, color=color.green)
    cylinder(vector(x,y,0*meter), vector(x,y,h), color=color.gray, radius=1*meter)

ground = box(pos=vector(0,0,0)*meter,
             wx=height, wy=height, wz=1*meter, color=color.green)

# camera.range = 3*height
camera.center = victim
camera.position = wizard.pos + vector(1*meter, 5*meter, 15*meter)

t=0*second
dt=0.01*second

g = vector(0,0,-9.8)*meter/second**2
wizard.v = vector(0,0,0)*meter/second
victim.v = vector(0,0,0)*meter/second

def drag(v, terminal):
    return -abs(v)*v*abs(g)/terminal**2

while t < 10*60*second and victim.pos.z > 0:
    victim.v += (g + drag(victim.v, 120*mph))*dt
    if t > delay_time:
        wizard.v += (2.11*g + drag(victim.v, 150*mph))*dt
        if abs(wizard.pos - victim.pos) < 5*meter:
            print('got ya!')
            break
        # else:
        #     print('so far', abs(wizard.pos - victim.pos))
    victim.pos += victim.v*dt
    wizard.pos += wizard.v*dt
    timestep(dt)
    t += dt
    camera.position = wizard.pos + vector(1*meter, 5*meter, 15*meter)

vmean = 0.5*wizard.v + 0.5*victim.v
wizard.v = vmean
victim.v = vmean
victim.color = color.cyan

while t < 10*60*second and wizard.v.z < 0*meter/second and victim.pos.z > 0:
    a = -0.11*g + drag(wizard.v, 120*mph)
    wizard.v += a*dt
    victim.v = wizard.v
    victim.pos += victim.v*dt
    wizard.pos += wizard.v*dt
    timestep(dt)
    t += dt
    camera.position = wizard.pos + vector(1*meter, 5*meter, 15*meter)

if wizard.v.z > 0*meter/second:
    print('we are safe at last! altitude', victim.pos.z)
else:
    print('sad death at speed', wizard.v.z/mph, 'mph')
