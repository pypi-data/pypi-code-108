from pydantic import BaseModel
from typing import List, Dict, Callable
from ehelply_bootstrapper.utils.db_encryption import DBEncryption


class eHelplySchema(BaseModel):
    """
    Extended Pydantic base model which adds helper functions for ease of use
    """

    def __init__(self, db_model=None, **kwargs):
        """
        Normal initialization of a Pydantic model.

        However, if a db_model is passed in, it will set up the Pydantic model with default values.

        Still, passing in values manually will OVERRIDE the values from the DB model.

        Args:
            db_model: SQL Alchemy model
            **kwargs:
        """
        if db_model:
            fields_from_model: dict = self.sql_to_pydantic(db_model)
            fields_from_model.update(kwargs)
            kwargs = fields_from_model

        super().__init__(**kwargs)

    def map(self, obj, whitelist: list = None):
        """
        Maps pydantic model values to another object. For example, a SQL Alchemy model.

        If whitelist is specified, it will only map those keys, otherwise, it maps all the keys

        Args:
            obj:
            whitelist:

        Returns:

        """
        my_data: dict = self.dict()
        if whitelist:
            for key in whitelist:
                if key in my_data and my_data[key] is not None:
                    setattr(obj, key, my_data[key])
        else:
            for key, value in my_data.items():
                if value is not None:
                    setattr(obj, key, value)
        return obj

    def pydantic_to_sql(self, obj, whitelist: list = None):
        """
        Alias function to provide a consistent API

        Args:
            obj:
            whitelist:

        Returns:

        """
        return self.map(obj, whitelist)

    def sql_encrypted_fields(self) -> Dict[str, str]:
        """
        Override to specify DB model fields to automatically decrypt.

        Format:
        {
            "field_name": "encryption_field_type"
        }

        Format example:
        {
            "address": "str"
        }

        Returns:

        """
        return {}

    def sql_pre_conversion(self, model: dict) -> dict:
        """
        Override this function to provide defaults and any other pre-processing that is required.

        Args:
            model:

        Returns:

        """
        return model

    def sql_to_pydantic(self, model):
        """
        Converts SQL DB Model from SQL Alchemy to this Pydantic model

        Args:
            model: SQL Alchemy model

        Returns:

        """
        model_dict: dict = model.asdict()

        for field, encrypted_type in self.sql_encrypted_fields().items():
            if field in model_dict:
                model_dict[field] = DBEncryption.decrypt(data=model_dict[field], enc_type=encrypted_type)

        return self.sql_pre_conversion(model_dict)
