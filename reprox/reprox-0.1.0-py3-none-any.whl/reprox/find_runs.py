import typing as ty
import os
import numpy as np
import pandas as pd
import strax
import utilix
from reprox import core


def find_data(
        targets: ty.Union[str, list, tuple],
        exclude_from_invalid_cmt_version: ty.Union[bool, str] = (
                core.config['context']['cmt_version']),
        context_kwargs: ty.Optional[dict] = None,
        keep_detectors: ty.Union[str, tuple, list] = ('tpc',),
) -> None:
    """
    Determine which data to process, see determine_data_to_reprocess
    :param targets: List of targets to process
    :param exclude_from_invalid_cmt_version: A CMT version (optional) to
        exclude runs that lie outside it's validity from
    :param context_kwargs: Any context kwargs
    :return:
    """
    if context_kwargs is None:
        context_kwargs = {}
    st = core.get_context(**context_kwargs)
    runs = determine_data_to_reprocess(
        st=st,
        targets=targets,
        exclude_from_invalid_cmt=exclude_from_invalid_cmt_version,
        keep_detectors=keep_detectors,
    )
    save_as = core.runs_csv
    if len(runs):
        runs.to_csv(save_as)
        core.log.info(f"Written to {save_as}")
    else:
        core.log.info("No runs to process!")
        if os.path.exists(save_as):
            core.log.info(f"Removing {save_as} since there are no runs to process")
            os.remove(save_as)


def determine_data_to_reprocess(
        st: strax.Context,
        targets: ty.Union[str, tuple, list] = tuple(),
        special_modes: ty.Union[ty.List[str], ty.Tuple[str]] = (
                'LED', 'noise', 'pmtap', 'pmtgain', 'exttrig'),
        keep_detectors: ty.Union[str, tuple, list] = ('tpc',),
        exclude_from_invalid_cmt: ty.Optional[str] = core.config['context']['cmt_version'],
        _max_workers: int = 50
) -> pd.DataFrame:
    """
    Find data that we can process. This data needs to:
     1. (optional) be within the validity of a specified CMT version.
        Disable with exclude_from_invalid_cmt=False
     2. Don't be some calibration mode (led/noise etc. data)
     3. Not be available already (why would you want to reprocess that?)
     4. Have the data which we need in order to compute this target.

    :param st: Context to run with
    :param targets: Data types to produce
    :param special_modes: list of modes to exclude to determine here
        (usually you can do this trivially, so no need to use this
        function)
    :param exclude_from_invalid_cmt: A CMT version whereof we will check
        that the CMT version extends to those ranges where we would like
        to reprocess.
    :param _max_workers: Max workers for finding the stored data
    :return:
    """
    runs = st.select_runs(exclude_tags=('messy', 'abandoned'))
    core.log.info(f"Found {len(runs)} runs in total")

    if exclude_from_invalid_cmt:
        core.log.info('Find CMT validity')
        included = _within_valid_cmt_dates(runs, exclude_from_invalid_cmt)
        core.log.info(f"Found {np.sum(~included)}/{len(runs)} runs "
                      f"outside of validity of {exclude_from_invalid_cmt}")
        runs = runs[included]

    if keep_detectors:
        correct_detector = _find_correct_detectors(runs, keep_detectors)
        core.log.info(f"Found {np.sum(~correct_detector)}/{len(runs)} runs "
                      f"that do not have the {keep_detectors}-detector(s)")
        runs = runs[correct_detector]

    core.log.info('Find special modes')
    special_mode_mask = np.array(
        [any(x in mode for x in special_modes) for mode in runs['mode'].values]
    )

    core.log.info(f"Found {np.sum(special_mode_mask)}/{len(runs)} special modes ({special_modes}) "
                  f"Leave these alone for now.")
    runs = runs[~special_mode_mask]

    core.log.info('Find already stored runs')
    already_done = st.select_runs(available=targets)
    already_done = np.in1d(runs['number'], already_done['number'])
    core.log.info(f"Found {np.sum(already_done)}/{len(runs)} runs where "
                  f"the data is already stored")

    runs = runs[~already_done]
    core.log.warning(f'We are going to do a data-availability check for'
                     f' {len(runs)} runs, this may take a while (~10 it/s)')

    core.log.info('Find runs with all requirements stored')
    has_base = strax.utils.multi_run(
        st.get_sources,
        runs['name'],
        targets,
        max_workers=_max_workers,
        multi_run_progress_bar=core.config['display']['progress_bar']
    )
    has_base = np.array(has_base)
    can_make = has_base['run_id'][has_base['can_make']]
    can_make = np.in1d(runs['name'], can_make)
    core.log.info(f"Found {np.sum(~can_make)}/{len(runs)} runs where there is no"
                  f" source for {targets}")

    runs = runs[can_make]
    core.log.info(f"That leaves {len(runs)} runs to work on.")
    return runs


def _get_detectors(runs):
    return utilix.xent_collection().find(
        {'number':
             {'$in': [int(r) for r in runs]}
         },
        projection={'number': True, 'detectors': True},
    )


def _find_correct_detectors(runs, keep_detectors):
    """For each of the runs, find if the correct detector is in the list"""
    core.log.info('Find correct detector runs')
    if isinstance(keep_detectors, str):
        keep_detectors = [keep_detectors]
    dets = list(_get_detectors(runs['number']))
    correct_detector = []
    for r in runs['number']:
        for i, rd in enumerate(dets):
            if rd['number'] == int(r):
                det = rd.get('detectors', '?')
                if det == '?':
                    raise ValueError(f'No detector for {r}:{rd}??')
                del dets[i]
                break
        else:
            raise ValueError('No rundoc?!')
        is_correct = any(d in det for d in keep_detectors)
        correct_detector.append(is_correct)
    correct_detector = np.array(correct_detector)
    return correct_detector


@strax.context.Context.add_method
def get_sources(self, r, targets, **kwargs):
    """Allow multithreading of st.get_source"""
    for t in strax.to_str_tuple(targets):
        if t not in self._plugin_class_registry:
            raise ValueError(f'One or more of {targets} is not in correct format')
    res = np.zeros(1, dtype=[('can_make', np.bool_)])
    try:
        source = self.__get_source(r, targets)
        if source:
            res['can_make'][0] = source != set(targets)
    except Exception as e:
        core.log.error(
            f'No result for {r}, {targets} due to {e} is the data corrupted?'
        )

        raise e
    return res


# Copied from strax.Context.get_source for strax <= 1.1.3 (when this feature was added)
@strax.context.Context.add_method
def __get_source(self,
                 run_id: str,
                 target: str,
                 check_forbidden: bool = True,
                 ) -> ty.Union[set, None]:
    """
    For a given run_id and target get the stored bases where we can
    start processing from, if no base is available, return None.
    :param run_id: run_id
    :param target: target
    :param check_forbidden: Check that we are not requesting to make
        a plugin that is forbidden by the context to be created.
    :return: set of plugin names that are needed to start processing
        from and are needed in order to build this target.
    """
    try:
        return {plugin_name for plugin_name, plugin_stored in
                self.__stored_dependencies(run_id=run_id,
                                           target=target,
                                           check_forbidden=check_forbidden
                                           ).items()
                if plugin_stored}
    except strax.DataNotAvailable:
        return None


# Copied from strax.Context.get_source for strax <= 1.1.3 (when this feature was added)
@strax.context.Context.add_method
def __stored_dependencies(self,
                          run_id: str,
                          target: ty.Union[str, list, tuple],
                          check_forbidden: bool = True,
                          _targets_stored: ty.Optional[dict] = None,
                          ) -> ty.Optional[dict]:
    """
    For a given run_id and target(s) get a dictionary of all the datatypes that:
    :param run_id: run_id
    :param target: target or a list of targets
    :param check_forbidden: Check that we are not requesting to make
        a plugin that is forbidden by the context to be created.
    :return: dictionary of data types (keys) required for building
        the requested target(s) and if they are stored (values)
    :raises strax.DataNotAvailable: if there is at least one data
        type that is not stored and has no dependency or if it
        cannot be created
    """
    if _targets_stored is None:
        _targets_stored = {}

    targets = strax.to_str_tuple(target)
    if len(targets) > 1:
        # Multiple targets, do them all
        for dep in targets:
            self.__stored_dependencies(run_id,
                                       dep,
                                       check_forbidden=check_forbidden,
                                       _targets_stored=_targets_stored,
                                       )
        return _targets_stored

    # Make sure we have the string not ('target',)
    target = targets[0]

    if target in _targets_stored:
        return

    this_target_is_stored = self.is_stored(run_id, target)
    _targets_stored[target] = this_target_is_stored

    if this_target_is_stored:
        return _targets_stored

    # Need to init the class e.g. if we want to allow depends on like this:
    # https://github.com/XENONnT/cutax/blob/d7ec0685650d03771fef66507fd6882676151b9b/cutax/cutlist.py#L33  # noqa
    plugin = self._plugin_class_registry[target]()
    dependencies = strax.to_str_tuple(plugin.depends_on)
    if not dependencies:
        raise strax.DataNotAvailable(f'Lowest level dependency {target} is not stored')

    forbidden = strax.to_str_tuple(self.context_config['forbid_creation_of'])
    if check_forbidden and target in forbidden:
        forbidden_warning = (
            'For {run_id}:{target}, you are not allowed to make {dep} and '
            'it is not stored. Disable check with check_forbidden=False'
        )
        raise strax.DataNotAvailable(
            forbidden_warning.format(run_id=run_id, target=target, dep=target, ))

    self.__stored_dependencies(run_id,
                               target=dependencies,
                               check_forbidden=check_forbidden,
                               _targets_stored=_targets_stored,
                               )
    return _targets_stored


def _within_valid_cmt_dates(runs: pd.DataFrame, cmt_version: str) -> np.ndarray:
    v5_start, v5_end = utilix.rundb.cmt_global_valid_range(cmt_version)
    mask = pd.to_datetime(runs['end']) <= v5_end
    mask &= pd.to_datetime(runs['start']) >= v5_start
    return np.array(mask)
