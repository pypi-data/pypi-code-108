from os import listdir

from mmap_ninja import numpy


def load_inference_results_from_directory(logdir):
    out_dir = logdir / 'infer'
    out_dir.mkdir(exist_ok=True)
    res = {}
    for key in ['logits', 'targets', 'interpretations']:
        res[key] = {}
        for loader_name in ['infer', 'valid', 'test']:
            res[key][loader_name] = {}
            for filename in listdir(out_dir / loader_name / key):
                full_path = out_dir / loader_name / key / filename
                task_name = filename
                res[key][loader_name][task_name] = numpy.open_existing(full_path)
                if key == 'logits' and not task_name.startswith('indices|'):
                    indices_path = out_dir / loader_name / 'indices' / filename
                    res[key][loader_name][f'indices|{task_name}'] = numpy.open_existing(indices_path)
    return res
