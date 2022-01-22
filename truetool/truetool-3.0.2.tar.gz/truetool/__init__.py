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
          filtered = filter(lambda a: a.update_available, INSTALLED_CHARTS)
        else:
          filtered = filter(lambda a: a.update_available and a.catalog == CATALOG, INSTALLED_CHARTS)
      else:
        if CATALOG == "ALL":
          filtered = filter(lambda a: a.update_available and a.status == "active", INSTALLED_CHARTS)
        else:
          filtered = filter(lambda a: a.update_available and a.status == "active" and a.catalog == CATALOG, INSTALLED_CHARTS)
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
    global DELETE
    parser = argparse.ArgumentParser(description='TrueCharts CLI Tool. Warning: please do NOT combine short arguments like -ubs always use -u -b -s etc.')
    parser.add_argument('-c', '--catalog', nargs='?', default='ALL', help='name of the catalog you want to process in caps. Or "ALL" to render all catalogs.')
    parser.add_argument('-v', '--versioning', nargs='?', default='minor', help='Name of the versioning scheme you want to update. Options: major, minor or patch. Defaults to minor')
    parser.add_argument('-b', '--backup', nargs='?', const='14', help='backup the complete Apps system prior to updates, add a number to specify the max old backups to keep')
    parser.add_argument('-r', '--restore', nargs='?', help='restore a previous backup, disables all other features')
    parser.add_argument('-d', '--delete', nargs='?', help='delete a specific backup')
    parser.add_argument('-s', '--sync', action="store_true", help='sync catalogs before trying to update')
    parser.add_argument('-u', '--update', action="store_true", help='update the Apps in the selected catalog')
    parser.add_argument('-p', '--prune', action="store_true", help='prune old docker images after update')
    parser.add_argument('-a', '--all', action="store_true", help='update all apps for said catalog, including "stopped" or "stuck" apps')
    parser.add_argument('-l', '--list', action="store_true", help='lists existing backups')
    args = parser.parse_args()
    CATALOG = args.catalog
    VERSIONING = args.versioning
    RESTORE = args.restore
    BACKUP = args.backup
    DELETE = args.delete
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
      process = subprocess.run(["docker", "image", "prune", "-af"], stdout=subprocess.PIPE)
      print("Images pruned.\n")
    else:
      print("Container Image Pruning disabled, skipping...")
      
def apps_backup():
    if BACKUP:
      print(f"Cleaning old backups to a max. of {BACKUP}...\n")
      backups_fetch = get_backups_names()
      backups_cleaned = [k for k in backups_fetch if 'TrueTool' in k]
      backups_remove = backups_cleaned[:len(backups_cleaned)-int(BACKUP)]
      for backup in backups_remove:
        backups_delete(backup)

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
      print("Generating Backup list...\n")
      backups = get_backups_names()
      for backup in backups:
        print(f"{backup}")
        
def backups_delete(backup: str):
    print(f"removing {backup}...")
    process = subprocess.run(["midclt", "call", "kubernetes.delete_backup", backup], stdout=subprocess.PIPE)
      
def get_backups_names():
      names = []
      process = subprocess.run(["cli", "-c", "app kubernetes list_backups"], stdout=subprocess.PIPE)
      output = process.stdout.decode('utf-8')
      for line in output.split("\n"):
        if line.startswith("+-"):
            continue
        else:
            rowlist = [col.strip() for col in line.strip().split("|") if col and col != ""]
            if rowlist:
              names.append(rowlist[0])
      names.sort()
      return names
      
def apps_restore():
    print("Running Backup Restore...\n")
    process = subprocess.run(["midclt", "call", "kubernetes.restore_backup", RESTORE], stdout=subprocess.PIPE)
    time.sleep(5)
    print("Restoration started, please check the restoration process in the TrueNAS SCALE Web GUI...\n")
    print("Please remember: This can take a LONG time.\n")
  
def run():
    process_args()
    print("Starting TrueCharts TrueTool...\n")
    if RESTORE:
      apps_restore()
    elif LIST:
      backups_list()
    elif DELETE:
      backups_delete(DELETE)
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

