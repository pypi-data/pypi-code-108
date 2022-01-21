from __future__ import print_function, unicode_literals

def format_fort(strs, seperator=','):
    """format array of string in fortran like string
    string elements are concatinated with commna
    """
    
    wrap_width = 80 - 7 - len(seperator) - 3# 7: leading spaces, 3:newline and mergin
    lines = []
    if len(strs) == 0:
        return ''
    curline = strs[0]
    for s in strs[1:]:
        # can i join this line?
        if len(curline) + len(seperator) + len(s) <= wrap_width:
            curline += seperator + s
        else:
            # no more string
            lines.append(curline)
            curline = s
    # add tailing curline
    if len(curline) != 0:
        lines.append(curline)

    # join and return
    return (seperator+'\n       ').join(lines)

# simple test 
# if __name__ == '__main__':
#     import sys
#     strs = []
#     for i in range(30):
#         strs.append('x'*i)
# 
#     sys.stdout.write('_&TEST_')
#     sys.stdout.write(format_fort(strs))
#     sys.stdout.write('/')
