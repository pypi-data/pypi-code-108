###############################################################################
# (c) Copyright 2021 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

import re
from collections import OrderedDict, defaultdict
from os.path import isfile, join, relpath

import jinja2
import yaml
from strictyaml import Any, Bool, Enum, Float, Int, Map, MapPattern
from strictyaml import Optional
from strictyaml import Optional as Opt
from strictyaml import Regex, Seq, Str, load

from LbAPCommon import config
from LbAPCommon.linting.bk_paths import validate_bk_query

RE_APPLICATION = r"^([A-Za-z]+/)+v\d+r\d+(p\d+)?"
RE_JOB_NAME = r"^[a-zA-Z0-9][a-zA-Z0-9_\-]+$"
RE_OUTPUT_FILE_TYPE = r"^([A-Za-z][A-Za-z0-9_]+\.)+((ROOT|root)|.?(DST|dst))$"
RE_OPTIONS_FN = r"^\$?[a-zA-Z0-9/\.\-\+\=_]+$"
RE_INFORM = r"^(?:[a-zA-Z]{3,}|[^@\s]+@[^@\s]+\.[^@\s]+)$"

RE_ROOT_IN_TES = r"^\/.+$"
RE_DDDB_TAG = r"^.{1,50}$"
RE_CONDDB_TAG = r"^.{1,50}$"

RE_COMMENT = r"(.{1,5000})"

BASE_JOB_SCHEMA = {
    "application": Regex(RE_APPLICATION),
    "input": MapPattern(Str(), Any()),
    "output": Regex(RE_OUTPUT_FILE_TYPE) | Seq(Regex(RE_OUTPUT_FILE_TYPE)),
    "options": Regex(RE_OPTIONS_FN) | Seq(Regex(RE_OPTIONS_FN)),
    "wg": Enum(config.known_working_groups),
    "inform": Regex(RE_INFORM) | Seq(Regex(RE_INFORM)),
    # Automatic configuration
    "automatically_configure": Bool(),
    "turbo": Bool(),
    Optional("root_in_tes"): Regex(RE_ROOT_IN_TES),
    Optional("simulation"): Bool(),
    Optional("luminosity"): Bool(),
    Optional("data_type"): Enum(config.known_data_types),
    Optional("input_type"): Enum(config.known_input_types),
    Optional("dddb_tag"): Regex(RE_DDDB_TAG),
    Optional("conddb_tag"): Regex(RE_CONDDB_TAG),
    Optional("checks"): Seq(Str()),  # TODO: replace this with a regex
    Optional("extra_checks"): Seq(Str()),  # TODO: replace this with a regex
    # Production submission metadata
    Optional("comment"): Regex(RE_COMMENT),
    "priority": Enum(config.allowed_priorities),
    "completion_percentage": Float(),
}
INPUT_SCHEMAS = {
    "bk_query": Map({"bk_query": Str(), Opt("n_test_lfns"): Int()}),
    "job_name": Map({"job_name": Str()}),
    "prod_id": Map({"prod_id": Str()}),
}
DEFAULT_JOB_VALUES = {
    "automatically_configure": False,
    "turbo": False,
    "completion_percentage": 100,
    "priority": "1b",
}

CHECK_TYPE_SCHEMAS = {
    "range": {
        "expression": Str(),  # TODO: replace this with a regex
        "limits": Map({"min": Float(), "max": Float()}),
        Optional("blind_ranges"): Map({"min": Float(), "max": Float()})
        | Seq(Map({"min": Float(), "max": Float()})),
        Optional("exp_mean"): Float(),
        Optional("exp_std"): Float(),
        Optional("mean_tolerance"): Float(),
        Optional("std_tolerance"): Float(),
    },
    "range_nd": {
        "expressions": Map(
            {  # TODO: replace Str() with a regex
                "x": Str(),
                "y": Str(),
                Optional("z"): Str(),
            }
        ),
        "limits": Map(
            {
                "x": Map({"min": Float(), "max": Float()}),
                "y": Map({"min": Float(), "max": Float()}),
                Optional("z"): Map({"min": Float(), "max": Float()}),
            }
        ),
        Optional("blind_ranges"): Seq(
            Map(
                {
                    "x": Map({"min": Float(), "max": Float()}),
                    "y": Map({"min": Float(), "max": Float()}),
                    Optional("z"): Map({"min": Float(), "max": Float()}),
                }
            )
        ),
    },
    "num_entries": {
        "count": Int(),
    },
    "num_entries_per_invpb": {
        "count_per_invpb": Float(),
        Optional("lumi_pattern"): Str(),
    },
    "range_bkg_subtracted": {
        "expression": Str(),
        "limits": Map({"min": Float(), "max": Float()}),
        "expr_for_subtraction": Str(),
        "mean_sig": Float(),
        "background_shift": Float(),
        "background_window": Float(),
        "signal_window": Float(),
        Optional("blind_ranges"): Map({"min": Float(), "max": Float()})
        | Seq(Map({"min": Float(), "max": Float()})),
    },
    "branches_exist": {
        "branches": Seq(Str()),
    },
}
BASE_CHECK_SCHEMA = {
    "type": Enum(list(CHECK_TYPE_SCHEMAS)),
    "tree_pattern": Str(),
}
BASE_CHECK_DEFAULT_VALUES = {
    "tree_pattern": r"(.*/DecayTree)|(.*/MCDecayTree)",
    "blind_ranges": [],
    "exp_mean": 0.0,
    "exp_std": 0.0,
    "mean_tolerance": 0.0,
    "std_tolerance": 0.0,
    "lumi_pattern": r"(.*/LumiTuple)",
}


def _ordered_dict_to_dict(a):
    if isinstance(a, (OrderedDict, dict)):
        return {k: _ordered_dict_to_dict(v) for k, v in a.items()}
    elif isinstance(a, (list, tuple)):
        return [_ordered_dict_to_dict(v) for v in a]
    else:
        return a


def render_yaml(raw_yaml):
    try:
        rendered_yaml = jinja2.Template(
            raw_yaml, undefined=jinja2.StrictUndefined
        ).render()
    except jinja2.TemplateError as e:
        raise ValueError(
            "Failed to render with jinja2 on line %s: %s"
            % (getattr(e, "lineno", "unknown"), e)
        ) from e
    return rendered_yaml


def _validate_proc_pass_map(job_names, proc_pass_map):
    """
    Given a list of step job names (in correct order), and the processing pass map,
    build the processing path for each step and verify the length is below 100.
    """
    for i, job_name in enumerate(job_names):
        proc_passes = map(proc_pass_map.get, job_names[:i] + [job_name])
        pro_path = "/".join(proc_passes)
        if len(pro_path) >= 100:
            proc_pass = proc_pass_map[job_name]
            step_jobs_list = "  - " + "\n  - ".join(job_names)
            raise ValueError(
                f"The expected processing path length for the job '{job_name}' is too long.\n"
                "DIRAC requires this to be less than 100 characters.\n\n"
                f"'Step' jobs:\n{step_jobs_list}\n"
                f"Job name: {job_name}\n"
                f"Processing pass for this step: {proc_pass}\n"
                f"Processing path for this step ({len(pro_path)} chars): {pro_path}\n\n"
                "To recover from this issue, consider:"
                "  - Removing redundant information from your job name.\n"
                "  - Shortening your job names.\n"
                "  - If the offending job depends on output from other jobs, ensure that they have a common prefix.\n"
            )


def create_proc_pass_map(job_names, version, default_proc_pass="default"):
    """
    Given a list of step job names and the production version, produce a
    job_name --> processing pass mapping.

    The processing pass map is validated by _validate_proc_pass_map
    """
    proc_pass_prefix = f"AnaProd-{version}-"
    proc_pass_map = {}

    # dummy_version = "v0r0p00000000"

    def clean_proc_pass(i, original_job_name):
        # attempt to remove redundant information from the job name
        job_name = re.sub(
            r"([0-9]{8})|(MagUp|MagDown|MU|MD)|((^|[^0*9])201[125678]($|[^0*9]))",
            "",
            original_job_name,
        )
        # Remove repeated separator chatacters
        job_name = re.sub(r"([-_])[-_]+", r"\1", job_name).strip("_-")
        if i == 0:
            return f"{proc_pass_prefix}{job_name}"

        proc_pass = job_name
        for previous_job_name in job_names[:i]:
            size = 0
            previous_proc_pass = proc_pass_map[previous_job_name]
            # Remove the prefix if this is the first job
            if previous_proc_pass.startswith(proc_pass_prefix):
                previous_proc_pass = previous_proc_pass[len(proc_pass_prefix) :]
            # Look for a common prefix and remove it
            for last, this in zip(previous_proc_pass, proc_pass):
                if last != this:
                    break
                size += 1
            proc_pass = proc_pass[size:].strip("_-+")
            # If the processing pass has been entirely stripped use a default
            if not proc_pass:
                proc_pass = default_proc_pass

        return proc_pass

    for i, job_name in enumerate(job_names):
        proc_pass_map[job_name] = clean_proc_pass(i, job_name)

    _validate_proc_pass_map(job_names, proc_pass_map)

    return proc_pass_map


def is_simulation_job(prod_data: dict, job_name: str):
    """Determine if a job is using MC input or not.

    :param prod_data: Entire production information from yaml parsing
    :param job_name: Name of the job to determine if it's using MC input or not
    :returns: True if the job is using MC input, False if it is not
    """

    job_dict = prod_data[job_name]
    if "simulation" not in job_dict:
        if "bk_query" in job_dict["input"]:
            if "/mc/" in job_dict["input"]["bk_query"].lower():
                return True
            else:
                return False
        elif "job_name" in job_dict["input"]:
            dependent_job = prod_data[job_name]["input"]["job_name"]
            return is_simulation_job(prod_data, dependent_job)
        else:
            raise NotImplementedError(
                "Input requires either a bookkeeping location or a previous job name"
            )


def parse_yaml(rendered_yaml):
    data1 = load(
        rendered_yaml, schema=MapPattern(Regex(RE_JOB_NAME), Any(), minimum_keys=1)
    )

    data_checks = {}
    if "checks" in data1:
        # apply the appropriate schema to each different type of check
        for _check_name, check_data in data1["checks"].items():
            check_schema = {
                **BASE_CHECK_SCHEMA,
                **CHECK_TYPE_SCHEMAS[str(check_data["type"])],
            }
            # apply default values
            for key, value in BASE_CHECK_SCHEMA.items():
                if key not in check_data and key in BASE_CHECK_DEFAULT_VALUES:
                    check_schema.pop(key, None)
                    check_schema[
                        Optional(key, default=BASE_CHECK_DEFAULT_VALUES[key])
                    ] = value

            check_data.revalidate(Map(check_schema))
        # if checks pass validation, store elsewhere & delete from main data
        # so that normal jobs aren't impacted
        data_checks = data1.data["checks"]
        del data1["checks"]

    if "defaults" in data1:
        defaults_schema = {}
        for key, value in BASE_JOB_SCHEMA.items():
            if isinstance(key, Optional):
                key = key.key
            key = Optional(key, default=DEFAULT_JOB_VALUES.get(key))
            defaults_schema[key] = value

        data1["defaults"].revalidate(Map(defaults_schema))
        defaults = data1.data["defaults"]
        # Remove the defaults data from the snippet
        del data1["defaults"]
    else:
        defaults = DEFAULT_JOB_VALUES.copy()

    job_names = list(data1.data.keys())
    if len(set(n.lower() for n in job_names)) != len(job_names):
        raise ValueError(
            "Found multiple jobs with the same name but different capitalisation"
        )

    job_name_schema = Regex(r"(" + r"|".join(map(re.escape, job_names)) + r")")

    # StrictYAML has non-linear complexity when parsing many keys
    # Avoid extremely slow parsing by doing each key individually
    data2 = {}
    for k, v in data1.items():
        k = k.data
        v = _ordered_dict_to_dict(v.data)

        production_schema = {}
        if "comment" in v:
            raise ValueError(
                "comment is only allowed to be set in the defaults of the production!"
            )
        for key, value in BASE_JOB_SCHEMA.items():
            if isinstance(key, Optional):
                key = key.key
                production_schema[Optional(key, default=defaults.get(key))] = value
            elif key in defaults:
                production_schema[Optional(key, default=defaults[key])] = value
            else:
                production_schema[key] = value

        data = load(
            yaml.safe_dump({k: v}),
            MapPattern(job_name_schema, Map(production_schema), minimum_keys=1),
        )
        for input_key, input_schema in INPUT_SCHEMAS.items():
            if input_key in data.data[k]["input"]:
                data[k]["input"].revalidate(input_schema)
                break
        else:
            raise ValueError(
                (
                    "Failed to find a valid schema for %s's input. "
                    "Allowed values are: %s"
                )
                % (k, set(INPUT_SCHEMAS))
            )

        # move contents of extra_checks to checks
        data.data.setdefault("checks", [])
        data_dict = data.data
        if "extra_checks" in data_dict[k]:
            data_dict[k]["checks"] += data_dict[k]["extra_checks"]
            del data_dict[k]["extra_checks"]

        data2.update(data_dict)

    return data2, data_checks


def _normalise_filetype(prod_name, job_name, filetype):
    filetype = filetype.upper()

    errors = []
    if len(filetype) >= 50:
        errors += ["The filetype is excessively long"]
    if re.findall(r"[0-9]{8}", filetype, re.IGNORECASE):
        errors += ["It appears the event type is included"]
    if re.findall(r"Mag(Up|Down)", filetype, re.IGNORECASE):
        errors += ["It appears the magnet polarity is included"]
    if re.findall(r"(^|[^0*9])201[125678]($|[^0*9])", filetype, re.IGNORECASE):
        errors += ["It appears the data taking year is included"]

    if errors:
        _errors = "\n  * ".join(errors)
        raise ValueError(
            f"Output filetype {filetype} for {prod_name}/{job_name} is invalid "
            f"as it appears to contain redundant information.\n\n"
            f"  * {_errors}"
        )
    return filetype


def _check_name_magnet_polarity(bk_query, job_name):
    match = re.search(r"-mag(up|down)[-/]", bk_query)
    if not match:
        return [f"Failed to find magnet polarity in {bk_query}"]
    good_pol = match.groups()[0]
    bad_pol = {"down": "up", "up": "down"}[good_pol]
    if f"mag{bad_pol}" in job_name:
        raise ValueError(
            f"Found 'mag{bad_pol}' in job name {job_name!r} with"
            f"'mag{good_pol}' input ({bk_query!r}). "
            "Has the wrong magnet polarity been used?"
        )
    match = re.search(r"([^a-z0-9]|\b)m(u|d)([^a-z0-9]|\b)", job_name)
    if match and match.groups()[1] == bad_pol[0]:
        raise ValueError(
            f"Found 'm{bad_pol[0]}' in job name {job_name!r} with"
            f"'mag{good_pol}' input ({bk_query!r}). "
            "Has the wrong magnet polarity been used?"
        )
    return []


def validate_yaml(jobs_data, checks_data, repo_root, prod_name):

    bk_query_to_job = defaultdict(set)

    warnings = []

    # Ensure all values that can be either a list or a string are lists of strings
    for job_name, job_data in jobs_data.items():
        try:
            _validate_job_data(repo_root, prod_name, job_name, job_data, checks_data)
        except Exception as e:
            raise ValueError(f"Failed to validate {job_name!r} with error {e!r}") from e
        if "bk_query" in job_data["input"]:
            if job_data["input"]["bk_query"].lower() in bk_query_to_job:
                warnings.append(
                    f'Duplicate bk_query found (this is a case insensitive check): {job_data["input"]["bk_query"].lower()}'
                )
            bk_query_to_job[job_data["input"]["bk_query"].lower()].add(job_name.lower())

    for query, job_set in bk_query_to_job.items():
        for job_name in job_set:
            warnings.extend(_check_name_magnet_polarity(query, job_name))

    polarity_len_swap = {"magdown": 5, "magup": 7}
    polarity_swap = {"magdown": "magup", "magup": "magdown"}

    # check that both polarities are always used for a given bk_query
    for query in bk_query_to_job:
        index = None
        query_polarity = None
        both_polarities = False
        for polarity in {"magdown", "magup"}:
            if polarity in query:
                index = query.find(polarity)
                query_polarity = polarity
        if query_polarity:
            for compare_query in bk_query_to_job:
                if compare_query != query:
                    if polarity_swap[query_polarity] in compare_query:
                        if (
                            compare_query[:index]
                            + query_polarity
                            + compare_query[
                                (index + polarity_len_swap[query_polarity]) :
                            ]
                            == query
                        ):
                            both_polarities = True
                            if len(bk_query_to_job[query]) != len(
                                bk_query_to_job[compare_query]
                            ):
                                warnings.append(
                                    f"The number of jobs requesting {query} does not"
                                    " match the number of jobs requesting its opposite"
                                    f" polarity counterpart {compare_query}."
                                )
            if not both_polarities:
                warnings.append(
                    f"{query} has been requested as input for {len(bk_query_to_job[query])} job(s)"
                    " but its opposite polarity counterpart has not been requested for any jobs."
                    " Are you sure you do not want the other polarity?"
                )

    # Validate checks
    try:
        _validate_checks_data(checks_data, jobs_data)
    except Exception as e:
        raise ValueError(f"Failed to validate checks with error {e!r}") from e

    return warnings


def _validate_job_data(repo_root, prod_name, job_name, job_data, checks_data):
    # Normalise list/str fields to always be lists
    for prop in ["output", "options", "inform", "checks", "extra_checks"]:
        if not isinstance(job_data.get(prop, []), list):
            job_data[prop] = [job_data[prop]]

    # Validate the input data
    if "bk_query" in job_data["input"]:
        validate_bk_query(job_data["input"]["bk_query"])

    # Validate the output filetype
    job_data["output"] = [
        _normalise_filetype(prod_name, job_name, s) for s in job_data["output"]
    ]

    # Normalise the options filenames
    normalised_options = []
    for fn in job_data["options"]:
        if fn.startswith("$"):
            normalised_options.append(fn)
            continue

        fn_normed = relpath(join(repo_root, fn), start=repo_root)
        if fn_normed.startswith("../"):
            raise ValueError(f"{fn} not found inside {repo_root}")
        if not isfile(join(repo_root, prod_name, fn_normed)):
            raise FileNotFoundError(
                f"Production {job_name!r} has a missing options file: "
                f"{join(prod_name, fn_normed)!r}",
            )
        normalised_options.append(
            join("$ANALYSIS_PRODUCTIONS_BASE", prod_name, fn_normed)
        )
    job_data["options"] = normalised_options

    # Validate the check names
    # All checks listed for jobs should match a check defined in checks_data
    if "checks" in job_data:
        for ck in job_data["checks"]:
            if ck not in list(checks_data.keys()):
                raise ValueError(f"Check {ck} not found in list of defined checks")

    # Validate the completion percentage
    if not (10 <= job_data["completion_percentage"] <= 100):
        raise ValueError(
            f"Validation failed for job '{job_name}', completion_percentage "
            f"was set to '{job_data['completion_percentage']}', allowed "
            "values are in the interval [10, 100]."
        )


def _validate_checks_data(checks_data, jobs_data):
    # All checks defined in checks_data should be used by at least 1 job
    checks_used = {ck: False for ck in checks_data}
    for _job_name, job_data in jobs_data.items():
        if "checks" in job_data:
            for ck in job_data["checks"]:
                if ck in checks_used:
                    checks_used[ck] = True
    for ck, ck_used in checks_used.items():
        if not ck_used:
            raise ValueError(f"Check {ck} is defined but not used")
