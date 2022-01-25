__doc__ = """
Usage

check_device_blackbox.py <device> <period> <filename>
"""

import sys, re, fandango as fn

device,period,filename = sys.argv[1:4]

dp = fn.get_device(device)

he = ".* (.*.cells.es)"

pe = '.* (PID [0-9]+)'
oe = '.* Operation ([a-z_0-9]+) '

hosts = fn.defaultdict(lambda:fn.defaultdict(set))

for i in range(3*int(period)):
    r = dp.black_box(50)
    for l in r:
        mh = re.match(he,l)
        if mh:
            mh = mh.groups()[0]
            ph  = re.match(pe,l)
            if ph:
                ph = ph.groups()[0]
            mo = re.match(oe,l)
            if mo:
                mo = mo.groups()[0]
            hosts[mh][ph].add(mo)
    fn.wait(.3)

f = open(filename,'w')

for k,v in sorted(hosts.items()):
  for p,l in sorted(v.items()):
    f.write('%s\t%s\t%s\n' % (k,p,l))
    
f.close()
