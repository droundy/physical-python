from physical import *
camera.windowsize = (100,100)
# start
s1 = sphere(vector(-1,0,0)*meter, color=color.red)
s2 = sphere(vector( 1,0,0)*meter, color=color.green)
s2.pos = vector(2,0,0)*meter # the spring stretches
h = helix(s1, s2)
# done
camera.range = 7*meter
savepng('figures/helix.png')
