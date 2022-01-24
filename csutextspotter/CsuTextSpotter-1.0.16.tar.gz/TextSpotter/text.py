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
from TextSpotter.TextSpotter import tools

os.environ["CUDA_VISIBLE_DEVICES"] = "0"


class Model:
    def __init__(self, data_root, results, model_pth_path):
        self.data_root = data_root
        self.results = results
        self.model_pth_path = model_pth_path
        self.num = tools.rename(data_root=data_root)
        self.char_dict_file = 'char_dict.json'
        self.model = dict(
            type='AE_TextSpotter',
            pretrained='torchvision://resnet50',
            backbone=dict(
                type='ResNet',
                depth=50,
                num_stages=4,
                out_indices=(0, 1, 2, 3),
                frozen_stages=1,
                style='pytorch'),
            neck=dict(
                type='FPN',
                in_channels=[256, 512, 1024, 2048],
                out_channels=256,
                num_outs=5),
            rpn_head=dict(
                type='AETSRPNHead',
                in_channels=256,
                feat_channels=256,
                anchor_scales=[8],
                anchor_strides=[4, 8, 16, 32, 64],
                text_anchor_ratios=[0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0],
                char_anchor_ratios=[0.5, 1.0, 2.0],
                target_means=[.0, .0, .0, .0],
                target_stds=[1.0, 1.0, 1.0, 1.0],
                loss_cls=dict(type='CrossEntropyLoss', use_sigmoid=True, loss_weight=1.0),
                loss_bbox=dict(type='SmoothL1Loss', beta=1.0 / 9.0, loss_weight=1.0)),
            # text detection module
            text_bbox_roi_extractor=dict(
                type='SingleRoIExtractor',
                roi_layer=dict(type='RoIAlign', out_size=7, sample_num=2),
                out_channels=256,
                featmap_strides=[4, 8, 16, 32]),
            text_bbox_head=dict(
                type='AETSBBoxHead',
                num_shared_fcs=0,
                num_cls_convs=2,
                num_reg_convs=2,
                in_channels=256,
                conv_out_channels=256,
                fc_out_channels=1024,
                roi_feat_size=7,
                num_classes=2,
                target_means=[0., 0., 0., 0.],
                target_stds=[0.1, 0.1, 0.2, 0.2],
                reg_class_agnostic=True,
                loss_cls=dict(type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0),
                loss_bbox=dict(type='SmoothL1Loss', beta=1.0, loss_weight=1.0)),
            text_mask_roi_extractor=dict(
                type='SingleRoIExtractor',
                roi_layer=dict(type='RoIAlign', out_size=14, sample_num=2),
                out_channels=256,
                featmap_strides=[4, 8, 16, 32]),
            text_mask_head=dict(
                type='AETSMaskHead',
                num_convs=4,
                in_channels=256,
                conv_out_channels=256,
                num_classes=2,
                loss_mask=dict(type='CrossEntropyLoss', use_mask=True, loss_weight=1.0)),
            # character-based recognition module
            char_bbox_roi_extractor=dict(
                type='SingleRoIExtractor',
                roi_layer=dict(type='RoIAlign', out_size=14, sample_num=2),
                out_channels=256,
                featmap_strides=[4, 8, 16, 32]),
            char_bbox_head=dict(
                type='AETSBBoxHead',
                num_shared_fcs=0,
                num_cls_convs=4,
                num_reg_convs=2,
                in_channels=256,
                conv_out_channels=256,
                fc_out_channels=1024,
                roi_feat_size=14,
                num_classes=3614,
                target_means=[0., 0., 0., 0.],
                target_stds=[0.1, 0.1, 0.2, 0.2],
                reg_class_agnostic=True,
                loss_cls=dict(type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0),
                loss_bbox=dict(type='SmoothL1Loss', beta=1.0, loss_weight=1.0)),
            crm_cfg=dict(
                char_dict_file=data_root + self.char_dict_file,
                char_assign_iou=0.3),
            # language module
            lm_cfg=dict(
                dictmap_file=data_root + 'dictmap_to_lower.json',
                bert_vocab_file='bert-base-chinese/bert-base-chinese-vocab.txt',
                bert_cfg_file='bert-base-chinese/bert-base-chinese-config.json',
                bert_model_file='bert-base-chinese/bert-base-chinese-pytorch_model.bin',
                sample_num=32,
                pos_iou=0.8,
                lang_score_weight=0.3,
                lang_model=dict(
                    input_dim=768,
                    output_dim=2,
                    gru_num=2,
                    with_bi=True)))
        # model training and testing settings
        self.train_cfg = dict(
            rpn=dict(
                assigner=dict(
                    type='MaxIoUAssigner',
                    pos_iou_thr=0.7,
                    neg_iou_thr=0.3,
                    min_pos_iou=0.3,
                    ignore_iof_thr=-1),
                sampler=dict(
                    type='RandomSampler',
                    num=256,
                    pos_fraction=0.5,
                    neg_pos_ub=-1,
                    add_gt_as_proposals=False),
                allowed_border=0,
                pos_weight=-1,
                debug=False),
            text_rpn_proposal=dict(
                nms_across_levels=False,
                nms_pre=2000,
                nms_post=2000,
                max_num=2000,
                nms_thr=0.7,
                min_bbox_size=0),
            char_rpn_proposal=dict(
                nms_across_levels=False,
                nms_pre=2000,
                nms_post=2000,
                max_num=2000,
                nms_thr=0.7,
                min_bbox_size=0),
            rcnn=dict(
                assigner=dict(
                    type='MaxIoUAssigner',
                    pos_iou_thr=0.5,
                    neg_iou_thr=0.5,
                    min_pos_iou=0.5,
                    ignore_iof_thr=-1),
                sampler=dict(
                    type='RandomSampler',
                    num=512,
                    pos_fraction=0.25,
                    neg_pos_ub=-1,
                    add_gt_as_proposals=True),
                mask_size=28,
                pos_weight=-1,
                debug=False))
        self.test_cfg = dict(
            text_rpn=dict(
                nms_across_levels=False,
                nms_pre=900,
                nms_post=900,
                max_num=900,
                nms_thr=0.7,
                min_bbox_size=0),
            char_rpn=dict(
                nms_across_levels=False,
                nms_pre=900,
                nms_post=900,
                max_num=900,
                nms_thr=0.5,  # 0.7
                min_bbox_size=0),
            text_rcnn=dict(
                score_thr=0.01,
                nms=dict(type='nms', iou_thr=0.9),
                max_per_img=500,
                mask_thr_binary=0.5),
            char_rcnn=dict(
                score_thr=0.1,
                nms=dict(type='nms', iou_thr=0.1),
                max_per_img=200,
                mask_thr_binary=0.5),
            recognizer=dict(
                char_dict_file=data_root + self.char_dict_file,
                char_assign_iou=0.5),
            poly_iou=0.1,
            ignore_thr=0.3)
        # dataset settings
        self.dataset_type = 'ReCTSDataset'
        img_norm_cfg = dict(
            mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)
        self.train_pipeline = [
            dict(type='LoadImageFromFile'),
            dict(type='LoadAnnotations', with_bbox=True, with_mask=True),
            dict(type='PhotoMetricDistortion',
                 brightness_delta=32,
                 contrast_range=(0.5, 1.5),
                 saturation_range=(0.5, 1.5),
                 hue_delta=18),
            # dict(type='Resize', img_scale=(1333, 800), keep_ratio=True),
            dict(type='Resize', img_scale=[(1664, 672), (1664, 928)], keep_ratio=True),
            dict(type='RandomFlip', flip_ratio=0),  # 0.5
            dict(type='Normalize', **img_norm_cfg),
            dict(type='Pad', size_divisor=32),
            dict(type='DefaultFormatBundle'),
            dict(type='Collect',
                 keys=['img', 'gt_bboxes', 'gt_labels', 'gt_masks'],
                 meta_keys=['filename', 'annpath', 'ori_shape', 'img_shape', 'pad_shape', 'scale_factor', 'flip',
                            'img_norm_cfg']),
        ]
        self.test_pipeline = [
            dict(type='LoadImageFromFile'),
            dict(
                type='MultiScaleFlipAug',
                img_scale=(1333, 800),
                flip=False,
                transforms=[
                    dict(type='Resize', keep_ratio=True),
                    dict(type='RandomFlip'),
                    dict(type='Normalize', **img_norm_cfg),
                    dict(type='Pad', size_divisor=32),
                    dict(type='ImageToTensor', keys=['img']),
                    dict(type='Collect', keys=['img']),
                ])
        ]
        self.data = dict(
            imgs_per_gpu=8,
            workers_per_gpu=8,
            # imgs_per_gpu=1,
            # workers_per_gpu=1,
            train=dict(
                type=self.dataset_type,
                data_root=data_root,
                ann_file='train/gt/',
                img_prefix='train/img/',
                cache_file='tda_rects_train_cache_file.json',
                char_dict_file=self.char_dict_file,
                pipeline=self.train_pipeline),
            val=dict(
                type=self.dataset_type,
                data_root=data_root,
                ann_file='train/gt/',
                img_prefix='train/img/',
                cache_file='tda_rects_val_cache_file.json',
                char_dict_file=self.char_dict_file,
                pipeline=self.test_pipeline),
            test=dict(
                test_mode=True,
                type=self.dataset_type,
                data_root=data_root,
                ann_file=None,
                img_prefix='rename/',
                cache_file='tda_rects_test_cache_file.json',
                char_dict_file=self.char_dict_file,
                pipeline=self.test_pipeline)
        )
        # optimizer
        self.optimizer = dict(type='SGD', lr=0.20, momentum=0.9, weight_decay=0.0001)
        self.optimizer_config = dict(grad_clip=dict(max_norm=35, norm_type=2))
        # learning policy
        self.lr_config = dict(
            policy='step',
            warmup='linear',
            warmup_iters=300,
            warmup_ratio=1.0 / 3,
            step=[8, 11])
        self.checkpoint_config = dict(interval=1)
        # yapf:disable
        self.log_config = dict(
            interval=50,
            hooks=[
                dict(type='TextLoggerHook'),
                # dict(type='TensorboardLoggerHook')
            ])
        # yapf:enable
        self.evaluation = dict(interval=1)
        # runtime settings
        self.total_epochs = 12
        self.dist_params = dict(backend='nccl')
        self.log_level = 'INFO'
        self.work_dir = 'work_dirs/rects_ae_textspotter_lm_r50_1x/'
        self.load_from = 'work_dirs/rects_ae_textspotter_r50_1x/epoch_12.pth'
        self.resume_from = None
        self.workflow = [('train', 1)]

    def train(self):
        train(self)
        tools.draw_box(num=self.num, data_root=self.data_root, results=self.results)


# model settings
def train(cfg: Model):
    args = parse_args()
    args.checkpoint = cfg.model_pth_path

    assert args.show or args.json_out, \
        ('Please specify at least one operation (save or show the results) '
         'with the argument or "--show" or "--json_out"')

    # cfg = mmcv.Config.fromfile(args.config)
    # set cudnn_benchmark
    # if cfg.get('cudnn_benchmark', False):
    #     torch.backends.cudnn.benchmark = True
    cfg.model.pretrained = None
    # cfg.data.test.test_mode = True

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
    # fp16_cfg = cfg.get('fp16', None)
    # if fp16_cfg is not None:
    #     wrap_fp16_model(model)

    load_checkpoint(model, args.checkpoint, map_location='cpu')

    model.CLASSES = dataset.label2char

    if not distributed:
        model = MMDataParallel(model, device_ids=[0])
        outputs = single_gpu_test(args, model, data_loader, args.show)
    else:
        model = MMDistributedDataParallel(model.cuda())
        outputs = multi_gpu_test(args, model, data_loader, args.tmpdir)

    rank, _ = get_dist_info()

    with open(os.path.join(cfg.results, "results.json"), 'w') as f:
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
