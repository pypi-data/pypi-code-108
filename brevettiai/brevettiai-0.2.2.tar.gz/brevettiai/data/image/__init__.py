class ImageKeys:
    BOUNDING_BOX = "bbox"
    ZOOM = "zoom_factor"
    SIZE = "size"
    INSIDE_POINTS = "inside_points"
    BBOX_SIZE_ADJUST = "bbox_size_adjust"
    ANNOTATION = "segmentation_path"

try:
    from .image_pipeline import ImagePipeline
    from .segmentation_loader import SegmentationLoader
    from .image_augmenter import ImageAugmenter
except Exception:
    pass
