import numpy
from PyQt5.QtWidgets import QWidget, QScrollBar, QVBoxLayout, QLabel
from PyQt5.QtGui import QImage, QPixmap, QResizeEvent
from PyQt5.QtCore import Qt

__all__ = ['normalize_image', 'convert_numpy_to_qimage', 'ImageWidget']


def normalize_image(image: numpy.ndarray) -> numpy.ndarray:
    """
    Normalize a NumPy array to the range [0, 255].

    Args:
        image: A 2D or 3D NumPy array.

    Returns:
        A normalized 2D or 3D NumPy array.
    """
    # copy and normalize image
    max_val = numpy.maximum(2e-15, image.max())
    min_val = numpy.maximum(1e-15, image.min())

    image = image.copy().astype(numpy.float32)
    image = 255 * (image - min_val) / (max_val - min_val)
    image = image.astype(numpy.uint8)

    return image


def __convert_numpy_to_qimage_2d(image: numpy.ndarray) -> QImage:
    """
    Convert a 2D NumPy array to a QImage.
    Supportsgrayscale images.

    Args:
        image: A 2D or 3D NumPy array.

    Returns:
        A QImage.
    """

    image_i = image.copy()
    return QImage(image_i.data, image_i.shape[1], image_i.shape[0],
                  image_i.strides[0], QImage.Format_Grayscale8).copy()


def __convert_numpy_to_qimage_rgb(image: numpy.ndarray) -> QImage:
    """
    Convert a (x, y, 3) NumPy array to a QImage.
    Supports RGB images.

    Args:
        image: A 3D NumPy array.

    Returns:
        A RGB QImage.
    """
    image = image.copy()
    qimage = QImage(image.data, image.shape[1], image.shape[0], image.strides[0], QImage.Format_RGB888)
    # Create a copy to prevent crashes due to the data pointed at the QImage being deleted
    return qimage.copy()


def __convert_numpy_to_qimage_rgba(image: numpy.ndarray) -> QImage:
    """
    Convert a (x, y, 4) NumPy array to a QImage.
    Supports RGBA images.

    Args:
        image: A 3D NumPy array.

    Returns:
        A RGBA QImage.
    """
    image = image.copy()
    qimage = QImage(image.data, image.shape[1], image.shape[0], image.strides[0], QImage.Format_RGBA8888)
    # Create a copy to prevent crashes due to the data pointed at the QImage being deleted
    return qimage.copy()


def __convert_numpy_to_qimage_3d(image: numpy.ndarray, num_measurements: int) -> [QImage]:
    """
    Convert a (x, y, num_measurements) NumPy array to a list of QImages.
    Supports grayscale images.

    Args:
        image: A 3D NumPy array.
        num_measurements: The number of measurements in the 3rd NumPy array dimension.

    Returns:
        A list of 2D grayscale QImages.
    """
    # Return variable
    return_list = []
    # Convert image to QImage
    for i in range(num_measurements):
        image_i = image[..., i].copy()
        qimage = QImage(image_i.data, image_i.shape[1], image_i.shape[0],
                        image_i.strides[0], QImage.Format_Grayscale8)
        # Create a copy to prevent crashes due to the data pointed at the QImage being deleted
        return_list.append(qimage.copy())
    return return_list


def convert_numpy_to_qimage(image: numpy.array) -> [QImage]:
    """
    Convert a 2D or 3D NumPy array to a QImage.
    Supports RGB and grayscale images.

    Args:
        image: A 2D or 3D NumPy array.

    Returns:
        A list of QImages (one for each element in the 3rd NumPy array dimension).
    """
    image = normalize_image(image)

    # If there is only one channel (grayscale), mark it for the next iterations.
    if image.ndim == 2:
        return [__convert_numpy_to_qimage_2d(image)]

    num_measurements = image.shape[2]

    # RGB
    if num_measurements == 3:
        return [__convert_numpy_to_qimage_rgb(image)]
    # RGBA
    elif num_measurements == 4:
        return [__convert_numpy_to_qimage_rgba(image)]

    return __convert_numpy_to_qimage_3d(image, num_measurements)


class ImageWidget(QWidget):
    """
    A widget for displaying images.
    """
    def __init__(self):
        super().__init__()

        self.layout = None
        self.image_label = None
        self.image_scroll_bar = None
        self.image: [QImage] = None
        self.pixmap = None

        self.init_ui()

    def init_ui(self) -> None:
        """
        Initialize the UI.

        Returns:
            None
        """
        self.layout = QVBoxLayout()

        # Set a default image
        self.image = QImage(self.maximumWidth(), self.maximumHeight(),
                            QImage.Format_Grayscale8)
        self.image.fill(0)
        self.pixmap = QPixmap.fromImage(self.image)

        # This label will be used to display the image
        self.image_label = QLabel()
        self.image_label.setPixmap(self.pixmap)
        self.image_label.setScaledContents(False)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        # This scroll bar will be used to scroll through the images
        self.image_scroll_bar = QScrollBar(Qt.Horizontal)
        self.image_scroll_bar.setRange(0, 0)
        self.image_scroll_bar.setSingleStep(1)
        self.image_scroll_bar.setPageStep(1)
        self.image_scroll_bar.setTracking(True)
        self.image_scroll_bar.valueChanged.connect(self.scroll_bar_changed)
        self.layout.addWidget(self.image_scroll_bar)

        self.setLayout(self.layout)

    def scroll_bar_changed(self) -> None:
        """
        Called when the scroll bar is changed.
        This method will update the displayed image.

        Returns:
            None
        """
        self.pixmap = QPixmap.fromImage(self.image[self.image_scroll_bar.value()])
        self.image_label.setPixmap(self.pixmap.scaled(self.image_label.size(),
                                                      Qt.KeepAspectRatio,
                                                      Qt.SmoothTransformation))

    def set_image(self, image: [QImage]) -> None:
        """
        Set the image to be displayed.

        Args:
            image: A list of QImages.

        Returns:
            None
        """
        self.image = image
        self.pixmap = QPixmap.fromImage(self.image[0])
        self.image_label.setPixmap(self.pixmap.scaled(self.image_label.size(),
                                                      Qt.KeepAspectRatio,
                                                      Qt.SmoothTransformation))
        self.image_scroll_bar.setRange(0, len(self.image) - 1)
        self.image_scroll_bar.setValue(0)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        """
        Called when the widget is resized.
        This method will update the displayed image.

        Args:
            a0: The resize event.

        Returns:
            None
        """
        if self.pixmap and not self.pixmap.isNull() and self.image_label:
            self.image_label.setPixmap(self.pixmap.scaled(self.image_label.size(),
                                                          Qt.KeepAspectRatio,
                                                          Qt.SmoothTransformation))
        super().resizeEvent(a0)
