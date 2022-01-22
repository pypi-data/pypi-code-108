import asyncio

from fhempy.lib.fusionsolar.fusionsolar_api import FusionSolarKioksApi

from .. import fhem, utils
from ..generic import FhemModule


class fusionsolar(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)

        attr_config = {
            "interval": {
                "default": 300,
                "format": "int",
                "help": "Change interval, default is 300.",
            }
        }
        self.set_attr_config(attr_config)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) > 3:
            return "Usage: define my_solar PythonModule fusionsolar <KIOSKKEY>"
        self._kioskkey = args[3]
        await fhem.readingsBeginUpdate(hash)
        await fhem.readingsBulkUpdateIfChanged(hash, "state", "ready")
        await fhem.readingsEndUpdate(hash, 1)
        self.create_async_task(self.update())

    async def update(self):
        api = FusionSolarKioksApi("https://eu5.fusionsolar.huawei.com")
        data = await utils.run_blocking(api.getRealTimeKpi, self._kioskkey)

        return data
