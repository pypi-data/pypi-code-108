from ry365 import O365Account



LOCALES = {
    'CAES': '50k',
    'DEAT': '25k',
    'ENZA': '25k',
    'HIIN': '50k',
    'PTBR': '25k',
    'PTPT': '50k',
    'ZHCN': '50k',
    'ZHHK': '50k'
}

DOMAINS = [
    # 'HC',
    # 'IN',
    'AL',
    'FF',
    'RE',
    'TR'
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


def get_moved(locale: str, domain: str):
    PATH = [
        'Lex Official Production',
        locale,
        'Full_Production',
        f"{locale}-{domain}",
        f"{locale}-{domain}-Merge_Staging"
    ]
    not_moved = 0
    moved = 0
    try:
        fol = ACCOUNT.get_folder(*PATH, site=SITE)
        for item in fol.get_items():
            if not item.is_folder:
                not_moved += 1
            if item.is_folder and 'moved' in item.name.lower():
                for moved_item in item.get_items():
                    if not moved_item.is_folder:
                        moved += 1
        return moved, not_moved
    except TypeError:
        return moved, not_moved


def get_raw_total(locale: str, domain: str):
    PATH = [
        'Lex Official Production',
        locale,
        'Full_Production',
        f"{locale}-{domain}",
        f"{locale}-{domain}-Raw_Input"
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


def main(locale: str, domain: str):
    moved, not_moved = get_moved(locale, domain)
    total = moved + not_moved
    raw_total = get_raw_total(locale, domain)
    percent = f"{(total/raw_total)*100:.1f}" if raw_total != 0 else 0
    return f"{locale}-{domain} ({percent}%): TFIDF ({tfidf_ready(locale, total)}); Code_Switching ({cs_ready(locale, total)})"


if __name__ == '__main__':
    for LOCALE in LOCALES:
        for DOMAIN in DOMAINS:
            print(main(LOCALE, DOMAIN))