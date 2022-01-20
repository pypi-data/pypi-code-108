from ry365 import O365Account



LOCALES = [
    'zhCN',
    'ptbr',
    'nlnl',
    'kokr',
    'jpjp',
    'frfr',
    'frca',
    'es419',
    'dede'
]

DIVISIONS = [
    'Assistant',
    'Skills'
]



SITE = 'msteams_08dd34'
ACCOUNT = O365Account(site=SITE)

def tfidf_ready(locale: str, file_count: int):
    CONVERTER = {
        '25k': 16750,
        '50k': 33500
    }
    THOLD = CONVERTER[LOCALES[locale]]
    COUNT = file_count * 70
    if COUNT > THOLD:
        return 'READY'
    if COUNT + 1260 > THOLD:
        return 'READY with pilot files'
    return f"{((THOLD - COUNT - 1260) // 70) + 1} Files Needed"


def cs_ready(locale: str, file_count: int):
    CONVERTER = {
        '25k': 25000,
        '50k': 50000
    }
    THOLD = CONVERTER[LOCALES[locale]]
    COUNT = file_count * 70
    if COUNT > THOLD:
        return 'READY'
    if COUNT + 1260 > THOLD:
        return 'READY with pilot files'
    return f"{((THOLD - COUNT - 1260) // 70) + 1} Files Needed"


def get_moved(locale: str, division: str):
    PATH = [
        'WD',
        f"{division}",
        'Language_Folders_2',
        locale,
        f"{locale}-Merge_Staging"
    ]
    not_moved = 0
    moved = 0
    try:
        fol = ACCOUNT.get_folder(*PATH, site=SITE)
        for item in fol.get_items():
            if not item.is_folder:
                not_moved += 1
            if item.is_folder and item.name.lower() in ['moved', 'moved-2']:
                for moved_item in item.get_items():
                    if not moved_item.is_folder:
                        moved += 1
        return moved, not_moved
    except TypeError:
        return moved, not_moved


def get_raw_total(locale: str, division: str):
    PATH = [
        'WD',
        f"{division}",
        'Language_Folders_2',
        locale,
        f"{locale}-Raw_input"
    ]
    total = 0
    try:
        fol = ACCOUNT.get_folder(*PATH, site=SITE)
        for item in fol.get_items():
            if not item.is_folder:
                total += 1
        return total
    except TypeError:
        return total


def main(locale: str, division: str):
    moved, not_moved = get_moved(locale, division)
    total = moved + not_moved
    raw_total = get_raw_total(locale, division)
    percent = f"{(total/raw_total)*100:.1f}" if raw_total != 0 else 0
    return f"{locale} {division} ({percent}%): {total} files completed"

