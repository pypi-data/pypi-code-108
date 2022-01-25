import json


def classes_filter(gt_data, filted_file, classes_names):
    new_gt_data = {}
    categories = []
    for each in gt_data['categories']:
        if each['name'] in classes_names:
            categories.append(each)
    classes = {each['id']: each['name'] for each in categories}#这里是获取原始完整类别中的所需类别名称及其id，没有改动原始id编号
    for each in categories:
        classes[each['id']] = each['name']
    annotations = []
    for each in gt_data['annotations']:#根据相应的类别名称，过滤出来所需的类别标签内容
        if each['category_id'] in classes.keys():
            annotations.append(each)
    new_gt_data['images'] = gt_data['images'] #这里是直接使用完整的图片路径
    new_gt_data['type'] = gt_data['type']
    new_gt_data['annotations'] =annotations
    new_gt_data['categories'] = categories
    with open(filted_file, 'w', encoding='utf8') as f:
        json.dump(new_gt_data, f, ensure_ascii=False, indent=4)
        
gold_json_file_path = r'D:/projects/choices/train.json' #完整的classes类别转换出来的json文件
gt_data = load_json(gold_json_file_path) #按照原定义的方法，进行加载json文件
filted_file = 'D:/projects/choices/test.json' #过滤类别后的新的json文件名称---其实可以和上面的json文件一致，直接覆盖原始文件
classes_names = ['operatingbar', 'wrongclothes', 'wrongglove','powerchecker', 'signboard'] #所需的类别名称
classes_filter(gt_data, filted_file, classes_names) #过滤后，将文件保存下来
