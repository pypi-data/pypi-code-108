'''_1390.py

PushbulletSettings
'''


from mastapy._internal import constructor
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.utility import _1387
from mastapy._internal.python_net import python_net_import

_PUSHBULLET_SETTINGS = python_net_import('SMT.MastaAPI.Utility', 'PushbulletSettings')


__docformat__ = 'restructuredtext en'
__all__ = ('PushbulletSettings',)


class PushbulletSettings(_1387.PerMachineSettings):
    '''PushbulletSettings

    This is a mastapy class.
    '''

    TYPE = _PUSHBULLET_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PushbulletSettings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def enable_pushbullet(self) -> 'bool':
        '''bool: 'EnablePushbullet' is the original name of this property.'''

        return self.wrapped.EnablePushbullet

    @enable_pushbullet.setter
    def enable_pushbullet(self, value: 'bool'):
        self.wrapped.EnablePushbullet = bool(value) if value else False

    @property
    def pushbullet_token(self) -> 'str':
        '''str: 'PushbulletToken' is the original name of this property.'''

        return self.wrapped.PushbulletToken

    @pushbullet_token.setter
    def pushbullet_token(self, value: 'str'):
        self.wrapped.PushbulletToken = str(value) if value else ''

    @property
    def send_progress_screenshot_interval_minutes(self) -> 'overridable.Overridable_int':
        '''overridable.Overridable_int: 'SendProgressScreenshotIntervalMinutes' is the original name of this property.'''

        return constructor.new(overridable.Overridable_int)(self.wrapped.SendProgressScreenshotIntervalMinutes) if self.wrapped.SendProgressScreenshotIntervalMinutes is not None else None

    @send_progress_screenshot_interval_minutes.setter
    def send_progress_screenshot_interval_minutes(self, value: 'overridable.Overridable_int.implicit_type()'):
        wrapper_type = overridable.Overridable_int.wrapper_type()
        enclosed_type = overridable.Overridable_int.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0, is_overridden)
        self.wrapped.SendProgressScreenshotIntervalMinutes = value

    def generate_pushbullet_token(self):
        ''' 'GeneratePushbulletToken' is the original name of this method.'''

        self.wrapped.GeneratePushbulletToken()
