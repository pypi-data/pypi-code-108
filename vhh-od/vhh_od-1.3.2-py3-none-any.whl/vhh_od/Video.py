import numpy as np
import cv2
import datetime
from vhh_od.utils import *
from vhh_od.Shot import Shot
from PIL import Image
import torchvision


class Video(object):
    """
    This class is representing a video. Each instance of this class is holding the properties of one Video.
    """

    def __init__(self):
        """
        Constructor
        """

        #printCustom("create instance of video class ... ", STDOUT_TYPE.INFO);
        self.vidFile = ''
        self.vidName = ""
        self.frame_rate = 10
        self.channels = 0
        self.height = 0
        self.width = 0
        self.format = ''
        self.length = 0
        self.number_of_frames = 0
        self.vid = None
        self.convert_to_gray = False
        self.convert_to_hsv = False
        self.shot_list = []

    def addShotObject(self, shot_obj: Shot):
        self.shot_list.append(shot_obj)

    def load(self, vidFile: str):
        """
        Method to load video file.

        :param vidFile: [required] string representing path to video file
        """

        #print(vidFile)
        printCustom(f"Loading Video \"{vidFile}\"... ", STDOUT_TYPE.INFO)
        self.vidFile = vidFile
        if(self.vidFile == ""):
            #print("A")
            print("ERROR: you must add a video file path!")
            exit(1)
        self.vidName = self.vidFile.split('/')[-1]
        self.vid = cv2.VideoCapture(self.vidFile)

        if(self.vid.isOpened() == False):
            #print("B")
            print(f"ERROR: not able to open video file \"{vidFile}\"!")
            exit(1)

        status, frm = self.vid.read()

        self.channels = frm.shape[2]
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.frame_rate = self.vid.get(cv2.CAP_PROP_FPS)
        self.format = self.vid.get(cv2.CAP_PROP_FORMAT)
        self.number_of_frames = self.vid.get(cv2.CAP_PROP_FRAME_COUNT)

        self.vid.release()

    def printVIDInfo(self):
        """
        Method to a print summary of video properties.
        """

        print("---------------------------------")
        print("Video information")
        print("filename: " + str(self.vidFile))
        print("format: " + str(self.format))
        print("fps: " + str(self.frame_rate))
        print("channels: " + str(self.channels))
        print("width: " + str(self.width))
        print("height: " + str(self.height))
        print("nFrames: " + str(self.number_of_frames))
        print("---------------------------------")
        print("<<< Shot list >>>")
        for shot in self.shot_list:
            shot.printShotInfo()

    def getAllFrames(self, preprocess_pytorch=None):
        # read all frames of video
        cap = cv2.VideoCapture(self.vidFile)

        frame_l = []
        frames_orig = []

        cnt = 0
        while (True):
            cnt = cnt + 1
            ret, frame_orig = cap.read()

            # print(cnt)
            # print(ret)
            # print(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if (ret == True):
                if(preprocess_pytorch is not None):
                    frame = preprocess_pytorch(frame_orig)
                frame_l.append(frame)  # .transpose((2,0,1)

                # Deep Sort Tracker needs original image in RGB Space
                frames_orig.append(cv2.cvtColor(frame_orig, cv2.COLOR_BGR2RGB))
            else:
                break
        cap.release()

        if (preprocess_pytorch is not None):
            all_tensors_l = torch.stack(frame_l)
            return {"Tensors": all_tensors_l, "Images" : frames_orig}

    # generator for loading Video Frame by Frame
    def loadVideoByFrame(self, preprocess_pytorch=None):

        cap = cv2.VideoCapture(self.vidFile)

        cnt = 0
        while (True):
            cnt = cnt + 1
            ret, frame_orig = cap.read()

            if (ret == True):
                if(preprocess_pytorch is not None):
                    frame_processed = preprocess_pytorch(frame_orig)
                else:
                    frame_processed = None
                frame_orig = cv2.cvtColor(frame_orig, cv2.COLOR_BGR2RGB)
                yield {"Tensors": frame_processed, "Images" : frame_orig}
            else:
                break
        cap.release()

    def getFrame(self, frame_id):
        """
        Method to get one frame of a video on a specified position.

        :param frame_id: [required] integer value with valid frame index
        :return: numpy frame (WxHx3)
        """

        self.vid.open(self.vidFile)
        if(frame_id >= self.number_of_frames):
            print("ERROR: frame idx out of range!")
            return []

        #print("Read frame with id: " + str(frame_id));
        time_stamp_start = datetime.datetime.now().timestamp()

        self.vid.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
        status, frame_np = self.vid.read()
        self.vid.release()

        if(status == True):
            if(self.convert_to_gray == True):
                frame_np = cv2.cvtColor(frame_np, cv2.COLOR_BGR2GRAY)
                #print(frame_gray_np.shape);
            if (self.convert_to_hsv == True):
                frame_np = cv2.cvtColor(frame_np, cv2.COLOR_BGR2HSV)
                h, s, v = cv2.split(frame_np)

        time_stamp_end = datetime.datetime.now().timestamp()
        time_diff = time_stamp_end - time_stamp_start
        #print("time: " + str(round(time_diff, 4)) + " sec")

        return frame_np

    def getFramesByShots_NEW(self, preprocess_pytorch=None, max_frames_per_return  = 2000):
        """
        Returns Video Shot by Shot
        If a single shot is longer than X frames, it will split the shot into frames of length at most X. 
        """
        # initialize video capture
        cap = cv2.VideoCapture(self.vidFile)

        frame_number = 0
        for shot in self.shot_list:

            frame_l = []
            frames_orig = []

            sid = int(shot.sid)
            start_idx = int(shot.start_pos)
            stop_idx = int(shot.end_pos)
            shot_is_not_over = True

            while shot_is_not_over:
                # print(f"Retrieving Frames for Shot {sid} (frames {frame_number} to {stop_idx})...")
                while frame_number < stop_idx and len(frame_l) < max_frames_per_return:
                    
                    # read next frame
                    success, image = cap.read()
                    frame_number = frame_number + 1
                    #print(frame_number)

                    # if(start_idx == stop_idx):
                    #    cv2.imshow("frame", image)
                    #    k = cv2.waitKey()

                    # skip to start position (for gradual cuts)
                    if frame_number < start_idx:
                        # print(frame_number)
                        continue

                    if success == True:
                        # if ( (frame_number >= start_idx and frame_number <= stop_idx) or (start_idx == stop_idx) ):
                        if (preprocess_pytorch != None):
                            frames_orig.append(image)
                            image = preprocess_pytorch(image)
                            frame_l.append(image)
                        else:
                            frames_orig.append(image)
                    else:
                        break

                if frame_l != [] and preprocess_pytorch is not None:
                    all_tensors_l = torch.stack(frame_l)
                    yield {"Tensors": all_tensors_l, "Images": np.array(frames_orig), "ShotInfo": shot}
                else:
                    yield {"Tensors": None, "Images": np.array(frames_orig), "ShotInfo": shot}

                # End the shot if the current frame is the last frame (or an even later frame)
                if not frame_number < stop_idx:
                    shot_is_not_over = False
                # If the shot is not over, prepare to return more frames in this shot   
                else:
                    frame_l = []
                    frames_orig = []

        cap.release()

    # Returns Video Shot by Shot
    def getFramesByShots(self, preprocess_pytorch=None):
        # initialize video capture
        cap = cv2.VideoCapture(self.vidFile)
        cnt = 0

        for shot in self.shot_list:

            frame_l = []
            frames_orig = []
            start_pos = shot.start_pos
            end_pos = shot.end_pos

            #print(f"Retrieving Frames for Shot {shot.sid} (frames {cnt} to {end_pos})...")

            while cnt <= end_pos:
                cnt = cnt + 1
                ret, frame_orig = cap.read()

                # skip to start position (for gradual cuts)
                if cnt < start_pos:
                    continue

                if ret == True:
                    if preprocess_pytorch is not None:
                        frame = preprocess_pytorch(frame_orig)
                        frame_l.append(frame)

                    # Deep Sort Tracker needs original image in RGB Space
                    frames_orig.append(cv2.cvtColor(frame_orig, cv2.COLOR_BGR2RGB))
                else:
                    break

            if preprocess_pytorch is not None:
                all_tensors_l = torch.stack(frame_l)
                yield {"Tensors": all_tensors_l, "Images": frames_orig, "ShotInfo": shot}
            else:
                yield {"Tensors": None, "Images": frames_orig, "ShotInfo": shot}

        cap.release()

    def getShotFromID(self, sid=-1):
        for shot in self.shot_list:
            if(shot.sid == sid):
                return shot
        return None

    def export2csv(self, filepath=None):

        printCustom(f"Exporting results to CSV \"{filepath}\'", type=STDOUT_TYPE.INFO)

        if(filepath == None):
            print("ERROR: You have to specify a vailid path! csv export aborted!")
            exit()

        ## clean up
        remove_csv_export(filepath)

        ## export
        field_names = ['movie_name', 'sid', 'start', 'stop', 'fid', 'oid', 'bb_x1', 'bb_y1', 'bb_x2', 'bb_y2',
                       'object_conf', 'class_score', 'class_name']

        add_header(filepath, field_names)
        for shot in self.shot_list:
            dict_l = shot.convertObjectList2Dict()
            for dict_entry in dict_l:
                append_dict_as_row(filepath, dict_entry, field_names)

    def loadCsvExport(self, filepath="/data/share/maxrecall_vhh_mmsi/develop/videos/results/vhh_od/raw_results/test.csv"):
        print("load csv results export ... ")

        field_names =  ['movie_name', 'sid', 'start', 'stop', 'fid', 'oid', 'bb_x1', 'bb_y1', 'bb_x2', 'bb_y2',
                       'object_conf', 'class_score', 'class_name']

        dict_l = load_csv_as_dict(file_name=filepath, field_names=field_names)
        print(dict_l)

        self.shot_list = []

    def visualizeShotsWithBB(self, path=None, sid=-1, all_frames_tensors=None, boundingbox_flag=True,
               save_single_plots_flag=True, plot_flag=False, save_as_video_flag=True):
        #print("plot shot with bounding boxes ... ")

        if(path == None):
            print("Error: you need to specify a valid path!")
            exit()

        shot = self.getShotFromID(sid=sid)
        if(shot == None):
            print("ERROR: shot with specified ID [" + str(sid) + "] is not available!")
            return -1

        shot_frames_tensors = all_frames_tensors[shot.start_pos:shot.end_pos+1, :, :, :]
        frameSize = (int(shot_frames_tensors[0].size()[1]), int(shot_frames_tensors[0].size()[2]))

        video_results_path = path + str(self.vidName.split('.')[0]) + "/"

        if not os.path.exists(video_results_path):
            os.makedirs(video_results_path)

        if (save_single_plots_flag == True):
            if not os.path.exists(video_results_path + str(sid)):
                os.makedirs(video_results_path + str(sid))

        if (save_as_video_flag == True):
            out = cv2.VideoWriter(video_results_path + str(sid) + ".avi", cv2.VideoWriter_fourcc(*"MJPG"), 12, frameSize)

        for i in range(0, len(shot_frames_tensors)):
            frame_id = i + shot.start_pos

            frame = shot_frames_tensors[i]
            frame_np = np.array(frame).transpose((1, 2, 0))
            normalized_frame = frame_np.copy()
            normalized_frame = cv2.normalize(frame_np, normalized_frame, 0, 255, cv2.NORM_MINMAX)
            normalized_frame = normalized_frame.astype('uint8')

            if (boundingbox_flag == True):
                for obj in shot.object_list:
                    if (frame_id == obj.fid):
                        cv2.rectangle(normalized_frame,  (obj.bb_x1, obj.bb_y1),  (obj.bb_x2, obj.bb_y2), (0, 255, 0), 1)
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        bottomLeftCornerOfText = (int(obj.bb_x1), int(obj.bb_y1) - 3)
                        fontScale = 0.4
                        fontColor = (0, 255, 0, 255)
                        thickness = 1
                        line_type = cv2.LINE_AA
                        obj_text = str(obj.object_class_name) + ": " + str(round(obj.object_conf, 2))
                        cv2.putText(normalized_frame,
                                    obj_text,
                                    bottomLeftCornerOfText,
                                    font,
                                    fontScale,
                                    fontColor,
                                    thickness,
                                    line_type)

            if (save_as_video_flag == True):
                out.write(normalized_frame)

            if (save_single_plots_flag == True):
                cv2.imwrite(video_results_path + str(sid) + "/" + str(frame_id) + ".png", normalized_frame)

            if (plot_flag == True):
                cv2.imshow("Shot ID:" + str(sid), normalized_frame)
                cv2.waitKey(10)

        if (save_as_video_flag == True):
            out.release()

        if (plot_flag == True):
            cv2.destroyAllWindows()

