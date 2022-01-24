from discolib.core import Disco
from discolib.io import DiscoIO, Validate
import serial  # pip install pyserial

disco = None

class SerialIO(DiscoIO):
    ser = serial.Serial('/dev/ttyACM0', baudrate=115200, timeout=0.5)  # An example serial device 

    @Validate.read
    def read_raw(self) -> bytes:
        """Read bytes from the serial device."""
        return self.ser.read_until(b'\x00')[:-1]  # Exclude delim

    @Validate.write
    def write_raw(self, data: bytes) -> None:
        """Send bytes to the serial device."""
        self.ser.write(data)


def main():
    global disco
    disco = Disco(SerialIO())               # Initialize a DISCo object
    print(disco.get_attr_json(indent=2))    # Get all of the DISCo's attributes (as json)
    print(dir(disco))                       # Check out all of the attributes which can be interracted with via attr.setpoint = X.

if __name__ == '__main__':
    main()
