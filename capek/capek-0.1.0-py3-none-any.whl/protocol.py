import re


class Protocol:
    @staticmethod
    def decode(message: str) -> dict:
        """
        Decode string of data using the SCR protocol.
        """
        result = {}

        for signal in re.findall(r'\((.*?)\)', message):
            signal = signal.split()
            try:
                sensor = signal.pop(0)
                if not signal:
                    result[sensor] = None
                else:
                    result[sensor] = signal if len(signal) > 1 else signal[0]
            except IndexError:
                continue

        return result

    @staticmethod
    def encode(structure: dict) -> str:
        """
        Encode control data using the SCR protocol.
        """
        result = ''

        for sensor, signal in structure.items():
            if signal is not None:
                if isinstance(signal, list):
                    signal = ' '.join([str(s) for s in signal])
                result += f'({sensor} {signal})'

        return result
