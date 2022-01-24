import glob
import math
import os
import shutil


def backup(filename: str, num_to_keep: int = 5) -> bool:
    if not os.path.exists(filename):
        return False
    digits = math.ceil(math.log10(num_to_keep)) or 1
    mask = filename + '.' + "[0-9]" * digits
    candidates = sorted(glob.glob(mask))
    numbers = [int(os.path.splitext(item)[1][1:]) for item in candidates]
    jobs = list(zip(numbers, numbers[1:]))
    if not all(map(lambda x: x[1] - x[0] == 1, jobs)):
        new_jobs = []
        for src, dest in jobs:
            if dest - src > 1:
                new_jobs.append((src, src + 1))
                break
            else:
                new_jobs.append((src, dest))
        jobs = new_jobs

    if not jobs:
        if numbers and numbers[0] == 0:
            jobs = [(0, 1), ]
    elif jobs[0][0] != 0:
        jobs = []
    elif len(jobs) < num_to_keep - 1:
        num = jobs[-1][1]
        if os.path.exists(f"{filename}.{num:0{digits}d}"):
            jobs.append((num, num + 1))
    for src, dest in list(reversed(list(jobs)))[:num_to_keep]:
        shutil.move(f"{filename}.{src:0{digits}d}",
                    f"{filename}.{dest:0{digits}d}")
    shutil.copy(filename, f"{filename}." + '0' * digits)
    return True
