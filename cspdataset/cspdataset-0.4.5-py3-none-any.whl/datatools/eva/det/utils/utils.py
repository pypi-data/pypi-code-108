from __future__ import division
import logging
import logging.handlers
import sys
# import torch
import numpy as np
import json 
import time,os
from PIL import Image
from PIL import ImageDraw,ImageFont, ImageOps

logger = logging.getLogger(__name__)


def init_log(base_level=logging.INFO):
	""" initialize log output configuration """
	_formatter = logging.Formatter("%(asctime)s: %(filename)s: %(lineno)d: %(levelname)s: %(message)s")
	logger = logging.getLogger()
	logger.setLevel(base_level)

	console_handler = logging.StreamHandler(sys.stdout)
	console_handler.setFormatter(_formatter)
	console_handler.setLevel(base_level)
	logger.addHandler(console_handler)
	
	# 写入文件
	#basedir = os.path.abspath(os.path.dirname(__file__))
	log_path = os.path.join('logs', time.strftime("%F"))  # 日志根目录 ../logs/yyyy-mm-dd/

	os.makedirs(log_path, exist_ok = True) 

	# # 创建一个handler，用于写入日志文件
	log_name = os.path.join(log_path, 'evatools.log')
	file_handler = logging.FileHandler(log_name, encoding='utf-8', mode='a')  # 指定utf-8格式编码，避免输出的日志文本乱码
	file_handler.setLevel(base_level) # 需要写入的日志级别
	file_handler.setFormatter(_formatter)
	logger.addHandler(file_handler)
	 
def load_json(result_json):
	""" load predicted and gold json file """
	with open(result_json, 'rb') as f:
		raw_data = json.load(f)
	return raw_data
 
def get_file_names(images):
	""" get the gold annotation information """
	 
	id_file_name = {}
	file_name_id = {}
	for j in range(len(images)):
		img_item = images[j]
		iid = img_item['id']
		file_name = img_item['file_name']
		id_file_name[iid] = file_name
		file_name_id[file_name] = iid
	return id_file_name,file_name_id


def get_pre_data(pred_data,file_name_id,class_name_dict):
	'''
	转换标准数据为coco评估数据
	'''
	new_pred_data = [] 
	for j in range(len(pred_data)):
		pred_item = pred_data[j]
		filename = pred_item['filename']
		category = pred_item['category']
		score = pred_item['score']
		bndbox = pred_item['bndbox'] 
		ann_item = { "image_id": file_name_id[filename],
					"category_id": class_name_dict[category],
					"score": score,
					"bbox": [
						int(bndbox['xmin']), #0
						int(bndbox['ymin']), #1
						int(bndbox['xmax']) - int(bndbox['xmin']) ,#2
						int(bndbox['ymax']) -  int(bndbox['ymin']) #3
					] 
			}  
		new_pred_data.append(ann_item)
	return new_pred_data
 
				
def get_class(gt_data): 
	'''
	获取分类与ID字典
	'''
	class_name_list = []
	class_name_dict = {}
	catid_name_dict = {}
	for class_item in gt_data['categories']:
		cid = int(class_item['id'])
		if isinstance(class_item['name'], list):
			class_name_list.append(class_item['name'][0])
			class_name_dict[class_item['name'][0]] = cid
			catid_name_dict[cid] = class_item['name'][0]
		else:
			class_name_list.append(class_item['name'])
			class_name_dict[class_item['name']] = cid
			catid_name_dict[cid] = class_item['name']
	return class_name_list,class_name_dict,catid_name_dict

def get_ann(image_id, annotations):
	"""
	统一处理返回相同格式的pred_data和gt_data
	"""
	ann = []
	for j in range(len(annotations)):
		ann_item = annotations[j]
		if ann_item['image_id'] == image_id:
			cls_id = int(ann_item['category_id'])
			x1 = int(ann_item['bbox'][0]) # xmin
			x2 = int(ann_item['bbox'][0]) + float(ann_item['bbox'][2])  # xmax
			y1 = int(ann_item['bbox'][1])
			y2 = int(ann_item['bbox'][1]) + float(ann_item['bbox'][3])
			ann.append([cls_id, x1, y1, x2, y2])  #原始标签数据格式
	return np.array(ann)  

def bbox_iou(box1, box2, x1y1x2y2=True):
	""" returns the IoU of two bounding boxes """

	if not x1y1x2y2:#如不是x1y1x2y2的格式，则可能是x,y,w,h的格式
		# transform from center and width to exact coordinates
		b1_x1, b1_x2 = box1[:, 0] - box1[:, 2] / 2, box1[:, 0] + box1[:, 2] / 2
		b1_y1, b1_y2 = box1[:, 1] - box1[:, 3] / 2, box1[:, 1] + box1[:, 3] / 2
		b2_x1, b2_x2 = box2[:, 0] - box2[:, 2] / 2, box2[:, 0] + box2[:, 2] / 2
		b2_y1, b2_y2 = box2[:, 1] - box2[:, 3] / 2, box2[:, 1] + box2[:, 3] / 2
	else:
		# get the coordinates of bounding boxes
		b1_x1, b1_y1, b1_x2, b1_y2 = box1[:, 0], box1[:, 1], box1[:, 2], box1[:, 3]
		b2_x1, b2_y1, b2_x2, b2_y2 = box2[:, 0], box2[:, 1], box2[:, 2], box2[:, 3]

	# get the corrdinates of the intersection rectangle
	inter_rect_x1 = np.max((b1_x1, b2_x1), axis=0)
	inter_rect_y1 = np.max((b1_y1, b2_y1), axis=0)
	inter_rect_x2 = np.min((b1_x2, b2_x2), axis=0)
	inter_rect_y2 = np.min((b1_y2, b2_y2), axis=0)

	# get intersection area and union area
	inter_area = np.clip(inter_rect_x2 - inter_rect_x1 + 1, 0, np.inf) * np.clip(inter_rect_y2 - inter_rect_y1 + 1, 0, np.inf)
	b1_area = (b1_x2 - b1_x1 + 1) * (b1_y2 - b1_y1 + 1)
	b2_area = (b2_x2 - b2_x1 + 1) * (b2_y2 - b2_y1 + 1)

	iou = inter_area / (b1_area + b2_area - inter_area + 1e-16)
	# print('iou', iou)
	return iou

def image_detection(pred_boxes, target_boxes, iou_threshold=0.5):
	'''
	通过一个函数，直接完成所有需求数据的统计。
	检测框：预测得到的框数据
	要求返回：
	1. false_detection_number：错检的数量
	2. missed_detection_number：漏检的数量
	3. detection_number：检测框的数量
	4. target_number: 实际框的数量
	'''

	detection_number = len(pred_boxes)
	target_number = len(target_boxes)
	# 极端情况：
	# 如果没有标注框，则为全部错检。即使检测框也为0，那预测错误的数量也是0，不影响结果。
	if len(target_boxes) == 0: 
		missed_detection_number = 0 #没有实际框，不存在漏检
		false_detection_number = len(pred_boxes) #这里假设预测结果为0，预测错误的数量也是0。        
	# 如果没有预测框，则全部漏检。
	# 如果标注框的数量为0，则没有漏检，len(target_labels) = 0，返回的就是0, 0
	elif len(pred_boxes) == 0:
		missed_detection_number = len(target_boxes)
		false_detection_number = 0  #没有预测框，不存在错检

	# 思路为：遍历每个检测框，与所有标注框进行iou计算，取最大的iou值，及其索引号
	# 是因为已经有第一个检测框结果了，所以仍旧视为错检。此时错检数量+1，检测结果的总数仍旧不变。--也就是说，返回的检测总数，永远都是len(pred_labels)
	else:
		correct_num = 0 #初始化正确检测到的数量
		for pred_box in pred_boxes: #逐个遍历检测框
			pred_box = np.expand_dims(pred_box, axis=0).repeat(len(target_boxes), axis=0) #扩充pred_box的维度
			iou_data = bbox_iou(pred_box, target_boxes) #单个pred_box与多个target_boxes一次性计算iou
			iou = np.max(iou_data, axis=0) #取最大的iou值
			target_idx = np.argmax(iou_data) #取相应的索引号
			if iou >= iou_threshold:
				correct_num +=1
				if len(target_boxes) == 1: #如果只有一个目标框，则直接跳出
					break
				else: #否则需要删除找到的目标框数据，继续下一轮的匹配
					tmp = target_boxes.tolist()
					tmp.pop(target_idx) #标注框需要剔除掉已经匹配过的target_box
					target_boxes = np.array(tmp)
					# print('target_boxes', target_boxes)
		false_detection_number = detection_number - correct_num  #对错检的数量而言，其是检测数 减去 正确的检测数
		missed_detection_number = target_number - correct_num #对漏检的数量而言，其是实际总数 减去 正确的检测数
	return false_detection_number, missed_detection_number, detection_number, target_number

def create_legend(h, catid_name_dict):
	color = (255,255,255)
	font_size = np.floor(3e-2 * h + 0.5).astype('int32')
	if font_size * 2.5 * len(catid_name_dict) > h:
		font_size = np.floor(1e-2 * h + 0.5).astype('int32')
		print('进入此处', font_size)		
	maxlen = max([len(value) for value in catid_name_dict.values()])
	w = int(maxlen * font_size)
	img = Image.new('RGB',size = (w, h), color = color)
	draw = ImageDraw.Draw(img)
	each_h = font_size * 2.5        
	font = ImageFont.truetype("./simhei.ttf", size = font_size)
	draw.rectangle((1, 1, w-1, each_h* len(catid_name_dict)), fill = color, outline = 'black')
	draw.line((w//5, 1, w//5, each_h* len(catid_name_dict)), 'black')
	for i in range(len(catid_name_dict)):
		draw.line((1, each_h * (i + 1), w - 1, each_h *(i + 1)), 'black')
		label_size = draw.textsize(catid_name_dict[i], font)
		h_gap = each_h - label_size[1] #计算框高和字高之间的空隙
		draw.text((w//10 , each_h * (i+1) - label_size[1] - h_gap//2), str(i), 'black', font)
		draw.text((h_gap + w//5 , each_h * (i+1) - label_size[1] - h_gap//2), catid_name_dict[i], 'black', font)
	del draw
	return img

def create_top(img_size):#创建图片抬头标识
	w, h = img_size
	w = int(w * 2)
	color = (255,255,255)
	img = Image.new('RGB',size = (w, h//15), color = color)
	draw = ImageDraw.Draw(img)
	font_size = np.floor(2e-2 * w + 0.5).astype('int32')
	font = ImageFont.truetype("./simhei.ttf", size = font_size)
	draw.rectangle((1, 1, w-1, h//15-1), fill = color, outline = 'black')
	draw.line((w//2, 1, w//2, h//15-1), 'black')
	height = (h//15 -1 - font_size) // 2 #总框高减文本框高后除2，确保文本高度方向居中对齐
	draw.text((w//4 , height), 'predition', 'black', font)
	draw.text((3 * w//4 , height), 'original', 'black', font)
	del draw
	return img

def plot_boxes(img_path, boxes, catid_name_dict, color='yellow'):
	'''
	根据bbox画框
	'''
	img = Image.open(img_path).convert('RGB')
	img = ImageOps.exif_transpose(img)  #需增加该方法，确保读取出来的图片与肉眼所见图片相同
	w, h = img.size
	draw = ImageDraw.ImageDraw(img)
	font = ImageFont.truetype(font='./simhei.ttf',size=np.floor(2e-2 * w + 0.5).astype('int32'))
	for bbox in boxes: 
		if len(bbox) > 5: # 兼容检测结果
			bbox = [bbox[5] ,bbox[0],bbox[1],bbox[2] ,bbox[3]]
		cli_id = int(bbox[0]) 
		left = bbox[1]
		top = bbox[2]
		bottom = bbox[3]
		right = bbox[4]  
		# 画框框
		label = '{}'.format(cli_id)  #catid_name_dict[cli_id]
		label_size = draw.textsize(label, font)
		label = label.encode('utf-8')
		# print(label)
		
		if top - label_size[1] >= 0:
			text_origin = np.array([left, top - label_size[1]])
		else:
			text_origin = np.array([left, top + 1])
 
		draw.rectangle((left, top,bottom, right), outline=color,width=min(w, h) // 400 )
		draw.rectangle([tuple(text_origin), tuple(text_origin + label_size)],outline=color,width=min(w, h) // 400)
		draw.text(text_origin, str(label,'UTF-8'), fill='red', font=font) 
			
		# draw.rectangle((x, y,width, height), outline=color, width=2)   
		# font = ImageFont.truetype(font='model_data/simhei.ttf',size=np.floor(3e-2 * np.shape(img)[1] + 0.5).astype('int32'))
		# draw.text(text_origin, str(label,'UTF-8'), fill=(0, 0, 0), font=font)
	del draw
	# img.show()
	return img