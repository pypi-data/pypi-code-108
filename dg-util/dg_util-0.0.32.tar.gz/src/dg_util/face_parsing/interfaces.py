#!/usr/bin/python
# -*- encoding: utf-8 -*-

from .model import BiSeNet
import torch
import os
import os.path as osp
import numpy as np
from PIL import Image
import torchvision.transforms as transforms
import cv2

file_id='1JvCvW1CjAmmS8rKKLFXlUSGD8sdp71A0'
pth_save_path='.cache/face_parsing/79999_iter.pth'

def vis_parsing_maps(im, parsing_anno, stride, save_im=False, save_path='vis_results/parsing_map_on_im.jpg'):
    # Colors for all 20 parts
    part_colors = [[255, 0, 0], [255, 85, 0], [255, 170, 0],
                   [255, 0, 85], [255, 0, 170],
                   [0, 255, 0], [85, 255, 0], [170, 255, 0],
                   [0, 255, 85], [0, 255, 170],
                   [0, 0, 255], [85, 0, 255], [170, 0, 255],
                   [0, 85, 255], [0, 170, 255],
                   [255, 255, 0], [255, 255, 85], [255, 255, 170],
                   [255, 0, 255], [255, 85, 255], [255, 170, 255],
                   [0, 255, 255], [85, 255, 255], [170, 255, 255]]

    im = np.array(im)
    vis_im = im.copy().astype(np.uint8)
    vis_parsing_anno = parsing_anno.copy().astype(np.uint8)
    vis_parsing_anno = cv2.resize(vis_parsing_anno, None, fx=stride, fy=stride, interpolation=cv2.INTER_NEAREST)
    vis_parsing_anno_color = np.zeros((vis_parsing_anno.shape[0], vis_parsing_anno.shape[1], 3)) + 255

    num_of_class = np.max(vis_parsing_anno)

    for pi in range(1, num_of_class + 1):
        index = np.where(vis_parsing_anno == pi)
        vis_parsing_anno_color[index[0], index[1], :] = part_colors[pi]

    vis_parsing_anno_color = vis_parsing_anno_color.astype(np.uint8)
    # print(vis_parsing_anno_color.shape, vis_im.shape)
    vis_im = cv2.addWeighted(cv2.cvtColor(vis_im, cv2.COLOR_RGB2BGR), 0.4, vis_parsing_anno_color, 0.6, 0)

    # Save result or not
    if save_im:
        cv2.imwrite(save_path[:-4] +'.png', vis_parsing_anno)
        cv2.imwrite(save_path, vis_im, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        return True
    else:
        return vis_parsing_anno, vis_im


def download_file_from_google_drive(id, destination):
    import requests
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

def download_pth():
    from pathlib import Path
    if not os.path.exists(pth_save_path):
        print('Pre-trained model does not exists, start downloading')
        # check if destinateion folder exists
        p=Path(pth_save_path)
        if not os.path.exists(p.parent):
            os.makedirs(p.parent)
    try:
        download_file_from_google_drive(file_id, pth_save_path)
        return True
    except Exception as e:
        print(e)
        return False

def check_pth():
    if not os.path.exists(pth_save_path):
        return download_pth()

def model_init():
    n_classes = 19
    net = BiSeNet(n_classes=n_classes)
    net.cuda()
    if not check_pth():
        if not download_pth():
            print('No pre-trained model')
    # save_pth = osp.join('res/cp', cp)
    net.load_state_dict(torch.load(pth_save_path))
    return net

def make_output_folder(folder_path):
    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path)
        except Exception as e:
            print(e)
            return False
    return True

def parsing_face(input_img, output_path=''):
    net=model_init()
    net.eval()
    to_tensor = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
    ])
    # img=Image.open(input_path)
    image = input_img.resize((512, 512), Image.BILINEAR)
    img = to_tensor(image)
    img = torch.unsqueeze(img, 0)
    img = img.cuda()
    with torch.no_grad():
        out = net(img)[0]
    parsing = out.squeeze(0).cpu().numpy().argmax(0)

    vis_parsing_anno, vis_im = vis_parsing_maps(image, parsing, stride=1, save_im=False)
    if output_path == '':
        return vis_parsing_anno, vis_im
    else:
        cv2.imwrite(output_path[:-4] +'_anno.png', vis_parsing_anno)
        cv2.imwrite(output_path, vis_im, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        return True


def parsing_faces(input_folder, output_folder):
    from tqdm import tqdm
    assert make_output_folder(output_folder)

    net=model_init()
    net.eval()
    to_tensor = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
    ])

    for image_path in tqdm(os.listdir(input_folder)):
            img = Image.open(osp.join(input_folder, image_path))
            image = img.resize((512, 512), Image.BILINEAR)
            img = to_tensor(image)
            img = torch.unsqueeze(img, 0)
            img = img.cuda()
            with torch.no_grad():
                out = net(img)[0]
            parsing = out.squeeze(0).cpu().numpy().argmax(0)

            vis_parsing_maps(image, parsing, stride=1, save_im=True, save_path=osp.join(output_folder, image_path))


def cli_parsing_face(file_byte):
    img = Image.open(io.BytesIO(data)).convert("RGB")
    _, res = parsing_face(img, '')

    bio = io.BytesIO()
    res.save(bio, "PNG")

    return bio.getbuffer()