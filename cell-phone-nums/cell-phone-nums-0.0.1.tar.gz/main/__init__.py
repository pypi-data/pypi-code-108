from params import *

firstname = fn()
lastname = ln()
pid = pn()
num = mnum()


if num[0:3] == '577':
    with open(r'geocell.txt','a') as t:
        t.write(num)
        t.write('\n')

elif num[0:3] == '571':
    with open(r'beeline.txt','a') as t:
        t.write(num)
        t.write('\n')

elif num[0:3] == '598':
    with open(r'magti.txt','a') as t:
        t.write(num)
        t.write('\n')
else:
    with open(r'unknown.txt','a') as t:
        t.write(num)
        t.write('\n')

