from time import sleep


def sleep_well(working_dir: str, logger, options: dict = None):
    options = options or {}
    tts = int(options.get("time", 5))
    logger.info("Sleeping for {} seconds".format(tts))
    sleep(tts)


sleep_well.description = {
    "label": "sleep well...",
    "help": "do nothing but sleep",
    "options": [
        {
            "id": "time",
            "label": "time to sleep",
            "default": 5,
            "free_input": True,
            "values": {"5": "5"},
        }
    ],
}
