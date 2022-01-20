from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import json

import math

import os

import publisher.settings as settings
from publisher.exceptions import ContentMissingError
from publisher.processing.data_sources.csv_steps_file import get_csv_steps_file
from publisher.processing.data_sources.utils import read_csv_file
from publisher.utils import get_procedure_code


def get_step_data(phase_code, csv_version=None):
    headers, rows = get_csv_info(phase_code, csv_version)

    learn_data = []
    test_data = []

    i = datetime.datetime.now()
    info_text = "This phase was built on %s/%s/%s at %s:%s" % (i.day, i.month, i.year, i.hour, i.minute)
    learn_data.append(
        {
            "name": "Build Information",
            "steps": [
                {
                    "stepId": "999999",
                    "text": info_text,
                    "firstImage": rows[0]["firstImageId"],
                    "lastImage": "",
                }
            ],
        }
    )

    for row in rows:
        # Update current objective
        if row["objective"]:
            cur_objective = row["objective"]
            learn_data.append({"name": cur_objective, "steps": []})
            test_data.append({"name": cur_objective, "steps": []})

        # Get all step text into 1 variable
        concat_text = row["text"]
        if "textBoxUpper" in row and row["textBoxUpper"]:
            concat_text += "\n\n" + row["textBoxUpper"]
        if "textBoxLower" in row and row["textBoxLower"]:
            concat_text += "\n\n" + row["textBoxLower"]
        if "moreInfo" in row and row["moreInfo"]:
            concat_text += "\n\n" + row["moreInfo"]
        concat_text = concat_text.replace("\\n", "\n")

        if not row["firstImageId"]:
            raise ValueError("Missing frame numbers in step {} of {}".format(row["stepId"], phase_code))

        # Add generic step data to dictionary
        learn_data[-1]["steps"].append(
            {
                "stepId": row["stepId"],
                "text": concat_text,
                "firstImage": row["firstImageId"],
                "lastImage": row["lastImageId"],
            }
        )

        if "interaction_sim2dData" in row and row["interaction_sim2dData"] and not row["interaction_sim2dData"] == "{}":
            interaction_data = json.loads(row["interaction_sim2dData"])
            if interaction_data["type"] == "dragger" and interaction_data["learn"]:
                learn_data[-1]["steps"][-1]["dragger"] = {
                    "start": [interaction_data["p1x"], interaction_data["p1y"]],
                    "target": [interaction_data["p2x"], interaction_data["p2y"]],
                }

            if interaction_data["type"] == "dirDrag":
                a = [interaction_data["p1x"], interaction_data["p1y"]]
                b = [interaction_data["p2x"], interaction_data["p2y"]]

                v1 = (0, 1)
                v2 = (a[0] - b[0], a[1] - b[1])

                v1_theta = math.atan2(v1[1], v1[0])
                v2_theta = math.atan2(v2[1], v2[0])

                # (round to fix yaml serialization error)
                angle = round((v2_theta - v1_theta) * (180.0 / math.pi))

                if angle < 0:
                    angle += 360.0

                # Calculate lengths between points
                # alpha = b[0] - a[0]
                # beta = b[1] - a[1]

                # Get distance between 2 points (round to fix yaml serialization error)
                # distance = round(math.hypot(alpha, beta), 2)
                distance = 60

                learn_data[-1]["steps"][-1]["dirDragger"] = {
                    "start": [interaction_data["p1x"], interaction_data["p1y"]],
                    "tolerance": 40,
                    "angle": angle,
                    "distance": distance,
                }

            if interaction_data["type"] == "tap":
                learn_data[-1]["steps"][-1]["tap"] = {
                    "target": [interaction_data["p1x"], interaction_data["p1y"]],
                }

            if interaction_data["type"] == "auto":
                learn_data[-1]["steps"][-1]["auto"] = {}

            if interaction_data["type"] == "hold":
                if "seconds" not in interaction_data:
                    interaction_data["seconds"] = 2

                if "start" not in interaction_data:
                    interaction_data["start"] = interaction_data["seconds"]

                if "finish" not in interaction_data:
                    interaction_data["finish"] = 0

                if "units" not in interaction_data:
                    interaction_data["units"] = "sec"

                learn_data[-1]["steps"][-1]["hold"] = {
                    "target": [interaction_data["p1x"], interaction_data["p1y"]],
                    "duration": int(interaction_data["seconds"]) * 1000,
                    "start": interaction_data["start"],
                    "finish": interaction_data["finish"],
                    "units": interaction_data["units"],
                }

        # Add other sim2d data, infoPoints, labels and pips
        if "infoPoints_sim2dData" in row and row["infoPoints_sim2dData"] and not row["infoPoints_sim2dData"] == "{}":
            info_point_data = json.loads(row["infoPoints_sim2dData"])
            data = {}
            for i, info_point in enumerate(info_point_data):
                data[i] = {
                    "text": info_point_data[info_point]["text"],
                    "targetPosition": info_point_data[info_point]["targetPosition"],
                    "moreInfoId": info_point_data[info_point]["moreInfoId"],
                }
            learn_data[-1]["steps"][-1]["infoPoints"] = info_point_data
        if "pip_sim2dData" in row and row["pip_sim2dData"] and not row["pip_sim2dData"] == "{}":
            pip_data = json.loads(row["pip_sim2dData"])

            # Set the first letter of position to be lower case
            position = pip_data["position"][0].lower() + pip_data["position"][1:]
            if position == "midLeft":
                position = "middleLeft"
            elif position == "midRight":
                position = "middleRight"

            learn_data[-1]["steps"][-1]["pip"] = {
                "position": position,
                "expandable": pip_data["expandable"],
                "shrinkable": pip_data["expandable"],
                "view": pip_data["view"],
                "sequence": pip_data["sequence"],
            }
            if pip_data["sequence"]:
                learn_data[-1]["steps"][-1]["pip"]["video"] = ""

        if "labels_sim2dData" in row and row["labels_sim2dData"] and not row["labels_sim2dData"] == "{}":
            label_data = json.loads(row["labels_sim2dData"])
            data = {}
            for i, label in enumerate(label_data):
                if not label_data[label]["textPosition"]:
                    raise ValueError(
                        "Invalid text position for label on step {} of {}".format(row["stepId"], phase_code)
                    )

                data[i] = {
                    "text": label_data[label]["text"],
                    "textPosition": label_data[label]["textPosition"],
                    "targetPosition": label_data[label]["targetPosition"],
                    "moreInfoId": label_data[label]["moreInfoId"],
                }
            learn_data[-1]["steps"][-1]["labels"] = data

        if "gallery_sim2dData" in row and row["gallery_sim2dData"] and not row["gallery_sim2dData"] == "{}":
            video_ext = [".mp4"]
            img_ext = [".jpg", ".png"]

            gallery_data = json.loads(row["gallery_sim2dData"])
            data = {}

            for i, gallery_item in enumerate(gallery_data):

                main_filepath = gallery_data[str(i)]["mainGraphic"].replace("\\", "/")
                main_file = os.path.splitext(os.path.basename(main_filepath))
                if not main_file:
                    raise ValueError(
                        "Gallery item is missing Main Graphic on step {} of {}".format(row["stepId"], phase_code)
                    )
                thumb_filepath = gallery_data[str(i)]["thumbnail"].replace("\\", "/")
                thumb_file = os.path.splitext(os.path.basename(thumb_filepath))
                if not thumb_file:
                    raise ValueError(
                        "Gallery item is missing Thumbnail on step {} of {}".format(row["stepId"], phase_code)
                    )

                if main_file[1] in video_ext:
                    file_type = "video"
                elif main_file[1] in img_ext:
                    file_type = "image"
                else:
                    raise TypeError(
                        "Unable to create gallery item for step {} of {} \n"
                        "Unrecognised file type: {}{}".format(row["stepId"], phase_code, main_file[0], main_file[1])
                    )

                data[i] = {
                    "title": gallery_data[str(i)]["title"],
                    "text": gallery_data[str(i)]["text"],
                    "type": file_type,
                    "mainFile": main_file[0],
                    "thumbFile": thumb_file[0],
                }

            learn_data[-1]["steps"][-1]["gallery"] = data

        if "flipbook_sim2dData" in row and row["flipbook_sim2dData"] and not row["flipbook_sim2dData"] == "{}":
            flip_book_data = json.loads(row["flipbook_sim2dData"])

            video_filepath = flip_book_data["videoName"].replace("\\", "/")
            video_file = os.path.splitext(os.path.basename(video_filepath))
            if not video_file:
                raise ValueError("Video file missing from flipbook in step {} of {}".format(row["stepId"], phase_code))

            image_filepath = flip_book_data["imageName"].replace("\\", "/")
            image_file = os.path.splitext(os.path.basename(image_filepath))
            if not image_file:
                raise ValueError("Image file missing from flipbook in step {} of {}".format(row["stepId"], phase_code))

            learn_data[-1]["steps"][-1]["flipbook"] = {
                "image": image_file[0],
                "video": video_file[0],
                "scrubberPos": flip_book_data["scrubberPos"],
            }

        # Store list of information cards needed
        if "moreInfoId" in row and row["moreInfoId"]:
            learn_data[-1]["steps"][-1]["moreInfoId"] = row["moreInfoId"]
            if "moreInfoLabel" in row:
                learn_data[-1]["steps"][-1]["moreInfoLabel"] = row["moreInfoLabel"]

        if not row["testable"].lower() == "false":
            mcq_exists = False

            test_data[-1]["steps"].append(
                {
                    "stepId": row["stepId"],
                    "testText": row["testText"],
                    "firstImage": row["firstImageId"],
                    "lastImage": row["lastImageId"],
                }
            )

            if "testFirstImageId" in row and row["testFirstImageId"]:
                test_data[-1]["steps"][-1]["testFirstImage"] = row["testFirstImageId"]

            if "testLastImageId" in row and row["testLastImageId"]:
                test_data[-1]["steps"][-1]["testLastImage"] = row["testLastImageId"]

            if row["testText"]:
                choice_list = []
                if row["choice2"]:
                    choice_list.append(row["choice2"])
                if row["choice3"]:
                    choice_list.append(row["choice3"])
                if row["choice4"]:
                    choice_list.append(row["choice4"])

                if row["choiceCorrect"]:
                    mcq_exists = True
                    test_data[-1]["steps"][-1]["correctChoice"] = row["choiceCorrect"]
                    test_data[-1]["steps"][-1]["incorrectChoices"] = choice_list

            if (
                "interaction_sim2dData" in row
                and row["interaction_sim2dData"]
                and not row["interaction_sim2dData"] == "{}"
            ):
                if interaction_data["type"] == "dragger" and interaction_data["test"]:
                    if mcq_exists:
                        # Set MCQ last frame to be empty to allow for question dragger combo
                        test_data[-1]["steps"][-1]["lastImage"] = ""
                        test_data[-1]["steps"][-1].pop("testLastImage", None)

                        test_data[-1]["steps"].append(
                            {
                                "stepId": row["stepId"] + "_d",
                                "testText": row["testText"],
                                "firstImage": row["firstImageId"],
                                "lastImage": row["lastImageId"],
                            }
                        )

                        if "testFirstImageId" in row and row["testFirstImageId"]:
                            test_data[-1]["steps"][-1]["testFirstImage"] = row["testFirstImageId"]

                        if "testLastImageId" in row and row["testLastImageId"]:
                            test_data[-1]["steps"][-1]["testLastImage"] = row["testLastImageId"]

                    test_data[-1]["steps"][-1]["testDragger"] = {
                        "start": [interaction_data["p1x"], interaction_data["p1y"]],
                        "target": [interaction_data["p2x"], interaction_data["p2y"]],
                    }

    return learn_data, test_data


def get_csv_info(phase_code, csv_version):
    if os.path.isdir(settings.BASE_DATA_DIR):
        csv_file = get_csv_steps_file(phase_code, csv_version)
    else:
        procedure_code = get_procedure_code()
        csv_file = os.path.join(
            settings.PROCEDURE_CHECKOUT_DIRECTORY, procedure_code, "build_assets", "csv", "%s.csv" % phase_code
        )

    if csv_file:
        headers, rows = read_csv_file(str(csv_file))
    else:
        raise ContentMissingError("No csv could be found for phase: %s" % phase_code)

    return headers, rows
