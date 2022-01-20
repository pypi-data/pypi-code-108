import json
from collections import defaultdict
from datetime import datetime
from functools import partial
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Literal
from typing import Optional
from typing import Union

import numpy as np

from dkist_processing_common.models.json_encoder import QualityValueEncoder
from dkist_processing_common.models.quality import Plot2D
from dkist_processing_common.models.quality import ReportMetric
from dkist_processing_common.models.quality import SimpleTable
from dkist_processing_common.models.tags import Tag


class QualityMixin:
    @property
    def quality_task_types(self) -> List[str]:
        """
        Task types to use in generating metrics that work on several task types
        """
        return ["dark", "gain", "lamp_gain", "solar_gain"]

    @staticmethod
    def _create_statement_metric(
        name: str, description: str, statement: str, warnings: Optional[str] = None
    ) -> dict:
        metric = ReportMetric(
            name=name, description=description, statement=statement, warnings=warnings
        )
        return metric.dict()

    @staticmethod
    def _format_warnings(warnings: Union[List[str], None]):
        """
        If warnings is an empty list, change its value to None
        """
        return warnings or None

    def _record_values(self, values, tags: Union[Iterable[str], str]):
        """
        Serialize and store distributed quality report values for
        """
        file_obj = json.dumps(values, allow_nan=False, cls=QualityValueEncoder).encode()
        self.write(file_obj=file_obj, tags=tags)

    def quality_store_ao_status(self, values: List[bool]):
        """
        Collect and store ao status data
        Parameters
        ----------
        values: boolean value denoting whether AO was running and locked or not
        """
        self._record_values(values=values, tags=Tag.quality("AO_STATUS"))

    def quality_build_ao_status(self) -> dict:
        """
        Build ao status schema from stored data
        """
        ao_status = []
        # Loop over files that contain data for this metric
        for path in self.read(tags=Tag.quality("AO_STATUS")):
            with path.open() as f:
                ao_status += json.load(f)
        percentage = round(100 * np.count_nonzero(ao_status) / len(ao_status), 1)
        return self._create_statement_metric(
            name="Adaptive Optics Status",
            description="This metric shows the percentage of frames in which the adaptive optics "
            "system was running and locked",
            statement=f"The adaptive optics system was running and locked for {percentage}% of the "
            f"observed frames",
            warnings=None,
        )

    def quality_store_range(self, name: str, warnings: List[str]):
        """
        Insert range checking warnings into the schema used to record quality info
        Parameters
        ----------
        name: name of the parameter / measurement for which range was out of bounds
        warnings: list of warnings to be entered into the quality report
        """
        data = {"name": name, "warnings": warnings}
        self._record_values(values=data, tags=Tag.quality("RANGE"))

    def quality_build_range(self) -> dict:
        """
        Build range data schema from stored data
        """
        warnings = []
        # Loop over files that contain data for this metric
        for path in self.read(tags=Tag.quality("RANGE")):
            with path.open() as f:
                data = json.load(f)
                for warning in data["warnings"]:
                    warnings.append(warning)

        return ReportMetric(
            name="Range checks",
            description="This metric is checking that certain input and calculated parameters "
            "fall within a valid data range. If no parameters are listed here, all "
            "pipeline parameters were measured to be in range",
            warnings=self._format_warnings(warnings),
        ).dict()

    @staticmethod
    def quality_build_warnings_count(total_warnings: int) -> dict:
        return ReportMetric(
            name="Warnings count",
            description="How many warnings were raised during the calibration " "process.",
            statement=f"{total_warnings} warnings were raised during the calibration of "
            f"this dataset",
        ).dict()

    @property
    def quality_metrics_no_task_dependence(self) -> Dict:
        return {
            "FRIED_PARAMETER": self.quality_build_fried_parameter,
            "LIGHT_LEVEL": self.quality_build_light_level,
            "NOISE": self.quality_build_noise,
            "POLARIMETRIC_NOISE": self.quality_build_polarimetric_noise,
            "POLARIMETRIC_SENSITIVITY": self.quality_build_polarimetric_sensitivity,
            "HEALTH_STATUS": self.quality_build_health_status,
            "TASK_TYPES": self.quality_build_task_type_counts,
            "DATASET_AVERAGE": self.quality_build_dataset_average,
            "DATASET_RMS": self.quality_build_dataset_rms,
            "HISTORICAL": self.quality_build_historical,
            "AO_STATUS": self.quality_build_ao_status,
            "RANGE": self.quality_build_range,
        }

    @property
    def quality_metrics_task_dependence(self) -> Dict:
        return {
            "FRAME_AVERAGE": self.quality_build_frame_average,
            "FRAME_RMS": self.quality_build_frame_rms,
        }

    def quality_build_report(self) -> List[dict]:
        """
        Build the quality report by checking for the existence of data for each metric
        """
        report = []
        for metric_name, metric_func in self.quality_metrics_no_task_dependence.items():
            if self._quality_metric_exists(metric_name=metric_name):
                if "POLARIMETRIC_NOISE" in metric_name:
                    for stokes in ["Q", "U", "V"]:
                        report.append(metric_func(stokes=stokes))
                else:
                    report.append(metric_func())
        for metric_name, metric_func in self.quality_metrics_task_dependence.items():
            for task_type in self.quality_task_types:
                if self._quality_metric_exists(metric_name=metric_name, task_type=task_type):
                    report.append(metric_func(task_type=task_type))

        total_warnings = 0
        for d in report:
            if d["warnings"] is not None:
                total_warnings += len(d["warnings"])
        report.append(self.quality_build_warnings_count(total_warnings=total_warnings))

        return report

    def _quality_metric_exists(self, metric_name: str, task_type: str = None) -> bool:
        """
        Look for the existence of data on disk for a quality metric
        """
        tags = [Tag.quality(quality_metric=metric_name)]
        if task_type:
            tags.append(Tag.quality_task(quality_task_type=task_type))
        try:
            next(self.read(tags=tags))
            return True
        except StopIteration:
            return False

    # 2D Plot

    @staticmethod
    def _create_2d_plot_with_datetime_metric(
        name: str,
        description: str,
        xlabel: str,
        ylabel: str,
        xdata: List[str],
        ydata: List[float],
        statement: Optional[str] = None,
        warnings: Optional[List[str]] = None,
    ) -> dict:
        # Convert datetime strings to datetime objects
        xdata = [datetime.fromisoformat(i) for i in xdata]
        # Sort the lists to make sure they are in ascending time order
        xdata, ydata = (list(t) for t in zip(*sorted(zip(xdata, ydata))))
        plot_data = Plot2D(data=[xdata, ydata], xlabel=xlabel, ylabel=ylabel)
        metric = ReportMetric(
            name=name,
            description=description,
            statement=statement,
            plot_data=plot_data,
            warnings=warnings,
        )
        return metric.dict()

    def _record_2d_plot_values(
        self,
        x_values: Union[List[str]],
        y_values: List[float],
        tags: Union[Iterable[str], str],
        task_type: Optional[str] = None,
    ):
        """
        Encode values for a 2d plot type metric and store as a file
        Parameters
        ----------
        x_values: values to apply to the x axis of a 2d plot
        y_values: values to apply to the y axis of a 2d plot
        tags: list of tags relating to the specific quality parameter being stored
        task_type: type of data to be used - dark, gain, etc
        """
        if isinstance(tags, str):
            tags = [tags]
        axis_are_different_lengths = len(x_values) != len(y_values)
        axis_are_zero_length = not x_values or not y_values
        if axis_are_different_lengths or axis_are_zero_length:
            raise ValueError(
                f"Cannot store 2D plot values with 0 length or different length axis. "
                f"{len(x_values)=}, {len(y_values)=}"
            )
        data = {"x_values": x_values, "y_values": y_values}
        if task_type:
            tags.append(Tag.quality_task(quality_task_type=task_type))
        self._record_values(values=data, tags=tags)

    def _load_2d_plot_values(self, tags: Union[str, List[str]], task_type: Optional[str] = None):
        """
        Load all quality files for a given tag and return the merged datetimes and values
        """
        if isinstance(tags, str):
            tags = [tags]
        if task_type:
            tags.append(Tag.quality_task(quality_task_type=task_type))
        datetimes = []
        values = []
        for path in self.read(tags=tags):
            with path.open() as f:
                data = json.load(f)
                datetimes += data["x_values"]
                values += data["y_values"]
        return datetimes, values

    @staticmethod
    def _find_iqr_outliers(datetimes: List[str], values: List[float]) -> List[str]:
        """
        Given a list of values, find values that fall more than (1.5 * iqr) outside the quartiles
        of the data
        Parameters
        ----------
        datetimes: list of datetime strings used to reference the files that are outliers
        values: values to use to determine outliers from the iqr
        """
        if len(values) == 0:
            raise ValueError("No values provided.")
        warnings = []
        q1 = np.quantile(values, 0.25)
        q3 = np.quantile(values, 0.75)
        iqr = q3 - q1
        for i, val in enumerate(values):
            if val < q1 - (iqr * 1.5) or val > q3 + (iqr * 1.5):
                warnings.append(
                    f"File with datetime {datetimes[i]} has a value considered to be an outlier "
                    f"for this metric"
                )
        return warnings

    def quality_store_fried_parameter(self, datetimes: List[str], values: List[float]):
        """
        Collect and store datetime / value pairs for the fried parameter
        """
        self._record_2d_plot_values(
            x_values=datetimes, y_values=values, tags=Tag.quality("FRIED_PARAMETER")
        )

    def quality_build_fried_parameter(self) -> dict:
        """
        Build fried parameter schema from stored data
        """
        # Merge all recorded quality values
        datetimes, values = self._load_2d_plot_values(tags=Tag.quality("FRIED_PARAMETER"))
        return self._create_2d_plot_with_datetime_metric(
            name="Fried Parameter",
            description="This metric quantifies the stability of the atmosphere during an "
            "observation and directly impacts the data quality through a phenomenon "
            "known as atmospheric seeing.",
            xlabel="Time",
            ylabel="Fried Parameter (m)",
            xdata=datetimes,
            ydata=values,
            statement=f"Average Fried Parameter for L1 dataset: "
            f"{round(np.mean(values), 2)} ± {round(np.std(values), 2)} m",
            warnings=None,
        )

    def quality_store_light_level(self, datetimes: List[str], values: List[float]):
        """
        Collect and store datetime / value pairs for the light level
        """
        self._record_2d_plot_values(
            x_values=datetimes, y_values=values, tags=Tag.quality("LIGHT_LEVEL")
        )

    def quality_build_light_level(self) -> dict:
        """
        Build light_level schema from stored data
        """
        datetimes, values = self._load_2d_plot_values(tags=Tag.quality("LIGHT_LEVEL"))
        return self._create_2d_plot_with_datetime_metric(
            name="Light Level",
            description="This metric describes the value of the telescope light level at the start "
            "of data acquisition of each frame.",
            xlabel="Time",
            ylabel="Light Level (adu)",
            xdata=datetimes,
            ydata=values,
            statement=f"Average Light Level for L1 dataset: "
            f"{round(np.mean(values), 2)} ± {round(np.std(values), 2)} adu",
            warnings=None,
        )

    def quality_store_frame_average(
        self, datetimes: List[str], values: List[float], task_type: str
    ):
        """
        Collect and store datetime / value pairs for the individual frame averages
        """
        self._record_2d_plot_values(
            x_values=datetimes,
            y_values=values,
            tags=Tag.quality("FRAME_AVERAGE"),
            task_type=task_type,
        )

    def quality_build_frame_average(self, task_type: str) -> dict:
        """
        Build frame average schema from stored data
        """
        datetimes, values = self._load_2d_plot_values(
            tags=Tag.quality("FRAME_AVERAGE"), task_type=task_type
        )
        warnings = self._find_iqr_outliers(datetimes=datetimes, values=values)
        return self._create_2d_plot_with_datetime_metric(
            name=f"Average Across Frame - {task_type.upper()}",
            description=f"Average intensity value across frames of task type {task_type}",
            xlabel="Time",
            ylabel="Average Value (adu)",
            xdata=datetimes,
            ydata=values,
            warnings=self._format_warnings(warnings),
        )

    def quality_store_frame_rms(self, datetimes: List[str], values: List[float], task_type: str):
        """
        Collect and store datetime / value pairs for the individual frame rms
        """
        self._record_2d_plot_values(
            x_values=datetimes, y_values=values, tags=Tag.quality("FRAME_RMS"), task_type=task_type
        )

    def quality_build_frame_rms(self, task_type: str) -> dict:
        """
        Build frame rms schema from stored data
        """
        datetimes, values = self._load_2d_plot_values(
            tags=Tag.quality("FRAME_RMS"), task_type=task_type
        )
        warnings = self._find_iqr_outliers(datetimes=datetimes, values=values)
        return self._create_2d_plot_with_datetime_metric(
            name=f"Root Mean Square (RMS) Across Frame - {task_type.upper()}",
            description=f"RMS value across frames of task type {task_type}",
            xlabel="Time",
            ylabel="RMS (adu)",
            xdata=datetimes,
            ydata=values,
            warnings=self._format_warnings(warnings),
        )

    def quality_store_noise(self, datetimes: List[str], values: List[float]):
        """
        Collect and store datetime / value pairs for the noise data
        """
        self._record_2d_plot_values(x_values=datetimes, y_values=values, tags=Tag.quality("NOISE"))

    def quality_build_noise(self) -> dict:
        """
        Build noise schema from stored data
        """
        datetimes, values = self._load_2d_plot_values(tags=Tag.quality("NOISE"))
        return self._create_2d_plot_with_datetime_metric(
            name="Noise",
            description="Noise present throughout the dataset.",
            xlabel="Time",
            ylabel="Noise (adu)",
            xdata=datetimes,
            ydata=values,
            statement=f"Average RMS noise value for L1 dataset: "
            f"{round(np.sqrt(np.mean(np.square(values))), 2)} ± {round(np.std(values), 2)} adu",
            warnings=None,
        )

    def quality_store_polarimetric_noise(
        self, stokes: Literal["Q", "U", "V"], datetimes: List[str], values: List[float]
    ):
        """
        Collect and store datetime / value pairs for the polarimetric noise data
        """
        self._record_2d_plot_values(
            x_values=datetimes,
            y_values=values,
            tags=[Tag.quality("POLARIMETRIC_NOISE"), Tag.stokes(stokes)],
        )

    def quality_build_polarimetric_noise(self, stokes: Literal["Q", "U", "V"]) -> dict:
        """
        Build polarimetric noise schema from stored data
        """
        datetimes, values = self._load_2d_plot_values(
            tags=[Tag.quality("POLARIMETRIC_NOISE"), Tag.stokes(stokes)]
        )
        return self._create_2d_plot_with_datetime_metric(
            name=f"Polarization Noise - Stokes {stokes}",
            description=f"This metric shows the evolution of polarimetric noise over the dataset in stokes {stokes}",
            xlabel="Time",
            ylabel="Polarization Noise (adu)",
            xdata=datetimes,
            ydata=values,
            statement=f"RMS polarization noise: {round(np.mean(values), 2)} ± "
            f"{round(np.std(values), 2)} adu",
            warnings=None,
        )

    def quality_store_polarimetric_sensitivity(self, datetimes: List[str], values: List[float]):
        """
        Collect and store datetime / value pairs for the polarimetric sensitivity data
        """
        self._record_2d_plot_values(
            x_values=datetimes,
            y_values=values,
            tags=Tag.quality("POLARIMETRIC_SENSITIVITY"),
        )

    def quality_build_polarimetric_sensitivity(self) -> dict:
        """
        Build polarimetric sensitivity schema from stored data
        """
        datetimes, values = self._load_2d_plot_values(tags=Tag.quality("POLARIMETRIC_SENSITIVITY"))
        return self._create_2d_plot_with_datetime_metric(
            name=f"Polarization Sensitivity",
            description=f"This metric shows the evolution of polarimetric sensitivity over the dataset",
            xlabel="Time",
            ylabel="Polarization Sensitivity (adu)",
            xdata=datetimes,
            ydata=values,
            statement=f"Estimate of polarimetric sensitivity: {round(np.mean(values), 2)}",
            warnings=None,
        )

    # Table

    @staticmethod
    def _create_table_metric(
        name: str,
        description: str,
        rows: List[List[Any]],
        statement: Optional[str] = None,
        warnings: Optional[str] = None,
    ) -> dict:
        metric = ReportMetric(
            name=name,
            description=description,
            statement=statement,
            table_data=SimpleTable(rows=rows),
            warnings=warnings,
        )
        return metric.dict()

    def quality_store_health_status(self, values: List[str]):
        """
        Collect and store health status data
        Parameters
        ----------
        values: statuses as listed in the headers
        """
        self._record_values(values=values, tags=Tag.quality("HEALTH_STATUS"))

    def quality_build_health_status(self) -> dict:
        """
        Build health status schema from stored data
        """
        values = []
        for path in self.read(tags=Tag.quality("HEALTH_STATUS")):
            with path.open() as f:
                data = json.load(f)
                values += data
        statuses, counts = np.unique(values, return_counts=True)
        statuses = [s.lower() for s in statuses]
        # JSON serialization does not work with numpy types
        counts = [int(c) for c in counts]
        warnings = []
        if "ill" in statuses or "bad" in statuses:
            warnings.append("Data sourced from components with a health status of 'Ill' or 'Bad'")
        table_data = [list(z) for z in zip(statuses, counts)]
        table_data.insert(0, ["Status", "Count"])
        return self._create_table_metric(
            name="Data Source Health",
            description="This metric contains the worst health status of the data source during "
            "data acquisition.",
            rows=table_data,
            warnings=self._format_warnings(warnings),
        )

    def quality_store_task_type_counts(
        self, task_type: str, total_frames: int, frames_not_used: Optional[int] = 0
    ):
        """
        Collect and store task type data
        Parameters
        ----------
        task_type: task type as listed in the headers
        total_frames: total number of frames supplied of the given task type
        frames_not_used: if some frames aren't used, how many
        """
        data = {
            "task_type": task_type.upper(),
            "total_frames": total_frames,
            "frames_not_used": frames_not_used,
        }
        self._record_values(values=data, tags=Tag.quality("TASK_TYPES"))

    def quality_build_task_type_counts(self) -> dict:
        """
        Build task type count schema from stored data
        """
        # Raise warning if more than 5% of frames of a given type are not used
        warning_count_threshold = 0.05
        default_int_dict = partial(defaultdict, int)
        task_type_counts = defaultdict(default_int_dict)
        # Loop over files that contain data for this metric
        for path in self.read(tags=Tag.quality("TASK_TYPES")):
            with path.open() as f:
                data = json.load(f)
                task_type_counts[data["task_type"]]["total_frames"] += data["total_frames"]
                task_type_counts[data["task_type"]]["frames_not_used"] += data["frames_not_used"]

        # Now, build metric from the counts dict
        table_data = [[i[0]] + list(i[1].values()) for i in task_type_counts.items()]
        warnings = []
        for row in table_data:
            if row[1] == 0:
                warnings.append(f"NO {row[0]} frames were used!")
            elif row[2] / row[1] > warning_count_threshold:
                warnings.append(
                    f"{round(100 * row[2] / row[1], 1)}% of frames were not used in the "
                    f"processing of task type {row[0]}"
                )
        # Add header row
        table_data.insert(0, ["Task Type", "Total Frames", "Unused Frames"])
        return self._create_table_metric(
            name="Frame Counts",
            description="This metric is a count of the number of frames used to produce a "
            "calibrated L1 dataset",
            rows=table_data,
            warnings=self._format_warnings(warnings),
        )

    def quality_store_dataset_average(self, task_type: str, frame_averages: List[float]):
        """
        Collect and store dataset average
        Parameters
        ----------
        task_type: task type as listed in the headers
        frame_averages: average value of all pixels in each frame of the given task type
        """
        data = {"task_type": task_type, "frame_averages": frame_averages}
        self._record_values(values=data, tags=Tag.quality("DATASET_AVERAGE"))

    def quality_build_dataset_average(self) -> dict:
        """
        Build dataset average schema from stored data
        """
        dataset_averages = defaultdict(list)
        # Loop over files that contain data for this metric
        for path in self.read(tags=Tag.quality("DATASET_AVERAGE")):
            with path.open() as f:
                data = json.load(f)
                # Add counts for the task type to its already existing counts
                dataset_averages[data["task_type"]] += data["frame_averages"]

        # Now, build metric from the counts dict
        table_data = [[i[0], round(np.mean(i[1]), 2)] for i in dataset_averages.items()]
        # Add header row
        table_data.insert(0, ["Task Type", "Dataset Average (adu)"])
        return self._create_table_metric(
            name="Average Across Dataset",
            description="This metric is the calculated mean intensity value across data from an "
            "instrument program task type used in the creation of an entire L1 "
            "dataset.",
            rows=table_data,
            warnings=None,
        )

    def quality_store_dataset_rms(self, task_type: str, frame_rms: List[float]):
        """
        Collect and store dataset average
        Parameters
        ----------
        task_type: task type as listed in the headers
        frame_rms: rms value of all pixels in each frame of the given task type
        """
        data = {"task_type": task_type, "frame_rms": frame_rms}
        self._record_values(values=data, tags=Tag.quality("DATASET_RMS"))

    def quality_build_dataset_rms(self) -> dict:
        """
        Build dataset rms schema from stored data
        """
        dataset_rms = {}
        # Loop over files that contain data for this metric
        for path in self.read(tags=Tag.quality("DATASET_RMS")):
            with path.open() as f:
                data = json.load(f)
                # If the task type isn't in the dict, add it with counts set to zero
                if not data["task_type"] in dataset_rms.keys():
                    dataset_rms[data["task_type"]] = []
                # Add counts for the task type to its already existing counts
                dataset_rms[data["task_type"]] += data["frame_rms"]

        # Now, build metric from the counts dict
        table_data = [[i[0], round(np.mean(i[1]), 2)] for i in dataset_rms.items()]
        # Add header row
        table_data.insert(0, ["Task Type", "Dataset RMS (adu)"])
        return self._create_table_metric(
            name="Dataset RMS",
            description="This metric is the calculated root mean square intensity value across data"
            " from an instrument program task type used in the creation of an entire "
            "L1 dataset.",
            rows=table_data,
            warnings=None,
        )

    def quality_store_historical(self, name: str, value: Any, warning: Optional[str] = None):
        """
        Insert historical data into the schema used to record quality info
        Parameters
        ----------
        name: name of the parameter / measurement to be recorded
        value: value of the parameter / measurement to be recorded
        warning: warning to be entered into the quality report
        """
        data = {"name": name, "value": value, "warnings": warning}
        self._record_values(values=data, tags=Tag.quality("HISTORICAL"))

    def quality_build_historical(self) -> dict:
        """
        Build historical data schema from stored data
        """
        table_data = []
        warnings = []
        # Loop over files that contain data for this metric
        for path in self.read(tags=Tag.quality("HISTORICAL")):
            with path.open() as f:
                data = json.load(f)
                table_data.append([data["name"], data["value"]])
                if data["warnings"] is not None:
                    warnings.append(data["warnings"])

        # Add header row
        table_data.insert(0, ["Metric", "Value"])
        return self._create_table_metric(
            name="Historical Comparisons",
            description="Over time, the data center will be comparing some of the above quality "
            "metrics and other parameters derived from file headers to see how the "
            "DKIST instruments and observations are changing.",
            rows=table_data,
            warnings=self._format_warnings(warnings),
        )
