from dataclasses import dataclass
import datetime
from pyinspirehep.utils import convert_json_timestamp
from typing import List

@dataclass
class SingleRecordResponse:
    """Class to contain Inspirehep API single record respones.

    Any single record object of Inspirehep API will have some determined
    keyword which are the attributes of the `SingleRecordResponse` class.

    Attribtes
    ---------
    id : str
        The unique identifier of the object.

    created: datetime.datetime
        The UTC timestamp when object was created.

    updated: datetime.datetime
        The UTC timestamp when object was las updated.

    links: dict
        List of related links to current object.

    metadata:
        Information about the objects such as titles, authors, etc.

    """
    id: str
    created: datetime.datetime = None
    updated: datetime.datetime = None
    links: dict = None
    metadata: dict = None

    @classmethod
    def from_response(cls, respone: dict):
        """

        Parameters
        ----------
        respone : dict
            

        Returns
        -------
        SingleRecordResponse

        """
        id = respone.get("id", None)
        created = convert_json_timestamp(
            respone.get("created", None),
        )
        updated = convert_json_timestamp(
            respone.get("updated", None),
        )
        links = respone.get("links", {})
        metadata = respone.get("metadata", {})
        return SingleRecordResponse(
            id=id,
            created=created,
            updated=updated,
            links=links,
            metadata=metadata,
        )

@dataclass
class Hits:
    """Class to contain Hits object.
    
    Inspirehep API when used for searhing returns a json object with
    two keys, hits and links. The current class is a class to store
    hits data only.
    The hits data itself contains two keys: hits and total.

    Attribtes
    ---------
    total : int
        The total number of records as a result of search.

    hits : List[SingleRecordResponse]
        List of SingleRecordResponse instances of Inspirehep API
        
    """
    total: int = None
    hits: List[SingleRecordResponse] = None

    @classmethod
    def from_dict(cls, hits_dict=None):
        """

        Parameters
        ----------
        hits_dict :
             (Default value = None)

        Returns
        -------
        Hits
        """
        hits_lits = []
        if hits_dict is not None:
            hits = hits_dict.get("hits", None)
            if hits:
                for hit in hits:
                    hits_lits.append(
                        SingleRecordResponse.from_response(hit)
                        )
            total = hits_dict.get("total", None)
        else:
            hits = None
            total = None
        return Hits(
            hits=hits_lits,
            total=total,
        )


@dataclass
class SearchResponse:
    """Class to contain the Inspirehep API search results.

    """
    hits: Hits
    links: dict

    @classmethod
    def from_response(cls, response: dict):
        """

        Parameters
        ----------
        response : dict
            A dictionary which is the json response of Inspirehep when
            the request is for searching
            

        Returns
        -------
        SearchResponse

        """
        links = response.get("links", None)
        hits = Hits.from_response(response.get("hits", None))
        return SearchResponse(
            links=links,
            hits=hits,
            )