from vhh_od.Configuration import Configuration
from vhh_od.Video import Video
from vhh_od.Models import *
from vhh_od.utils import *
from vhh_od.Shot import Shot
from vhh_od.CustObject import CustObject
from vhh_od.visualize import visualize_video
import vhh_od.helpers as Helpers
import vhh_od.Classifier as Classifier
from deep_sort.deep_sort import DeepSort

import numpy as np
import os, sys
import cv2
from matplotlib import cm
import torch
from torch.autograd import Variable
from torch.utils import data
from torchvision import transforms
from collections import namedtuple

Detection_Data = namedtuple('Detection_Data', 'x1 x2 y1 y2 ids obj_class obj_conf class_conf num_results')

class OD(object):
    """
        Main class of shot type classification (stc) package.
    """

    def __init__(self, config_file: str):
        """
        Constructor

        :param config_file: [required] path to configuration file (e.g. PATH_TO/config.yaml)
                                       must be with extension ".yaml"
        """

        if (config_file == ""):
            printCustom("No configuration file specified!", STDOUT_TYPE.ERROR)
            exit()

        self.config_instance = Configuration(config_file)
        self.config_instance.loadConfig()

        if (self.config_instance.debug_flag == True):
            print("DEBUG MODE activated!")
            self.debug_results = "/data/share/maxrecall_vhh_mmsi/develop/videos/results/vhh_od/develop/"

        # prepare object detection model
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.use_tracker = self.config_instance.use_deepsort

        if self.use_tracker:
            printCustom(f"Initializing Deep Sort Tracker...", STDOUT_TYPE.INFO)
            ds_model_path = self.config_instance.ds_model_path
            ds_max_dist = self.config_instance.ds_max_dist
            ds_min_conf = self.config_instance.ds_min_conf
            ds_nms_max_overlap = self.config_instance.ds_nms_max_overlap
            ds_max_iou_dist = self.config_instance.ds_max_iou_dist
            ds_max_age = self.config_instance.ds_max_age
            ds_num_init = self.config_instance.ds_num_init
            use_cuda = (self.device == "cuda")

            self.tracker = DeepSort(ds_model_path, ds_max_dist, ds_min_conf, ds_nms_max_overlap, ds_max_iou_dist, ds_max_age,
                               ds_num_init, use_cuda=torch.cuda.is_available())
            printCustom(f"Deep Sort Tracker initialized successfully!", STDOUT_TYPE.INFO)

        self.num_colors = 10
        self.color_map = cm.get_cmap('gist_rainbow', self.num_colors)

    def iterate_over_images(self, image_files_full_path):
        """
        Iterates over a given list of images applying the object
        detection to each frame. In each iteration it returns one crop.
        """
        self.advanced_init()
        for a, image_file in enumerate(image_files_full_path):
            print("Processed {0} / {1} images".format(a, len(image_files_full_path)), end ="\r")

            img = cv2.imread(image_file)
            img_orig = img

            tensors = torch.unsqueeze(self.preprocess(img), dim = 0)

            predictions_l = self.runModel(model=self.model, tensor_l=tensors, classes=self.classes, class_filter=self.class_selection)
            frame_based_predictions = predictions_l[0]

            # No predictions means no boundary boxes
            if frame_based_predictions is None:
                continue

            im, x, y, w, h = self.rescale_bb(img_orig, frame_based_predictions)
            detection_data = self.detection_data_without_tracking_to_custom_obj(0, x, y, w, h, frame_based_predictions)

            # Switch color channels 
            im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)

            if len(frame_based_predictions) > 0:
                for i, data in enumerate(detection_data):
                    crop_img = im[data.bb_y1:data.bb_y2, data.bb_x1:data.bb_x2]

                    # Sometimes OD predicts boundary boxes with coordinates < 0, cannot crop those so ignore them
                    if(data.bb_y1 < 0) or (data.bb_y2 < 0) or (data.bb_x1 < 0) or (data.bb_x2 < 0):
                        continue

                    name_crop_img = data.object_class_name + "_" + str(a) + "_" + str(data.oid) + ".png"
                    
                    yield {
                        "cropped_img": crop_img,
                        "class": data.object_class_name,
                        "name": name_crop_img,
                        "image_file": image_file,
                        "x1": str(data.bb_x1),
                        "x2": str(data.bb_x2),
                        "y1": str(data.bb_y1),
                        "y2": str(data.bb_y2),
                    } 

    def advanced_init(self):
        """"
        Creates and loads weight into the mode, loads classes, loads resized dims, and creates preprocess object
        """

        printCustom(f"Initializing Model using \"{self.config_instance.model_config_path}\"...", STDOUT_TYPE.INFO)
        self.model = Darknet(config_path=self.config_instance.model_config_path,
                        img_size=self.config_instance.resize_dim).to(self.device)

        printCustom(f"Loading Weights from \"{self.config_instance.path_pre_trained_model}\"...", STDOUT_TYPE.INFO)
        if self.config_instance.path_pre_trained_model.endswith(".weights"):
            # Load darknet weights
            self.model.load_darknet_weights(self.config_instance.path_pre_trained_model)
        else:
            # Load checkpoint weights
            self.model.load_state_dict(torch.load(self.config_instance.path_pre_trained_model))

        printCustom(f"Loading Class Names from \"{self.config_instance.model_class_names_path}\"... ", STDOUT_TYPE.INFO)
        self.classes = load_classes(self.config_instance.model_class_names_path)

        printCustom(f"Loading Class Selection from \"{self.config_instance.model_class_selection_path}\"... ", STDOUT_TYPE.INFO)
        self.class_selection = load_classes(self.config_instance.model_class_selection_path)
        printCustom(f"Classes of interest: {self.class_selection}", STDOUT_TYPE.INFO)

        # prepare transformation for vhh_od model
        self.preprocess = transforms.Compose([
            transforms.ToPILImage(),
            # transforms.Resize((int(vid_instance.height), vid_instance.width)),
            # transforms.CenterCrop((int(vid_instance.height), int(vid_instance.height))),
            transforms.Resize(self.config_instance.resize_dim),
            # ToGrayScale(),
            transforms.ToTensor()
            # transforms.Normalize((self.config_instance.mean_values[0] / 255.0,
            #                      self.config_instance.mean_values[1] / 255.0,
            #                      self.config_instance.mean_values[2] / 255.0),
            #                     (self.config_instance.std_dev[0] / 255.0,
            #                      self.config_instance.std_dev[1] / 255.0,
            #                      self.config_instance.std_dev[2] / 255.0))
        ])

        self.resized_dim_y = self.config_instance.resize_dim[0]
        self.resized_dim_x = self.config_instance.resize_dim[1]

        if self.config_instance.use_classifier:
            self.classifier = Classifier.Classifier(self.config_instance.classifier_model_architecture, self.config_instance.classifier_model_path, self.device)


    def detection_data_with_tracking_to_custom_obj(self, frame_id, tracking_results):
        """
        Takes prediction data and outputs the detection data as a list of "CustObject"s
        Use this if you are using a tracker
        """
        x1_list = tracking_results[:,0]
        x2_list = tracking_results[:,2]
        y1_list = tracking_results[:,1]
        y2_list = tracking_results[:,3]
        ids = tracking_results[:,4]
        object_classes = tracking_results[:,5]
        object_confs = None
        class_confs = None
        num_results = len(tracking_results)

        data = Detection_Data(x1_list, x2_list, y1_list, y2_list, ids, object_classes, object_confs, class_confs, num_results)
        return self.detection_data_to_custom_obj(data, frame_id)

    def detection_data_without_tracking_to_custom_obj(self, frame_id, x, y, w, h, frame_based_predictions):
        """
        Takes prediction data and outputs the detection data as a list of "CustObject"s
        Use this if you are NOT using a tracker
        """
        x1_list = x
        x2_list = x + w
        y1_list = y
        y2_list = y + h
        ids = None
        object_confs = frame_based_predictions[:,4].cpu().numpy()
        class_confs = frame_based_predictions[:,5].cpu().numpy()
        object_classes = frame_based_predictions[:, 6].cpu().numpy()
        num_results = len(frame_based_predictions)
        data = Detection_Data(x1_list, x2_list, y1_list, y2_list, ids, object_classes, object_confs, class_confs, num_results)
        return self.detection_data_to_custom_obj(data, frame_id)


    def detection_data_to_custom_obj(self, data, frame_id):
        """
        Takes a the detection data in the format of a "Detection_Data" named tuple, outputs a list of "CustObject"s
        """
        obj_id = 0
        cust_object_list = []
        for object_idx in range(data.num_results):
            x1 = int(data.x1[object_idx])
            x2 = int(data.x2[object_idx])
            y1 = int(data.y1[object_idx])
            y2 = int(data.y2[object_idx])

            if data.ids is None:
                instance_id = obj_id
                obj_id = obj_id + 1
            else:
                instance_id = data.ids[object_idx]

            if data.obj_conf is None:
                obj_conf = "N/A"
            else:
                obj_conf = data.obj_conf[object_idx]

            if data.class_conf is None:
                class_conf = "N/A"
            else:
                class_conf = data.class_conf[object_idx]

            class_idx = int(data.obj_class[object_idx])
            class_name = self.classes[class_idx]

            obj_instance = CustObject(oid=instance_id,
                                        fid=frame_id,
                                        object_class_name=class_name,
                                        object_class_idx=class_idx, 
                                        object_conf=obj_conf,
                                        class_score=class_conf,
                                        bb_x1=x1,
                                        bb_y1=y1,
                                        bb_x2=x2,
                                        bb_y2=y2
                                        )
            cust_object_list.append(obj_instance)
        return cust_object_list

    def rescale_bb(self, image_orig, frame_based_predictions):
        """
        Rescales bounding boxes to fit original video resolution
        """
        im = cv2.cvtColor(image_orig, cv2.COLOR_BGR2RGB)
        y_factor = im.shape[0] / self.resized_dim_y
        x_factor = im.shape[1] / self.resized_dim_x
        x = (frame_based_predictions[:, 0]).cpu().numpy() * x_factor
        y = (frame_based_predictions[:, 1]).cpu().numpy() * y_factor
        w = (frame_based_predictions[:, 2]).cpu().numpy() * x_factor - x
        h = (frame_based_predictions[:, 3]).cpu().numpy() * y_factor - y
        return im, x, y, w, h

    def apply_tracker(self, x, y, w, h, im, frame_id, new_custom_objects, frame_based_predictions, vis = False):
         # Convert BBoxes from XYXY (corner points) to XYWH (center + width/height) representation
        x = x+w/2
        y = y+h/2
        bbox_xywh = np.array([[x[i],y[i],w[i],h[i]] for i in range(len(frame_based_predictions))])

        # get class confidences
        cls_conf = frame_based_predictions[:, 5].cpu().numpy()
        class_predictions = frame_based_predictions[:, 6].cpu().numpy()

        # Track Objects using Deep Sort tracker
        # Tracker expects Input as XYWH but returns Boxes as XYXY
        tracking_results = np.array(self.tracker.update(bbox_xywh, cls_conf, class_predictions, im))
        num_results = len(tracking_results)

        if num_results > 0:
            detection_data = self.detection_data_with_tracking_to_custom_obj(frame_id, tracking_results)
        else:
            # Since we need to advance the framecounter of the classifier, we keep track of frames with no predictions
            new_custom_objects.append(None)
            detection_data = []

        if not vis:
            return detection_data

        # visualization
        num_colors = 10
        color_map = cm.get_cmap('gist_rainbow', num_colors)
        if len(tracking_results) > 0:
            for box in tracking_results:
                x1v = int(box[0])
                x2v = int(box[2])
                y1v = int(box[1])
                y2v = int(box[3])
                color_idx = box[4] % self.num_colors
                color = color_map(color_idx)[0:3]
                color = tuple([int(color[i] * 255) for i in range(len(color))])
                class_name = self.classes[int(box[5])]
                label = f"{class_name} {box[4]}"
                font_size = 0.5
                font_thickness = 1
                text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_size , font_thickness)[0]
                # draw bounding box
                im = cv2.rectangle(im, (x1v, y1v), (x2v, y2v), color, 5)
                # draw text and background
                cv2.rectangle(im, (x1v, y1v), (x1v + text_size[0] + 3, y1v + text_size[1] + 4), color, -1)
                cv2.putText(im, label, (x1v, y1v + text_size[1]), cv2.FONT_HERSHEY_SIMPLEX, font_size,
                            [0, 0, 0], font_thickness)
            cv2.imshow("im", im)
            cv2.waitKey()
        return detection_data

    def get_video_instance(self, shots_per_vid_np, max_recall_id):
        """
        Generate the video instance on which object detection will be run
        Also handles initialization and checking of parameters for runOnSingleVideo(...)
        """
        if (type(shots_per_vid_np) == None):
            print("ERROR: you have to set the parameter shots_per_vid_np!")
            exit()

        if (max_recall_id == -1 or max_recall_id == 0):
            print("ERROR: you have to set a valid max_recall_id [1-n]!")
            exit()

        if(self.config_instance.debug_flag == True):
            # load shot list from result file
            printCustom(f"Loading STC Results from \"{self.config_instance.path_stc_results}\"...", STDOUT_TYPE.INFO)
            shots_np = self.loadStcResults(self.config_instance.path_stc_results)
        else:
            shots_np = shots_per_vid_np

        if (len(shots_np) == 0):
            print("ERROR: there must be at least one shot in the list!")
            exit()

        if (self.config_instance.debug_flag == True):
            num_shots = 10
            offset = 0
        else:
            num_shots = len(shots_per_vid_np)
            offset = 0

        # Ensure tracker is empty
        if self.use_tracker:
            self.tracker.tracker.clear_id()
            self.tracker.reset()

        # load video instance
        vid_name = shots_np[0][0]
        vid_instance = Video()
        vid_instance.load(os.path.join(self.config_instance.path_videos, vid_name))

        # prepare numpy shot list
        shot_instance = None
        for s in range(offset, offset + num_shots):
            # print(shots_per_vid_np[s])

            # Do not use shots that have the wrong shot type
            if shots_per_vid_np[s][4] in self.config_instance.shot_types_do_not_run_od:
                continue

            shot_instance = Shot(sid=int(s + 1),
                                 movie_name=shots_per_vid_np[s][0],
                                 start_pos=int(shots_per_vid_np[s][2]),
                                 end_pos=int(shots_per_vid_np[s][3]))

            vid_instance.addShotObject(shot_obj=shot_instance)

        self.advanced_init()
        return vid_instance

    def process_predictions(self, predictions_l, images_orig, frame_id, results_od_l, new_custom_objects, current_shot):
        shot_id = int(current_shot.sid)
        vid_name = str(current_shot.movie_name)
        start = int(current_shot.start_pos)
        stop = int(current_shot.end_pos)

        # For each frame, track predictions and store results
        for a in range(0, len(predictions_l)):
            frame_id += 1
            frame_based_predictions = predictions_l[a]
            detection_data = []

        
            if (frame_based_predictions is None):
                results_od_l.append(["None", shot_id, vid_name, start, stop, frame_id,
                                        "None", "None", "None", "None", "None", "None", "None"])

                if (self.config_instance.debug_flag == True):
                    tmp = str(None) + ";" + str(shot_id) + ";" + str(vid_name) + ";" + str(start) + ";" + str(
                        stop) + ";" + str(frame_id) + ";" + str(None) + ";" + str(None) + ";" + str(
                        None) + ";" + str(None) + ";" + str(None) + ";" + str(None) + ";" + str(None)
                    print(tmp)

                # Since we need to advance the framecounter of the classifier, we keep track of frames with no predictions
                new_custom_objects.append(None)
                continue

            # rescale bounding boxes to fit original video resolution
            im, x, y, w, h = self.rescale_bb(images_orig[a], frame_based_predictions)

            if self.use_tracker:
                detection_data =  self.apply_tracker(x, y, w, h, im, frame_id, new_custom_objects, frame_based_predictions)
            else:
                # if no tracker is used, store the detection results
                detection_data = self.detection_data_without_tracking_to_custom_obj(frame_id, x, y, w, h, frame_based_predictions)

            # store predictions for each object in the frame
            for obj in detection_data:   
                results_od_l.append([obj.oid, shot_id, vid_name, start, stop, frame_id,
                                        obj.bb_x1, obj.bb_y1, obj.bb_x2, obj.bb_y2, obj.object_conf, obj.class_score, obj.object_class_idx])                     

                current_shot.addCustomObject(obj)


                if (self.config_instance.debug_flag == True):
                    print(obj.printObjectInfo())
            new_custom_objects += detection_data
        return frame_id

    def normalize_bb(self, bb_list, width, height):
        for obj in bb_list:
            obj.bb_x1 /= width
            obj.bb_x2 /= width
            obj.bb_y1 /= height
            obj.bb_y2 /= height

    def runOnSingleVideo(self, shots_per_vid_np=None, max_recall_id=-1):
        """
        Method to run stc classification on specified video.

        :param shots_per_vid_np: [required] numpy array representing all detected shots in a video
                                 (e.g. sid | movie_name | start | end )
        :param max_recall_id: [required] integer value holding unique video id from VHH MMSI system
        """
        print("run vhh_od detector on single video ... ")
        vid_instance = self.get_video_instance(shots_per_vid_np, max_recall_id)

        printCustom(f"Starting Object Detection (Executing on device {self.device})... ", STDOUT_TYPE.INFO)
        results_od_l = []
        previous_shot_id, frame_id = -1, -1
        
        height, width = None, None
        for shot_frames in vid_instance.getFramesByShots_NEW(preprocess_pytorch=self.preprocess, max_frames_per_return=self.config_instance.max_frames):
            shot_tensors, images_orig, current_shot = shot_frames["Tensors"], shot_frames["Images"], shot_frames["ShotInfo"]

            if height is None:
                height, width, _ = images_orig[0].shape

            shot_id, vid_name = int(current_shot.sid), str(current_shot.movie_name)
            start, stop = int(current_shot.start_pos), int(current_shot.end_pos)

            # Collect all custom objects so we can run the classifier on them
            new_custom_objects = []

            if shot_id != previous_shot_id:
                frame_id = start - 1

            # Only run the model if we actually have tensors
            if shot_tensors is None:
                previous_shot_id = shot_id
                continue

            print("{0} / {1} shots".format(shot_id, len(vid_instance.shot_list)), end="\r")

            if(self.config_instance.debug_flag == True):
                print("-----")
                print(f"Video Name: {vid_name}")
                print(f"Shot ID: {shot_id}")
                print(f"Start: {start} / Stop: {stop}")
                print(f"Duration: {stop - start} Frames")

            # Run vhh_od detector get predictions
            predictions_l = self.runModel(model=self.model, tensor_l=shot_tensors, classes=self.classes, class_filter=self.class_selection)

            # Reset tracker for every new shot
            if self.use_tracker and previous_shot_id != shot_id:
                self.tracker.reset()

            # Process Yolo's predictions and update: results_od_l, new_custom_objects, current_shot
            # This also runs the tracker
            frame_id = self.process_predictions(predictions_l, images_orig, frame_id, results_od_l, new_custom_objects, current_shot)

            # Use classifier on crops
            if self.config_instance.use_classifier:
                Classifier.run_classifier_on_list_of_custom_objects(self.classifier, new_custom_objects, shot_frames["Images"])

            # Add classifier results, do majority voting
            current_shot.update_obj_classifications(self.config_instance.use_classifier_majority_voting, self.config_instance.others_factor)

            # Normalize coordinates
            if self.config_instance.do_normalize_coordinates:
                self.normalize_bb(current_shot.object_list, width, height)

            previous_shot_id = shot_id
        
        if (self.config_instance.debug_flag):
            vid_instance.printVIDInfo()

        # Store results
        if (self.config_instance.save_final_results):
            results_path = Helpers.mkdir_if_necessary(self.config_instance.path_final_results)
            filepath = f"{results_path}{vid_name.split('.')[0]}.{self.config_instance.path_postfix_final_results}"
            vid_instance.export2csv(filepath=filepath)

            if (self.config_instance.save_raw_results):
                results_path = Helpers.mkdir_if_necessary(self.config_instance.path_raw_results)
                visualize_video(vid_instance, filepath, results_path)

                '''
                for shot in vid_instance.shot_list:
                    vid_instance.visualizeShotsWithBB(path=results_path,
                                                    sid=int(shot.sid),
                                                    all_frames_tensors=all_tensors_l,
                                                    save_single_plots_flag=True,
                                                    plot_flag=False,
                                                    boundingbox_flag=True,
                                                    save_as_video_flag=True
                                                    ) '''

    def runModel(self, model, tensor_l, classes, class_filter):
        """
        Method to calculate stc predictions of specified model and given list of tensor images (pytorch).

        :param model: [required] pytorch model instance
        :param tensor_l: [required] list of tensors representing a list of frames.
        :return: predicted class_name for each tensor frame,
                 the number of hits within a shot,
                 frame-based predictions for a whole shot
        """
        # run vhh_od detector

        # prepare pytorch dataloader
        Tensor = torch.cuda.FloatTensor if torch.cuda.is_available() else torch.FloatTensor
        dataset = data.TensorDataset(tensor_l)  # create your datset
        inference_dataloader = data.DataLoader(dataset=dataset,
                                               batch_size=self.config_instance.batch_size)

        predictions_l = []
        for i, inputs in enumerate(inference_dataloader):
            input_batch = inputs[0]
            input_batch = Variable(input_batch.type(Tensor))

            # move the input and model to GPU for speed if available
            if torch.cuda.is_available():
                input_batch = input_batch.to('cuda')
                model.to('cuda')

            model.eval()
            with torch.no_grad():
                output = model(input_batch)
                batch_detections = non_max_suppression(prediction=output,
                                                 conf_thres=self.config_instance.confidence_threshold,
                                                 nms_thres=self.config_instance.nms_threshold)

                for frame_detection in batch_detections:

                    filtered_detection = None

                    if frame_detection is not None:

                        for i in range(len(frame_detection)):

                            detected_object = frame_detection[i]
                            class_idx = detected_object[6].int().item()

                            if classes[class_idx] in class_filter:
                                if filtered_detection is None:
                                    filtered_detection = detected_object.unsqueeze(dim=0)
                                else:
                                    filtered_detection = torch.cat([filtered_detection, detected_object.unsqueeze(dim=0)], dim=0)

                    predictions_l.append(filtered_detection)

        return predictions_l

    def loadStcResults(self, stc_results_path):
        """
        Method for loading shot type classification results as numpy array
        :param stc_results_path: [required] path to results file of shot type classification module (vhh_stc)
        :return: numpy array holding list of detected shots and shot types.
        """

        # open sbd results
        fp = open(stc_results_path, 'r')
        lines = fp.readlines()
        lines = lines[1:]

        lines_n = []
        for i in range(0, len(lines)):
            line = lines[i].replace('\n', '')
            line_split = line.split(';')
            lines_n.append([line_split[0], line_split[1], line_split[2], line_split[3], line_split[4]])
        lines_np = np.array(lines_n)

        return lines_np
