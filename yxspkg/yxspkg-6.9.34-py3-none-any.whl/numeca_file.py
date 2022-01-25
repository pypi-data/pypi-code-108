
def read_mf(mf):
    result = {}
    fp = open(mf)
    read_line = lambda n:[fp.readline() for i in range(n)]
    def read2Element(s):
        s = s.strip().split()
        if len(s)<2:
            return
        result[s[0]] = float(s[1])
    def read_in_out(s):
        s = s.strip().split()
        if len(s) < 3:
            return
        d = {'INLET':float(s[1]),'OUTLET':float(s[2])}
        result[s[0]] = d
    global_read = True
    while True:
        s = fp.readline()
        if s=='':
            break
        s = s.strip()
        if s == 'Mesh data' and global_read:
            ls = read_line(4)[2:4]
            [read2Element(i) for i in ls]
        elif s=='Geometrical data' and global_read:
            ls = read_line(85-34+1)
            [read_in_out(i) for i in ls]
        elif s=='Global performance' and global_read:
            ls = read_line(103-89+1)
            [read2Element(i) for i in ls]
            global_read = False
    return result