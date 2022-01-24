from discolib.core import Disco
from discolib.io import DiscoIO, Validate

class CustomIO(DiscoIO):

    @Validate.read
    def read(self, length: int) -> bytes:
        """Implement your own read() that will read bytes from your component(s)."""
        super().read(length)  # Remove this.
        ...

    @Validate.write
    def write(self, data: bytes) -> None:
        """Implement your own write() that send bytes to your component(s)."""
        super().read(data)  # Remove this.
        ...


def main():
    disco = Disco(CustomIO())               # Initialize a DISCo object
    print(disco.get_attr_json(indent=2))    # Get all of the DISCo's attributes (as json)
    print(dir(disco))                       # Check out all of the attributes which can be interracted with via attr.setpoint = X.

if __name__ == '__main__':
    main()
