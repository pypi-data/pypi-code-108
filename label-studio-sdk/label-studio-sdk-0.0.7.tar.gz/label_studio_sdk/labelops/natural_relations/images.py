
from shapely import geometry

class NaturalRelations(object):

    def infer(self, predictions):
        return predictions


class BoundingBoxesNaturalRelations(NaturalRelations):

    def infer(self, prediction):
        bboxes = []
        for p in prediction['result']:
            v = p['value']
            bboxes.append((p['id'], geometry.box(
                minx=v['x'], miny=v['y'] - v['height'],
                maxx=v['x'] + v['width'], maxy=v['y']
            )))
        relations = []
        for i, (pred_i_id, bbox_i) in enumerate(bboxes):
            for j, (pred_j_id, bbox_j) in enumerate(bboxes):
                if i == j:
                    continue
                if bbox_i.within(bbox_j):
                    relations.append({
                        'type': 'relation',
                        'from_id': pred_i_id,
                        'to_id': pred_j_id,
                        'labels': ['within'],
                        'direction': 'right'
                    })
                if bbox_i.overlaps(bbox_j):
                    relations.append({
                        'type': 'relation',
                        'from_id': pred_i_id,
                        'to_id': pred_j_id,
                        'labels': ['overlaps'],
                        'direction': 'right'
                    })
        new_prediction = prediction  # todo: deepcopy
        new_prediction['result'].extend(relations)
        return new_prediction
