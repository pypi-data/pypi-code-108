import os
import xmltodict

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, validate_arguments
from json import dumps

from easyDataverse.core.uploader import upload_to_dataverse, update_dataset
from easyDataverse.core.dataverseBase import DataverseBase
from easyDataverse.core.downloader import download_from_dataverse


class Dataset(BaseModel):

    class Config:
        extra = "allow"

    metadatablocks: Dict[str, Any] = dict()
    p_id: Optional[str] = None

    # ! Adders

    def add_metadatablock(
        self,
        metadatablock: DataverseBase
    ) -> None:
        """Adds a metadatablock object to the dataset if it is of 'DataverseBase' type and has a metadatablock name"""

        # Check if the metadatablock is of 'DataverseBase' type
        if issubclass(metadatablock.__class__, DataverseBase) is False:
            raise TypeError(
                f"Expected class of type 'DataverseBase', got '{metadatablock.__class__.__name__}'"
            )

        if hasattr(metadatablock, '_metadatablock_name') is False:
            raise TypeError(
                f"The provided class {metadatablock.__class__.__name__} has no metadatablock name and is thus not compatible with this function."
            )

        # Add the metadatablock to the dataset as a dict
        block_name = getattr(metadatablock, "_metadatablock_name")
        self.metadatablocks.update(
            {block_name: metadatablock}
        )

        # ... and to the __dict__
        setattr(self, block_name, metadatablock)

    # ! Exporters

    def xml(self) -> str:
        """Returns an XML representation of the dataverse object."""

        # Turn all keys to be camelcase
        fields = self._keys_to_camel(
            {"dataset_version": self.dict()}
        )

        return xmltodict.unparse(
            fields,
            pretty=True, indent="    "
        )

    def dataverse_dict(self) -> dict:
        """Returns a dictionary representation of the dataverse dataset."""

        # Convert all blocks to the appropriate format
        blocks = {}
        for block in self.metadatablocks.values():
            blocks.update(block.dataverse_dict())

        return {
            "datasetVersion": {
                "metadataBlocks": blocks
            }
        }

    def dataverse_json(self, indent: int = 2) -> str:
        """Returns a JSON representation of the dataverse dataset."""

        return dumps(self.dataverse_dict(), indent=indent)

    # ! Dataverse interfaces

    def upload(
        self,
        dataverse_name: str,
        filenames: List[str] = None,
        DATAVERSE_URL: Optional[str] = None,
        API_TOKEN: Optional[str] = None
    ) -> str:
        """Uploads a given dataset to a Dataverse installation specified in the environment variable.

        Args:
            dataverse_name (str): Name of the target dataverse.
            filenames (List[str], optional): File or directory names which will be uploaded. Defaults to None.
            DATAVERSE_URL (Optional[str], optional): Alternatively provide base url as argument. Defaults to None.
            API_TOKEN (Optional[str], optional): Alternatively provide the api token as argument. Attention, do not use this for public scripts, otherwise it will expose your API Token. Defaults to None.
            contact_name (Optional[str], optional): Provide a name that can be contacted for any requests regarding the dataset. Defaults to None.
            contact_mail (Optional[str], optional): Provide an email that can be used to send requests regarding the dataset. Defaults to None.

        Returns:
            str: [description]
        """

        self.p_id = upload_to_dataverse(
            json_data=self.dataverse_json(),
            dataverse_name=dataverse_name,
            filenames=filenames,
            p_id=self.p_id,
            DATAVERSE_URL=DATAVERSE_URL,
            API_TOKEN=API_TOKEN
        )

        return self.p_id

    def update(
        self,
        contact_name: Optional[str] = None,
        contact_mail: Optional[str] = None,
        filenames: Optional[list[str]] = None,
        DATAVERSE_URL: Optional[str] = None,
        API_TOKEN: Optional[str] = None
    ):
        """Updates a given dataset if a p_id has been given.

        Use this function in conjunction with 'from_dataverse_doi' to edit and update datasets.
        Due to the Dataverse REST API, downloaded datasets wont include contact mails, but in
        order to update the dataset it is required. For this, provide a name and mail for contact.
        EasyDataverse will search existing contacts and when a name fits, it will add the mail.
        Otherwise a new contact is added to the dataset.

        Args:
            contact_name (str, optional): Name of the contact. Defaults to None.
            contact_mail (str, optional): Mail of the contact. Defaults to None.
        """

        # Update contact
        if contact_name is None and contact_mail is None:
            # Check if there is already a contact defined
            contact_mails = [
                contact.email
                for contact in self.citation.contact
                if contact.email
            ]

            if len(contact_mails) == 0:
                raise ValueError(
                    f"Please provide a contact name and email to update the dataset"
                )

        # Check if there is a contact with the given name already in the dataset
        has_mail = False
        for contact in self.citation.contact:
            if contact.name == contact_name:
                contact.email = contact_mail
                has_mail = True

        if has_mail == False:
            # Assign a completely new contact if the name is new
            self.citation.add_contact(
                name=contact_name,
                email=contact_mail
            )

        update_dataset(
            json_data=self.dataverse_dict()["datasetVersion"],
            p_id=self.p_id,
            DATAVERSE_URL=DATAVERSE_URL,
            API_TOKEN=API_TOKEN,
            filenames=filenames
        )

    # ! Initializers

    @classmethod
    @validate_arguments
    def from_dataverse_doi(cls, doi: str):
        """Initializes a Dataset from a given Dataverse dataset.

        Args:
            doi (str): DOI of the dataverse Dataset.
            lib_name (str): Name of the library to fetch the given metadatablocks.

        Returns:
            Dataset: Resulting dataset that has been downloaded from Dataverse.
        """

        lib_name = os.environ["EASYDATAVERSE_LIB_NAME"]

        return download_from_dataverse(cls(), doi, lib_name)

    # ! Utilities

    @staticmethod
    def _snake_to_camel(word: str) -> str:
        return ''.join(x.capitalize() or '_' for x in word.split('_'))

    def _keys_to_camel(self, dictionary: dict):
        nu_dict = {}
        for key in dictionary.keys():
            if isinstance(dictionary[key], dict):
                nu_dict[
                    self._snake_to_camel(key)
                ] = self._keys_to_camel(dictionary[key])
            else:
                nu_dict[
                    self._snake_to_camel(key)
                ] = dictionary[key]
        return nu_dict
