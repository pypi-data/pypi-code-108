from vhh_od.OD import OD
import os
import sys
import argparse
from vhh_od.Configuration import Configuration
import numpy as np
import cv2

"""
This is file contains a class that can be used to run the object detector on a folder of frames.
Depending on the used parameters this will store the classified crops or can be used to assess the accuracy of the detector
"""

config_file = "./config/config_vhh_od.yaml"

def prepare_paths_list(path_list, n_imgs):
    """
    Selects n_imgs from the list and shuffles list
    """
    paths_chosen = []

    if n_imgs <= 0:
        paths_chosen = path_list

    while len(path_list) > 0 and n_imgs > 0:
        n_imgs -= 1
        i = np.random.randint(0, len(path_list))
        paths_chosen.append(path_list[i])
        del path_list[i]

    np.random.shuffle(paths_chosen)
    return paths_chosen

def store_crops(information, output_folder_path, crop_dict):
    """
    Stores crops and updates information string
    """
    folder_crop_img_path = os.path.join(output_folder_path, crop_dict["class"])
    if not os.path.isdir(folder_crop_img_path):
        os.mkdir(folder_crop_img_path)

    fullpath_crop_img = os.path.join(folder_crop_img_path, crop_dict["name"])
    cv2.imwrite(fullpath_crop_img, crop_dict["cropped_img"])

    information += ','.join([crop_dict["image_file"], crop_dict["name"], crop_dict["class"], crop_dict["x1"], crop_dict["x2"], crop_dict["y1"], crop_dict["y2"]])
    information += '\n'
    return information

def evaluate(crop_dict):
    """
    Opens a window and asks the user whether the classification is correct
    """

    # In case someone touches a wrong key, keep asking for annotations
    need_to_evaluate = True
    while(need_to_evaluate):
        print("\nClass: ", crop_dict["class"])
        sys.stdout.flush()
        cv2.imshow(crop_dict["class"], crop_dict["cropped_img"])
        k = cv2.waitKey(0)

        # There is a bug that waitKey() sometimes gets "ghost" keypresses, if such a keypress occurs call waitKey() again
        while k == 0:
            k = cv2.waitKey(0)

        cv2.destroyAllWindows()

        if k==27:       # Esc key to stop
            need_to_evaluate = False
            break
        elif k==49:     # Keyvalue for 1
            print("Selected: Classification is CORRECT.\n")
            return True
        elif k==48:     # Keyvalue for 0
            print("Selected: Classification is WRONG.\n")
            return False
        else:
            print("Neither 0 or 1 detected, please make sure to not use the numpad.")

def run_on_folder_return_crops(folder_path, output_folder_path):
    """
    Extracts the crops from each image in folder_path and stores them in output_folder_path
    """
    return runOnAllFramesInFolder(folder_path, output_folder_path, True, False)

def run_on_folder_evaluate_model(folder_path, n_imgs=-1, n_annotations=10):
    """
    Runs the object detector on folder_path, classifying at most n_imgs images and manually asks the user if n_annotations crops are correctly classified
    This is then used to compute the accuracy of the model
    If all images are supposed to be used then set n_imgs to <= 0
    """
    return runOnAllFramesInFolder(folder_path, "", False, True, n_imgs, n_annotations)
    
def runOnAllFramesInFolder(folder_path, output_folder_path, do_store_crops, do_evaluate_model, n_imgs=-1, n_annotations=10):
    """
    Runs object detector on images in folder path, at most n_imgs images will be processed
    If all images are supposed to be used then set n_imgs to <= 0
    If do_store_crops is true then the crops will be stored in output_folder_path
    If do_evaluate_model is true: user will be asked to  manually check if n_annotations crops are correctly classified
    This is then used to compute the accuracy of the model
    """

    np.random.seed(0)
    config_instance = Configuration(config_file)
    config_instance.loadConfig()
    od_instance = OD(config_file)

    nr_crops, nr_correct_crops, crops_evaluated = 0, 0, 0

    image_files = [os.path.join(folder_path, path) for path in os.listdir(folder_path)]
    image_files = prepare_paths_list(image_files, n_imgs)
    
    print("Press 1 if the crop and class is correct, 0 if it is wrong. Do not use the numpad. Use escape to quit.")

    # Text for the information file
    information = ""

    for crop_dict in od_instance.iterate_over_images(image_files):
        nr_crops += 1

        # Store crops and update information string
        if do_store_crops:
            information = store_crops(information, output_folder_path, crop_dict)

        # Check if crop is correct
        if do_evaluate_model and  np.random.random() < float(n_annotations) / len(image_files):
            if crops_evaluated >= n_annotations:
                continue

            # Ties are very small and a crop of a tie is hard to indentify as a tie, hence we do not evalute ties
            if crop_dict["class"] == "tie":
                continue

            crops_evaluated += 1
            is_correct = evaluate(crop_dict)

            if is_correct:
                nr_correct_crops += 1

            print("Annotated {0} / {1}".format(crops_evaluated, n_annotations))               

    # Store information string in file        
    if do_store_crops:
        information_file = open(os.path.join(output_folder_path, "crop_information.txt"), "w")
        information_file.write("original_image, crop_image, class_name, x1, x2, y1, y2\n")
        information_file.write(information)
        information_file.close()

    # Output data
    print("Processed {0} / {0} images\nExtracted {1} crops".format(len(image_files), nr_crops))

    if do_evaluate_model:
        print("Manually checked {0} crops, {1} were correcty classified. That is {2}%.".format(crops_evaluated, nr_correct_crops, nr_correct_crops/crops_evaluated * 100))
        return nr_crops, nr_correct_crops, crops_evaluated
