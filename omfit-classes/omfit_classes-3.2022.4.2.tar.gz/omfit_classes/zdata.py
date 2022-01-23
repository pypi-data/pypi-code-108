import sys, os, re
import pickle
import numpy as np


def write_f(name, fvec, unit, file):

    file.write("@R %s %d [%s]\n" % (name.upper(), len(fvec), unit))
    for i in range(len(fvec)):
        file.write(" %16.9e" % fvec[i])
        if (i + 1) % 4 == 0 and i != (len(fvec) - 1):
            file.write("\n")
    file.write("\n")


def write_i(name, ivec, unit, file):

    file.write("@I %s %d []\n" % (name.upper(), len(ivec)))
    for i in range(len(ivec)):
        file.write(" %16d" % ivec[i])
        if (i + 1) % 4 == 0 and i != (len(ivec) - 1):
            file.write("\n")
    file.write("\n")


def write_formatted(fdata, filename, vars=None):

    with open(filename, "w") as f:
        if vars:
            for var in vars:
                if isinstance(fdata[var], type(1)):
                    write_i(var, fdata[var], '', f)
                else:
                    write_f(var, fdata[var], '', f)
        else:
            for var in fdata:
                if isinstance(fdata[var][0], type(1)):
                    write_i(var, fdata[var], '', f)
                else:
                    write_f(var, fdata[var], '', f)


def read_formatted(file):

    fdata = {}

    # ---read formatted data

    # print("####################################")
    # print("READ ",file)

    with open(file, 'r') as f:
        lines = f.readlines()
    nlines = len(lines)

    pat_R = re.compile("@")

    # ---parsing outone

    # print("####################################")
    # print("PARSING ",file)

    for k in range(nlines):

        if pat_R.search(lines[k]):
            p = lines[k].split()
            vname = p[1]
            ndata = int(p[2])
            # print vname,ndata
            fdata[vname] = []  # np.zeros(ndata)
            nread = 0
            for j in range(ndata):
                if pat_R.search(lines[k + j + 1]):
                    print('incompatible file format')
                if p[0][1] == 'R':
                    d = [float(x) for x in lines[k + j + 1].split()]
                elif p[0][1] == 'I':
                    d = [int(x) for x in lines[k + j + 1].split()]
                    # print type(d[0])
                else:
                    print('type mismatch')
                    raise  # sys.exit()
                nread = nread + len(d)
                fdata[vname] = fdata[vname] + d
                if nread == ndata:
                    break
            # print nread
            # fdata[vname] = np.array(fdata[vname])

    return fdata


def scale(fname, vname, factor):

    fdata = read_formatted(fname)
    fdata[vname] = factor * fdata[vname]
    write_formatted(fdata, fname + "_new")


def temp1(fname):

    fdata = read_formatted(fname)
    # fdata["OMEGA"] = fdata["TI"]*1.0e5
    nrho = len(fdata["OMEGA"])
    rho = np.arange(nrho) / (nrho - 1.0)
    fdata["OMEGA"] = 1.0e6 * np.array([1.0 - x * x for x in rho])
    write_formatted(fdata, fname + "_new")


def temp():

    fdata = read_formatted("inprof0")
    nrho = len(fdata["CURRF"])
    rho = np.arange(nrho) / (nrho - 1.0)
    scale = 0.0  # 3.2/2.54
    fdata["CURRF"] = scale * fdata["CURRF"]
    fdata["QRFE"] = scale * fdata["QRFE"]
    write_formatted(fdata, "inprof")


def from_dict(indict, filename):

    with open(filename, "w") as f:
        for var in list(indict.keys()):
            # 'from_dict '+var,type(indict[var][0])
            if isinstance(indict[var][0], type(1)):
                write_i(var, indict[var], '', f)
            else:
                write_f(var, indict[var], '', f)
