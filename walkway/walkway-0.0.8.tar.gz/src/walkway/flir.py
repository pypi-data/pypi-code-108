# 2021-07-31. Leonardo Molina.
# 2022-01-21. Last modified.

import logging
import PySpin

def getRange(nodemap, nodeName, cast=None):
    success = True
    values = (None, None)
    exception = ""
    
    if cast is None:
        cast = getType(nodeName)
    if cast is None:
        exception = "'%s' could not be recognized." % nodeName
        success = False
    else:
        try:
            node = cast(nodemap.GetNode(nodeName))
            values = (node.GetMin(), node.GetMax())
        except PySpin.SpinnakerException as ex:
            exception = str(ex)
            success = False
    
    if not success:
        message = "Unable to get value range for '%s'" % nodeName
        if len(exception) > 0:
            message = "%s ==> %s" % (message, exception)
        logging.warning(message)
    
    return values


def getValue(nodemap, nodeName, cast=None):
    success = True
    value = None
    exception = ""
    
    if cast is None:
        cast = getType(nodeName)
    if cast is None:
        exception = "'%s' could not be recognized." % nodeName
        success = False
    else:
        try:
            node = cast(nodemap.GetNode(nodeName))
        except PySpin.SpinnakerException as ex:
            exception = str(ex)
            success = False
    
    if success:
        if cast in (PySpin.CIntegerPtr, PySpin.CFloatPtr, PySpin.CBooleanPtr, PySpin.CStringPtr):
            getter = lambda node: node.GetValue()
        elif cast == PySpin.CEnumerationPtr:
            getter = lambda node: node.GetEntries()[node.GetIntValue()].GetDisplayName()
        try:
            value = getter(node)
        except PySpin.SpinnakerException as ex:
            exception = str(ex)
            success = False
    
    if not success:
        message = "Unable to get '%s'" % nodeName
        if len(exception) > 0:
            message = "%s ==> %s" % (message, exception)
        logging.warning(message)
    
    return value
    

def getType(nodeName, value=None):
    if nodeName in ("AcquisitionFrameRateEnable", "GammaEnable"):
        cast = PySpin.CBooleanPtr
    elif nodeName in ("Width", "Height", "OffsetX", "OffsetY"):
        cast = PySpin.CIntegerPtr
    elif nodeName in ("AcquisitionFrameRate", "ExposureTime", "Gain", "Gamma"):
        cast = PySpin.CFloatPtr
    elif nodeName in ("AcquisitionMode", "ExposureAuto", "GainAuto", "StreamBufferHandlingMode", "TriggerMode", "TriggerSelector"):
        cast = PySpin.CEnumerationPtr
    elif nodeName in ("DeviceSerialNumber", "DeviceUserID"):
        cast = PySpin.CStringPtr
    elif isinstance(value, bool):
        cast = PySpin.CBooleanPtr
    elif isinstance(value, int):
        cast = PySpin.CIntegerPtr
    elif isinstance(value, float):
        cast = PySpin.CFloatPtr
    elif isinstance(value, str):
        cast = PySpin.CEnumerationPtr
    else:
        cast = None
    return cast
    

def setValue(nodemap, nodeName, value, cast=None):
    success = True
    exception = ""
    
    if cast is None:
        cast = getType(nodeName, value)
    if cast is None:
        exception = "'%s' could not be recognized." % nodeName
        success = False
    else:
        try:
            node = cast(nodemap.GetNode(nodeName))
        except PySpin.SpinnakerException as ex:
            exception = str(ex)
            success = False
            
    if success:
        if cast in (PySpin.CIntegerPtr, PySpin.CFloatPtr, PySpin.CBooleanPtr, PySpin.CStringPtr):
            setter = lambda node, value : node.SetValue(value)
        elif cast == PySpin.CEnumerationPtr:
            setter = lambda node, value : node.SetIntValue(node.GetEntryByName(value).GetValue())
        try:
            setter(node, value)
        except PySpin.SpinnakerException as ex:
            exception = str(ex)
            success = False
            
    if not success:
        message = "Unable to set '%s' to '%s'" % (nodeName, str(value))
        if len(exception) > 0:
            message = "%s ==> %s" % (message, exception)
        logging.warning(message)
        
    return success