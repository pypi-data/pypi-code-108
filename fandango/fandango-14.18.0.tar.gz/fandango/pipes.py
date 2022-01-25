#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

"""
#############################################################################
##
## project :     Functional tools for Tango Control System
##
## $Author:      Sergi Rubio Manrique, srubio@cells.es $
##
## $Revision:    2008 $
##
## copyleft :    ALBA Synchrotron Controls Section, CELLS
##               Bellaterra
##               Spain
##
#############################################################################
##
## This file is part of Tango Control System
##
## Tango Control System is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as published
## by the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
##
## Tango Control System is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see <http://www.gnu.org/licenses/>.
####################################################################@########
"""

########################################################################
## Methods for piped iterators
## Inspired by Maxim Krikun [ http://code.activestate.com/recipes/276960-shell-like-data-processing/?in=user-1085177]
########################################################################
  
from fandango.functional import *
      
class Piped:
    """This class gives a "Pipeable" interface to a python method:
        cat | Piped(method,args) | Piped(list)
        list(method(args,cat))
    e.g.: 
    class grep:
        #keep only lines that match the regexp
        def __init__(self,pat,flags=0):
            self.fun = re.compile(pat,flags).match
        def __ror__(self,input):
            return ifilter(self.fun,input) #imap,izip,count,ifilter could ub useful
    cat('filename') | grep('myname') | printlines
    """
    import itertools
    def __init__(self,method,*args,**kwargs):
        self.process=partial(method,*args,**kwargs)
    def __ror__(self,input):
        return imap(self.process,input)
        
class iPiped:
    """ Used to pipe methods that already return iterators 
    e.g.: hdb.keys() | iPiped(filter,partial(fandango.inCl,'elotech')) | plist
    """
    def __init__(self,method,*args,**kwargs): self.process = partial(method,*args,**kwargs)
    def __ror__(self,input): return self.process(input)
    
class zPiped:
    """ 
    Returns a callable that applies elements of a list of tuples to a set of functions 
    e.g. [(1,2),(3,0)] | zPiped(str,bool) | plist => [('1',True),('3',False)]
    """
    def __init__(self,*args): self.processes = args
    def __ror__(self,input): return (tuple(p(i[j]) for j,p in enumerate(self.processes))+tuple(i[len(self.processes):]) for i in input)
    
pgrep = lambda exp: iPiped(lambda input: (x for x in input if inCl(exp,x)))
pmatch = lambda exp: iPiped(lambda input: (x for x in input if matchCl(exp,str(x))))
pfilter = lambda meth=bool,*args: iPiped(filter,partial(meth,*args))
ppass = Piped(lambda x:x)
plist = iPiped(list)
psorted = iPiped(sorted)
pdict = iPiped(dict)
ptuple = iPiped(tuple)
pindex = lambda i: Piped(lambda x:x[i])
pslice = lambda i,j: Piped(lambda x:x[i,j])
penum = iPiped(lambda input: izip(count(),input) )
pzip = iPiped(lambda i:izip(*i))
ptext = iPiped(lambda input: '\n'.join(imap(str,input)))
