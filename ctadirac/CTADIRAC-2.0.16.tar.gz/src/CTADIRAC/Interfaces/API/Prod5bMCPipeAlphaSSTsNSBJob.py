"""
  New job class to run Prod5b full moon SST only simulations
  Only Paranal in the Alpha layout is supported, using zstd compression
  for simtel output files
          OG, January 2022
"""

__RCSID__ = "$Id$"

# generic imports
import json
import collections
# DIRAC imports
import DIRAC
from CTADIRAC.Interfaces.API.Prod5MCPipeNSBJob import Prod5MCPipeNSBJob


class Prod5bMCPipeAlphaSSTsNSBJob(Prod5MCPipeNSBJob):
  """ Job extension class for Prod5 MC full moon NSB SST only simulations,
  takes care of running corsika piped into simtel
  3 output files are created for Dark, Half Moon and Full Moon NSB
  """

  def __init__(self, cpu_time=259200):
    """ Constructor takes almosst everything from base class

    Keyword arguments:
    cpuTime -- max cpu time allowed for the job
    """
    Prod5MCPipeNSBJob.__init__(self, cpu_time)
    self.setCPUTime(cpu_time)
    self.setName('Prod5bMC_Generation')
    self.version = '2020-06-29b'
    self.compiler = 'gcc83_matchcpu'
    self.configuration_id = 8
    self.n_shower = 100
    self.output_pattern = './Data/*.simtel.zst'
    self.base_path = '/vo.cta.in2p3.fr/MC/PROD5b/'
    self.catalogs = json.dumps(['DIRACFileCatalog', 'TSCatalog'])
    self.n_output_files = 1  # Run only fullmoon NSB (comment lines in multi file)
    self.metadata = collections.OrderedDict()

  def set_site(self, site):
    """ Set the site to simulate

    Parameters:
    site -- a string for the site name (LaPalma)
    """
    if site in ['Paranal']:
      DIRAC.gLogger.info('Set Corsika site to: %s' % site)
      self.cta_site = site
      self.output_pattern = 'Data/*.zst'
    else:
      DIRAC.gLogger.error('Site must be Paranal')
      DIRAC.exit(-1)

  def set_meta_data(self):
    """ define the common meta data of the application
    """
    # The order of the metadata dictionary is important,
    # since it's used to build the directory structure
    self.metadata['array_layout'] = 'Alpha'
    self.metadata['site'] = self.cta_site
    self.metadata['particle'] = self.particle
    # for air shower simulation means North=0 and South=180
    # but here piped into tel_sim so North=180 and South=0
    if self.pointing_dir == 'North':
      self.metadata['phiP'] = 180
    if self.pointing_dir == 'South':
      self.metadata['phiP'] = 0
    self.metadata['thetaP'] = float(self.zenith_angle)
    # hard coded, not ideal... but not sure how to do better
    # self.metadata['airshower_sim_prog'] = 'corsika'
    # self.metadata['airshower_sim_prog_version'] = self.version
    # back to common write up from class
    self.metadata[self.program_category + '_prog'] = self.prog_name
    self.metadata[self.program_category + '_prog_version'] = self.version
    self.metadata['data_level'] = self.output_data_level
    self.metadata['configuration_id'] = self.configuration_id
    # self.metadata['sct'] = False

  def setupWorkflow(self, debug=False):
    """ Override the base class job workflow to adapt to NSB test simulations
        All parameters shall have been defined before that method is called.
    """
    # step 1 - debug only
    i_step = 1
    if debug:
      ls_step = self.setExecutable('/bin/ls -alhtr', logFile='LS_Init_Log.txt')
      ls_step['Value']['name'] = 'Step%i_LS_Init' % i_step
      ls_step['Value']['descr_short'] = 'list files in working directory'
      i_step += 1

      env_step = self.setExecutable('/bin/env', logFile='Env_Log.txt')
      env_step['Value']['name'] = 'Step%i_Env' % i_step
      env_step['Value']['descr_short'] = 'Dump environment'
      i_step += 1

    # step 2
    sw_step = self.setExecutable('cta-prod-setup-software',
                                 arguments='-p %s -v %s -a simulations -g %s' %
                                 (self.package, self.version, self.compiler),
                                 logFile='SetupSoftware_Log.txt')
    sw_step['Value']['name'] = 'Step%i_SetupSoftware' % i_step
    sw_step['Value']['descr_short'] = 'Setup software'
    i_step += 1

    # step 3 runnin
    prod_script = './dirac_prod5_alpha_run'
    if 'gcc10' in self.compiler:
      prod_exe = './dirac_singularity_run'
      prod_args = '%s --start_run %s --run %s %s %s %s %s' % \
                  (prod_script, self.start_run_number, self.run_number,
                   self.cta_site, self.particle, self.pointing_dir,
                   self.zenith_angle)
    else:
      prod_exe = prod_script
      prod_args = '--only-ssts --start_run %s --run %s %s %s %s %s' % \
                  (self.start_run_number, self.run_number,
                   self.cta_site, self.particle, self.pointing_dir,
                   self.zenith_angle)

    cs_step = self.setExecutable(prod_exe, arguments=prod_args,
                                 logFile='CorsikaSimtel_Log.txt')
    cs_step['Value']['name'] = 'Step%i_CorsikaSimtel' % i_step
    cs_step['Value']['descr_short'] = 'Run Corsika piped into simtel'
    i_step += 1

    # step 4a verify Corsika log file
    cl_step = self.setExecutable('cta-prod-verifysteps', arguments='corsika',
                                 logFile='Verify_Corsika_Log.txt')
    cl_step['Value']['name'] = 'Step%i_VerifyCorsikaLog' % i_step
    cl_step['Value']['descr_short'] = 'Verify Corsika log file'
    i_step += 1

    # step 4 verify simtel data
    mgv_step = self.setExecutable('cta-prod-verifysteps',
                                  arguments="generic %0d %0d '%s'" %
                                  (self.n_output_files, self.output_file_size, self.output_pattern),
                                  logFile='Verify_Simtel_Log.txt')
    mgv_step['Value']['name'] = 'Step%i_VerifySimtel' % i_step
    mgv_step['Value']['descr_short'] = 'Verify simtel files'
    i_step += 1

    # step 5 - debug only
    if debug:
      ls_step = self.setExecutable('/bin/ls -Ralhtr', logFile='LS_End_Log.txt')
      ls_step['Value']['name'] = 'Step%i_LS_End' % i_step
      ls_step['Value']['descr_short'] = 'list files in working directory and sub-directory'
      i_step += 1

    # step 6 - define meta data, upload file on SE and register in catalogs
    self.set_meta_data()
    md_json = json.dumps(self.metadata)

    meta_data_field = {'array_layout': 'VARCHAR(128)', 'site': 'VARCHAR(128)',
                       'particle': 'VARCHAR(128)',
                       'phiP': 'float', 'thetaP': 'float',
                       self.program_category + '_prog': 'VARCHAR(128)',
                       self.program_category + '_prog_version': 'VARCHAR(128)',
                       'data_level': 'int', 'configuration_id': 'int', 'merged': 'int'}
    md_field_json = json.dumps(meta_data_field)

    # Upload and register data - NSB=1 dark
    file_meta_data = {'runNumber': self.run_number, 'nsb': 1}
    file_md_json = json.dumps(file_meta_data)
    data_output_pattern = 'Data/*dark*.simtel.zst'

    dm_step = self.setExecutable('cta-prod-managedata',
                                 arguments="'%s' '%s' '%s' %s '%s' %s %s '%s' Data" %
                                 (md_json, md_field_json, file_md_json,
                                  self.base_path, data_output_pattern, self.package,
                                  self.program_category, self.catalogs),
                                 logFile='DataManagement_dark_Log.txt')
    dm_step['Value']['name'] = 'Step%s_DataManagement' % i_step
    dm_step['Value']['descr_short'] = 'Save data files to SE and register them in DFC'
    i_step += 1

    # Upload and register log and histo file - NSB=1
    file_meta_data = {}
    file_md_json = json.dumps(file_meta_data)
    log_file_pattern = 'Data/*dark*.log_hist.tar'
    log_step = self.setExecutable('cta-prod-managedata',
                                  arguments="'%s' '%s' '%s' %s '%s' %s %s '%s' Log" %
                                  (md_json, md_field_json, file_md_json,
                                   self.base_path, log_file_pattern, self.package,
                                   self.program_category, self.catalogs),
                                  logFile='LogManagement_dark_Log.txt')
    log_step['Value']['name'] = 'Step%s_LogManagement' % i_step
    log_step['Value']['descr_short'] = 'Save log to SE and register them in DFC'
    i_step += 1

    # Now switching to half moon NSB
    # Upload and register data - NSB=5 half moon
    file_meta_data = {'runNumber': self.run_number, 'nsb': 5}
    file_md_json = json.dumps(file_meta_data)
    data_output_pattern = 'Data/*-moon*.simtel.zst'

    dm_step = self.setExecutable('cta-prod-managedata',
                                 arguments="'%s' '%s' '%s' %s '%s' %s %s '%s' Data" %
                                 (md_json, md_field_json, file_md_json,
                                  self.base_path, data_output_pattern, self.package,
                                  self.program_category, self.catalogs),
                                 logFile='DataManagement_moon_Log.txt')
    dm_step['Value']['name'] = 'Step%s_DataManagement' % i_step
    dm_step['Value']['descr_short'] = 'Save data files to SE and register them in DFC'
    i_step += 1

    # Upload and register log file - NSB=5
    file_meta_data = {}
    file_md_json = json.dumps(file_meta_data)
    log_file_pattern = 'Data/*-moon*.log_hist.tar'
    log_step = self.setExecutable('cta-prod-managedata',
                                  arguments="'%s' '%s' '%s' %s '%s' %s %s '%s' Log" %
                                  (md_json, md_field_json, file_md_json,
                                   self.base_path, log_file_pattern, self.package,
                                   self.program_category, self.catalogs),
                                  logFile='LogManagement_moon_Log.txt')
    log_step['Value']['name'] = 'Step%s_LogManagement' % i_step
    log_step['Value']['descr_short'] = 'Save log to SE and register them in DFC'
    i_step += 1

    # Now switching to full moon NSB
    # Upload and register data - NSB=19 full moon
    file_meta_data = {'runNumber': self.run_number, 'nsb': 19}
    file_md_json = json.dumps(file_meta_data)
    data_output_pattern = 'Data/*-fullmoon*.simtel.zst'

    dm_step = self.setExecutable('cta-prod-managedata',
                                 arguments="'%s' '%s' '%s' %s '%s' %s %s '%s' Data" %
                                 (md_json, md_field_json, file_md_json,
                                  self.base_path, data_output_pattern, self.package,
                                  self.program_category, self.catalogs),
                                 logFile='DataManagement_fullmoon_Log.txt')
    dm_step['Value']['name'] = 'Step%s_DataManagement' % i_step
    dm_step['Value']['descr_short'] = 'Save data files to SE and register them in DFC'
    i_step += 1

    # Upload and register log file - NSB=19
    file_meta_data = {}
    file_md_json = json.dumps(file_meta_data)
    log_file_pattern = 'Data/*-fullmoon*.log_hist.tar'
    log_step = self.setExecutable('cta-prod-managedata',
                                  arguments="'%s' '%s' '%s' %s '%s' %s %s '%s' Log" %
                                  (md_json, md_field_json, file_md_json,
                                   self.base_path, log_file_pattern, self.package,
                                   self.program_category, self.catalogs),
                                  logFile='LogManagement_fullmoon_Log.txt')
    log_step['Value']['name'] = 'Step%s_LogManagement' % i_step
    log_step['Value']['descr_short'] = 'Save log to SE and register them in DFC'
    i_step += 1

    # Step 6 - debug only
    if debug:
      ls_step = self.setExecutable('/bin/ls -Ralhtr', logFile='LS_End_Log.txt')
      ls_step['Value']['name'] = 'Step%s_LSHOME_End' % i_step
      ls_step['Value']['descr_short'] = 'list files in Home directory'
      i_step += 1

    # Number of showers is passed via an environment variable
    self.setExecutionEnv({'NSHOW': '%s' % self.n_shower})
