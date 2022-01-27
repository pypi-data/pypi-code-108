from multiprocessing import Pool
import os, argparse
from tqdm import tqdm
import cv2 as cv

def margin_crop(img_name):
    img = cv.imread(os.path.join(image_dir_shared, img_name))
    L2 = int(L_shared/2)
    img = img[L_shared:,L2:-L2]
    cv.imwrite(os.path.join(output_dir_shared,img_name), img)

def initializer(image_dir,L,output_dir):
    global image_dir_shared,L_shared,output_dir_shared
    image_dir_shared = image_dir
    L_shared = L
    output_dir_shared = output_dir

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--image_dir', type=str)
    parser.add_argument('--L', type=int)
    parser.add_argument('--output_dir', type=str)
    parser.add_argument('--workers', type=int, default=10)
    args = parser.parse_args()
    image_dir = args.image_dir
    L = args.L
    output_dir = args.output_dir
    image_names = [f for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg'))]
    image_names = sorted(image_names)

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    pool = Pool(args.workers,initializer=initializer,initargs=(image_dir,L,output_dir))
    with tqdm(total=len(image_names)) as t:
        for _ in pool.imap_unordered(margin_crop, image_names):
            t.update(1)
        pool.close()
        pool.join()
        