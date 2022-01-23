"""Platform for sensor integration."""
import random
import re
from datetime import datetime, timedelta

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator, UpdateFailed

from .ng import get_accounts

pattern = re.compile(r"(?<!^)(?=[A-Z])")

ATTRIBUTION = "Data provided by Nordigen"
DEFAULT_BALANCE_TYPES = [
    "expected",
    "closingBooked",
    "openingBooked",
    "interimAvailable",
    "interimBooked",
    "forwardAvailable",
    "nonInvoiced",
]


def snake(name):
    return pattern.sub("_", name).lower()


def random_balance(*args, **kwargs):
    """Generate random balances for testing."""
    return {
        "balances": [
            {
                "balanceAmount": {
                    "amount": random.randrange(0, 100000, 1) / 100,
                    "currency": "SEK",
                },
                "balanceType": "interimAvailable",
                "creditLimitIncluded": True,
            },
            {
                "balanceAmount": {
                    "amount": random.randrange(0, 100000, 1) / 100,
                    "currency": "SEK",
                },
                "balanceType": "interimBooked",
            },
        ]
    }


def balance_update(logger, async_executor, fn, account_id):
    """Fetch latest information."""

    async def update():
        logger.debug("Getting balance for account :%s", account_id)
        try:
            data = (await async_executor(fn, account_id))["balances"]
        except Exception as err:
            raise UpdateFailed(f"Error updating Nordigen sensors: {err}")

        data = {
            **{
                "closingBooked": None,
                "expected": None,
                "openingBooked": None,
                "interimAvailable": None,
                "interimBooked": None,
                "forwardAvailable": None,
                "nonInvoiced": None,
            },
            **{balance["balanceType"]: balance["balanceAmount"]["amount"] for balance in data},
        }

        logger.debug("balance for %s : %s", account_id, data)
        return data

    return update


def requisition_update(logger, async_executor, fn, requisition_id):
    """Fetch latest information."""

    async def update():
        logger.debug("Getting requisition for account :%s", requisition_id)
        try:
            data = await async_executor(fn, requisition_id)
        except Exception as err:
            raise UpdateFailed(f"Error updating Nordigen sensors: {err}")

        logger.debug("balance for %s : %s", requisition_id, data)
        return data

    return update


def build_coordinator(hass, logger, updater, interval, reference):
    return DataUpdateCoordinator(
        hass,
        logger,
        name=f"nordigen-balance-{reference}",
        update_method=updater,
        update_interval=interval,
    )


def get_balance_types(logger, config, field, defaults=DEFAULT_BALANCE_TYPES):
    ret = [balance_type for balance_type in config.get(field) or defaults]
    logger.debug("configured balance types: %s", ret)
    return ret


async def build_account_sensors(hass, logger, account, const, debug):
    fn = random_balance if debug else hass.data[const["DOMAIN"]]["client"].account.balances
    updater = balance_update(
        logger=logger,
        async_executor=hass.async_add_executor_job,
        fn=fn,
        account_id=account["id"],
    )
    interval = timedelta(minutes=int(account["config"][const["REFRESH_RATE"]]))
    balance_coordinator = build_coordinator(
        hass=hass, logger=logger, updater=updater, interval=interval, reference=account.get("unique_ref")
    )

    await balance_coordinator.async_config_entry_first_refresh()

    logger.debug("listeners: %s", balance_coordinator._listeners)

    balance_types = get_balance_types(logger=logger, config=account["config"], field=const["BALANCE_TYPES"])

    entities = []
    for balance_type in balance_types:
        entities.append(
            BalanceSensor(
                domain=const["DOMAIN"],
                icons=const["ICON"],
                balance_type=balance_type,
                coordinator=balance_coordinator,
                **account,
            )
        )

    return entities


async def build_requisition_sensor(hass, logger, requisition, const, debug):
    updater = requisition_update(
        logger=logger,
        async_executor=hass.async_add_executor_job,
        fn=hass.data[const["DOMAIN"]]["client"].requisitions.by_id,
        requisition_id=requisition["id"],
    )
    interval = timedelta(seconds=15)
    coordinator = build_coordinator(
        hass=hass, logger=logger, updater=updater, interval=interval, reference=requisition.get("reference")
    )

    await coordinator.async_config_entry_first_refresh()

    logger.debug("listeners: %s", coordinator._listeners)

    return [
        RequisitionSensor(
            domain=const["DOMAIN"],
            icons=const["ICON"],
            coordinator=coordinator,
            client=hass.data[const["DOMAIN"]]["client"],
            ignored_accounts=requisition["config"][const["IGNORE_ACCOUNTS"]],
            logger=logger,
            const=const,
            debug=debug,
            **requisition,
        )
    ]


async def build_sensors(hass, logger, account, const, debug=False):
    return await build_requisition_sensor(hass=hass, logger=logger, requisition=account, const=const, debug=debug)


class RequisitionSensor(CoordinatorEntity):
    _account_sensors = {}

    def __init__(
        self,
        coordinator,
        domain,
        client,
        logger,
        *args,
        **kwargs,
    ):
        """Unconfirmed sensor entity."""
        self._domain = domain
        self._client = client
        self._logger = logger

        self._id = kwargs["id"]
        self._reference = kwargs["reference"]
        self._icons = kwargs["icons"]
        self._link = kwargs["link"]
        self._ignored_accounts = kwargs["ignored_accounts"]
        self._const = kwargs["const"]
        self._debug = kwargs.get("debug", False)
        self._config = kwargs["config"]
        self._details = kwargs["details"]
        self._account_sensors = {}

        id = self._details.get("id")
        self._device = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(self._domain, id)},
            manufacturer="Nordigen",
            model="v2",
            name=self._details.get("name"),
            configuration_url="https://ob.nordigen.com/api/docs",
        )

        super().__init__(coordinator)

    @property
    def device_info(self):
        """Return device information."""
        return self._device

    @property
    def unique_id(self):
        """Return the ID of the sensor."""
        return self._reference

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._reference

    @property
    def state(self):
        """Return the sensor state."""
        return self.coordinator.data.get("status") == "LN"

    def _requisition(self):
        return {
            "id": self._id,
            "reference": self._reference,
            "details": self._details,
        }

    def do_job(self, **kwargs):
        def job():
            return get_accounts(**kwargs)

        return job

    async def _setup_account_sensors(self, client, accounts, ignored):
        accounts = await self.hass.async_add_executor_job(
            self.do_job(
                fn=client.account.details,
                requisition={
                    "id": self._id,
                    "accounts": accounts,
                },
                logger=self._logger,
                ignored=ignored,
            )
        )
        self._logger.debug(accounts)
        entities = []
        for account in accounts:
            self._logger.debug("account: %s", account)

            if self._account_sensors.get(account["unique_ref"]):
                continue

            self._account_sensors[account["unique_ref"]] = True
            entities.extend(
                await build_account_sensors(
                    hass=self.hass,
                    logger=self._logger,
                    const=self._const,
                    debug=self._debug,
                    account={
                        **account,
                        "config": self._config,
                        "requisition": self._requisition(),
                    },
                )
            )

        if entities:
            await self.platform.async_add_entities(entities)

    @property
    def state_attributes(self):
        """Return State attributes."""
        info = (
            "Authenticate to your bank with this link. This sensor will "
            "monitor the requisition every few minutes and update once "
            "authenticated. "
            ""
            "Once authenticated this sensor will be replaced with the actual "
            "account sensor. If you will not authenticate this service "
            "consider removing the config entry."
        )
        state = {
            "link": self._link,
            "info": info,
            "accounts": self.coordinator.data.get("accounts"),
            "status": self.coordinator.data.get("status"),
            "last_update": datetime.now(),
        }

        seconds = 120 if self.coordinator.data.get("status") == "LN" else 15
        self.coordinator.update_interval = timedelta(seconds=seconds)

        if self.state:
            del state["info"]
            del state["link"]

            sensor_job = self._setup_account_sensors(
                client=self._client, accounts=self.coordinator.data.get("accounts"), ignored=self._ignored_accounts
            )
            self.hass.add_job(sensor_job)

        return state

    @property
    def icon(self):
        """Return the entity icon."""
        return self._icons.get("auth")

    @property
    def available(self) -> bool:
        """Return True when account is enabled."""
        return True


class BalanceSensorEntityDescription(SensorEntityDescription):
    """Balance Sensor Entity Description."""


class BalanceSensor(CoordinatorEntity, SensorEntity):
    """Nordigen Balance Sensor."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        domain,
        icons,
        coordinator,
        id,
        iban,
        bban,
        unique_ref,
        name,
        owner,
        currency,
        product,
        status,
        bic,
        requisition,
        balance_type,
        config,
    ):
        """Initialize the sensor."""
        self._icons = icons
        self._domain = domain
        self._balance_type = balance_type
        self._id = id
        self._iban = iban
        self._bban = bban
        self._unique_ref = unique_ref
        self._name = name
        self._owner = owner
        self._currency = currency
        self._product = product
        self._status = status
        self._bic = bic
        self._requisition = requisition
        self._config = config

        self.entity_description = BalanceSensorEntityDescription(
            key=self.unique_id,
            name=self.name,
            native_unit_of_measurement=self._currency,
            icon=self.icon,
            device_class=SensorDeviceClass.MONETARY,
            state_class=SensorStateClass.MEASUREMENT,
        )

        id = self._requisition.get("details", {}).get("id")
        self._device = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(self._domain, id)},
            manufacturer="Nordigen",
            model="v2",
            name=self._requisition.get("details", {}).get("name"),
            configuration_url="https://ob.nordigen.com/api/docs",
        )

        super().__init__(coordinator)

    @property
    def device_info(self):
        """Return device information."""
        return self._device

    @property
    def unique_id(self):
        """Return the ID of the sensor."""
        return f"{self._unique_ref}-{self.balance_type}"

    @property
    def balance_type(self):
        """Return the sensors balance type."""
        return snake(self._balance_type)

    @property
    def name(self):
        """Return the name of the sensor."""
        if self._owner and self._name:
            return f"{self._owner} {self._name} ({self.balance_type})"

        if self._name:
            return f"{self._name} {self._unique_ref} ({self.balance_type})"

        return f"{self._unique_ref} ({self.balance_type})"

    @property
    def state(self):
        """Return the sensor state."""
        if not self.coordinator.data[self._balance_type]:
            return None
        return round(float(self.coordinator.data[self._balance_type]), 2)

    @property
    def state_attributes(self):
        """Return State attributes."""
        return {
            "balance_type": self._balance_type,
            "iban": self._iban,
            "unique_ref": self._unique_ref,
            "name": self._name,
            "owner": self._owner,
            "product": self._product,
            "status": self._status,
            "bic": self._bic,
            "reference": self._requisition["reference"],
            "last_update": datetime.now(),
        }

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._currency

    @property
    def icon(self):
        """Return the entity icon."""
        return self._icons.get(self._currency, self._icons.get("default"))

    @property
    def available(self) -> bool:
        """Return True when account is enabled."""
        return True
