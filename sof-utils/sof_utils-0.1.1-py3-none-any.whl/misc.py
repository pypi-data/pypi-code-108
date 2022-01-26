from typing import List, Dict, Tuple


def id_and_visit_from_filename(filename: str) -> Tuple[int, int]:
    """ Extract the SOF ID and the visit from a given DICOM filename
    :param filename: filenamne of a .dcm file
    :return: (id: int, visit: int) SOF id and visit as encoded in the filename
    """
    import re
    pattern = "SF([0-9]+)V([0-9]+)H.dcm"
    match = re.match(pattern, filename)
    return int(match.groups()[0]), int(match.groups()[1])


def read_label_file(filename: str) -> List[Dict]:
    """ Reads proximal femur detection labels from a label-studio json file and returns
        it's content in a cleaned up way.
    :param filename: Path to a label-studio json file
    :return: List of dictionary containing the information:
        (id: str, flipped: int, left_incomplete: int, left_incomplete_shaft:int, left_implant,
         right_incomplete: int, right_incomplete_shaft:int, right_implant,
         left_bbox_x: float, left_bbox_y: float, left_bbox_w: float, left_bbox_h: float,
         right_bbox_x: float, right_bbox_y: float, right_bbox_w: float, right_bbox_h: float) where the id
         is stored in the format <SOF_ID>V<Visit> and all int values are either 0 (false/absent) or 1 (true/present).
         The bbox coordinates are given in absolute pixel coordinates.
    """
    import json
    import re
    from pathlib import Path
    from zipfile import ZipFile

    labels = []

    label_path = Path(filename)

    open_file = lambda: open(filename, 'r')

    skipped = []

    if label_path.suffix == '.zip':
        zip_file = ZipFile(label_path, 'r')
        open_file = zip_file.open('result.json', 'r')

    with open_file as fh:
        for item in json.load(fh):
            matches = re.match('^.*[/-]([0-9]+)V([0-9])+(L|R)-([0-9]+)x([0-9]+)\.png$', item['image']).groups()
            image_filename = re.match('^(.*/)?([^/]+\.png)$', item['image']).groups()[-1]
            if not matches or len(matches) != 5:
                raise ValueError(f"Annotated image '{item['image']}' has wrong format!")

            image_id = int(matches[0])
            visit = int(matches[1])
            lr = matches[2]
            width = int(matches[3])
            height = int(matches[4])

            if "labels" in item:
                image_labels = item['labels'] if isinstance(item['labels'], List) else [item['labels']]
            else:
                image_labels = []
            incomplete = 1 if "Incomplete" in image_labels else 0
            implant = 1 if "Implant" in image_labels else 0
            upside_down = 1 if "UpsideDown" in image_labels else 0

            invalid_keypoints = (incomplete + implant) > 0

            if not invalid_keypoints and ("keypoints" not in item or len(item['keypoints']) != 12):
                import sys
                print(f"Annotation for {image_filename} has invalid keypoints. Skipping.", file=sys.stderr)
                skipped.append(image_filename)
                continue

            entry = {
                'filename': image_filename,
                'id': image_id,
                'visit': visit,
                'left_right': lr,
                'upside_down': upside_down,
                'incomplete': incomplete,
                'implant': implant,
                'width': width,
                'height': height
            }

            keypoints = item['keypoints'] if not invalid_keypoints else [i for i in range(12)]

            bbox_min_x = min([float(kp['x']) for kp in keypoints]) if not invalid_keypoints else 0.0
            bbox_max_x = max([float(kp['x']) for kp in keypoints]) if not invalid_keypoints else 100.0
            bbox_min_y = min([float(kp['y']) for kp in keypoints]) if not invalid_keypoints else 0.0
            bbox_max_y = max([float(kp['y']) for kp in keypoints]) if not invalid_keypoints else 100.0

            entry['bbox_min_x'] = bbox_min_x
            entry['bbox_max_x'] = bbox_max_x
            entry['bbox_min_y'] = bbox_min_y
            entry['bbox_max_y'] = bbox_max_y

            for index, kp in enumerate(keypoints):
                entry[f"keypoint_x_{index}"] = float(kp['x']) if not invalid_keypoints else 0.0
                entry[f"keypoint_y_{index}"] = float(kp['y']) if not invalid_keypoints else 0.0

            labels.append(entry)

    return labels, skipped
