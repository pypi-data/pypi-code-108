# single ClientSession for all fhempy modules

from aiohttp import ClientSession

session = ClientSession()
