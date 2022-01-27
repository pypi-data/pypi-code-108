#!/usr/bin/env python
"""
  Simple terminal job monitoring
"""
__RCSID__ = "$Id$"

from DIRAC import gLogger
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script
from CTADIRAC.Core.Utilities import tool_box
from CTADIRAC.Core.Utilities.tool_box import highlight

@Script()
def main():
  ''' Select jobs based on conditions
  '''
  Script.registerSwitch("", "owner=", "the job owner")
  Script.registerSwitch("", "jobGroup=", "the job group")
  Script.registerSwitch("", "hours=", "Get status for jobs of the last n hours")
  Script.registerSwitch("", "failed=", "1 or 0 : Save or not failed jobs in \"failed.txt\"")
  switches, argss = Script.parseCommandLine(ignoreErrors=True)
  # defaults
  owner = "arrabito"
  job_group = ""
  n_hours = 24

  for switch in switches:
    if switch[0].lower() == "owner":
      owner = switch[1]
    elif switch[0].lower() == "jobgroup":
      job_group = switch[1]
    elif switch[0].lower() == "hours":
      n_hours = int(switch[1])

  # do the jobs via the 2 main methods
  jobs_list = tool_box.get_job_list(owner, job_group, n_hours)
  gLogger.notice(
      "%s jobs found for group \"%s\" and owner \"%s\" in the past %s hours\n" %
      (len(jobs_list), job_group, owner, n_hours))

  # get status dictionary
  status_dict, sites_dict = tool_box.parse_jobs_list(jobs_list)

  # print out my favourite tables
  gLogger.notice(
      "%16s\tWaiting\tRunning\tFailed\tStalled\tDone\tTotal" %
      "Site")
  for key, val in sites_dict.items():
    txt = "%16s\t%s\t%s\t%s\t%s\t%s\t%s" %\
        (key.split('LCG.')[-1], val['Waiting'], val['Running'], val['Failed'],
         val['Stalled'], val['Done'], val['Total'])
    if float(val['Done']) > 0.:
      # More than 10% crash, print bold red
      if float(val['Failed']) / float(val['Done']) > 0.1:
        txt = highlight(txt)
    gLogger.notice(txt)

  gLogger.notice("%16s\t%s\t%s\t%s\t%s\t%s\t%s" %
                        ('Total', status_dict['Waiting'], status_dict['Running'],
                         status_dict['Failed'], status_dict['Stalled'],
                         status_dict['Done'], status_dict['Total']))

if __name__ == '__main__':
  main()