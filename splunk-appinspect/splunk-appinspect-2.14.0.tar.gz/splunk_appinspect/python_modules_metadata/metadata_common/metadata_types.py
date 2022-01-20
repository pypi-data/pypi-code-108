from enum import Enum

from splunk_appinspect.python_analyzer.ast_types import (
    AstCallableFunction,
    AstClass,
    AstContext,
    AstModule,
    AstVariable,
)


class Metadata(object):
    def __init__(self, name, namespace, description, tags, python_object):
        self.name = name
        self.namespace = namespace
        self.description = description

        assert isinstance(self.name, str)
        assert isinstance(self.namespace, str)

        if self.description is None:
            self.description = ""
        assert isinstance(self.description, str)
        self.description = self.description.strip()

        if tags is None:
            self.tags = set()
        else:
            # only accept iter collection
            assert hasattr(tags, "__iter__")
            self.tags = set(tags)

        self.python_object = python_object

    def add(self, metadata):
        pass

    def instantiate(self):
        pass


class ModuleMetadata(Metadata):
    def __init__(self, name, namespace, description, tags=None, python_object=None):
        # in case check writer pass a enum as argument
        if isinstance(name, Enum):
            name = name.value
        super(ModuleMetadata, self).__init__(
            name, namespace, description, tags, python_object
        )
        self._sub_modules = []
        self._functions = []
        self._classes = []

    def __str__(self):
        return "Module name: {}, Sub Module names: {}, Function names: {}, Classes: {}".format(
            self.name,
            ", ".join(map(lambda node: node.name, self._sub_modules)),
            ", ".join(map(lambda node: node.name, self._functions)),
            ", ".join(map(lambda node: node.name, self._classes)),
        )

    def add(self, metadata):
        if isinstance(metadata, ModuleMetadata):
            self.sub_modules.append(metadata)
        elif isinstance(metadata, FunctionMetadata):
            self.functions.append(metadata)
        elif isinstance(metadata, ClassMetadata):
            self.classes.append(metadata)
        else:
            raise Exception("Illegal Metadata types {}".format(str(type(metadata))))

    def instantiate(self):

        ast_module = AstModule(self.name, namespace=self.namespace)
        for sub_module in self._sub_modules:
            ast_module.global_map[sub_module.name] = sub_module.instantiate()
        for function in [func for func in self._functions if func.instantiate()]:
            ast_module.global_map[function.name] = function.instantiate()
        for class_instance in self._classes:
            ast_module.global_map[class_instance.name] = class_instance.instantiate()
        return ast_module

    @property
    def sub_modules(self):
        return self._sub_modules

    @property
    def functions(self):
        return self._functions

    @property
    def classes(self):
        return self._classes


class ClassMetadata(Metadata):
    def __init__(self, name, namespace, description, tags=None, python_object=None):
        super(ClassMetadata, self).__init__(
            name, namespace, description, tags, python_object
        )
        self._functions = []
        self._classes = []

    def add(self, metadata):
        if isinstance(metadata, FunctionMetadata):
            self._functions.append(metadata)
        elif isinstance(metadata, ClassMetadata):
            self._classes.append(metadata)
        else:
            raise Exception("Illegal metadata type {}".format(str(type(metadata))))

    def instantiate(self):

        ast_class = AstClass(self.name, AstContext(0, None), namespace=self.namespace)
        for function in [func for func in self._functions if func.instantiate()]:
            ast_class.function_dict[function.name] = function.instantiate()
        for sub_class in self._classes:
            ast_class.class_context.variable_map[sub_class.name] = AstVariable(
                None, {AstVariable.CLASS_TYPE}, sub_class.instantiate()
            )
        return ast_class

    def __str__(self):
        return "Class name: {}, Class names: {}, Function names: {}".format(
            self.name,
            ", ".join(map(lambda node: node.name, self._classes)),
            ", ".join(map(lambda node: node.name, self._functions)),
        )

    @property
    def functions(self):
        return self._functions

    @property
    def classes(self):
        return self._classes

    @property
    def module_name(self):
        return ".".join(self.namespace.split(".")[:-1])


class FunctionMetadata(Metadata):
    def __init__(self, name, namespace, description, tags=None, python_object=None):
        super(FunctionMetadata, self).__init__(
            name, namespace, description, tags, python_object
        )

    def __str__(self):
        return "Function name: {}, function description: {}".format(
            self.name, self.description
        )

    def instantiate(self):
        python_function_object_in_metadata, function_name, function_namespace = (
            self.python_object,
            self.name,
            self.namespace,
        )

        if not hasattr(python_function_object_in_metadata, "executable"):
            return None

        class PythonFunction(AstCallableFunction):
            def __init__(self):
                AstCallableFunction.__init__(self, function_name, function_namespace)

            def action(self, function_node, analyzer, args, keywords, context):
                # Delegate function call procedure to python function object
                # Keep user defined function simple, only args and keywords are required positional arguments
                # other arguments are optional keyword arguments
                return python_function_object_in_metadata(
                    args,
                    keywords,
                    function_node=function_node,
                    analyzer=analyzer,
                    context=context,
                )

        return PythonFunction()

    @property
    def module_name(self):
        return ".".join(self.namespace.split(".")[:-1])
