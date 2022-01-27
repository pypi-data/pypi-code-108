#!/bin/env python
"""
  Simple terminal job error summary
"""

import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script
from CTADIRAC.Core.Utilities import tool_box

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
  save_failed = False

  for switch in switches:
    if switch[0].lower() == "owner":
      owner = switch[1]
    elif switch[0].lower() == "jobgroup":
      job_group = switch[1]
    elif switch[0].lower() == "hours":
      n_hours = int(switch[1])
    elif switch[0].lower() == "failed":
      save_failed = int(switch[1])

  # Start doing something
  # import Dirac here after parseCommandLine
  from DIRAC.Interfaces.API.Dirac import Dirac
  dirac = Dirac()

  # do the jobs via the 2 main methods
  jobs_list = tool_box.get_job_list(owner, job_group, n_hours)
  gLogger.notice(
      "%s jobs found for group \"%s\" and owner \"%s\" in the past %s hours\n" %
      (len(jobs_list), job_group, owner, n_hours))

  # get jobs status
  status = dirac.getJobStatus(jobs_list)

  # print out my favourite tables
  SitesDict = {}

  for job in jobs_list:
    #    print job, status['Value'][int(job)]
    site = status['Value'][int(job)]['Site']
  #    site=status['Value'][int(job)]['CE']
    minstatus = status['Value'][int(job)]['MinorStatus']
    majstatus = status['Value'][int(job)]['Status']

    if majstatus not in {'Done', 'Failed'}:
      continue

    if site not in SitesDict.keys():
      if site.find('.') == -1:
        site = '    None'  # note that blank spaces are needed
      SitesDict[site] = {'Total': 0, 'Failed': 0, 'Errors': {}}

    SitesDict[site]['Total'] += 1
    if majstatus == 'Failed':
      SitesDict[site]['Failed'] += 1
      if minstatus not in SitesDict[site]['Errors'].keys():
        SitesDict[site]['Errors'][minstatus] = 0
      SitesDict[site]['Errors'][minstatus] += 1

  gLogger.notice("%20s  Finish  Errors  Rate  Failure reason" % "Site")
  for site, val in sorted(SitesDict.items()):
    errstr = ""
    for error, amount in val['Errors'].items():
      if len(errstr) > 0:
        errstr += "\n\t\t\t\t\t    "
      errstr += "%s (%d)" % (error, amount)

    txt = "%20s%8d%8d%5d%%  %s" % (site, val['Total'], val['Failed'], val['Failed'] * 100 / val['Total'], errstr)
    gLogger.notice(txt)

  # saved information on failed jobs on disk
  if save_failed:
    txt = ''
    for job in jobs_list:
      majstatus = status['Value'][int(job)]['Status']
      if majstatus == "Failed":
        txt += str(dirac.getJobSummary(int(job))) + '\n'
    open('failed.txt', 'w').write(txt)
    gLogger.notice('Saved failed.txt on disk')

  DIRAC.exit()

if __name__ == '__main__':
  main()