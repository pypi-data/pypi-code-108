import logging as log


def check_xnat_item(x, a):
    experiments = x.array.experiments()
    projects = [e['project'] for e in experiments]
    experiments = [e['ID'] for e in x.array.experiments()]

    result = -1
    if a in projects:
        log.info('Project detected: %s' % a)
        result = 0
    elif a in experiments:
        log.info('Experiment detected: %s' % a)
        result = 1
    else:
        from bx import lists
        if hasattr(lists, a):
            print('List detected: %s' % a)
            result = 2

    return result


def collect_experiments(x, id, columns=['label', 'subject_label'], max_rows=1):
    import os
    t = check_xnat_item(x, id)

    if not os.environ.get('CI_TEST', None):
        max_rows = None

    experiments = []
    if t == 0:
        experiments = x.array.experiments(project_id=id,
                                          columns=columns).data[:max_rows]
    elif t == 1:
        experiments = [x.array.experiments(experiment_id=id,
                                           columns=columns).data[0]]
    elif t == 2:
        from bx import lists
        expes = getattr(lists, id)
        for e in expes[:max_rows]:
            ex = x.array.experiments(experiment_id=e,
                                     columns=columns).data[0]
            experiments.append(ex)
    else:
        msg = '%s is not a project or an experiment nor a list' % id
        raise ValueError(msg)

    return experiments
