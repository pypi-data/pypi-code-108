import os
import cv2
import glob
from PMTD.tools.PMTD.PMTD_predictor import PMTDDemo
from PMTD.tools.PMTD.inference import PlaneClustering
from PMTD.maskrcnn_benchmark.config import cfg
from PMTD.maskrcnn_benchmark.modeling.roi_heads.mask_head.inference import Masker


class PMTD:
    def __init__(self, merge_from_file, model_path, longer_size=1600, method="PlaneClustering", device="cuda"):
        self.merge_from_file = cfg.merge_from_file(merge_from_file)
        self.merge_from_list = cfg.merge_from_list([
            'MODEL.DEVICE', device,
            'MODEL.WEIGHT', model_path,
            'INPUT.MAX_SIZE_TEST', longer_size,
        ])
        if method == 'PlaneClustering':
            masker = PlaneClustering()
        else:
            masker = Masker(threshold=0.01, padding=1)

        self.model = PMTDDemo(
            cfg,
            masker=masker,
            confidence_threshold=0.5,
            show_mask_heatmaps=False,
        )

    def train(self, images_path, results_path, output_type="Image"):
        model = self.model
        im_names = glob.glob(os.path.join(images_path, '*.png')) + \
                   glob.glob(os.path.join(images_path, '*.jpg')) + \
                   glob.glob(os.path.join(images_path, '*.bmp')) + \
                   glob.glob(os.path.join(images_path, '*.jpeg')) + \
                   glob.glob(os.path.join(images_path, '*.JPG'))
        for img_path in im_names:
            print('image path == ', img_path)
            image = cv2.imread(img_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            if output_type == "Image":
                predictions = model.run_on_opencv_image(image)

                save_path = results_path + '/' + img_path.split('/')[-1]
                print(save_path)
                cv2.imwrite(save_path, predictions[:, :, ::-1])
                cv2.waitKey(0)
            else:
                predictions = model.compute_prediction(image)
                top_predictions = model.select_top_predictions(predictions)

                bboxes = top_predictions.bbox
                masks = top_predictions.extra_fields['mask']
                scores = top_predictions.extra_fields['scores']
                for bbox, mask, score in zip(bboxes, masks, scores):
                    print(bbox, mask[0], score)
                save_path = results_path + '/' + img_path.split('/')[-1]
                print(save_path)
                cv2.imwrite(save_path, predictions[:, :, ::-1])
