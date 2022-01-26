import threading
import time

import adafruit_dht
from board import D17
from gpiozero import LED


class StatusLed:
    def __init__(self, ok_pin, err_pin):
        self.ok_led = LED(ok_pin)
        self.err_led = LED(err_pin)
        self._error = False

    def _turn_off(self, duration):
        time.sleep(duration)
        if not self._error:
            self.off()

    def error(self):
        self._error = True
        self._update_led_color()

    def clear(self):
        self._error = False

    def on(self):
        self._update_led_color()
        self.schedule_stop_after(1)

    def _update_led_color(self):
        if self._error:
            self.ok_led.off()
            self.err_led.on()
        else:
            self.ok_led.on()
            self.err_led.off()

    def schedule_stop_after(self, stop_after):
        threading.Thread(None, self._turn_off, args=(stop_after,), daemon=True).start()

    def off(self):
        self.ok_led.off()
        self.err_led.off()
        self.clear()


class HTSensor:
    _name: str
    _thread: threading.Thread
    _started: bool

    def __init__(self, name, data_pin, ok_pin, err_pin):
        self._name = name
        self.humidity = -1
        self.temperature = -1
        self._started = False
        self._status_led = StatusLed(ok_pin, err_pin)
        self._dht_sensor = _dht_sensor_factory(data_pin)

    def start_daemon(self, poll_interval):
        self._started = True
        self._thread = threading.Thread(target=self._poll, args=(poll_interval,), daemon=True)
        self._thread.start()

    def stop(self):
        self._started = False
        self._status_led.clear()

    def _poll(self, poll_interval):
        while self._started:
            try:
                self._status_led.on()
                self._do_read()
                time.sleep(poll_interval)
            except RuntimeError as error:
                # Errors happen fairly often, DHT's are hard to read, just keep going
                self._status_led.error()
                print(error.args[0])
                time.sleep(poll_interval)
                continue
            except Exception as error:
                self._status_led.error()
                self._dht_sensor.exit()
                raise error
            finally:
                self._status_led.clear()

    def _do_read(self):
        self.humidity = self._dht_sensor.humidity
        self.temperature = self._dht_sensor.temperature
        _log_reading(self.temperature, self.humidity)


def _log_reading(temperature, humidity):
    print('Temp={0:.1f}*C  Humidity={1:.1f}%'.format(temperature, humidity))


def _dht_sensor_factory(pin_number: int) -> adafruit_dht.DHTBase:
    """Factory method to create DHT11/12 sensors

    :param pin_number: the pin number to which the DHT sensor is connected
    :return: the DHT11/12 sensor instance
    """
    known_pins = {17: D17}
    if pin_number in known_pins:
        return adafruit_dht.DHT11(known_pins[pin_number])
    raise Exception(f"Unknown pin {pin_number}")


