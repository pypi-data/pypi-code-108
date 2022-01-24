import matplotlib
matplotlib.use('PDF')
import matplotlib.pyplot as plt
import sys
from ampule import Ampule, search_mask, dat_parser

#This command must be at the beginning of every Ampule script
ampule = Ampule(*sys.argv)

plt.ylim(-10, 10)

for path, k in search_mask('dat/hermite/H_', '.dat'):
    data, meta = ampule.load(dat_parser, path)
    formula = meta.f.replace('**', '^').replace('*', '')
    label = rf'$H_{k} = {formula}$'
    plt.plot(data.x, data.H, label = label)

plt.xlabel(r'$x$')
plt.ylabel(r'$y$')
plt.grid()
plt.legend()
plt.title('Hermite Polynomials')

#Simple wrapper for matplotlib save functions (pyplot.savefig, animation.FuncAnimation.save, ...)
#Removing the embedding of the date in the output files as well as creating some necessary paths
ampule.save(plt.savefig, 'hermite')
plt.clf()

###############################################################################

#This command must be at the end of every Ampule script
ampule.flush_deps()
