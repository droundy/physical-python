from __future__ import division, print_function

import timeit

def timing(operation, setup, name):
    N = 1000000
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

timing('a=a*s',
       'from {module} import vector; a = vector(1,2,0); s = 1.1',
       '{module}.vector scalar multiplication (reversed)')

timing('a=a/s',
       'from {module} import vector; a = vector(1,2,0); s = 1.1',
       '{module}.vector scalar division')

timing('a=s*a',
       'from {module} import vector; a = vector(1,2,0); s = 1.1',
       '{module}.vector scalar multiplication')

timing('b = s**2',
       '''try:
    from {module} import meter
    s = 5.5*meter
except:
    s = 5.5''',
       '{module}.scalar pow')

timing('c = a*b',
       '''try:
    from {module} import meter
    a = 5.5*meter
    b = -.5*meter
except:
    a = 5.5
    b = -.5''',
       '{module}.scalar mul')

timing('c = a*b',
       '''try:
    from {module} import meter
    a = 5.5*meter
    b = -.5
except:
    a = 5.5
    b = -.5''',
       '{module}.scalar mul float')

timing('c = b*a',
       '''try:
    from {module} import meter
    a = 5.5*meter
    b = -.5
except:
    a = 5.5
    b = -.5''',
       '{module}.scalar float mul')

timing('c = a/b',
       '''try:
    from {module} import meter
    a = 5.5*meter
    b = -.5*meter
except:
    a = 5.5
    b = -.5''',
       '{module}.scalar div')

