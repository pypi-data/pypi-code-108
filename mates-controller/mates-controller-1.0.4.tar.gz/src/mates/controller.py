"""
A module used for communicating with BBM Devices, over serial port.

Module contains various methods for sending and retrieving data
relating to display widgets, their states and parameters and
the health of the controller
"""
import ctypes
import sys
import struct
import time
import typing
import io
import serial
# import gpiozero

from mates.data import *
from mates.constants import *
from mates.commands import MatesCommand

class MatesController:
    """
    A class representing the Python Mates Serial controller.

    Attributes
    ----------
    serial_port: serial.Serial
        - pyserial serial port abstraction, used for reading
        and writing data over a serial connection.

    debug: io.TextIOWrapper
        - Text file object to write debugging code to, supply of none
        will result in no debugging. Examples include sys.stdout, open('log.txt', 'r+')

    mates_error: MatesError
        - error status of the Python Mates Serial controller.

    mates_reset_fnc: int
        - function used to perform a hard reset.
    """

    MATES_STUDIO_COMPATIBILITY_VERSION = "1.0.8"
    MATES_CONTROLLER_LIBRARY_VERSION = "1.0.4"

    def __init__(self, portName: str, resetFunction=None, debugStream: io.TextIOWrapper=None, debugFileLength: int=50):
        """
        Constructs all the necessary attributes associated with an instance
        of a Mates Controller Object.

        Args:

            portName: str
                - the name of the port to be opened. Example: /dev/ttyUSB0 for linux.

            resetFunction:
                - function used to perform a hard reset.

            debugStream: io.TextIOWrapper
                - Text file object to write debugging code to, supply of none
                will result in no debugging. Examples include sys.stdout, open('log.txt', 'r+')

            debugFileLength: int
                - Determines the extent of debug history kept with respect to lines in a file,
                given a circular log. O indicates full history kept with no circular logging.
                Users must be careful here to manage storage space effectively.
        """

        self.mates_reset_fnc = resetFunction
        self.debug = self.__MatesDebug(log_length=debugFileLength, file_stream=debugStream)

        # Create serial object
        self.serial_port = serial.Serial()
        
        # Configure serial object
        self.serial_port.port = portName
        self.serial_port.bytesize = serial.EIGHTBITS
        self.serial_port.parity = serial.PARITY_NONE
        self.serial_port.stopbits = serial.STOPBITS_ONE
        self.serial_port.timeout = MATES_RESPONSE_TIMEOUT / 1000
        self.serial_port.xonxoff = False
        self.serial_port.rtscts = False
        self.serial_port.dsrdtr = False
        self.serial_port.write_timeout = None
        self.serial_port.inter_byte_timeout = None

        self.mates_error = MatesError.MATES_ERROR_NONE
        self.mates_buffer_size = MATES_STRING_BUFFER_SIZE

    def __del__(self):
        """
        Handles safe destruction of Mates Controller object.
        notably closes the opened serial port to prevent
        erroneous states.

        Args:

            void.

        Returns:

            void.
        """
        self.serial_port.close()
        self.debug.close_file()

    def begin(self, baudrate: int = 9600):
        """
        Begins the serial connection with the specified baudrate

        Args:

            baudrate: int
                - the baudrate of the serial port.


        Returns:

            void.
        """

        self.debug.publish_string("Initializing Serial port {} @ {} baud".format(self.serial_port.port, baudrate), termination='\n')
        self.serial_port.baudrate = baudrate
        self.serial_port.open()
        self.reset()

    def close(self):
        """
        Closes opened serial port.

        Args:

            void.

        Returns:

            void.
        """
        self.debug.publish_string("Closing {} port".format(self.serial_port.port), termination='\n')
        self.serial_port.close()

    def reset(self, waitPeriod: int=MATES_BOOT_TIMEOUT) -> bool:
        """
        Uses hardware driven signal to hard reset companion device.

        Args:

            wait_period: int
                - determines how long to wait (milliseconds) before checking for connection.
                Value must be within the uint16 datatype range.

        Returns:

            boolean response of reset.
        """

        self.debug.publish_string("Resetting module ...")

        if (self.mates_reset_fnc == None):
            self.debug.publish_string("Can't perform hardware reset. No reset function provided ...")
            return False
        else:
            self.mates_reset_fnc()

        start_time = time.time()

        resp = self.__wait_for_ack(timeout=waitPeriod)

        if resp:
            self.debug.publish_string("Done after {} ms".format((time.time() - start_time) / 1000), termination='\n')
        else:
            self.debug.publish_string("Timed out after {} ms".format((time.time() - start_time) / 1000), termination='\n')

        return resp

    def softReset(self, waitPeriod: int=MATES_BOOT_TIMEOUT) -> bool:
        """
        Sends a serial command to the connected device to trigger a reset.

        Args:

            waitPeriod: int
                - determines how long (milliseconds) to wait before timing out after
                no acknowledgement. Value must be within the uint16 datatype range.

        Returns:

            boolean response of reset.
        """
        self.debug.publish_string("Resetting module using command ...")

        self.__write_command(MatesCommand.MATES_CMD_SYSTEM_RESET)

        start_time = time.time()

        resp = self.__wait_for_ack(waitPeriod)

        if resp:
            self.debug.publish_string("Done after {} ms".format((time.time() - start_time) / 1000), termination='\n')
        else:
            self.debug.publish_string("Timed out after {} ms".format((time.time() - start_time) / 1000), termination='\n')
        return resp

    def setBacklight(self, backlightValue: int) -> bool:
        """
        Sets the intensity of the backlight of connected device.

        Args:

            backlightValue: int
                - intensity of backlight. Value must be within the uint8 datatype range.

        Returns:

            boolean response indicating command success or failure.
        """
        self.debug.publish_string("Setting backlight to {} ...".format(backlightValue))

        self.__check_argument_value('backlightValue', backlightValue, UINT8)
        self.__write_command(MatesCommand.MATES_CMD_SET_BACKLIGHT)
        self.__write_int16(backlightValue)

        resp = self.__wait_for_ack()

        self.debug.end_operation()

        return resp

    def setPage(self, pageIndex: int) -> bool:
        """
        Sets the page to be displayed on the connected device.

        Args:

            pageIndex: int
                - index of page to set as current. Value must be within the uint16 datatype range.

        Returns:

            boolean response indicating command success or failure.
        """
        self.debug.publish_string("Navigating to page {} ...".format(pageIndex))

        self.__check_argument_value('pageIndex', pageIndex,UINT16)
        self.__write_command(MatesCommand.MATES_CMD_SET_PAGE)
        self.__write_int16(pageIndex)

        resp = self.__wait_for_ack()

        self.debug.end_operation()

        return resp

    def getPage(self) -> int:
        """
        Returns the index of the current page displayed by the connected device.

        Args:

            void.

        Returns:

            integer corresponding to current page index.
        """
        self.debug.publish_string("Querying active page ....")

        self.__write_command(MatesCommand.MATES_CMD_GET_PAGE)

        return self.__read_response()

    def setWidgetValueById(self, widgetId: int, value: int) -> bool:
        """
        Sets the value of a specific widget based on the provided identifier.

        Args:

            widgetId: int
                - the unique id of the desired widget.
                Value must exist within the int16 datatype range.

            value: int
                - the value the corresponding widget will be set to.
                Value must exist within the int16 datatype range.

        Returns:

            boolean response indicating command success or failure.
        """
        self.__check_argument_value('widgetId', widgetId, INT16)
        self.__check_argument_value('value', value, INT16)

        self.debug.publish_string("Setting widget ({}) value to {} ...".format(hex(widgetId), value))

        self.__write_command(MatesCommand.MATES_CMD_SET_WIDGET_VALUE)
        self.__write_int16(widgetId)
        self.__write_int16(value)

        resp = self.__wait_for_ack()

        self.debug.end_operation()

        return resp

    def getWidgetValueById(self, widgetId: int) -> int:
        """
        Gets the value of a specific widget based on the provided identifier.

        Args:
            widgetId: int

                the unique id of the target widget.
                Value must be within the uint16 datatype range.

        Returns:

            integer corresponding to widget value.
        """
        self.__check_argument_value('widgetId', widgetId, INT16)

        self.debug.publish_string("Query widget ({}) value ...".format(hex(widgetId)))

        self.__write_command(MatesCommand.MATES_CMD_GET_WIDGET_VALUE)
        self.__write_int16(widgetId)

        return self.__read_response()

    def setWidgetValueByIndex(self, widgetType: MatesWidget, widgetIndex: int, value: int) -> bool:
        """
        Sets the value of a specific widget based on the index within a widget type.

        Args:

            widgetType: MatesWidget
                - the unique type of widget to be changed.

            widgetIndex: int
                - the index of the widget, of a specific type.
                Value must be within the uint8 datatype range.

            value: int
                - the value the corresponding widget will be set to.
                Value must be within the int16 datatype range.

        Returns:

            boolean response indicating command success or failure.
        """
        return self.setWidgetValueById(self.__getWidgetId(widgetType, widgetIndex), value)

    def getWidgetValueByIndex(self, widgetType: MatesWidget, widgetIndex: int) -> int:
        """
        Gets the value of a specific widget based on the index within a widget type.

        Args:

            widgetType: MatesWidget
                - the unique type of widget to be changed.

            widgetIndex: int
                - the index of the widget, of a specific type.
                Value must be within the uint8 datatype range.

        Returns:

            integer corresponding to widget value.
        """
        return self.getWidgetValueById(self.__getWidgetId(widgetType, widgetIndex))

    def setLedDigitsShortValue(self, widgetIndex: int, value: int):
        """
        Sets the value of specifically int16 LED Digits widgets based on the widget index.

        Args:

            widgetIndex: int
                - the index of the LED Digits widget. Value must be within uint8 datatype range.

            value: int, float
                - the value the corresponding widget will be set to.
                Values must be within the int16 datatype range.

        Returns:

            boolean response indicating command success or failure.
        """
        return self.setWidgetValueByIndex(MatesWidget.MATES_LED_DIGITS, widgetIndex, value)

    def setLedDigitsLongValue(self, widgetIndex: int, value: int):
        """
        Sets the value of specifically int32 LED Digits widgets based on the widget index.

        Args:

            widgetIndex: int
                - the index of the LED Digits widget. Value must be within uint8 datatype range.

            value: int, float
                - the value the corresponding widget will be set to.
                Values must be within the int32 datatype range.

        Returns:

            boolean response indicating command success or failure.
        """
        self.__check_argument_value('value', value, INT32)
        return self.__set_widget_value_32bit(self.__getWidgetId(MatesWidget.MATES_LED_DIGITS, widgetIndex), value)

    def setLedDigitsFloatValue(self, widgetIndex: int, value: float):
        """
        Sets the value of specifically float32 LED Digits widgets based on the widget index.

        Args:

            widgetIndex: int
                - the index of the LED Digits widget. Value must be within uint8 datatype range.

            value: int, float
                - the value the corresponding widget will be set to.
                Values must be within the float32 datatype range.

        Returns:

            boolean response indicating command success or failure.
        """
        self.__check_argument_value('value', value, FLOAT32)
        return self.__set_widget_value_32bit(self.__getWidgetId(MatesWidget.MATES_LED_DIGITS, widgetIndex), value)

    def setSpectrumValue(self, spectrumId: int, gaugeIndex: int, value: int) -> bool:
        """
        Sets the value of specifically Spectrum widgets based the spectrum id and gauge index.

        Args:

            spectrumId: int
                - the id of the relevant Spectrum widget.
                Value must be within the int16 datatype range.

            gaugeIndex: int
                - the gauge index within the target Spectrum widget.
                Value must be within the uint8 datatype range.

            value: int
                - the value the corresponding widget will be set to.
                Value must be within the uint8 datatype range.

        Returns:

            boolean response indicating command success or failure.
        """
        self.__check_argument_value('spectrumId', spectrumId, INT16)
        self.__check_argument_value('gaugeIndex', gaugeIndex, UINT8)
        self.__check_argument_value('value', value, UINT8)
        return self.setWidgetValueById(spectrumId, (gaugeIndex << 8)|value)

    def setLedSpectrumValue(self, ledSpectrumIndex: int, gaugeIndex: int, value) -> bool:
        """
        Sets the value of specifically LED Spectrum widgets based on the gauge index.

        Args:

            ledSpectrumIndex: int
                - the index of the desired LED Spectrum widget.
                Value must be within the uint8 datatype range.

            gaugeIndex: int
                - the gauge index within the target LED Spectrum widget.
                Value must be within the uint8 datatype range.

            value: int
                - the value the corresponding widget will be set to.
                Value must be within the uint8 datatype range.

        Returns:

            boolean response indicating command success or failure.
        """
        self.__check_argument_value('gaugeIndex', gaugeIndex, UINT8)
        self.__check_argument_value('value', value, UINT8)
        return self.setWidgetValueById(self.__getWidgetId(MatesWidget.MATES_LED_SPECTRUM, ledSpectrumIndex), (gaugeIndex<<8)|value)

    def setMediaSpectrumValue(self, mediaIndex: int, gaugeIndex: int, value: int) -> bool:
        """
        Sets the value of specifically Media Spectrum widgets
        based on the Media Spectrum index and the gauge index.

        Args:

            mediaIndex: int
                - the index of the Media Spectrum widget.
                Value must be within the uint8 datatype range.

            gaugeIndex: int
                - the index of the desired gauge.
                Value must be within the uint8 datatype range.

            value: int
                - the value the corresponding widget will be set to.
                Value must be within the uint8 datatype range.

        Returns:

            boolean response indicating command success or failure.
        """
        self.__check_argument_value('gaugeIndex', gaugeIndex, UINT8)
        self.__check_argument_value('value', value, UINT8)
        return self.setWidgetValueById(self.__getWidgetId(MatesWidget.MATES_MEDIA_SPECTRUM, mediaIndex), (gaugeIndex<<8)|value)

    def setWidgetParamById(self, widgetId: int, param: int, value: int) -> bool:
        """
        Sets the value of a widget parameter based on widget id and parameter id.

        Args:

            widgetId: int
                - the unique id of the target widget.
                Value must be within the int16 datatype range.

            param: int
                - the unique id of the target parameter.
                Value must be within the int16 datatype range.

            value: int
                - the value the corresponding parameter will be set to.
                Value must be within the int16 datatype range.

        Returns:

            boolean response indicating command success or failure.
        """
        self.__check_argument_value('widgetId', widgetId, INT16)
        self.__check_argument_value('param', param, INT16)
        self.__check_argument_value('value', value, INT16)

        self.debug.publish_string("Set widget ({}) parameter ({}) to {} ..."
            .format(hex(widgetId), hex(param), value))

        self.__write_command(MatesCommand.MATES_CMD_SET_WIDGET_PARAM)
        self.__write_int16(widgetId)
        self.__write_int16(param)
        self.__write_int16(value)

        resp = self.__wait_for_ack()

        self.debug.end_operation()

        return resp

    def getWidgetParamById(self, widgetId: int, param: int) -> int:
        """
        Gets the value of a widget parameter based on widget id and parameter id.

        Args:

            widgetId: int
                - the unique id of the target widget.
                Value must be within the int16 datatype range.

            param: int
                - the unique id of the target parameter.
                Value must be within the int16 datatype range.

        Returns:

            integer response indicating target parameter value.
        """
        self.__check_argument_value('widgetId', widgetId, INT16)
        self.__check_argument_value('param', param, INT16)

        self.debug.publish_string("Query widget ({}) parameter ({}) ..."
            .format(hex(widgetId), hex(param)))

        self.__write_command(MatesCommand.MATES_CMD_GET_WIDGET_PARAM)
        self.__write_int16(widgetId)
        self.__write_int16(param)

        return self.__read_response()

    def setWidgetParamByIndex(self, widgetType: MatesWidget, widgetIndex: int, param: int, value: int) -> bool:
        """
        Sets the value of a widget parameter based on widget index and parameter id.

        Args:

            widgetType: MatesWidget
                - the type of the target widget.

            widgetIndex: int
                - the index of the target widget.
                Value must be within the uint8 datatype range.

            param: int
                - the unique id of the target parameter.
                Value must be within the int16 datatype range.

            value: int
                - the value the corresponding parameter will be set to.
                Value must be within the int16 datatype range.

        Returns:
        
            boolean response indicating command success or failure.
        """
        self.__check_argument_value('widgetIndex', widgetIndex, UINT8)
        self.__check_argument_value('param', param, INT16)
        self.__check_argument_value('value', value, INT16)

        return self.setWidgetParamById(self.__getWidgetId(widgetType, widgetIndex), param, value)

    def getWidgetParamByIndex(self, widgetType: MatesWidget, widgetIndex: int, param: int) -> int:
        """
        Gets the value of a widget parameter based on widget index and parameter id.

        Args:

            widgetType: MatesWidget
                - the type of the target widget.

            widgetIndex: int
                - the index of the target widget.
                Value must be within the uint8 datatype range.

            param: int
                - the unique id of the target parameter.
                Value must be within the int16 datatype range.

        Returns:

            integer response indicating target parameter value.
        """
        self.__check_argument_value('widgetIndex', widgetIndex, UINT8)
        self.__check_argument_value('param', param, INT16)

        return self.getWidgetParamById(self.__getWidgetId(widgetType, widgetIndex), param)

    def setBufferSize(self, size: int):
        """
        Currently unused (also undocumented).
        Sets Buffer Size. Provided for future development.

        Args:

            size: int
            - new size of buffer

        Returns:

            void.
        """
        if not 0 < size <= MATES_STRING_MAX_BUFFER_SIZE:
            raise ValueError('Buffer size of {} outside the range of min:{} to max:{}'
                .format(size, 1, MATES_STRING_MAX_BUFFER_SIZE))

        self.mates_buffer_size = size

    def clearTextArea(self, textAreaIndex: int) -> bool:
        """
        Clears a targeted Text Area.

        Args:

            textAreaIndex: int
                - the index of the target Text Area widget.
                Value must be within the uint16 datatype range.

        Returns:

            boolean response indicating command success or failure.
        """
        self.__check_argument_value('textAreaIndex', textAreaIndex, UINT16)

        self.debug.publish_string("Clear TextArea {} ...".format(textAreaIndex))

        self.__write_command(MatesCommand.MATES_CMD_UPDATE_TEXT_AREA)
        self.__write_int16(textAreaIndex)
        self.__write_int8(0)

        resp = self.__wait_for_ack()

        self.debug.end_operation()

        return resp

    def updateTextArea(self, textAreaIndex: int, textFormat: str, *formatArgs) -> bool:
        """
        Updates the text displayed within Text Area widget.

        Args:

            textAreaIndex: int
                - the index of the target Text Area widget.
                Value must be within the uint16 datatype range.

            textFormat: str
                - the string format to be displayed.

            formatArgs:
                - zero or more values to be formatted into the provided
                text format string.

        Returns:

            boolean response indicating command success or failure.
        """
        self.__check_argument_value('textAreaIndex', textAreaIndex, UINT16)

        self.debug.publish_string("Update TextArea {} ...".format(textAreaIndex))

        self.__write_command(MatesCommand.MATES_CMD_UPDATE_TEXT_AREA)
        self.__write_int16(textAreaIndex)
        text_string = textFormat.format(*formatArgs)
        self.__write_string(text_string)
        self.__write_int8(0)

        resp = self.__wait_for_ack()

        self.debug.end_operation()

        return resp

    def clearPrintArea(self, printAreaIndex: int) -> bool:
        """
        Clears a targeted Print Area.

        Args:

            printAreaIndex: int
                - the index of the target Print Area widget.
                Value must be within the uint16 datatype range.

        Returns:

            boolean response indicating command success or failure.
        """
        self.__check_argument_value('printAreaIndex', printAreaIndex, UINT16)

        self.debug.publish_string("Clear PrintArea {} ...".format(printAreaIndex))

        self.__write_command(MatesCommand.MATES_CMD_CLR_PRINT_AREA)
        self.__write_int16(printAreaIndex)

        resp = self.__wait_for_ack()

        self.debug.end_operation()

        return resp

    def setPrintAreaColor565(self, printAreaIndex: int, rgb565: int):
        """
        Sets the color of a PrintArea Widget based on an rgb565 value.

        Args:
        
            printAreaIndex: int
            - index of widget, value must be within uint16 datatype range.

            rgb565: int
            - colour to set widget to, value must be within uint16 datatype range.

        Returns:

            boolean response indicating command success or failure.
        """
        self.__check_argument_value('printAreaIndex', printAreaIndex, UINT16)
        self.__check_argument_value('rgb565', rgb565, UINT16)
        
        self.__write_command(MatesCommand.MATES_CMD_SET_PRINT_COLOR)
        self.__write_int16(printAreaIndex)
        self.__write_uint16(rgb565)

        self.debug.publish_string("Set PrintArea ({}) color to {} ...".format(printAreaIndex, hex(rgb565)))

        resp = self.__wait_for_ack()

        self.debug.end_operation()

        return resp
        
    def setPrintAreaColorRGB(self, printAreaIndex: int, red: int, green: int, blue: int) -> bool:
        """
        Sets the colour of a targeted Print Area.

        Args:

            printAreaIndex: int
                - the index of the target Print Area widget.
                Value must be within the uint16 datatype range.

            red: int
                - Unsigned 8 bit integer value of red concentration.
                Value must be within the uint8 datatype range.

            blue: int
                - Unsigned 8 bit integer value of green concentration.
                Value must be within the uint8 datatype range.

            green: int
                - Unsigned 8 bit integer value of blue concentration.
                Value must be within the uint8 datatype range.

        Returns:

            boolean response indicating command success or failure.
        """
        self.__check_argument_value('printAreaIndex', printAreaIndex, UINT16)
        self.__check_argument_value('red', red, UINT8)
        self.__check_argument_value('green', green, UINT8)
        self.__check_argument_value('blue', blue, UINT8)

        rgb565 = self.__construct_rgb565_value(red, green, blue)

        return self.setPrintAreaColor565(printAreaIndex, rgb565)
    
    def appendArrayToPrintArea(self, printAreaIndex: int, array) -> bool:
        """
        Appends an array of 8-bit integers to a targeted Print Area.

        Args:

            printAreaIndex: int
                - the index of the target Print Area widget.
                Value must be within the uint16 datatype range.

            array: str
                - list of 8-bit values to be appended

        Returns:

            boolean response indicating command success or failure.
        """
        self.__check_argument_value('printAreaIndex', printAreaIndex, UINT16)

        self.debug.publish_string("Append array {} to PrintArea {} ...".format(array, printAreaIndex))

        self.__write_command(MatesCommand.MATES_CMD_APPEND_PRINT_AREA)
        self.__write_int16(printAreaIndex)
        self.__write_int16(len(array))
        for char in array:
            self.__check_argument_value('print area array item', char, UINT8)
            self.__write_uint8(char)
        
        resp = self.__wait_for_ack()

        self.debug.end_operation()

        return resp


    def appendStringToPrintArea(self, printAreaIndex: int, textFormat: str, *formatArgs) -> bool:
        """
        Appends text to a targeted Print Area.

        Args:

            printAreaIndex: int
                - the index of the target Print Area widget.
                Value must be within the uint16 datatype range.

            textFormat: str
                - the string to be appended to the Print Area
                with zero or more format specifiers to be formatted.

            formatArgs:
                - zero or more args that can be formatted into the
                textFormat string.

        Returns:

            boolean response indicating command success or failure.
        """
        self.__check_argument_value('printAreaIndex', printAreaIndex, UINT16)
        text_string = textFormat.format(*formatArgs)

        self.debug.publish_string("Append string {} to PrintArea {} ...".format(text_string, printAreaIndex))

        self.__write_command(MatesCommand.MATES_CMD_APPEND_PRINT_AREA)
        self.__write_int16(printAreaIndex)
        
        self.__write_int16(len(text_string))
        self.__write_string(text_string)

        resp = self.__wait_for_ack()

        self.debug.end_operation()

        return resp

    def appendToScopeWidget(self, scopeIndex: int, buffer:typing.List[int]) -> bool:
        """
        Appends a list of integers to a Scope widget.

        Args:

            scopeIndex: int
                - the index of the target Scope widget.
                Value must be within the uint16 datatype range.

            buffer: [int]
                - the list of datapoints to be appended to scope widget.
                Values must be within the int16 datatype range.

        Returns:

            boolean response indicating command success or failure.
        """
        self.__check_argument_value('scopeIndex', scopeIndex, UINT16)

        self.debug.publish_string("Appending values to Scope {} ...".format(scopeIndex))

        self.__write_command(MatesCommand.MATES_CMD_APPEND_SCOPE_DATA)
        self.__write_int16(scopeIndex)
        self.__write_int16(len(buffer))
        self.__write_int16_buffer(buffer)

        resp = self.__wait_for_ack()

        self.debug.end_operation()

        return resp

    def updateDotMatrixWidget(self, matrixIndex: int, textFormat: str, *formatArgs) -> bool:
        """
        Changes the text displayed by the target Dot Matrix widget.


        Args:

            matrixIndex (int): 
            - The index of the target Scope widget.
            Value must be within the uint16 datatype range.

            textFormat: str
            - the string to be appended to the Scope widget
            with zero or more format specifiers to be formatted.

            formatArgs:
            - zero or more args that can be formatted into the
            text_format string.

        Returns:

            boolean response indicating command success or failure.
        """
        self.__check_argument_value('matrix_index', matrixIndex, UINT16)

        self.debug.publish_string("Updating DotMatrix {} ...".format(matrixIndex))

        self.__write_command(MatesCommand.MATES_CMD_UPDATE_DOT_MATRIX)
        self.__write_int16(matrixIndex)
        string_to_write = textFormat.format(*formatArgs)
        self.__write_int16(len(string_to_write))
        self.__write_string(string_to_write)

        resp = self.__wait_for_ack()

        self.debug.end_operation()

        return resp

    def getButtonEventCount(self) -> int:
        """
        Gets the number of events recorded from applicable button widgets.

        Args:

            void.

        Returns:

            integer corresponding to the number of events.
        """

        self.debug.publish_string("Query number of button events...")

        self.__write_command(MatesCommand.MATES_CMD_BTN_EVENT_COUNT)

        return self.__read_response()

    def getNextButtonEvent(self) -> int:
        """
        Gets the next event source logged from applicable buttons

        Args:

            void.

        Returns:

            integer corresponding to the button widget ID
        """

        self.debug.publish_string("Query the next recorded button event...")

        self.__write_command(MatesCommand.MATES_CMD_NEXT_BTN_EVENT)

        return self.__read_response()        

    def getSwipeEventCount(self) -> int:
        """
        Gets the number of events recorded from swipe gestures.

        Args:

            void.

        Returns:

            integer corresponding to the number of events.
        """

        self.debug.publish_string("Query number of swipe events...")

        self.__write_command(MatesCommand.MATES_CMD_SWP_EVENT_COUNT)

        return self.__read_response()

    def getNextSwipeEvent(self) -> int:
        """
        Gets the next swipe event value

        Args:

            void.

        Returns:

            integer corresponding to the swipe event
        """

        self.debug.publish_string("Query the next recorded swipe event...")

        self.__write_command(MatesCommand.MATES_CMD_NEXT_SWP_EVENT)

        return self.__read_response()        

    def getVersion(self) -> str:
        """
        Helper function to obtain the version of the Python Mates Controller library.

        Args:

            void.

        Returns:

            string response of library version.
        """
        return self.MATES_CONTROLLER_LIBRARY_VERSION

    def getCompatibility(self) -> str:
        """
        Helper function to obtain the version of the Mates Studio compatible
        with this library version.

        Args:

            void.

        Returns:

            string response of Mates Studio version compatible with this library.
        """
        return self.MATES_STUDIO_COMPATIBILITY_VERSION

    def printVersion(self) -> str:
        """
        Debugging function to print the version of the Mates Studio compatible
        along with this specific library version.

        Args:

            void.

        Returns:

            void.
        """
        self.debug.publish_string("Mates Studio - Compatible Version : {} ".format(self.getCompatibility()), termination='\n')
        self.debug.publish_string("Mates Controller - Library Version: {}".format(self.getVersion()), termination='\n')

    def getError(self) -> MatesError:
        """
        Function to return the current error state of the Mates Controller.

        Args:

            void.

        Returns:

            MatesError response of current error.
        """
        return self.mates_error

    # private functions below

    def __write_command(self, command: MatesCommand):
        command_bytes = bytearray(bytes(MATES_COMMAND_START_BYTE, 'utf8'))
        command_bytes.extend(bytearray(int(command).to_bytes(WORD_BYTE_LENGTH,'big')))
        self.__write_bytes(command_bytes)

    def __write_int8(self, int8_value: int):
        self.__write_bytes(int8_value.to_bytes(CHAR_BYTE_LENGTH, 'big'))

    def __write_uint8(self, uint8_value: int):
        self.__write_bytes(uint8_value.to_bytes(CHAR_BYTE_LENGTH, 'big', signed=False))

    def __write_int16(self, word: int):
        self.__write_bytes(word.to_bytes(WORD_BYTE_LENGTH, 'big', signed=True))

    def __write_uint16(self, word: int):
        self.__write_bytes(word.to_bytes(WORD_BYTE_LENGTH, 'big', signed=False))

    def __write_int32(self, long: int):
        self.__write_bytes(long.to_bytes(INT_BYTE_LENGTH, 'big', signed=True))

    def __write_float(self, value: float):
        float_32b_value = ctypes.c_float(value).value
        bytes_to_write = struct.pack('>f', float_32b_value)
        self.__write_bytes(bytes_to_write)

    def __write_string(self, string: str):
        self.__write_bytes(bytes(string, 'utf-8'))

    def __write_int16_buffer(self, buffer: typing.List[int]):
        for word in buffer:
            self.__write_int16(word)

    def __write_bytes(self, bytes_to_write: bytes):
        self.serial_port.write(bytes_to_write)

    def __wait_for_ack(self, timeout: int=MATES_RESPONSE_TIMEOUT) -> bool:
        self.serial_port.timeout = timeout / 1000
        resp = self.serial_port.read(CHAR_BYTE_LENGTH)

        # check timeout based upon returned byte length
        if len(resp) < CHAR_BYTE_LENGTH:
            self.mates_error = MatesError.MATES_ERROR_COMMAND_TIMEOUT
            self.debug.publish_string("Commmand timedout", termination='\n')
            return False

        ack = int.from_bytes(resp, 'big', signed=False) == MATES_SAFE_ACK
        if not ack:
            self.mates_error = MatesError.MATES_ERROR_COMMAND_FAILED
            return ack

        self.mates_error = MatesError.MATES_ERROR_NONE
        self.debug.publish_response(ack)

        return ack

    def __read_int16(self) -> int:
        resp = self.serial_port.read(WORD_BYTE_LENGTH)

        # check timeout based upon returned byte length
        if len(resp) < WORD_BYTE_LENGTH:
            self.debug.publish_string("Response timeout", termination='\n')
            self.mates_error = MatesError.MATES_ERROR_RESPONSE_TIMEOUT
            return None

        return int.from_bytes(resp, 'big', signed=True)

    def __read_response(self, timeout:int =MATES_RESPONSE_TIMEOUT) -> int:
        if not self.__wait_for_ack():
            return -1

        self.serial_port.timeout = timeout / 1000
        resp = self.__read_int16()
        if self.mates_error == MatesError.MATES_ERROR_RESPONSE_TIMEOUT:
            return -1

        self.debug.publish_string(" response: {}".format(resp), termination='\n')

        return resp

    def __set_widget_value_32bit(self, widget_id: int, value:typing.Union[int, float]) -> bool:
        self.debug.publish_string("Set widget ({}) value to {} ...".format(hex(widget_id), value))

        self.__write_command(MatesCommand.MATES_CMD_SET_WIDGET_32VAL)
        self.__write_int16(widget_id)

        if isinstance(value, int):
            self.__check_argument_value('value', value, FLOAT32)
            self.__write_int32(value)
        elif isinstance(value, float):
            self.__check_argument_value('value', value, INT32)
            self.__write_float(value)

        resp = self.__wait_for_ack()

        self.debug.end_operation()        

        return resp

    def __construct_rgb565_value(self, red: int, green: int, blue: int) -> int:
        """
        Constructs a 16 bit rgb565 value.

        Args:
            red: int
                - Unsigned 8 bit integer value of red concentration.

            green: int
                - Unsigned 8 bit integer value of green concentration.

            blue: int
                - Unsigned 8 bit integer value of blue concentration.

        Returns:
            16 bit rgb565 value.
        """
        self.__check_argument_value('red', red, UINT8)
        self.__check_argument_value('green', green, UINT8)
        self.__check_argument_value('blue', blue, UINT8)

        rgb565 = ctypes.c_uint16(0)
        rgb565.value = rgb565.value | ((red&0xF8) << 8)
        rgb565.value = rgb565.value | ((green&0xFC) << 3)
        rgb565.value = rgb565.value | ((blue&0xF8) >> 3)
        return rgb565.value

    def __check_argument_value(self, arg_to_check_name: str, arg_to_check_value: int, arg_range: str=UINT16):
        (arg_min, arg_max) = datatype_ranges[arg_range]

        if not arg_min <= arg_to_check_value <= arg_max:
            raise ValueError("{} of {} outside the {} range of {} to {}"
                .format(arg_to_check_name, arg_to_check_value, arg_range, arg_min, arg_max))

    def __getWidgetId(self, widget_type: MatesWidget, widget_index: int) -> int:
        """
        Helper function to obtain the ID of a widget based on its index and type.

        Args:

            widget_type: MatesWidget
                the type of the target widget.

            widget_index: int
                the index of the target widget.

        Returns:

            boolean response indicating command success or failure.
        """
        self.__check_argument_value('widget_index', widget_index, INT16)
        return (widget_type << 8) | widget_index

    class __MatesDebug():
        def __init__(self, log_length: int=20, file_stream: io.TextIOWrapper=None ):
            self.__file_stream = file_stream
            self.__cyclic_log_length = log_length

        def end_operation(self):
            self.publish_string('\n', termination='')

        def publish_response(self, response:bool):
            if response:
                self.publish_string("success", termination='')
            else:
                self.publish_string("failure", termination='')

        def publish_string(self, debug_string: str, termination: str=' '):
            debug_string = (debug_string + termination)
            if self.__file_stream:
                try:
                    self.__file_stream.writelines(debug_string)
                except(io.UnsupportedOperation, ValueError):
                    pass
                if self.__cyclic_log_length:
                    try:
                        self.__file_stream.seek(0)
                        log_lines = self.__file_stream.readlines()
                        if len(log_lines) >= self.__cyclic_log_length:
                            self.__file_stream.truncate(0)
                            self.__file_stream.seek(0)
                            self.__file_stream.writelines(log_lines[-(self.__cyclic_log_length):])
                    except (io.UnsupportedOperation, ValueError):
                        pass
        
        def close_file(self):
            if self.__file_stream != sys.stdout:
                try:
                    self.__file_stream.close()
                except (AttributeError, io.UnsupportedOperation, ValueError):
                    pass

if __name__ == '__main__':
    print("mates controller module")