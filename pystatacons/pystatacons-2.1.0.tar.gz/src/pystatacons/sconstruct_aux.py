import subprocess
import re
import os
from pkg_resources import packaging
import sys
from pathlib import Path #scons' Glob is not recursive
import platform

import SCons
from SCons.Defaults import DefaultEnvironment
import SCons.Debug
import SCons.Script
from SCons.Script import AddOption, GetOption, SetOption
from SCons.Builder import Builder


has_pywin32 = False
if platform.system()=="Windows":
    import importlib
    has_pywin32 = importlib.util.find_spec("win32api") is not None
    
in_stata = 'sfi' in sys.modules
pre_sys_stdout = sys.stdout #Need this for SCons.Debug.Trace while run from Stata once building (e.g., stata_run)
def print_during_build(msg):
    if not GetOption('silent'):
        SCons.Debug.Trace(msg, pre_sys_stdout)
        if in_stata: 
            import sfi
            sfi.SFIToolkit.pollnow()

##############################################
#               Configuration                #
##############################################
# use to test for optional keys
def query_config(env, header, key, default=None):
    if 'CONFIG' in env and header in env['CONFIG'] and key in env['CONFIG'][header]:
        return env['CONFIG'][header][key]
    return default

def _find(pathname, paths=None):
    if paths is None:
        paths = os.environ['PATH'].split(os.pathsep)
    for dirname in paths:
        candidate = os.path.join(dirname, pathname)
        if os.path.isfile(candidate):
            return (pathname, candidate, dirname)
    return None

def configuration(config_user_ini = 'config_user.ini', config_project_ini='config_project.ini'):
    import shutil
    import configparser
    # Copies templates if no such file exists
    if not os.path.isfile(config_user_ini) and os.path.isfile('utils/config_user_template.ini'):
        shutil.copy('utils/config_user_template.ini', config_user_ini)

    CONFIG = configparser.ConfigParser()
    # Load the easy defaults initially
    CONFIG['SCons'] = {'success_batch_log_dir': '', 'use_custom_datasignature': 'Strict', 'stata_chdir': ''}
    
    # Loads config ini files (user ones can over-ride project ones)
    config_files = [f for f in [config_project_ini, config_user_ini] if os.path.isfile(f)]
    CONFIG.read(config_files)

    #Remove quotes form paths if people are confused
    def strip_quotes_config(k1, k2, conf):
        if k1 in conf and k2 in conf[k1]:
            conf[k1][k2] = conf[k1][k2].strip('"').strip("'")

    strip_quotes_config('Programs', 'stata_exe', CONFIG)
    strip_quotes_config('SCons', 'success_batch_log_dir', CONFIG)
    strip_quotes_config('Project', 'cache_dir', CONFIG)
    
    return CONFIG

AddOption(
    '--config-user',
    dest='config_user',
    action='store',
    type="string",
    help='Specify config_user file path.',
)

##############################################
#           Stata tool (find it)             #
##############################################
def stata_tool(env):
    plat = platform.system()
    if not query_config(env, 'Programs', 'stata_exe', default=None) is None:
        env['STATABATCHEXE'] = env['CONFIG']['Programs']['stata_exe']
    
    else:      
        #TODO: allow abs path for STATAEXE (use os.path.isabs(...))
        def_execs = {'Windows': ['StataMP-64.exe', 'StataSE-64.exe', 'StataBE-64.exe', 'Stata-64.exe'], 
                     'Linux':['stata-mp', 'stata-se', 'stata'],
                     'Darwin':['StataMP', 'StataSE', 'StataBE', 'Stata']}
        candidate_stata_exes = def_execs[plat]
        if 'STATAEXE' in os.environ:
            candidate_stata_exes = [os.environ['STATAEXE']] + candidate_stata_exes
        found_ret = None
        for candidate_stata_exe in candidate_stata_exes:
            found_ret = _find(candidate_stata_exe)
            if found_ret is not None:
                env['STATABATCHEXE'] = found_ret[0]
                break
        if found_ret is None and plat=='Windows':
            for candidate_stata_exe in candidate_stata_exes:
                found_ret = _find(candidate_stata_exe, [os.path.join(os.environ['ProgramFiles'], "Stata" + str(n)) for n in range(17, 12, -1)])
                if found_ret is not None:
                    env['STATABATCHEXE'] = found_ret[1]
                    break
        if found_ret is None and plat=='Darwin':
            for candidate_stata_exe in candidate_stata_exes:
                found_ret = _find(candidate_stata_exe, ["/Applications/Stata/" + st_type + ".app/Contents/MacOS/" for st_type in def_execs[plat]])
                if found_ret is not None:
                    env['STATABATCHEXE'] = found_ret[1]
                    break
            
        if found_ret is None:
            print("Can't find Stata from config or defaults")
            return

    batch_flags = {'Windows': '/e', 
                   'Linux': '-b',
                   'Darwin': '-e'}
    
    env['STATABATCHFLAG'] = batch_flags[plat]
    env['STATABATCHCOM'] = '"' + env['STATABATCHEXE'] + '"' if " " in env['STATABATCHEXE'] else env['STATABATCHEXE']
    env['STATABATCHCOM'] = env['STATABATCHCOM']  + " " + batch_flags[plat]



##############################################
#              Deciders                      #
##############################################
# Note that timestamp-newer/make compares target vs source, whereas timestamp-changed doesn't look at target (just prev vs current of source)
# 'content-timestamp' = 'timestamp-changed' and 'content'

# 'make' and 'content'
def dependency_newer_then_content_changed(dependency, target, prev_ni, repo_node=None):
    return dependency.changed_timestamp_newer(target, prev_ni, repo_node) and dependency.changed_content(target, prev_ni, repo_node)

# 'make' and 'content-timestamp'
def changed_timestamp_then_dependency_newer_then_content_content(dependency, target, prev_ni, repo_node=None):
    return dependency.changed_timestamp_newer(target, prev_ni, repo_node) and dependency.changed_timestamp_then_content(target, prev_ni, repo_node)

decider_str_lookup = {'content-timestamp-newer': dependency_newer_then_content_changed,
                      'content-timestamp-newer-timestamp-changed': changed_timestamp_then_dependency_newer_then_content_content}
decider_str_lookup.update({k:k for k in ['MD5', 'content', 'MD5-timestamp', 'content-timestamp', 'timestamp-newer', 'make', 'timestamp-match']})


##############################################
#              Builders                      #
##############################################
#We impliment these skip-logic routines in stata_run() and not a dedicated Decider so that
# we can have them thought of as 'built' and info saved in the sconsign file. Also,
# someone can change them on the command-line without changing any files and is orthogonal
# to what decider they choose (MD5, MD5-timestamp)
AddOption(
    '--assume-built',
    dest='assume_built',
    action='store',
    type="string",
    help='Assume these targets are up-to-date (and if all targets for a task are up-to-date it will be skipped).',
)
AddOption(
    '--assume-done',
    dest='assume_done',
    action='store',
    type="string",
    help='Assume these do-files are up-to-date and do no rebuild.',
)
assume_built = GetOption('assume_built') #If there are outer quotes on the cli, these are stripped.
assume_built_list = []
if not assume_built is None:
    assume_built_list = [str(path) for file_pattern in assume_built.split(':') for path in Path().rglob(file_pattern) if not path.is_dir()] #could've used os.pathsep, but want consistent across sytems

assume_done = GetOption('assume_done') #If there are outer quotes on the cli, these are stripped.
assume_done_list = []
if not assume_done is None:
    assume_done_list = [str(path) for file_pattern in assume_done.split(':') for path in Path().rglob(file_pattern) if not path.is_dir()] #could've used os.pathsep, but want consistent across sytems

def try_hidden_desktop(cmd_line, cwd=None, disp_str=""):
    try:
        import win32api, win32con, pywintypes, win32service, win32process, win32event
    except ImportError:
        print("Need pywin32 package installed.")
        return None
    
    #Open Desktop. No need to close as destroyed when process ends
    desktop_name = "pystatacons"
    try:
        hdesk = win32service.OpenDesktop(desktop_name, 0, True, win32con.MAXIMUM_ALLOWED)
    except win32service.error: #desktop doesn't exist
        try:
            sa = pywintypes.SECURITY_ATTRIBUTES()
            sa.bInheritHandle = 1
            hdesk = win32service.CreateDesktop(desktop_name, 0, win32con.MAXIMUM_ALLOWED, sa) # return if already created
        except win32service.error:
            print("Couldn't create Desktop")
            return None
    
    s = win32process.STARTUPINFO()
    s.lpDesktop = desktop_name
    s.dwFlags = win32con.STARTF_USESHOWWINDOW + win32con.STARTF_FORCEOFFFEEDBACK
    s.wShowWindow = win32con.SW_SHOWMINNOACTIVE
    (hProcess, hThread, dwProcessId, dwThreadId) = win32process.CreateProcess(None, cmd_line, None, None, False, 0, None, cwd, s)
    if disp_str!="": print_during_build(disp_str + ". Starting in hidden desktop (pid=" + str(dwProcessId) +")." + "\n")
    response = win32event.WaitForSingleObject(hProcess, win32event.INFINITE)
    ret_code = win32process.GetExitCodeProcess(hProcess)
    return ret_code

# Handles log file (better than Clean() as we typically want them removed right away (there may be a lot and this is easier))
def stata_run(target, source, env, params="", file_cmd="do", full_cmd=None):
    if 'STATABATCHEXE' not in env:
        raise LookupError("Can't find Stata")
    if full_cmd is None: 
        fname = str(source[0]) #Assumes the first element of source is the do file
        
    if not assume_built is None and all([str(t) in assume_built_list for t in target]):
        if full_cmd is None: full_cmd = file_cmd + ' "' + fname + '" ' + params
        for t in target: Path(str(t)).touch() #In case someone is using a time-stamp option for content being up-to-date. Touch() doesn't seem to work
        print_during_build("Assuming built: " + full_cmd + "\n")
        return 0
    if not assume_done is None and 'fname' in locals() and fname in assume_done_list:
        for t in target: Path(str(t)).touch() #In case someone is using a time-stamp option for content being up-to-date. Touch() doesn't seem to work
        print_during_build("Assuming done: " + fname + "\n")
        return 0

    cwd = None
    
    # Can't use the Builder chdir option, since that moves the target dir (and we want source)
    stata_chdir = env['CONFIG']['SCons']['stata_chdir']
    if stata_chdir=='': stata_chdir = '0'

    if stata_chdir == '1' and full_cmd is None:
        cwd = os.path.dirname(fname)
        fname = os.path.basename(fname)
    elif stata_chdir != '0':
        cwd = stata_chdir
        fname = os.path.relpath(fname, stata_chdir)

    if full_cmd is None: 
        full_cmd = file_cmd + ' "' + fname + '" ' + params
    
    #Get hash of command to avoid collisions
    import hashlib
    max_digest_len = 8
    cmd_digest = hashlib.md5(full_cmd.encode('utf-8')).hexdigest()[:max_digest_len]

    if 'fname' in locals():
        recipe_basename = os.path.splitext(os.path.basename(fname))[0]
        #TODO (potential): could track all basefnames (in StataBuild) and if there's duplicates then attach digests to those
        if file_cmd!="do" or params!="": 
            recipe_basename = recipe_basename + "-" + cmd_digest
    else:
        recipe_basename = "stata-"+cmd_digest
        
    log_basename = recipe_basename + ".log"
    if cwd is not None:
        log_name = os.path.join(cwd, log_basename)
    else:
        log_name = log_basename


    import tempfile
    with tempfile.TemporaryDirectory() as tmpdirname:
        #if GetOption("debug")!=[]: print_during_build("Executing in temporary directory: " + tmpdirname+"\n")
        recipe_fname = os.path.join(tmpdirname, recipe_basename+".do")
        with open(recipe_fname, "w") as recipe:
            recipe.write(full_cmd + '\n')
        
        args_split = [env['STATABATCHEXE'], env['STATABATCHFLAG'], "do", recipe_fname]
        digest_str = "" if 'fname' in locals() and file_cmd=="do" and params=="" else ". log="+log_basename
        
        no_hidden = query_config(env, 'Programs', 'win_stata_hidden', default='True')=='False'
        ret_code = None
        disp_str = "Running: "+env['STATABATCHCOM'] + " " +full_cmd+digest_str
        if has_pywin32 and not no_hidden:
            # win32's CreateProcess just takes a string, so see if need to wrap terms in quotes
            if not " " in recipe_fname: cmd_line = env['STATABATCHCOM'] + "do " + recipe_fname
            else: cmd_line = env['STATABATCHCOM'] + 'do "' + recipe_fname + '"'
            ret_code = try_hidden_desktop(cmd_line, cwd, disp_str)
        if ret_code is None:
            print_during_build(disp_str+"\n")
            cproc = subprocess.run(args_split, cwd=cwd)
            ret_code = cproc.returncode
        
    if ret_code!=0: #In case the Stata executable has a real issue
        return ret_code

    #check if script had an error
    retcode = 0
    with open(log_name, 'r') as f:
        lines = f.readlines() #if logs are really big, iterate until end to not store whole thing
        # Thanks to Kyle https://gist.github.com/pschumm/b967dfc7f723507ac4be#gistcomment-2657900
        match = re.search('^r\(([0-9]+)\);$', lines[-1]) #pytask looks in any of last 10 lines
        if match is not None:
            retcode = int(match[1])
    if retcode!=0: 
        os.replace(log_name, os.path.join(".", recipe_basename + ".log"))
        return retcode
    
    success_batch_log_dir = env['CONFIG']['SCons']['success_batch_log_dir']
    if success_batch_log_dir=="":
        os.remove(log_name)
    elif success_batch_log_dir!="." and success_batch_log_dir!="":
        os.replace(log_name, os.path.join(success_batch_log_dir, recipe_basename + ".log"))

    return 0
    

def copy_func(f):
    """Based on http://stackoverflow.com/a/6528148/190597 (Glenn Maynard)"""
    import types
    import functools
    g = types.FunctionType(f.__code__, f.__globals__, name=f.__name__,
                           argdefs=f.__defaults__,
                           closure=f.__closure__)
    g = functools.update_wrapper(g, f)
    g.__kwdefaults__ = f.__kwdefaults__
    return g

builder_counter = 1
task_dependencies = []
def stata_run_params_factory(self, target, source=None, do_file=None, params="", file_cmd="do", full_cmd=None, depends=None):
    """Factory function to create Builder instances for Stata tasks.

    Typically called as env.StataBuild() and omitting the first (self) argument.
    Marks all targets as Precious() (more intuitive for Stata users, and facilitates --assume-done/built).
    
    Build time: Tasks that specify file_cmd, params, or full_cmd  will have their stata batch-mode log-file names
    so that it's the typical name with a short hash signature at the end (to ensure uniqueness). 
    By default, successful tasks have their batch-mode log files deleted. An alternative is to put them in a directory
    Specified by the value of the 'success_batch_log_dir' key in the '[SCons]' header in a configuration file.
    By default, Stata's current directory when executing the script is the project root. This can be changed by specifying
    the value of the 'stata_chdir' key in the '[SCons]' header. If set to '1', then Stata will change to the directory of the script.
    If it is set as string,  then Stata will change to this directory.
    On Windows, running Stata in batch-mode will typically briefly steal the focus. If the pywin32 Python package is installed,
    we will execute Stata batch-mode tasks in a hidden desktop to prevent this. (Does not work 100% of the time in Stata for some unknown reason.)
    As these processes are hidden, process IDs are printed to allow someone to kill the process manually if desired using Task Manager's Details tab.
    To disable this hidden-desktop behavior, set the 'win_stata_hidden' key's value to False in the section [Programs].

    Parameters
    ----------
    self : Environment
        Environment
    target : list or str
        Targets of the task
    source : list or str
        Sources of the task. If mulitple, then the first should be the Stata script file.
    do_file : str
        Alternative way of specifying the do file.
    params : str
        Parameters to the script execution
    file_cmd : str
        Override 'do' command for the script.
    file_cmd : str
        Alternative to (file_cmd, script file, params) for specifying the full command
    depends : list
        Additional dependencies of the task. Equivalent to using Depends().

    Returns
    -------
    Builder instance
        Builder instance for this task

    """
    #partial approach doesn't work because the signature includes the address of original function
    env = self #print(type(self)) #self is env
    
    #scons typically deletes targets when they will be re-made, but we want to allow assume_built
    env.Precious(target)

    if do_file is not None: source = [do_file]

    if (params=="") and (file_cmd=="do") and (full_cmd is None): #don't need a custom builder
        build_obj = env.StataDo(target, source)
    else:
        custom_stata_run = copy_func(stata_run)
        custom_stata_run.__defaults__ = (params,file_cmd,full_cmd)
        global builder_counter
        cust_name = 'StataBuild' + str(builder_counter)
        builder_counter = builder_counter+1
        cust_builder = Builder(action=custom_stata_run)
        env.Append(BUILDERS={cust_name: cust_builder}) #TODO: Do I need this?
        
        build_obj = env.__dict__[cust_name](target, source) #don't think i need the env.XXX form
    
    if depends is not None:
        env.Depends(build_obj, depends)

    if type(source) is not list: source = [source]
    global task_dependencies
    deps = source
    if depends is not None: deps = deps + depends
    task_dependencies.append((target, deps))

    return build_obj
    


##############################################
#                Info                        #
##############################################
AddOption(
    '--show-config',
    dest='show_config',
    action='store_true',
    default=False,
    help='Show pystatacons configuration.',
)



    
##############################################
#              Patching                      #
##############################################
# how to get a Stata-style datasignature
int_env = None
def get_datasign(fname):
    if 'STATABATCHEXE' not in int_env:
        raise LookupError("Can't find Stata")
    m_str = int_env['CONFIG']['SCons']['use_custom_datasignature']
    meta = m_str!="DataOnly" and m_str!="Datasignature"
    meta_arg_split = [] if meta else ["nometa"]
    vv_only = m_str=="VVLabelsOnly"
    vv_only_arg_split = ["vv_labels_only"] if vv_only else []
    slow = (query_config(int_env, 'Project', 'cache_dir') is not None) or (query_config(int_env, 'Project', 'dta_sig_mode')=='slow')
    fast_arg_split = [] if slow else ["fast"]
    fname_abs = os.path.abspath(fname)
    
    #Run in temp-dir as in parallel mode we don't want to processes to try writing to the same stata.log
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdirname:
        #tmpdirname = "."
        sig_fname="sig.txt"
        args_split = [int_env['STATABATCHEXE'], int_env['STATABATCHFLAG'], 'complete_datasignature,', 'dta_file("' + fname_abs + '")', 'fname("' + sig_fname + '")'] + meta_arg_split + fast_arg_split + vv_only_arg_split
        
        no_hidden = query_config(int_env, 'Programs', 'win_stata_hidden', default='True')=='False'
        ret_code = None
        if has_pywin32 and not no_hidden:
            meta_arg = "" if meta else " nometa"
            fast_arg = "" if slow else " fast"
            vv_only_arg = " vv_labels_only" if vv_only else ""
            cmd_line = int_env['STATABATCHCOM'] + ' complete_datasignature, dta_file("' + fname_abs + '") fname("' + sig_fname + '")' + meta_arg + fast_arg + vv_only_arg
            ret_code = try_hidden_desktop(cmd_line, tmpdirname)
        if ret_code is None:
            cproc = subprocess.run(args_split, cwd=tmpdirname)
            ret_code = cproc.returncode
        if ret_code!=0: #In case the Stata executable has a real issue
            raise Exception("Couldn't get the file data-signature. Stata error")
        #Don't need to check log error, because lack of sig_fname will just raise exception
        with open(os.path.join(tmpdirname,sig_fname), "r") as f:
            sig = f.readline()
    return sig

# replacement of hash_file_signature. Checks if .dta and then special call, otherwise hands off to reguarl hash_file_signature()
special_sig_fns = {".dta": get_datasign}

def hash_file_signature_new(fname, chunksize=65536, hash_format=None):
    """
    Generate the md5 signature of a file

    Args:
        fname: file to hash
        chunksize: chunk size to read
        hash_format: Specify to override default hash format

    Returns:
        String of Hex digits representing the signature
    """
    import SCons.Util

    #print_during_build('new hash: ' + fname + "\n") 
    fname_ext = os.path.splitext(fname)[1]
    if fname_ext in special_sig_fns.keys():
        try:
            #print_during_build(str(fname_ext) + "\n")
            sig = special_sig_fns[fname_ext](fname)
            print_during_build('Computed ' + fname_ext[1:] + '-signature: ' + fname + "\n")
            return sig
        except Exception as e:
            print(e)
            #print_during_build(str(fname_ext) + "\n")
            pass

    return SCons.Util.hash_file_signature(fname, chunksize, hash_format)

# replacement of get_content_hash, just called hash_file_signature_new() instead of default
def get_content_hash_new(self) -> str:
    """
    Compute and return the hash for this file.
    """
    import SCons.Util
    import SCons.Node.FS
    if not self.rexists():
        return SCons.Util.hash_signature(SCons.Util.NOFILE)
    fname = self.rfile().get_abspath()
    try:
        cs = hash_file_signature_new(fname, chunksize=SCons.Node.FS.File.hash_chunksize)
    except EnvironmentError as e:
        if not e.filename:
            e.filename = fname
        raise
    return cs

# Remove condition where if file size < hash_chunksize it calls hash_signature(contents) instead of going down to hash_file_signature
def get_csig_new(self) -> str:
	"""Generate a node's content signature."""
	import SCons.Util
	ninfo = self.get_ninfo()
	try:
		return ninfo.csig
	except AttributeError:
		pass

	csig = self.get_max_drift_csig()
	if csig is None:
		try:
			size = self.get_size()
			if size == -1:
				contents = SCons.Util.NOFILE
			#elif size < File.hash_chunksize:
			#    contents = self.get_contents()
			else:
				csig = get_content_hash_new(self)
		except IOError:
			# This can happen if there's actually a directory on-disk,
			# which can be the case if they've disabled disk checks,
			# or if an action with a File target actually happens to
			# create a same-named directory by mistake.
			csig = ''
		else:
			if not csig:
				csig = SCons.Util.hash_signature(contents)
	
	ninfo.csig = csig

	return csig

#Save the originals (just in case someone needs them)
import SCons.Node.FS
get_content_hash_orig = SCons.Node.FS.File.get_content_hash
get_csig_orig = SCons.Node.FS.File.get_csig


def monkey_patch_scons(m_str=""):
    if not GetOption('silent'):
        if m_str!="DataOnly" and m_str!="Datasignature" and m_str!="VVLabelsOnly":
            print("Using 'Strict' custom_datasignature.")
            print("Calculates timestamp-independent checksum of dataset, including all metadata.")
            print("Edit use_custom_datasignature in config_project.ini to change.")
            print("  (other options are DataOnly, VVLabelsOnly, False)")
        elif m_str=="VVLabelsOnly":
            print("Using 'VVLabelsOnly' custom_datasignature.")
            print("Calculates timestamp-independent checksum of dataset, including variable and value labels.")
            print("Edit use_custom_datasignature in config_project.ini to change.")
            print("  (other options are Strict, DataOnly, False)")
        else:       
            print("Using 'DataOnly' datasignature.")
            print("Calculates timestamp-independent checksum of dataset, not including metadata")
            print("Edit use_custom_datasignature in config_project.ini to change.")
            print("  (other options are Strict, VVLabelsOnly, False)")
    ### Allow using Stata-style data-signatures instead of MD5 file hashes
    # Can't do this in SConstruct
    # Can't use Decider because I need my hash of the previous file and don't want to store it
    # Can't easily replace SCons.Util.hash_file_signature because it's imported druing SCons/Script/__init__.py
    # (https://medium.com/@chipiga86/python-monkey-patching-like-a-boss-87d7ddb8098e)
    # So have to override the calling class method instead
    SCons.Node.FS.File.get_content_hash = get_content_hash_new
    #Overwrite this one too that used a different hash method with small files
    SCons.Node.FS.File.get_csig = get_csig_new

def init_env(env=None, patch_scons_sig_fns=True, skip_scons_vs_check=False):
    """Sets up an environment for Stata.

    Reads configuration data and saves to env['CONFIG']. By default it will check for and read
    two ini files ('config_user.ini' and 'config_project.ini'), though the former
    can be overridden using the '--config-user=....' option.

    Displays the config if the '--show-config' option was specified.
    Runs a Stata Tool to find Stata automatically. 
    If this is not in a typical location then you can specify the full path as the value for a 'stata_exe' key under a '[Programs]' header in the configuration file.
    Attaches the 'StataBuild' Builder method to the environment.
    Optionally patches SCons to allow for file-extension-specific signature functions.

    Parameters
    ----------
    env : Environment
        Environment to configure for Stata support. If not provided will instantiate a DefaultEnvironment with the `os.environ` and no tools (many Stata users don't have defaults ones that SCons would complain about not finding).
    patch_scons_sig_fns : bool
        Whether to patch the SCons file signature functions to support special signature functions by file extensions. Default support is provided for .dta files.
    skip_scons_vs_check: bool
        If false, will not output a warning when using a version of SCons that has not been tested.

    Returns
    -------
    Environment
        Environment setup with Stata support.

    """
    if not skip_scons_vs_check and packaging.version.parse(SCons.__version__) < packaging.version.parse("4.2.0"):
        print("WARNING: You are running SCons version" + SCons.__version__ + " and statacons has only been tested on 4.2.0+.")

    if env is None: env = DefaultEnvironment(ENV=os.environ, tools=[])
    global int_env
    int_env = env

    if GetOption("config_user") is not None:
        config = configuration(config_user_ini=GetOption("config_user"))
    else:
        config = configuration()

    env['CONFIG'] = config

    env.Tool(stata_tool)
    
    stata_do_bld = Builder(action=stata_run)
    env.Append(BUILDERS={'StataDo': stata_do_bld})
    env.AddMethod(stata_run_params_factory, 'StataBuild')
    
    if GetOption("show_config"):
        SetOption("no_exec", True)
        SetOption("silent", True)
        print("Current config:")
        if 'Programs' not in config or 'stata_exe' not in config['Programs']:
            print("Stata batch found automatically: "+env['STATABATCHCOM'])
        for section in config.sections():
            print("["+section+"]")
            for key in config[section]:
                print(key + ": " + config[section][key])
        print("\n")

    if not GetOption("clean") and patch_scons_sig_fns:
        if config['SCons']['use_custom_datasignature']!="False": 
            monkey_patch_scons(config['SCons']['use_custom_datasignature'])
        elif not GetOption('silent'):
            print("Using default timestamp-dependent checksums of dataset,")
            print("Edit use_custom_datasignature in config_project.ini to change (Strict, DataOnly, VVLabelsOnly)")

    return(env)
