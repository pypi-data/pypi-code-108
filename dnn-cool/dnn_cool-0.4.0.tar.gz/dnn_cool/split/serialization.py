import numpy as np

from dnn_cool.utils.base import train_test_val_split


def split_already_done(n: int, project_dir):
    total_len = 0
    for i, split_name in enumerate(['train', 'test', 'val']):
        split_path = project_dir / f'{split_name}_indices.npy'
        if not split_path.exists():
            return False
        total_len += len(np.load(split_path))

    return total_len == n


def read_split(runner_dir):
    res = []
    for i, split_name in enumerate(['train', 'test', 'val']):
        split_path = runner_dir / f'{split_name}_indices.npy'
        res.append(np.load(split_path))
    return res


def save_split(project_dir, res):
    for i, split_name in enumerate(['train', 'test', 'val']):
        split_path = project_dir / f'{split_name}_indices.npy'
        np.save(split_path, res[i])


def runner_split(n: int, runner_dir):
    if split_already_done(n, runner_dir):
        return read_split(runner_dir)
    res = train_test_val_split(n)
    save_split(runner_dir, res)
    return res
