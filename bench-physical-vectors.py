from __future__ import division, print_function

import timeit
from physical import *


def timing(operation, setup, name):
    N = 10000
    t = timeit.timeit(operation,
                      setup.format(module = 'physical'),
                      number=N)
    print()
    print(t*1e6/N, 'us', name.format(module = 'physical'))
    t = timeit.timeit(operation,
                      setup.format(module = 'visual'),
                      number=N)
    print(t*1e6/N, 'us', name.format(module = 'visual'))

timing('a=a+b',
       'from {module} import vector; a = vector(0,0,0); b = vector(0,0,0.001)',
       '{module}.vector addition')

timing('a=a-b',
       'from {module} import vector; a = vector(0,0,0); b = vector(0,0,0.001)',
       '{module}.vector subtraction')

timing('c=a.dot(b)',
       'from {module} import vector; a = vector(0,0,0); b = vector(0,0,0.001)',
       '{module}.vector dot method')

timing('a.x=a.dot(b)',
       'from {module} import vector; a = vector(0,0,0); b = vector(0,0,0.001)',
       '{module}.vector dot method and component assignment')

timing('a=a.cross(b)',
       'from {module} import vector; a = vector(1,2,0); b = vector(0,0,0.001)',
       '{module}.vector cross method')
