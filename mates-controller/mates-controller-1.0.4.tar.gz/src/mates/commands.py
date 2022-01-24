class MatesCommand():
    """
    An enumerated class to represent possible commands to send to devices over a serial port.

    Attributes
    ----------
    MATES_CMD_SET_PAGE: int
        - commmand sent by controller to set current page.

    MATES_CMD_GET_PAGE: int
        - commmand sent by controller to get index of current page.

    MATES_CMD_SET_WIDGET_VALUE: int
        - commmand sent by controller to set value of a widget.

    MATES_CMD_GET_WIDGET_VALUE: int
        - commmand sent by controller to get the value of a widget.

    MATES_CMD_SET_WIDGET_PARAM: int
        - commmand sent by controller to set the value of a parameter associated with a widget.

    MATES_CMD_GET_WIDGET_PARAM: int
        - commmand sent by controller to get the value of a parameter associated with a widget.

    MATES_CMD_SET_BACKLIGHT: int
        - commmand sent by controller to set the intensity of device backlight.

    MATES_CMD_CLR_PRINT_AREA: int
        - commmand sent by controller to clear Print Area widgets.

    MATES_CMD_SET_PRINT_COLOR: int
        - commmand sent by controller to set the colour of Print Area widgets.

    MATES_CMD_SYSTEM_RESET: int
        - commmand sent by controller to request a soft system reset.

    MATES_CMD_PIN_MODE: int
        - commmand sent by controller to designate available pins as input or output.

    MATES_CMD_DIGITAL_WRITE: int
        - commmand sent by controller to control an IO pin set as output.

    MATES_CMD_DIGITAL_READ: int
        - commmand sent by controller to read a specified pin set as input.

    MATES_CMD_BTN_EVENT_COUNT: int
        - commmand sent by controller to query the number of button events recorded.

    MATES_CMD_NEXT_BTN_EVENT: int
        - commmand sent by controller to query the next button recorded.
    
    MATES_CMD_SWP_EVENT_COUNT: int
        - commmand sent by controller to query the number of swipe events recorded.

    MATES_CMD_NEXT_SWP_EVENT: int
        - commmand sent by controller to query the next swipe recorded.

    MATES_CMD_UPDATE_TEXT_AREA: int
        - commmand sent by controller to update the contents of a Text Area widget.

    MATES_CMD_APPEND_PRINT_AREA: int
        - commmand sent by controller to append data to a Print Area widget.

    MATES_CMD_PRINT_STRING: int
        - commmand sent by controller to print a string.

    MATES_CMD_SET_WIDGET_32VAL: int
        - commmand sent by controller to change the 32 bit value of compatible widgets.

    MATES_CMD_APPEND_SCOPE_DATA: int
        - commmand sent by controller to append data to a Scope widget.

    MATES_CMD_UPDATE_DOT_MATRIX: int
        - commmand sent by controller to update data displayed by a Dot Matrix widget.
    """

    MATES_CMD_SET_PAGE = 0x0000
    MATES_CMD_GET_PAGE = 0x0001
    MATES_CMD_SET_WIDGET_VALUE = 0x0002
    MATES_CMD_GET_WIDGET_VALUE = 0x0003
    MATES_CMD_SET_WIDGET_PARAM = 0x0004
    MATES_CMD_GET_WIDGET_PARAM = 0x0005
    MATES_CMD_SET_BACKLIGHT = 0x0006
    MATES_CMD_CLR_PRINT_AREA = 0x0007
    MATES_CMD_SET_PRINT_COLOR = 0x0008
    MATES_CMD_SYSTEM_RESET = 0x0009
    MATES_CMD_PIN_MODE = 0x000A
    MATES_CMD_DIGITAL_WRITE = 0x000B
    MATES_CMD_DIGITAL_READ = 0x000C
    MATES_CMD_BTN_EVENT_COUNT = 0x000D
    MATES_CMD_NEXT_BTN_EVENT = 0x000E
    MATES_CMD_SWP_EVENT_COUNT = 0x000F
    MATES_CMD_NEXT_SWP_EVENT = 0x0010
    MATES_CMD_UPDATE_TEXT_AREA = 0xFFFF
    MATES_CMD_APPEND_PRINT_AREA = 0xFFFE
    # MATES_CMD_PRINT_STRING = 0xFFFD # not being utilized, might be replaced in the future
    MATES_CMD_SET_WIDGET_32VAL = 0xFFFC
    MATES_CMD_APPEND_SCOPE_DATA = 0xFFFB
    MATES_CMD_UPDATE_DOT_MATRIX = 0xFFFA