import argparse
import os, sys

sys.path.append(os.getcwd())
# print('sys_path = ',os.getcwd())
import os.path as osp
import shutil
import tempfile
import numpy as np
import cv2

import mmcv
import torch
import torch.distributed as dist
import torch.nn.functional as F
from mmcv.parallel import MMDataParallel, MMDistributedDataParallel
from mmcv.runner import get_dist_info, load_checkpoint

from mmdet.apis import init_dist
from mmdet.core import coco_eval, results2json, wrap_fp16_model
from mmdet.datasets import build_dataloader, build_dataset
from mmdet.models import build_detector
import pycocotools.mask as maskUtils
from mmdet.core import poly_nms
from pytorch_transformers import BertTokenizer, BertConfig, BertModel
import Polygon as plg
from TextSpotter import tools

os.environ["CUDA_VISIBLE_DEVICES"] = "0"


class Model:
    def __init__(self, model_pth_path, data_root="images", results="results"):
        self.data_root = data_root
        self.results = results
        self.model_pth_path = model_pth_path
        self.num = tools.rename(data_root=data_root)
        tools.prepare(data_root)

    def train(self):
        train(model_pth_path=self.model_pth_path, results=self.results)
        tools.draw_box(num=self.num, data_root=self.data_root, results=self.results)


# model settings
def train(model_pth_path, results):
    args = parse_args()
    args.checkpoint = model_pth_path

    cfg = mmcv.Config.fromfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), "cfg.py"))
    # set cudnn_benchmark
    if cfg.get('cudnn_benchmark', False):
        torch.backends.cudnn.benchmark = True
    cfg.model.pretrained = None
    cfg.data.test.test_mode = True

    # init distributed env first, since logger depends on the dist info.
    if args.launcher == 'none':
        distributed = False
    else:
        distributed = True
        init_dist(args.launcher, **cfg.dist_params)

    # build the dataloader
    # TODO: support multiple images per gpu (only minor changes are needed)
    dataset = build_dataset(cfg.data.test)
    data_loader = build_dataloader(
        dataset,
        imgs_per_gpu=1,
        workers_per_gpu=cfg.data.workers_per_gpu,
        dist=distributed,
        shuffle=False)

    # build the model and load checkpoint
    model = build_detector(cfg.model, train_cfg=None, test_cfg=cfg.test_cfg)
    fp16_cfg = cfg.get('fp16', None)
    if fp16_cfg is not None:
        wrap_fp16_model(model)

    load_checkpoint(model, args.checkpoint, map_location='cpu')

    model.CLASSES = dataset.label2char

    if not distributed:
        model = MMDataParallel(model, device_ids=[0])
        outputs = single_gpu_test(args, model, data_loader, args.show)
    else:
        model = MMDistributedDataParallel(model.cuda())
        outputs = multi_gpu_test(args, model, data_loader, args.tmpdir)

    rank, _ = get_dist_info()

    with open(os.path.join(results, "results.json"), 'w') as f:
        mmcv.dump(outputs, f, file_format='json', ensure_ascii=False)


def single_gpu_test(args, model, data_loader, show=False, bert_tokenizer=None, bert_model=None, text_model=None):
    model.eval()
    if bert_tokenizer is not None:
        bert_model.eval()
        text_model.eval()
    results = []
    dataset = data_loader.dataset
    prog_bar = mmcv.ProgressBar(len(dataset))

    for i, data in enumerate(data_loader):
        img_meta = data['img_meta'][0].data[0]
        img_name = img_meta[0]['filename'].split('/')[-1]
        print("img_name === ", img_name)
        # print("data == ", data)
        with torch.no_grad():
            result = model(return_loss=False, rescale=not show, **data)

        rects, scores, char_bbox_results, texts = result

        if show:
            model.module.show_result(data, result)

        if args.with_char:
            char_rects = []
            char_scores = []
            chars = []
            char_bboxes = mmcv.concat_list(char_bbox_results)
            char_labels = np.concatenate([
                np.full(bbox.shape[0], i, dtype=np.int32)
                for i, bbox in enumerate(char_bbox_results)
            ])
            for char_bbox, char_label in zip(char_bboxes, char_labels):
                char_bbox = [float(x) for x in char_bbox]
                char_rect = [char_bbox[0], char_bbox[1],
                             char_bbox[0], char_bbox[3],
                             char_bbox[2], char_bbox[3],
                             char_bbox[2], char_bbox[1]]
                char_rects.append(char_rect)
                char_scores.append(char_bbox[-1])
                chars.append(dataset.label2char[char_label])

        result_i = {
            'img_name': img_name,
            'points': rects,
            'scores': scores
        }

        if len(result) == 4:
            result_i['texts'] = texts

        if args.with_char:
            result_i['chars'] = {
                'points': char_rects,
                'scores': char_scores,
                'chars': chars
            }

        results.append(result_i)

        batch_size = data['img'][0].size(0)
        for _ in range(batch_size):
            prog_bar.update()
        # '''
    return results


def multi_gpu_test(args, model, data_loader, tmpdir=None, bert_tokenizer=None, bert_model=None, text_model=None):
    model.eval()
    results = []
    dataset = data_loader.dataset
    rank, world_size = get_dist_info()
    if rank == 0:
        prog_bar = mmcv.ProgressBar(len(dataset))

    for i, data in enumerate(data_loader):
        img_meta = data['img_meta'][0].data[0]
        img_name = img_meta[0]['filename'].split('/')[-1]
        with torch.no_grad():
            result = model(return_loss=False, rescale=True, **data)

        rects, scores, char_bbox_results, texts = result

        if args.with_char:
            char_rects = []
            char_scores = []
            chars = []
            char_bboxes = mmcv.concat_list(char_bbox_results)
            char_labels = np.concatenate([
                np.full(bbox.shape[0], i, dtype=np.int32)
                for i, bbox in enumerate(char_bbox_results)
            ])
            for char_bbox, char_label in zip(char_bboxes, char_labels):
                char_bbox = [float(x) for x in char_bbox]
                char_rect = [char_bbox[0], char_bbox[1],
                             char_bbox[0], char_bbox[3],
                             char_bbox[2], char_bbox[3],
                             char_bbox[2], char_bbox[1]]
                char_rects.append(char_rect)
                char_scores.append(char_bbox[-1])
                chars.append(dataset.label2char[char_label])

        result_i = {
            'img_name': img_name,
            'points': rects,
            'scores': scores,
        }

        if len(result) == 4:
            result_i['texts'] = texts

        if args.with_char:
            result_i['chars'] = {
                'points': char_rects,
                'scores': char_scores,
                'chars': chars
            }

        results.append(result_i)

        if rank == 3:
            batch_size = data['img'][0].size(0)
            for _ in range(batch_size * world_size):
                prog_bar.update()

    # collect results from all ranks
    results = collect_results(results, len(dataset), tmpdir)

    return results


def collect_results(result_part, size, tmpdir=None):
    rank, world_size = get_dist_info()
    # create a tmp dir if it is not specified
    if tmpdir is None:
        MAX_LEN = 512
        # 32 is whitespace
        dir_tensor = torch.full((MAX_LEN,),
                                32,
                                dtype=torch.uint8,
                                device='cuda')
        if rank == 0:
            tmpdir = tempfile.mkdtemp()
            tmpdir = torch.tensor(
                bytearray(tmpdir.encode()), dtype=torch.uint8, device='cuda')
            dir_tensor[:len(tmpdir)] = tmpdir
        dist.broadcast(dir_tensor, 0)
        tmpdir = dir_tensor.cpu().numpy().tobytes().decode().rstrip()
    else:
        mmcv.mkdir_or_exist(tmpdir)
    # dump the part result to the dir
    mmcv.dump(result_part, osp.join(tmpdir, 'part_{}.pkl'.format(rank)))
    dist.barrier()
    # collect all parts
    if rank != 0:
        return None
    else:
        # load results of all parts from tmp dir
        part_list = []
        for i in range(world_size):
            part_file = osp.join(tmpdir, 'part_{}.pkl'.format(i))
            part_list.append(mmcv.load(part_file))
        # sort the results
        ordered_results = []
        for res in zip(*part_list):
            ordered_results.extend(list(res))
        # the dataloader may pad some samples
        ordered_results = ordered_results[:size]
        # remove tmp dir
        shutil.rmtree(tmpdir)
        return ordered_results


def parse_args():
    parser = argparse.ArgumentParser(description='MMDet test detector')
    # parser.add_argument('config', help='test config file path')
    # parser.add_argument('checkpoint', help='checkpoint file')
    parser.add_argument(
        '--json_out',
        help='output result file name without extension',
        type=str)
    parser.add_argument('--show', action='store_true', help='show results')
    parser.add_argument('--with_char', action='store_true', help='show results')
    parser.add_argument('--tmpdir', help='tmp dir for writing some results')
    parser.add_argument(
        '--launcher',
        choices=['none', 'pytorch', 'slurm', 'mpi'],
        default='none',
        help='job launcher')
    parser.add_argument('--local_rank', type=int, default=3)
    args = parser.parse_args()
    if 'LOCAL_RANK' not in os.environ:
        os.environ['LOCAL_RANK'] = str(args.local_rank)
    return args
