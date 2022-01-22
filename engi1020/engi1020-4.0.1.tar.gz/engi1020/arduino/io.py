from . import command


def analog_read(pin):
    """Read a value from an analog port.

    Parameters:
      pin (int):     Analog pin to read from (e.g., 2 for A2).

    Returns:         Quantized analog value (0–1023).
    """

    return command(f"Reading from analog port {pin}", "ar", int, bytes([pin]))


def analog_write(pin, duty):
    """Write a value to an analog port.

    Parameters:
      pin (int):     Analog pin to write to (e.g., 2 for A2).
      duty (int):    Duty cycle to set (0–255).
    """

    command(f"Writing {duty} to analog port {pin}",
            "aw", "AW-OK", bytes([pin, duty]))


def digital_read(pin):
    """Read a value from a digital port.

    Parameters:
      pin (int):     Digital pin to read from (e.g., 4 for D4).

    Returns:         True or False.
    """

    return command(f"Reading from digital port {pin}", "dr", bool, bytes([pin]))


def digital_write(pin, value):
    """Write a value to a digital port.

    Parameters:
      pin (int):     Digital pin to write to (e.g., 4 for D4).
      value (bool):  Value to write (True or False).
    """

    command(f"Writing {value} to digital port {pin}",
            "dw", "DW-OK", bytes([pin, value]))

def buzzer_frequency(pin, freq):
    """Play a frequency on a buzzer in a given port

    Parameters:
      pin (int):     Pin to write to (e.g., 4 for D4).
      freq (int):    Note to play in Hz.
    """
    
    freq_bytes = freq.to_bytes(2, byteorder = "little")
    command(f"Playing {freq}Hz on buzzer in port {pin}",
             "bf", "BF-OK", bytes([pin, freq_bytes[0], freq_bytes[1]]))

def buzzer_note(pin, freq, sec):
    """Play a frequency on a buzzer in a given port

    Parameters:
      pin (int):     Pin to write to (e.g., 4 for D4).
      freq (int):    Note to play in Hz.
      sec (int/float):  Duration of note in seconds
    """
    freq_bytes = freq.to_bytes(2, byteorder = "little")
    sec *= 1000 #Convert to ms
    sec = int(sec)
    sec_bytes = sec.to_bytes(4, byteorder = "little")
    command(f"Playing {freq}Hz on buzzer in port {pin} for {sec} seconds",
             "bt", "BT-OK", bytes([pin, freq_bytes[0], freq_bytes[1], sec_bytes[0], sec_bytes[1], sec_bytes[3], sec_bytes[4]]))

def buzzer_stop(pin):
    """Play a frequency on a buzzer in a given port

    Parameters:
      pin (int):     Pin to write to (e.g., 4 for D4).
      freq (int):    Note to play in Hz.
    """
    
    command(f"Stopping buzzer in port {pin}",
             "bs", "BS-OK", bytes([pin]))


