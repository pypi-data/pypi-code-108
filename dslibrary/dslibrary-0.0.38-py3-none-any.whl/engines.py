"""
Execution on various engines.
"""
from .run_models import ModelRunner


class ModelEngine(object):
    def get_metadata(self, uri: str):
        """
        Obtain metadata for the given model or pipeline step.  This metadata includes input and output schemas, which
        will help us know how we can connect the steps of a pipeline, as well as parameter names.
        """

    # TODO enumerate models?
    # TODO wrapper for container build process?
    # TODO compare to SageMaker, AzureML, GoogleAI

    def run(self, model_run_spec: ModelRunner):
        """
        Execute the given model.
        """


class ModelEngineLocal(ModelEngine):
    """
    Execute models locally.
    """
    def __init__(self, default_folder: str=None):
        """
        :param default_folder:  A folder containing model folders.  A model is referenced by supplying the name
                                of a subfolder as its URI.
        """
        self.default_folder = default_folder

    def get_metadata(self, model_uri: str):
        pass

    def run(self, model_run_spec: ModelRunner):
        # TODO with a path we can invoke as a subprocess, but with a method name we can invoke more quickly
        #  - how about we add a method name to the entry point metadata?  (package.module.method)
        #    - if it is a module with a __main__, we invoke that, if it is a method, we call that
        pass




'''
def get_metadata(self):

ModelEngineMLFlow() - the URI is used to invoke the model
ModelEngineKubernetesJob() - etc.
ModelEngineSageMaker() - etc.

engine = ModelEngineLocal(default_model_path="/my_models")
run = ModelRunner("model1")
run.set_input(...)
engine.run(run)
'''

