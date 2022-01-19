import subprocess
import sys
import argparse
import time
from datetime import datetime

class Chart(object):
    def __setattr__(self, name, value):
        if name == 'status':
            value = value.casefold()
        if 'update_available' in name:
            value = True if value.casefold() == "true" else False
        super(Chart, self).__setattr__(name, value)

    def new_attr(self, attr):
        setattr(self, attr, attr)

INSTALLED_CHARTS = []

def parse_headers(charts: str):
    for line in charts.split("\n"):
        if line.startswith("+-"):
            continue
        if "name" in line.casefold():
            return [col.strip() for col in line.casefold().strip().split("|") if col and col != ""]

def parse_charts(charts: str):
    headers = parse_headers(charts)
    table_data = charts.split("\n")[3:-2:]  # Skip the header part of the table
    for row in table_data:
        row = [section.strip() for section in row.split("|") if section and section != ""]
        chart = Chart()
        for item in zip(headers, row):
            setattr(chart, item[0], item[1])
        INSTALLED_CHARTS.append(chart)

def check_semver(current: str, latest: str):
    split_current_semver = current.split(".", 3)
    split_latest_semver = latest.split(".", 3)
    if split_current_semver[0] != split_latest_semver[0]:
      type="major"
      if VERSIONING == "major":
        return True
    if split_current_semver[1] != split_latest_semver[1]:
      type="minor"
      if VERSIONING != "patch":
        return True
    if split_current_semver[2] != split_latest_semver[2]:
      type="patch"
      return True
    return False
    

def execute_upgrades():
    if UPDATE:
      if ALL:
        if CATALOG == "ALL":
          filtered = filter(lambda a: a.update_available and a.status == "active", INSTALLED_CHARTS)
        else:
          filtered = filter(lambda a: a.update_available and a.status == "active" and a.catalog == CATALOG, INSTALLED_CHARTS)
      else:
        if CATALOG == "ALL":
          filtered = filter(lambda a: a.update_available, INSTALLED_CHARTS)
        else:
          filtered = filter(lambda a: a.update_available and a.catalog == CATALOG, INSTALLED_CHARTS)
      for chart in filtered:
        pre_update_ver = chart.human_version
        post_update_ver = chart.human_latest_version
        split_current_version = chart.human_version.split("_", 1)
        current_version = split_current_version[1]
        split_latest = chart.human_latest_version.split("_", 1)
        latest_version = split_latest[1]
        if check_semver(current_version, latest_version):
          print(f"Updating {chart.name}... \n")
          pre_update_ver = chart.human_version
          result = subprocess.run(['cli', '-c', f'app chart_release upgrade release_name="{chart.name}"'], capture_output=True)
          post_update_ver = chart.human_latest_version
          if "Upgrade complete" not in result.stdout.decode('utf-8'):
              print(f"{chart.name} failed to upgrade. \n{result.stdout.decode('utf-8')}")
          else:
              print(f"{chart.name} upgraded ({pre_update_ver} --> {post_update_ver})")
    else:
      print("Update disabled, skipping...")

def fetch_charts():
  rawcharts = subprocess.run(["cli", "-c", "app chart_release query"], stdout=subprocess.PIPE)
  charts = rawcharts.stdout.decode('utf-8')
  return(charts)
  
def process_args():
    global CATALOG
    global VERSIONING
    global SYNC
    global PRUNE
    global ALL
    global BACKUP
    global UPDATE
    global RESTORE
    global LIST
    parser = argparse.ArgumentParser(description='Update TrueNAS SCALE Apps')
    parser.add_argument('-c', '--catalog', nargs='?', default='ALL', help='name of the catalog you want to process in caps. Or "ALL" to render all catalogs.')
    parser.add_argument('-v', '--versioning', nargs='?', default='minor', help='Name of the versioning scheme you want to update. Options: major, minor or patch. Defaults to minor')
    parser.add_argument('-s', '--sync', action="store_true", help='sync catalogs before trying to update')
    parser.add_argument('-u', '--update', action="store_true", help='update the Apps in the selected catalog')
    parser.add_argument('-p', '--prune', action="store_true", help='prune old docker images after update')
    parser.add_argument('-a', '--all', action="store_true", help='update "active" apps only and ignore "stopped" or "stuck" apps')
    parser.add_argument('-b', '--backup', action="store_true", help='backup the complete Apps system prior to updates')
    parser.add_argument('-r', '--restore', nargs='?', help='restore a previous backup, disables all other features')
    parser.add_argument('-l', '--list', action="store_true", help='lists existing backups')
    args = parser.parse_args()
    CATALOG = args.catalog
    VERSIONING = args.versioning
    RESTORE = args.restore
    if args.update:
      UPDATE = True
    else:
      UPDATE = False
    if args.sync:
      SYNC = True
    else:
      SYNC = False
    if args.prune:
      PRUNE = True
    else:
      PRUNE = False
    if args.all:
      ALL = True
    else:
      ALL = False
    if args.backup:
      BACKUP = True
    else:
      BACKUP = False
    if args.list:
      LIST = True
    else:
      LIST = False

    
def sync_catalog():
    if SYNC:
      print("Syncing Catalogs...\n")
      process = subprocess.Popen(["cli", "-c", "app catalog sync_all"], stdout=subprocess.PIPE)
      while process.poll() is None:
          lines = process.stdout.readline()
          print (lines.decode('utf-8'))
      temp = process.stdout.read()
      if temp:
        print (temp.decode('utf-8'))
    else:
      print("Catalog Sync disabled, skipping...")
  
def docker_prune():
    if PRUNE:
      print("Pruning old docker images...\n")
      process = subprocess.Popen(["docker", "image", "prune", "-af"], stdout=subprocess.PIPE)
      print("Images pruned.\n")
    else:
      print("Container Image Pruning disabled, skipping...")
      
def apps_backup():
    if BACKUP:
      print("Running App Backup...\n")
      now = datetime.now()
      command = "app kubernetes backup_chart_releases backup_name=TrueTool_"+now.strftime("%Y_%d_%m_%H_%M_%S")
      process = subprocess.Popen(["cli", "-c", command], stdout=subprocess.PIPE)
      while process.poll() is None:
          lines = process.stdout.readline()
          print (lines.decode('utf-8'))
      temp = process.stdout.read()
      if temp:
        print (temp.decode('utf-8'))
    else:
      print("Backup disabled, skipping...")
      
def backups_list():
    if LIST:
      print("Running App Backup...\n")
      process = subprocess.Popen(["cli", "-c", "app kubernetes list_backups"], stdout=subprocess.PIPE)
      while process.poll() is None:
          lines = process.stdout.readline()
          print (lines.decode('utf-8'))
      temp = process.stdout.read()
      if temp:
        print (temp.decode('utf-8'))
      
def apps_restore():
    print("Running Backup Restore...\n")
    command = "app kubernetes restore_backup backup_name="+RESTORE
    print(f"{command}")
    process = subprocess.Popen(["cli", "-c", command], stdout=subprocess.PIPE)
    while process.poll() is None:
        lines = process.stdout.readline()
        print (lines.decode('utf-8'))
    temp = process.stdout.read()
    if temp:
      print (temp.decode('utf-8'))

  
def run():
    process_args()
    print("Starting TrueCharts TrueTool...\n")
    if RESTORE:
      apps_restore()
    elif LIST:
      backups_list()
    else:
      apps_backup()
      sync_catalog()
      charts = fetch_charts()
      parse_charts(charts)
      print("Executing Updates...\n")
      execute_upgrades()
      docker_prune()
      print("TrueTool Finished\n")
      exit(0)


if __name__ == '__main__':
    run()

