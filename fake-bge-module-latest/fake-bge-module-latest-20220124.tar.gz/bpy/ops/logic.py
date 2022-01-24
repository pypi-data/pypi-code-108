import sys
import typing
import bpy.types


def actuator_add(type: typing.Union[str, int] = '',
                 name: str = "",
                 object: str = ""):
    ''' Add an actuator to the active object

    :param type: Type, Type of actuator to add
    :type type: typing.Union[str, int]
    :param name: Name, Name of the Actuator to add
    :type name: str
    :param object: Object, Name of the Object to add the Actuator to
    :type object: str
    '''

    pass


def actuator_move(actuator: str = "",
                  object: str = "",
                  direction: typing.Union[str, int] = 'UP'):
    ''' Move Actuator

    :param actuator: Actuator, Name of the actuator to edit
    :type actuator: str
    :param object: Object, Name of the object the actuator belongs to
    :type object: str
    :param direction: Direction, Move Up or Down
    :type direction: typing.Union[str, int]
    '''

    pass


def actuator_remove(actuator: str = "", object: str = ""):
    ''' Remove an actuator from the active object

    :param actuator: Actuator, Name of the actuator to edit
    :type actuator: str
    :param object: Object, Name of the object the actuator belongs to
    :type object: str
    '''

    pass


def controller_add(type: typing.Union[str, int] = 'LOGIC_AND',
                   name: str = "",
                   object: str = ""):
    ''' Add a controller to the active object

    :param type: Type, Type of controller to add * LOGIC_AND And -- Logic And. * LOGIC_OR Or -- Logic Or. * LOGIC_NAND Nand -- Logic Nand. * LOGIC_NOR Nor -- Logic Nor. * LOGIC_XOR Xor -- Logic Xor. * LOGIC_XNOR Xnor -- Logic Xnor. * EXPRESSION Expression. * PYTHON Python.
    :type type: typing.Union[str, int]
    :param name: Name, Name of the Controller to add
    :type name: str
    :param object: Object, Name of the Object to add the Controller to
    :type object: str
    '''

    pass


def controller_move(controller: str = "",
                    object: str = "",
                    direction: typing.Union[str, int] = 'UP'):
    ''' Move Controller

    :param controller: Controller, Name of the controller to edit
    :type controller: str
    :param object: Object, Name of the object the controller belongs to
    :type object: str
    :param direction: Direction, Move Up or Down
    :type direction: typing.Union[str, int]
    '''

    pass


def controller_remove(controller: str = "", object: str = ""):
    ''' Remove a controller from the active object

    :param controller: Controller, Name of the controller to edit
    :type controller: str
    :param object: Object, Name of the object the controller belongs to
    :type object: str
    '''

    pass


def custom_object_create(class_name: str = "module.MyObject"):
    ''' Create a KX_GameObject subclass and attach it to the selected object

    :param class_name: MyObject, The class name with module (module.ClassName)
    :type class_name: str
    '''

    pass


def custom_object_register(class_name: str = "module.MyObject"):
    ''' Use a custom KX_GameObject subclass for the selected object

    :param class_name: MyObject, The class name with module (module.ClassName)
    :type class_name: str
    '''

    pass


def custom_object_reload():
    ''' Reload custom object from the source script

    '''

    pass


def custom_object_remove():
    ''' Remove this custom class from the object

    '''

    pass


def links_cut(path: typing.Union[
        typing.Dict[str, 'bpy.types.OperatorMousePath'], typing.
        List['bpy.types.OperatorMousePath'], 'bpy_prop_collection'] = None,
              cursor: int = 12):
    ''' Remove logic brick connections

    :param path: Path
    :type path: typing.Union[typing.Dict[str, 'bpy.types.OperatorMousePath'], typing.List['bpy.types.OperatorMousePath'], 'bpy_prop_collection']
    :param cursor: Cursor
    :type cursor: int
    '''

    pass


def properties():
    ''' Toggle the properties region visibility

    '''

    pass


def python_component_create(component_name: str = "module.Component"):
    ''' Create a Python component to the selected object

    :param component_name: Component, The component class name with module (module.ComponentName)
    :type component_name: str
    '''

    pass


def python_component_move_down(index: int = 0):
    ''' Move this component down in the list

    :param index: Index, Component index to move
    :type index: int
    '''

    pass


def python_component_move_up(index: int = 0):
    ''' Move this component up in the list

    :param index: Index, Component index to move
    :type index: int
    '''

    pass


def python_component_register(component_name: str = "module.Component"):
    ''' Add a Python component to the selected object

    :param component_name: Component, The component class name with module (module.ComponentName)
    :type component_name: str
    '''

    pass


def python_component_reload(index: int = 0):
    ''' Reload component from the source script

    :param index: Index, Component index to reload
    :type index: int
    '''

    pass


def python_component_remove(index: int = 0):
    ''' Remove this component from the object

    :param index: Index, Component index to remove
    :type index: int
    '''

    pass


def region_flip():
    ''' Toggle the properties region's alignment (left/right)

    '''

    pass


def sensor_add(type: typing.Union[str, int] = '',
               name: str = "",
               object: str = ""):
    ''' Add a sensor to the active object

    :param type: Type, Type of sensor to add
    :type type: typing.Union[str, int]
    :param name: Name, Name of the Sensor to add
    :type name: str
    :param object: Object, Name of the Object to add the Sensor to
    :type object: str
    '''

    pass


def sensor_move(sensor: str = "",
                object: str = "",
                direction: typing.Union[str, int] = 'UP'):
    ''' Move Sensor

    :param sensor: Sensor, Name of the sensor to edit
    :type sensor: str
    :param object: Object, Name of the object the sensor belongs to
    :type object: str
    :param direction: Direction, Move Up or Down
    :type direction: typing.Union[str, int]
    '''

    pass


def sensor_remove(sensor: str = "", object: str = ""):
    ''' Remove a sensor from the active object

    :param sensor: Sensor, Name of the sensor to edit
    :type sensor: str
    :param object: Object, Name of the object the sensor belongs to
    :type object: str
    '''

    pass


def view_all():
    ''' Resize view so you can see all logic bricks

    '''

    pass
