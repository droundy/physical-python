from physical import *
camera.windowsize = (100,100)
# start
s = sphere(vector(-1,3,0)*meter, radius=1.5*meter, color=color.blue)
# done
savepng('figures/sphere.png')
