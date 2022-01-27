import os, argparse, shutil
import glob
from tqdm import tqdm
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument('input_dir', type=str)
parser.add_argument('output_dir', type=str)
parser.add_argument('split_size', type=int)
args = parser.parse_args()
input_dir = args.input_dir
output_dir = args.output_dir

image_paths = glob.glob(input_dir+'/*.jpg')
image_paths.extend(glob.glob(input_dir+'/*.png'))

over_dir = os.path.join(output_dir, 'over_%d' % args.split_size)
under_dir = os.path.join(output_dir, 'under_%d' % args.split_size)
os.makedirs(over_dir, exist_ok=True)
os.makedirs(under_dir, exist_ok=True)

for image_path in tqdm(image_paths):
    try:
        image = Image.open(image_path)
        w, h = image.size
        if w>args.split_size:
            new_image_path = os.path.join(over_dir, os.path.basename(image_path))
        else:
            new_image_path = os.path.join(under_dir, os.path.basename(image_path))
        shutil.copyfile(image_path,new_image_path)
    except:
        print(image_path,': failed')
        pass
