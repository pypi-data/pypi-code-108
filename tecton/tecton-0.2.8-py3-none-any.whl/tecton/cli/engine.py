import io
import os
import sys
import tarfile
import time
from pathlib import Path
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import requests
from colorama import Fore
from colorama import Style
from google.protobuf.json_format import MessageToJson
from yaspin.spinners import Spinners

import tecton
from .cli_utils import confirm_or_exit
from .cli_utils import human_fco_type
from .error_utils import format_server_errors
from tecton import Entity
from tecton import FeatureService
from tecton._internals import errors
from tecton._internals import metadata_service
from tecton._internals.analytics import TectonStateUpdateMetrics
from tecton._internals.utils import is_live_workspace
from tecton.cli import printer
from tecton.cli.common import get_current_workspace
from tecton.data_sources.data_source import BaseDataSource
from tecton.feature_views.feature_view import FeatureDefinition
from tecton.transformations.builtin_transformations import BuiltinTransformation
from tecton.transformations.transformation import Transformation
from tecton_proto.args.entity_pb2 import EntityArgs
from tecton_proto.args.fco_args_pb2 import FcoArgs
from tecton_proto.args.feature_service_pb2 import FeatureServiceArgs
from tecton_proto.args.feature_view_pb2 import FeatureViewArgs
from tecton_proto.args.feature_view_pb2 import FeatureViewType
from tecton_proto.args.new_transformation_pb2 import NewTransformationArgs
from tecton_proto.args.repo_metadata_pb2 import FeatureRepoSourceInfo
from tecton_proto.args.virtual_data_source_pb2 import DataSourceType
from tecton_proto.args.virtual_data_source_pb2 import VirtualDataSourceArgs
from tecton_proto.cli import repo_diff_pb2
from tecton_proto.data import state_update_pb2
from tecton_proto.metadataservice.metadata_service_pb2 import ApplyStateUpdateRequest
from tecton_proto.metadataservice.metadata_service_pb2 import NewStateUpdateRequest
from tecton_proto.metadataservice.metadata_service_pb2 import QueryStateUpdateRequest

UnwrappedFcoArgs = Union[
    VirtualDataSourceArgs,
    EntityArgs,
    NewTransformationArgs,
    FeatureViewArgs,
    FeatureServiceArgs,
]


def convert_to_repo_diff_summary(fco_diffs: List[state_update_pb2.FcoDiff]) -> repo_diff_pb2.TectonRepoDiffSummary:
    repo_diff = repo_diff_pb2.TectonRepoDiffSummary()
    for fco_diff in fco_diffs:
        repo_diff.object_diffs.append(convert_to_tecton_object_diff(fco_diff))

    return repo_diff


def convert_to_tecton_object_diff(fco_diff: state_update_pb2.FcoDiff) -> repo_diff_pb2.TectonObjectDiff:
    object_diff = repo_diff_pb2.TectonObjectDiff()
    object_diff.transition_type = fco_diff.type

    _, _, unwrapped_args = parse_plan_item(fco_diff)
    object_diff.object_metadata.name = unwrapped_args.info.name
    if unwrapped_args.info.owner:
        object_diff.object_metadata.owner = unwrapped_args.info.owner
    if unwrapped_args.info.description:
        object_diff.object_metadata.description = unwrapped_args.info.description

    object_diff.object_metadata.object_type = get_tecton_object_type(fco_diff)

    return object_diff


_FCO_TYPE_TO_OBJECT_TYPE = {
    "virtual_data_source": repo_diff_pb2.TectonObjectType.DATA_SOURCE,
    "entity": repo_diff_pb2.TectonObjectType.ENTITY,
    "feature_view": repo_diff_pb2.TectonObjectType.FEATURE_VIEW,
    "feature_service": repo_diff_pb2.TectonObjectType.FEATURE_SERVICE,
    "transformation": repo_diff_pb2.TectonObjectType.TRANSFORMATION,
    "new_transformation": repo_diff_pb2.TectonObjectType.TRANSFORMATION,
}


def get_tecton_object_type(fco_diff: state_update_pb2.FcoDiff) -> repo_diff_pb2.TectonObjectType:
    if fco_diff.type == state_update_pb2.FcoTransitionType.CREATE:
        fco_type = fco_diff.declared_args.WhichOneof("args")
    else:
        fco_type = fco_diff.existing_args.WhichOneof("args")

    if fco_type not in _FCO_TYPE_TO_OBJECT_TYPE:
        raise errors.INTERNAL_ERROR(f"Error computing Tecton object type from FCO type: {fco_type}.")

    return _FCO_TYPE_TO_OBJECT_TYPE[fco_type]


def unwrap_args(fco_args) -> Tuple[str, UnwrappedFcoArgs]:
    fco_type = fco_args.WhichOneof("args")
    if fco_type == "virtual_data_source":
        unwrapped_args = fco_args.virtual_data_source
        if unwrapped_args.type == DataSourceType.BATCH:
            fco_type = "batch_data_source"
        elif unwrapped_args.type == DataSourceType.STREAM_WITH_BATCH:
            fco_type = "stream_data_source"
    elif fco_type == "entity":
        unwrapped_args = fco_args.entity
    elif fco_type == "transformation":
        unwrapped_args = fco_args.transformation
    elif fco_type == "new_transformation":
        unwrapped_args = fco_args.new_transformation
    elif fco_type == "feature_view":
        unwrapped_args = fco_args.feature_view
        if unwrapped_args.feature_view_type == FeatureViewType.FEATURE_VIEW_TYPE_TEMPORAL:
            if unwrapped_args.temporal_args.data_source_type == DataSourceType.BATCH:
                fco_type = "batch_feature_view"
            elif unwrapped_args.temporal_args.data_source_type == DataSourceType.STREAM_WITH_BATCH:
                fco_type = "stream_feature_view"
        elif unwrapped_args.feature_view_type == FeatureViewType.FEATURE_VIEW_TYPE_TEMPORAL_AGGREGATE:
            if unwrapped_args.temporal_aggregate_args.data_source_type == DataSourceType.BATCH:
                fco_type = "batch_window_aggregate_feature_view"
            elif unwrapped_args.temporal_aggregate_args.data_source_type == DataSourceType.STREAM_WITH_BATCH:
                fco_type = "stream_window_aggregate_feature_view"
        elif unwrapped_args.feature_view_type == FeatureViewType.FEATURE_VIEW_TYPE_ON_DEMAND:
            fco_type = "on_demand_feature_view"

    elif fco_type == "feature_service":
        unwrapped_args = fco_args.feature_service
    else:
        assert False, f"Unknown object type: '{fco_type}'"

    # Currently, FeatureTable args are stored using FeatureViewArgs proto.
    # We differentiate between FeatureTable and FeatureView python classes here.
    if fco_type == "feature_view" and unwrapped_args.HasField("feature_table_args"):
        fco_type = "feature_table"

    return fco_type, unwrapped_args


def parse_plan_item(item: state_update_pb2.FcoDiff) -> Tuple[str, str, UnwrappedFcoArgs]:
    plan_item_type = state_update_pb2._FCOTRANSITIONTYPE.values_by_number[item.type].name
    if plan_item_type == "CREATE":
        fco_args = item.declared_args
    elif plan_item_type == "DELETE":
        fco_args = item.existing_args
    elif plan_item_type == "UPGRADE":
        fco_args = item.existing_args
    elif plan_item_type == "UPDATE":
        fco_args = item.existing_args
    elif plan_item_type == "RECREATE":
        fco_args = item.existing_args
    else:
        assert False, f"Unknown item type {plan_item_type}"

    fco_type, unwrapped_args = unwrap_args(fco_args)

    return plan_item_type, fco_type, unwrapped_args


def pprint_fields(args):
    def pprint_metadata(indent, args):
        colwidth = 16
        printer.safe_print(indent * " " + f'{"name:".ljust(colwidth)} {args.info.name}')
        if args.info.owner:
            printer.safe_print(indent * " " + f'{"owner:".ljust(colwidth)} {args.info.owner}')
        if args.info.description:
            printer.safe_print(indent * " " + f'{"description:".ljust(colwidth)} {args.info.description}')

    pprint_metadata(4, args)


def pprint_plan_item(item):
    plan_item_type, fco_type, unwrapped_args = parse_plan_item(item)
    indent = 2
    if plan_item_type == "CREATE":
        color = Fore.GREEN
        msg = f"+ Create {human_fco_type(fco_type)}"
    elif plan_item_type == "DELETE":
        color = Fore.RED
        msg = f"- Delete {human_fco_type(fco_type)}"
    elif plan_item_type == "UPGRADE":
        color = Fore.CYAN
        msg = f"~ Upgrade {human_fco_type(fco_type)} to the latest Tecton version"
    elif plan_item_type == "UPDATE":
        color = Fore.YELLOW
        msg = f"~ Update {human_fco_type(fco_type)}"
    elif plan_item_type == "RECREATE":
        color = Fore.RED
        msg = f"~ Recreate (destructive) {human_fco_type(fco_type)}"
    else:
        assert False, f"Unknown item type {plan_item_type}"

    printer.safe_print((indent * " ") + color + msg + Fore.RESET)
    pprint_fields(unwrapped_args)

    diff_indent = 4
    for diff_item in item.diff:
        if len(diff_item.val_existing) + len(diff_item.val_declared) < 80:
            msg = diff_item.property_name + ": " + diff_item.val_existing + " -> " + diff_item.val_declared
        else:
            nl = (
                ""
                if len(diff_item.val_existing) + len(diff_item.val_declared) < 80
                else "\n" + ((diff_indent + 2) * " ")
            )
            msg = (
                diff_item.property_name
                + ": "
                + nl
                + diff_item.val_existing
                + nl
                + " \u2B07\u2B07\u2B07\u2B07\u2B07 "
                + nl
                + diff_item.val_declared
            )
        printer.safe_print((diff_indent * " ") + color + msg + Fore.RESET)


def print_plan_server(plan_items: Iterable[state_update_pb2.FcoDiff]):
    if not plan_items:
        printer.safe_print(Style.BRIGHT + "🎉 The remote and local state are the same, nothing to do! ", Style.RESET_ALL)
        return
    printer.safe_print(Style.BRIGHT, "↓↓↓↓↓↓↓↓↓↓↓↓ Plan Start ↓↓↓↓↓↓↓↓↓↓", Style.RESET_ALL)
    printer.safe_print(Fore.RESET)
    for item in plan_items:
        pprint_plan_item(item)
        printer.safe_print(Fore.RESET)

    printer.safe_print(Style.BRIGHT, "↑↑↑↑↑↑↑↑↑↑↑↑ Plan End ↑↑↑↑↑↑↑↑↑↑↑↑", Style.RESET_ALL)


def confirm_plan(plan_items: Iterable[state_update_pb2.FcoDiff], interactive: bool, workspace: str):
    updates_fs = False
    for item in plan_items:
        _, fco_type, _ = parse_plan_item(item)
        if fco_type == "feature_service":
            updates_fs = True

    materialization_enabled = is_live_workspace(workspace)
    if updates_fs and materialization_enabled:
        printer.safe_print(
            "Note: Updates to Feature Services may take up to 60 seconds to be propagated to the real-time feature-serving endpoint.",
            file=sys.stderr,
        )

    if interactive:
        if materialization_enabled:
            printer.safe_print(
                f'{Fore.YELLOW}NOTE: the "{workspace}" workspace is a "Live" workspace. Applying may result in materialization jobs being spun up.{Fore.RESET}'
            )

        confirm_or_exit(f'Are you sure you want to apply this plan to: "{workspace}"?')


def get_declared_fco_args(objects) -> Tuple[List[FcoArgs], FeatureRepoSourceInfo]:
    all_args = []
    repo_source_info = FeatureRepoSourceInfo()

    for fco_obj in objects:
        fco_args = FcoArgs()
        args = fco_obj._args
        source_info = fco_obj._source_info
        if isinstance(fco_obj, BaseDataSource):
            source_info.fco_id.CopyFrom(args.virtual_data_source_id)
            fco_args.virtual_data_source.CopyFrom(args)
        elif isinstance(fco_obj, Entity):
            source_info.fco_id.CopyFrom(args.entity_id)
            fco_args.entity.CopyFrom(args)
        elif isinstance(fco_obj, Transformation):
            if isinstance(fco_obj, BuiltinTransformation) and fco_obj.call_count == 0:
                continue
            source_info.fco_id.CopyFrom(args.transformation_id)
            fco_args.new_transformation.CopyFrom(args)
        elif isinstance(fco_obj, FeatureDefinition):
            source_info.fco_id.CopyFrom(args.feature_view_id)
            fco_args.feature_view.CopyFrom(args)
        elif isinstance(fco_obj, FeatureService):
            source_info.fco_id.CopyFrom(args.feature_service_id)
            fco_args.feature_service.CopyFrom(args)
        else:
            assert False, f"Warning: unknown object{fco_obj}"

        all_args.append(fco_args)

        source_info.CopyFrom(source_info)
        repo_source_info.source_info.append(source_info)

    return all_args, repo_source_info


def dump_local_state(objects):
    with printer.safe_yaspin(Spinners.earth, text="Collecting local feature declarations") as sp:
        fco_args, repo_source_info = get_declared_fco_args(objects)
        sp.ok(printer.safe_string("✅"))

    request_plan = NewStateUpdateRequest()
    request_plan.request.fco_args.extend(fco_args)
    request_plan.request.repo_source_info.CopyFrom(repo_source_info)
    printer.safe_print(MessageToJson(request_plan, including_default_value_fields=True))


# upload tar.gz of python files to url via PUT request
def upload_files(repo_files: List[Path], repo_root, url: str):
    tar_bytes = io.BytesIO()
    with tarfile.open(fileobj=tar_bytes, mode="w|gz") as targz:
        for f in repo_files:
            targz.add(f, arcname=os.path.relpath(f, repo_root))
    for _ in range(3):
        try:
            r = requests.put(url, data=tar_bytes.getbuffer())
            if r.status_code != 200:
                # We will get 403 (forbidden) when the signed url expires.
                if r.status_code == 403:
                    printer.safe_print(
                        f"\nUploading feature repo failed due to expired session. Please retry the command."
                    )
                else:
                    printer.safe_print(f"\nUploading feature repo failed with reason: {r.reason}")
                sys.exit(1)
            return
        except requests.RequestException as e:
            last_error = e
    else:
        raise SystemExit(last_error)


def update_tecton_state(
    objects,
    repo_files: List[Path],
    repo_root: str,
    apply,
    debug,
    interactive,
    upgrade_all: bool,
    json_out_path: Optional[Path] = None,
    timeout_seconds=90 * 60,
) -> TectonStateUpdateMetrics:

    with printer.safe_yaspin(Spinners.earth, text="Collecting local feature declarations") as sp:
        fco_args, repo_source_info = get_declared_fco_args(objects)
        sp.ok(printer.safe_string("✅"))

    request_plan = NewStateUpdateRequest()
    request_plan.request.workspace = get_current_workspace()
    request_plan.request.upgrade_all = upgrade_all

    request_plan.request.fco_args.extend(fco_args)
    request_plan.request.repo_source_info.CopyFrom(repo_source_info)

    # In debug mode we compute the plan synchronously, do not save it in the database, and do not allow to apply it.
    # Primary goal is allowing local development/debugging plans against remote clusters in read-only mode.
    if debug:
        assert not apply, "Cannot apply in debug mode"
        request_plan.blocking_dry_run_mode = True

    server_side_msg_prefix = "Performing server-side feature validation: "
    with printer.safe_yaspin(Spinners.earth, text=server_side_msg_prefix) as sp:
        try:
            response_submit = metadata_service.instance().NewStateUpdate(request_plan)
            if debug:
                response_query = response_submit.blocking_dry_run_mode_response
            else:
                upload_files(repo_files, repo_root, response_submit.signed_url_for_repo_upload)

                seconds_slept = 0
                request_query = QueryStateUpdateRequest()
                request_query.state_id.CopyFrom(response_submit.state_id)
                while True:
                    response_query = metadata_service.instance().QueryStateUpdate(request_query)
                    if response_query.latest_status_message:
                        sp.text = server_side_msg_prefix + response_query.latest_status_message
                    if response_query.ready:
                        break
                    seconds_to_sleep = 5
                    time.sleep(seconds_to_sleep)
                    seconds_slept += seconds_to_sleep
                    if seconds_slept > timeout_seconds:
                        sp.fail(printer.safe_string("⛔"))
                        printer.safe_print("Validation timed-out")
                        return TectonStateUpdateMetrics.from_error_message("Validation timed-out")

            if response_query.error:
                sp.fail(printer.safe_string("⛔"))
                printer.safe_print(response_query.error)
                return TectonStateUpdateMetrics.from_error_message(response_query.error)
            if response_query.validation_result.messages:
                sp.fail(printer.safe_string("⛔"))
                format_server_errors(response_query.validation_result.messages, objects, repo_root)
                return TectonStateUpdateMetrics.from_error_message(str(response_query.validation_result.messages))
            sp.ok(printer.safe_string("✅"))
        except tecton.tecton_errors.TectonInternalError as e:
            sp.fail(printer.safe_string("⛔"))
            printer.safe_print(e)
            return TectonStateUpdateMetrics.from_error_message(str(e))
        except tecton._internals.tecton_errors.TectonAPIValidationError as e:
            sp.fail(printer.safe_string("⛔"))
            printer.safe_print(e)
            return TectonStateUpdateMetrics.from_error_message(str(e))

    print_plan_server(response_query.diff_items)

    if apply and response_query.diff_items:
        # Use the workspace from the update request because the current workspace may have changed.
        confirm_plan(response_query.diff_items, interactive, request_plan.request.workspace)

        request_apply = ApplyStateUpdateRequest()
        request_apply.state_id.CopyFrom(response_submit.state_id)
        response_apply = metadata_service.instance().ApplyStateUpdate(request_apply)

        printer.safe_print("🎉 all done!")

    if json_out_path:
        repo_diff_summary = convert_to_repo_diff_summary(response_query.diff_items)
        json_out_path.parent.mkdir(parents=True, exist_ok=True)
        json_out_path.write_text(MessageToJson(repo_diff_summary))

    num_fcos_changed = 0
    for item in response_query.diff_items:
        if item.type != state_update_pb2.FcoTransitionType.UNCHANGED:
            num_fcos_changed += 1
    return TectonStateUpdateMetrics(num_total_fcos=len(objects), num_fcos_changed=num_fcos_changed)
