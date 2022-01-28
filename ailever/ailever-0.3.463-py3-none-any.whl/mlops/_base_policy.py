import os
import shutil

class ConceptualHierarchy:
    def __init__(self, name:str=None):
        self.__level = 0
        self.__name = name if name else None

    def __str__(self):
        return self.__name

    def hierarchy(self, name:str=None): 
        instance = super().__new__(type(self))
        instance.__init__(name=name)
        return instance

    def rename(self, name:str):
        self.__name = name

    @property
    def name(self):
        return self.__name

class BasePolicyHierarchy:
    def __init__(self, name:str=None):
        self.__path = ''
        self.__parent_name = ''
        self.__ascendants = list()
        self.__level = 0
        self.__name = name if name else None

    def __str__(self):
        return self.__name

    def hierarchy(self, name:str=None): 
        instance = super().__new__(type(self))
        instance.__init__(name=name)
        return instance

    def compiling(self, mkdir:bool=False):
        if mkdir:
            path = str(self)
            if not os.path.isdir(path):
                os.mkdir(path)

        children = self._compiling(self, mkdir=mkdir)
        while children:
            _children = list()
            for child in children:
                _children.extend(self._compiling(child, mkdir))
            children = _children
        self.path = [self.name]

    @staticmethod
    def _compiling(parent, mkdir:bool=False):
        selected_objs = filter(lambda x: isinstance(x[1], type(parent)), vars(parent).items())
        children = list(map(lambda child: vars(parent)[child[0]], selected_objs))
        for child_obj in children:
            child_obj.parent_name = parent.name
            child_obj.ascendants = (parent.ascendants, parent.name)
            child_obj.path = child_obj.ascendants + [child_obj.name]
            child_obj.level = parent.level + 1
            if mkdir:
                path = child_obj.path
                if not os.path.isdir(path):
                    os.mkdir(path)
        return children

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, bases:list):
        self.__path = os.path.join(*bases)

    @property
    def parent_name(self):
        return self.__parent_name

    @parent_name.setter
    def parent_name(self, name:str):
        self.__parent_name = name

    @property
    def ascendants(self):
        return self.__ascendants

    @ascendants.setter
    def ascendants(self, ascendants:tuple):
        self.__ascendants.extend(ascendants[0])
        self.__ascendants.append(ascendants[1])

    def listdir(self, format:str=None):
        self._listdir = os.listdir(self.path)
        if format:
            assert isinstance(format, str), 'The format argements must be object of string-type.'
            self._listdir = list(filter(lambda x: x[-len(format):]==format, self._listdir))
        return self._listdir

    def rename(self, name:str):
        self.__name = name

    def remove(self, name:str):
        os.remove(os.path.join(self.__path, name))

    def rmdir(self, name:str):
        shutil.rmtree(os.path.join(self.__path, name))
    
    def mkdir(self, name:str):
        path = os.path.join(self.__path, name)
        if not os.path.isdir(path):
            os.mkdir(path)

    @property
    def name(self):
        return self.__name

    @property
    def level(self):
        return self.__level

    @level.setter
    def level(self, level:int):
        self.__level = level


def initialization_policy(local_environment:dict=None):

    r"""
    Usage:
        >>> # without arguments
        >>> from ._base_policy import initialization_policy
        >>> initialization_policy()
       
        >>> # with arguments
        >>> from ._base_policy import initialization_policy
        >>> local_environment = dict()
        >>> local_environment['root'] = '.mlops'
        >>> local_environment['feature_store'] = 'feature_store'
        >>> local_environment['model_registry'] = 'model_registry'
        >>> local_environment['source_repository'] = 'source_repository'
        >>> local_environment['metadata_store'] = 'metadata_store'
        >>> initialization_policy(local_environment=local_environment)

        >>> from ailever.mlops import __mlops_bs__ as mlops_bs
        >>> mlops_bs.file_system.root.feature_store.listdir()  # files in directory
        >>> mlops_bs.file_system.root.feature_store.remove()   # delete file
        >>> mlops_bs.file_system.root.feature_store.rmdir()    # delete folder
        >>> mlops_bs.file_system.root.feature_store.path
        >>> mlops_bs.file_system.root.feature_store.name
    """

    mlops_bs = ConceptualHierarchy('MLOpsPackage')
    mlops_bs.file_system = mlops_bs.hierarchy('file_system')

    mlops = BasePolicyHierarchy('.mlops')
    mlops_bs.file_system.root = mlops
    mlops_bs.file_system.root.feature_store = mlops.hierarchy('feature_store')
    mlops_bs.file_system.root.model_registry = mlops.hierarchy('model_registry')
    mlops_bs.file_system.root.source_repository = mlops.hierarchy('source_repository')
    mlops_bs.file_system.root.metadata_store = mlops.hierarchy('metadata_store')

    if local_environment:
        assert isinstance(local_environment, dict), 'The local_environment information must be supported by wtih dictionary data-type.'
        assert 'root' in local_environment.keys(), 'Set your root name.'
        assert 'feature_store' in local_environment.keys(), 'Set your feature_store name.'
        assert 'model_registry' in local_environment.keys(), 'Set your model_registry name.'
        assert 'source_repository' in local_environment.keys(), 'Set your source_repository name.'
        assert 'metadata_store' in local_environment.keys(), 'Set your metadata_store name.'

        mlops_bs.file_system.root.rename(local_environment['root'])
        mlops_bs.file_system.root.feature_store.rename(local_environment['feature_store'])
        mlops_bs.file_system.root.model_registry.rename(local_environment['model_registry'])
        mlops_bs.file_system.root.source_repository.rename(local_environment['source_repository'])
        mlops_bs.file_system.root.metadata_store.rename(local_environment['metadata_store'])

    mlops.compiling(mkdir=True)

    r"""
    - .mlops
      |-- feature_store
      |-- model_registry
      |-- source_repository
      |-- metadata_store
    """

    mlops_bs.core = dict()
    mlops_bs.core['MLOPS'] = mlops_bs.file_system.root
    mlops_bs.core['FS'] = mlops_bs.file_system.root.feature_store
    mlops_bs.core['SR'] = mlops_bs.file_system.root.source_repository
    mlops_bs.core['MR'] = mlops_bs.file_system.root.model_registry
    mlops_bs.core['MS'] = mlops_bs.file_system.root.metadata_store

    return mlops_bs


