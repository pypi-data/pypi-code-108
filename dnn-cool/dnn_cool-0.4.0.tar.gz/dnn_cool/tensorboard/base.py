from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Tuple, Dict, Mapping, List, Callable

from tensorboardX import SummaryWriter

from dnn_cool.external.autograd import Dataset


class ITensorboardPublisher:

    def __call__(self, writer: SummaryWriter, tag: str, sample: Any, idx: int):
        """
        Publishes interpretation data.

        :param writer: A :class:`SummaryWriter` that logs to the tensorboard.

        :param tag: The prefix, this is typically either "best_key" or "worst_key".

        :param sample: The sample that is going to be published to the Tensorboard

        :param idx: The index of the dataset sample.

        """
        raise NotImplementedError()


def img_publisher(writer: SummaryWriter, tag: str, sample: Any, idx: int):
    writer.add_image(f'{tag}_images', sample, global_step=idx)


def text_publisher(writer: SummaryWriter, tag: str, sample: Any, idx: int):
    writer.add_text(f'{tag}_text', sample, global_step=idx)


def default_tensorboard_type_mapping():
    return {
        'img': [img_publisher],
        'text': [text_publisher]
    }


def publish_all(prefix: str,
                idx: int,
                sample: Tuple[Dict, Dict],
                mapping_key: str,
                key: str,
                writer: SummaryWriter,
                mapping: Mapping,
                task_name: str):
    """
    Publishes a given key given all publishers supplied via the mapping
    :param prefix: The prefix, this is typically either "best" or "worst".

    :param idx: The index of the sample in the dataset.

    :param sample: A tuple X, y where X and y and dictionaries.

    :param mapping_key: The key which when applied to the mapping gives a list of publishers.

    :param key: The key in X that is being published.

    :param writer: A :class:`SummaryWriter` that logs to the tensorboard.

    :param mapping: A mapping `[str, List[Callable]]` where the key are either input columns, or input types and the values are a list of publisher functions.

    :param task_name: The name of the task, to be included in the name
    """
    if mapping_key in mapping:
        publishers: List[ITensorboardPublisher] = mapping[mapping_key]
        for publisher in publishers:
            X, y = sample
            tag = f'{prefix}_{task_name}'
            publisher(writer, tag, X[key], idx)


@dataclass()
class TensorboardConverter:
    """
    A dataclass which holds mappings from column names to Tensorboard publishers and from column types to Tensorboard
    publishers. Also, it stores which column is of what type, to be able to log any column name to the Tensorboard.
    """
    col_mapping: Dict[str, List[ITensorboardPublisher]] = field(default_factory=lambda: {})
    """
    Stores a `dict` from column names to a list of publishers. A publisher is just a callable which will be called 
    with this signature: 
    :code:`publisher(writer: SummaryWriter, idx: int, sample: Tuple, prefix: str, task_name: str, key: str)`. Example 
    publisher functions are :meth:`dnn_cool.catalyst_utils.img` and :meth:`dnn_cool.catalyst_utils.text`.
    """
    type_mapping: Dict[str, List[ITensorboardPublisher]] = field(default_factory=lambda: {})
    """
    Stores a `dict` from column types to a list of publishers. A publisher is just a callable which will be called 
    with this signature: 
    :code:`publisher(writer: SummaryWriter, idx: int, sample: Tuple, prefix: str, task_name: str, key: str)`. Example 
    publisher functions are :meth:`dnn_cool.catalyst_utils.img` and :meth:`dnn_cool.catalyst_utils.text`.
    """
    col_to_type_mapping: Dict[str, str] = field(default_factory=lambda: {})
    """
    Stores a `dict` from column names to type names.
    """

    def __call__(self, writer: SummaryWriter, idx: int, sample: Tuple[Dict, Dict], prefix: str, task_name: str):
        """
        Publishes a given sample to the tensorboard, using the mappings defined in the dataclass.

        :param writer: A :class:`SummaryWriter` that logs to the tensorboard.

        :param idx: The index of the sample that is being published

        :param sample: A tuple of dictionaries X, y.

        :param prefix: The prefix, this is typically either "best" or "worst".

        :param task_name: The name of the task

        :return:
        """
        if task_name == 'gt':
            return
        X, y = sample
        for key in X:
            publish_all(prefix, idx, sample, key, key, writer, self.col_mapping, task_name)
        for key in X:
            if key in self.col_to_type_mapping:
                publish_all(prefix,
                            idx,
                            sample,
                            self.col_to_type_mapping[key],
                            key,
                            writer,
                            self.type_mapping,
                            task_name)


@dataclass
class TensorboardConverters:
    """
    This class handles the logging to the Tensorboard of an interpretation for a task
    """
    logdir: Path
    datasets: Dict[str, Dataset]
    tensorboard_loggers: Callable = field(default_factory=TensorboardConverter)
    loggers: Dict[str, SummaryWriter] = field(default_factory=lambda: {})
    top_k: int = 10

    def initialize(self, state):
        """
        Initializes the tensorboard loggers.

        :param state: The state with which the callback is called.
        """
        if (self.logdir is not None) and (state.loader_key not in self.loggers):
            path = str(self.logdir / f"{state.loader_key}_log")
            writer = SummaryWriter(path)
            self.loggers[state.loader_key] = writer

    def publish(self, state, interpretations):
        """
        Publishes all interpretations

        :param state: The state with which the callback is called.

        :param interpretations: A dict object from task name to loss values. Also additional keys are those prefixed \
        with "indices|{task_name}", which hold the corresponding indices in the original dataset for which the loss \
        items are computed.

        """
        for key, value in interpretations.items():
            if key.startswith('indices'):
                continue
            sorted_indices = value.argsort()
            best_indices = interpretations[f'indices|{key}'][sorted_indices][:self.top_k]
            worst_indices = interpretations[f'indices|{key}'][sorted_indices][-self.top_k:]
            writer: SummaryWriter = self.loggers[state.loader_key]
            dataset = self.datasets[state.loader_key]
            self._publish_inputs(best_indices, writer, dataset, prefix='best', key=key)
            self._publish_inputs(worst_indices, writer, dataset, prefix='worst', key=key)

    def _publish_inputs(self, best_indices, writer, dataset, prefix, key):
        for idx in best_indices:
            if self.tensorboard_loggers is not None:
                self.tensorboard_loggers(writer, idx, dataset[idx], prefix, key)

    def close(self, state):
        """Close opened tensorboard writers"""
        if state.logdir is None:
            return

        for logger in self.loggers.values():
            logger.close()
