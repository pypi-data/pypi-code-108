# Standard library imports
import os

# Internal imports
from rohub import utils
from rohub import settings
from rohub import rohub


class Resource(object):
    """
    Class Representation of Rohub's resource.

    .. note::

        | **editable attributes:**
        | - resource_type
        | - title
        | - folder
        | - description

        | **read-only attributes:**
        | - ros
        | - identifier
        | - name
        | - filename
        | - size
        | - download_url
        | - created
        | - creator
        | - modificator
        | - modified
        | - created_on
        | - created_by
        | - modified_on
        | - modified_by
        | - original_created_on
        | - original_created_by
        | - original_creator_name
        | - authors_credits
        | - contributors_credits
        | - shared
        | - doi
        | - read_only
        | - api_link
    """
    def __init__(self, ro_id=None, source=None, resource_type=None, input_url=None, file_path=None,
                 title=None, folder=None, description=None, identifier=None, post_request=True):
        """
        Constructor for the Resource.

        .. seealso::
            :func:`~rohub.list_valid_resource_types`

        :param ro_id: research object's identifier, optional
        :type ro_id: str
        :param source: resource's source - either internal or external, optional
        :type source: str
        :param resource_type: type of resource, optional
        :type resource_type: str
        :param input_url: resource's url, optional
        :type input_url: str
        :param file_path: resource's file path, optional
        :type file_path: str
        :param title: resource's title, optional
        :type title: str
        :param folder: folder's identifier, optional
        :type folder: str
        :param description: resource's description
        :type description: str
        :param identifier: resource's identifier, optional, used when object already exists and has to be loaded
        :type identifier: str
        :param post_request: if True, the object will be created, otherwise loaded - default is True
        :type post_request: bool
        """
        if self._is_valid():
            # Main.
            self.res_response_content = {}
            self.source = source

            if post_request:
                # Required attributes
                self.ro_id = ro_id   # REGULAR
                self.resource_type = self._validate_resource_type(res_type=str(resource_type))
                self.input_url = input_url   # REGULAR
                self.file_path = file_path   # REGULAR
                # Optional attributes
                self.title = title   # TYPE VALIDATION
                self.folder = folder   # TYPE VALIDATION
                self.description = description   # TYPE VALIDATION
                # Crating new Research Object.
                self._post_resource()
            else:
                self.__identifier = identifier
                # Loading existing Research Object.
                self._load_resource()

            # Updating required attributes with values from the response.
            self.resource_type = self.res_response_content.get("type")
            self.input_url = self.res_response_content.get("url")
            if self.input_url:
                self.source = "external"
            else:
                self.source = "internal"
            self.file_path = self.res_response_content.get("path")

            # Updating optional attributes with values from the response.
            self.title = self.res_response_content.get("title")
            self.folder = self.res_response_content.get("folder")
            self.description = self.res_response_content.get("description")

            # ReadOnly attributes; will be updated after request post.
            self.__ros = self.res_response_content.get("ros")
            self.__identifier = self.res_response_content.get("identifier")
            self.__name = self.res_response_content.get("name")
            self.__filename = self.res_response_content.get("filename")
            self.__size = self.res_response_content.get("size")
            self.__download_url = self.res_response_content.get("download_url")
            self.__created = self.res_response_content.get("created")
            self.__creator = self.res_response_content.get("creator")
            self.__modificator = self.res_response_content.get("modificator")
            self.__modified = self.res_response_content.get("modified")
            self.__created_on = self.res_response_content.get("created_on")
            self.__created_by = self.res_response_content.get("created_by")
            self.__modified_on = self.res_response_content.get("modified_on")
            self.__modified_by = self.res_response_content.get("modified_by")
            self.__original_created_on = self.res_response_content.get("original_created_on")
            self.__original_created_by = self.res_response_content.get("original_created_by")
            self.__original_creator_name = self.res_response_content.get("original_creator_name")
            self.__authors_credits = self.res_response_content.get("authors_credits")
            self.__contributors_credits = self.res_response_content.get("contributors_credits")
            self.__shared = self.res_response_content.get("shared")
            self.__doi = self.res_response_content.get("doi")
            self.__read_only = self.res_response_content.get("read_only")
            self.__api_link = self.res_response_content.get("api_link")

            # Other Attributes.
            self.update_metadata_response_content = None
            self.update_content_response_content = None
            self.delete_response_content = None
            self.assign_doi_response_content = None

            if post_request:
                print(f"Resource was successfully created with id = {self.identifier}")
            else:
                print(f"Resource was successfully loaded with id = {self.identifier}")
        else:
            print('Token is no longer valid! Use login function to generate a new one!')

    def __str__(self):
        return f"Resource with ID: {self.identifier}"

    def __repr__(self):
        return f"Resource(identifier={self.identifier}, post_request=False)"

    ###############################################################################
    #              Properties.                                                    #
    ###############################################################################
    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, value):
        if value:
            self.__title = str(value)
        else:
            self.__title = None

    @property
    def folder(self):
        return self.__folder

    @folder.setter
    def folder(self, value):
        if value:
            self.__folder = str(value)
        else:
            self.__folder = None

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, value):
        if value:
            self.__description = str(value)
        else:
            self.__description = None

    @property
    def identifier(self):
        return self.__identifier

    @identifier.setter
    def identifier(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def ros(self):
        return self.__ros

    @ros.setter
    def ros(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def filename(self):
        return self.__filename

    @filename.setter
    def filename(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def download_url(self):
        return self.__download_url

    @download_url.setter
    def download_url(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def created(self):
        return self.__created

    @created.setter
    def created(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def creator(self):
        return self.__creator

    @creator.setter
    def creator(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def modificator(self):
        return self.__modificator

    @modificator.setter
    def modificator(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def modified(self):
        return self.__modified

    @modified.setter
    def modified(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def created_on(self):
        return self.__created_on

    @created_on.setter
    def created_on(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def created_by(self):
        return self.__created_by

    @created_by.setter
    def created_by(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def modified_on(self):
        return self.__modified_on

    @modified_on.setter
    def modified_on(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def modified_by(self):
        return self.__modified_by

    @modified_by.setter
    def modified_by(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def original_created_on(self):
        return self.__original_created_on

    @original_created_on.setter
    def original_created_on(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def original_created_by(self):
        return self.__original_created_by

    @original_created_by.setter
    def original_created_by(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def original_creator_name(self):
        return self.__original_creator_name

    @original_creator_name.setter
    def original_creator_name(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def authors_credits(self):
        return self.__authors_credits

    @authors_credits.setter
    def authors_credits(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def contributors_credits(self):
        return self.__contributors_credits

    @contributors_credits.setter
    def contributors_credits(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def shared(self):
        return self.__shared

    @shared.setter
    def shared(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def doi(self):
        return self.__doi

    @doi.setter
    def doi(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def read_only(self):
        return self.__read_only

    @read_only.setter
    def read_only(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def api_link(self):
        return self.__api_link

    @api_link.setter
    def api_link(self, value):
        raise AttributeError('This is a read-only attribute!')

    ###############################################################################
    #              Main Methods.                                                  #
    ###############################################################################

    @staticmethod
    def _is_valid():
        """
        Semi-Private function that checks if current token is still valid, and if not it attempts
        to refresh it.
        :return: boolean -> True if valid, False otherwise.
        """
        if utils.is_valid(token_type="access"):
            valid_token = True
        else:
            valid_token = utils.refresh_access_token()
        return valid_token

    def _post_resource(self):
        """
        Semi-private function that creates post request for a resource given
        required and optional parameters.
        """
        if self._is_valid():
            if self.source == "internal":
                url = settings.API_URL + f"ros/{self.ro_id}/resources/"
                data = {"ro": self.ro_id,
                        "folder": self.folder,
                        "type": self.resource_type,
                        "title": self.title,
                        "description": self.description}
                data = {key: value for key, value in data.items() if value is not None}
                r = utils.post_request_with_data_and_file(url=url, data=data, file=self.file_path)
                self.res_response_content = r.json()
            elif self.source == "external":
                url = settings.API_URL + f"ros/{self.ro_id}/resources/"
                data = {"ro": self.ro_id,
                        "folder": self.folder,
                        "type": self.resource_type,
                        "title": self.title,
                        "url": self.input_url,
                        "description": self.description}
                data = {key: value for key, value in data.items() if value is not None}
                r = utils.post_request(url=url, data=data)
                self.res_response_content = r.json()
            else:
                msg = "Unexpected Error: Unrecognized method of Resource creation."
                SystemExit(msg)
        else:
            msg = "Your current access token is either missing or expired, please log into" \
                  " rohub again"
            raise SystemExit(msg)

    def _load_resource(self):
        """
        Semi-private function that creates get request for existing Resource.
        """
        if self._is_valid():
            self.res_response_content = rohub.resource_search_using_id(identifier=self.identifier)
        else:
            msg = "Your current access token is either missing or expired, please log into" \
                  " rohub again"
            raise SystemExit(msg)

    def show_metadata(self):
        """
        Function that shows selected (most relevant) information regarding resource.

        :returns: resource's most relevant metadata
        :rtype: dict
        """
        basic_metadata = {
            "identifier": self.identifier,
            "type": self.resource_type,
            "source": self.source,
            "title": self.title,
            "description": self.description,
            "url": self.input_url,
            "folder": self.folder,
            "path": self.file_path,
            "size": self.size,
            "creator": self.creator,
            "created_on": self.created_on,
            "modified_on": self.modified_on,
            "download_url": self.download_url,
        }
        return basic_metadata

    def show_full_metadata(self):
        """
        Function that shows all metadata associated with the resource.

        :returns: response content from the API
        :rtype: dict
        """
        return self.res_response_content

    def update_metadata(self):
        """
        Function that updates resource's metadata.

        .. note::
            After executing update_metadata the resource will be updated in the service with accordance
            to the changes that were made to the python object in your local scope.

        :returns: response content from the API
        :rtype: dict
        """
        # validating attributes before making a call to the API
        self.resource_type = self._validate_resource_type(res_type=str(self.resource_type))
        # making a call
        self.update_metadata_response_content = rohub.resource_update_metadata(identifier=self.identifier,
                                                                               res_type=self.resource_type,
                                                                               title=self.title,
                                                                               folder=self.folder,
                                                                               description=self.description)
        return self.update_metadata_response_content

    def update_content(self, input_url=None, file_path=None):
        """
        Function that updates resource's content.

        .. note::
            After executing update_content the resource will be updated in the service with accordance
            to the changes that were made to the python object in your local scope.
            In order to update content for internal resource please provide resource through file_path argument.
            In case of external resource an input_url argument should be provided.

        :param input_url: url to the external resource
        :type input_url: str
        :param file_path: path to the internal resource
        :type file_path: str
        :returns: response content from the API
        :rtype: dict
        """
        self.update_content_response_content = rohub.resource_update_content(identifier=self.identifier,
                                                                             input_url=input_url,
                                                                             file_path=file_path)
        return self.update_content_response_content

    def delete(self):
        """
        Function that deletes resource.

        .. warning::
            The resource will be deleted from the service and will no longer appear in the API.
            This doesn't mean that object created in your local scope will be removed!

        :returns: response content from the API
        :rtype: dict
        """
        self.delete_response_content = rohub.resource_delete(identifier=self.identifier)
        return self.delete_response_content

    def assign_doi(self):
        """
        Function that assigns doi to the resource.

        :returns: doi
        :rtype: str
        """
        self.assign_doi_response_content = rohub.resource_assign_doi(identifier=self.identifier)
        return self.assign_doi_response_content

    def download(self, resource_filename, path=None):
        """
        Function that acquires the resource to the local file storage.

        :param resource_filename: resource's full filename (with extension)
        :type resource_filename: str
        :param path: path where file should be downloaded, optional - current working dir is the default!
        :type path: str
        :returns: full path to the acquired resource
        :rtype: str
        """
        return rohub.resource_download(identifier=self.identifier, resource_filename=resource_filename,
                                       path=path)

    ###############################################################################
    #              Required Attributes methods.                                   #
    ###############################################################################

    @staticmethod
    def _validate_resource_type(res_type):
        """
        Semi private function that validates user's input for resource type.
        :param res_type: str -> resource type provided by the user
        :return: str -> validate resource type value.
        """
        if res_type:
            try:
                valid_resource_types = set(rohub.list_valid_resource_types())
                # generating different permutations of user's input that are acceptable
                # i.e small letters, capital letters, title.
                verified_res_type = utils.validate_against_different_formats(input_value=res_type,
                                                                             valid_value_set=valid_resource_types)
                # checking if set contains at least one element
                if len(verified_res_type):
                    # expected behaviour, only one value is correct
                    return verified_res_type[0]
                else:
                    msg = f"Incorrect resource type. Must be one of: {valid_resource_types}"
                    raise SystemExit(msg)
            except KeyError:
                msg = "Something went wrong and we couldn't validate the resource type."
                print(msg)

    @staticmethod
    def _validate_file_path(file_path):
        """
        Semi-private function that validates if user's input for file_path exists.
        :param file_path: str -> path to the input file.
        :return: path to the file if exists, None otherwise.
        """
        if file_path:
            if os.path.isfile(file_path):
                return file_path
            else:
                msg = f"Warning: {file_path} does not point to an existing file!"
                print(msg)
