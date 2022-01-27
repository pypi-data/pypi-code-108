import os.path
from chardet.universaldetector import UniversalDetector


def guess_file_encoding(path, max_line=1000):
    if not os.path.isfile(path):
        raise ValueError(f'guess_file_encoding: {path} is not a file')
    detector = UniversalDetector()
    detector.reset()
    with open(path, "rb") as f:
        for i, line in enumerate(f):
            detector.feed(line)
            if detector.done:
                break
            if i!=0 and i%max_line == 0:
                break
    detector.close()
    return detector.result['encoding']


