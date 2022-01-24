from bosch_thermostat_client.const.easycontrol import PAGINATION
from bosch_thermostat_client.const import (
    ID,
    NAME,
    REGULAR,
    URI,
    TYPE,
    VALUE,
    RECORDING,
    RECORDERDRES,
    DEEP,
    SENSOR_TYPE,
    DB_RECORD,
    STATE_CLASS,
    DEVICE_CLASS,
)
from bosch_thermostat_client.helper import (
    BoschEntities,
)

from .notification import NotificationSensor
from .sensor import Sensor
from .recording import RecordingSensor
from .crawl import CrawlSensor
from .energy import EnergySensor

NOTIFICATIONS = "notifications"
STATE = "state"
ENERGY = "energy"


def get_sensor_class(recording_type=False):
    return RecordingSensor if recording_type else CrawlSensor


def get_device_class(uri, default_class="energy"):
    if any(x in uri for x in ["temp", "outdoor"]):
        return "temperature"
    return default_class


class Sensors(BoschEntities):
    """Sensors object containing multiple Sensor objects."""

    def __init__(self, connector, sensors_db=None, uri_prefix=None):
        """
        Initialize sensors.

        :param dict requests: { GET: get function, SUBMIT: submit function}
        """
        self._connector = connector
        super().__init__(connector.get)
        self._items = {}
        for sensor_id, sensor in sensors_db.items():
            if sensor_id not in self._items:
                if sensor_id == NOTIFICATIONS:
                    self._items[sensor_id] = NotificationSensor(
                        connector=connector,
                        attr_id=sensor_id,
                        name=sensor[NAME],
                        path=f"{uri_prefix}/{sensor[ID]}" if uri_prefix else sensor[ID],
                    )
                elif sensor_id == ENERGY:
                    self._items[sensor_id] = EnergySensor(
                        connector=connector,
                        attr_id=sensor_id,
                        name=sensor.get(NAME),
                        path=sensor.get(ID),
                        pagination=sensor.get(PAGINATION),
                        state_class=sensor.get(STATE_CLASS),
                    )
                else:
                    self._items[sensor_id] = Sensor(
                        connector=connector,
                        attr_id=sensor_id,
                        name=sensor[NAME],
                        path=f"{uri_prefix}/{sensor[ID]}" if uri_prefix else sensor[ID],
                        device_class=sensor.get(DEVICE_CLASS),
                        state_class=sensor.get(STATE_CLASS),
                        kind=sensor.get(TYPE, REGULAR),
                    )

    async def initialize(self, crawl_sensors):
        """Initialize recording sensors."""
        fetched_sensors = []

        for record in crawl_sensors:
            retrieved = {
                VALUE: await self.retrieve_from_module(
                    deep=record[DEEP],
                    path=record[URI],
                    exclude=record.get("exclude"),
                ),
                DB_RECORD: record,
                RECORDING: record.get(SENSOR_TYPE, REGULAR) == RECORDING,
            }
            if VALUE in retrieved:
                fetched_sensors.append(retrieved)

        def get_id(value, recording_type=False):
            value = value if not recording_type else value[RECORDERDRES]
            return f'r{value[ID].split("/")[-1]}'

        for found in fetched_sensors:
            for rec in found[VALUE]:
                sensor_id = get_id(rec, found[RECORDING])
                if sensor_id not in self._items:
                    self._items[sensor_id] = get_sensor_class(found[RECORDING])(
                        connector=self._connector,
                        attr_id=sensor_id,
                        name=sensor_id,
                        path=rec[ID],
                        kind=found[DB_RECORD].get(SENSOR_TYPE),
                        state=found[DB_RECORD].get(STATE),
                        device_class=get_device_class(
                            uri=rec[ID],
                            default_class=found[DB_RECORD].get(DEVICE_CLASS, "energy"),
                        ),
                        state_class=found[DB_RECORD].get(STATE_CLASS),
                    )

    def __iter__(self):
        return iter(self._items.values())

    @property
    def sensors(self):
        """Get sensor list."""
        return self.get_items().values()
