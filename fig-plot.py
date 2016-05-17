from physical import *
camera.windowsize = (100,100)
# start
quadratic = plot(color.green)
linear = plot(color.red)
x = 0
while x < 1:
    quadratic.plot(x, x**2)
    linear.plot(x,x)
    x = x+0.01
# done
savepng('figures/plot.png')
