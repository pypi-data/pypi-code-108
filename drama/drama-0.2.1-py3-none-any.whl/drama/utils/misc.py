import os
import pathlib
import pickle
from collections import namedtuple

import numpy as np
from scipy import signal


def safe_open_write(file, mode="a"):
    """Open file in write mode and return a corresponding file object,
    creating the parent directories if they do not exist.

    Parameters
    ----------
    file : path-like object (str or bytes)
        path to file to be opened
    mode : str
        specify the mode in which the file is open. Built-in
        open() options must be used (Default value = "a")

    Returns
    -------
    file object
        a file object corresponding to file

    """
    dir_path = os.path.dirname(file)
    os.makedirs(
        dir_path, exist_ok=True
    )  # Make the parent directory, if it does not exist
    filename = pathlib.Path(file)
    filename.touch(exist_ok=True)  # Trying to create a new file or open one
    return open(filename, mode)


def get_par_file(parfile=None):
    """Mini gui to get filename

    Parameters
    ----------
    parfile :
         (Default value = None)

    Returns
    -------

    """

    def _test(out_q):
        """

        Parameters
        ----------
        out_q :


        Returns
        -------

        """
        out_q.put("hola")

    if parfile is None:
        # output_queue = multiprocessing.Queue()
        # p = multiprocessing.Process(target=_get_par_file, args=(output_queue,))
        # p.start()
        # parfile = output_queue.get()
        # p.join()
        parfile = _get_par_file(1)
    return parfile


def _get_par_file(out_q):
    """

    Parameters
    ----------
    out_q :


    Returns
    -------

    """
    from tkinter import filedialog as tkfiledialog
    from tkinter import Tk

    root = Tk()
    root.withdraw()
    root.overrideredirect(True)
    root.geometry("0x0+0+0")
    root.deiconify()
    root.lift()
    root.focus_force()
    parfile = tkfiledialog.askopenfilename(parent=root)
    root.destroy()
    # out_q.put(parfile)
    return parfile


def save_object(obj, filename):
    """Saves an object in a file (better use .pkl format)

    Parameters
    ----------
    obj :

    filename :


    Returns
    -------

    """
    with safe_open_write(filename, "wb") as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)


def load_object(filename):
    """Loads an object from a file.pkl

    Parameters
    ----------
    filename :


    Returns
    -------

    """
    with open(filename, "rb") as f:
        obj = pickle.load(f)
    return obj


def save_tuple(obj, filename):
    """saves a one level tuple containg arrays, lists and single elements
        Note: no nested tuples can be included

    Parameters
    ----------
    obj :

    filename :


    Returns
    -------

    """
    # name of the tuple
    tname = type(obj).__name__

    # tuple fields
    fields1 = obj._fields
    # field types
    types_all = np.empty(len(fields1), dtype=type)
    type_var = []  # corresponding field name
    listall = ["np.savez(filename", "tname=" + '"' + tname + '"']
    for i in range(len(fields1)):
        listall.append(fields1[i] + " = obj." + fields1[i])
        types_all[i] = type(obj[i])
        type_var.append(fields1[i])
    types = sorted(zip(type_var, types_all))
    listall.append("types = types)")
    eval(",".join(listall))


def load_tuple(filename):
    """load tuple from file saved using save_tuple

    Parameters
    ----------
    filename :


    Returns
    -------

    """
    arrays = np.load(filename)
    fields = arrays.files

    # name of the tuple
    tname = str(arrays["tname"])
    fields.remove("tname")
    # fields types
    types = arrays["types"]
    fields.remove("types")

    # rearange types according to fields order
    t_name = [i[0] for i in types]
    t_type = [i[1] for i in types]
    pos = [fields.index(i) for i in t_name]
    #    t_name = [x for (y,x) in sorted(zip(pos,t_name))]
    t_type = [x for (y, x) in sorted(zip(pos, t_type))]

    # Create new tuple
    Data = namedtuple(tname, fields)

    # create an empty tuple
    emptyD = "Data("
    for i in range(len(fields)):
        if t_type[i] is int:
            var = 'int(arrays["' + fields[i] + '"]),'
        elif t_type[i] is float:
            var = 'float(arrays["' + fields[i] + '"]),'
        elif t_type[i] is str:
            var = 'str(arrays["' + fields[i] + '"]),'
        elif t_type[i] is list:
            var = 'arrays["' + fields[i] + '"].tolist(),'
        else:
            var = 'arrays["' + fields[i] + '"],'
        emptyD = emptyD + var
    emptyD = emptyD[:-1] + ")"
    data = eval(emptyD)
    return data


# def gentype(element, intuple=False):
#    """ similar to type function, except that it works on tuples
#
#    :param element: element to be type tested
#    :param intuple: if True and element is a tuple, then check type of tuple
#                    fields
#    :return: type as an array or single (depending on intuple)
#    """
#    # check type of elements inside the tuple
#    if isinstance(element, tuple) and intuple:
#        dtype = np.empty(len(element), dtype=type)
#        for i in range(len(element)):
#            if isinstance(element[i], tuple):
#                dtype[i] = tuple
#            else:
#                dtype[i] = type(element[i])
#    elif intuple:  # return array output
#        if isinstance(element, tuple):
#            dtype = np.array([tuple], dtype=type)
#        else:
#            dtype = np.array([type(element)], dtype=type)
#    else:  # return single output
#        if isinstance(element, tuple):
#            dtype = tuple
#        else:
#            dtype = type(element)
#    return dtype


def db(data, clip=False, clip_value=-20, norm=False):
    """Converts data to dB scale

    Parameters
    ----------
    data :
        Input data
    clip :
        Limit dB range (Default value = False)
    clip_value :
        Clipping value (Default value = -20)
    norm :
        Normalize data w.r.t. maximum (Default value = False)

    Returns
    -------
    type
        dB data

    """

    if clip:
        lin_value = np.power(10.0, clip_value / 10.0)
        c_data = np.where(data < lin_value, lin_value, data)
    else:
        c_data = data

    db_val = 10 * np.log10(np.abs(c_data))

    return db_val - np.max(db_val) if norm else db_val


def db2lin(data, amplitude=False):
    """Converts data from dB to linear

    Parameters
    ----------
    data :
        Input data
    amplitude : bool
        Input is amplitude :math:`20\log{x}` or power :math:`10\log{x}` (Default value = False)

    Returns
    -------
    type
        Linear data

    """

    if amplitude:
        return 10.0 ** (data / 20.0)
    else:
        return 10.0 ** (data / 10.0)


def nearest_power_2(value):
    """Calculates the nearest 2^n value for given input
        Method from http://graphics.stanford.edu/~seander/bithacks.html

    Parameters
    ----------
    value :
        Input value/s (scalar or array, max. 32-bit integer!)

    Returns
    -------
    type
        Nearest 2^n

    """

    v = np.array(value).astype(int)
    v -= 1
    v |= v >> 1
    v |= v >> 2
    v |= v >> 4
    v |= v >> 8
    v |= v >> 16
    v += 1

    return v


def nearest_power2(values):
    """

    Parameters
    ----------
    values :


    Returns
    -------

    """
    return (2 ** np.ceil(np.log2(values))).astype(int)


def optimize_fftsize(values, max_prime=2):
    """Returns 'good' dimensions for FFT algorithm

    Parameters
    ----------
    value :
        Input value/s
    max_prime :
        Maximum prime allowed (FFT is optimal for 2) (Default value = 2)
    values :


    Returns
    -------
    type
        Nearest 'good' value/s

    """
    # Force array type (if scalar was given)
    if np.isscalar(values):
        values = np.array([values], dtype=np.int)

    if max_prime == 2:
        good_values = nearest_power2(values)
        return good_values if len(good_values) > 1 else good_values[0]

    good_values = np.array([], dtype=np.int)
    for value in values:
        best_value = value
        while np.max(factorize(best_value)) > max_prime:
            best_value += 1
        good_values = np.append(good_values, best_value)

    return good_values if len(good_values) > 1 else good_values[0]


def factorize(n):
    """Prime factorize a number

    Parameters
    ----------
    n :
        Number

    Returns
    -------
    type
        Array with prime factors

    """
    result = np.array([])
    for i in np.append(2, np.arange(3, n + 1, 2)):
        s = 0
        while np.mod(n, i) == 0:
            n /= i
            s += 1
        result = np.append(result, [i] * s)
        if n == 1:
            return result


def balance_elements(N, size):
    """Divide N elements in size chunks
        Useful to balance arrays of size N not multiple
        of the number of processes

    Parameters
    ----------
    N :
        Number of elements
    size :
        Number of divisions

    Returns
    -------
    type
        counts, displ) vectors

    """
    # Counts
    count = np.round(N / size)
    counts = count * np.ones(size, dtype=np.int)
    diff = N - count * size
    counts[:diff] += 1

    # Displacements
    displ = np.concatenate(([0], np.cumsum(counts)[:-1]))

    return counts, displ



def prime(i, primes):
    """
    Taken from https://stackoverflow.com/questions/1628949/to-find-first-n-prime-numbers-in-python
    author: Lennart

    Parameters
    ----------
    i : int
        number to check if it's a prime

    primes : set
        prime numbers to check against
    """
    for prime in primes:
        if not (i == prime or i % prime):
            return False
    primes.add(i)
    return i


def historic(n):
    """Lists the first n prime numbers
    Taken from https://stackoverflow.com/questions/1628949/to-find-first-n-prime-numbers-in-python
    author: Lennart

    Parameters
    ----------
    n : int
        number of prime numbers to comput

    Returns
    -------
    Set
        set of first n prime numbers
    """
    primes = set([2])
    i, p = 2, 0
    while True:
        if prime(i, primes):
            p += 1
            if p == n:
                return primes
        i += 1


def checkcommondivisors(a, b):
    """Checks the common devisors between 2 variables a and b

    Parameters
    ----------
    a :

    b :


    Returns
    -------

    """

    pr = historic(min([a, b]))
    pr = list(pr)
    for i in range(0, len(pr)):
        if (a % pr[i]) == 0 and (b % pr[i]) == 0:
            return 1
    return 0


def asc_desc(v_arr):
    """Function that gives the indices for ascending and descending node
        according to a velocity vector.

    Parameters
    ----------
    v_arr : 2-D float array
        Velocity vector.

    Returns
    -------
    collections.namedtuple
        named tuple containing ascending and descending indices.
    """
    # separate data into ascending and descending nodes
    desc_loc = np.where(v_arr[:, 2] < 0)
    order_desc = np.array_split(
        desc_loc[0], np.where(np.diff(desc_loc[0]) != 1)[0] + 1
    )
    # create descending indices
    desc_idx = np.zeros((len(order_desc), 2), dtype=np.int32)
    for i in range(0, len(order_desc)):
        desc_idx[i, 0] = order_desc[i][0]
        desc_idx[i, 1] = order_desc[i][-1]

    asc_loc = np.where(v_arr[:, 2] > 0)
    order_asc = np.array_split(
        asc_loc[0], np.where(np.diff(asc_loc[0]) != 1)[0] + 1
    )
    # create ascending indices
    asc_idx = np.zeros((len(order_asc), 2), dtype=np.int32)
    for i in range(0, len(order_asc)):
        asc_idx[i, 0] = order_asc[i][0]
        asc_idx[i, 1] = order_asc[i][-1]

    Arr_indices = namedtuple("Arr_indices", ["asc_idx", "desc_idx"])
    arr_indices = Arr_indices(asc_idx, desc_idx)
    return arr_indices


def find_con_idx(arr1):
    """

    Parameters
    ----------
    arr1 :


    Returns
    -------

    """
    "Find indices of continuous segments"

    idx_arr = np.array(([[0, 0]]))
    j = 0
    while j < arr1.shape[0]:
        st_idx = arr1[j]
        i = j
        while (i < arr1.shape[0] - 1) and (arr1[i + 1] - arr1[i] == 1):
            i = i + 1
        j = j + i
        end_idx = arr1[i]
        idx_arr = np.append(idx_arr, [[st_idx, end_idx]], axis=0)
        j = j + 1

    return idx_arr[1:, :]


class PrInfo(object):
    """ """

    def __init__(self, verbosity, header="processing"):
        self.verbosity = verbosity
        self.header = header

    def msg(self, message, importance=2):
        """

        Parameters
        ----------
        message :

        importance :
             (Default value = 2)

        Returns
        -------

        """
        if importance > (2 - self.verbosity):
            print("%s -- %s" % (self.header, message))


def writepar(
    fileName,
    dDays,
    nRevs,
    i,
    e,
    omega,
    asc_node,
    starttime,
    timeduration,
    timestep,
    near_look,
    far_look,
    gr_res,
):
    """Create a parameter file

    Parameters
    ----------
    fileName :

    dDays :

    nRevs :

    i :

    e :

    omega :

    asc_node :

    starttime :

    timeduration :

    timestep :

    near_look :

    far_look :

    gr_res :


    Returns
    -------

    """
    try:
        filename = pathlib.Path(fileName)
        filename.touch(exist_ok=True)  # Trying to create a new file or open one
        file = open(filename, "w")
    except:
        print("Something went wrong!")

    # Start writing Procedure
    file.write("# Repeat Mission Parameters")
    file.write("\n\n")
    file.write("[orbit]")
    file.write("\n\n")
    file.write("# desired days per cycle [d]")
    file.write("\n")
    file.write("days_cycle = " + str(dDays))
    file.write("\n\n")
    file.write("# number of orbits for repeat")
    file.write("\n")
    file.write("orbits_nbr = " + str(nRevs))
    file.write("\n\n")
    file.write("# inclination")
    file.write("\n")
    file.write("inc =  " + str(i))
    file.write("\n\n")
    file.write("# eccentricity")
    file.write("\n")
    file.write("ecc = " + str(e))
    file.write("\n\n")
    file.write("omega_p = " + str(omega))
    file.write("\n\n")
    file.write("# right ascension of ascending node [deg]")
    file.write("\n")
    file.write("asc_node = " + str(asc_node))
    file.write("\n\n")
    file.write("# fraction of an orbit period")
    file.write("\n")
    file.write("starttime = " + str(starttime))
    file.write("\n\n")
    file.write("# orbit calculation time [d]")
    file.write("\n")
    file.write("timeduration = " + str(timeduration))
    file.write("\n\n")
    file.write("# Time step [s]")
    file.write("\n")
    file.write("timestep = " + str(timestep))
    file.write("\n\n")
    file.write("[sar]")
    file.write("\n\n")
    file.write("# 1st near range angle (RL --> negative angle) [deg]")
    file.write("\n")
    file.write("near_1 = " + str(near_look))
    file.write("\n\n")
    file.write("# 1st far range angle [deg]")
    file.write("\n")
    file.write("far_1 = " + str(far_look))
    file.write("\n\n")
    file.write("# ground range resolution [m]")
    file.write("\n")
    file.write("gr_res = " + str(gr_res))
    file.write("\n")

    file.close()
