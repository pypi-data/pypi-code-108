from rypy.ry365 import O365Account
import re

SITE = 'msteams_08dd34'
ACCOUNT = O365Account(site=SITE)
LOCALE = 'jpjn'

PATH = ['WD', 'Skills', 'Language_Folders_2']

folder = ACCOUNT.get_folder(*PATH, LOCALE, site=SITE)

merge_fol = ACCOUNT.get_folder(*PATH, LOCALE, f"{LOCALE}-Merge_Staging")
moved = [item.name[:3] for item in merge_fol.get_items() if item.is_file]
for fol in folder.get_items():
    if fol.is_folder and re.match(r'^\d{3}$', fol.name):
        for item in fol.get_items():
            if fol.name in item.name and fol.name not in moved:
                print(f"Copying {item.name} to Merge_Staging directory...")
                item.copy(merge_fol)
