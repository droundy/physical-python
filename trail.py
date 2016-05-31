from physical import *
camera.windowsize = (100,100)
camera.center = vector(5,0,8)*meter
camera.range = 30*meter
# start
s = sphere(vector(-1,0,16)*meter, radius=1.5*meter)
s.velocity = vector(2,0,0)*meter/second
trail(s, duration=4*second, dash_time=0.1*second)
g = vector(0,0,-9.8)*meter/second**2
t = 0*second
dt = 0.001*second
while t < 5*second:
    s.pos += s.velocity*dt
    s.velocity += g*dt
    if s.pos.z < 0*meter:
        s.velocity.z = abs(s.velocity.z)
    timestep(dt)
    t += dt
# done
savepng('figures/trail.png')
