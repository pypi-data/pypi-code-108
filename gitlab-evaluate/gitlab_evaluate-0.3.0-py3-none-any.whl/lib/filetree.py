import os

def get_subfolders(path):
    sub_paths = []
    file_exists = False
    for item in get_files(path):
        if item != ".git":
            abs_path = f"{path}/{item}"
            if not os.path.isfile(abs_path):
                sub_paths.append(abs_path)
            else:
                file_exists = True
    return sub_paths, file_exists

def get_files(path):
    for dirpath,_,filenames in os.walk(path):
        if '.git' not in dirpath:
            for f in filenames:
                yield os.path.abspath(os.path.join(dirpath, f))

def traverse(root_path, func, *args, **kwargs):
    '''
        Recursive wrapper function to interact with a series of filepaths

        Provide a root path as the starting point,
        a function to interact with each directory level,
        and pass through any parameters 'func' requires
    '''
    sub_paths, _ = get_subfolders(root_path)
    files = get_files(root_path)
    func(files, *args, **kwargs)
    if sub_paths:
        for sub_path in sub_paths:
            traverse(sub_path, func, *args, **kwargs)