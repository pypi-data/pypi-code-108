import os                                                                                                                                                                                                   
from PIL import Image
from tqdm import tqdm
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='resize oversize images')
    parser.add_argument('image_dir', type=str, help='path of input image dir')
    parser.add_argument('image_out_dir', type=str, help='path of ouput image dir')
    parser.add_argument('resolution', type=int, help='path of ouput image dir')
    args = parser.parse_args()

    image_out_dir = args.image_out_dir
    if not os.path.isdir(image_out_dir):
        os.mkdir(image_out_dir)

    image_dir = args.image_dir
    if not os.path.isabs(image_dir):
        image_dir = os.path.join(os.getcwd(), image_dir)

    image_names = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.png'))]

    for image_name in tqdm(image_names):
        image_path = os.path.join(image_dir, image_name)
        image_out_path = os.path.join(image_out_dir, image_name)
        img = Image.open(image_path)
        resized = img.resize((args.resolution, args.resolution), Image.LANCZOS)
        resized.save(image_out_path[:-4]+'.png')
