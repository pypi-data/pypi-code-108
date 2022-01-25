
import logging.handlers
import sys,os
# import torch
import traceback
import numpy as np, math, time
from tqdm  import tqdm
import multiprocessing, threading #引入多进程模块
 
from terminaltables import AsciiTable
from datatools.eva.det.utils.utils import get_ann, image_detection, init_log, load_json, get_file_names, get_pre_data, get_class, plot_boxes, create_legend, create_top
# image_false_detection, image_missed_detection, image_object_detection

from datatools.eva.det.utils.voc_xml import gen_voc_xml,gen_object
 
logger = logging.getLogger(__name__) 
  
			  
def evaluate_image_score(predicted_file_json_path: str, gold_json_file_path: str, iou_threshold: float,
									 false_detection_weight: float,
									 missed_detection_weight: float, object_detection_weight: float):
	""" calculate the  image score by the predicted and gold json file """
	try:
		gt_data = load_json(gold_json_file_path)  #gt_data的数据中，是(x1,y1,w, h)
		pred_data = load_json(predicted_file_json_path)
		#id_file_name是字典，id: filename
		#file_name_id与id_file_name相反， filename:id
		id_file_name,file_name_id = get_file_names(gt_data['images'])
		#class_name_list是将所有类别名称，用列表表示
		#class_name_dict是字典格式，将类别名称与id号进行关联映射，类别名称：id
		#catid_name_dict与class_name_dict相反，id: 类别名称
		class_name_list,class_name_dict,catid_name_dict = get_class(gt_data)
		
		pred_data = get_pre_data(pred_data,file_name_id,class_name_dict)
		# load the names of categories  

		ap_table = [["category","false detection rate", "missed detection rate", "object detection correct rate","image score"]]
		
		sum_false_detection_rate = 0
		sum_missed_detection_rate = 0
		sum_object_detection_correct_rate = 0
		sum_image_score = 0
		bad_cases = []
		for class_name in class_name_list:  #逐个遍历类别，统计每个类别的检测结果。
			# traverse the images, a batch of one picture
			false_detection_count = 0
			detection_total_count = 0
			missed_detection_count = 0
			gold_total_count = 0
			object_detection_correct_count = 0
			object_detection_total_count = 0
			
			for i in range(len(gt_data['images'])):
				image_id = gt_data['images'][i]['id']
				# load gold annotations，ann_gt = n * [cls_id, x1, y1, x2, y2]
				ann_gt = get_ann(image_id, gt_data['annotations'])
				# load predicted annotations，ann_pred = n * [x1, y1, x2, y2, pred_score, cls_id]
				ann_pred = get_ann(image_id, pred_data)  #要注意ann_pred的数据格式，与ann_gt略有不同
				# sort the ann pred list by the confidence pred scores in a descending order
				# predicted no_wear boxes and labels
				if len(ann_pred) == 0:
					pred_no_wear_indices, pred_labels, pred_boxes = [], [], []
				else:
					#获取预测类别为class_name的矩形框数据索引号，即第几个数据为指定类别
					pred_no_wear_indices = np.where(ann_pred[:, 0] == class_name_dict[class_name])
					pred_boxes = ann_pred[:, 1:][pred_no_wear_indices]
	
				# target no_wear boxes and labels
				if len(ann_gt) == 0:
					target_no_wear_indices, target_labels, target_boxes = [], [], []
				else:
					target_no_wear_indices = np.where(ann_gt[:, 0] == class_name_dict[class_name])
					target_boxes = ann_gt[:, 1:][target_no_wear_indices]
				false_detection_number, missed_detection_number, detection_number, target_number = image_detection(pred_boxes=pred_boxes, target_boxes=target_boxes, iou_threshold=iou_threshold) 
				object_detection_correct_number = target_number - missed_detection_number

				false_detection_count += false_detection_number
				detection_total_count += detection_number

				missed_detection_count += missed_detection_number
				gold_total_count += target_number

				object_detection_correct_count += object_detection_correct_number
				object_detection_total_count += target_number                

				if false_detection_number > 0 or missed_detection_number >0:
					bad_cases.append(image_id)

			false_detection_rate = round(false_detection_count / detection_total_count, 4) if (detection_total_count != 0) else 0
			missed_detection_rate = round(missed_detection_count / gold_total_count,4) if (gold_total_count != 0) else 0
			object_detection_correct_rate = round(object_detection_correct_count / object_detection_total_count, 4) if (object_detection_total_count != 0) else 0
			logger.info('checking the class of {}'.format(class_name))
			logger.info("false_detection_rate: {} / {} = {}".format(false_detection_count, detection_total_count,false_detection_rate))
			logger.info("missed_detection_rate: {} / {} = {}".format(missed_detection_count, gold_total_count, missed_detection_rate))
			logger.info("object_detection_correct_rate: {} / {} = {}".format(object_detection_correct_count,object_detection_total_count, object_detection_correct_rate))
	
			image_score = round(1 - (false_detection_weight * false_detection_rate + missed_detection_weight * missed_detection_rate + object_detection_weight * (1 - object_detection_correct_rate)), 4)
	
			logger.info("evaluation for {} and {}\n".format(predicted_file_json_path, gold_json_file_path))
			
			ap_table += [[class_name,false_detection_rate, missed_detection_rate, object_detection_correct_rate, image_score]]
			
			sum_false_detection_rate = sum_false_detection_rate + false_detection_rate
			sum_missed_detection_rate = sum_missed_detection_rate + missed_detection_rate
			sum_object_detection_correct_rate = sum_object_detection_correct_rate + object_detection_correct_rate
			sum_image_score = sum_image_score + image_score  
		ap_table += [['total',round(sum_false_detection_rate/len(class_name_list),4), round(sum_missed_detection_rate/len(class_name_list),4), 
					  round(sum_object_detection_correct_rate/len(class_name_list),4), round(sum_image_score/len(class_name_list),4)]]
		
		logger.info("\n{}\n".format(AsciiTable(ap_table).table))  
		 
		return float('{:.8f}'.format(sum_image_score/len(class_name_list))), "评测成功",list(set(bad_cases))
	except Exception as e:
		return -1, "格式错误",[]
	except AssertionError:
		_, _, tb = sys.exc_info()
		traceback.print_tb(tb)
		tb_info = traceback.extract_tb(tb)
		filename, line, func, text = tb_info[-1]

		logger.info('an error occurred on line {} in statement {}'.format(line, text))

		return -1, "格式错误",[]


def entrance(predicted_file_json_path: str, gold_json_file_path: str): 
	score, message,bad_cases = evaluate_image_score(predicted_file_json_path=predicted_file_json_path, gold_json_file_path=gold_json_file_path, iou_threshold=0.5, false_detection_weight=0.3, missed_detection_weight=0.5, object_detection_weight=0.2)
	if message != "评测成功":
		status = 0
	else:
		status = 1

	return score, message, status,bad_cases

def processing_treat(func, predicted_file_json_path,gold_json_file_path,bad_cases,origin_image_file_path,output_image_file_path):
	process_num = os.cpu_count()
	NUMS = len(bad_cases)
	num_part = math.ceil(NUMS / process_num) #计算每个进程要处理的最大数据量
	#需要根据线程数，确定每个线程所需生成的数据量
	temp_t = []
	for thread_num in range(process_num):
		new_bad_cases = bad_cases[thread_num * num_part: (thread_num +1) * num_part]
		t = multiprocessing.Process(target = func, args = (predicted_file_json_path,gold_json_file_path,new_bad_cases,origin_image_file_path,output_image_file_path))
		temp_t.append(t)
		t.start()
	for t in temp_t:
		t.join()

def gen_img_badcase(predicted_file_json_path: str, gold_json_file_path: str,bad_cases: list,origin_image_file_path:str,output_image_file_path:str): 
	'''				
	生成badcase (拼接图片)
	''' 
	import skimage.io as io
	gt_data = load_json(gold_json_file_path)
	pred_data = load_json(predicted_file_json_path)
	id_file_name,file_name_id = get_file_names(gt_data['images']) 
	class_name_list,class_name_dict,catid_name_dict = get_class(gt_data)
	pred_data = get_pre_data(pred_data,file_name_id,class_name_dict) 
	for image_id in tqdm(bad_cases):
		ann_gt = get_ann(image_id, gt_data['annotations']) 
		origin_image_path = os.path.join(origin_image_file_path,id_file_name[image_id])#step 2原始的coco的图像存放位置
		origin_draw_img = plot_boxes(origin_image_path,ann_gt, catid_name_dict) 
		ori_size = origin_draw_img.size
		legend= create_legend(ori_size[1], catid_name_dict) #创建标签图片
		pj1 = np.zeros((ori_size[1], ori_size[0]*2 + legend.size[0] ,3), dtype= np.uint8)   #横向拼接
		pj1[:,ori_size[0]: ori_size[0] * 2,:] = origin_draw_img  #原始图片在中间
		pj1[:,ori_size[0] * 2 : ,:] = legend  #标签铭牌在右    
		del origin_draw_img, legend  #为减少内存占用，事先提早删除不必要的数组

		ann_pred = get_ann(image_id, pred_data)
		pred_draw_img = plot_boxes(origin_image_path,ann_pred, catid_name_dict) 
		pj1[:,:ori_size[0],:] = pred_draw_img    #预测图片在左        
		del pred_draw_img

		top = create_top(ori_size) #增加抬头标题， top是Image的格式，形状是W * H
		final = np.ones((top.size[1] + pj1.shape[0], pj1.shape[1], 3),dtype=np.uint8) * 255 #H * W * 3的形状
		final[:top.size[1], : top.size[0],:] = top
		final[top.size[1]:, :, :] = pj1
		del pj1
		final=np.array(final,dtype=np.uint8)
		output_image = os.path.join(output_image_file_path,id_file_name[image_id])
		io.imsave(output_image, final)   #保存拼接后的图片
		del final, top

def gen_voc_badcase(predicted_file_json_path: str, gold_json_file_path: str,bad_cases: list,origin_image_file_path:str,output_voc_file_path:str): 
	'''
	生成voc
	'''  
	gt_data = load_json(gold_json_file_path)
	pred_data = load_json(predicted_file_json_path)
	id_file_name,file_name_id = get_file_names(gt_data['images']) 
	class_name_list,class_name_dict,catid_name_dict = get_class(gt_data)
	pred_data = get_pre_data(pred_data,file_name_id,class_name_dict) 
	id_img_dict = { img_info['id']:img_info for img_info in gt_data['images']}
	for image_id in tqdm(bad_cases):
		objs = []
		#_, ann_gt = get_ann(image_id, gt_data['annotations'])  
		img_info = id_img_dict[image_id]
		ann_pred = get_ann(image_id, pred_data)  
		for ann in ann_pred:
			xmin = int(ann[1])
			ymin = int(ann[2])
			xmax = int(ann[3])
			ymax = int(ann[4])
			
			obj = gen_object(catid_name_dict[int(ann[0])],xmin,ymin,xmax,ymax)
			objs.append(obj)
		xml_name = os.path.splitext(id_file_name[image_id])[0]  + '.xml'
		xml_name = os.path.join(output_voc_file_path,xml_name)
		gen_voc_xml(img_info['file_name'],objs,img_info['width'],img_info['height'],xml_name) 
		
def eva(args):
	# initialize log output configuration
	init_log(logging.INFO)

	# set predicted and gold json file paths
	predicted_file_json_path = args.contestant_submitted_file_name
	gold_json_file_path = args.gold_json_file_path
	origin_image_file_path = args.origin_image_file_path
	output_image_file_path = args.output_image_file_path
	output_voc_file_path = args.output_voc_file_path
	 
	logger.info('predicted_file_json_path: {}'.format(predicted_file_json_path))
	logger.info('gold_json_file_path: {}'.format(gold_json_file_path))
	logger.info('origin_image_file_path: {}'.format(origin_image_file_path))
	logger.info('output_image_file_path: {}'.format(output_image_file_path))
	logger.info('output_voc_file_path: {}'.format(output_voc_file_path))
	
	score, message, status,bad_cases = entrance(predicted_file_json_path=predicted_file_json_path,
									   gold_json_file_path=gold_json_file_path)
	t1 = time.time()
	if output_image_file_path:
		os.makedirs(output_image_file_path,exist_ok = True)
		gen_img_badcase(predicted_file_json_path,gold_json_file_path,bad_cases,origin_image_file_path,output_image_file_path)
		# processing_treat(gen_img_badcase, predicted_file_json_path,gold_json_file_path,bad_cases,origin_image_file_path,output_image_file_path)# 
		
	if output_voc_file_path:
		os.makedirs(output_voc_file_path,exist_ok = True)
		gen_voc_badcase(predicted_file_json_path,gold_json_file_path,bad_cases,origin_image_file_path,output_voc_file_path)
		# processing_treat(gen_voc_badcase, predicted_file_json_path,gold_json_file_path,bad_cases,origin_image_file_path,output_voc_file_path)
	print('time cost:', time.time() - t1)
if __name__ == "__main__":
	from utils.options import args_parser
	args = args_parser()
	eva(args)
