import time
import numpy as np
import matplotlib.pyplot as plt
import timeit

t = (2009, 2, 17, 17, 3, 38, 1, 48, 0)
t_mk = time.mktime(t)#convert to sec
print 't_mk', t_mk
print 'time.gmtime(t_mk)', time.gmtime(t_mk)#convert to time structure
print 'strftime', time.strftime("%b %d %Y %H:%M:%S", time.gmtime(t_mk))
t_mk_2 = time.mktime(time.gmtime(t_mk))
print 't_mk', t_mk_2