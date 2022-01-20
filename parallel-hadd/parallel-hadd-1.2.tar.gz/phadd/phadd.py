
from distutils.spawn import find_executable
from os import listdir, devnull
from enum import IntEnum, unique
from shutil import rmtree, copy2
from os.path import isfile
from random import choice
from string import ascii_lowercase, ascii_uppercase, digits
from tempfile import mkdtemp
from subprocess import call
from sys import exit

import logging
import argparse


__version__ = "1.2"

@unique
class EXIT(IntEnum):
    """ Shell exit codes are being used in this package. """

    OK = 0
    Error_bad = 1
    MISSING_HADD = 2

# Test to see if Multiprocessing exists
has_multiprocessing= True
try:
    import multiprocessing as mp
except ImportError:
    has_multiprocessing= False        
    
# Define Helper functions
def listdir_with_path(dir):

    """ It returns a list of files with their path """    
    return [dir + '/' + file for file in listdir(dir)]

def hadd_mp(input_tuple):
    """ Takes an input_tuple, hadds the files, and saves them to the given
    directory."""
    (out_file, start_num, end_num, total_num, input_files) = input_tuple
    """The input_tuple has the following format 
    ( out_file, start_num, end_num, total_num, (file0, ..., fileN) ) """
    args = ["hadd", out_file] + input_files
    logging.debug("Calling hadd: Input: %s Output: %s", input_files, out_file)
    
    # calling hadd
    code = None
    logging.debug("hadding files %i-%i of %i." % (start_num, end_num, total_num))
    code = call(args)
    ## check for hadd errors
    if code != 0:
       logging.error("Hadd error occurs")
       exit(EXIT.Error_bad)
    else:
        logging.debug("hadd finished successfully")
        return EXIT.OK
    
# hadd class
class Hadd:
    """Define a hadd for hadd files in parallel"""
    
    
    def __init__(
        self,
        outfile,
        input_files,
        tmpdir,
        force_overwrite=False,
        save= False,
        num_files=20,
        num_jobs=1,
    ):
        """Class setup"""
        self.outfile = outfile
        self.input_files = input_files
        self.force_overwrite = force_overwrite
        self.num_jobs = num_jobs
        self.num_files= num_files
        self.save = save
        self.counter = 0
        self.__check_output_file()
        self.__print_in_and_out()
        self.__set_tmp_dir(tmpdir)
        
    def run_hadd(self):
        """ Function to combine files by looping through input files """
        logging.info("Adding files together")
    
        i=0
        input_files = list(self.input_files) 
        while True:
            logging.info("Starting step %s", i)
            tmp_write_dir= mkdtemp(prefix=str(i) + "_", dir=self.tmpdir) + "/"
            ## Tuplize the files into a tuple   
            tmp_tuples= self.__tuplize_files(tmp_write_dir, input_files)
            ## Run hadd in parallel
            self.__hadd_mp(tmp_write_dir, tmp_tuples)    
            ## check output files
            tmp_read_dir= tmp_write_dir
            input_files = listdir_with_path(tmp_read_dir)
            ## If there are no more files except one, break
            if len(input_files) == 1:
                logging.info("Copying final file: %s --> %s", input_files[0], self.outfile)
                copy2(input_files[0], self.outfile)
                break
            else: 
                i += 1      
        ## clean up tmp dir
        self.__cleanup()   
    def __hadd_mp(self, target_dir, in_tuples):
        """ Takes a list of input_files, and write_dir it hadds the files and save them to target_dir"""
        ## If we run only one num_jobs
        if self.num_jobs <= 1:
            for tuple in in_tuples:
                hadd_mp(tuple)
        ## If multiple jobs
        else: 
            pool = mp.Pool(processes=self.num_jobs)
            pool.map(hadd_mp, in_tuples)
            pool.close()
            pool.join() # wait until all processes are done
    def __print_in_and_out(self):
        """ function to print list of input and output files """
        logging.info("Number of files to hadd at once : %s", self.num_files)
        logging.info("Output file: %s", self.outfile)
        logging.info("Input files: %s", self.input_files)  
              
    def __check_output_file(self):
        """ This function checks if the output file exists, if so it overwrite if we have set force_overwrite to True """
        if not self.force_overwrite and isfile(self.outfile):
            logging.error("Output file already exists! File: %s", self.outfile)
            exit(EXIT.Error_bad)
        elif self.force_overwrite and isfile(self.outfile):
            logging.warning("Output file already exists!, it will be overwritten", self.outfile)
                
    def __tuplize_files(self, target_dir, input_files):    
        """ Takes the input list and writes a specialized tuple of them""" 
        file_tuple= []
        
        # Loop over to fill tuples
        total_num = len(input_files)
        for i in range(0, total_num, self.num_jobs):
            out_file = self.__get_random_root_name(target_dir) 
            tmp_list = input_files[i:i+self.num_files]
            start_num = i + 1
            end_num = i + len(tmp_list)
            new_tuple = (out_file, start_num, end_num, total_num, tmp_list)
            file_tuple.append(new_tuple)
            
        return tuple(file_tuple)
    
    
    def __cleanup(self):
        """ This function cleans up the intermediate files in tmpdir"""
        if not self.save:
            logging.info("Delete tmpdir %s", self.tmpdir) 
            rmtree(self.tmpdir)
        else:
            logging.debug("tmpdir %s will be kept", self.tmpdir)
            
    def __set_tmp_dir(self, tmpdir):
        """ This function seuup a temporary directory to hold intermediate files """   
        if tmpdir is None:
            self.tmpdir = mkdtemp(prefix="phadd_") + "/"
        else: 
            self.tmpdir = mkdtemp(prefix="phadd", dir=tmpdir) + "/"
            logging.debug("tmpdir %s will be created", self.tmpdir)
                 
                     
    def __get_random_root_name(self, dir):  
        """ This function returns a random root name for the output file """
        chars = ascii_uppercase + ascii_lowercase + digits
        random = []
        for _ in range(10):
            random.append(choice(chars))
            num = self.counter
            self.counter += 1
        return dir + "".join(random) + "_" + str(num) + ".root"                        
    
# The main function
def main():
        ## Set the default job number
    if has_multiprocessing:
        N_JOBS = int(mp.cpu_count() * 2)
    else: 
        N_JOBS = 1
        
    argparser = argparse.ArgumentParser(description="Hadd ROOT histograms in parallel")
    argparser.add_argument("output_file", type=str, help="the output file")
    argparser.add_argument("input_files", type=str, nargs="+", help="one or more input files")
    argparser.add_argument("-t","--tmpdir", action="store", type=str, default=None, help="the temporary directory to store intermediate files")
    argparser.add_argument("-j","--jobs", action="store", type=int, dest="num_jobs", default=N_JOBS, help="the number of jobs to run in parallel , [default cpu_count * 2 = {N_JOBS}")
    argparser.add_argument("-n","--num_files", action="store", type=int, default=10, help="the number of files to hadd at once")
    argparser.add_argument("-f","--force_overwrite", action="store_true",default=False, help="force overwrite of output file")
    argparser.add_argument("-s","--save-tmp", action="store_true", default=False, help="save the intermediate files, otherwise they will be deleted (which is the default)")
    argparser.add_argument("-l","--log", help="the log level, [default Warning]", dest="log_level", default=logging.WARNING, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    argparser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
        
    args = argparser.parse_args()
    logging.basicConfig(level=args.log_level)
    logging.debug("args: %s", args)
        
        
    ## Let's check if hadd command exists
    if find_executable("hadd") is None:
        logging.error("hadd command not found, please install it")
        exit(EXIT.MISSING_HADD)
            
    ## check if num_jobs is not bigger than the number of cores
    if args.num_jobs > mp.cpu_count() and not has_multiprocessing:
        logging.warning("has_multiprocessing is not available and num_jobs is bigger than the number of cores, it will be reduced to %s", mp.cpu_count())
        args.num_jobs = mp.cpu_count()
        
    ## check if we only have one input file 
    if len(args.input_files) == 1:
        logging.warning("Only one input file is given, it will be copied to the output file")
        logging.info("copy the input file to the output file : %s --> %s", args.input_files[0], args.output_file)
        copy2(args.input_files[0], args.output_file)
        exit(EXIT.OK)
            
    ## Also check if the number of input files is negative
    if len(args.input_files) < 1:
        logging.error("Hadding one file or less is not supported (will not converge)")
        exit(EXIT.Error_bad)
        
        
        
    ## Setup the Hadd object
    hadd = Hadd(args.output_file, 
                args.input_files,
                args.tmpdir,
                args.force_overwrite,
                args.save_tmp,
                args.num_files,
                args.num_jobs,
    )
    hadd.run_hadd()
    
if __name__ == "__main__":
    main()    