import numpy
import os
from PyQt5.QtCore import QThread, QObject, pyqtSignal

import SLIX
if SLIX.toolbox.gpu_available:
    import cupy

__all__ = ['ParameterGeneratorWorker']


class ParameterGeneratorWorker(QObject):
    """
    Worker class for the parameter generator.
    This class gets called from the ParameterGeneratorWidget when the user clicks the "Generate" button.
    """
    # Signal to inform the ParameterGeneratorWidget that the worker has finished
    finishedWork = pyqtSignal()
    # Signal to inform the ParameterGeneratorWidget what step the worker is currently working on
    currentStep = pyqtSignal(str)
    # Error message
    errorMessage = pyqtSignal(str)

    def __init__(self, filename: str, image: numpy.array,
                 output_folder: str, filtering: str,
                 filtering_parm_1: float, filtering_parm_2: float,
                 use_gpu: bool, detailed: bool, min: bool, max: bool,
                 avg: bool, direction: bool, nc_direction: bool,
                 peaks: bool, peak_width: bool, peak_distance: bool,
                 peak_prominence: bool, dir_correction: float):
        """
        Initialize the worker.

        Args:
            filename: Filename of the measurement image

            image: NumPy array of the measurement image

            output_folder: Folder to save the generated images

            filtering: Filtering method to use

            filtering_parm_1: Parameter 1 of the filtering method

            filtering_parm_2: Parameter 2 of the filtering method

            use_gpu: Use GPU for calculations

            detailed: Use detailed mode

            min: Generate minima image

            max: Generate maxima image

            avg: Generate average image

            direction: Generate direction image

            nc_direction: Generate non crossing direction image

            peaks: Generate peaks image

            peak_width: Generate peak width image

            peak_distance: Generate peak distance image

            peak_prominence: Generate peak prominence image

            dir_correction: Direction correction in degree
        """
        super().__init__()
        self.filename = filename
        self.image = image
        self.output_folder = output_folder
        self.gpu = use_gpu
        self.detailed = detailed
        self.min = min
        self.max = max
        self.avg = avg
        self.direction = direction
        self.nc_direction = nc_direction
        self.peaks = peaks
        self.peak_width = peak_width
        self.peak_distance = peak_distance
        self.peak_prominence = peak_prominence
        self.filtering = filtering
        self.filtering_parameter_1 = filtering_parm_1
        self.filtering_parameter_2 = filtering_parm_2
        self.dir_correction = dir_correction

        self.output_path_name = ""
        self.output_data_type = ".tiff"

    def get_output_path_name(self) -> str:
        # Get the filename without the extension to determine the output file names
        if os.path.isdir(self.filename):
            filename_without_extension = SLIX._cmd.ParameterGenerator.get_file_pattern(self.filename)
        else:
            filename_without_extension = \
                os.path.splitext(os.path.basename(self.filename))[0]
        output_path_name = f'{self.output_folder}/{filename_without_extension}'
        # Create the output folder if it does not exist

        return output_path_name

    def apply_filtering(self) -> None:
        # If the thread is stopped, return
        if QThread.currentThread().isInterruptionRequested():
            self.finishedWork.emit()
            return

        # Apply filtering
        if self.filtering != "None":
            self.currentStep.emit(f"Filtering: {self.filtering} "
                                  f"{self.filtering_parameter_1} "
                                  f"{self.filtering_parameter_2}")
            if self.filtering == "Fourier":
                self.image = SLIX.preparation.low_pass_fourier_smoothing(self.image,
                                                                         self.filtering_parameter_1,
                                                                         self.filtering_parameter_2)
            elif self.filtering == "Savitzky-Golay":
                self.image = SLIX.preparation.savitzky_golay_smoothing(self.image,
                                                                       self.filtering_parameter_1,
                                                                       self.filtering_parameter_2)

    def generate_minima(self) -> None:
        if QThread.currentThread().isInterruptionRequested():
            self.finishedWork.emit()
            return
        # Generate minima image
        if self.min:
            self.currentStep.emit("Generating minima...")
            min_img = numpy.min(self.image, axis=-1)
            SLIX.io.imwrite(f'{self.output_path_name}_min'
                            f'{self.output_data_type}', min_img)

    def generate_maxima(self) -> None:
        if QThread.currentThread().isInterruptionRequested():
            self.finishedWork.emit()
            return
        # Generate maxima image
        if self.max:
            self.currentStep.emit("Generating maxima...")
            max_img = numpy.max(self.image, axis=-1)
            SLIX.io.imwrite(f'{self.output_path_name}_max'
                            f'{self.output_data_type}', max_img)

    def generate_average(self) -> None:
        if QThread.currentThread().isInterruptionRequested():
            self.finishedWork.emit()
            return
        # Generate average image
        if self.avg:
            self.currentStep.emit("Generating average...")
            avg_img = numpy.mean(self.image, axis=-1)
            SLIX.io.imwrite(f'{self.output_path_name}_avg'
                            f'{self.output_data_type}', avg_img)

    def generate_peaks(self, peaks: numpy.ndarray, detailed: bool, gpu: bool) -> None:
        if QThread.currentThread().isInterruptionRequested():
            self.finishedWork.emit()
            return
        # Generate all peaks to write low and high prominence peaks
        if self.peaks:
            self.currentStep.emit("Generating all peaks...")
            all_peaks = SLIX.toolbox.peaks(self.image, use_gpu=gpu, return_numpy=True)
            if not detailed:
                SLIX.io.imwrite(f'{self.output_path_name}_high_prominence_peaks'
                                f'{self.output_data_type}',
                                numpy.sum(peaks, axis=-1,
                                          dtype=numpy.uint16))
                SLIX.io.imwrite(f'{self.output_path_name}_low_prominence_peaks'
                                f'{self.output_data_type}',
                                numpy.sum(all_peaks, axis=-1, dtype=numpy.uint16) -
                                numpy.sum(peaks, axis=-1,
                                          dtype=numpy.uint16))
            else:
                SLIX.io.imwrite(f'{self.output_path_name}_all_peaks_detailed'
                                f'{self.output_data_type}', all_peaks)
                SLIX.io.imwrite(
                    f'{self.output_path_name}_high_prominence_peaks_detailed'
                    f'{self.output_data_type}',
                    peaks
                )

    def generate_direction(self, peaks: numpy.ndarray, centroids: numpy.ndarray, gpu: bool) -> None:
        if QThread.currentThread().isInterruptionRequested():
            self.finishedWork.emit()
            return
        # Generate the direction images
        if self.direction:
            self.currentStep.emit("Generating direction...")
            direction = SLIX.toolbox.direction(peaks, centroids, use_gpu=gpu, number_of_directions=3,
                                               correction_angle=self.dir_correction, return_numpy=True)
            for dim in range(direction.shape[-1]):
                SLIX.io.imwrite(f'{self.output_path_name}_dir_{dim + 1}'
                                f'{self.output_data_type}',
                                direction[:, :, dim])
            del direction

    def generate_non_crossing_direction(self, peaks: numpy.ndarray, centroids: numpy.ndarray, gpu: bool) -> None:
        if QThread.currentThread().isInterruptionRequested():
            self.finishedWork.emit()
            return
        # Generate the non-crossing direction images
        if self.nc_direction:
            self.currentStep.emit("Generating non crossing direction...")
            nc_direction = SLIX.toolbox.direction(peaks, centroids, use_gpu=gpu,
                                                  number_of_directions=1, return_numpy=True)
            SLIX.io.imwrite(f'{self.output_path_name}_dir'
                            f'{self.output_data_type}',
                            nc_direction[:, :])
            del nc_direction

    def generate_peak_distance(self, peaks: numpy.ndarray, centroids: numpy.ndarray, detailed: bool, gpu: bool) -> None:
        detailed_str = "_detailed" if detailed else ""
        if QThread.currentThread().isInterruptionRequested():
            self.finishedWork.emit()
            return

        # Generate the peak distance
        if self.peak_distance:
            self.currentStep.emit("Generating peak distance...")
            if detailed:
                peak_distance = SLIX.toolbox.peak_distance(peaks, centroids, use_gpu=gpu, return_numpy=True)
            else:
                peak_distance = SLIX.toolbox.mean_peak_distance(peaks, centroids, use_gpu=gpu, return_numpy=True)
            SLIX.io.imwrite(f'{self.output_path_name}_peakdistance{detailed_str}'
                            f'{self.output_data_type}', peak_distance)
            del peak_distance

    def generate_peak_width(self, peaks: numpy.ndarray, detailed: bool, gpu: bool) -> None:
        detailed_str = "_detailed" if detailed else ""
        if QThread.currentThread().isInterruptionRequested():
            self.finishedWork.emit()
            return
        # Generate the peak width
        if self.peak_width:
            self.currentStep.emit("Generating peak width...")
            if detailed:
                peak_width = SLIX.toolbox.peak_width(self.image, peaks, use_gpu=gpu, return_numpy=True)
            else:
                peak_width = SLIX.toolbox.mean_peak_width(self.image, peaks, use_gpu=gpu)
            SLIX.io.imwrite(f'{self.output_path_name}_peakwidth{detailed_str}'
                            f'{self.output_data_type}', peak_width)
            del peak_width

    def generate_peak_prominence(self, peaks: numpy.ndarray, detailed: bool, gpu: bool) -> None:
        detailed_str = "_detailed" if detailed else ""
        if QThread.currentThread().isInterruptionRequested():
            self.finishedWork.emit()
            return
        # Generate the peak prominence
        if self.peak_prominence:
            self.currentStep.emit("Generating peak prominence...")
            if detailed:
                prominence = SLIX.toolbox.peak_prominence(self.image, peaks, use_gpu=gpu, return_numpy=True)
            else:
                prominence = SLIX.toolbox.mean_peak_prominence(self.image, peaks, use_gpu=gpu, return_numpy=True)
            SLIX.io.imwrite(f'{self.output_path_name}_peakprominence{detailed_str}'
                            f'{self.output_data_type}', prominence)
            del prominence

    def process(self) -> None:
        """
        Process the image. This method is called from the ParameterGeneratorWidget.

        Returns:
             None
        """
        self.output_path_name = self.get_output_path_name()
        if os.path.isdir(self.filename):
            SLIX.io.imwrite(f'{self.output_path_name}_Stack{self.output_data_type}', self.image)

        gpu = self.gpu
        detailed = self.detailed

        try:
            self.apply_filtering()
            self.generate_minima()
            self.generate_maxima()
            self.generate_average()

            if QThread.currentThread().isInterruptionRequested():
                self.finishedWork.emit()
                return
            # The following steps require the significant peaks of the measurement ...
            self.currentStep.emit("Generating significant peaks...")
            peaks = SLIX.toolbox.significant_peaks(self.image, use_gpu=gpu, return_numpy=True)

            if QThread.currentThread().isInterruptionRequested():
                self.finishedWork.emit()
                return
            # ... as well as the centroids
            self.currentStep.emit("Generating centroids...")
            centroids = SLIX.toolbox.centroid_correction(self.image, peaks, use_gpu=gpu, return_numpy=True)

            self.generate_peaks(peaks, detailed, gpu)
            self.generate_direction(peaks, centroids, gpu)
            self.generate_non_crossing_direction(peaks, centroids, gpu)
            self.generate_peak_distance(peaks, centroids, detailed, gpu)
            self.generate_peak_width(peaks, detailed, gpu)
            self.generate_peak_prominence(peaks, detailed, gpu)
        except cupy.cuda.memory.OutOfMemoryError as e:
            self.errorMessage.emit("cupy.cuda.memory.OutOfMemoryError: Ran out of memory during computation. "
                                   "Please disable the GPU option.")
        if self.gpu:
            mempool = cupy.get_default_memory_pool()
            mempool.free_all_blocks()
        # Tell connected components that we are done
        self.finishedWork.emit()
