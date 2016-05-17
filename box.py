from physical import *
camera.windowsize = (100,100)
# start
# create a box that is 1x1x0.1 meters in dimension,
# centered at the origin.
b = box(vector(0,0,0)*meter, 1*meter, 1*meter, 0.2*meter)
camera.position = vector(.5,1.5,1)*meter
# done
savepng('figures/box.png')
