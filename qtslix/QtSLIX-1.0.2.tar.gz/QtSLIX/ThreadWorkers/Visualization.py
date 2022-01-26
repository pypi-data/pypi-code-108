import numpy
from PyQt5.QtCore import QObject, pyqtSignal
import SLIX

__all__ = ['FOMWorker', 'VectorWorker']


class FOMWorker(QObject):
    """
    Worker class for the visualization.
    This class gets called from the VisualizationWidget when the user clicks the "Generate" button.
    """
    # Signal to inform the ParameterGeneratorWidget that the worker has finished
    finishedWork = pyqtSignal(numpy.ndarray)
    # Signal to inform the ParameterGeneratorWidget what step the worker is currently working on
    currentStep = pyqtSignal(str)
    # Error message
    errorMessage = pyqtSignal(str)

    def __init__(self, saturation_weighting, value_weighting, color_map, directions, inclination):
        super().__init__()
        self.directions = directions
        self.inclinations = inclination
        self.saturation_weighting = saturation_weighting
        self.value_weighting = value_weighting
        self.color_map = color_map

    def process(self) -> None:
        image = None
        try:
            self.currentStep.emit("Generating FOM...")
            image = SLIX.visualization.direction(self.directions, inclination=self.inclinations,
                                                 saturation=self.saturation_weighting,
                                                 value=self.value_weighting, colormap=self.color_map)
        except ValueError as e:
            self.errorMessage.emit(f'Could not generate FOM. Check your input files.\n'
                                   f'Error message:\n{e}')
        self.finishedWork.emit(image)


class VectorWorker(QObject):
    # Signal to inform the ParameterGeneratorWidget that the worker has finished
    finishedWork = pyqtSignal(numpy.ndarray)
    # Signal to inform the ParameterGeneratorWidget what step the worker is currently working on
    currentStep = pyqtSignal(str)
    # Error message
    errorMessage = pyqtSignal(str)

    def __init__(self, fig, ax, input_array, alpha, thinout, scale,
                 vector_width, distribution, threshold, colormap,
                 background_image, value_weighting):
        super().__init__()
        self.fig = fig
        self.ax = ax
        self.input_array = input_array
        self.alpha = alpha
        self.thinout = thinout
        self.scale = scale
        self.vector_width = vector_width
        self.distribution = distribution
        self.threshold = threshold
        self.color_map = colormap
        self.value_background = background_image
        self.value_weighting = value_weighting

    def calculate_distribution(self, UnitX, UnitY) -> None:
        color_map = SLIX._cmd.VisualizeParameter.available_colormaps[self.color_map]
        SLIX.visualization.unit_vector_distribution(UnitX, UnitY,
                                                    ax=self.ax,
                                                    thinout=self.thinout,
                                                    alpha=self.alpha,
                                                    scale=self.scale,
                                                    vector_width=self.vector_width,
                                                    colormap=color_map,
                                                    weighting=self.value_weighting)

    def calculate_unit_vectors(self, UnitX, UnitY) -> None:
        color_map = SLIX._cmd.VisualizeParameter.available_colormaps[self.color_map]
        SLIX.visualization.unit_vectors(UnitX, UnitY,
                                        ax=self.ax,
                                        thinout=self.thinout,
                                        alpha=self.alpha,
                                        scale=self.scale,
                                        vector_width=self.vector_width,
                                        background_threshold=self.threshold,
                                        colormap=color_map,
                                        weighting=self.value_weighting)

    def process(self) -> None:
        vector_image = None

        try:
            # Generate unit vectors from direction images
            self.currentStep.emit("Generating unit vectors...")
            UnitX, UnitY = SLIX.toolbox.unit_vectors(self.input_array, use_gpu=False)
            if self.distribution:
                self.currentStep.emit("Visualizing vector distribution...")
                self.calculate_distribution(UnitX, UnitY)
            else:
                self.currentStep.emit("Visualizing unit vectors...")
                self.calculate_unit_vectors(UnitX, UnitY)
            if self.value_background is not None:
                self.ax.imshow(self.value_background, cmap='gray')

            self.fig.subplots_adjust(0, 0, 1, 1)
            # Convert current plot to NumPy array
            self.currentStep.emit("Drawing image...")
            self.fig.canvas.draw()
            vector_image = numpy.array(self.fig.canvas.buffer_rgba(), dtype=float)
            vector_image = vector_image[:, :, :3]
        except ValueError as e:
            self.errorMessage.emit(f'Could not generate FOM. Check your input files.\n'
                                   f'Error message:\n{e}')

        self.finishedWork.emit(vector_image)

