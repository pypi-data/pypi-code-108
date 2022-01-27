from lib.data_manager import DataManager
from lib.anno_manager import AnnotationManager
from copy import deepcopy

class_dict = [
    {'class_id': 0, 'class_name': 'NG', 'parent': None},
    {'class_id': 1, 'class_name': 'word', 'parent': None},
    {'class_id': 2, 'class_name': 'number', 'parent': 'word'},
    {'class_id': 3, 'class_name': 'character', 'parent': 'word'},
    {'class_id': 4, 'class_name': 'dirt', 'parent': 'NG'},
    {'class_id': 5, 'class_name': 'dent', 'parent': 'NG'},
    {'class_id': 6, 'class_name': 'scratch', 'parent': 'NG'},
]

## Easy annotation generation
am = AnnotationManager(class_dict)


#
# detection mode
#
assert am._distribution_classes == am._leaf_classes
assert am._distribution_type == 'detection'
am.setup_distribution_type(
    distribution_classes = ['dirt', 'dent', 'number']
)
assert am._distribution_type == 'detection'
distribution_classes = deepcopy(am._distribution_classes)

assert len(am.get_classname([])) == 0
assert set(['dent']) == set(am.get_classname([0, 1, 0]))
assert set(['number']) == set(am.get_classname([0,.2,.3]))
assert set(['dirt', 'dent']) == set(am.get_classname([.2,.2,.13]))

try:
    am.setup_distribution_type(distribution_classes = ['dirt', 'dent', 'NG'])
except Exception as e:
    print("DETECTION MODE: ", e)
else:
    raise RuntimeError("Class conflict should be detected but it is not")




#
# multiclass mode
#
am.setup_distribution_type(
    distribution_type = 'multiclass',
    distribution_classes = ['dirt', 'dent', 'word']
)

assert set(['OK']) == set(am.get_classname([]))
assert set(['dent']) == set(am.get_classname([0,1,0]))
assert set(['word']) == set(am.get_classname([.1,.1,.8]))



am.setup_distribution_type(
    distribution_classes = ['OK', 'dirt', 'dent', 'word']
)
assert set(['OK']) == set(am.get_classname([.5,0,.2,.3]))
assert set(['OK', 'word']) == set(am.get_classname([.3,.2,.2,.3]))



try:
    am.setup_distribution_type(
        distribution_classes = ['dirt', 'dent', 'NG']
    )
except Exception as e:
    print("MULTICLASS MODE: ", e)
else:
    raise RuntimeError("Class conflict should be detected but it is not")


