from .ng import get_client, get_requisitions

PLATFORMS = ["sensor"]


def config_schema(vol, cv, const):
    return vol.Schema(
        {
            const["DOMAIN"]: vol.Schema(
                {
                    vol.Required(const["SECRET_ID"]): cv.string,
                    vol.Required(const["SECRET_KEY"]): cv.string,
                    vol.Optional(const["DEBUG"], default=False): cv.string,
                    vol.Required(const["REQUISITIONS"]): [
                        {
                            vol.Required(const["ENDUSER_ID"]): cv.string,
                            vol.Required(const["INSTITUTION_ID"]): cv.string,
                            vol.Optional(const["REFRESH_RATE"], default=240): cv.string,
                            vol.Optional(const["BALANCE_TYPES"], default=[]): [cv.string],
                            vol.Optional(const["HISTORICAL_DAYS"], default=30): cv.string,
                            vol.Optional(const["IGNORE_ACCOUNTS"], default=[]): [cv.string],
                            vol.Optional(const["ICON_FIELD"], default="mdi:cash-100"): cv.string,
                        },
                    ],
                },
                extra=vol.ALLOW_EXTRA,
            )
        },
        extra=vol.ALLOW_EXTRA,
    )


def get_config(configs, requisition):
    """Get the associated config."""
    for config in configs:
        ref = f"{config['enduser_id']}-{config['institution_id']}"
        if requisition["reference"] == ref:
            return config


def entry(hass, config, const, logger):
    """Nordigen platform entry."""
    domain_config = config.get(const["DOMAIN"])
    if domain_config is None:
        logger.warning("Nordigen not configured")
        return True

    logger.debug("config: %s", domain_config)
    client = get_client(secret_id=domain_config[const["SECRET_ID"]], secret_key=domain_config[const["SECRET_KEY"]])
    hass.data[const["DOMAIN"]] = {
        "client": client,
    }

    requisitions = get_requisitions(
        client=client,
        configs=domain_config[const["REQUISITIONS"]],
        logger=logger,
        const=const,
    )

    discovery = {
        "requisitions": requisitions,
    }

    for platform in PLATFORMS:
        hass.helpers.discovery.load_platform(platform, const["DOMAIN"], discovery, config)

    return True
