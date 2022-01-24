from typing import NoReturn

from ._http import HTTPClient
from ._models import (
    Camp,
    CastleGalleries,
    CrewMember,
    PlebisciteCandidate
)


class Client:
    """
    Pozwala na wykonywanie asynchronicznych zapytań do Quatromondis API.

    :ivar http: ``HTTPClient`` używany do wykonywania zapytań.
    """

    def __init__(self, http: HTTPClient | None = None):
        """
        Initializuje instancję Client-a.

        :param http: HTTPClient, który będzie używany zamiast tworzenia zupełnie nowego.
        """
        self.http: HTTPClient = HTTPClient() if http is None else http

    async def get_castles(self) -> list[CastleGalleries]:
        """
        Dostaje listę zamków z fotorelacji.

        :returns: lista zamków.
        """
        castles = await self.http.get_api_images_galleries_castles()
        return [CastleGalleries.from_dict(castle, http=self.http) for castle in castles]

    async def get_camps(self) -> list[Camp]:
        """
        Dostaje listę obozów.

        :returns: lista aktualnie dostępnych na stronie obozów.
        """
        camps = await self.http.get_api_camps()
        return [Camp.from_dict(camp) for camp in camps]

    async def get_crew(self) -> list[CrewMember]:
        """
        Dostaje członków kadry z obozów.

        :returns: lista psorów i kierowników.
        """
        crew = await self.http.get_api_parentszone_crew()
        return [CrewMember.from_dict(crew_member, http=self.http) for crew_member in crew]

    async def get_plebiscite(self, year: int) -> list[PlebisciteCandidate]:  # TODO Plebiscite - model
        """
        Dostaje listę kandydatów plebiscytu.

        :param year: rok, z którego szukani są kandydaci plebiscytu.
        :returns: lista kandydatów plebiscytu z podanego roku.
        """
        candidates = await self.http.get_api_vote_plebiscite(year)
        return [PlebisciteCandidate.from_dict(candidate, http=self.http) for candidate in candidates]

    async def apply_for_job(self):
        """
        Zgłasza aplikację o pracę.
        """
        await self.http.post_api_parentszone_apply()

    async def __aenter__(self) -> "Client":
        await self.http.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self.http.__aexit__(exc_type, exc_val, exc_tb)

    def __enter__(self) -> NoReturn:
        self.http.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.http.__aexit__(exc_type, exc_val, exc_tb)
