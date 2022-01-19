#----------------------------------------------------------------------#
# Python interface for reading HIPO files.
# Authors: G.Gavalian (2019, Jefferson Lab),
#          M. McEneaney (2022, Duke University)
#----------------------------------------------------------------------#

import os
import glob
import sys
import ctypes
import numpy as np
import numpy.ma as ma
import awkward as ak

#----------------------------------------------------------------------#
# Set path to shared library depending on system type

LIBFILENAME = os.path.abspath(os.path.dirname(__file__))
if sys.platform == "darwin":
    LIBFILENAME = os.path.join(LIBFILENAME,"../hipo/libhipo4.dylib")
else: 
    LIBFILENAME = os.path.join(LIBFILENAME,"../hipo/libhipo4.so")

#----------------------------------------------------------------------#
# Basic  I/O behaviors

def open(filename,mode="r"):
    """
    Arguments:
        filename - pretty obvious
        mode     - "r" : read, "w" : write, "a" : append
    Description:
        Open a HIPO file to read.
    """
    f = hipofile(filename,LIBFILENAME,mode=mode)
    f.open()
    return f

def iterate(files,banks,step=100):
    """
    Arguments:
        files - list of file names
        banks - list of bank names to read
    Description:
        Iterate through
    """
    f = hipochain(files,banks,step=step)
    return f


def create(filename):
    """
    Arguments:
        filename - pretty obvious
    Description:
        Open a HIPO file to write (from scratch).
    """
    f = hipofile(filename,LIBFILENAME,mode="w")
    return f

def recreate(filename):
    """
    Arguments:
        filename - pretty obvious
    Description:
        Open a HIPO file to write (from scratch).
    """
    f = hipofile(filename,LIBFILENAME,mode="a")
    f.open() #NOTE: This just opens the reader.  To open the writer, call f.open() again explicitly after adding schema you want to write.
    return f

#----------------------------------------------------------------------#
# Classes: hipofile, hipofileIterator, hipochain, hipochainIterator

class hipofile:

    def __init__(self,filename,libpath,mode="r"):
        self.filename = filename
        self.libpath  = libpath
        self.mode     = mode # "r" : read, "w" : write, "a" : append
        self.lib      = ctypes.CDLL(self.libpath)
        self.status   = ctypes.c_int(0)
        self.group    = 0
        self.item     = 1
        self.dtypes   = {}
        self.buffext  = "~"
        self.buffname = None
        
    def open(self):
        """
        Description:
            Open a HIPO file to read, write (from scratch), or append data.
            IMPORTANT:  Make sure you add schema before opening a file to write!
        """
        if self.mode=="r": self.lib.hipo_file_open(self.filename.encode('ascii'))
        if self.mode=="w": self.lib.hipo_write_open_(self.filename.encode('ascii'))
        if self.mode=="a" and self.buffname is None:
            self.lib.hipo_file_open(self.filename.encode('ascii'))
            self.lib.hipo_read_all_banks_()
            self.group = self.lib.hipo_get_group_()
            self.buffname = self.filename + self.buffext #NOTE: Separate code here so that you can call addSchema()
        elif self.mode=="a" and self.buffname is not None:
            self.lib.hipo_write_open_(self.buffname.encode('ascii'))
            
    def flush(self):
        """
        Description:
            Write current HIPO writer buffer to file.
        """
        self.lib.hipo_write_flush_()

    def close(self,mode="w"):
        """
        Arguments:
            mode - "r" : read, "w" : write, "a" : append
        Description:
            Close osstream for an open file.
        """
        if mode=="r": pass #NOTE: Nothing to do here.
        if mode=="w":
            self.lib.hipo_write_close_()
        if mode=="a":
            self.lib.hipo_write_close_()
            # shutil.copy(self.buffname,self.filename) #TODO: Check this
            # shutil.rm(self.buffname) #TODO: Check this

    def goToEvent(self,event):
        """
        Arguments:
            event - integer # indicating event # in file (starts at 0)
        Returns:
            boolean - True if requested event exists, otherwise False
        Description:
            Move to requested HIPO event in a file in read mode.
        """
        self.status = ctypes.c_int(self.lib.hipo_go_to_event_(ctypes.byref(self.status),ctypes.byref(ctypes.c_int(event))))
        if self.status.value==0: return True
        return False

    def nextEvent(self):
        """
        Returns:
            boolean - True if next event exists, otherwise False
        Description:
            Move to next HIPO event from a file in read mode.
        """
        self.status = ctypes.c_int(self.lib.hipo_file_next_(ctypes.byref(self.status)))
        if self.status.value==0: return True
        return False

    def addSchema(self, name, namesAndTypes, group=-1, item=1):
        """
        Arguments:
            name          - bank name
            namesAndTypes - map of column names to types ("D", "F", "I", "B", "S", "L")
            group         - group # for bank #TODO Might need to keep track of this.
            item          - item # for bank 
        Description:
            Add a schema structure to HIPO file writer dictionary for
            a bank you wish to write.  NOTE: Do this BEFORE opening the 
            file in write mode.
        """

        names = namesAndTypes.keys()
        types = namesAndTypes.values()
        schemaString = ",".join( ["/".join( [key,namesAndTypes[key]] ) for key in namesAndTypes] )
        if group <= self.group or group < 0:
            self.group += 1
            group = self.group

        self.lib.hipo_add_schema_(
            schemaString.encode("ascii"),
            name.encode("ascii"),
            ctypes.c_int(group),
            ctypes.c_int(item)
        )

    def addEvent(self):
        """
        Description:
            Adds current hipo event to buffer and advances writer to next event.
        """
        self.lib.hipo_add_event_()

    def writeEvent(self):
        """
        Description:
            Writes current hipo event buffer to file.
        """
        self.lib.hipo_write_flush_()

    def writeAllBanks(self):
        """
        Description:
            Write all existing banks to event for appending to file.
        """
        self.lib.hipo_write_all_banks_()

    def writeBank(self, name, names, data, dtype="D"):

        """
        Arguments:
            name  - bank name
            names - column names
            data  - 2D numpy array of dimension (columns,rows)
            dtype - data type ("D", "F", "I", "B", "S", "L")
        Description:
            Fill an event bank with data and write to buffer.
        """

        # Define (2D, ndim=1 for 2D---it's confusing) array type 
        _2d = np.ctypeslib.ndpointer(dtype=np.uintp, ndim=1, flags='C')

        # Specify argument types for C function
        hipo_write_bank_ = self.lib.hipo_write_bank_
        hipo_write_bank_.argtypes = [
            ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p), _2d,
            ctypes.c_int, ctypes.c_int, ctypes.c_char_p
            ] 
        hipo_write_bank_.restype = None

        # Format arguments
        names = (ctypes.c_char_p * len(names))(*[ctypes.c_char_p(n.encode("ascii")) for n in names])
        x = (data.__array_interface__['data'][0]
            + np.arange(data.shape[0])*data.strides[0]).astype(np.uintp)

        self.lib.hipo_write_bank_(
            ctypes.c_char_p(name.encode("ascii")),
            names,
            x,
            ctypes.c_int(np.shape(data)[0]),
            ctypes.c_int(np.shape(data)[1]),
            dtype.encode("ascii")
        )

    def newTree(self,bank,bankdict,group=None,item=None):
        """
        Arguments:
            bank     - bank name
            bankdict - dictionary of bank entry names to data types ("D", "F", "I")
            group    - group identifier for bank (must be unique)
            item     - item identifier for bank (does not have to be unique)
        Description:
            Mimics uproot newTree function.
        """
        group = self.group if group is None else group
        item  = self.item if item is None else item
        self.addSchema(bank,bankdict,group,item)
        self.dtypes[bank] = bankdict

    def extend(self,datadict):
        """
        Arguments:
            datadict - dictionary of bank names to data arrays of shape (nEvents,nEntries,nRows)
        Description:
            Mimics uproot extend function. NOTE: dtype argument fixed until I figure out how to pass
            different types to C wrapper.
        """
        keys = list(datadict.keys())
        nEvents = len(datadict[keys[0]])

        # Write mode routine
        if self.mode == "w":
            for event in range(nEvents):
                for bank in datadict: # This requires datadict shape to be (nEvents,nNames,nRows)
                    self.writeBank(bank,self.dtypes[bank].keys(),datadict[bank][event],dtype="D") #TODO: self.dtypes[bank]
                self.addEvent()
            self.writeEvent()

        # Append mode routine
        elif self.mode == "a":
            for event in range(nEvents):
                if not self.nextEvent():
                    print(" *** ERROR *** Tried to more events than are in current file.") #TODO: Implement logging and figure out how to append more events safely.
                    continue
                self.writeAllBanks()
                for bank in datadict: # This requires datadict shape to be (nEvents,nNames,nRows)
                    self.writeBank(bank,self.dtypes[bank].keys(),datadict[bank][event],dtype="D") #TODO: self.dtypes[bank]
                self.addEvent()
            self.writeEvent()

    def write(self):
        """
        Alias for self.close()
        """
        self.close()

    def hasBank(self,bankName):
        """
        Arguments:   bankName - pretty obvious
        Description: Check if bank exists for current file.
        """
        return self.lib.hipo_has_bank_( #TODO: Figure out how to see if bank exists in current event.
            ctypes.c_char_p(bankName.encode('ascii')),
            ctypes.c_int(len(bankName))
        )

    def show(self):
        """
        Description: Print out all available bank names in open file.
        """
        self.lib.hipo_show_banks_()
    
    def showBank(self,bankName):
        """
        Arguments:   bankName - pretty obvious
        Description: Print out bank contents for current event.
        """
        self.lib.hipo_show_bank_(
            ctypes.c_char_p(bankName.encode('ascii')),
            ctypes.c_int(len(bankName))
        )

    def getBanks(self):
        """
        Description:
            Returns a list of all bank names in the reader dictionary.
        """
        hipo_get_banks_ = self.lib.hipo_get_banks_
        hipo_get_banks_.restype = ctypes.c_char_p
        return hipo_get_banks_().decode('ascii').split(" ")

    def readAllBanks(self):
        """
        Description:
            Read all existing banks to event for appending to file.
        """
        self.lib.hipo_read_all_banks_()

    def readBank(self,bankName,verbose=False):
        """
        Arguments:
            bankName - pretty obvious
            verbose  - print out loading message for each event if true
        Description:
            Setup to read bank contents for each event into memory.
        """
        self.lib.hipo_read_bank_(
            ctypes.c_char_p(bankName.encode('ascii')),
            ctypes.c_int(len(bankName)),
            verbose
        )

    def getGroup(self):
        """
        Description:
            Get highest # group of all existing schema in reader for initiating file in append mode.
        """
        return self.lib.hipo_get_group() #TODO:

    def getEntries(self,bankName):
        """
        Arguments:
            bankName - pretty obvious
        Description:
            Get # of entries in bank.  Make sure you read bank first 
            with readBank(bankName) method above.
        """
        return self.lib.hipo_get_bank_entries_(
            ctypes.c_char_p(bankName.encode('ascii')),
            ctypes.c_int(len(bankName))
        )

    def getNamesAndTypes(self,bankName):
        """
        Arguments:
            bankName - pretty obvious
        Returns:
            data     - ctypes c_char_p array containing the bank entries
        Description:
            Get a list of the entry names from the data table in the current event's bank.
        """
        hipo_get_bank_entries_names_types_ = self.lib.hipo_get_bank_entries_names_types_
        hipo_get_bank_entries_names_types_.restype = ctypes.c_char_p
        bankdict = hipo_get_bank_entries_names_types_(
            ctypes.c_char_p(bankName.encode('ascii')),
            ctypes.c_int(len(bankName))
        ).decode('ascii')
        bankdict = bankdict.split("}{")[1][:-1]
        bankdict = { entry.split("/")[0]:entry.split("/")[1] for entry in bankdict.split(",")}
        return bankdict
    
    def getNames(self,bankName):
        """
        Arguments:
            bankName - pretty obvious
        Returns:
            data     - ctypes c_char_p array containing the bank entries
        Description:
            Get a list of the entry names from the data table in the current event's bank.
        """
        hipo_get_bank_entries_names_ = self.lib.hipo_get_bank_entries_names_
        hipo_get_bank_entries_names_.restype = ctypes.c_char_p
        return hipo_get_bank_entries_names_(
            ctypes.c_char_p(bankName.encode('ascii')),
            ctypes.c_int(len(bankName)),
        ).decode('ascii').split(' ')

        # return [data[i].decode('ascii') for i in range(nEntries)]

    def getTypes(self,bankName):
        """
        Arguments:
            bankName - pretty obvious
        Returns:
            data     - ctypes c_char_p array containing the bank entries
        Description:
            Get a list of the entry types from the data table in the current event's bank.
        """
        nEntries = self.getEntries(bankName)
        data = (ctypes.c_char_p * nEntries)()
        self.lib.hipo_get_bank_entries_types_(
            ctypes.c_char_p(bankName.encode('ascii')),
            ctypes.c_int(len(bankName)),
            data
        )

        return [data[i].decode('ascii') for i in range(nEntries)]

    def getRows(self,bankName):
        """
        Arguments:
            bankName - pretty obvious
        Description:
            Get # of rows in bank.  Make sure you read bank first 
            with readBank(bankName) method above.
        """
        return self.lib.hipo_get_bank_rows_(
            ctypes.c_char_p(bankName.encode('ascii')),
            ctypes.c_int(len(bankName))
        )

    def getInts(self,bankName,item):
        """
        Arguments:
            bankName - pretty obvious
            item     - column name you wish to read in bank
        Returns:
            data     - ctypes int array containing the bank entries
        Description:
            Get a column of ints from the data table in the current event's bank.
        """
        bankRows = self.getRows(bankName)
        data = (ctypes.c_int * bankRows)()
        self.lib.hipo_get_ints(
            ctypes.c_char_p(bankName.encode('ascii')),
            ctypes.c_int(len(bankName)),
            ctypes.c_char_p(item.encode('ascii')),
            ctypes.c_int(len(item)),
            data
        )
        return data

    def getFloats(self,bankName,item):
        """
        Arguments:
            bankName - pretty obvious
            item     - column name you wish to read in bank
        Returns:
            data     - ctypes float array containing the bank entries
        Description:
            Get a column of floats from the data table in the current event's bank.
        """
        bankRows = self.getRows(bankName)
        data = (ctypes.c_float * bankRows)()
        self.lib.hipo_get_floats(
            ctypes.c_char_p(bankName.encode('ascii')),
            ctypes.c_int(len(bankName)),
            ctypes.c_char_p(item.encode('ascii')),
            ctypes.c_int(len(item)),
            data
        )
        return data

    def getDoubles(self,bankName,item):
        """
        Arguments:
            bankName - pretty obvious
            item     - column name you wish to read in bank
        Returns:
            data     - ctypes double array containing the bank entries
        Description:
            Get a column of doubles from the data table in the current event's bank.
        """
        bankRows = self.getRows(bankName)
        data = (ctypes.c_double * bankRows)()
        self.lib.hipo_get_doubles(
            ctypes.c_char_p(bankName.encode('ascii')),
            ctypes.c_int(len(bankName)),
            ctypes.c_char_p(item.encode('ascii')),
            ctypes.c_int(len(item)),
            data
        )
        return data

    def getShorts(self,bankName,item):
        """
        Arguments:
            bankName - pretty obvious
            item     - column name you wish to read in bank
        Returns:
            data     - ctypes short array containing the bank entries
        Description:
            Get a column of shorts from the data table in the current event's bank.
        """
        bankRows = self.getRows(bankName)
        data = (ctypes.c_short * bankRows)()
        self.lib.hipo_get_shorts(
            ctypes.c_char_p(bankName.encode('ascii')),
            ctypes.c_int(len(bankName)),
            ctypes.c_char_p(item.encode('ascii')),
            ctypes.c_int(len(item)),
            data
        )
        return data

    def getLongs(self,bankName,item):
        """
        Arguments:
            bankName - pretty obvious
            item     - column name you wish to read in bank
        Returns:
            data     - ctypes long array containing the bank entries
        Description:
            Get a column of longs from the data table in the current event's bank.
        """
        bankRows = self.getRows(bankName)
        data = (ctypes.c_long * bankRows)()
        self.lib.hipo_get_longs(
            ctypes.c_char_p(bankName.encode('ascii')),
            ctypes.c_int(len(bankName)),
            ctypes.c_char_p(item.encode('ascii')),
            ctypes.c_int(len(item)),
            data
        )
        return data

    def __iter__(self):
        return hipofileIterator(self)

class hipofileIterator:

    def __init__(self,hipofile):
        self.hipofile = hipofile
        self.idx = 0

    def __next__(self):
        if self.hipofile.nextEvent():
            self.idx += 1
            return self.hipofile #TODO: This is kind of useless right now.
        raise StopIteration

class hipochain:

    def __init__(self,names,banks="",step=100,mode="r"):
        self.names   = names

        # Parse regex NOTE: Must be full or relative path from $PWD.  ~/... does not work.
        if type(self.names)==str:
            self.names = glob.glob(names)
        else:
            newnames = []
            for i in range(len(self.names)):
                files = glob.glob(self.names[i])
                if len(files>0):
                    for file in files:
                        self.newnames.append(file)
            self.names = newnames

        self.banks   = banks if banks != "" else self.getBanks()
        self.step    = step
        self.mode    = "r"   #TODO: Does it make sense to just fix this?
        self.verbose = False #TODO: Do we really need this?

    def __iter__(self):
        return hipochainIterator(self)

class hipochainIterator:

    def __init__(self,chain):
        self.chain   = chain
        self.idx     = 0
        self.counter = 0
        self.file    = None
        self.items   = {}
        self.dict    = None

    def switchFile(self):
        """
        Description:
            Checks if next file exists and opens if so. 
        """
        # Open file
        self.file = hipofile(self.chain.names[self.idx],LIBFILENAME,mode=self.chain.mode)
        self.file.open()
        self.idx += 1

        # Add banks you want to read
        for b in self.chain.banks:
            self.file.readBank(b,self.chain.verbose)
            helper = self.file.getNamesAndTypes(b)
            self.items[b] = helper

    def __next__(self):
        """
        Description:
            Loops files reading requested banks if they exist 
        """

        if self.idx == 0: self.switchFile() # Load first file manually
        while self.idx<(len(self.chain.names)): #TODO: Check this condition.

            # Check if output array has been initialized
            if self.dict is None:
                self.dict = {}

            # Loop events in current file
            while self.file.nextEvent():

                # Get bank data
                for bank in self.chain.banks:
                    for item in self.items[bank]:
                        data = []
                        if   self.items[bank][item]=="F": data = self.file.getFloats(bank,item)
                        elif self.items[bank][item]=="I": data = self.file.getInts(bank,item)
                        elif self.items[bank][item]=="D": data = self.file.getDoubles(bank,item)
                        elif self.items[bank][item]=="L": data = self.file.getLongs(bank,item)

                        # Add bank data to batch dictionary
                        if not bank+"_"+item in self.dict.keys() : self.dict[bank+"_"+item] = [np.array(data)]
                        else: self.dict[bank+"_"+item].append(np.array(data))               

                # Check size of output array
                self.counter += 1
                if self.counter % self.chain.step == 0:
                    res       = self.dict
                    self.dict = None
                    return res

            # Switch the file AFTER you get through event loop above
            self.switchFile()

        # Final return for remainder
        if self.dict != None:
            res       = self.dict
            self.dict = None
            return res #TODO: Will this return last remainder that is not necessarily stepsize?
        
        # Final stop
        raise StopIteration
