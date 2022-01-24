import matplotlib
matplotlib.use('PDF')
import matplotlib.pyplot as plt
import sys
from ampule import Ampule, search_mask, dat_parser

#This command must be at the beginning of every Ampule script
ampule = Ampule(*sys.argv)

data, _ = ampule.load(dat_parser, 'dat/poly.dat')

plt.plot(data.x, data.f, label = r'$f(x)$')
plt.plot(data.x, data.g, label = r'$g(x)$')
plt.plot(data.x, data.h, label = r'$h(x)$')

#Also you can use arithmetic on columns
plt.plot(data.x, data.f + data.g/2 + data.h/6, label = r'$(f + g/2 + h/6)(x)$')
#For more complex cases, use functions like numpy.sin() or do the thing manually using
#map(), zip() and list comprehensions

plt.xlabel(r'$x$')
plt.ylabel(r'$y$')
plt.grid()
plt.legend()
plt.title('Linear scale')

#Simple wrapper for matplotlib save functions (pyplot.savefig, animation.FuncAnimation.save, ...)
#Removing the embedding of the date in the output files as well as creating some necessary paths
ampule.save(plt.savefig, 'linear')
plt.clf()

#You are not limited to one picture per script. Let's create another
###############################################################################

plt.plot(data.x, data.f, label = r'$f(x)$')
plt.plot(data.x, data.g, label = r'$g(x)$')
plt.plot(data.x, data.h, label = r'$h(x)$')

plt.xlabel(r'$x$')
plt.ylabel(r'$y$')
plt.loglog()
plt.grid()
plt.legend()
plt.title('Logarithmic scale')

ampule.save(plt.savefig, 'loglog')
plt.clf()

###############################################################################

#This command must be at the end of every Ampule script
ampule.flush_deps()
