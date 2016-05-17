from physical import *
camera.windowsize = (100,100)
# start
c = cylinder(vector(0,0,0)*meter, vector(1,0,0)*meter, radius=1*meter)
c.pos2 = vector(.4,.3,-.3)*meter
# done
camera.range = 5*meter
savepng('figures/cylinder.png')
