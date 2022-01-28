import os
import pwd

def cx_installpath():
    search_pathes = []
    print(os.getenv('HOME'))

    if os.getenv('CXDIR'):
        search_pathes.append(os.getenv('CXDIR') + '/4cx/exports')
        search_pathes.append(os.getenv('CXDIR') + '/exports')

    search_pathes.append(os.getenv('HOME') + '/cx/4cx/exports')

    if os.getenv('USER') == "root":
        search_pathes.append(pwd.getpwnam(os.getenv('USER')).pw_dir + '/4pult')
        search_pathes.append(pwd.getpwnam(os.getenv('USER')).pw_dir + '/cx/4cx/exports')

    try:
        search_pathes.append(pwd.getpwnam('oper').pw_dir + '/4pult')
    except KeyError:
        pass

    try:
        search_pathes.append(pwd.getpwnam('pi').pw_dir + '/4pult')
    except KeyError:
        pass

    # if this subdirs are exist - let's say it' valid cx install place
    subdirs = ['/include', '/lib']
    for basedir in search_pathes:
        count = 0
        for subdir in subdirs:
            if os.path.exists(basedir + subdir):
                count += 1
        if count == len(subdirs):
            return basedir
    return None


if __name__ == '__main__':

    print('using cx install path:', cx_installpath())
