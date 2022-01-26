import math
import string
import textwrap
from enum import Enum
from typing import Callable, Mapping, Optional, Union, List, Set

import pandas as pd
from deprecated import deprecated

from seeq.spy import _common
from seeq.spy import _pull
from seeq.spy import _push
from seeq.spy._errors import *
from seeq.spy._session import Session
from seeq.spy.assets._context import BuildContext, BuildMode, BuildPhase
from seeq.spy.workbooks import Analysis, AnalysisWorksheet, Topic, TopicDocument, DateRange


class WorkbookNotBuilt(SPyException):
    def __init__(self, workbook_type, workbook, worksheet=None):
        self.workbook_type = workbook_type
        self.workbook = workbook
        self.worksheet = worksheet


METHOD_TYPE_ATTR = 'spy_model'
FRIENDLY_NAME_ATTR = 'spy_friendly_name'


class MethodType(Enum):
    ATTRIBUTE = 'Attributes'
    COMPONENT = 'Components'
    DISPLAY = 'Displays'
    DATE_RANGE = 'Date Ranges'
    DOCUMENT = 'Documents'
    PLOT = 'Plots'
    REQUIREMENT = 'Requirements'


class PlotRenderInfo:
    def __init__(self, image_format, render_function):
        self.image_format = image_format
        self.render_function = render_function


def get_method_friendly_name(func: Callable):
    return func.__name__.replace('_', ' ')


class _AssetBase:
    definition: Union[dict, Mapping]
    context: BuildContext

    DEFAULT_WORKBOOK_NEEDED = '__DEFAULT_WORKBOOK_NEEDED__'
    UNKNOWN = '__unknown__'

    def __init__(self, context: BuildContext, definition: Union[dict, pd.DataFrame, pd.Series] = None, *, parent=None):
        """
        Instantiates an Asset or Mixin.

        :param context: A BuildContext object used to store information about the build operation and all other
        assets in the build.
        :type context: BuildContext
        :param definition: A dictionary of property-value pairs that make up the definition of the Asset or Mixin.
        Typically you will want to supply 'Name' at minimum.
        :type definition: dict, pd.DataFrame, pd.Series
        :param parent: An instance of either an Asset or Mixin that represents the parent of this instance. Typically
        this is supplied when @Asset.Component is used to define child assets.
        :type parent: Asset
        """
        self.definition = dict()

        if isinstance(definition, _AssetBase):
            self.definition = definition.definition
        elif isinstance(definition, pd.DataFrame):
            if len(definition) != 1:
                raise SPyValueError('DataFrame must be exactly one row')
            self.definition = definition.iloc[0].to_dict()
        elif isinstance(definition, pd.Series):
            self.definition = definition.to_dict()
        elif definition is not None:
            self.definition = definition

        if _common.present(self.definition, 'Path'):
            self.definition['Path'] = _common.sanitize_path_string(self.definition['Path'])

        self.definition['Type'] = 'Asset'
        if 'Name' in self.definition:
            # For an Asset, its name and the Asset column are made identical for clarity
            self.definition['Asset'] = self.definition['Name']

        self.context = context

        self._parent = self.UNKNOWN  # This is a cache for the parent once it is found

        if parent is not None and parent != self.UNKNOWN:
            self._parent = parent

            # Passing in a parent will relieve the user from having to construct the right path
            if _common.present(parent.definition, 'Path'):
                self.definition['Path'] = parent.definition['Path'] + ' >> ' + parent.definition['Name']
            else:
                self.definition['Path'] = parent.definition['Name']

        self.definition['Asset Object'] = self

        # 'Template' is set on the asset with the hope that, in the future, we will be able to search for items in
        # the asset tree that are derived from a particular template.
        self.definition['Template'] = self.template_friendly_name

        self.initialize()

        if not self.is_mixin:
            # Register ourselves in the build context
            context.add_object(self)

    def initialize(self):
        # This is for users to override so they don't have to know about the "crazy" __init__ function and its arguments
        pass

    @property
    def is_mixin(self):
        return issubclass(self.__class__, Mixin)

    def __contains__(self, key):
        return _common.present(self.definition, key)

    def __getitem__(self, key):
        return _common.get(self.definition, key)

    def __setitem__(self, key, val):
        self.definition[key] = val

    def __delitem__(self, key):
        del self.definition[key]

    def __repr__(self):
        return self.fqn

    @property
    @deprecated(reason="Use self.definition instead")
    def asset_definition(self):
        return self.definition

    @property
    @deprecated(reason="Use self.parent.definition instead")
    def parent_definition(self):
        return self.parent.definition if self.parent is not None else None

    @property
    def fqn(self):
        """
        The Fully-Qualified Name of this object, which includes both the Path and the Name using the usual >>
        separators.
        :return: The Fully-Qualified Name of this object
        :rtype: str
        """
        return '%s >> %s' % (_common.get(self, 'Path'), _common.get(self, 'Name'))

    @property
    def parent(self):
        """
        The parent Asset object of this Asset or Mixin, if it exists.
        :return: The parent asset object of this Asset of Mixin
        :rtype: _AssetBase
        """
        if self._parent != self.UNKNOWN:
            return self._parent

        expected_parent_path_list = _common.path_string_to_list(self.fqn)
        if len(expected_parent_path_list) == 0:
            self._parent = None
        else:
            expected_parent_path_list = expected_parent_path_list[0:-1]
            for asset in self.all_assets():
                if _common.path_string_to_list(asset.fqn) == expected_parent_path_list:
                    self._parent = asset
                    break

        return self._parent

    def all_assets(self):
        """
        All asset instances in the entire tree.

        Note that, during the INSTANTIATING build phase (the first), this function returns
        a blank list because not all asset objects have been instantiated yet.

        :return: A list of all asset instances in the entire tree.
        """
        if self.context.phase == BuildPhase.INSTANTIATING:
            # Since the context is currently being filled in with objects, it's better to return an empty list here
            # rather than confusingly returning a half-filled-in list.
            return list()

        return self.context.objects.values()

    def is_child_of(self, asset):
        """
        Tests if this asset instance (self) is a direct child of the specified asset.
        :param asset: The asset that might be self's parent
        :return: True if self is a direct child of asset
        """
        return self.parent == asset

    def is_parent_of(self, asset):
        """
        Tests if this asset instance (self) is a direct parent of the specified asset.
        :param asset: The asset that might be self's child
        :return: True if self is a direct parent of asset
        """
        return self == asset.parent

    def is_ancestor_of(self, asset):
        """
        Tests if this asset instance (self) is a parent or grandparent etc of the specified asset (looking all the way
        up the tree).
        :param asset: The asset that might be above self in the hierarchy
        :return: True if self is above asset
        """
        return asset.fqn.startswith(self.fqn) and asset.fqn != self.fqn

    def is_descendant_of(self, asset):
        """
        Tests if this asset instance (self) is a child or grandchild etc of the specified asset (looking all the way
        down the tree).
        :param asset: The asset that might be below self in the hierarchy
        :return: True if self is below asset
        """
        return self.fqn.startswith(asset.fqn) and asset.fqn != self.fqn

    def get_model_methods(self, method_type: MethodType = None):
        # Filter out property members so that the Deprecated library doesn't produce warnings as we iterate over them
        method_names = [m for m in dir(self) if m not in ['asset_definition', 'parent_definition', 'parent', 'fqn',
                                                          'is_mixin', 'template_name', 'template_friendly_name']]

        # Assemble a list of all functions on this object instance that are callable so that we can iterate over them
        # and find @Asset.Attribute() and @Asset.Component() functions
        object_methods = [getattr(self, method_name) for method_name in method_names
                          if callable(getattr(self, method_name))]

        # The "spy_model" attribute is added to any @Asset.Attribute() and @Asset.Component() decorated
        # functions so that they are processed during build
        remaining_methods = [func for func in object_methods if hasattr(func, METHOD_TYPE_ATTR)]

        if method_type:
            remaining_methods = filter(lambda m: getattr(m, METHOD_TYPE_ATTR) == method_type, remaining_methods)

        return remaining_methods

    def build(self, metadata: pd.DataFrame):
        definitions = list()
        context = self.context

        def _include_method(_func):
            # The build is made in two passes, first to instantiate the objects and then to build all the attributes,
            # requirements, documents, date ranges etc. Components must be touched in both phases because they
            # can instantiate objects.

            _func_type = getattr(_func, METHOD_TYPE_ATTR)
            if self.context.phase == BuildPhase.INSTANTIATING:
                return _func_type in [MethodType.COMPONENT, MethodType.REQUIREMENT]
            else:
                return _func_type not in [MethodType.REQUIREMENT]

        remaining_methods = [m for m in self.get_model_methods() if _include_method(m)]

        while len(remaining_methods) > 0:
            at_least_one_built = False
            asset_member_errors: Set[str] = set()
            workbooks_not_built = list()

            for func in remaining_methods.copy():
                func_type = getattr(func, 'spy_model')
                func_results = None

                # noinspection PyBroadException
                try:
                    func_results = func(metadata)

                except WorkbookNotBuilt as e:
                    workbooks_not_built.append(e)
                    continue

                except (SPyAssetMemberError, SPyComponentErrors) as e:
                    asset_member_errors.add(str(e))
                    continue

                except BaseException:
                    if self.context.errors == 'raise':
                        raise
                    else:
                        asset_member_errors.add(_common.format_exception())

                at_least_one_built = True
                remaining_methods.remove(func)

                if func_results is None or func_type not in [MethodType.ATTRIBUTE,
                                                             MethodType.COMPONENT,
                                                             MethodType.REQUIREMENT]:
                    continue

                if isinstance(func_results, list):
                    # This is the @Asset.Component case
                    definitions.extend(func_results)
                elif isinstance(func_results, dict):
                    # This is the @Asset.Attribute case
                    definitions.append(func_results)

            if not at_least_one_built and len(workbooks_not_built) > 0:
                for not_built in workbooks_not_built:
                    if (not_built.workbook_type, not_built.workbook) not in self.context.workbooks:
                        if not_built.workbook_type == 'analysis':
                            workbook = Analysis({'Name': not_built.workbook})
                        else:
                            workbook = Topic({'Name': not_built.workbook})
                        self.context.workbooks[(not_built.workbook_type, not_built.workbook)] = workbook

                at_least_one_built = True

            if not at_least_one_built and len(asset_member_errors) > 0:
                raise SPyAssetMemberErrors(self, asset_member_errors)

            if not at_least_one_built:
                raise SPyRuntimeError('Build failed: Build loop ended unexpectedly, contact Seeq support')

        if context.phase == BuildPhase.BUILDING and not self.is_mixin:
            definitions.append(self.definition)
            self.context.add_results(self.definition)

        self.definition['Build Result'] = BuildPhase.SUCCESS

        return definitions

    def build_component(self, template, metadata, component_name) -> List[dict]:
        """
        Builds a single component by instantiating the supplied template
        and building it with the supplied metadata.

        Parameters
        ----------
        template : {Asset}
            An asset class that is used to construct the attributes and sub-
            components.

        metadata : pd.DataFrame
            The metadata DataFrame containing all rows relevant to the
            sub-component.

        component_name : str
            The name of the sub-component. This will be used as the Name
            property of the instantiated asset (unless template is a Mixin.)

        Returns
        -------
        list(dict)
            A list of definitions (comprising one item). Note that this list
            will be empty in the first build phase (where self.context.phase
            equals BuildPhase.INSTANTIATING), as only the asset objects will
            have been instantiated.
        """

        instance = template(self.context, {
            'Name': component_name,
        }, parent=self)
        return instance.build(metadata)

    def build_components(self, template, metadata: pd.DataFrame, column_name: str) -> List[dict]:
        """
        Builds a set of components by identifying the unique values in the
        column specified by column_name and then instantiating the supplied
        template for each one and building it with the subset of metadata
        for that column value.

        Useful when constructing a rich model whereby a root asset is composed
        of unique components, possibly with further sub-components. For
        example, you may have a Plant asset that contains eight Refigerator
        units that each have two associated Compressor units.

        Parameters
        ----------
        template : {Asset}
            An asset class that is used to construct the attributes and sub-
            components.

        metadata : pd.DataFrame
            The metadata DataFrame containing all rows relevant to all
            (sub-)components of this asset. The DataFrame must contain the
            column specified by column_name.

        column_name : str
            The name of the column that will be used to discover the unique
            (sub-)components of this asset. For example, if column_name=
            'Compressor', then there might be values of 'Compressor A12' and
            'Compressor B74' in the 'Compressor' column of the metadata
            DataFrame.

        Returns
        -------
        list(dict)
            A list of definitions for each component. Note that this list
            will be empty in the first build phase (where self.context.phase
            equals BuildPhase.INSTANTIATING), as only the asset objects will
            have been instantiated.

        Examples
        --------
        Define a Refrigerator template that has Compressor subcomponents.

        >>> class Refrigerator(Asset):
        >>>     @Asset.Attribute()
        >>>     def Temperature(self, metadata):
        >>>         return metadata[metadata['Name'].str.endswith('Temperature')]
        >>>
        >>>     @Asset.Component()
        >>>     def Compressor(self, metadata):
        >>>         return self.build_components(Compressor, metadata, 'Compressor')
        >>>
        >>> class Compressor(Asset):
        >>>
        >>>     @Asset.Attribute()
        >>>     def Power(self, metadata):
        >>>         return metadata[metadata['Name'].str.endswith('Power')]
        """
        component_names = metadata[column_name].dropna().drop_duplicates().tolist()
        component_definitions = ItemGroup()
        asset_member_errors: Set[SPyAssetMemberErrors] = set()
        component_errors = set()
        for component_name in component_names:
            instance = template(self.context, {
                'Name': component_name,
            }, parent=self)

            # noinspection PyBroadException
            try:
                component_definition = instance.build(metadata[metadata[column_name] == component_name])
                component_definitions.extend(component_definition)

            except SPyAssetMemberErrors as e:
                asset_member_errors.add(e)

            except BaseException:
                if self.context.errors == 'raise':
                    raise
                else:
                    component_errors.add(_common.format_exception())

        if len(asset_member_errors) > 0:
            raise SPyComponentErrors(asset_member_errors)

        if len(component_errors) > 0:
            raise SPyRuntimeError('\n'.join(component_errors))

        return component_definitions

    def pull(self, items, *, start=None, end=None, grid='15min', header='__auto__', group_by=None,
             shape='auto', capsule_properties=None, tz_convert=None, calculation=None, bounding_values=False,
             errors='raise', session: Optional[Session] = None):
        session = Session.validate(session)

        if isinstance(items, list):
            items = pd.DataFrame(items)

        _common.validate_unique_dataframe_index(items, 'items')

        for index, item in items.iterrows():
            if not _common.present(item, 'ID') or _common.get(item, 'Reference', False):
                pushed_item = _push.get_from_push_df(item, self.context.push_df)
                items.at[index, 'ID'] = pushed_item['ID']

        return _pull.pull(pd.DataFrame(items), start=start, end=end, grid=grid, header=header, group_by=group_by,
                          shape=shape, capsule_properties=capsule_properties, tz_convert=tz_convert,
                          calculation=calculation, bounding_values=bounding_values, errors=errors,
                          status=self.context.status, session=session)

    @staticmethod
    def _add_asset_metadata(asset, attribute_definition):
        if 'Path' in asset.definition and 'Path' not in attribute_definition:
            attribute_definition['Path'] = asset.definition['Path']

        if 'Asset' in asset.definition and 'Asset' not in attribute_definition:
            attribute_definition['Asset'] = asset.definition['Asset']

        if 'Template' in asset.definition and 'Template' not in attribute_definition:
            attribute_definition['Template'] = asset.template_friendly_name

    @staticmethod
    def _build_attribute_definition(asset, func, func_results):
        attribute_definition = dict()

        def _preserve_originals():
            for _key in ['Name', 'Path', 'Asset', 'Datasource Class', 'Datasource ID', 'Data ID',
                         'Source Number Format', 'Source Maximum Interpolation', 'Source Value Unit Of Measure']:
                if _common.present(attribute_definition, _key):
                    attribute_definition['Referenced ' + _key] = attribute_definition[_key]
                    del attribute_definition[_key]

        if isinstance(func_results, pd.DataFrame):
            if len(func_results) == 1:
                attribute_definition.update(func_results.iloc[0].to_dict())
                _preserve_originals()
                attribute_definition['Reference'] = True
            elif len(func_results) > 1:
                raise SPyAssetMemberError(asset, func, f'Multiple attributes returned:\n{func_results}')
            else:
                raise SPyAssetMemberError(asset, func, 'No matching metadata row found')

        elif isinstance(func_results, dict):
            attribute_definition.update(func_results)
            if _common.present(func_results, 'ID'):
                # If the user is supplying an identifier, they must intend it to be a reference, otherwise
                # it can't be in the tree.
                attribute_definition['Reference'] = True

        if not _common.present(attribute_definition, 'Name'):
            attribute_definition['Name'] = get_method_friendly_name(func)

        attribute_definition['Asset'] = asset.definition['Name']
        attribute_definition['Asset Object'] = asset

        _AssetBase._add_asset_metadata(asset, attribute_definition)

        if 'Formula Parameters' in attribute_definition:
            for key, val in attribute_definition['Formula Parameters'].items():
                if val is None:
                    raise SPyAssetMemberError(
                        asset, func,
                        f'Formula Parameter "{key}" not found. If necessary, check for None before attempting to use '
                        'optional Requirements or Attribute dependencies and return None from your Attribute function '
                        'to exclude the calculated attribute from your asset (if desired).')

        for key in ['Formula', 'Description']:
            if key in attribute_definition and isinstance(attribute_definition[key], str):
                attribute_definition[key] = textwrap.dedent(attribute_definition[key]).strip()

        return attribute_definition

    @property
    def template_name(self):
        return self.__class__.__name__

    @property
    def template_friendly_name(self):
        return self.template_name.replace('_', ' ')

    @staticmethod
    def _set_wrapper_attrs(wrapper: Callable, method_type: MethodType, func: Callable):
        # Setting this attribute on the function itself makes it discoverable during build()
        setattr(wrapper, METHOD_TYPE_ATTR, method_type)

        setattr(wrapper, FRIENDLY_NAME_ATTR, get_method_friendly_name(func))
        setattr(wrapper, '__doc__', func.__doc__)

    @staticmethod
    def _call_and_catch(func, asset, *args):
        try:
            return func(asset, *args)
        except SPyException as e:
            raise SPyAssetMemberError(asset, func, str(e))
        except BaseException:
            raise SPyAssetMemberError(asset, func, _common.format_exception())

    # noinspection PyPep8Naming
    @classmethod
    def Attribute(cls):
        """
        This decorator appears as @Asset.Attribute on a function with a class that derives from Asset.
        """

        def attribute_decorator(func):
            def attribute_wrapper(self, metadata=None):
                # type: (_AssetBase, pd.DataFrame) -> Optional[dict]
                if (self, func.__name__) in self.context.cache:
                    return self.context.cache[(self, func.__name__)]

                if metadata is None:
                    raise SPyDependencyNotBuilt(self, func, 'attribute dependency not built')

                func_results = _AssetBase._call_and_catch(func, self, metadata)

                attribute_definition = None
                if func_results is not None:
                    attribute_definition = _AssetBase._build_attribute_definition(self, func, func_results)
                    attribute_definition['Build Result'] = BuildPhase.SUCCESS

                self.context.cache[(self, func.__name__)] = attribute_definition
                self.context.add_results(attribute_definition)

                return attribute_definition

            _AssetBase._set_wrapper_attrs(attribute_wrapper, MethodType.ATTRIBUTE, func)

            return attribute_wrapper

        return attribute_decorator

    # noinspection PyPep8Naming
    @classmethod
    def Component(cls):
        """
        This decorator appears as @Asset.Component on a function with a class that derives from Asset.
        """

        def component_decorator(func):
            def component_wrapper(self, metadata=None):
                # type: (_AssetBase, pd.DataFrame) -> ItemGroup
                if (self, func.__name__) in self.context.cache:
                    return self.context.cache[(self, func.__name__)]

                if metadata is None:
                    raise SPyDependencyNotBuilt(self, func, 'component dependency not built')

                func_results = _AssetBase._call_and_catch(func, self, metadata)

                component_definitions = ItemGroup()
                if func_results is not None:
                    if not isinstance(func_results, list):
                        func_results = [func_results]

                    for func_result in func_results:
                        if isinstance(func_result, _AssetBase):
                            _asset_obj = func_result  # type: _AssetBase
                            if not _common.present(_asset_obj.definition, 'Name'):
                                _asset_obj.definition['Name'] = get_method_friendly_name(func)
                            build_results = _asset_obj.build(metadata)
                            component_definitions.extend(build_results)
                        elif isinstance(func_result, dict):
                            component_definition = func_result  # type: dict
                            _AssetBase._add_asset_metadata(self, component_definition)
                            component_definitions.append(component_definition)

                if self.context.phase == BuildPhase.BUILDING:
                    # We do not want to store the definitions in the cache if we are in the INSTANTIATING phase. In
                    # fact, in that phase it would always be an empty list, which would not be correct to cache.
                    self.context.cache[(self, func.__name__)] = component_definitions
                    self.context.add_results(component_definitions)

                return component_definitions

            _AssetBase._set_wrapper_attrs(component_wrapper, MethodType.COMPONENT, func)

            return component_wrapper

        return component_decorator

    # noinspection PyPep8Naming
    @classmethod
    def Display(cls, analysis=None):
        def display_decorator(func):
            # noinspection PyUnusedLocal
            def display_wrapper(self, metadata=None):
                if (self, func.__name__) in self.context.cache:
                    # We've already built this
                    return self.context.cache[(self, func.__name__)]

                if ('analysis', analysis) not in self.context.workbooks:
                    raise WorkbookNotBuilt('analysis', analysis)

                worksheet_object = self.context.workbooks[('analysis', analysis)]  # type: AnalysisWorksheet

                workstep_object = _AssetBase._call_and_catch(func, self, metadata, worksheet_object)

                self.context.cache[(self, func.__name__)] = workstep_object

                return workstep_object

            _AssetBase._set_wrapper_attrs(display_wrapper, MethodType.DISPLAY, func)

            return display_wrapper

        return display_decorator

    # noinspection PyPep8Naming
    @classmethod
    def DateRange(cls):
        def date_range_decorator(func):
            # noinspection PyUnusedLocal
            def date_range_wrapper(self, metadata=None):
                if (self, func.__name__) in self.context.cache:
                    # We've already built this
                    return self.context.cache[(self, func.__name__)]

                date_range_spec = _AssetBase._call_and_catch(func, self, metadata)
                date_range_object = DateRange(date_range_spec, None)

                if 'Name' not in date_range_spec:
                    date_range_spec['Name'] = get_method_friendly_name(func)

                self.context.cache[(self, func.__name__)] = date_range_object

                return date_range_object

            _AssetBase._set_wrapper_attrs(date_range_wrapper, MethodType.DATE_RANGE, func)

            return date_range_wrapper

        return date_range_decorator

    # noinspection PyPep8Naming
    @classmethod
    def Document(cls, topic=None):
        def document_decorator(func):
            # noinspection PyUnusedLocal
            def document_wrapper(self, metadata=None):
                # type: (_AssetBase, pd.DataFrame) -> TopicDocument

                if (self, func.__name__) in self.context.cache:
                    # We've already built this
                    return self.context.cache[(self, func.__name__)]

                if ('topic', topic) not in self.context.workbooks:
                    raise WorkbookNotBuilt('topic', topic)

                topic_object = self.context.workbooks[('topic', topic)]  # type: Topic

                document_object = _AssetBase._call_and_catch(func, self, metadata, topic_object)

                self.context.cache[(self, func.__name__)] = document_object

                return document_object

            _AssetBase._set_wrapper_attrs(document_wrapper, MethodType.DOCUMENT, func)

            return document_wrapper

        return document_decorator

    # noinspection PyPep8Naming
    @classmethod
    def Plot(cls, image_format):
        def plot_decorator(func):
            # noinspection PyUnusedLocal
            def plot_wrapper(self, metadata=None):
                if (self, func.__name__) in self.context.cache:
                    # We've already built this
                    return self.context.cache[(self, func.__name__)]

                def _plot_function(date_range):
                    return _AssetBase._call_and_catch(func, self, metadata, date_range)

                plot_render_info = PlotRenderInfo(image_format, _plot_function)
                self.context.cache[(self, func.__name__)] = plot_render_info

                return plot_render_info

            _AssetBase._set_wrapper_attrs(plot_wrapper, MethodType.PLOT, func)

            return plot_wrapper

        return plot_decorator

    # noinspection PyPep8Naming
    @classmethod
    def Requirement(cls):
        def requirement_decorator(func):
            def requirement_wrapper(self, metadata=None):
                # type: (Asset, pd.DataFrame) -> Optional[dict, tuple]
                if (self, func.__name__) in self.context.cache:
                    return self.context.cache[(self, func.__name__)]

                if metadata is None and self.context.mode != BuildMode.BROCHURE:
                    raise SPyDependencyNotBuilt(self, func, 'requirement dependency not built')

                func_results = _AssetBase._call_and_catch(func, self, metadata)

                if isinstance(func_results, type):
                    if not issubclass(func_results, Asset):
                        raise ValueError(f'Requirement function returns non-Asset type: {func_results}')

                    if self.context.mode != BuildMode.BROCHURE:
                        return None

                    func_results = {
                        'Type': 'Template',
                        'Name': func_results.__name__.replace('_', ' '),
                        'Description': func_results.__doc__
                    }

                if self.context.mode == BuildMode.BROCHURE:
                    return func_results

                if not _common.present(func_results, 'Name'):
                    func_results['Name'] = get_method_friendly_name(func)

                asset_metadata: pd.DataFrame = metadata[(metadata['Build Path'] == self['Path']) &
                                                        (metadata['Build Asset'] == self['Asset']) &
                                                        (metadata['Type'] == 'Asset')]

                def _handle_optional():
                    if _common.get(func_results, 'Optional'):
                        self.context.cache[(self, func.__name__)] = None
                        return None
                    else:
                        raise SPyAssetMemberError(
                            self, func,
                            f'Requirement "{func_results["Name"]}" not found (required by "{self.__class__.__name__}")')

                if func_results['Type'] == 'Property':
                    if len(asset_metadata) != 0 and func_results['Name'] in asset_metadata.columns:
                        property_name = func_results['Name']
                        property_value = asset_metadata.iloc[0][func_results['Name']]

                        if pd.isna(property_value):
                            return _handle_optional()

                        self.context.cache[(self, func.__name__)] = property_value
                        self.definition[property_name] = property_value
                        return property_value

                    else:
                        return _handle_optional()

                requirement_metadata = metadata[(metadata['Build Path'] == self['Path']) &
                                                (metadata['Build Asset'] == self['Asset']) &
                                                (metadata['Name'] == func_results['Name'])]

                if len(requirement_metadata) == 0:
                    if _common.get(func_results, 'Type') == 'Scalar' and \
                            len(asset_metadata) != 0 and func_results['Name'] in asset_metadata.columns:

                        # This is the case where the user is satisfying a Scalar requirement by providing a column in
                        # the metadata DataFrame that specifies the Scalar value directly (as opposed to referring to
                        # an already-established Scalar item in Seeq).

                        scalar_name = func_results['Name']
                        scalar_value = asset_metadata.iloc[0][func_results['Name']]

                        if pd.isna(scalar_value):
                            return _handle_optional()

                        if _common.get(func_results, 'Unit Of Measure Family') == 'string':
                            scalar_value = _common.string_to_formula_literal(str(scalar_value))

                        requirement_metadata = {
                            'Name': scalar_name,
                            'Type': 'Scalar',
                            'Formula': scalar_value
                        }

                    else:
                        return _handle_optional()

                elif len(requirement_metadata) > 1:
                    raise SPyAssetMemberError(
                        self, func,
                        f'Duplicates found for "{func_results["Name"]}" (required by "{self.__class__.__name__}"):\n'
                        f'{requirement_metadata}')

                requirement_definition = _AssetBase._build_attribute_definition(self, func, requirement_metadata)

                requirement_definition['Requirement'] = True
                requirement_definition['Build Result'] = BuildPhase.SUCCESS

                self.context.cache[(self, func.__name__)] = requirement_definition
                self.context.add_results(requirement_definition)

                return requirement_definition

            _AssetBase._set_wrapper_attrs(requirement_wrapper, MethodType.REQUIREMENT, func)

            return requirement_wrapper

        return requirement_decorator


class Asset(_AssetBase):
    """
    A class derived from Asset can have @Asset.Attribute and @Asset.Component decorated functions that are executed
    as part of the call to build() which returns a list of definition dicts for the asset.
    """

    # This class does not differ from _AssetBase... but we separate it from Mixin so that
    # isinstance(mixin_object, Asset) doesn't return True and make things confusing.
    pass


class Mixin(_AssetBase):
    """
    A Mixin is nearly identical to an Asset, but it adds attributes/components to an otherwise-defined Asset. The
    definition argument that is passed into the constructor should be the definition of the otherwise-defined Asset.

    This allows asset tree designers to add a set of "special" attributes to a particular instance of an asset
    without "polluting" the main asset definition with attributes that most of the instances shouldn't have.
    """

    asset: Asset

    def __init__(self, context, definition, parent):
        # Adopt the "parent" asset's definition since this is a Mixin
        super().__init__(context, parent.definition, parent=parent.parent)

        self.asset = parent
        self.definition['Asset Object'] = self
        self.definition['Template'] = self.template_friendly_name


def do_paths_match_criteria(criteria, names):
    return do_lists_match_criteria(_common.path_string_to_list(criteria), _common.path_string_to_list(names))


def do_lists_match_criteria(criteria, names):
    end = max(len(criteria), len(names))
    for i in range(0, end):
        if i > len(criteria) - 1:
            return False

        criterion = criteria[i]
        if criterion == '**':
            remaining_criteria = criteria[i + 1:]
            for j in range(i, len(names) + 1):
                remaining_names = names[j:]
                if do_lists_match_criteria(remaining_criteria, remaining_names):
                    return True

        if i > len(names) - 1:
            return False

        name = names[i]
        if not _common.does_query_fragment_match(criterion, name, contains=False):
            return False

    return True


class ItemGroup(list):
    def __init__(self, _list=None):
        super().__init__(list(ItemGroup.flatten(_list) if _list else list()))

    @staticmethod
    def flatten(l):
        for el in l:
            if isinstance(el, list):
                yield from ItemGroup.flatten(el)
            else:
                yield el

    def pick(self, criteria):
        picked = ItemGroup()

        if not isinstance(criteria, dict):
            raise SPyValueError('pick(criteria) argument must be a dict')

        for definition in self:
            if definition is None:
                continue

            good = True
            for prop, criterion in criteria.items():
                if prop not in definition:
                    good = False
                    break

                val = definition[prop]

                # If they didn't specify Calculated vs Stored, match on both
                if criterion in ['Signal', 'Condition', 'Scalar']:
                    criterion = f'*{criterion}'

                if prop == 'Path':
                    if not do_paths_match_criteria(criterion, val):
                        good = False
                        break
                elif not _common.does_query_fragment_match(criterion, val, contains=False):
                    good = False
                    break

            if good:
                picked.append(definition)

        return picked

    def assets(self):
        picked = list()
        for definition in self:
            if definition is None:
                continue

            if 'Asset Object' in definition and definition['Asset Object'] not in picked:
                picked.append(definition['Asset Object'])

        return picked

    def as_parameters(self, *, prefix='p'):
        parameters = dict()
        zero_padding = int(math.log10(len(self))) + 1 if len(self) > 0 else 1
        for i in range(len(self)):
            definition = self[i]

            if definition is None:
                # We skip over None here, because it may be due to an optional requirement. This relieves the user
                # from having to always account for "holes" in the tree whenever doing roll-ups
                continue

            string_spec = '$%s{0:0%dd}' % (prefix, zero_padding)
            parameters[string_spec.format(i)] = definition

        return parameters

    def roll_up(self, statistic):
        parameters = self.as_parameters()

        if len(parameters) > 0:
            types = {p['Type'] for p in parameters.values()}
            if len(types) == 0:
                return None

            if len(types) > 1:
                debug_string = '\n'.join(
                    [_common.safe_json_dumps(p) for p in parameters.values()])
                raise SPyRuntimeError('Cannot compute statistics across different types of items:\n%s' % debug_string)

            _type = types.pop().replace('Stored', '').replace('Calculated', '')
            fns = {fn.statistic: fn for fn in _common.ROLL_UP_FUNCTIONS if fn.input_type == _type}

            if statistic.lower() not in fns:
                raise SPyValueError('Statistic "%s" not recognized for type %s. Valid statistics:\n%s' %
                                    (statistic, _type, '\n'.join([string.capwords(s) for s in fns.keys()])))
        else:
            fns = {fn.statistic: fn for fn in _common.ROLL_UP_FUNCTIONS}
            if statistic.lower() not in fns:
                raise SPyValueError('Statistic "%s" not recognized. Valid statistics:\n%s' %
                                    (statistic, '\n'.join([string.capwords(s) for s in fns.keys()])))

        fn = fns[statistic.lower()]  # type: _common.RollUpFunction

        param_list = list(parameters.keys())
        if len(parameters) > 1:
            if fn.style == 'union':
                formula = ' or '.join(param_list)
            elif fn.style == 'intersect':
                formula = ' and '.join(param_list)
            elif fn.style == 'fluent':
                formula = param_list[0]
                for p in param_list[1:]:
                    formula += f'.{fn.function}({p})'
            else:
                formula = f'{fn.function}({", ".join(param_list)})'
        elif len(parameters) == 1:
            parameter = param_list[0]
            if fn.function.startswith('count'):
                formula = f'{fn.function}({parameter})'
            elif fn.function == 'range':
                formula = '0.toSignal()'
            else:
                formula = parameter
        else:
            if fn.output_type == 'Signal':
                formula = 'SCALAR.INVALID.toSignal()'
            elif fn.output_type == 'Condition':
                formula = "condition(40d, capsule('1970-01-01T00:00:00Z', '1970-01-01T00:00:00Z'))"
            else:
                formula = 'SCALAR.INVALID'

        return {
            'Type': fn.output_type,
            'Formula': formula,
            'Formula Parameters': parameters
        }


class SPyAssetMemberError(SPyException):
    asset: _AssetBase
    func: Callable
    message: str

    def __init__(self, asset: _AssetBase, func: Callable, message: str):
        self.asset = asset
        self.func = func
        self.message = message

    def __str__(self):
        return f'"{SPyAssetMemberError._get_friendly_path_for_error(self.asset, self.func)}":' \
               f' {self.message}'

    @staticmethod
    def _get_friendly_path_for_error(asset: _AssetBase, func: Callable):
        full_path = asset.definition.get('Asset', '')
        if _common.present(asset.definition, 'Name') and _common.get(asset.definition, 'Type') != 'Asset':
            full_path += ' >> ' + asset.definition['Name']
        if _common.present(asset.definition, 'Path'):
            full_path = asset.definition['Path'] + ' >> ' + full_path

        if func is not None:
            full_path += ' >> ' + func.__name__

        full_path += f' [on {asset.__class__.__name__} class]'

        return full_path


class SPyAssetMemberErrors(SPyException):
    asset: _AssetBase
    errors: Set[str]

    def __init__(self, asset: _AssetBase, errors: Set[str]):
        self.asset = asset
        self.errors = errors

    def __str__(self):
        return f'The following issues could not be resolved:\n' \
               f'(If the cause is not immediately obvious, make sure to check for circular references.)\n' + \
               '\n'.join(self.errors)


class SPyComponentErrors(SPyException):
    errors: Set[SPyAssetMemberErrors]

    def __init__(self, errors: Set[SPyAssetMemberErrors]):
        self.errors = errors

    def __str__(self):
        return '\n'.join([str(e) for e in self.errors])


class SPyDependencyNotBuilt(SPyAssetMemberError):
    def __str__(self):
        return f'"{SPyAssetMemberError._get_friendly_path_for_error(self.asset, self.func)}"' \
               f' {self.message}'
