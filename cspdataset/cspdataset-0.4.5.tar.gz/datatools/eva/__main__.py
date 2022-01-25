#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2021/9/2 16:32
# @Author  : xgy
# @Site    : 
# @File    : datatools.py
# @Software: PyCharm
# @python version: 3.7.4
"""

import argparse 
from datatools.eva.det.eva import eva as deteva

# usag = "evatools --eva det --data_dir C:/Users/xgy/Desktop/voc_coco/cocotest1 --division_ratio 0.9 0.8"

def get_args():
    parser = argparse.ArgumentParser(description="tools for det eva") 
    
    # 评估脚本要求参数
    parser.add_argument("--eva", "-e", help="eva for model type", type=str, required=True, default='det',
                        choices=["det", "DET"])
    
    parser.add_argument('--contestant_submitted_file_name',  '-s',type=str, required=True, # default="test_pred_simple.json", 
                        help="contestant submitted json file name")
 
    parser.add_argument('--gold_json_file_path', '-t',type=str, required=True, #default="test.json",
                        help="coco dataset json file name")
     
    parser.add_argument('--origin_image_file_path', '-o', required=True,type=str, # default='e:/opt/local/object_detection/train1_coco_aug/images/val1', 
                        help="origin image file path") 
    
    parser.add_argument('--output_image_file_path', '-i',type=str, default="",
                        help="origin image file path") 
     
    parser.add_argument('--output_voc_file_path', '-v',type=str, default="",
                        help="output image file path")

    args = parser.parse_args()
    return args


def main():
    args = get_args()
 
    if args.eva == "DET" or args.eva == "det":
            deteva(args)
    

if __name__ == '__main__':
    print("start")
    main()
