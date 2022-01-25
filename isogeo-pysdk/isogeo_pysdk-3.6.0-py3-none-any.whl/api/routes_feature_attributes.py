#! python3  # noqa E265

"""
    Isogeo API v1 - API Routes for FeatureAttributes entities

    See: http://help.isogeo.com/api/complete/index.html
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging

# submodules
from isogeo_pysdk.checker import IsogeoChecker
from isogeo_pysdk.decorators import ApiDecorators
from isogeo_pysdk.models import FeatureAttribute, Metadata
from isogeo_pysdk.utils import IsogeoUtils

# #############################################################################
# ########## Global #############
# ##################################

logger = logging.getLogger(__name__)
checker = IsogeoChecker()
utils = IsogeoUtils()


# #############################################################################
# ########## Classes ###############
# ##################################
class ApiFeatureAttribute:
    """Routes as methods of Isogeo API used to manipulate feature attributes into a Metadata."""

    def __init__(self, api_client=None):
        if api_client is not None:
            self.api_client = api_client

        # store API client (Request [Oauthlib] Session) and pass it to the decorators
        self.api_client = api_client
        ApiDecorators.api_client = api_client

        # ensure platform and others params to request
        (
            self.platform,
            self.api_url,
            self.app_url,
            self.csw_url,
            self.mng_url,
            self.oc_url,
            self.ssl,
        ) = utils.set_base_url(self.api_client.platform)
        # initialize
        super(ApiFeatureAttribute, self).__init__()

    @ApiDecorators._check_bearer_validity
    def listing(self, metadata: Metadata) -> list:
        """Get all feature-attributes of a metadata.

        :param Metadata metadata: metadata (resource)
        """
        # check metadata type
        if metadata.type != "vectorDataset":
            raise TypeError(
                "Feature attributes routes are only available for metadata of vector datasets, not: {}".format(
                    metadata.type
                )
            )
        else:
            pass
        # URL
        url_feature_attributes = utils.get_request_base_url(
            route="resources/{}/feature-attributes/".format(metadata._id)
        )

        # request
        req_feature_attributes = self.api_client.get(
            url=url_feature_attributes,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_feature_attributes)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_feature_attributes.json()

    @ApiDecorators._check_bearer_validity
    def get(self, metadata_id: str, attribute_id: str) -> FeatureAttribute:
        """Get details about a specific feature-attribute.

        :param str metadata_id: metadata UUID
        :param str attribute_id: feature-attribute UUID

        :Example:

        >>> # get a metadata
        >>> md = isogeo.metadata.get(METADATA_UUID)
        >>> # list all og its attributes
        >>> md_attributes = isogeo.metadata.attributes.listing(md)
        >>> # get the first attribute
        >>> attribute = isogeo.metadata.attributes.get(
            metadata_id=md._id,
            attribute_id=md_attributes[0].get("_id")
            )

        """
        # check metadata UUID
        if not checker.check_is_uuid(metadata_id):
            raise ValueError(
                "Metadata ID is not a correct UUID: {}".format(metadata_id)
            )
        else:
            pass

        # check feature-attribute UUID
        if not checker.check_is_uuid(attribute_id):
            raise ValueError("Features Attribute ID is not a correct UUID.")
        else:
            pass

        # URL
        url_feature_attribute = utils.get_request_base_url(
            route="resources/{}/feature-attributes/{}".format(metadata_id, attribute_id)
        )

        # request
        req_feature_attribute = self.api_client.get(
            url=url_feature_attribute,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            timeout=self.api_client.timeout,
            verify=self.api_client.ssl,
        )

        # checking response
        req_check = checker.check_api_response(req_feature_attribute)
        if isinstance(req_check, tuple):
            return req_check

        # add parent resource id to keep tracking
        feature_attribute_augmented = req_feature_attribute.json()
        feature_attribute_augmented["parent_resource"] = metadata_id

        # end of method
        return FeatureAttribute(**feature_attribute_augmented)

    @ApiDecorators._check_bearer_validity
    def create(
        self, metadata: Metadata, attribute: FeatureAttribute
    ) -> FeatureAttribute:
        """Add a new feature attribute to a metadata (= resource).

        :param Metadata metadata: metadata (resource) to edit
        :param FeatureAttribute attribute: feature-attribute object to create

        :returns: 409 if an attribute with the same name already exists.

        :rtype: FeatureAttribute or tuple

        :Example:

        >>> # retrieve metadata
        >>> md = isogeo.metadata.get(METADATA_UUID)
        >>> # create the attribute locally
        >>> new_attribute = FeatureAttribute(
            alias="Code INSEE de la commune",
            name="INSEE_COM",
            description="Une commune nouvelle résultant d’un regroupement de communes "
            "préexistantes se voit attribuer  le  code  INSEE  de  l’ancienne  commune "
            "désignée  comme  chef-lieu  par  l’arrêté  préfectoral  qui  l’institue. "
            "En  conséquence  une  commune change  de  code  INSEE  si  un  arrêté "
            "préfectoral modifie son chef-lieu.",
            dataType="CharacterString (5)",
            language="fr",
            )
        >>> # add it to the metadata
        >>> isogeo.metadata.attributes.create(md, new_attribute)

        """
        # check metadata type
        if metadata.type != "vectorDataset":
            raise TypeError(
                "Feature attributes routes are only available for metadata of vector datasets, not: {}".format(
                    metadata.type
                )
            )
        else:
            pass

        # check required data
        if not attribute.name:
            raise ValueError("Attribute name is required: {}".format(attribute.name))
        if not attribute.dataType:
            logger.warning(
                ValueError(
                    "Attribute dataType is missing. "
                    "An empty string '\"\"' (but != None) will be used."
                )
            )
            attribute.dataType = ""

        # URL
        url_feature_attribute_create = utils.get_request_base_url(
            route="resources/{}/feature-attributes/".format(metadata._id)
        )

        # request
        req_new_feature_attribute = self.api_client.post(
            url=url_feature_attribute_create,
            json=attribute.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_new_feature_attribute)
        if isinstance(req_check, tuple):
            return req_check

        # add parent resource id to keep tracking
        feature_attribute_augmented = req_new_feature_attribute.json()
        feature_attribute_augmented["parent_resource"] = metadata._id

        # end of method
        return FeatureAttribute(**feature_attribute_augmented)

    @ApiDecorators._check_bearer_validity
    def delete(self, attribute: FeatureAttribute, metadata: Metadata = None):
        """Delete a feature-attribute from a metadata.

        :param FeatureAttribute attribute: FeatureAttribute model object to delete
        :param Metadata metadata: parent metadata (resource) containing the feature-attribute
        """
        # check feature-attribute UUID
        if not checker.check_is_uuid(attribute._id):
            raise ValueError(
                "FeatureAttribute ID is not a correct UUID: {}".format(attribute._id)
            )
        else:
            pass

        # retrieve parent metadata
        if not checker.check_is_uuid(attribute.parent_resource) and not metadata:
            raise ValueError(
                "FeatureAttribute parent metadata is required. Requesting it..."
            )
        elif not checker.check_is_uuid(attribute.parent_resource) and metadata:
            attribute.parent_resource = metadata._id
        else:
            pass

        # URL
        url_feature_attribute_delete = utils.get_request_base_url(
            route="resources/{}/feature-attributes/{}".format(
                attribute.parent_resource, attribute._id
            )
        )

        # request
        req_feature_attribute_deletion = self.api_client.delete(
            url=url_feature_attribute_delete,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            timeout=self.api_client.timeout,
            verify=self.api_client.ssl,
        )

        # checking response
        req_check = checker.check_api_response(req_feature_attribute_deletion)
        if isinstance(req_check, tuple):
            return req_check

        return req_feature_attribute_deletion

    @ApiDecorators._check_bearer_validity
    def update(
        self, attribute: FeatureAttribute, metadata: Metadata = None
    ) -> FeatureAttribute:
        """Update a feature-attribute.

        :param FeatureAttribute attribute: Feature Attribute model object to update
        :param Metadata metadata: parent metadata (resource) containing the feature-attribute
        """
        # check feature-attribute UUID
        if not checker.check_is_uuid(attribute._id):
            raise ValueError(
                "FeatureAttribute ID is not a correct UUID: {}".format(attribute._id)
            )
        else:
            pass

        # retrieve parent metadata
        if not checker.check_is_uuid(attribute.parent_resource) and not metadata:
            raise ValueError(
                "FeatureAttribute parent metadata is required. Requesting it..."
            )
        elif not checker.check_is_uuid(attribute.parent_resource) and metadata:
            attribute.parent_resource = metadata._id
        else:
            pass

        # URL
        url_feature_attribute_update = utils.get_request_base_url(
            route="resources/{}/feature-attributes/{}".format(
                attribute.parent_resource, attribute._id
            )
        )

        # request
        req_feature_attribute_update = self.api_client.put(
            url=url_feature_attribute_update,
            json=attribute.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_feature_attribute_update)
        if isinstance(req_check, tuple):
            return req_check

        # add parent resource id to keep tracking
        feature_attribute_augmented = req_feature_attribute_update.json()
        feature_attribute_augmented["parent_resource"] = attribute.parent_resource

        # end of method
        return FeatureAttribute(**feature_attribute_augmented)

    # -- Extra methods as helpers --------------------------------------------------
    def import_from_dataset(
        self,
        metadata_source: Metadata,
        metadata_dest: Metadata,
        mode: str = "add",
        case_sensitive_matching: bool = True,
    ) -> bool:
        """Import feature-attributes from another vector metadata.

        :param Metadata metadata_source: metadata from which to import the attributes
        :param Metadata metadata_dest: metadata where to import the attributes
        :param str mode: mode of import, defaults to 'add':

            - 'add': add the attributes except those with a duplicated name
            - 'update': update only the attributes with the same name
            - 'update_or_add': update the attributes with the same name or create
        : param bool case_sensitive_matching: False to make featureattributes's name
        matching case-insensitive when mode == "update"

        :raises TypeError: if one metadata is not a vector
        :raises ValueError: if mode is not one of accepted value

        :Example:

        .. code-block:: python

            # get the metadata objects
            md_source = isogeo.metadata.get(METADATA_UUID_SOURCE)
            md_dest = isogeo.metadata.get(METADATA_UUID_DEST)

            # launch import
            isogeo.metadata.attributes.import_from_dataset(md_source, md_dest, "add")
        """
        accepted_modes = ("add", "update", "update_or_add")

        # check metadata type
        if (
            metadata_source.type != "vectorDataset"
            or metadata_dest.type != "vectorDataset"
        ):
            raise TypeError(
                "Feature attributes routes are only available for metadata of vector datasets, not: {} or {}".format(
                    metadata_source.type, metadata_dest.type
                )
            )
        else:
            pass

        # retrieving attributes in source and destination to compare and adapt
        attributes_source = self.listing(metadata_source)
        attributes_dest = self.listing(metadata_dest)
        attributes_dest_names = [attr.get("name") for attr in attributes_dest]
        attributes_dest_names_low = [
            attr.get("name").lower() for attr in attributes_dest
        ]

        # according to the selected mode
        if mode == "add":
            for attribute in attributes_source:
                attribute = FeatureAttribute(**attribute)
                # check if an attribute with the same name already exists and ignore it
                if attribute.name in attributes_dest_names:
                    logger.info(
                        "Attribute with the same name ({}) already exists. It has been ignored.".format(
                            attribute.name
                        )
                    )
                    continue
                # or create it
                self.create(metadata_dest, attribute)
                logger.debug(
                    "Attribute {} has been added to the metadata {}".format(
                        attribute.name, metadata_dest._id
                    )
                )
        elif mode == "update":
            for attribute in attributes_source:
                attr_src = FeatureAttribute(**attribute)
                # check if an attribute with the same name already exists, then update it
                if attr_src.name in attributes_dest_names:
                    attr_dst = FeatureAttribute(
                        **[
                            attr
                            for attr in attributes_dest
                            if attr.get("name") == attr_src.name
                        ][0]
                    )
                elif (
                    attr_src.name.lower() in attributes_dest_names_low
                    and not case_sensitive_matching
                ):
                    attr_dst = FeatureAttribute(
                        **[
                            attr
                            for attr in attributes_dest
                            if attr.get("name").lower() == attr_src.name.lower()
                        ][0]
                    )
                else:
                    continue

                attr_dst.alias = attr_src.alias
                attr_dst.dataType = attr_src.dataType
                attr_dst.description = attr_src.description
                attr_dst.language = attr_src.language
                self.update(metadata=metadata_dest, attribute=attr_dst)
                logger.debug(
                    "Attribute with the same name ({}) spotted. It has been updated.".format(
                        attr_dst.name
                    )
                )
        elif mode == "update_or_add":
            for attribute in attributes_source:
                attr_src = FeatureAttribute(**attribute)
                # check if an attribute with the same name already exists, then update it
                if attr_src.name in attributes_dest_names:
                    attr_dst = FeatureAttribute(
                        **[
                            attr
                            for attr in attributes_dest
                            if attr.get("name") == attr_src.name
                        ][0]
                    )
                    attr_dst.alias = attr_src.alias
                    attr_dst.dataType = attr_src.dataType
                    attr_dst.description = attr_src.description
                    attr_dst.language = attr_src.language
                    self.update(metadata=metadata_dest, attribute=attr_dst)
                    logger.debug(
                        "Attribute with the same name ({}) spotted. It has been updated.".format(
                            attr_dst.name
                        )
                    )
                else:
                    # or create it
                    self.create(metadata_dest, attribute)
        else:
            raise ValueError(
                "Incorrect mode value ({}). Must be one of: {}".format(
                    mode, " | ".join(accepted_modes)
                )
            )

        return True


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    api_feature_attribute = ApiFeatureAttribute()
