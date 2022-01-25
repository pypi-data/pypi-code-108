import re

def _each(o, func):
    """
    iterates through each item of an object

    underscore.js:
    Iterates over a list of elements, yielding each in turn to an iteratee
    function. The iteratee is bound to the context object, if one is
    passed. Each invocation of iteratee is called with three arguments:
        (element, index, list). 
    If list is a JavaScript object, iteratee's arguments will be (value,
    key, list). Returns the list for chaining.
    """
    if callable(getattr(o, 'items', None)):
        for key, value in o.items():
            r = func(value, key, o)
            if r is "breaker":
                break
    else:
        for index, value in enumerate(o):
            r = func(value, index, o)
            if r is "breaker":
                break
    return o

def _any(o, func=None):
    """
    Determine if at least one element in the object
    matches a truth test.
    """
    if func is None:
        func = lambda x, *args: x

    antmp = False

    def testEach(value, index, *args):
        if func(value, index, *args) is True:
            antmp = True
            return "breaker"

    _each(o, testEach)
    return antmp

def paren_split(subject, separator=",", lparen="(", rparen=")", strip=" ", rtrim=False):
    # https://stackoverflow.com/questions/42070323/split-on-spaces-not-inside-parentheses-in-python/42070578#42070578
    nb_brackets=0
    subject = subject.strip(strip or separator) # get rid of leading/trailing seps

    l = [0]
    for i, c in enumerate(subject):
        if c == lparen:
            nb_brackets += 1
        elif c == rparen:
            nb_brackets -= 1
        elif c == separator and nb_brackets == 0:
            l.append(i + 1) # skip seperator
        # handle malformed string
        if nb_brackets < 0:
            if rtrim:
                subject = subject[0:i]
                # print("retrying with: {}".format(subject))
                return paren_split(subject, separator, lparen, rparen, strip)
            else:
                raise Exception("Syntax error (unmatch rparen)")

    l.append(len(subject))
    # handle missing closing parentheses
    if nb_brackets > 0:
        raise Exception("Syntax error (unmatched lparen)")


    return([subject[i:j].strip(strip or separator) for i, j in zip(l, l[1:])])

def escape_backslash(subject, position):
    c = subject[position]
    last_escape = next_escape = None
    previous_escapes = 0
    p = position
    last_escape = subject.rfind('\\', 0, p)
    while ~last_escape and last_escape == p - 1:
        previous_escapes += 1
        p -= 1
        last_escape = subject.rfind('\\', 0, last_escape)

    
    # dprint("[last_] last_escape, next_escape")
    #  print("[escape_backslash] {} s:'{}' last_escape:{}, previous_escapes:{}".format(position, subject[0:position+1], last_escape, previous_escapes))

    return (previous_escapes % 2) != 0
                    
def func(ea=None):
    """
    func

    @param ea: linear address
    """

    ea = eax(ea)
    


def paren_multisplit(subject, separator=",", lparen="([{'\"", rparen=[")", "]", "}", "'", '"'], strip=None, escape=escape_backslash, skipEmpty=False):
    if isinstance(subject, list):
        return [paren_multisplit(x, separator, lparen, rparen, strip, escape, skipEmpty) for x in subject]

    def is_separator(c):
        if type(c) == type(separator):
            return c == separator
        else:
            return re.match(separator, c)

    # https://stackoverflow.com/questions/42070323/split-on-spaces-not-inside-parentheses-in-python/42070578#42070578
    lparen = list(lparen)
    rparen = list(rparen)
    paren_len = len(lparen)
    if len(rparen) != paren_len:
        raise Exception("len(rparen) != len(lparen)")
    brackets=[0] * paren_len
    stack = []

    subject = subject.strip(strip) # get rid of leading/trailing seps

    l = [0]
    for i, c in enumerate(subject):
        if c in lparen and not escape(subject, i):
            deal = False
            index = lparen.index(c)
            if rparen[index] == c:
                # dealing with symetrical things like ' or "
                if stack and stack[-1] == c:
                    brackets[index] -= 1
                    stack.pop()
                    deal = True
            if not deal:
                brackets[index] += 1
                stack.append(c)
        elif c in rparen and not escape(subject, i):
            index = rparen.index(c)
            brackets[index] -= 1
            if brackets[index] < 0:
                raise Exception("Syntax error (unbalanced '{}' at '{}')".format(c, subject[0:i+1]))
            if stack[-1] != lparen[index]:
                raise Exception("Syntax error (unbalanced '{}' stack: '{}')".format(c, stack))
            stack.pop()
        elif is_separator(c) and sum(brackets) == 0 and not escape(subject, i):
            l.append(i + 1) # skip seperator
        # handle malformed string
        if _any(brackets, lambda x, *a: x < 0):
            raise Exception("Syntax error (unmatch rparen)")

    l.append(len(subject) + 1)
    # handle missing closing parentheses
    if _any(brackets, lambda x, *a: x < 0):
        raise Exception("Syntax error (unmatch rparen) final")
    elif _any(brackets, lambda x, *a: x < 0):
        raise Exception("Syntax error (unmatch lparen) final")

    result = [subject[i:j-1].strip(strip) for i, j in zip(l, l[1:])]
    if skipEmpty:
        return [x for x in result if x != '']
    return result
