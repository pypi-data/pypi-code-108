# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
# ! /usr/bin/env python
"""Script to detect YANG model changes between 2 repositories."""
from ysfilemanager import YSYangSet, YSYangDirectoryRepository, merge_user_set
from ysyangtree import YSContext, YSYangModels
from ysyangtree.ymodels import ALL_NODETYPES
from yangsuite import get_logger
log = get_logger(__name__)


class YSYangDatasetException(Exception):
    """Pre-commit exception."""

    pass


def dataset_for_yangset(owner, setname, model, addons=None,
                        reference=None, all_data=False):
    try:
        ys = YSYangSet.load(owner, setname)
    except (OSError, ValueError):
        raise YSYangDatasetException('No such yangset "{0}"'
                                     .format(merge_user_set(owner, setname)))
    except RuntimeError:
        raise YSYangDatasetException('No such user "{0}"'.format(owner))
    return _dataset_for_repo(ys, model, addons,
                             reference=reference,
                             yangset=merge_user_set(owner, setname),
                             all_data=all_data)


def dataset_for_directory(path, model, addons=None, reference=None,
                          all_data=False):
    try:
        repo = YSYangDirectoryRepository(path)
    except OSError:
        raise YSYangDatasetException('Invalid path "{0}"'.format(path))
    return _dataset_for_repo(repo, model, addons, reference=reference,
                             all_data=all_data)


def _dataset_for_repo(repo, model, addons=None, reference=None,
                      yangset=None, all_data=False):
    """Logic shared between dataset_for_yangset and dataset_for_directory."""
    models = YSYangModels.get_instance(reference)
    if ((not models) or
            model not in models.modelnames or
            models.ctx.repository != repo or
            models.ctx.repository.is_stale):
        ctx = YSContext.get_instance(reference, yangset)
        if not ctx:
            ctx = YSContext(repo, reference, [model])
        models = YSYangModels(ctx, [model])
        # We are intentionally not storing it due to memory/performance
        # issue

    if not addons:
        addons_list = []
    else:
        addons_list = list(addons)

    # Add module to addons list
    if 'module' not in addons_list:
        addons_list.insert(0, 'module')

    addons = addons_list

    data = []
    if models.yangs[model]:
        if 'data' in models.yangs[model].tree:
            if 'modtype' in models.yangs[model].tree['data']:
                modtype = models.yangs[model].tree['data']['modtype']
                if modtype == 'submodule':
                    log.warning("%s is a submodule.", model)
                    models = YSYangModels(ctx, [model],
                                          included_nodetypes=ALL_NODETYPES)
                    for m, parser in models.yangs.items():
                        if m == model:
                            data = parser.tw.get_dataset_using_key(
                                parser.tw.tree,
                                'name',
                                [],
                                '',
                                *addons
                            )

        for m, parser in models.yangs.items():
            data += parser.tw.get_dataset(parser.tw.tree, [], *addons)

    if not all_data:
        # Trim down dataset
        to_dataset = []
        for to_data in data:
            if model in to_data:
                to_dataset.append(to_data)
        data = to_dataset

    return {'header': ['xpath'] + list(addons),
            'data': data}
