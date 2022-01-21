import cv2
import csv
import os
from matplotlib import cm
from vhh_od.Video import Video
from vhh_od.utils import *
import yaml

def drawBBox(image, bbox, parameters, tracked):
    obj_id = int(bbox[0])
    x1 = int(bbox[1])
    x2 = int(bbox[3])
    y1 = int(bbox[2])
    y2 = int(bbox[4])

    if tracked:
        color_idx = obj_id % parameters["num_colors"]
        color = parameters["color_map"](color_idx)[0:3]
        color = tuple([int(color[i] * 255) for i in range(len(color))])
    else:
        color = parameters["const_color"]

    class_name = bbox[5]
    if tracked:
        label = f"{class_name} {obj_id}"
    else:
        label = class_name
    font = parameters["font"]
    font_size = parameters["font_size"]
    font_thickness = parameters["font_thickness"]
    text_size = cv2.getTextSize(label, font, font_size, font_thickness)[0]

    # draw bounding box
    cv2.rectangle(image, (x1, y1), (x2, y2), color, 5)

    # draw text and background
    cv2.rectangle(image, (x1, y1), (x1 + text_size[0] + 3, y1 + text_size[1] + 4), color, -1)
    cv2.putText(image, label, (x1, y1 + text_size[1]), font, font_size, [0, 0, 0], font_thickness)

def visualize_video(video: Video, full_csv_path, out_path):

    csv_file = open(full_csv_path, "r")
    annotations = csv.reader(csv_file, delimiter=",")

    # Skip header
    next(annotations, None) 

    vid_id = video.vidName.split('.')[0]
    vid_format = video.vidName.split('.')[1]

    printCustom(f"Visualizing Annotations for Video {vid_id}.{vid_format} from {full_csv_path}", type=STDOUT_TYPE.INFO)

    try:
        annotation = next(annotations)
        annotation_available = True
    except StopIteration:
        annotation_available = False

    if annotation_available == False:
        printCustom(f"CSV-File seems to be empty", STDOUT_TYPE.ERROR)
        return
    elif annotation[0] != f"{vid_id}.{vid_format}":
        printCustom(f"CSV-File does not seem to match Video", STDOUT_TYPE.ERROR)
        return

    # TODO: at the moment, missing confidence values indicate tracking. Maybe use file naming convention instead.
    if annotation[10] == "N/A":
        tracked = True
    else:
        tracked = False
    printCustom(f"Visualizing Tracked Results: {tracked}", STDOUT_TYPE.INFO)

    # Loading Parameters from Config
    config_file = "./config/vis_config.yaml"
    fp = open(config_file, 'r')
    config = yaml.load(fp, Loader=yaml.BaseLoader)

    if tracked:
        num_colors = int(config["NUM_COLORS"])
        color_map = cm.get_cmap(config["COLORMAP"], num_colors)
        const_color = None
    else:
        num_colors = None
        color_map = None
        const_color = config["CONST_COLOR"].split(',')
        const_color = tuple([int(const_color[i]) for i in range(len(const_color))])

    parameters = {"num_colors": num_colors,
                  "color_map": color_map,
                  "const_color": const_color,
                  "font": cv2.FONT_HERSHEY_SIMPLEX,
                  "font_size": float(config["FONT_SIZE"]),
                  "font_thickness": int(config["FONT_THICKNESS"]),
                  "result_path": os.path.join(out_path, f"{video.vidName.split('.')[0]}_results.avi")}

    print(parameters)

    frame_idx = 0
    video_writer = None

    for frame in video.loadVideoByFrame():
        image = frame["Images"]

        if video_writer is None:
            frame_size = (image.shape[1], image.shape[0])
            print(frame_size)
            video_writer = cv2.VideoWriter(parameters["result_path"], cv2.VideoWriter_fourcc(*"MJPG"), 12, frame_size)
            printCustom(f"Writing Video to {parameters['result_path']}", STDOUT_TYPE.INFO)

        # draw all available bounding boxes onto frame
        while annotation_available and int(annotation[4]) == frame_idx:
            annotation = np.array(annotation)
            drawBBox(image, annotation[[5,6,7,8,9,12]], parameters, tracked)
            try:
                annotation = next(annotations)
            except StopIteration:
                annotation_available = False

        video_writer.write(image)

        frame_idx += 1
    video_writer.release()
    printCustom(f"Visualization done. Wrote {frame_idx} frames to \"{parameters['result_path']}", STDOUT_TYPE.INFO)
