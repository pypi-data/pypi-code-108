import _ast
import inspect
import ast
import logging
import re
import typing

from enum import auto, Enum
from threading import Lock
from typing import Any, Dict, List
from deafadder_container.ContainerException import InstanceNotFound, MultipleAutowireReference, \
    AnnotatedDeclarationMissing

DEFAULT_INSTANCE_NAME = "default"

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Scope(Enum):
    """A Scope define hte type of Component that should be created.

    - SINGLETON means that the Component should be treated as a singleton (with different name possible) and should be
    retrievable.

    - PROTOTYPE means that the Component should not be a singleton, a new instance will be created each time we call
    the class init. However it is still treated as Component capable of autowiring and post initialization.
    """
    SINGLETON = auto()
    PROTOTYPE = auto()


class _NamedInstance:
    """Used internally to represent a named component instance"""

    def __init__(self, name: str, instance: any, tags: List[str] = None):
        self.name = name
        self.instance = instance
        self.tags = tags or []


class Component(type):
    _instances: Dict[Any, List[_NamedInstance]] = {}
    _lock: Lock = Lock()

    def __call__(cls, instance_name: str = DEFAULT_INSTANCE_NAME, scope: Scope = Scope.SINGLETON, tags: List[str] = None, *args, **kwargs):
        if scope == Scope.SINGLETON:
            return cls._singleton_scope_handler(instance_name, tags=tags, *args, **kwargs)
        elif scope == Scope.PROTOTYPE:
            return cls._prototype_scope_handler(*args, **kwargs)

    def _singleton_scope_handler(cls, instance_name: str, tags: List[str] = None, *args, **kwargs):
        """Create or retrieve the correct Singleton for the given class.

        For creation, perform autowiring when needed and post initialization when the _post_init method is
        available. It will then register the new instance in the collection of available instances so that
        it can be retrieved later when needed.

        :param instance_name: default value is 'default'. The name of the instance so it can be retrieved later
        :param args: the args of the __init__ method
        :param kwargs: the kwargs of the __init__ method
        :return: a new instance of the given class or an already existing instance
        """
        with cls._lock:

            if cls not in cls._instances:
                log.debug(f"(__call__ {cls}, {instance_name}) Component not present, initializing the entry in the instance record.")
                cls._instances[cls] = []

            if instance_name not in cls._known_instance_name_for_class(cls):
                log.debug(f"(__call__ {cls}, {instance_name}) No instance with name '{instance_name}' found for the Component. Creating it...")
                new_instance = super().__call__(*args, **kwargs)

                _AutowireMechanism(new_instance, cls, instance_name).apply()

                _apply_post_init(new_instance)

                cls._instances[cls].append(_NamedInstance(name=instance_name, instance=new_instance, tags=tags))
        container_entry = cls._get_entry_for_name(cls, instance_name)
        log.debug(f"(__call__ {cls}, {instance_name}) Instance found.")
        return container_entry.instance

    def _prototype_scope_handler(cls, *args, **kwargs):
        """Always create a new instance of the given class.

        Does not register the new instance for future reference and access but still perform autowiring and
        post initialization of the Component.

        :param args: the args of the __init__ method
        :param kwargs: the kwargs of the __init__ method
        :return: a new instance of the given class
        """
        with cls._lock:
            new_instance = super().__call__(*args, **kwargs)
            _AutowireMechanism(new_instance, cls, "<prototype>").apply()
            _apply_post_init(new_instance)
        return new_instance

    @staticmethod
    def get(cls, instance_name: str = DEFAULT_INSTANCE_NAME):
        """Retrieve a Component based on its class and name

        This method works as well for class that are not Component
        but treated as so thanks to Component.of(instance)

        -----------------------------------------------
        InDepth:
        --------

        class MyCustomComponent(metaclass=Component):
            pass

        Component.get(MyCustomComponent, "name")


        class NormalClass:
            pass

        Component.of(NormalClass())
        # this instance can be retrieve through:
        Component.get(NormalClass)

        -----------------------------------------------


        :param cls: the class for which you want its instance retrieve
        :param instance_name: the name of the instance to retrieve
        :return: the instance with the given name if present
        :raises: InstanceNotFound exception if there is no instance of the given class with the given name
        """
        if type(cls) is Component:
            return Component._get(cls, cls, instance_name=instance_name)
        else:
            return Component._get(_Anchor, cls, instance_name=instance_name)

    def _get(cls, actual_class, instance_name: str = DEFAULT_INSTANCE_NAME):
        """Anchor method to let static method access inner field such as lock and instance"""
        if actual_class in cls._instances and instance_name in cls._known_instance_name_for_class(actual_class):
            return cls._get_entry_for_name(actual_class, instance_name).instance
        else:
            raise InstanceNotFound(f"Unable to find an instance for {actual_class} with name '{instance_name}'")

    @staticmethod
    def get_all(cls, pattern: str = None, names: List[str] = None, tags: List[str] = None, dirty_context: bool = False) -> Dict[str, Any]:
        """ Get all registered instance of a given Component as a dict of name:instance

         -----------------------------------------------
        InDepth:
        --------

        class MyCustomComponent(metaclass=Component):
            pass

        i = MyCustomComponent()
        j = MyCustomComponent(instance_name="non default")

        compo_dict = Component.get_all(MyCustomComponent)
        # compo_dict = {"default": i, "non default": j}
        -----------------------------------------------

        :param cls: the class for which you want to get all instances
        :param pattern: a regex that describe the names of the instances you want to retrieve
        :param names: the list of names of the instances you want to retrieve
        :param tags: a list of tags that the instances you want to retrieve contains
        :param dirty_context: a bool to tell if we want to use the lock mechanism or not. This parameter
                              should only be used for internal use in the library
        :return: a dictionary containing all hte instance for the given class, as Dict[name:instance]
        """
        if not dirty_context:
            return Component._get_all_with_lock_context(
                cls if type(cls) is Component else _Anchor,
                cls, pattern=pattern, names=names, tags=tags
            )
        else:
            return Component._get_all(
                cls if type(cls) is Component else _Anchor,
                cls, pattern=pattern, names=names, tags=tags
            )

    def _get_all_with_lock_context(cls, actual_class, pattern: str = None, names: List[str] = None, tags: List[str] = None) -> Dict[str, Any]:
        """Anchor method to let static method access inner field such as lock and instance."""
        with cls._lock:
            return Component._get_all(cls, actual_class, pattern=pattern, names=names, tags=tags)

    def _get_all(cls, actual_class, pattern: str = None, names: List[str] = None, tags: List[str] = None) -> Dict[str, Any]:
        """Anchor method to let static method access inner field such as lock and instance."""
        if actual_class not in cls._instances:
            return {}
        else:
            if pattern is None and names is None and tags is None:
                return {i.name: i.instance for i in cls._instances[actual_class]}
            else:
                return {i.name: i.instance for i in cls._instances[actual_class]
                        if cls._name_match_pattern(i.name, pattern)
                        or cls._name_in_wanted_name_list(i.name, names)
                        or cls._tag_in_anted_tag_list(i.tags, tags)}

    @staticmethod
    def _name_match_pattern(name: str, pattern: str = None) -> bool:
        return re.match(pattern, name) if pattern is not None else False

    @staticmethod
    def _name_in_wanted_name_list(name: str, name_list: List[str] = None):
        return name in name_list if name_list is not None else False

    @staticmethod
    def _tag_in_anted_tag_list(instance_tags: List[str], wanted_tags: List[str] = None) -> bool:
        return any(x in instance_tags for x in wanted_tags) if wanted_tags is not None else False

    @staticmethod
    def delete(cls, instance_name: str = DEFAULT_INSTANCE_NAME):
        """Remove one specific instance form the list of possible instance for a given Component.

        -----------------------------------------------
        InDepth:
        --------

        class MyCustomComponent(metaclass=Component):
            pass

        Component.delete(MyCustomComponent, "name")
        -----------------------------------------------

        If a reference to the instance exist somewhere else, this reference will continue to exist.
        However, it will not be possible to retrieve the instance using Component.get() or using
        the autowire mechanism after use of this function.

        This is mostly for test purpose. Since there is very few use case that could need this
        deletion feature in real world scenario.

        :param cls: the class you want to delete an entry from
        :param instance_name: the name of the instance to delete
        :return:  Nothing
        :raises: InstanceNotFound exception if there is no instance of the given class with the given name
        """
        Component._delete_with_lock_context(
            cls if type(cls) is Component else _Anchor,
            cls, instance_name=instance_name
        )

    def _delete_with_lock_context(cls, actual_class, instance_name: str = DEFAULT_INSTANCE_NAME):
        """Anchor method to let static method access inner field such as lock and instance."""
        with cls._lock:
            Component._delete(cls, actual_class, instance_name=instance_name)

    def _delete(cls, actual_class, instance_name: str = DEFAULT_INSTANCE_NAME):
        """Anchor method to let static method access inner field such as lock and instance."""
        if actual_class in cls._instances and instance_name in cls._known_instance_name_for_class(actual_class):
            log.debug(f"(delete {actual_class}, {instance_name}) Deleting instance")
            cls._instances[actual_class] = list(filter(lambda i: i.name != instance_name, cls._instances[actual_class]))
        else:
            raise InstanceNotFound(f"Unable to find an instance for {actual_class} with name '{instance_name}'")

    @staticmethod
    def delete_all(cls, pattern: str = None, names: List[str] = None, tags: List[str] = None) -> None:
        """Remove all instance of the given Component from the possible references.

        -----------------------------------------------
        InDepth:
        --------

        class MyCustomComponent(metaclass=Component):
            pass

        Component.delete_all(MyCustomComponent)
        -----------------------------------------------

        If a reference to the instance exist somewhere else, this reference will continue to exist.
        However, it will not be possible to retrieve the instance using Component.get() or using
        the autowire mechanism after use of this function.

        This is mostly for test purpose. Since there is very few use case that could need this
        deletion feature in real world scenario.

        :return: Nothing
        """
        if type(cls) is Component:
            Component._delete_all(cls, cls, pattern=pattern, names=names, tags=tags)
        else:
            Component._delete_all(_Anchor, cls, pattern=pattern, names=names, tags=tags)

    def _delete_all(cls, actual_class, pattern: str = None, names: List[str] = None, tags: List[str] = None) -> None:
        """Anchor method to let static method access inner field such as lock and instance."""
        with cls._lock:
            instances = cls._get_all(actual_class, pattern=pattern, names=names, tags=tags)

            if not instances:
                log.debug(f"(delete_all) Nothing to do. No instance found for class {actual_class}")
            else:
                log.debug(f"(delete_all) Deleting entries for {actual_class}.")
                deleted_classes_string = str(instances.keys())
                for key in instances:
                    Component._delete(cls, actual_class, instance_name=key)
                if not cls._instances[actual_class]:
                    cls._instances.pop(actual_class)
                log.debug(f"(delete_all) Entries deleted: {deleted_classes_string}")

    @staticmethod
    def purge():
        """Remove all instance.

        If a reference to the instance exist somewhere else, this reference will continue to exist.
        However, it will not be possible to retrieve the instance using Component.get() or using
        the autowire mechanism after use of this function.

        This is mostly for test purpose. Since there is very few use case that could need this
        deletion feature in real world scenario.

        :return: Nothing
        """
        Component._purge(_Anchor)

    def _purge(cls):
        """Inner function to remove all instance from the dict.

        It is splat this way in order to let the purge function be static, but still access
        class level attribute.

        Anchor method to let static method access inner field such as lock and instance.
        """
        with cls._lock:
            keys = [k for k, v in cls._instances.items()]
            log.debug(f"(purge) Deleting all instances for the following Component: {keys}")
            for k in keys:
                cls._instances.pop(k)

    @staticmethod
    def of(instance, instance_name: str = DEFAULT_INSTANCE_NAME):
        """Create a Component out of a simple instance

        :param instance: the instance you want to convert to Component
        :param instance_name: the name of the instance you want to create
        :return: the instance passed as parameter, but as a Component
        """
        return Component._of(_Anchor, instance.__class__, instance, instance_name)

    def _of(cls, normal_class, instance, instance_name: str = DEFAULT_INSTANCE_NAME):
        """Anchor method to let static method access inner field such as lock and instance."""
        with cls._lock:
            if normal_class not in cls._instances:
                log.debug(f"(of) no entry for class {normal_class} found, adding the entry to the collection of instances.")
                cls._instances[normal_class] = []
            if instance_name not in cls._known_instance_name_for_class(normal_class):
                cls._instances[normal_class].append(_NamedInstance(instance_name, instance))
                log.debug(f"(of) instance with name '{instance_name}', created.")
            return cls._get_entry_for_name(normal_class, instance_name).instance

    def _known_instance_name_for_class(cls, actual_class) -> List[str]:
        return [i.name for i in cls._instances[actual_class]]

    def _get_entry_for_name(cls, actual_class, instance_name) -> _NamedInstance:
        return next(filter(lambda i: i.name == instance_name, cls._instances[actual_class]))

    @staticmethod
    def contains(cls) -> bool:
        """ Check if the collection of managed instances contains an entry for the given class.

        Used for the autowiring mechanism to handle component created with Component.of
        Could be used for other purpose but the usage should be quite limited.

        :param cls: the class we want to check if an instance is present in the collection
        :return: true if an instance of the class is present in the list of managed instances
                 false otherwise
        """
        return Component._contains(_Anchor, cls)

    def _contains(cls, actual_class) -> bool:
        """Anchor method to let static method access inner field such as lock and instance."""
        return actual_class in cls._instances and cls._instances[actual_class]


class _Anchor(metaclass=Component):
    """This is a dummy class only to enable access to the metaclass inner field through it."""
    pass


class _AutowireType(Enum):
    INSTANCE = auto()
    LIST = auto()
    DICT = auto()

    @staticmethod
    def from_generic(generic_alias):
        if type(generic_alias) is typing._GenericAlias:
            if generic_alias.__origin__ is list:
                return _AutowireType.LIST
            if generic_alias.__origin__ is dict:
                return _AutowireType.DICT

    def is_collection(self):
        return self in [_AutowireType.LIST, _AutowireType.DICT]


class _AutowireCandidate:
    """Used internally for autowiring mechanism.
    It groups together the attribute to autowire in the Component, the component instance name to use and the component class to use
    for injection.
    """

    attribute_name: str
    component_instance_name: List[str]
    component_class: Any
    autowire_type: _AutowireType

    def __init__(self,
                 attribute_name: str = None,
                 component_instance_name: List[str] = None,
                 component_class: Any = None,
                 autowire_type: _AutowireType = None):
        self.attribute_name = attribute_name
        self.component_instance_name = component_instance_name or []
        self.component_class = component_class
        self.autowire_type = autowire_type

    def set(self,
            attribute_name: str = None,
            component_instance_name: List[str] = None,
            component_class: Any = None,
            autowire_type: _AutowireType = None):
        self.attribute_name = attribute_name or self.attribute_name
        self.component_instance_name = component_instance_name or self.component_instance_name
        self.component_class = component_class or self.component_class
        self.autowire_type = autowire_type or self.autowire_type
        return self

    def is_default(self):
        return len(self.component_instance_name) == 0

    def is_collection(self):
        return self.autowire_type is not None and self.autowire_type.is_collection()

    def is_dict_collection(self):
        return self.autowire_type is not None and self.autowire_type is _AutowireType.DICT


class _AutowireMechanism:
    """Package the autowiring mechanism

    This class is used by the Component metaclass in order to detect filed that are Component and can be autowire
    either explicitly (with the autowire decorator) or implicitly (when the component with the default name is
    required).

    It uses ast to parse the Abstract Syntax Tree and inspect to get the source of the Component.

    Each component, at creation time, will be inspected by this class to detect if autowiring is needed and, if so,
    retrieve the correct instance to inject into the correct fields.
    """
    autowire_triplet_candidates: List[_AutowireCandidate] = []
    _autowire_candidates: List[_AutowireCandidate] = []
    _autowire_non_default_candidates: List[_AutowireCandidate] = []
    _autowire_default_candidates: List[_AutowireCandidate] = []
    _instance = None
    _cls = None
    _instance_name = None

    def __init__(self, instance, cls, instance_name):
        try:
            instance.__annotations__
        except AttributeError:
            return

        self._instance = instance
        self._cls = cls
        self._instance_name = instance_name

        self._infer_autowire_candidates()
        self._infer_explicit_autowire_candidates()
        self._infer_autowire_default_candidates()
        self.autowire_triplet_candidates = [*self._autowire_default_candidates, *self._autowire_non_default_candidates]

    def apply(self):
        """Apply auto wire mechanism on the given instance.

        After init of this class, if any filed need to be injected using the auto wire mechanism,
        this method inject the correct instance into all those field that requires automatic injection
        of Component.

        :return: None
        """
        if self.autowire_triplet_candidates:
            log.debug(f"(_AutowireMechanism.apply {self._cls}, {self._instance_name}) Injecting dependencies:")
        else:
            log.debug(f"(_AutowireMechanism.apply {self._cls}, {self._instance_name}) Nothing to inject")
        for autowire_candidate in self.autowire_triplet_candidates:
            log.debug(f"(_AutowireMechanism.apply {self._cls}, {self._instance_name})      Injecting the dependency "
                      f"{autowire_candidate.component_class} with name '{autowire_candidate.component_instance_name}' "
                      f"in the field '{autowire_candidate.attribute_name}'")
            self._autowire(autowire_candidate)

        if self.autowire_triplet_candidates:
            log.debug(f"(_AutowireMechanism.apply {self._cls}, {self._instance_name}) Dependency injection finished")

    def _autowire(self, candidate: _AutowireCandidate):
        if candidate.is_collection():
            instance_names_to_inject = candidate.component_instance_name
            if candidate.is_default():
                element_dict_to_inject = Component.get_all(candidate.component_class, dirty_context=True)
            else:
                element_dict_to_inject = Component.get_all(candidate.component_class, names=instance_names_to_inject, dirty_context=True)

            element_to_inject = element_dict_to_inject if candidate.is_dict_collection() else [v for _, v in element_dict_to_inject.items()]

        else:
            # this is a single instance to inject directly, not inside a collection
            instance_name_to_inject = DEFAULT_INSTANCE_NAME if candidate.is_default() else candidate.component_instance_name[0]
            element_to_inject = Component.get(candidate.component_class, instance_name_to_inject)

        setattr(self._instance, candidate.attribute_name, element_to_inject)

    def _infer_autowire_candidates(self):
        annotations = self._instance.__annotations__
        self._autowire_candidates = [_AutowireCandidate(attribute_name=k,
                                                        component_class=self._base_component_class(v),
                                                        autowire_type=self._get_injection_type(v))
                                     for k, v in annotations.items()
                                     if not hasattr(self._instance, k)
                                     and (self._is_component(v) or self._is_collection_of_component(v))]

    @staticmethod
    def _is_component(clazz) -> bool:
        # type(x) return the metaclass of the class (whatever the inheritance level)
        # so type(x) is either Component or something else in our case
        if type(clazz) is Component or Component.contains(clazz):
            return True
        else:
            return False

    @staticmethod
    def _is_collection_of_component(clazz) -> bool:
        if type(clazz) is typing._GenericAlias and clazz.__origin__ in (list, dict):
            if clazz.__origin__ is list:
                return _AutowireMechanism._is_component(clazz.__args__[0])
            if clazz.__origin__ is dict:
                return _AutowireMechanism._is_component(clazz.__args__[1])
        return False

    @staticmethod
    def _base_component_class(clazz):
        if _AutowireMechanism._is_component(clazz):
            return clazz
        if type(clazz) is typing._GenericAlias:
            if clazz.__origin__ is list and _AutowireMechanism._is_component(clazz.__args__[0]):
                return clazz.__args__[0]
            if clazz.__origin__ is dict and _AutowireMechanism._is_component(clazz.__args__[1]):
                return clazz.__args__[1]

    @staticmethod
    def _get_injection_type(clazz):
        if _AutowireMechanism._is_component(clazz):
            return _AutowireType.INSTANCE
        if _AutowireMechanism._is_collection_of_component(clazz):
            return _AutowireType.from_generic(clazz)

    @staticmethod
    def _get_init_decorators(cls):
        """Parse the AST to retrieve all decorator on the __init__ method for a given class"""
        target = cls
        init_decorators = {}

        def get_string_value(decorator_arg: _ast.keyword) -> List[str]:
            elements = []

            # if the keyword is a simple element, like a string, then we the keyword.value has a value attribute
            # that contains the string
            # else, it is a list keyword and it contains an elts attribute where each element has a value attribute
            if hasattr(decorator_arg.value, "value"):
                elements.append(decorator_arg.value.value)
            elif hasattr(decorator_arg.value, "elts"):
                for e in decorator_arg.value.elts:
                    elements.append(e.value)
            return elements

        def visit_function_def(node):
            if node.name != "__init__":
                return
            for n in node.decorator_list:
                decorator_args = []
                name = ''
                if isinstance(n, ast.Call):
                    name = n.func.attr if isinstance(n.func, ast.Attribute) else n.func.id
                    if name != "autowire":
                        # might have an issue if the decorator is not exactly @autowire (like
                        # with renaming on import or full import @deafadder_container.Wiring.autowire
                        # or @Wiring.autowire. Will see later if there is an issue or a better way to do so
                        # Could also cause an issue if we have another decorator from another package called
                        # autowire.
                        continue
                    decorator_args = [(decorator_arg.arg, get_string_value(decorator_arg)) for decorator_arg in n.keywords]
                # to be complete, the decorator without parenthesis should be included. But since we
                # don't really need it, we can ignore it for now
                #
                # Sample code to be complete
                # > else:
                # >    name = n.attr if isinstance(n, ast.Attribute) else n.id

                if name not in init_decorators:
                    init_decorators[name] = []
                init_decorators[name].append(decorator_args)

        node_iter = ast.NodeVisitor()
        node_iter.visit_FunctionDef = visit_function_def
        node_iter.visit(ast.parse(inspect.getsource(target)))
        return init_decorators

    def _infer_explicit_autowire_candidates(self):
        init_decorators = self._get_init_decorators(self._instance.__class__)
        if not init_decorators:
            self._autowire_non_default_candidates = []
            return
        autowire_decorators = init_decorators["autowire"]
        flattened_args = [t for sublist in autowire_decorators for t in sublist]

        all_args_name = [i[0] for i in flattened_args]

        duplicate_args = [name for name, times in self._count_name_occurrence(all_args_name).items() if times > 1]
        if len(duplicate_args) > 0:
            raise MultipleAutowireReference(f"The following arguments are referenced multiple times in autowire: {', '.join(duplicate_args)}")

        annotated_elements = [i.attribute_name for i in self._autowire_candidates]
        not_annotated_elements_in_explicit_autowire = [i for i in all_args_name if i not in annotated_elements]
        if len(not_annotated_elements_in_explicit_autowire) > 0:
            raise AnnotatedDeclarationMissing(f"Elements to autowire '{', '.join(not_annotated_elements_in_explicit_autowire)}'"
                                              f" should be defined and annotated at class level.")

        autowire_non_default_candidates_dict = {
            candidate.attribute_name: candidate
            for candidate in self._autowire_candidates
            if candidate.attribute_name in all_args_name
        }
        self._autowire_non_default_candidates = [
            autowire_non_default_candidates_dict[t[0]].set(component_instance_name=t[1])
            for t in flattened_args
        ]

    @staticmethod
    def _count_name_occurrence(names: list) -> dict:
        """This class is used to count the """
        occurrences = {name: 0 for name in set(names)}
        for name in names:
            occurrences[name] = occurrences[name] + 1
        return occurrences

    def _infer_autowire_default_candidates(self) -> None:
        """Retrieve all field in the component that should be autowired using the default instance if present.

        It does not return any value but store the result inside the _autowire_default_candidates attribute
        """
        non_default_attribute_name = [i.attribute_name for i in self._autowire_non_default_candidates]
        all_candidates_attribute_name = [i.attribute_name for i in self._autowire_candidates]
        default_candidates = set(all_candidates_attribute_name) - set(non_default_attribute_name)

        self._autowire_default_candidates = [
            candidate
            for candidate in self._autowire_candidates
            if candidate.attribute_name in default_candidates
        ]


def _apply_post_init(instance):
    post_init = getattr(instance, "_post_init", None)
    if callable(post_init):
        instance._post_init()
