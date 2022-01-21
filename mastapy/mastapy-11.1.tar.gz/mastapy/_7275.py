'''_7275.py

TaskProgress
'''


from typing import (
    List, Callable, Iterable, Optional
)

from mastapy._internal import constructor, conversion
from mastapy._internal.class_property import classproperty
from mastapy._internal.python_net import python_net_import

_ARRAY = python_net_import('System', 'Array')
_STRING = python_net_import('System', 'String')
_ACTION = python_net_import('System', 'Action')
_TASK_PROGRESS = python_net_import('SMT.MastaAPIUtility', 'TaskProgress')


__docformat__ = 'restructuredtext en'
__all__ = ('TaskProgress',)


class TaskProgress:
    '''TaskProgress

    This is a mastapy class.
    '''

    TYPE = _TASK_PROGRESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TaskProgress.TYPE'):
        self.wrapped = instance_to_wrap
        self._freeze()

    __frozen = False

    def __setattr__(self, attr, value):
        prop = getattr(self.__class__, attr, None)
        if isinstance(prop, property):
            prop.fset(self, value)
        else:
            if self.__frozen and attr not in self.__dict__:
                raise AttributeError((
                    'Attempted to set unknown '
                    'attribute: \'{}\''.format(attr))) from None

            super().__setattr__(attr, value)

    def __delattr__(self, name):
        raise AttributeError(
            'Cannot delete the attributes of a mastapy object.') from None

    def _freeze(self):
        self.__frozen = True

    @property
    def title(self) -> 'str':
        '''str: 'Title' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Title

    @property
    def status(self) -> 'str':
        '''str: 'Status' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Status

    @property
    def current_item(self) -> 'int':
        '''int: 'CurrentItem' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CurrentItem

    @property
    def total_items(self) -> 'int':
        '''int: 'TotalItems' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalItems

    @property
    def show_progress(self) -> 'bool':
        '''bool: 'ShowProgress' is the original name of this property.'''

        return self.wrapped.ShowProgress

    @show_progress.setter
    def show_progress(self, value: 'bool'):
        self.wrapped.ShowProgress = bool(value) if value else False

    @property
    def show_completion_status(self) -> 'bool':
        '''bool: 'ShowCompletionStatus' is the original name of this property.'''

        return self.wrapped.ShowCompletionStatus

    @show_completion_status.setter
    def show_completion_status(self, value: 'bool'):
        self.wrapped.ShowCompletionStatus = bool(value) if value else False

    @property
    def can_cancel(self) -> 'bool':
        '''bool: 'CanCancel' is the original name of this property.'''

        return self.wrapped.CanCancel

    @can_cancel.setter
    def can_cancel(self, value: 'bool'):
        self.wrapped.CanCancel = bool(value) if value else False

    @property
    def additional_string_to_add_to_title(self) -> 'str':
        '''str: 'AdditionalStringToAddToTitle' is the original name of this property.'''

        return self.wrapped.AdditionalStringToAddToTitle

    @additional_string_to_add_to_title.setter
    def additional_string_to_add_to_title(self, value: 'str'):
        self.wrapped.AdditionalStringToAddToTitle = str(value) if value else ''

    @property
    def is_progress_tree_cell_expanded(self) -> 'bool':
        '''bool: 'IsProgressTreeCellExpanded' is the original name of this property.'''

        return self.wrapped.IsProgressTreeCellExpanded

    @is_progress_tree_cell_expanded.setter
    def is_progress_tree_cell_expanded(self, value: 'bool'):
        self.wrapped.IsProgressTreeCellExpanded = bool(value) if value else False

    @property
    def parent(self) -> 'TaskProgress':
        '''TaskProgress: 'Parent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(TaskProgress)(self.wrapped.Parent) if self.wrapped.Parent is not None else None

    @classproperty
    def null_task_progress(cls) -> 'TaskProgress':
        '''TaskProgress: 'NullTaskProgress' is the original name of this property.'''

        return constructor.new(TaskProgress)(TaskProgress.TYPE.NullTaskProgress) if TaskProgress.TYPE.NullTaskProgress is not None else None

    @null_task_progress.setter
    def null_task_progress(cls, value: 'TaskProgress'):
        value = value.wrapped if value else None
        TaskProgress.TYPE.NullTaskProgress = value

    @property
    def child_tasks(self) -> 'List[TaskProgress]':
        '''List[TaskProgress]: 'ChildTasks' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ChildTasks, constructor.new(TaskProgress))
        return value

    @property
    def is_aborting(self) -> 'bool':
        '''bool: 'IsAborting' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IsAborting

    @property
    def additional_status_string(self) -> 'str':
        '''str: 'AdditionalStatusString' is the original name of this property.'''

        return self.wrapped.AdditionalStatusString

    @additional_status_string.setter
    def additional_status_string(self, value: 'str'):
        self.wrapped.AdditionalStatusString = str(value) if value else ''

    def add_progress_status_updated(self, value: 'Callable[[str], None]'):
        ''' 'add_ProgressStatusUpdated' is the original name of this method.

        Args:
            value (Callable[[str], None])
        '''

        self.wrapped.add_ProgressStatusUpdated(value)

    def remove_progress_status_updated(self, value: 'Callable[[str], None]'):
        ''' 'remove_ProgressStatusUpdated' is the original name of this method.

        Args:
            value (Callable[[str], None])
        '''

        self.wrapped.remove_ProgressStatusUpdated(value)

    def add_progress_incremented(self, value: 'Callable[[float], None]'):
        ''' 'add_ProgressIncremented' is the original name of this method.

        Args:
            value (Callable[[float], None])
        '''

        self.wrapped.add_ProgressIncremented(value)

    def remove_progress_incremented(self, value: 'Callable[[float], None]'):
        ''' 'remove_ProgressIncremented' is the original name of this method.

        Args:
            value (Callable[[float], None])
        '''

        self.wrapped.remove_ProgressIncremented(value)

    def abort(self):
        ''' 'Abort' is the original name of this method.'''

        self.wrapped.Abort()

    def continue_with_progress(self, status_update: 'str', perform_analysis: 'Callable[[TaskProgress], None]') -> 'TaskProgress':
        ''' 'ContinueWith' is the original name of this method.

        Args:
            status_update (str)
            perform_analysis (Callable[[mastapy.TaskProgress], None])

        Returns:
            mastapy.TaskProgress
        '''

        status_update = str(status_update)
        method_result = self.wrapped.ContinueWith.Overloads[_STRING, _ACTION[_TASK_PROGRESS]](status_update if status_update else '', perform_analysis)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def continue_with(self, status_update: 'str', perform_analysis: 'Callable[..., None]') -> 'TaskProgress':
        ''' 'ContinueWith' is the original name of this method.

        Args:
            status_update (str)
            perform_analysis (Callable[..., None])

        Returns:
            mastapy.TaskProgress
        '''

        status_update = str(status_update)
        method_result = self.wrapped.ContinueWith.Overloads[_STRING, _ACTION](status_update if status_update else '', perform_analysis)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def get_all_errors(self) -> 'Iterable[str]':
        ''' 'GetAllErrors' is the original name of this method.

        Returns:
            Iterable[str]
        '''

        return conversion.pn_to_mp_objects_in_iterable(self.wrapped.GetAllErrors(), str)

    def set_current_completion(self, fraction_done: 'float'):
        ''' 'SetCurrentCompletion' is the original name of this method.

        Args:
            fraction_done (float)
        '''

        fraction_done = float(fraction_done)
        self.wrapped.SetCurrentCompletion(fraction_done if fraction_done else 0.0)

    def increment_progress(self, inc: Optional['int'] = 1):
        ''' 'IncrementProgress' is the original name of this method.

        Args:
            inc (int, optional)
        '''

        inc = int(inc)
        self.wrapped.IncrementProgress(inc if inc else 0)

    def add_task(self):
        ''' 'AddTask' is the original name of this method.'''

        self.wrapped.AddTask()

    def update_status(self, new_status: 'str'):
        ''' 'UpdateStatus' is the original name of this method.

        Args:
            new_status (str)
        '''

        new_status = str(new_status)
        self.wrapped.UpdateStatus(new_status if new_status else '')

    def update_status_with_increment(self, new_status: 'str'):
        ''' 'UpdateStatusWithIncrement' is the original name of this method.

        Args:
            new_status (str)
        '''

        new_status = str(new_status)
        self.wrapped.UpdateStatusWithIncrement(new_status if new_status else '')

    def add_error(self, error: 'str'):
        ''' 'AddError' is the original name of this method.

        Args:
            error (str)
        '''

        error = str(error)
        self.wrapped.AddError(error if error else '')

    def complete(self):
        ''' 'Complete' is the original name of this method.'''

        self.wrapped.Complete()

    def create_new_task(self, title: 'str', total_items: 'int', show_progress: Optional['bool'] = True, show_eta: Optional['bool'] = False, manual_increment: Optional['bool'] = False) -> 'TaskProgress':
        ''' 'CreateNewTask' is the original name of this method.

        Args:
            title (str)
            total_items (int)
            show_progress (bool, optional)
            show_eta (bool, optional)
            manual_increment (bool, optional)

        Returns:
            mastapy.TaskProgress
        '''

        title = str(title)
        total_items = int(total_items)
        show_progress = bool(show_progress)
        show_eta = bool(show_eta)
        manual_increment = bool(manual_increment)
        method_result = self.wrapped.CreateNewTask(title if title else '', total_items if total_items else 0, show_progress if show_progress else False, show_eta if show_eta else False, manual_increment if manual_increment else False)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def dispose(self):
        ''' 'Dispose' is the original name of this method.'''

        self.wrapped.Dispose()

    def to_string(self) -> 'str':
        ''' 'ToString' is the original name of this method.

        Returns:
            str
        '''

        method_result = self.wrapped.ToString()
        return method_result

    def initialize_lifetime_service(self) -> 'object':
        ''' 'InitializeLifetimeService' is the original name of this method.

        Returns:
            object
        '''

        method_result = self.wrapped.InitializeLifetimeService()
        return method_result

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.dispose()
