from ._base_policy import initialization_policy
from .mlops import MLOps


def Project(local_environment:dict=None):

    if local_environment is None:
        local_environment = dict()
        local_environment['root'] = input('[MLOps:Root]:')
        local_environment['feature_store'] = input('[MLOps:FeatureStore]:')
        local_environment['model_registry'] = input('[MLOps:ModelRegistry]:')
        local_environment['source_repository'] = input('[MLOps:SourceRepository]:')
        local_environment['metadata_store'] = input('[MLOps:MetadataStore]:')
    elif isinstance(local_environment, dict):
        keys = local_environment.keys()
        assert 'root' in keys, 'The local_environment must include the root.'
        assert 'feature_store' in keys, 'The local_environment must include path of the feature_store.'
        assert 'model_registry' in keys, 'The local_environment must include path of the model_registry.'
        assert 'source_repository' in keys, 'The local_environment must include path of the source_repository.'
        assert 'metadata_store' in keys, 'The local_environment must include path of the metadata_store.'
    else:
        local_environment = None

    mlops = MLOps(initialization_policy(local_environment))
    return mlops

    

