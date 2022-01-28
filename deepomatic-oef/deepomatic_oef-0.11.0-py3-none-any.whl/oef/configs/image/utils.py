def fixed_shape_resizer(width, height):
    return {'fixed_shape_resizer': {'convert_to_grayscale': False, 'height': height, 'resize_method': 'BILINEAR', 'width': width}}


def keep_aspect_ratio_resizer(min_size, max_size):
    return {'keep_aspect_ratio_resizer': {'convert_to_grayscale': False, 'max_dimension': max_size, 'min_dimension': min_size, 'pad_to_max_dimension': False, 'per_channel_pad_value': None, 'resize_method': 'BILINEAR'}}
