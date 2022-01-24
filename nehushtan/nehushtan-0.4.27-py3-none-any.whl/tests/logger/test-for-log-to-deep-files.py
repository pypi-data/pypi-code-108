from nehushtan.logger.NehushtanFileLogger import NehushtanFileLogger

if __name__ == '__main__':
    log_dir = '/Users/leqee/code/nehushtan/log/x'
    cases = [
        'a',
        'a/b',
        'a/b/c',
        '/a',
        '/a/',
        '/a/b',
        '/a/b/',
        'a/',
        'a/b/',
    ]
    for case in cases:
        NehushtanFileLogger(case, log_dir).info(case)
