
import threading
import uuid

from concurrent.futures import ThreadPoolExecutor

from rox.core.consts import property_type
from rox.core.core import Core
from rox.core.custom_properties.custom_property import CustomProperty
from rox.core.custom_properties.custom_property_type import CustomPropertyType
from rox.core.custom_properties.device_property import DeviceProperty
from rox.core.logging.logging import Logging
from rox.server.client.sdk_settings import SdkSettings
from rox.server.client.server_properties import ServerProperties
from rox.server.flags.server_entities_provider import ServerEntitiesProvider
from rox.server.rox_options import RoxOptions
from rox.server.rox_state import RoxState

class Rox:
    core = Core()
    executor = ThreadPoolExecutor(1)
    startupShutdownLock = threading.Lock()
    State = RoxState.Idle

    @staticmethod
    def _reset():
        Rox.State = RoxState.ShuttingDown

        Rox.core.shutdown()
        Rox.core = Core()

        Rox.State = RoxState.Idle

    @staticmethod
    def shutdown():
        with Rox.startupShutdownLock:
            if Rox.State is not RoxState.Set and Rox.State is not RoxState.Corrupted:
                Logging.get_logger().warn('Rox can only be shutdown when it is already Set up, skipping Shutdown')
                return
            else:
                Rox._reset()

    @staticmethod
    def setup(api_key, rox_options=None):
        with Rox.startupShutdownLock:
            if Rox.State is not RoxState.Idle and Rox.State is not RoxState.Corrupted:
                Logging.get_logger().warn('Rox was already initialized, skipping setup')
                return

            if Rox.State is RoxState.Corrupted:
                Rox._reset()

            if Rox.State is RoxState.Idle:
                Rox.State = RoxState.SettingUp
                try:
                    if rox_options is None:
                        rox_options = RoxOptions()

                    sdk_settings = SdkSettings(api_key, rox_options.dev_mode_key)
                    server_properties = ServerProperties(sdk_settings, rox_options)

                    props = server_properties.get_all_properties()
                    Rox.core.add_custom_property_if_not_exists(DeviceProperty(property_type.PLATFORM.name, CustomPropertyType.STRING, props[property_type.PLATFORM.name]))
                    Rox.core.add_custom_property_if_not_exists(DeviceProperty(property_type.APP_RELEASE.name, CustomPropertyType.SEMVER, props[property_type.APP_RELEASE.name]))
                    Rox.core.add_custom_property_if_not_exists(DeviceProperty(property_type.DISTINCT_ID.name, CustomPropertyType.STRING, lambda c: str(uuid.uuid4())))
                    Rox.core.add_custom_property_if_not_exists(DeviceProperty('internal.realPlatform', CustomPropertyType.STRING, props[property_type.PLATFORM.name]))
                    Rox.core.add_custom_property_if_not_exists(DeviceProperty('internal.customPlatform', CustomPropertyType.STRING, props[property_type.PLATFORM.name]))
                    Rox.core.add_custom_property_if_not_exists(DeviceProperty('internal.appKey', CustomPropertyType.STRING, server_properties.rollout_key))
                    Rox.core.add_custom_property_if_not_exists(DeviceProperty('internal.'+property_type.LIB_VERSION.name , CustomPropertyType.SEMVER, props[property_type.LIB_VERSION.name]))
                    Rox.core.add_custom_property_if_not_exists(DeviceProperty('internal.'+property_type.API_VERSION.name , CustomPropertyType.SEMVER, props[property_type.API_VERSION.name]))
                    Rox.core.add_custom_property_if_not_exists(DeviceProperty('internal.'+property_type.DISTINCT_ID.name, CustomPropertyType.STRING, lambda c: str(uuid.uuid4())))

                    def setup_callback(task):
                        try:
                            task.result()
                        except Exception as ex:
                            Logging.get_logger().error('Failed in Rox.setup', ex)
                            raise

                    setup_task = Rox.core.setup(sdk_settings, server_properties)
                    setup_task.add_done_callback(setup_callback)
                    Rox.State = RoxState.Set
                    return setup_task
                except Exception as ex:
                    Rox.State = RoxState.Corrupted
                    Logging.get_logger().error('Failed in Rox.setup', ex)
                    raise

    @staticmethod
    def register(arg1, *argv):
        if len(argv) > 1:
            raise Exception('There should be no more than 2 arguments passed in')
        elif len(argv) == 1:
            # Both namespace and container has been provided in the args
            Rox.core.register(arg1, argv[0])
        else:
            # Only the container has been provided
            Rox.core.register('', arg1)

    @staticmethod
    def set_userspace_unhandled_error_handler(user_unhandled_error_invoker):
        Rox.core.set_userspace_unhandled_error_handler(user_unhandled_error_invoker)

    @staticmethod
    def set_context(context):
        Rox.core.set_context(context)

    @staticmethod
    def fetch():
        def fetch():
            try:
                Rox.core.fetch()
            except Exception as ex:
                Logging.get_logger().error('Failed in Rox.fetch', ex)

        return Rox.executor.submit(fetch)

    @staticmethod
    def set_custom_string_property(name, value):
        Rox.core.add_custom_property(CustomProperty(name, CustomPropertyType.STRING, value))

    @staticmethod
    def set_custom_boolean_property(name, value):
        Rox.core.add_custom_property(CustomProperty(name, CustomPropertyType.BOOL, value))

    @staticmethod
    def set_custom_int_property(name, value):
        Rox.core.add_custom_property(CustomProperty(name, CustomPropertyType.INT, value))

    @staticmethod
    def set_custom_float_property(name, value):
        Rox.core.add_custom_property(CustomProperty(name, CustomPropertyType.FLOAT, value))

    @staticmethod
    def set_custom_semver_property(name, value):
        Rox.core.add_custom_property(CustomProperty(name, CustomPropertyType.SEMVER, value))

    @staticmethod
    def dynamic_api():
        return Rox.core.dynamic_api(ServerEntitiesProvider())
