import os
import argparse
from tqdm import tqdm
import cv2
from PIL import Image
import numpy as np

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_image_dir', type=str )
    parser.add_argument('in_image_parse_dir', type=str)
    parser.add_argument('out_image_and_parse_dir', type=str)
    parser.add_argument('--alpha', type=float, default=0.60)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    in_image_dir = args.in_image_dir
    in_image_parse_dir = args.in_image_parse_dir
    out_image_and_parse_dir = args.out_image_and_parse_dir

    if not os.path.exists(out_image_and_parse_dir):
        os.mkdir(out_image_and_parse_dir)

    image_names = sorted([f for f in os.listdir(in_image_dir) if f.endswith(('.jpg', '.png'))])
    #image_parse_names = sorted([f for f in os.listdir(in_image_parse_dir) if f.endswith(('.jpg', '.png'))])

    n_preview = 3
    for image_name in tqdm(image_names):
        img = cv2.imread( os.path.join(in_image_dir, image_name) )

        if( in_image_parse_dir.split("/")[-1] == "image-parse3" ):
            img_parse = cv2.imread( os.path.join(in_image_parse_dir, "vis_" + image_name) )
        else:
            img_parse = cv2.imread( os.path.join(in_image_parse_dir, image_name) )

        if( args.debug ):
            if(n_preview > 0):
                n_preview -= 1
                print( "img.shape :", img.shape )
                print( "img_parse.shape :", img_parse.shape )

        blended_img = cv2.addWeighted( img, args.alpha, img_parse, 1.0 - args.alpha, 0)
        #cv2.imwrite( os.path.join(out_image_and_parse_dir, image_name), blended_img )

        base_img = Image.new( "RGB", (3*img.shape[1], img.shape[0]), (0, 0, 0) ) 
        base_img.paste( Image.fromarray(cv2.cvtColor(blended_img, cv2.COLOR_BGR2RGB)), (0, 0) )
        base_img.paste( Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)), (1*img.shape[1], 0) )
        base_img.paste( Image.fromarray(cv2.cvtColor(img_parse, cv2.COLOR_BGR2RGB)), (2*img.shape[1], 0) )
        base_img.save( os.path.join(out_image_and_parse_dir, image_name) )
