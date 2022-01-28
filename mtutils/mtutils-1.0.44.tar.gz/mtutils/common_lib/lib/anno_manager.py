#
# Annotation manager
#
from .utils import decode_distribution
from .utils import decode_labelme_shape
from .utils import encode_distribution
from .utils import encode_labelme_shape
from .utils import create_uuid
import numpy as np

def logging(func):
    def wrapper(*args, **kw):
        res = func(*args, **kw)
        print("----------------")
        print("{}():".format(func.__name__))
        print("Inputs:")
        for idx, arg in enumerate(args[1:]):
            print("\targ{} = {}".format(idx+1, arg))
        for key, val in kw.items():
            print("\t{} = {}".format(key, val))
        print("Return: \n\t{}".format(res))
        print("----------------\n\n")
        return res
    return wrapper


class AnnotationManager(object):
    def __init__(self, class_dict=[]):
        """ class_dict could be get from the data manager object """
        assert isinstance(class_dict, (list, tuple))
        self._class_dict = sorted(class_dict, key=lambda x: x['class_id'])
        self._class2label_global = {x['class_name']:x['class_id'] for x in class_dict}
        self._label2class_global = {x['class_id']:x['class_name'] for x in class_dict}

        self._all_classes = [x['class_name'] for x in self._class_dict]
        self._leaf_classes = self.__get_leaf_classes(class_dict)
        self._OK_classname = 'OK'  # class name for OK (in DataManager, we don't save OK as a class in distribution)

        # initialize class object
        self.setup_distribution_type(distribution_type='detection', distribution_classes=self._leaf_classes)

    @property
    def classnames(self):
        return self._distribution_classes

    def __get_leaf_classes(self, class_dict):
        # 1) collect all parent classnames
        nonleaf_classes = set([x['parent'] for x in class_dict if x['parent'] is not None])
        leaf_classes = list()
        for x in self._class_dict:
            if x['class_name'] not in nonleaf_classes:
                leaf_classes.append(x['class_name'])
        return leaf_classes

    def __check_classes_conflict(self, classname_list):
        """ because we have parent classes, this function checks if there are parent class
            and its child class in the classname_list.
        """
        # loop over classname_list to check if one's parent is also in classname_list
        for classname in classname_list:
            if classname == self._OK_classname:
                continue
            parent = 'WHAT THE FUCK'
            child  = classname
            while parent is not None:
                classid_global = self._class2label_global[child]
                parent = self._class_dict[classid_global]['parent']
                if parent in classname_list:
                    raise RuntimeError("(WARNING) conflict class pair found: ({}, {})".format(child, parent))
                child = parent

    # @logging
    def setup_distribution_type(self, distribution_type=None, distribution_classes=None):
        """
        :distribution_type: string, there're 3 modes: 'multilabel' (default), 'multiclass' and 'detection'
        :distribution_classes: list of strings, the output distribution that indicates the relations between class names and labels
        """
        if distribution_classes is not None:
            assert isinstance(distribution_classes, (list, tuple))
        else:
            distribution_classes = self._distribution_classes

        if distribution_type is None:
            distribution_type = self._distribution_type

        if None: pass
        elif distribution_type in ['multilabel', 'multi-label']:
            self._distribution_type = 'multilabel'
            self._distribution_classes = distribution_classes

        elif distribution_type in ['multiclass', 'multi-class', 'seg', 'segmentation']:
            self.__check_classes_conflict(distribution_classes)
            self._distribution_type = 'multiclass'
            self._distribution_classes = distribution_classes

        elif distribution_type in ['detection', 'det']:
            self.__check_classes_conflict(distribution_classes)
            self._distribution_type = 'detection'
            self._distribution_classes = distribution_classes

        else:
            raise RuntimeError('Unknown distribution type: {}'.format(distribution_type))

        self._class2label = {name:label for label, name in enumerate(self._distribution_classes)}
        self._label2class = {label:name for label, name in enumerate(self._distribution_classes)}


    def __guess_object_type(self, obj):
        """
        get_xxx() method series take an ambiguous object as their major input.
        this function returns a type guess about the object for them, by checking their type
        """
        exception = RuntimeError("Illegible object type ({}): {}".format(type(obj), obj))
        if isinstance(obj, str):
            return 'classname'
        elif isinstance(obj, (int, np.int32, np.int64)):
            return 'classid'
        elif isinstance(obj, dict):
            if 'instances' in obj:
                return 'record'
            else:
                return 'instance'
        elif isinstance(obj, (tuple, list)):
            if len(obj) == 0:
                return 'empty-list'
            elif isinstance(obj[0], (tuple, list)):
                return 'list-list'
            elif isinstance(obj[0], str):
                return 'string-list'
            elif isinstance(obj[0], (float, int)):
                return 'number-list'
            elif isinstance(obj[0], dict):
                key_type = self.__guess_object_type(obj[0])
                return '{}-list'.format(key_type)
            else:
                raise exception
        else:
            raise exception


    # @logging
    def get_classid(self, obj):
        """
        :obj: could be a distribution, record, instance of list, instances or a class name
        return [] (if no instance or matched class name), or class id in current distribution type
        """
        obj_type = self.__guess_object_type(obj)
        if obj_type == 'number-list':    # we assume this is a distribution
            distribution = obj
            return [class_id for class_id, score in enumerate(distribution) if score > 0]
        elif obj_type == 'list-list':    # we assume this is a list of distribution
            distribution_list = obj
            return [self.get_classid(distribution) for distribution in distribution_list]
        else:
            distributions = self.get_distribution(obj)
            assert len(distributions) > 0
            if isinstance(distributions[0], list):  # if returns a list of distribution
                return [self.get_classid(distribution) for distribution in distributions]
            else:
                distribution = distributions
                return self.get_classid(distribution)

    
    # @logging
    def get_classname(self, obj):
        """
        :obj: could be a distribution, record, instance of list, instances or a class label (in distribution classes format)
        return [] (if no instance or matched class name), or class id in current distribution type
        """
        eps = 1e-8
        obj_type = self.__guess_object_type(obj)
        if None: pass
        elif obj_type == 'classid':
            classid = obj
            return self._label2class[classid]
        elif obj_type == 'number-list':    # we assume this is a distribution
            distribution = np.array(obj)
            assert len(distribution) == len(self._distribution_classes)
            if self._distribution_type == 'multilabel':
                return [self.get_classname(classid) for classid, score in enumerate(distribution) if score > 0]
            else:
                max_score = np.max(distribution)
                return [self.get_classname(classid) for classid, score in enumerate(distribution) if (score == max_score) and (max_score > eps)]
        elif obj_type == 'list-list':     # we assume this is a list of distribution
            distribution_list = obj
            return [self.get_classname(distribution) for distribution in distribution_list]
        elif obj_type == 'empty-list':    # we assume this is from the empty instance of a OK record: rec['instances']
            if self._distribution_type == 'detection':
                return []
            else:
                return [self._OK_classname]
        else:
            distributions = self.get_distribution(obj)
            assert len(distributions) > 0
            if isinstance(distributions[0], list):  # if returns a list of distribution
                return [self.get_classname(distribution) for distribution in distributions]
            else:
                distribution = distributions
                return self.get_classname(distribution)


    # @logging
    def get_score(self, obj):
        """
        :obj: could be a record, distribution (list), a instance (list)
        return [] (if no instance or matched class name), or class id in current distribution type
        """
        obj_type = self.__guess_object_type(obj)
        if obj_type == 'number-list':    # we assume this is a distribution
            distribution = obj
            return [score for class_id, score in enumerate(distribution) if score > 0]
        elif obj_type == 'list-list':    # we assume this is a list of distribution
            distribution_list = obj
            return [self.get_score(distribution) for distribution in distribution_list]
        else:
            distributions = self.get_distribution(obj)
            return self.get_score(distributions)


    # @logging
    def get_distribution(self, obj):
        """
        :obj: could be a record, instance of list, instances
        return a probability distribution defined by distribution classes
        """
        obj_type = self.__guess_object_type(obj)
        if None: pass
        elif obj_type == 'classname':
            classname = obj
            distribution = [0] * len(self._distribution_classes)
            distribution[self._class2label[classname]] = 1
            return distribution
        elif obj_type == 'string-list':  # we assume this is a classname list
            classname_list = obj
            distribution = [0] * len(self._distribution_classes)
            for classname in classname_list:
                distribution[self._class2label[classname]] = 1
            return distribution
        elif obj_type == 'empty-list':
            return [1 if x == self._OK_classname else 0 for x in self._distribution_classes]
        elif obj_type == 'record':
            record = obj
            return self.get_distribution(record['instances'])
        elif obj_type == 'instance':
            instance = obj
            distribution_global = decode_distribution(instance['distribution'])
            distribution_target = list()
            ok_score = None
            for classname in self._distribution_classes:
                if classname == self._OK_classname:
                    ok_score = score = 0
                else:
                    score = distribution_global[self._class2label_global[classname]]
                distribution_target.append(score)
            if ok_score is not None:
                assert ok_score == 0
                ok_score = max(0, 1-sum(distribution_target))
                ok_id = self._class2label[self._OK_classname]
                distribution_target[ok_id] = ok_score
            return distribution_target
        elif obj_type == 'instance-list':
            instances = obj
            distributions = [self.get_distribution(inst) for inst in instances]
            if self._distribution_type in ['multiclass', 'multilabel']:  # in classification mode, squeeze to a single distribution
                distribution = np.max(distributions, axis=0)
                return distribution.tolist()
            else:
                return distributions
        else:
            raise RuntimeError("Unknown type: {} is a {}".format(obj, obj_type))


    # @logging
    def get_xyxy(self, obj):
        """
        :obj: could be a record, instance of list, instances
        return a bbox or a list of bboxes, or None if shape_type = None
        """
        obj_type = self.__guess_object_type(obj)
        if obj_type == 'empty-list':
            return []
        elif obj_type == 'instance-list':
            instances = obj
            return [self.get_xyxy(inst) for inst in instances]
        elif obj_type == 'record':    # we assume this is a list of distribution
            record = obj
            return self.get_xyxy(record['instances'])
        elif obj_type == 'instance':
            instance = obj
            if instance['shape_type'] is None:
                print("Warning: you are trying to extract bboxes from classification predictions/annotation")
                return None
            else:
                points = decode_labelme_shape(instance['points'])
                points = np.reshape(points, [-1,2])
                x1,y1,x2,y2 = points[:,0].min(), points[:,1].min(), points[:,0].max(), points[:,1].max()
                return [x1,y1,x2,y2]
        elif obj_type == 'number-list':
            if len(obj) == 4:
                # is a xyxy
                return obj
            else:
                raise RuntimeError("bad bumber_list: {}".format(obj))
        else:
            raise RuntimeError("Unknown type: {}".format(obj))

    
    # @logging
    def get_xywh(self, obj):
        """
        :obj: could be a record, instance of list, instances
        return a bbox or a list of bboxes, or None if shape_type = None
        """
        xyxy = self.get_xyxy(obj)
        if None: pass
        elif xyxy is None or len(xyxy) == 0:
            return xyxy
        elif isinstance(xyxy[0], list):
            return [self.get_xywh(bbox) for bbox in xyxy]
        else:
            x1,y1,x2,y2 = xyxy
            return [x1,y1,x2-x1,y2-y1]


    # @logging
    def get_polygon(self, obj):
        """
        :obj: could be a record, instance of list, instances
        return a bbox or a list of bboxes
        """
        obj_type = self.__guess_object_type(obj)
        if obj_type == 'empty-list':
            return []
        elif obj_type == 'instance-list':
            instances = obj
            return [self.get_polygon(inst) for inst in instances]
        elif obj_type == 'record':    # we assume this is a list of distribution
            record = obj
            return self.get_polygon(record['instances'])
        elif obj_type == 'instance':
            instance = obj
            if None: pass
            elif instance['shape_type'] is None:
                print("Warning: you are trying to extract bboxes from classification predictions/annotation")
                return None
            elif instance['shape_type'] == 'polygon':
                points = decode_labelme_shape(instance['points'])
                points = np.reshape(points, [-1,2])
                return points.tolist()
            elif instance['shape_type'] == 'rectangle':
                x1,y1,x2,y2 = decode_labelme_shape(instance['points'])
                return [[x1,y1],[x1,y2],[x2,y2],[x2,y1],[x1,y1]]
            else:
                raise RuntimeError("Unknown shape type: {}".format(instance['shape_type']))
        else:
            raise RuntimeError("Unknown type: {}".format(obj))


    def _extend_distribution(self, distribution_global, exclude_classes=[]):
        """ extend the global distribution: fill parents with their maximal child """
        for child_id, child_score in enumerate(distribution_global):
            # trace back to root class
            parent = self._class_dict[child_id]['parent']
            while parent is not None:
                parent_id = self._class2label_global[parent]
                parent_score = distribution_global[parent_id]
                if parent not in exclude_classes:
                    distribution_global[parent_id] = max(child_score, parent_score)  # update parent score
                parent = self._class_dict[parent_id]['parent']   # update parent
                child_score = max(child_score, parent_score)     # update child_score
        return distribution_global


    # @logging
    def create_instance(self, obj, score=1, shape=[]):
        """
        :obj: could be a distribution (list) and class_name
        return a bbox or a list of bboxes
        """
        # create distribution
        if None: pass
        elif isinstance(obj, (list, np.ndarray)):
            distribution = list(obj)
            assert len(distribution) == len(self._distribution_classes)
            distribution_global = [0]*len(self._all_classes)
            for class_id, sc in enumerate(distribution):
                class_name = self._label2class[class_id]
                if class_name == self._OK_classname:  # skip ok probability
                    continue
                class_id_global = self._class2label_global[class_name]
                distribution_global[class_id_global] = sc
                distribution_global = self._extend_distribution(distribution_global, exclude_classes=self._distribution_classes)
        elif isinstance(obj, str):
            class_name = obj
            distribution_global = [0]*len(self._all_classes)
            if class_name != self._OK_classname:  # skip ok probability
                class_id_global = self._class2label_global[class_name]
                distribution_global[class_id_global] = score
                distribution_global = self._extend_distribution(distribution_global, exclude_classes=[class_name])
        else:
            raise RuntimeError("Unknown type: {}".format(obj))


        # create shape
        shape_type = 'polygon'
        assert isinstance(shape, (list, tuple, np.ndarray))
        if None: pass
        elif len(shape) == 0:
            assert self._distribution_type != 'detection'
            shape_type = None
            points = []
        elif len(shape) == 2:
            assert isinstance(shape[0], (list, tuple, np.ndarray))
            (x1,y1),(x2,y2) = shape[0], shape[1]
            points = [[x1,y1],[x1,y2],[x2,y2],[x2,y1],[x1,y2]]
        elif len(shape) == 4:
            # assert isinstance(shape[0], (int, float, np.float32))
            mark_list = [not hasattr(item, '__iter__') for item in shape]
            if all(mark_list):
                x1, y1, x2, y2 = shape
                points = [[x1, y1], [x1, y2], [x2, y2], [x2, y1], [x1, y2]]
            elif not any(mark_list):
                points = [[x, y] for x, y in shape]
            else:
                raise RuntimeError("Invalid shape: {}".format(shape))
        elif len(shape) >= 3:
            points = [[x, y] for x, y in shape]
        else:
            raise RuntimeError("Invalid shape: {}".format(shape))

        instance = {
            'uuid': create_uuid(),
            'distribution': encode_distribution(distribution_global),
            'shape_type': shape_type,
            'points': encode_labelme_shape(points)
        } 

        return instance

    def show(self, image, obj, thickness=2, visual=True):
        """
        [show annotations on input image]
        Args:
            image ([numpy]): [input image]
            obj ([record, [instance], instance]): [could be a record, instance of list, instances]
        """

        import cv2
        color_list = [(159, 2, 98), (95, 32, 219), (222, 92, 189), (56, 233, 120), (23, 180, 100), (78, 69, 20), (97, 202, 39), (65, 179, 135), (163, 159, 219)]

        image = image.copy()

        old_dist_type = self._distribution_type
        self.setup_distribution_type(distribution_type='detection')
        polygon_list = self.get_polygon(obj)
        classname_list = self.get_classname(obj)
        self.setup_distribution_type(distribution_type=old_dist_type)

        obj_type = self.__guess_object_type(obj)

        if obj_type == 'instance':
            polygon_list = [polygon_list]
            classname_list = [classname_list]

        for polygon, class_name in zip(polygon_list, classname_list):
            class_id = self.get_classid(class_name)[-1]
            color = color_list[class_id % len(color_list)][1]
            # cv2.fillPoly(image, [np.array(polygon).astype('int32')], color)
            cv2.polylines(image, [np.array(polygon).astype('int32')], True, color, thickness=thickness)

        if visual:
            import matplotlib.pyplot as plt
            plt.figure()
            plt.imshow(image)
            plt.show()

        return image
