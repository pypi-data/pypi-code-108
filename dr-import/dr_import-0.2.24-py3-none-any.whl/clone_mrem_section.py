""" Clones a MREM trip/section to another project/section
Assumptions:
- Types are the same in the source/destination projects
- Assumes using Baseline version
"""

import argparse
import datetime
import dateutil
import os

import tator

def main(
        in_host: str,
        in_token: str,
        in_src_project: int,
        in_dest_project: int,
        in_src_section_name: str,
        in_dest_section_name: str,
        in_copy_annotations: bool,
        in_start_time: datetime.datetime=None,
        in_end_time: datetime.datetime=None) -> None:
    """ Clones the section (including GPS)

    :param in_host: Tator URL
    :param in_token: Tator API token
    :param in_src_project: Project ID that includes the section name to be cloned
    :param in_dest_project: Destination project ID
    :param in_src_section_name: Section to clone
    :param in_dest_section_name: Name of cloned section
    :param in_copy_annotations: If true, all discards and annotations (eg hauls) are cloned
    """

    tator_api = tator.get_api(host=in_host, token=in_token)

    # Get the media types in the source project
    media_types = tator_api.get_media_type_list(project=in_src_project)

    src_multi_type = []
    src_video_type = []
    src_image_type = []
    for media_type in media_types:
        if media_type.dtype == "multi":
            src_multi_type.append(media_type.id)

        elif media_type.dtype == "video":
            src_video_type.append(media_type.id)

        elif media_type.dtype == "image":
            src_image_type.append(media_type.id)

    if len(src_multi_type) != 1:
        logger.error(f"Multi type IDs: {src_multi_type}")
        raise ValueError(f"Invalid amount of multi media types in project {in_src_project}!")
    src_multi_type = src_multi_type[0]

    if len(src_video_type) != 1:
        logger.error(f"Video type IDs: {src_video_type}")
        raise ValueError(f"Invalid amount of video media types in project {in_src_project}!")
    src_video_type = src_video_type[0]

    if len(src_image_type) != 1:
        logger.error(f"Image type IDs: {src_image_type}")
        raise ValueError(f"Invalid amount of image media types in project {in_src_project}!")
    src_image_type = src_image_type[0]

    # Get the GPS type in source project
    src_gps_type = []
    state_types = tator_api.get_state_type_list(project=in_src_project)
    for state_type in state_types:
        if state_type.name == "GPS":
            src_gps_type.append(state_type.id)

    if len(src_gps_type) != 1:
        logger.error(f"GPS type IDs: {src_gps_type}")
        raise ValueError(f"Invalid amount of GPS state types in project {in_src_project}!")
    src_gps_type = src_gps_type[0]

    # #TODO Adjust to be dynamic with versions
    src_baseline_version = None
    versions = tator_api.get_version_list(project=in_src_project)
    for version in versions:
        if version.name == "Baseline":
            src_baseline_version = version.id

    # Only get the other types if requested to copy over annotations
    if in_copy_annotations:

        src_discard_type = None
        loc_types = tator_api.get_localization_type_list(project=in_src_project)
        for loc_type in loc_types:
            if loc_type.name == "Discard Event":
                if src_discard_type != None:
                    raise ValueError(f"Invalid amount of Discard Event types in project {in_src_project}!")
                src_discard_type = loc_type.id

        state_types = tator_api.get_state_type_list(project=in_src_project)

        src_reviewer_type = None
        src_haul_type = None
        src_crew_type = None
        src_em_specific_type = None
        src_video_qual_type = None
        src_fishing_op_type = None

        for state_type in state_types:
            if state_type.name == "Reviewer Info":
                if src_reviewer_type != None:
                    raise ValueError(f"Invalid amount of Reviewer Info types in project {in_src_project}!")
                src_reviewer_type = state_type.id

            elif state_type.name == "Haul":
                if src_haul_type != None:
                    raise ValueError(f"Invalid amount of Haul types in project {in_src_project}!")
                src_haul_type = state_type.id

            elif state_type.name == "Crew Event":
                if src_crew_type != None:
                    raise ValueError(f"Invalid amount of Crew Event types in project {in_src_project}!")
                src_crew_type = state_type.id

            elif state_type.name == "EM Specific Event":
                if src_em_specific_type != None:
                    raise ValueError(f"Invalid amount of EM Specific Event types in project {in_src_project}!")
                src_em_specific_type = state_type.id

            elif state_type.name == "Fishing Op. Event":
                if src_fishing_op_type != None:
                    raise ValueError(f"Invalid amount of Fishing Op. Event types in project {in_src_project}!")
                src_fishing_op_type = state_type.id

            #elif state_type.name == "Video Qual. Event":
            #    if src_video_qual_type != None:
            #        raise ValueError(f"Invalid amount of Video Qual. Event types in project {in_src_project}!")
            #    src_video_qual_type = state_type.id

    # Get the corresponding section ID
    src_section = tator_api.get_section_list(
        project=in_src_project, name=in_src_section_name)[0].id

    if in_dest_project == in_src_project:
        dest_multi_type = src_multi_type
        dest_video_type = src_video_type
        dest_image_type = src_image_type
        dest_gps_type = src_gps_type
        dest_baseline_version = src_baseline_version

        if in_copy_annotations:
            dest_discard_type = src_discard_type
            dest_haul_type = src_haul_type
            dest_crew_type = src_crew_type
            dest_em_specific_type = src_em_specific_type
            dest_video_qual_type = src_video_qual_type
            dest_fishing_op_type = src_fishing_op_type
            dest_reviewer_type = src_reviewer_type

    else:
        media_types = tator_api.get_media_type_list(project=in_dest_project)

        dest_multi_type = []
        dest_video_type = []
        dest_image_type = []
        for media_type in media_types:
            if media_type.dtype == "multi":
                dest_multi_type.append(media_type.id)

            elif media_type.dtype == "video":
                dest_video_type.append(media_type.id)

            elif media_type.dtype == "image":
                dest_image_type.append(media_type.id)

        if len(dest_multi_type) != 1:
            logger.error(f"Multi type IDs: {dest_multi_type}")
            raise ValueError(f"Invalid amount of multi media types in project {in_dest_project}!")
        dest_multi_type = dest_multi_type[0]

        if len(dest_video_type) != 1:
            logger.error(f"Video type IDs: {dest_video_type}")
            raise ValueError(f"Invalid amount of video media types in project {in_dest_project}!")
        dest_video_type = dest_video_type[0]

        if len(dest_image_type) != 1:
            logger.error(f"Image type IDs: {dest_image_type}")
            raise ValueError(f"Invalid amount of image media types in project {in_dest_project}!")
        dest_image_type = dest_image_type[0]

        # Get the GPS type in source project
        dest_gps_type = []
        state_types = tator_api.get_state_type_list(project=in_dest_project)
        for state_type in state_types:
            if state_type.name == "GPS":
                dest_gps_type.append(state_type.id)

        if len(dest_gps_type) != 1:
            logger.error(f"GPS type IDs: {dest_gps_type}")
            raise ValueError(f"Invalid amount of GPS state types in project {in_dest_project}!")
        dest_gps_type = dest_gps_type[0]

        # #TODO Adjust to be dynamic with versions
        dest_baseline_version = None
        versions = tator_api.get_version_list(project=in_dest_project)
        for version in versions:
            if version.name == "Baseline":
                dest_baseline_version = version.id

        if in_copy_annotations:

            dest_discard_type = None
            loc_types = tator_api.get_localization_type_list(project=in_dest_project)
            for loc_type in loc_types:
                if loc_type.name == "Discard Event":
                    if dest_discard_type != None:
                        raise ValueError(f"Invalid amount of Discard Event types in project {in_dest_project}!")
                    dest_discard_type = loc_type.id

            state_types = tator_api.get_state_type_list(project=in_dest_project)

            dest_haul_type = None
            dest_crew_type = None
            dest_em_specific_type = None
            dest_video_qual_type = None
            dest_fishing_op_type = None
            dest_reviewer_type = None

            for state_type in state_types:
                if state_type.name == "Reviewer Info":
                    if dest_reviewer_type != None:
                        raise ValueError(f"Invalid amount of Reviewer Info types in project {in_dest_project}!")
                    dest_reviewer_type = state_type.id

                elif state_type.name == "Haul":
                    if dest_haul_type != None:
                        raise ValueError(f"Invalid amount of Haul types in project {in_dest_project}!")
                    dest_haul_type = state_type.id

                elif state_type.name == "Crew Event":
                    if dest_crew_type != None:
                        raise ValueError(f"Invalid amount of Crew Event types in project {in_dest_project}!")
                    dest_crew_type = state_type.id

                elif state_type.name == "EM Specific Event":
                    if dest_em_specific_type != None:
                        raise ValueError(f"Invalid amount of EM Specific Event types in project {in_dest_project}!")
                    dest_em_specific_type = state_type.id

                elif state_type.name == "Fishing Op. Event":
                    if dest_fishing_op_type != None:
                        raise ValueError(f"Invalid amount of Fishing Op. Event types in project {in_dest_project}!")
                    dest_fishing_op_type = state_type.id

                #elif state_type.name == "Video Qual. Event":
                #    if dest_video_qual_type != None:
                #        raise ValueError(f"Invalid amount of Video Qual. Event types in project {in_dest_project}!")
                #    dest_video_qual_type = state_type.id

    # Create the new trip/section in the target project
    #response = tator_api.create_section_list(project=dest_project, name=in_dest_section_name)
    #dest_section = tator_api.get_section_list(id=response.id)

    # Create the new single-view trip/section in the target project
    #response = tator_api.create_section_list(project=dest_project, name=in_dest_single_view_section)
    #dest_single_view_section = tator_api.get_section_list(id=response.id)

    # Grab the multviews we care about
    src_multis = tator_api.get_media_list(
        project=in_src_project, type=src_multi_type, section=src_section)

    # Clone the new multi-view media
    media_ids = []
    filtered_src_multis = []
    for multi in src_multis:

        if in_start_time is not None and in_end_time is not None:
            current_multi_date = dateutil.parser.parse(multi.name.split(".multi")[0])
            if in_start_time <= current_multi_date <= in_end_time:
                media_ids.append(multi.id)
                filtered_src_multis.append(multi)
        else:
            media_ids.append(multi.id)
            filtered_src_multis.append(multi)

    print(f"Cloning media: {len(media_ids)} of {len(src_multis)}")
    src_multis = filtered_src_multis

    spec = {
      "dest_project": in_dest_project,
      "dest_type": dest_multi_type,
      "dest_section": in_dest_section_name
    }
    response = tator_api.clone_media_list(
        project=in_src_project, media_id=media_ids, clone_media_spec=spec)
    print(response)

    multi_id_mapping = {} # Keys = src multi ID, value = corresponding dest multi ID
    for src_multi_id, dest_multi_id in zip(media_ids, response.id):
        multi_id_mapping[src_multi_id] = dest_multi_id

    dest_section = tator_api.get_section_list(project=in_dest_project, name=in_dest_section_name)[0]
    dest_section_tator_user_sections = dest_section.tator_user_sections
    dest_section = dest_section.id
    dest_multis = tator_api.get_media_list(
        project=in_dest_project, type=dest_multi_type, section=dest_section)

    # Clone the single videos and update the new multi-view media
    prime_video_mapping = {} # Keys = src_multi.media_files.ids[0], values = dest_multi.media_files.ids
    single_video_mapping = {}
    for src_multi in src_multis:

        dest_multi_id = multi_id_mapping[src_multi.id]
        dest_multi = tator_api.get_media(dest_multi_id)

        spec = {
          "dest_project": in_dest_project,
          "dest_type": dest_video_type,
          "dest_section": in_dest_section_name + " singleview"
        }
        print(f"Cloning source multi.media_files.ids: {src_multi.media_files.ids}")
        response = tator_api.clone_media_list(
            project=in_src_project, media_id=src_multi.media_files.ids, clone_media_spec=spec)
        print(response)

        dest_videos = response.id
        dest_multi.media_files.ids = dest_videos
        media_update_spec = {"multi": {"ids": dest_multi.media_files.ids}}
        response = tator_api.update_media(id=dest_multi.id, media_update=media_update_spec)
        print(response)

        prime_video_mapping[src_multi.media_files.ids[0]] = dest_videos

        for src_vid, dest_vid in zip(src_multi.media_files.ids, dest_videos):
            single_video_mapping[src_vid] = dest_vid

    if in_copy_annotations:
        # Clone the summary media
        summary_media = tator_api.get_media_list(
            project=in_src_project, type=src_image_type, section=src_section)

        summary_media_id = [summary_media[0].id]

        spec = {
          "dest_project": in_dest_project,
          "dest_type": dest_image_type,
          "dest_section": in_dest_section_name
        }
        response = tator_api.clone_media_list(
            project=in_src_project, media_id=summary_media_id, clone_media_spec=spec)
        print(response)
        dest_media = response.id

        # Clone the reviewer info
        states = tator_api.get_state_list(
            project=in_src_project, media_id=summary_media_id, type=src_reviewer_type)

        dest_state_specs = []
        for state in states:
            spec = {
                "type": dest_reviewer_type,
                "media_ids": dest_media,
                "localization_ids": [],
                "version": dest_baseline_version,
                **state.attributes
            }
            if state.frame is not None:
                spec["frame"] = state.frame
            dest_state_specs.append(spec)

        if len(states) > 0:
            response = tator_api.create_state_list(project=in_dest_project, state_spec=dest_state_specs)
            print(response)

    else:
        # Upload the trip image
        summary_image = os.path.join(os.path.dirname(__file__),
                                    "trip_summary.png")
        for progress, response in tator.util.upload_media(
                api=tator_api, type_id=dest_image_type, path=summary_image):
            continue
        print(response)
        summary_image_id = response.id

        summary_media = tator_api.get_media(summary_image_id)
        media_update_spec = {"attributes": summary_media.attributes}
        media_update_spec["attributes"]["tator_user_sections"] = dest_section_tator_user_sections
        response = tator_api.update_media(id=summary_image_id, media_update=media_update_spec)

    # Copy over the GPS states
    #
    # States have shared media IDs. So only loop over the single videos, copy the states in that
    # video, and apply the shared media IDs.
    for src_video_id, dest_video_ids in prime_video_mapping.items():
        states = tator_api.get_state_list(
            project=in_src_project, media_id=[src_video_id], type=src_gps_type)

        # #TODO look into tator.util.clone_state_list to do this
        dest_state_specs = []
        for state in states:
            spec = {
                "type": dest_gps_type,
                "media_ids": dest_video_ids,
                "localization_ids": [],
                "version": dest_baseline_version,
                **state.attributes
            }
            if state.frame is not None:
                spec["frame"] = state.frame

            keys_to_remove = []
            for key in spec:
                if spec[key] is None:
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del spec[key]

            dest_state_specs.append(spec)

        if len(states) > 0:
            response = tator_api.create_state_list(project=in_dest_project, state_spec=dest_state_specs)
            print(response)

    if in_copy_annotations:
        # Copy over the other states if requested
        if src_video_qual_type is not None:
            src_state_types = [src_haul_type, src_crew_type, src_em_specific_type, src_video_qual_type, src_fishing_op_type]
            dest_state_types = [dest_haul_type, dest_crew_type, dest_em_specific_type, dest_video_qual_type, dest_fishing_op_type]
        else:
            src_state_types = [src_haul_type, src_crew_type, src_em_specific_type, src_fishing_op_type]
            dest_state_types = [dest_haul_type, dest_crew_type, dest_em_specific_type, dest_fishing_op_type]

        try:
            for src_video_id, dest_video_ids in prime_video_mapping.items():
                for src_type, dest_type in zip(src_state_types, dest_state_types):
                    states = tator_api.get_state_list(
                        project=in_src_project, media_id=[src_video_id], type=src_type)

                    # #TODO look into tator.util.clone_state_list to do this
                    dest_state_specs = []
                    for state in states:
                        spec = {
                            "type": dest_type,
                            "media_ids": dest_video_ids,
                            "localization_ids": [],
                            "version": dest_baseline_version,
                            **state.attributes
                        }
                        if state.frame is not None:
                            spec["frame"] = state.frame
                        dest_state_specs.append(spec)

                    if len(states) > 0:
                        response = tator_api.create_state_list(project=in_dest_project, state_spec=dest_state_specs)
                        print(response)
        except Exception as exc:
            print(exc)

        # Copy over the other localizations if requested
        for src_video_id, dest_video_id in single_video_mapping.items():
            locs = tator_api.get_localization_list(
                project=in_src_project, media_id=[src_video_id], type=src_discard_type)

            dest_loc_specs = []
            for loc in locs:
                spec = {
                    'type': dest_discard_type,
                    'version': dest_baseline_version,
                    'media_id': dest_video_id,
                    'x': loc.x,
                    'y': loc.y,
                    'width': loc.width,
                    'height': loc.height,
                    'u': loc.u,
                    'v': loc.v,
                    'frame': loc.frame,
                    **loc.attributes}
                dest_loc_specs.append(spec)

            if len(locs) > 0:
                response = tator_api.create_localization_list(project=in_dest_project, localization_spec=dest_loc_specs)
                print(response)

def parse_args() -> argparse.Namespace:
    """ Process script's arguments
    """

    parser = argparse.ArgumentParser(description="Clones a MREM trip/section to another project. Can copy all annotations.")
    parser.add_argument('--host', type=str, required=True)
    parser.add_argument('--token', type=str, required=True)
    parser.add_argument('--src-project', type=int, required=True)
    parser.add_argument('--src-section-name', type=str, required=True)
    parser.add_argument('--dest-project', type=int, required=True)
    parser.add_argument('--dest-section-name', type=str, required=True)
    parser.add_argument('--copy-annotations', action='store_true')
    parser.add_argument('--start-time', type=str, help="Use in conjunction with end-time argument. Omit to copy entire trip. Example: 2021-08-02T16:11:53")
    parser.add_argument('--end-time', type=str, help="Use in conjunction with end-time argument. Omit to copy entire trip. Example: 2021-08-02T16:11:53")
    args = parser.parse_args()
    return args

def script_main() -> None:
    """ Script's entry point
    """
    args = parse_args()

    start_time = None
    if args.start_time is not None:
        start_time = dateutil.parser.parse(args.start_time)

    end_time = None
    if args.end_time is not None:
        end_time = dateutil.parser.parse(args.end_time)

    main(
        in_host=args.host,
        in_token=args.token,
        in_src_project=args.src_project,
        in_src_section_name=args.src_section_name,
        in_dest_project=args.dest_project,
        in_dest_section_name=args.dest_section_name,
        in_copy_annotations=args.copy_annotations,
        in_start_time=start_time,
        in_end_time=end_time)

if __name__ == "__main__":
    script_main()