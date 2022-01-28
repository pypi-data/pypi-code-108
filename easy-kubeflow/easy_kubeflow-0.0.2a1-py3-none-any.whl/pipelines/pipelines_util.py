import inspect
from typing import Callable, Optional
from uuid import uuid4

import kfp
from kfp import compiler
import kfp.dsl as dsl
import kfp.notebook
from kfp_server_api.exceptions import ApiException
from kubernetes import client as k8s_client

from easy_kubeflow.utils import MyLogger

Strategies = {
    'big_data': {
        'bigdata': 'yes'
    },
    'deep_learning': {
        'func': 'deep-learning'
    }
}

# select default resource
CPU_REQUEST = '0.5'
CPU_LIMIT = '1'
MEM_REQUEST = '1Gi'
MEM_LMIT = '2Gi'

# set nfs
NFS_MASTER_HOST = '10.55.41.243'
NFS_PATH = '/kubeflow-pv-test/'

_logger = MyLogger()


def _valid_strategy(strategy):
    if strategy in Strategies:
        return True
    else:
        return False


def _get_strategy_key_value(dic):
    for key, value in dic.items():
        return key, value


def _input_arg_path(arg):
    """
    ping to args path
    :param arg:
    :return: ars path
    """
    return dsl.InputArgumentPath(argument=arg)


def _is_PipelineParam(obj):
    if obj:
        if obj.__class__.__name__ == 'PipelineParam':
            return True
        else:
            return False
    else:
        _logger.error("Invalid args")
        return False


def _dict2list(dic: dict = None):
    ls = list()
    if dic:
        for key, value in dic.items():
            ls.append(key)
            ls.append(value)
        return ls
    else:
        return None


def _uniform_data_path(dic: dict = None):
    re_dic = dict()
    if dic:
        for key, value in dic.items():
            re_dic[key] = value
        return re_dic
    else:
        return None


def _is_url(character):
    if character.startswith('http'):
        return True
    else:
        return False


_pipeline_decorator_handler = None


class EasyPipelines(object):
    """easy way to kubeflow pipelines"""

    def __init__(self, description: Optional[str] = None):
        """
        :param description: description for your experiment, default no description.
        """
        self.client = None
        self.experiment_name = 'Default'
        self.description = description
        self.components_list = list()

    @property
    def experiment(self):
        return self.experiment_name

    @experiment.setter
    def experiment(self, name: Optional[str] = None):
        """
        set experiment
        :param name: `Default` is default experiment name
        """
        self.experiment_name = name
        if not self.client:
            self.client = kfp.Client()
        self.experiment_obj = self.client.create_experiment(name=self.experiment_name, description=self.description)
        _logger.info("Connected to kubeflow pipelines client successfully !")

    @property
    def components(self):
        return self.components_list

    @components.setter
    def components(self, comp):
        self.components_list.append(comp)

    def dec_func(self):
        return dsl.pipeline()

    def input_arg_path(self, arg):
        """
        ping to args path
        :param arg:
        :return: ars path
        """
        return dsl.InputArgumentPath(argument=arg)

    def pipeline(self,
                 name: Optional[str] = None,
                 description: Optional[str] = None,
                 output_directory: Optional[str] = None):
        """Decorator of pipeline functions.

        Example
          ::

            @pipeline(
              name='my awesome pipeline',
              description='Is it really awesome?'
              output_directory='gs://my-bucket/my-output-path'
            )
            def my_pipeline(a: PipelineParam, b: PipelineParam):
              ...

        Args:
          name: The pipeline name. Default to a sanitized version of the function
            name.
          description: Optionally, a human-readable description of the pipeline.
          output_directory: The root directory to generate input/output URI under this
            pipeline. This is required if input/output URI placeholder is used in this
            pipeline.
        """

        def _pipeline(func: Callable):
            if name:
                func._component_human_name = name
            if description:
                func._component_description = description
            if output_directory:
                func.output_directory = output_directory

            if _pipeline_decorator_handler:
                return _pipeline_decorator_handler(func) or func
            else:
                return func

        return _pipeline

    def compiler_pipeline(self, pipeline_func, file_name):
        """
        compile pipeline in notebook
        :param pipeline_func: Pipeline functions with @pipeline decorator.
        :param file_name: The output workflow tar.gz file path. for example, "~/a.tar.gz"
        """
        compiler.Compiler().compile(pipeline_func=pipeline_func, package_path=file_name)
        pass

    def run_pipeline(self, run_name: str = None, pipeline_package: str = None):
        """
        run pipeline in notebook
        :param run_name: run name for your experiment, runs will be nested in the same experiment.
        :param pipeline_package: Local path of the pipeline package(
                                 the filename should end with one of the following .tar.gz, .tgz, .zip, .yaml, .yml).
        """
        if not self.client:
            self.client = kfp.Client()
        try:
            self.client.run_pipeline(experiment_id=self.experiment_obj.id, job_name=run_name,
                                     pipeline_package_path=pipeline_package)
        except ApiException as ae:
            _logger.error(ae)

    def _pars_comp(self, comp_list: list = None):
        if comp_list:
            for comp in comp_list:
                print(comp.name)
        pass

    def _dag(self):
        pass

    def load_component(self, component_file: str = None):
        """
        load reuse component from file or url
        :param component_file: url or local dir
        :return: reuse component factory func
        """
        func = None
        if component_file:
            is_url = _is_url(component_file)
            if is_url:
                func = kfp.components.load_component_from_url(url=component_file)
            else:
                func = kfp.components.load_component_from_file(filename=component_file)
            _logger.info(
                "args for your component factory func are : `%s`" % inspect.getfullargspec(func=func).annotations)
            _logger.info("You can use class `ReuseComponent` to build pipelines component !")
        else:
            _logger.error("at least, you need to add a component file !")
        return func


class Component(object):
    """definition for pipelines component"""

    def __init__(self, name: str = None, image: str = None, arguments: Optional[dict] = None,
                 file_outputs: Optional[dict] = None, nfs_path: str = NFS_PATH,
                 nfs_master_host: str = NFS_MASTER_HOST):
        """
        Component object
        :param name: name of component
        :param image: image for component container
        :param arguments: [dict] args to run component container, default None
        :param file_outputs: [dict] out put file of component container, default None
        :param nfs_path: default root path defined by cluster admin
        :param nfs_master_host: default host selected by cluster admin
        """
        self.name = name
        self.uuid = str(uuid4())
        self.image = image
        self.arguments = arguments
        self.file_outputs = file_outputs
        self.nfs_path = nfs_path
        self.nfs_master_host = nfs_master_host
        self.op = dsl.ContainerOp(
            name=self.name,
            image=self.image,
            arguments=_dict2list(self.arguments),
            file_outputs=self.file_outputs
        )

    def default_op(self) -> 'dsl.ContainerOp':
        """
        default pipelines component containerOp
        :return: component containerOp
        """
        _logger.info("Component op of `%s` init ..." % self.name)
        _logger.info("Container mount path is: %s" % self.nfs_path)
        self._pull_image_policy()
        self._add_volume()
        return self.op

    def udf_op(self, request_cpu: Optional[str] = None, request_mem: Optional[str] = None,
               request_gpu: Optional[str] = '1',
               strategies: Optional[list] = None) -> 'dsl.ContainerOp':
        """
        user define pipelines component containerOp
        :param request_cpu: a string can be a number followed by "m", like `300m`, or `0.3` which equals `300m`
        :param request_mem: a string which can be a number or a number followed by one of "E", "P", "T", "G", "M", "K".
                            like `1Gi`, `1Mi`, `1Ki`
        :param request_gpu: str(number) like '1', '4', '8' means the amount of gpu you use
        :param strategies: node select strategy, defined by cluster admin. strategy: `"big_data"` is available.
        :return: component containerOp
        """
        self.default_op()
        self._node_selecter(strategies=strategies)
        self._resource_limit(request_cpu=request_cpu, request_mem=request_mem, request_gpu=request_gpu)
        return self.op

    def _pull_image_policy(self, policy: str = 'Always'):
        """
        default image pull policy: `Always`
        """
        self.op.container.image_pull_policy = policy
        _logger.info("Use image pull policy: %s" % policy)

    def _add_volume(self):
        """add nfs volume, volume and mount volume has the same path"""
        self.op.add_volume(
            k8s_client.V1Volume(name=self.uuid + '-pv',
                                nfs=k8s_client.V1NFSVolumeSource(
                                    path=self.nfs_path,
                                    server=self.nfs_master_host
                                )
                                )
        ) \
            .container \
            .add_volume_mount(
            k8s_client.V1VolumeMount(
                mount_path=self.nfs_path,
                name=self.uuid + '-pv')
        )
        _logger.info("Nfs server master host is: %s" % self.nfs_master_host)
        _logger.info("Nfs server mount path: %s" % self.nfs_path)

    def _node_selecter(self, strategies: Optional[list] = None):
        """
        add pod's node select strategies
        :param strategies: strategy list
        """
        if strategies:
            for strategy in strategies:
                if _valid_strategy(strategy):
                    key, value = _get_strategy_key_value(Strategies.get(strategy))
                    self.op.add_node_selector_constraint(key, value)
                    _logger.info("Add strategy: %s" % strategy)
                else:
                    _logger.error("strategy: %s not found in Strategies" % strategy)
        else:
            _logger.warning("Use default strategy")

    def _resource_limit(self, request_cpu: Optional[str] = None,
                        request_mem: Optional[str] = None,
                        request_gpu: Optional[str] = '1'):
        """
        resource: cpu, memory
        when user set resource, we recommend `request` equals to `limit`
        :param request_cpu: a string can be a number followed by "m", like `300m`, or `0.3` which equals `300m`
        :param request_mem: a string which can be an integer number or an integer number followed by one of "E",
                            "P", "T", "G", "M", "K". like `1Gi`, `1Mi`, `1Ki`
        :param request_gpu: str(number) like '1', '4', '8' means the amount of gpu you use
        """
        # config for cpu
        if request_cpu:
            self.op.container.set_cpu_request(
                request_cpu) \
                .set_cpu_limit(
                request_cpu)
            _logger.info("Set cpu request: %s" % request_cpu)
            _logger.info("Set cpu limit: %s" % request_cpu)
        else:
            self.op.container.set_cpu_request(
                CPU_REQUEST) \
                .set_cpu_limit(
                CPU_LIMIT)
            _logger.warning("Use default cpu request: %s" % CPU_REQUEST)
            _logger.warning("Use default cpu limit: %s" % CPU_LIMIT)
        # config for memory
        if request_mem:
            self.op.container.set_memory_request(
                request_mem) \
                .set_memory_limit(
                request_mem)
            _logger.info("Set mem request: %s" % request_mem)
            _logger.info("Set mem limit: %s" % request_mem)
        else:
            self.op.container.set_memory_request(
                MEM_REQUEST) \
                .set_memory_limit(
                MEM_LMIT)
            _logger.warning("Use default mem request: %s" % MEM_REQUEST)
            _logger.warning("Use default mem limit: %s" % MEM_LMIT)
        # config for gpu
        if request_gpu:
            self.op.container.set_gpu_limit(
                gpu=request_gpu)
            _logger.info("Set gpu request amount: %s" % request_gpu)
            _logger.info("Set gpu limit amount: %s" % request_gpu)
        else:
            self.op.container.set_gpu_limit(
                gpu=request_gpu)
            _logger.warning("Use default gpu request: %s" % request_gpu)
            _logger.warning("Use default gpu limit: %s" % request_gpu)


class ReuseComponent(object):
    """definition for reuse pipelines component"""

    def __init__(self, component_factory_func: Callable = None, arguments: Optional[dict] = None,
                 nfs_path: str = NFS_PATH,
                 nfs_master_host: str = NFS_MASTER_HOST):
        """
        Reuse component object
        :param component_factory_func: factory func to build reuse component op
        :param arguments: [dict] args to run reuse component container, default None
        :param nfs_path: default root path defined by cluster admin
        :param nfs_master_host: default host selected by cluster admin
        """
        self.uuid = str(uuid4())
        self.arguments = arguments
        self.factory_func = component_factory_func
        self.nfs_path = nfs_path
        self.nfs_master_host = nfs_master_host
        self.op = self.factory_func(**_uniform_data_path(self.arguments))

    @staticmethod
    def _uniform_name(name: str = None):
        if name:
            name = name.lower()
            return '-'.join(name.split())
        else:
            return name

    def default_op(self) -> 'dsl.ContainerOp':
        """
        default pipelines component containerOp
        :return: component containerOp
        """
        _logger.info("ReuseComponent op of `%s` init ..." % self._uniform_name(self.factory_func.__name__))
        _logger.info("Container mount path is: %s" % self.nfs_path)
        self._pull_image_policy()
        self._add_volume()
        return self.op

    def udf_op(self, request_cpu: Optional[str] = None, request_mem: Optional[str] = None,
               request_gpu: Optional[str] = '1',
               strategies: Optional[list] = None) -> 'dsl.ContainerOp':
        """
        user define pipelines component containerOp
        :param request_cpu: a string can be a number followed by "m", like `300m`, or `0.3` which equals `300m`
        :param request_mem: a string which can be a number or a number followed by one of "E", "P", "T", "G", "M", "K".
                            like `1Gi`, `1Mi`, `1Ki`
        :param request_gpu: str(number) like '1', '4', '8' means the amount of gpu you use
        :param strategies: node select strategy, defined by cluster admin. strategy: `"big_data"` is available.
        :return: component containerOp
        """
        self.default_op()
        self._node_selecter(strategies=strategies)
        self._resource_limit(request_cpu=request_cpu, request_mem=request_mem, request_gpu=request_gpu)
        return self.op

    def _pull_image_policy(self, policy: str = 'Always'):
        """
        default image pull policy: `Always`
        """
        self.op.container.image_pull_policy = policy
        _logger.info("Use image pull policy: %s" % policy)

    def _add_volume(self):
        """add nfs volume, volume and mount volume has the same path"""
        self.op.add_volume(
            k8s_client.V1Volume(name=self.uuid + '-pv',
                                nfs=k8s_client.V1NFSVolumeSource(
                                    path=self.nfs_path,
                                    server=self.nfs_master_host
                                )
                                )
        ) \
            .container \
            .add_volume_mount(
            k8s_client.V1VolumeMount(
                mount_path=self.nfs_path,
                name=self.uuid + '-pv')
        )
        _logger.info("Nfs server master host is: %s" % self.nfs_master_host)
        _logger.info("Nfs server mount path: %s" % self.nfs_path)

    def _node_selecter(self, strategies: Optional[list] = None):
        """
        add pod's node select strategies
        :param strategies: strategy list
        """
        if strategies:
            for strategy in strategies:
                if _valid_strategy(strategy):
                    key, value = _get_strategy_key_value(Strategies.get(strategy))
                    self.op.add_node_selector_constraint(key, value)
                    _logger.info("Add strategy: %s" % strategy)
                else:
                    _logger.error("strategy: %s not found in Strategies" % strategy)
        else:
            _logger.warning("Use default strategy")

    def _resource_limit(self, request_cpu: Optional[str] = None,
                        request_mem: Optional[str] = None,
                        request_gpu: Optional[str] = '1'):
        """
        resource: cpu, memory
        when user set resource, we recommend `request` equals to `limit`
        :param request_cpu: a string can be a number followed by "m", like `300m`, or `0.3` which equals `300m`
        :param request_mem: a string which can be an integer number or an integer number followed by one of "E",
                            "P", "T", "G", "M", "K". like `1Gi`, `1Mi`, `1Ki`
        :param request_gpu: str(number) like '1', '4', '8' means the amount of gpu you use
        """
        # config for cpu
        if request_cpu:
            self.op.container.set_cpu_request(
                request_cpu) \
                .set_cpu_limit(
                request_cpu)
            _logger.info("Set cpu request: %s" % request_cpu)
            _logger.info("Set cpu limit: %s" % request_cpu)
        else:
            self.op.container.set_cpu_request(
                CPU_REQUEST) \
                .set_cpu_limit(
                CPU_LIMIT)
            _logger.warning("Use default cpu request: %s" % CPU_REQUEST)
            _logger.warning("Use default cpu limit: %s" % CPU_LIMIT)
        # config for memory
        if request_mem:
            self.op.container.set_memory_request(
                request_mem) \
                .set_memory_limit(
                request_mem)
            _logger.info("Set mem request: %s" % request_mem)
            _logger.info("Set mem limit: %s" % request_mem)
        else:
            self.op.container.set_memory_request(
                MEM_REQUEST) \
                .set_memory_limit(
                MEM_LMIT)
            _logger.warning("Use default mem request: %s" % MEM_REQUEST)
            _logger.warning("Use default mem limit: %s" % MEM_LMIT)
        # config for gpu
        if request_gpu:
            self.op.container.set_gpu_limit(
                gpu=request_gpu)
            _logger.info("Set gpu request amount: %s" % request_gpu)
            _logger.info("Set gpu limit amount: %s" % request_gpu)
        else:
            self.op.container.set_gpu_limit(
                gpu=request_gpu)
            _logger.warning("Use default gpu request: %s" % request_gpu)
            _logger.warning("Use default gpu limit: %s" % request_gpu)


