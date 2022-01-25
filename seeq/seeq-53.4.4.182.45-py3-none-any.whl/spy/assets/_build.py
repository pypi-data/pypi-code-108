import inspect
import re
import types
from types import ModuleType
from typing import List, Union, Type

import pandas as pd

from seeq.spy import _common
from seeq.spy._errors import *
from seeq.spy._status import Status
from seeq.spy.assets._model import _AssetBase, BuildContext, BuildPhase, SPyAssetMemberErrors
from seeq.spy.workbooks import Workbook


def build(model, metadata, errors='catalog', quiet=False, status: Status = None):
    """
    Utilizes a Python Class-based asset model specification to produce a set
    of item definitions as a metadata DataFrame.

    Parameters
    ----------
    model : {ModuleType, type, List[type]}
        A Python module, a spy.assets.Asset or list of spy.asset.Assets to
        use as the model for the asset tree to be produced. Follow the
        spy.assets.ipynb Tutorial to understand the structure of your
        module/classes.

    metadata : {pd.DataFrame}
        The metadata DataFrame, usually produced from calls to spy.search(),
        that will be used as the "ingredients" for the asset tree and passed
        into all Asset.Attribute() and Asset.Component() decorated class
        functions.

    errors : {'raise', 'catalog'}, default 'catalog'
        If 'raise', any errors encountered will cause an exception. If
        'catalog', errors will be added to a 'Result' column in the status.df
        DataFrame.

    quiet : bool
        If True, suppresses progress output.

    status : spy.Status, optional
        If specified, the supplied Status object will be updated as the command
        progresses. It gets filled in with the same information you would see
        in Jupyter in the blue/green/red table below your code while the
        command is executed. The table itself is accessible as a DataFrame via
        the status.df property.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with the metadata for the items that were built and are
        meant to be pushed, along with any errors in the Build Result column
        about the operation.

        Additionally, the following properties are stored on the "spy"
        attribute of the output DataFrame:

        =================== ===================================================
        Property            Description
        =================== ===================================================
        func                A str value of 'spy.assets.build'
        kwargs              A dict with the values of the input parameters
                            passed to spy.assets.build to get the output
                            DataFrame
        context             An object with the intermediate outputs of the
                            build process, sometimes useful for debugging
        status              A spy.Status object with the status of the
                            spy.assets.build call
        =================== ===================================================
    """

    input_args = _common.validate_argument_types([
        (model, 'model', (ModuleType, type, list)),
        (metadata, 'metadata', pd.DataFrame),
        (errors, 'errors', str),
        (quiet, 'quiet', bool),
        (status, 'status', Status)
    ])

    status = Status.validate(status, quiet)
    _common.validate_errors_arg(errors)

    status.update('Initializing', Status.RUNNING)

    if isinstance(model, type) and issubclass(model, _AssetBase) and 'Build Template' not in metadata:
        if 'Build Path' not in metadata or 'Build Asset' not in metadata:
            raise SPyValueError('"Build Path", "Build Asset" are required columns')
        status.df = metadata[['Build Path', 'Build Asset']].drop_duplicates()
        status.df['Build Template'] = model.__name__
    elif 'Build Path' not in metadata or 'Build Asset' not in metadata or 'Build Template' not in metadata:
        raise SPyValueError('"Build Path", "Build Asset", "Build Template" are required columns')
    else:
        status.df = metadata[['Build Path', 'Build Asset', 'Build Template']].drop_duplicates()

    columns_to_drop = ['Build Path', 'Build Asset', 'Build Template', 'Build Phase']
    build_templates = get_build_templates(model)

    # Note that we need to reset_index here because the metadata DataFrame may have been concatenated together and
    # contain non-unique index entries. We need them to be unique for proper bookkeeping during the loop below.
    status.df = status.df.dropna(subset=['Build Asset', 'Build Template']).reset_index(drop=True)

    context = BuildContext(status, errors=errors)

    phases = [BuildPhase.INSTANTIATING, BuildPhase.BUILDING, BuildPhase.SUCCESS]
    status.df['Build Phase'] = phases[0]

    while len(phases) > 1:
        context.phase = phases.pop(0)
        at_least_one_built = True
        while at_least_one_built:
            at_least_one_built = False
            for index, row in status.df.iterrows():
                if row['Build Phase'] != context.phase:
                    continue

                if not _common.present(row, 'Build Template'):
                    continue

                build_template_name = row['Build Template'].replace(' ', '_')

                found_templates = [bt for bt in build_templates if bt.__name__ == build_template_name]
                if len(found_templates) == 0:
                    raise SPyValueError(
                        f'Class not found in "model" argument that corresponds to '
                        f'Build Template "{build_template_name}"')

                template_to_use = found_templates[0]

                if context.phase != BuildPhase.INSTANTIATING:
                    instance = context.get_object(row, template_to_use)
                else:
                    instance = template_to_use(context, {
                        'Name': row['Build Asset'],
                        'Asset': row['Build Asset'],
                        'Path': row['Build Path']
                    })

                if pd.isna(row['Build Path']):
                    instance_metadata = metadata[(metadata['Build Asset'] == row['Build Asset']) &
                                                 (metadata['Build Path'].isna())]
                else:
                    instance_metadata = metadata[(metadata['Build Asset'] == row['Build Asset']) &
                                                 (metadata['Build Path'] == row['Build Path'])]

                try:
                    instance.build(instance_metadata)

                    at_least_one_built = True

                    next_phase = phases[0]
                    if next_phase == BuildPhase.SUCCESS:
                        # If there were any errors, put them in the status DataFrame now
                        status.df.at[index, 'Build Result'] = instance['Build Result']

                    # Advance to the next build phase
                    status.df.at[index, 'Build Phase'] = next_phase

                except SPyAssetMemberErrors as e:
                    status.df.at[index, 'Build Result'] = str(e)
                    continue

                except BaseException as e:
                    if errors == 'raise':
                        status.exception(e)
                        raise
                    else:
                        status.df.at[index, 'Build Result'] = str(e)

    if errors == 'raise':
        build_results = status.df['Build Result']
        build_errors = build_results.where(build_results != 'Success').dropna().tolist()
        if len(build_errors) > 0:
            error_message = '\n'.join(build_errors)
            exception = SPyRuntimeError(error_message)
            status.exception(exception)
            raise exception

    results = context.get_results()
    results.extend([{
        'Type': 'Workbook',
        'Workbook Type': workbook['Workbook Type'],
        'Name': workbook.name,
        'Object': workbook
    } for workbook in context.workbooks.values() if isinstance(workbook, Workbook)])

    results_df = pd.DataFrame(results)

    results_df = results_df.drop(columns=columns_to_drop, errors='ignore')

    status.df.drop(columns=['Build Phase'], inplace=True)

    build_results = status.df['Build Result'].drop_duplicates().tolist()
    if len(build_results) != 1 or build_results[0] != 'Success':
        status.update('Errors were encountered. Look for entries in "Build Result" that are not "Success".',
                      Status.FAILURE)
    else:
        status.update(f'Successfully built {len(status.df)} assets and '
                      f'{len(results_df[results_df["Type"] != "Asset"])} attributes.', Status.SUCCESS)

    output_df_properties = types.SimpleNamespace(
        func='spy.assets.build',
        kwargs=input_args,
        context=context,
        status=status)

    _common.put_properties_on_df(results_df, output_df_properties)

    return results_df


def get_build_templates(model: Union[ModuleType, Type[_AssetBase], List[Type[_AssetBase]]]) -> List[Type[_AssetBase]]:
    templates = list()
    if isinstance(model, ModuleType):
        for name, obj in inspect.getmembers(model):
            if isinstance(obj, type) and issubclass(obj, _AssetBase) and obj != _AssetBase:
                templates.append(obj)

    elif isinstance(model, list):
        templates = model
    elif issubclass(model, _AssetBase):
        templates = [model]
    else:
        raise SPyTypeError('"model" parameter must be a Python module (with Assets) or an Asset class declaration')

    return templates


def prepare(metadata, *, root_asset_name=None):
    """
    Modifies (in place) a metadata DataFrame that represents an existing tree,
    usually obtained by doing spy.search(recursive=True), and creates
    "Build Path" and "Build Asset" columns that are suitable for typical use of
    spy.assets.build().

    Parameters
    ----------
    metadata : pd.DataFrame
        The metadata DataFrame, usually produced from calls to
        spy.search(recursive=True) on an existing tree, that will be used
        as the "ingredients" for spy.assets.build().

    root_asset_name : str, optional
        An optional new name to use as the root of the tree. You will typically
        want to specify this so that your new tree is differentiated from the
        existing tree.
    """
    for column in ['Type', 'Path', 'Asset', 'Name']:
        if column not in metadata:
            raise SPyValueError(f'"{column}" is a required column')

    def _choose_build_asset(_row):
        if _row['Type'] == 'Asset':
            return _row['Name']
        else:
            return _row['Asset']

    def _choose_build_path(_row):
        path = _row['Path']
        if _row['Type'] == 'Asset':
            if pd.isna(_row['Path']):
                path = _row['Asset']
            else:
                path = f'{_row["Path"]} >> {_row["Asset"]}'

        if root_asset_name:
            path = re.sub(r'^\s*.*?(\s*(>>|$))', rf'{root_asset_name}\1', path)

        return path

    metadata['Build Path'] = metadata.apply(_choose_build_path, axis=1)
    metadata['Build Asset'] = metadata.apply(_choose_build_asset, axis=1)
