import os
import sys
from os import walk
from pathlib import Path
from shutil import copyfile


def git_push(dest_path):
    print(f'cd {dest_path} && git pull && git add . && git commit -am"." && git push')
    os.system(f'cd {dest_path} && git pull && git add . && git commit -am"." && git push')


def file_append(size, sized, full_path_source, max_size, files, dir_path_dest, full_path_dest):
    if sized + size > max_size:
        if sized > 0:
            return False, sized
    files.append((full_path_source, dir_path_dest, full_path_dest, size))
    sized += size
    print(f'file append ({round(sized / max_size * 1024, 2)} MB) : {full_path_dest}')
    return True, sized


def do(argv):
    # print(argv)
    # print(os.path.abspath(os.curdir))

    max_size = 1024 * 1024 * 1024
    source_path = argv[1]
    dest_path = argv[2]

    if len(argv) < 2 or not os.path.isdir(source_path):
        raise Exception('The path must contain the source directory')

    if len(argv) < 3 or not os.path.isdir(dest_path):
        raise Exception('The path must contain the destination directory')

    excl = ['.git', '.idea', 'TmpFile1', 'Programs', 'tmp', '.php', 'templates', 'sql-log']

    files = []
    sized = 0
    apend_res = False

    for (dirpath, dirnames, filenames) in walk(source_path):
        for filename in filenames:
            full_path_source = f'{dirpath}{os.sep}{filename}'
            exclude = len(list(filter(lambda x: dirpath.find(x) != -1, excl))) > 0
            if exclude is False:
                exclude = len(list(filter(lambda x: full_path_source.find(x) != -1, excl))) > 0
            if exclude is True:
                continue
            stat_source = Path(full_path_source).stat()

            full_path_dest = full_path_source.replace(source_path, dest_path)
            dir_path_dest = dirpath.replace(source_path, dest_path)
            if not os.path.exists(full_path_dest):
                apend_res, sized = file_append(
                    dir_path_dest=dir_path_dest,
                    files=files,
                    full_path_dest=full_path_dest,
                    full_path_source=full_path_source,
                    max_size=max_size,
                    sized=sized,
                    size=stat_source.st_size,
                )
            else:
                stat_dest = Path(full_path_dest).stat()
                if stat_source.st_size != stat_dest.st_size:
                    apend_res, sized = file_append(
                        dir_path_dest=dir_path_dest,
                        files=files,
                        full_path_dest=full_path_dest,
                        full_path_source=full_path_source,
                        max_size=max_size,
                        sized=sized,
                        size=stat_source.st_size,
                    )
                else:
                    print(f'file ({round(sized / max_size * 1024, 2)} MB) : {full_path_dest} exists.')
                    apend_res = True
            if apend_res is False:
                break
        if apend_res is False:
            break

    i = 0
    for src, dir_dst, dst, size in files:
        if not os.path.exists(dir_dst):
            os.makedirs(dir_dst)

        try:
            copyfile(src, dst)
            print(f'Copied ({i} from {len(files)}) {src} -> {dst}')
            i += 1
            sized += size
        except FileNotFoundError as ex:
            print(ex)

    if sized > 0:
        git_push(dest_path=dest_path)

    return apend_res


if __name__ == '__main__':
    a = False
    while a is False:
        a = do(sys.argv)
    print('Done.')
