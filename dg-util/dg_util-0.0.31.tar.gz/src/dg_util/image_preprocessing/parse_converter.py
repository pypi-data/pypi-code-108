from PIL import Image
from PIL import ImageDraw
import numpy as np
import json
import os, argparse
from tqdm import tqdm

label_colours = [(0,0,0)
                # 0=Background
                ,(128,0,0),(255,0,0),(0,85,0),(170,0,51),(255,85,0)
                # 1=Hat,  2=Hair,    3=Glove, 4=Sunglasses, 5=UpperClothes
                ,(0,0,85),(0,119,221),(85,85,0),(0,85,85),(85,51,0)
                # 6=Dress, 7=Coat, 8=Socks, 9=Pants, 10=Jumpsuits
                ,(52,86,128),(0,128,0),(0,0,255),(51,170,221),(0,255,255)
                # 11=Scarf, 12=Skirt, 13=Face, 14=LeftArm, 15=RightArm
                ,(85,255,170),(170,255,85),(255,255,0),(255,170,0), (0,255,65),(83,53,99),(255,228,225),(139,125,123)
                # 16=LeftLeg, 17=RightLeg, 18=LeftShoe, 19=RightShoe 20=RightHand 21=LeftHand, 22= LeftForearm, 23=RightForearm
                 ,(188,143,143)]
                #24=LowerBody

dict_colours = {(0,0,0):0
                # 0=Background
                ,(128,0,0):1,(255,0,0):2,(0,85,0):3,(170,0,51):4,(255,85,0):5
                # 1=Hat,  2=Hair,    3=Glove, 4=Sunglasses, 5=UpperClothes
                ,(0,0,85):6,(0,119,221):7,(85,85,0):8,(0,85,85):9,(85,51,0):10
                # 6=Dress, 7=Coat, 8=Socks, 9=Pants, 10=Jumpsuits
                ,(52,86,128):11,(0,128,0):12,(0,0,255):13,(51,170,221):14,(0,255,255):15
                # 11=Scarf, 12=Skirt, 13=Face, 14=LeftArm, 15=RightArm
                ,(85,255,170):16,(170,255,85):17,(255,255,0):18,(255,170,0):19,(0,255,65):20,(83,53,99):21
                ,(255,228,225):22,(139,125,123):23,(188,143,143):24}
                # 16=LeftLeg, 17=RightLeg, 18=LeftShoe, 19=RightShoe

def decode_labels(mask, num_images=1, num_classes=22):

    h, w = mask.shape
    outputs = np.zeros((h, w, 3), dtype=np.uint8)
    img = Image.new('RGB', (w, h))
    pixels = img.load()
    for i in range(h):
        for j in range(w):
            pixels[j, i] = label_colours[mask[i,j]]
    outputs = np.array(img)
    return outputs

def is_image_file(filename):

    IMG_EXTENSIONS = [
        '.jpg', '.JPG', '.jpeg', '.JPEG',
        '.png', '.PNG', '.ppm', '.PPM', '.bmp', '.BMP',
    ]
    return any(filename.endswith(extension) for extension in IMG_EXTENSIONS)


def arm_clipper(elbow, shoulder, wrist, size, label):

    shoulder_elbow_vec = (shoulder - elbow)[:2]
    wrist_elbow_vec = (wrist - elbow)[:2]

    k1 = shoulder_elbow_vec[1] / shoulder_elbow_vec[0]
    k2 = wrist_elbow_vec[1] / wrist_elbow_vec[0]

    L_x = np.sqrt(shoulder_elbow_vec.dot(shoulder_elbow_vec))
    L_y = np.sqrt(wrist_elbow_vec.dot(wrist_elbow_vec))

    cos_angle = shoulder_elbow_vec.dot(wrist_elbow_vec) / (L_x * L_y)
    angle = np.arccos(cos_angle)
    angle2 = angle / 2

    if k1 > k2:
        angle_line = angle2 + np.arctan(k2)
    else:
        angle_line = angle2 + np.arctan(k1)

    k = np.tan(angle_line)

    return draw_region(elbow, wrist, size, label, k)


def leg_clipper(hip, knee, size, label):

    mid = np.array([(hip[0]+knee[0])/2, (hip[1]+knee[1])/2])
    hip_knee_vec = np.array([(knee[0]-hip[0]), (knee[1]-hip[1])])

    k = -1 / (hip_knee_vec[1]/hip_knee_vec[0])

    return draw_region(mid, knee, size, label, k)


def draw_region(root, point, size, label, k):

    im = Image.new('L', size=size)
    draw = ImageDraw.Draw(im)

    xmax = (size[1]-root[1])/k + root[0]
    xmin = (-root[1] / k) + root[0]
    ymax = k*(size[0]-root[0]) + root[1]
    ymin = k * (-root[0]) + root[1]

    is_upper = ((k * (point[0] - root[0]) + root[1]) > point[1])

    if xmax >= size[0]:
        if ymin >= 0:
            if is_upper:
                draw.polygon(((0,0), (0,ymin), (size[0],ymax), (size[0], 0)), fill=label, outline=label)
            else:
                draw.polygon(((0,ymin), (0,size[1]), (size[0],size[1]),(size[0], ymax)), fill=label, outline=label)
        else:
            if is_upper:
                draw.polygon(((xmin, 0), (size[0], ymax), (size[0], 0)), fill=label, outline=label)
            else:
                draw.polygon(((0, 0), (0, size[1]), (size[0], size[1]), (size[0], ymax), (xmin, 0)), fill=label,
                             outline=label)

    elif xmax < size[0] and xmax >= 0:
        if xmin >= size[0]:
            if is_upper:
                draw.polygon(((0, 0), (0, size[1]), (xmax, size[1]), (size[0],ymax),(size[0],0)), fill=label, outline=label)
            else:
                draw.polygon(((xmax, size[1]), (size[0], size[1]), (size[0], ymax)), fill=label, outline=label)

        elif xmin<size[0] and xmin >=0:
            if is_upper:
                draw.polygon(((0, 0), (0, size[1]), (xmax, size[1]), (xmin, 0)), fill=label,
                             outline=label)
            else:
                draw.polygon(((xmax, size[1]), (size[0], size[1]), (size[0], 0), (xmin, 0)), fill=label,
                             outline=label)
    elif xmax < 0:
        if ymax >= 0:
            if is_upper:
                draw.polygon(((0, 0), (0, ymin), (size[0], ymax), (size[0], 0)), fill=label,
                         outline=label)
            else:
                draw.polygon(((0, ymin), (0, size[1]), (size[0], size[1]), (size[0], ymax)), fill=label,
                         outline=label)
        else:
            if is_upper:
                draw.polygon(((0, 0), (0, ymin), (xmin, 0)), fill=label,
                         outline=label)
            else:
                draw.polygon(((0, ymin), (0, size[1]), (size[0], size[1]), (size[0], 0),(xmin,0)), fill=label,
                         outline=label)
    return im

if __name__ == '__main__':

    #output_dir = '/Users/admin/Desktop/datagrid/UR_test/parse_convert'
    #img_dir = '/Users/admin/Desktop/datagrid/UR_test/image-parse'
    #json_dir = '/Users/admin/Desktop/datagrid/UR_test/pose-raw'

    parser = argparse.ArgumentParser()
    parser.add_argument('input_parse_dir', type=str)
    parser.add_argument('input_json_dir', type=str)
    parser.add_argument('output_parse_dir', type=str)
    args = parser.parse_args()
    output_dir = args.output_parse_dir
    img_dir = args.input_parse_dir
    json_dir = args.input_json_dir
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    img_paths = sorted([f for f in os.listdir(img_dir) if os.path.isfile(os.path.join(img_dir, f))])
    
    for img_filename in tqdm(img_paths):
        if not is_image_file(os.path.join(img_dir, img_filename)):
            continue
        json_name = img_filename[:-4] +'_keypoints.json'
    
        with open(os.path.join(json_dir, json_name), 'r') as f:
            pose_label = json.load(f)
            righthand_data = pose_label['people'][0]['hand_right_keypoints_2d']
            righthand_data = np.array(righthand_data)
            righthand_data = righthand_data.reshape((-1, 3))
            lefthand_data = pose_label['people'][0]['hand_left_keypoints_2d']
            lefthand_data = np.array(lefthand_data)
            lefthand_data = lefthand_data.reshape((-1, 3))
            pose_data = pose_label['people'][0]['pose_keypoints_2d']
            pose_data = np.array(pose_data)
            pose_data = pose_data.reshape((-1, 3))

        right_shoulder = pose_data[2]
        right_elbow = pose_data[3]
        right_wrist = pose_data[4]

        left_shoulder = pose_data[5]
        left_elbow = pose_data[6]
        left_wrist = pose_data[7]

        right_knee = pose_data[9]
        right_hip = pose_data[8]

        left_knee = pose_data[12]
        left_hip = pose_data[11]

        im_parse = Image.open(os.path.join(img_dir, img_filename))
        SIZE = im_parse.size

        parse_array = np.array(im_parse).astype(np.int32)

        right_arm = (parse_array == 15).astype(np.int32)
        left_arm = (parse_array == 14).astype(np.int32)
        right_leg = (parse_array == 17).astype(np.int32)
        left_leg = (parse_array == 16).astype(np.int32)
        pants = (parse_array == 9).astype(np.int32)
        skirt = (parse_array == 12).astype(np.int32)

        parse_array = parse_array - right_arm*15- left_arm*14\
        - pants*9 - skirt*12

        right_arm_clipper = arm_clipper(right_elbow, right_shoulder, right_wrist, SIZE, 1)
        left_arm_clipper = arm_clipper(left_elbow, left_shoulder, left_wrist, SIZE, 1)

        right_arm_clipper = np.array(right_arm_clipper).astype(np.int32)
        left_arm_clipper = np.array(left_arm_clipper).astype(np.int32)

        right_forearm = right_arm * right_arm_clipper

        left_forearm = left_arm * left_arm_clipper

        right_arm = right_arm - right_forearm
        left_arm = left_arm - left_forearm

        right_leg_clipper = leg_clipper(right_hip, right_knee, SIZE, 1)
        left_leg_clipper = leg_clipper(left_hip, left_knee, SIZE, 1)

        right_leg_clipper = np.array(right_leg_clipper).astype(np.int32)
        left_leg_clipper = np.array(left_leg_clipper).astype(np.int32)

        right_clipper_pants = pants * right_leg_clipper
        right_clipper_skirt = skirt * right_leg_clipper
        left_clipper_pants = pants  * left_leg_clipper
        left_clipper_skirt = skirt * left_leg_clipper

        pants_clipper = ((right_clipper_pants + left_clipper_pants)>0).astype(np.int32)
        skirt_clipper = ((right_clipper_skirt + left_clipper_skirt)>0).astype(np.int32)

        pants = pants - pants_clipper
        skirt = skirt - skirt_clipper

        #right_leg = right_leg - (right_shank / 25)
        #left_leg = left_leg - (left_shank / 24)

        #lower_body = pants + skirt - (left_shank / 24 ) - (right_shank / 25)
        parse_array = parse_array + right_arm*15 + left_arm*14\
        + right_forearm*23 + left_forearm*22 + pants*9 + skirt*12\
        + pants_clipper*24 + skirt_clipper*24

        im_parse = Image.fromarray(parse_array.astype(np.int32))
        im_parse.save(os.path.join(output_dir, img_filename))

        img_filename = 'vis_' + img_filename
        parse_array = decode_labels(parse_array.astype(np.int32))
        im_parse = Image.fromarray(parse_array)
        im_parse.save(os.path.join(output_dir, img_filename))



