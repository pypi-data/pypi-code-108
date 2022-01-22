"""
The polynomial class adapted from definition from the bgabrovsek@github Laurent class.

Pawel Dabrowski-Tumanski
p.dabrowski at cent.uw.edu.pl
27.06.2019

Docs:
https://realpython.com/documenting-python-code/#docstring-types

The type used here: Google


Support in PyCharm:
https://www.jetbrains.com/help/pycharm/settings-tools-python-integrated-tools.html
- change default reStructuredText to Google

Docs will be published in: https://readthedocs.org/

"""

import re
import operator
from collections import defaultdict
from functools import reduce
import numbers
import numpy as np
from .polvalues import *


# compile RegEx's for parsing
re_insert_plus = re.compile(r'^(?=\w)')  # start of line with no alphanumerical
re_insert_ones = re.compile(r'([-+](?!\d))')  # +-char
re_insert_carets = re.compile(r'([A-Z|a-z](?!\^))')  # char without a following caret
re_insert_whitespace = re.compile(r'(?<=\d)([-+])(?=\d)')  # +- with decimals on both sides
re_insert_star = re.compile(r'([A-Z|a-z])')  # char
re_whitespace = re.compile(r'\s')  # whitespace
re_star = re.compile(r'\*')  # star
re_brackets = re.compile(r'[()\[\]{}]')  # bracketss
re_star_star = re.compile(r'\*\*')  # star
re_star_caret = re.compile(r'[*^]')  # star or carets



class term:
    """class representing a single multivariate term in polynomial"""

    # Initialization, deletion, representation

    # def __new__(self, arg): N/A

    def __init__(self, s=None, parent=None):
        """ initializes the multivariate laurent term, argument may be either:
        a term (makes a copy),
        integer (makes a term with degrees 0),
        string (of the form '+ x^ay^bz^c...'),
        or empty (makes an empty term) """

        # by default laurent has variable one x

        if isinstance(s, term):
            self.coef = s.coef
            self.degree = dict(s.degree)

        elif s == None:
            # make empty term
            self.coef = 0
            pass

        elif isinstance(s, str):
            s_split = re_star_caret.split(s)
            self.coef = float(s_split[0]) if '.' in s_split[0] else int(s_split[0])
            self.degree = {}  # empty dict

            for i in range(len(s_split) // 2):
                self.degree[s_split[i * 2 + 1]] = float(s_split[i * 2 + 2]) if '.' in s_split[i * 2 + 2] else int(
                    s_split[i * 2 + 2])

        elif isinstance(s, int) or isinstance(s, float):
            self.coef = s
            self.degree = {}

        else:
            raise ValueError('Term called with wrong argument.')

        self.canonical()

    # def __del__(self, arg): N/A

    def __repr__(self):
        """ term to readable string """

        if self.zeroQ(): return '0'
        if self.intQ(): return ('- ' if self.coef < 0 else '') + str(abs(self.coef))

        # coefficient
        s = ('- ' if self.coef < 0 else '') + (str(abs(self.coef)) if abs(self.coef) != 1 else '')

        # variables
        for v in self.degree:
            s += v + (('^' + str(self.degree[v])) if self.degree[v] != 1 else '')
        return s

    # def __str__(self, arg): N/A

    # Comparison operators

    def __eq__(self, t):
        """ == operator """
        #   return self.__cmp_split() == t.__cmp_split()
        return (tuple(self.degree.items()), self.coef) == (tuple(self.degree.items()), self.coef)

    def __ne__(self, t):
        """ != operator"""
        return (tuple(self.degree.items()), self.coef) != (tuple(self.degree.items()), self.coef)

    def __xor__(self, t):
        """ ^ operator, True if term similar (ie. degrees match), False otherwise """
        return self.degree == t.degree

    # Call emulator

    def __call__(self, d):
        """ evaluate term at values specified in dictionary,
         e.g. dict = {'x':3, 'y': 4} avaluates the polynomial at x=3, y=4.
         Can be used make a substitution by e.g. dict = {'x':'A+1'}. """

        t = term(self)
        res = polynomial(1)
        for v in d:
            if v in t.degree:
                if isinstance(d[v], numbers.Number):
                    res *= polynomial(d[v] ** t.degree[v])
                else:
                    if t.degree[v] > 0:
                        res *= polynomial(d[v]) ** t.degree[v]
                    else:
                        res *= polynomial(d[v]) ** -t.degree[v]
                        res = res.__invert__()
                del t.degree[v]
            elif len(v.split('**')) > 1 and v.split('**')[0] in t.degree:
                var, pow = v.split('**')
                pow = int(pow) # TODO and what if not int?
                if t.degree[var] % pow == 0:
                    if t.degree[var] > 0:
                        res *= polynomial(d[v]) ** int(t.degree[var]/pow)
                    else:
                        res *= polynomial(d[v]) ** int(-t.degree[var]/pow)
                        res = res.__invert__()

                    del t.degree[var]
        return res * polynomial(str(t))

    def __add__(self, other):
        t = term(self)
        t += other
        return t

    def __sub__(self, other):
        t = term(self)
        t -= other
        return t

    def __mul__(self, t):
        """ * operator """
        new_t = term(self)
        new_t *= t
        return new_t

    def __pow__(self, exponent):
        """ ** operator """
        new_t = term(self)
        new_t **= exponent
        return new_t

    def __iadd__(self, other):
        if self.zeroQ():
            return other
        elif not self ^ other:
            raise ValueError("Cannot add non-similar terms.")
        self.coef += other.coef
        self.canonical()
        return self

    def __isub__(self, other):
        if self.zeroQ():
            return other
        elif not self ^ other: raise ValueError("Cannot add non-similar terms.")
        self.coef -= other.coef
        self.canonical()
        return self

    def __imul__(self, other):
        """ *= operator """

        if isinstance(other, int) or isinstance(other, float):  # division by integer
            self.coef *= other


        elif isinstance(other, term):
            self.coef *= other.coef
            for v in other.degree:
                self.degree[v] = (self.degree[v] + other.degree[v]) if v in self.degree else other.degree[v]

        else:
            raise ValueError('Multiplication of term by unsupported type.')

        self.canonical()
        return self

    def __ipow__(self, exponent):
        """ **= operator """
        self.coef **= exponent
        for v in self.degree:
            self.degree[v] += exponent
        self.canonical()
        return self


    def __neg__(self):
        """ negate, - unary operator """
        new_t = term(self)
        new_t.coef = -new_t.coef
        return new_t

    def __pos__(self):
        """ + unary operator (returns a copy) """
        return term(self)

    def __abs__(self):
        """ turns all coefficient to their absolute value """
        new_t = term(self)
        new_t.coef = abs(new_t.coef)
        return new_t

    def __invert__(self):
        """ ~, raplaces each var v with v^-1 """
        new_t = term(self)
        for v in new_t.degree:
            new_t.degree[v] *= -1
        return new_t

    def canonical(self):
        """puts in canonical form: if zero coeff, zero out term as well, remove variables with power 0"""

        if self.coef == 0: self.degree = {}
        self.degree = {v: exponent for v, exponent in sorted(self.degree.items()) if exponent != 0}

    # Custom methods (Queries)

    def intQ(self):
        """ True if the term an integer, False othwerwise """
        return all(v == 0 for v in self.degree)

    def zeroQ(self):
        """ True if the term is 0, False othwerwise """
        #  print("test(",self.coef,self.coef == 0,")")
        return self.coef == 0

    def oneQ(self):
        """ True if the term is 1, False othwerwise """
        return self.coef == 1 and self.intQ()

    def minusoneQ(self):
        """ True if the term is 1, False othwerwise """
        return self.coef == -1 and self.intQ()


class polynomial:
    """class representing a multivariate polynomials, an ordered list of terms"""

    # Initialization, deletion, representation

    # def __new__(self, arg): N/A

    def __init__(self, s=None):
        """ initializes the multivariate laurent polynomial, argument may be either:
        a laurent polynomial (makes a copy),
        integer (makes poly with one 0 degrees term),
        string (of the form 'x+2y^3 -4y^-1 + z^(-3)y**5'),
        or empty (makes a polynomial without terms, ie. polynomial 0)
        In vars we should provide a list (or string) of variables used
        (otherwise they are extracted from the string)."""

        if isinstance(s, polynomial):
            # make a copy
            self.term = [term(t) for t in s.term]

        elif s == None:
            self.term = []

        elif isinstance(s, str):

            # variable_list = sorted(set(re.sub(r'[^a-zA-Z]+','',s))) # set of variables usef in polynomial

            """ accepts strings like 'x+2y^3 -4y^-1 + z^(-3)y**5' """
            s = re_whitespace.sub('', s)  # remove whitespace
            s = re_star_star.sub('^', s)  # replace ** -> ^
            s = re_brackets.sub('', s)  # remove brackets
            s = re_insert_plus.sub('+', s)  # put + in front if missing
            s = re_insert_ones.sub('\g<1>1', s)  # insert 1s in front of term starting with a variable
            s = re_insert_carets.sub('\g<1>^1', s)  # insert ^1's after variables
            s = re_insert_whitespace.sub(' \g<1>', s)  # insert whitespace between term
            s = re_insert_star.sub('*\g<1>', s)  # insert *'s between elements
            s_split = re_whitespace.split(s)  # split into a list of term

            self.term = [term(st) for st in s_split]

        elif isinstance(s, int) or isinstance(s, float):
            #            raise ValueError('Not yet supported.') #TODO: variable tables
            self.term = [term(s)]

        self.canonical()

    def __repr__(self):

        """ outputs the polynomial in human readable form """
        if self.zeroQ():
            return '0'
        return ' '.join(('+ ' if i != 0 and s[0] != '-' else '') + s for i, s in enumerate(map(str, self.term)))

    # Comparison

    def __eq__(self, p):
        """ == operator """
        return len(self.term) == len(p.term) and all(t0 == t1 for t0, t1 in zip(self.term, p.term))

    def __ne__(self, p):
        """ != operator """
        return not self == p

    def __nonzero__(self):
        """ False if polynomial is 0, True othwerwise """
        return not self.zeroQ()

    # Call emulator

    def __call__(self, dic):
        """ evaluates the polynomial at values specified in dictionary, e.g. {x:4, y:3} evaluates at x=4, y=3"""
        p = polynomial()
        for t in self.term:
            p += t(dic)
        p.canonical()
        return p

    # Container emulator

    def __len__(self):
        """ returns number of terms """
        return len(self.term)

    # Binary arithemrics

    def __add__(self, p):
        """ + operator """
        new_p = polynomial(self)  # make a copy
        new_p += p
        return new_p

    def __sub__(self, p):
        """ - operator """
        new_p = polynomial(self)  # make a copy
        new_p -= p
        return new_p

    def __mul__(self, p):
        """ * operator """

        new_p = polynomial()

        if isinstance(p, polynomial):
            new_p.term = [t0 * t1 for t0 in self.term for t1 in p.term]
        elif isinstance(p, int) or isinstance(p, float) or isinstance(p, term):
            new_p.term = [term(t) * p for t in self.term]

        new_p.canonical()

        return new_p

    def __pow__(self, i):
        """ ** operator """
        new_p = polynomial(1)
        if i > 0:
            for n in range(i):  # TODO: use map/reduce
                new_p *= self
        # else:
        #     for n in range(-i):  # TODO: use map/reduce
        #         new_p *= self
        return new_p

    def __iadd__(self, p):
        """ += operator """
        if isinstance(p, polynomial):
            # self.term += [ term(t) for t in p.term] # makes copies
            self.term += list(map(term, p.term))
        elif isinstance(p, term) or isinstance(p, int) or isinstance(p, float):
            self.term.append(term(p))  # makes a copy
        else:
            raise ValueError("Adding unsupported type.")
        self.canonical()
        return self

    def __isub__(self, p):
        """ -= operator """

        if isinstance(p, polynomial):
            self.term += [-t for t in p.term]  # makes copies
        elif isinstance(p, term) or isinstance(p, int) or isinstance(p, float):
            self.term += [-p]  # makes a copy
        self.canonical()
        return self

    def __imul__(self, p):
        """ *= operator """
        self.term = (self * p).term
        return self

    def __ipow__(self, n):
        """ **= operator """
        self.term = (self ** n).term
        return self

    # Unary arithemtics

    def __neg__(self):
        """ - unary operator """
        new_p = polynomial(self)
        for t in new_p.term:
            t.coef *= -1
        return new_p

    def __pos__(self):
        """ + unary operator, makes a copy"""
        return polynomial(self)

    def __abs__(self):
        """ replaces all coefficients with their absolute value """
        new_p = polynomial(self)
        for t in new_p.term:
            t.coef = abs(t.coef)
        return new_p

    def __invert__(self):
        """ replaces all variables v with v^-1 """
        new_p = polynomial()
        new_p.term = [~t for t in self.term]
        new_p.canonical()
        return new_p

    def canonical(self):
        """ orders the polynomial and adds up coefficients of similar terms """
        # add similar terms in canonical form
        split_terms = defaultdict(list)
        for t in self.term:
            split_terms[tuple(sorted(t.degree.items()))].append(t)
        self.term = list(
            filter(lambda t: not t.zeroQ(), [reduce(operator.add, split_terms[tnc]) for tnc in sorted(split_terms)]))

        for t in self.term:
            t.canonical()

    # Custom method (degrees, spans)

    def vars(self):
        """ returns set of all vars used in any of the terms """
        return sorted(v for t in self.term for v in t.degree)

    def max_deg(self, v=None):
        """ returns maximal degree of variable v, or a dictionary of maximal degrees if v not supplied """
        if v is None:
            return {v: max((t.degree[v] if v in t.degree else 0) for t in self.term) for v in self.vars()}
        return max((t.degree[v] if v in t.degree else 0) for t in self.term if v in t.degree)

    def min_deg(self, v=None):
        """ returns maximal degree of variable v, or a dictionary of maximal degrees if v not supplied """
        if v is None:
            return {v: min((t.degree[v] if v in t.degree else 0) for t in self.term) for v in self.vars()}
        return min((t.degree[v] if v in t.degree else 0) for t in self.term)

    def min_max_deg(self, v=None):
        """ returns a list of max/min degrees of variable v, or a dictionary if v not supplied """
        if v is None:
            min_degs, max_degs = self.min_deg(), self.max_deg()
            return {u: (min_degs[u], max_degs[u]) for u in min_degs}
        return (self.min_deg(v), self.max_deg(v))

    def span(self, v=None):
        """ returns the span of variable v, or a dictionary of spans if v not supplied """
        if v is None:
            minmax = self.min_max_deg(v)
            return {u: minmax[u][1] - minmax[u][0] for u in minmax}
        return self.max_deg(v) - self.min_deg(v)

    # Custom methods (queries)

    def monomialQ(self):
        """ True if polynomial is a monomial (has one term), False otherwise """
        return len(self.term) == 1

    def intQ(self):
        """ True if polynomial is an integer, False otherwise  """
        return self.monomialQ() and self.term[0].intQ()

    def zeroQ(self):
        """ True if polynomial is 0, False otherwise """
        return len(self.term) == 0

    def oneQ(self):
        """ True if polynomial is 1, False otherwise """
        return self.monomialQ() and self.term[0].oneQ()

    def minusoneQ(self):
        """ True if polynomial is -1, False otherwise """
        return self.monomialQ() and self.term[0].minusoneQ()

    def collect(self, s):
        """ collect vars in s, e.g. s = "xy", we collect x & y's, (a+a^2)x + (3+a)xy^3 """

        ev_dict = {v: 1 for v in s}
        groups = defaultdict(list)

        for t in self.term:
            groups[tuple((v, t.degree[v] if v in t.degree else 0) for v in s)].append(t(ev_dict))

        s = ''
        for i, (g, poly) in enumerate(groups.items()):
            abs1 = False
            if len(poly) == 1:
                sp, abs1 = str(poly[0]), abs(poly[0]).oneQ()
            else:
                sp = '(' + ' '.join(
                    ('+ ' if i != 0 and s[0] != '-' else '') + s for i, s in enumerate(map(str, poly))) + ')'
            sg = ''.join([(v if e else '') + (('^' + str(e)) if e not in (0, 1) else '') for v, e in g])
            s += (' + ' if i and sp[0] != '-' else (' ' if i else '')) + (sp[:-1] if abs1 and sg else sp) + sg

        return s

    def print_short(self, two_vars=False, double=False):
        variables = sorted(list(set(self.vars())))
        if len(variables) == 0:
            if len(self.term) == 1:
                coef = int(float(str(self.term[0])))
                if two_vars:
                    return '[[' + str(coef) + ']]'
                else:
                    return '{ 0 } | ' + str(coef)
            else:
                return '{ 0 } | 0'
        elif len(variables) == 2:
            degs = {}
            for term in self.term:
                if variables[1] in term.degree.keys():
                    degm = term.degree[variables[1]]
                else:
                    degm = 0
                if variables[0] in term.degree.keys():
                    degl = term.degree[variables[0]]
                else:
                    degl = 0
                if degm not in degs:
                    degs[degm] = []
                coef = int(term.coef)
                degs[degm].append([degl, coef])
            minm = min(list(degs.keys()))
            maxm = max(list(degs.keys()))
            res = []
            for m in range(min(0, minm), max(maxm, 0)+1):
                part = []
                if m not in degs.keys():
                    part.append('[0]')
                else:
                    ls = [x for x, y in degs[m]]
                    coefs = {x: str(y) for x, y in degs[m]}
                    beg = min(min(ls), 0)
                    end = max(max(ls), 0) + 1
                    shift = 0
                    if not isinstance(beg, int):
                        beg = int(beg) - 1
                        end = int(end)
                        shift = 0.5
                    for l in range(beg, end):
                        power = l + shift
                        if power in coefs:
                            part.append(coefs[power])
                        else:
                            part.append('0')
                        if power == 0:
                            part[-1] = '[' + part[-1] + ']'
                part = ' '.join(part)
                if m == 0:
                    part = '[' + part + ']'
                res.append(part)
            return '|'.join(res)
        var = variables[0]
        coefficients = {}
        result = []
        for t in self.term:
            try:
                coefficients[t.degree[var]] = int(t.coef)
            except KeyError:
                coefficients[0] = int(t.coef)
        if len(coefficients.keys()) == 0:
            return '{ 0 } | 0'
        minpower = min(coefficients.keys())
        maxpower = max(coefficients.keys())
        shift = 0
        #print("WANDA polynomial, print_short, coef =", coefficients)
        if minpower != int(minpower):
            shift = -0.5
        for k in range(int(minpower), int(maxpower)+2):  #WANDA strange range, probably for links and non-natural powers, for natural powers it always couses additional zero at the end
            power = k + shift
            try:
                result.append(coefficients[power])
            except KeyError:
                result.append(0)
        if int(minpower) == minpower:
            minpower = int(minpower)

        #remove first and last zeroes from result
        while (len(result)>0):
            if (result[0] == '0' or result[0]==0): result.pop(0)
            else: break

        while (len(result)>0):
            if (result[-1] == '0' or result[-1]==0): result.pop()
            else: break

        return '{ ' + str(minpower) + ' } | ' + ' '.join([str(x) for x in result]).strip()
        #return '{ ' + str(minpower) + ' } | ' + ' '.join([str(x) for x in result]).strip('0').strip()

    def homfly_general(self):
        result = polynomial(0)
        for t in self.term:
            p = int((t.degree.get('l', 0) - t.degree.get('m',0))/2)
            q = int(-(t.degree.get('l', 0) + t.degree.get('m', 0)) / 2)
            r = t.degree.get('m', 0)
            partx = polynomial('x**' + str(p))
            party = polynomial('y**' + str(q))
            partz = polynomial('z**' + str(r))
            result += polynomial(t.coef) * partx * party * partz
        return result

    def homfly_translate_em(self, p):
        result = polynomial(0)
        for t in p.term:
            powx = t.degree.get('x', 0)
            powy = t.degree.get('y', 0)
            powz = t.degree.get('z', 0)
            partl = polynomial('l**' + str(powx-powy))
            partm = polynomial('m**' + str(powz))
            result += polynomial(t.coef) * partm * partl
        return result

    def homfly_translate_dh(self, p):
        result = polynomial(0)
        for t in p.term:
            powx = t.degree.get('x', 0)
            powy = t.degree.get('y', 0)
            powz = t.degree.get('z', 0)
            partv = polynomial(str((-1)**powy)) * polynomial('v**' + str(powy-powx))
            partz = polynomial(str((-1)**powz)) * polynomial('z**' + str(powz))
            result += polynomial(t.coef) * partv * partz
        return result

    def homfly_translate_katlas(self, p):
        result = polynomial(0)
        for t in p.term:
            powx = t.degree.get('x', 0)
            powy = t.degree.get('y', 0)
            powz = t.degree.get('z', 0)
            parta = polynomial(str((-1)**powy)) * polynomial('a**' + str(powx-powy))
            partz = polynomial(str((-1)**powz)) * polynomial('z**' + str(powz))
            result += polynomial(t.coef) * parta * partz
        return result

    def homfly_translate(self, version='EM'):
        p = self.homfly_general()
        if version == 'EM':
            return self.homfly_translate_em(p)
        elif version == 'DH':
            return self.homfly_translate_dh(p)
        elif version == 'katlas':
            return self.homfly_translate_katlas(p)
        else:
            return p

