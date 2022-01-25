from datetime import datetime
import os
import sys


def check_dep(deps, outfile=sys.stdout, reterr=False):
    """Check dependencies"""
    check_dep_format(deps)
    errdep = check_dep_time(deps, outfile)
    if reterr:
        return errdep
    else:
        return None


def get_mtime(filepath):
    """Get the latest of created time and last modified time"""
    stat = os.stat(filepath)
    return datetime.fromtimestamp(max(stat.st_ctime, stat.st_mtime))


def print_dep(outdep, outfile):
    """Print dependency"""
    # Max path length
    maxlen = max(
        max(len(s) for s in outdep[0].keys()) if len(outdep[0]) > 0 else 0,
        max(len(s) for s in outdep[1].keys()),
        max(len(s) for s in outdep[2].keys()) if len(outdep[0]) > 0 else 0,
    ) + 5
    print(' ' * (maxlen + 4 + 2 + 4) + 'Last Modified Time', file=outfile)
    print('  Input:', file=outfile)
    for k, v in outdep[0].items():
        print(
            f'    {k:{maxlen}s}: {v.strftime("%Y-%m-%d %H:%M:%S.%f")}',
            file=outfile
        )
    print('  Code:', file=outfile)
    for k, v in outdep[1].items():
        print(
            f'    {k:{maxlen}s}: {v.strftime("%Y-%m-%d %H:%M:%S.%f")}',
            file=outfile
        )
    print('  Output:', file=outfile)
    for k, v in outdep[2].items():
        print(
            f'    {k:{maxlen}s}: {v.strftime("%Y-%m-%d %H:%M:%S.%f")}',
            file=outfile
        )


def check_dep_format(deps):
    """Check format of dependencies"""
    assert isinstance(deps, list), f'deps is not a list'
    ndep = len(deps)
    for i in range(ndep):
        # Each tuple must have 3 elements
        assert len(deps[i]) == 3, f'deps[{i}] does not have size 3'
        # Type of each element
        assert isinstance(deps[i][0], list), f'deps[{i}][0] is not a list'
        assert isinstance(deps[i][1], str), f'deps[{i}][1] is not a str'
        assert isinstance(deps[i][2], list), f'deps[{i}][2] is not a list'
        # Existence of each file
        for p in deps[i][0] + [deps[i][1]] + deps[i][2]:
            if not os.path.exists(p):
                raise AssertionError(f'The following file does not exist: {p}')
    return None


def check_dep_time(deps, outfile):
    """Check time of file dependency"""
    ndep = len(deps)
    # Save problematic dependencies
    errdep = []
    for i in range(ndep):
        if len(deps[i][0]) == 0:
            datetime1 = datetime(1900,1,1)
        else:
            datetime1 = max(get_mtime(x) for x in deps[i][0])
        if len(deps[i][2]) == 0:
            datetime3 = datetime(2999,1,1)
        else:
            datetime3 = min(get_mtime(x) for x in deps[i][2])
        if deps[i][1].strip() != '':
            datetime2 = get_mtime(deps[i][1])
            if not (datetime1 <= datetime2 <= datetime3):
                failed = True
            else:
                failed = False
        else:
            if not (datetime1 <= datetime3):
                failed = True
            else:
                failed = False
        if failed:
            errdep.append(
                (
                    {f: get_mtime(f) for f in deps[i][0]},
                    {deps[i][1]: get_mtime(deps[i][1])},
                    {f: get_mtime(f) for f in deps[i][2]},
                )
            )
    # Print
    if len(errdep) > 0:
        print(f'There are {len(errdep)} broken file dependencies!!! ', file=outfile)
        for i, outdep in enumerate(errdep):
            print(f'[{i+1}]', file=outfile)
            print_dep(outdep, outfile=outfile)
            print('', file=outfile)
        return errdep
    else:
        print('All file dependencies are verified!', file=outfile)
        return None


