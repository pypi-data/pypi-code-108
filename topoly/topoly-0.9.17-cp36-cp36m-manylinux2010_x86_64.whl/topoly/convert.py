import re

def convert_xyz2vmd(xyz_file):
    """
    Converts xyz file into .pdb file and creates .psf topoly file with same name.
    Then you can open your structure in vmd typing „vmd file.pdb -psf file.psf"

    file.xyz: 4 columns (id, x, y, z)
    Atoms in neighboring rows are treated as bonded.
    Lines with „X" are separating arcs arcs.
    """
    pdb_file = xyz_file.replace('.xyz','.pdb')
    psf_file = xyz_file.replace('.xyz','.psf')

    indexes = []
    xs = []
    ys = []
    zs = []
    bonds = []
    line_ndx = 0

    with open(xyz_file,'r') as f:
        with open(pdb_file, 'w') as ff:
            bond1=None
            bond2=None
            for line in f.readlines():
                line_ndx += 1
                m = re.search('\s*([0-9]+)\s*(\-?[0-9.]+)\s*(\-?[0-9.]+)\s*(\-?[0-9.]+)\s*', line)
                X = re.search('[^0-9]\n', line)
                if line[0] == '#':
                    continue
                elif m:
                    index = int(m.group(1))
                    x = float(m.group(2))
                    y = float(m.group(3))
                    z = float(m.group(4))
                    bond2 = bond1
                    bond1 = index
                elif X:
                    bond2 = bond1
                    bond1 = None
                else:
                    raise ValueError('Unexpected format in line {:d}: {}'.format(line_ndx, line))
                if bond1 and bond2:
                    bonds.append((bond2,bond1))
                if index not in indexes:
                    indexes.append(index)
                    xs.append(x)
                    ys.append(y)
                    zs.append(z)
                    ff.write('ATOM  {:5d}  CA  GLY {:5d}    {:7.3f} {:7.3f} {:7.3f}  1.00  0.00      MOLE \n'.format(index,index,x,y,z)) 

    header="""
    PSF CMAP

        {:>4d}  !NATOM
    """.format(len(indexes))

    i=0
    with open(psf_file, 'w') as ff:
        ff.write(header)
        for index in indexes:
            ff.write(' {:>7d} A {:>7d}  GLY  CA  CA   0.000  1.000      0\n'.format(index, index))
        ff.write('\n    {:>4d} !NBOND: bonds\n'.format(len(bonds)))    
        for bond in bonds:
            i+=1
            ff.write(' {:>7d} {:>7d}'.format(bond[0], bond[1]))
            if i%4==0:
                ff.write('\n')
