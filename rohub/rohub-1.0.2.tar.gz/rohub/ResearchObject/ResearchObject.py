# Internal imports
from rohub import utils
from rohub import settings
from rohub import rohub


class ResearchObject(object):
    """
    Class Representation of Rohub's research object.

    .. note::

        | **editable attributes:**
        | - title
        | - research_areas
        | - description
        | - access_mode
        | - ros_type
        | - template
        | - owner
        | - editors
        | - readers
        | - creation_mode

        | **read-only attributes:**
        | - identifier
        | - shared_link
        | - status
        | - created
        | - creator
        | - modificator
        | - modified
        | - importer
        | - rating
        | - number_of_ratings
        | - number_of_likes
        | - number_of_dislikes
        | - quality
        | - size
        | - doi
        | - api_link
        | - created_by
        | - metadata
        | - contributors_credits
        | - authors_credits
        | - number_of_all_aggregates
        | - number_of_resources
        | - original_created_on
        | - parent_ro
        | - contributed_by
        | - number_of_views
        | - number_of_forks
        | - authored_by
        | - snapshotter
        | - user_liked
        | - cloned
        | - archived
        | - contributors
        | - geolocation
        | - read_only
        | - created_on
        | - credits
        | - forker
        | - number_of_downloads
        | - number_of_folders
        | - original_created_by
        | - golden
        | - archiver
        | - forked
        | - number_of_events
        | - modified_on
        | - sketch
        | - user_rate
        | - modified_by
        | - original_creator_name
        | - imported
        | - snapshotted
        | - number_of_archives
        | - quality_calculated_on
        | - user_disliked
        | - number_of_snapshots
        | - number_of_annotations
        | - number_of_comments
        | - content
        | - annotations
    """
    def __init__(self, title=None, research_areas=None, description=None, access_mode=None,
                 ros_type=None, use_template=False, owner=None, editors=None,
                 readers=None, creation_mode=None, identifier=None, post_request=True):
        """
        Constructor for the ResearchObject.

        .. seealso::
            | :func:`~rohub.list_valid_research_areas`
            | :func:`~rohub.list_valid_access_modes`
            | :func:`~rohub.list_valid_ros_types`
            | :func:`~rohub.list_valid_templates`
            | :func:`~rohub.list_valid_creation_modes`

        :param title: title of your research object, optional
        :type title: str
        :param research_areas: research areas associated with your research object, optional
        :type research_areas: list
        :param description: description of your research object, optional
        :type description: str
        :param access_mode: research object's access mode, optional
        :type access_mode: str
        :param ros_type: research object's type, optional
        :type ros_type: str
        :param use_template: if True appropriate template for ro type will be used, optional
        :type use_template: bool
        :param owner: research object's owner, optional
        :type owner: str
        :param editors: research object's editors, optional
        :type editors: list
        :param readers: research object's readers, optional
        :type readers: list
        :param creation_mode: research object's creation mode, optional
        :type creation_mode: str
        :param identifier: research object's identifier, optional, used when object already exists and has to be loaded
        :type identifier: str
        :param post_request: if True, the object will be created, otherwise loaded - default is True
        :type post_request: bool
        """
        if self._is_valid():
            # Main.
            self.roi_response_content = {}

            if post_request:
                # Required attributes
                self.title = title   # TYPE VALIDATION
                self.research_areas = self._validate_research_areas(research_areas=research_areas)
                # Optional attributes with default value.
                self.description = description   # TYPE VALIDATION
                self.owner = owner   # TYPE VALIDATION
                if access_mode:
                    self.access_mode = self._validate_and_set_access_mode(access_mode=str(access_mode))
                else:
                    self.access_mode = None
                if ros_type:
                    self.ros_type = self._validate_and_set_ros_type(ros_type=str(ros_type))
                else:
                    self.ros_type = None
                # additional validation for matching template with ro_type
                if use_template:
                    # self._validate_type_matching(template=template)
                    # self.template = self._validate_and_set_template(template=str(template))
                    self.template = self._assign_template()
                else:
                    self.template = None
                self.editors = editors   # TYPE VALIDATION
                self.readers = readers   # TYPE VALIDATION
                if creation_mode:
                    self.creation_mode = self._validate_and_set_creation_mode(creation_mode=str(creation_mode))
                else:
                    self.creation_mode = None

                # Crating new Research Object.
                self._post_research_object()
            else:
                self.__identifier = identifier
                # Loading existing Research Object.
                self._load_research_object()

            # Updating required attributes with values from the response.
            self.title = self.roi_response_content.get("title")
            self.research_areas = self.roi_response_content.get("research_areas")

            # Updating optional attributes with values from the response.
            self.description = self.roi_response_content.get("description")
            self.access_mode = self.roi_response_content.get("access_mode")
            self.ros_type = self.roi_response_content.get("type")
            self.template = self.roi_response_content.get("template")
            self.owner = self.roi_response_content.get("owner")
            self.editors = self.roi_response_content.get("editors")
            self.readers = self.roi_response_content.get("readers")
            self.creation_mode = self.roi_response_content.get("creation_mode")

            # ReadOnly attributes; will be updated after request post.
            self.__identifier = self.roi_response_content.get("identifier")
            self.__shared_link = self.roi_response_content.get("shared_link")
            self.__status = self.roi_response_content.get("status")
            self.__created = self.roi_response_content.get("created")
            self.__creator = self.roi_response_content.get("creator")
            self.__modificator = self.roi_response_content.get("modificator")
            self.__modified = self.roi_response_content.get("modified")
            self.__importer = self.roi_response_content.get("importer")
            self.__rating = self.roi_response_content.get("rating")
            self.__number_of_ratings = self.roi_response_content.get("number_of_ratings")
            self.__number_of_likes = self.roi_response_content.get("number_of_likes")
            self.__number_of_dislikes = self.roi_response_content.get("number_of_dislikes")
            self.__quality = self.roi_response_content.get("quality")
            self.__size = self.roi_response_content.get("size")
            self.__doi = self.roi_response_content.get("doi")
            self.__api_link = self.roi_response_content.get("api_link")

            # Full Meta-Data.
            self.created_by = None
            self.metadata = None
            self.contributors_credits = None
            self.authors_credits = None
            self.number_of_all_aggregates = None
            self.number_of_resources = None
            self.original_created_on = None
            self.parent_ro = None
            self.contributed_by = None
            self.number_of_views = None
            self.number_of_forks = None
            self.authored_by = None
            self.snapshotter = None
            self.user_liked = None
            self.cloned = None
            self.archived = None
            self.contributors = None
            self.geolocation = None
            self.read_only = None
            self.created_on = None
            self.credits = None
            self.forker = None
            self.number_of_downloads = None
            self.number_of_folders = None
            self.original_created_by = None
            self.golden = None
            self.archiver = None
            self.forked = None
            self.number_of_events = None
            self.modified_on = None
            self.sketch = None
            self.user_rate = None
            self.modified_by = None
            self.original_creator_name = None
            self.imported = None
            self.snapshotted = None
            self.number_of_archives = None
            self.quality_calculated_on = None
            self.user_disliked = None
            self.number_of_snapshots = None
            self.number_of_annotations = None
            self.number_of_comments = None

            # Other Attributes.
            self.content = None
            self.geolocation_response_content = None
            self.folders_response_content = None
            self.resource_upload_response_content = None
            self.annotations_response_content = None
            self.fork_response_content = None
            self.snapshot_response_content = None
            self.archive_response_content = None
            self.delete_response_content = None
            self.update_response_content = None
            self.full_metadata_response_content = None
            self.show_publication_response_content = None

            # Curated data.
            self.annotations = None

            if post_request:
                print(f"Research Object was successfully created with id = {self.identifier}")
            else:
                print(f"Research Object was successfully loaded with id = {self.identifier}")
        else:
            print('Token is no longer valid! Use login function to generate a new one!')

    def __str__(self):
        return f"Research Object with ID: {self.identifier}"

    def __repr__(self):
        return f"ResearchObject(identifier={self.identifier}, post_request=False)"

    ###############################################################################
    #              Properties.                                                    #
    ###############################################################################
    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, value):
        self.__title = str(value)

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
    def owner(self):
        return self.__owner

    @owner.setter
    def owner(self, value):
        if value:
            self.__owner = str(value)
        else:
            self.__owner = None

    @property
    def editors(self):
        return self.__editors

    @editors.setter
    def editors(self, value):
        if value:
            self.__editors = list(value)
        else:
            self.__editors = None

    @property
    def readers(self):
        return self.__readers

    @readers.setter
    def readers(self, value):
        if value:
            self.__readers = list(value)
        else:
            self.__readers = None

    @property
    def identifier(self):
        return self.__identifier

    @identifier.setter
    def identifier(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def shared_link(self):
        return self.__shared_link

    @shared_link.setter
    def shared_link(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
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
    def importer(self):
        return self.__importer

    @importer.setter
    def importer(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def rating(self):
        return self.__rating

    @rating.setter
    def rating(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def number_of_ratings(self):
        return self.__number_of_ratings

    @number_of_ratings.setter
    def number_of_ratings(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def number_of_likes(self):
        return self.__number_of_likes

    @number_of_likes.setter
    def number_of_likes(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def number_of_dislikes(self):
        return self.__number_of_dislikes

    @number_of_dislikes.setter
    def number_of_dislikes(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def quality(self):
        return self.__quality

    @quality.setter
    def quality(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, value):
        raise AttributeError('This is a read-only attribute!')

    @property
    def doi(self):
        return self.__doi

    @doi.setter
    def doi(self, value):
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

    def _post_research_object(self):
        """
        Semi-private function that creates post request for a research object given
        required and optional parameters.
        """
        data = {"title": self.title,
                "research_areas": self.research_areas,
                "description": self.description,
                "access_mode": self.access_mode,
                "type": self.ros_type,
                "template": self.template,
                "owner": self.owner,
                "editors": self.editors,
                "readers": self.readers,
                "creation_mode": self.creation_mode}
        data = {key: value for key, value in data.items() if value is not None}
        if self._is_valid():
            r = utils.post_request(url=settings.API_URL + "ros/", data=data)
            self.roi_response_content = r.json()
        else:
            msg = "Your current access token is either missing or expired, please log into" \
                  " rohub again"
            raise SystemExit(msg)

    def _load_research_object(self):
        """
        Semi-private function that creates get request for existing Research Object.
        """
        if self._is_valid():
            self.roi_response_content = rohub.ros_search_using_id(identifier=self.identifier)
        else:
            msg = "Your current access token is either missing or expired, please log into" \
                  " rohub again"
            raise SystemExit(msg)

    def get_content(self):
        """
        Function that loads content related to the research object.

        .. note::
            result is accessible through content attribute after the execution

        :returns: None
        :rtype: None
        """
        self.content = rohub.ros_content(identifier=self.identifier)

    def load_full_metadata(self):
        """
        Function that loads full meta information of research object.

        .. seealso::
            :func:`~show_full_metadata`

        .. note::
            | results are accessible in two ways:
            | **1) API's response which can be displayed using show_full_metadata**
            | **2) Accessing a single attribute containing a piece of metadata**
            | - created_by
            | - metadata
            | - contributors_credits
            | - authors_credits
            | - number_of_all_aggregates
            | - number_of_resources
            | - original_created_on
            | - parent_ro
            | - contributed_by
            | - number_of_views
            | - number_of_forks
            | - authored_by
            | - snapshotter
            | - user_liked
            | - cloned
            | - archived
            | - contributors
            | - geolocation
            | - read_only
            | - created_on
            | - credits
            | - forker
            | - number_of_downloads
            | - number_of_folders
            | - original_created_by
            | - golden
            | - archiver
            | - forked
            | - number_of_events
            | - modified_on
            | - sketch
            | - user_rate
            | - modified_by
            | - original_creator_name
            | - imported
            | - snapshotted
            | - number_of_archives
            | - quality_calculated_on
            | - user_disliked
            | - number_of_snapshots
            | - number_of_annotations
            | - number_of_comments

        :returns: None
        """
        self.full_metadata_response_content = rohub.ros_full_metadata(identifier=self.identifier)
        self.created_by = self.full_metadata_response_content.get("created_by")
        self.metadata = self.full_metadata_response_content.get("metadata")
        self.contributors_credits = self.full_metadata_response_content.get("contributors_credits")
        self.authors_credits = self.full_metadata_response_content.get("authors_credits")
        self.number_of_all_aggregates = self.full_metadata_response_content.get("number_of_all_aggregates")
        self.number_of_resources = self.full_metadata_response_content.get("number_of_resources")
        self.original_created_on = self.full_metadata_response_content.get("original_created_on")
        self.parent_ro = self.full_metadata_response_content.get("parent_ro")
        self.contributed_by = self.full_metadata_response_content.get("contributed_by")
        self.number_of_views = self.full_metadata_response_content.get("number_of_views")
        self.number_of_forks = self.full_metadata_response_content.get("number_of_forks")
        self.authored_by = self.full_metadata_response_content.get("authored_by")
        self.snapshotter = self.full_metadata_response_content.get("snapshotter")
        self.user_liked = self.full_metadata_response_content.get("user_liked")
        self.cloned = self.full_metadata_response_content.get("cloned")
        self.archived = self.full_metadata_response_content.get("archived")
        self.contributors = self.full_metadata_response_content.get("contributors")
        self.geolocation = self.full_metadata_response_content.get("geolocation")
        self.read_only = self.full_metadata_response_content.get("read_only")
        self.created_on = self.full_metadata_response_content.get("created_on")
        self.credits = self.full_metadata_response_content.get("credits")
        self.forker = self.full_metadata_response_content.get("forker")
        self.number_of_downloads = self.full_metadata_response_content.get("number_of_downloads")
        self.number_of_folders = self.full_metadata_response_content.get("number_of_folders ")
        self.original_created_by = self.full_metadata_response_content.get("original_created_by")
        self.golden = self.full_metadata_response_content.get("golden")
        self.archiver = self.full_metadata_response_content.get("archiver")
        self.forked = self.full_metadata_response_content.get("forked")
        self.number_of_events = self.full_metadata_response_content.get("number_of_events")
        self.modified_on = self.full_metadata_response_content.get("modified_on")
        self.sketch = self.full_metadata_response_content.get("sketch")
        self.user_rate = self.full_metadata_response_content.get("user_rate")
        self.modified_by = self.full_metadata_response_content.get("modified_by")
        self.original_creator_name = self.full_metadata_response_content.get("original_creator_name")
        self.imported = self.full_metadata_response_content.get("imported")
        self.snapshotted = self.full_metadata_response_content.get("snapshotted")
        self.number_of_archives = self.full_metadata_response_content.get("number_of_archives")
        self.quality_calculated_on = self.full_metadata_response_content.get("quality_calculated_on")
        self.user_disliked = self.full_metadata_response_content.get("user_disliked")
        self.number_of_snapshots = self.full_metadata_response_content.get("number_of_snapshots")
        self.number_of_annotations = self.full_metadata_response_content.get("number_of_annotations")
        self.number_of_comments = self.full_metadata_response_content.get("number_of_comments")

    def show_metadata(self):
        """
        Function that displays basic metadata information associated with the research object.

        :returns: response content from the API
        :rtype: dict
        """
        return self.roi_response_content

    def show_full_metadata(self):
        """
        Function that displays full metadata information associated with the research object.

        .. seealso::
            :func:`~load_full_metadata`

        :returns: response content from the API
        :rtype: dict
        """
        if self.full_metadata_response_content:
            return self.full_metadata_response_content
        else:
            print("To access full metadata for the object, please use load_full_metadata method first followed"
                  " by the current method to display it.")

    def list_resources(self):
        """
        Function that lists resources that are associated with the research object.

        :returns: table containing selected information about all associated resources
        :rtype: Panda's DataFrame
        """
        return rohub.ros_list_resources(identifier=self.identifier)

    def add_geolocation(self, body_specification_json=None):
        """
        Function that adds geolocation to the research object.

        :param body_specification_json: path to the JSON file or Python serializable object (dict, list), optional
        :type body_specification_json: str/dict/list
        :returns: response content from the API
        :rtype: dict
        """
        self.geolocation_response_content = rohub.ros_add_geolocation(identifier=self.identifier,
                                                                      body_specification_json=body_specification_json)
        return self.geolocation_response_content

    def add_folders(self, name, description=None, parent_folder=None):
        """
        Function that adds folders to the research object.

        :param name: folder's name
        :type name: str
        :param description: folder's description, optional
        :type description: str
        :param parent_folder: parent folder identifier, optional
        :type parent_folder: str
        :returns: response content from the API
        :rtype: dict
        """
        self.folders_response_content = rohub.ros_add_folders(identifier=self.identifier,
                                                              name=name,
                                                              description=description,
                                                              parent_folder=parent_folder)
        return self.folders_response_content

    def add_resource_from_zip(self, path_to_zip):
        """
        Function that adds resource from the zip package to the research object.

        :param path_to_zip: path to the existing zip package
        :type path_to_zip: str
        :returns: response content from the API
        :rtype: dict
        """
        self.resource_upload_response_content = rohub.ros_upload_resources(identifier=self.identifier,
                                                                           path_to_zip=path_to_zip)
        return self.resource_upload_response_content

    def add_internal_resource(self, res_type, file_path, title=None, folder=None, description=None):
        """
        Function that adds internal resource to the research object.

        .. seealso::
            :func:`~rohub.list_valid_resource_types`

        .. note::
            The newly created resource object will return a Python object that has its own set of methods
            and attributes. You may want to assign it to a variable to make it easy to work with.
            For example: ``my_res = ros_add_internal_resource(**your set of params)``

        :param res_type: type of resource
        :type res_type: str
        :param file_path: resource's file path
        :type file_path: str
        :param title: resource's title, optional
        :type title: str
        :param folder: folder's identifier, optional
        :type folder: str
        :param description: resource's description
        :type description: str
        :returns: newly created resource object
        :rtype: Resource
        """
        resource = rohub.ros_add_internal_resource(identifier=self.identifier, res_type=res_type,
                                                   file_path=file_path, title=title, folder=folder,
                                                   description=description)
        return resource

    def add_external_resource(self, res_type, input_url, title=None, folder=None, description=None):
        """
        Function that adds external resource to the research object.

        .. seealso::
            :func:`~rohub.list_valid_resource_types`

        .. note::
            The newly created resource object will return a Python object that has its own set of methods
            and attributes. You may want to assign it to a variable to make it easy to work with.
            For example: ``my_res = ros_add_external_resource(**your set of params)``

        :param res_type: type of resource
        :type res_type: str
        :param input_url: resource's url
        :type input_url: str
        :param title: resource's title, optional
        :type title: str
        :param folder: folder's identifier, optional
        :type folder: str
        :param description: resource's description
        :type description: str
        :returns: newly created resource object
        :rtype: Resource
        """
        resource = rohub.ros_add_external_resource(identifier=self.identifier, res_type=res_type,
                                                   input_url=input_url, title=title, folder=folder,
                                                   description=description)
        return resource

    def add_annotations(self, resources=None, body_specification_json=None):
        """
        Function that adds annotations to the research object.

        :param resources: resources to which annotations will be applied, optional
        :type resources: list
        :param body_specification_json: path to the JSON file or Python serializable object (dict, list), optional
        :type body_specification_json: str/dict/list
        :returns: response content from the API
        :rtype: dict
        """
        self.annotations_response_content = rohub.ros_add_annotations(identifier=self.identifier,
                                                                      resources=resources,
                                                                      body_specification_json=body_specification_json)
        return self.annotations_response_content

    def add_triple(self, the_subject, the_predicate, the_object, annotation_id, object_class=None):
        """
        Function that adds triple to the annotations and validates if annotations are associated with research object.

        .. seealso::
            :func:`~rohub.list_triple_object_classes`

        :param the_subject: triple's subject
        :type the_subject: str
        :param the_predicate: triple's predicate
        :type the_predicate: str
        :param the_object: triple's object
        :type the_object: str
        :param annotation_id: annotation's identifier
        :type annotation_id: str
        :param object_class: object's class, optional
        :type object_class: str
        :returns: response content from the API
        :rtype: dict
        """
        if not self.annotations:
            self.list_annotations()
        # validating if annotations belongs to the current ros.
        validated_annotations = [result for result in self.annotations if result["identifier"] == annotation_id]
        if not validated_annotations:
            print(f"Annotation with given id {annotation_id} doesn't belong to the research object "
                  f"you are currently working with!")
        else:
            if len(validated_annotations) > 1:
                print("Unexpected behaviour, more than one annotation with the same id belongs to the"
                      " current Research Object! Please be aware of that.")
            r = rohub.ros_add_triple(the_subject=the_subject, the_predicate=the_predicate,
                                     the_object=the_object, annotation_id=annotation_id, object_class=object_class)
            return r

    def set_authors(self, agents):
        """
        Function that sets authors to the research object.

        :param agents: usernames representing authors, if one doesn't exist it will be automatically created
        :type agents: list
        :returns: response content from the API
        :rtype: dict
        """
        return rohub.ros_set_authors(identifier=self.identifier, agents=agents)

    def set_contributors(self, agents):
        """
        Function that sets contributors to the research object.

        :param agents: usernames representing contributors, if one doesn't exist it will be automatically created
        :type agents: list
        :returns: response content from the API
        :rtype: dict
        """
        return rohub.ros_set_contributors(identifier=self.identifier, agents=agents)

    def set_publishers(self, agents):
        """
        Function that sets publishers to the research object.

        :param agents: usernames/organizations representing publishers, if one doesn't exist it will be automatically created
        :type agents: list
        :returns: response content from the API
        :rtype: dict
        """
        return rohub.ros_set_publishers(identifier=self.identifier, agents=agents)

    def set_copyright_holders(self, agents):
        """
        Function that sets copyright holders to the research object.

        :param agents: usernames/organizations representing holders, if one doesn't exist it will be automatically created
        :type agents: list
        :returns: response content from the API
        :rtype: dict
        """
        return rohub.ros_set_copyright_holders(identifier=self.identifier, agents=agents)

    def add_funding(self, grant_identifier, grant_name, funder_name, grant_title=None, funder_doi=None):
        """
        Function that adds funding information to the research object.

        .. note::
            two auxiliary functions can be used to get some examples for funders and grants from the Zenodo database,
            respectively:
            :func:`~rohub.zenodo_list_funders`
            :func:`~rohub.zenodo_list_grants`
            check documentation of the above to get usage details

        :param grant_identifier: grant's identifier
        :type grant_identifier: str
        :param grant_name: grant's name
        :type grant_name: str
        :param funder_name: funder's name
        :type funder_name: str
        :param grant_title: grant's title, optional
        :type grant_title: str
        :param funder_doi: funder's doi, optional
        :type funder_doi: str
        :returns: service identifier for the newly created funding
        :rtype: str
        """
        return rohub.ros_add_funding(identifier=self.identifier, grant_name=grant_name, funder_name=funder_name,
                                     grant_identifier=grant_identifier, grant_title=grant_title,
                                     funder_doi=funder_doi)

    def set_license(self, license_id):
        """
        Function that sets license information to the research object.

        :param license_id: license's identifier
        :type license_id: str
        :returns: response content from the API
        :rtype: dict
        """
        return rohub.ros_set_license(ros_id=self.identifier, license_id=license_id)

    def fork(self, title=None, description=None):
        """
        Function that creates research object's fork.

        :param title: fork title, optional
        :type title: str
        :param description: fork description, optional
        :type description: str
        :returns: fork identifier
        :rtype: str
        """
        self.fork_response_content = rohub.ros_fork(identifier=self.identifier,
                                                    description=description,
                                                    title=title)
        return self.fork_response_content

    def snapshot(self, title=None, description=None, create_doi=None,
                 external_doi=None, publication_services=None):
        """
        Function that creates research object's snapshot.

        .. seealso::
            :func:`~rohub.list_valid_publication_services`

        .. note::
            if one chooses to use doi it can be provided in two ways:
            1) through setting create_doi to True, then doi will be generated for you
            2) through passing your doi using external_doi parameter
            create_doi = True and external_doi are mutually exclusive, therefore
            they can't be used simultaneously!

        .. warning::
            user needs to make sure that he has service credentials associated with his profile
            for the publication services that he would like to use!
            If that is not the case, warning will be shown and the ros will not be published as intended!

        :param title: snapshot title, optional
        :type title: str
        :param description: snapshot description, optional
        :type description: str
        :param create_doi: doi is created if True, False otherwise, optional, False is the default
        :type create_doi: bool
        :param external_doi: existing doi value that will be associated with the snapshot, optional
        :type external_doi: str
        :param publication_services: services where the snapshot should be published into
        :type publication_services: list
        :returns: snapshot identifier
        :rtype: str
        """
        self.snapshot_response_content = rohub.ros_snapshot(identifier=self.identifier,
                                                            description=description,
                                                            create_doi=create_doi,
                                                            external_doi=external_doi,
                                                            title=title,
                                                            publication_services=publication_services)
        return self.snapshot_response_content

    def archive(self, title=None, description=None, create_doi=None,
                external_doi=None, publication_services=None):
        """
        Function that creates research object's archive.

        .. seealso::
            :func:`~rohub.list_valid_publication_services`

        .. note::
            if one chooses to use doi it can be provided in two ways:
            1) through setting create_doi to True, then doi will be generated for you
            2) through passing your doi using external_doi parameter
            create_doi = True and external_doi are mutually exclusive, therefore
            they can't be used simultaneously!

        .. warning::
            user needs to make sure that he has service credentials associated with his profile
            for the publication services that he would like to use!
            If that is not the case, warning will be shown and the ros will not be published as intended!

        :param title: archive title, optional
        :type title: str
        :param description: archive description, optional
        :type description: str
        :param create_doi: doi is created if True, False otherwise, optional, False is the default
        :type create_doi: bool
        :param external_doi: existing doi value that will be associated with the snapshot, optional
        :type external_doi: str
        :param publication_services: services where the archive should be published into
        :type publication_services: list
        :returns: archive identifier
        :rtype: str
        """
        self.archive_response_content = rohub.ros_snapshot(identifier=self.identifier,
                                                           description=description,
                                                           create_doi=create_doi,
                                                           external_doi=external_doi,
                                                           title=title,
                                                           publication_services=publication_services)
        return self.archive_response_content

    def delete(self):
        """
        Function that deletes Research Object.

        .. warning::
            The research object will be deleted from the service and will no longer appear in the API.
            This doesn't mean that object created in your local scope will be removed!

        :returns: response content from the API
        :rtype: dict
        """
        self.delete_response_content = rohub.ros_delete(identifier=self.identifier)
        return self.delete_response_content

    def delete_funding(self, funding_identifier):
        """
        Function that deletes specific funding associated with research object.

        :param funding_identifier: funding's identifier
        :type funding_identifier: str
        :returns: response content from the API
        :rtype: dict
        """
        return rohub.ros_delete_funding(identifier=self.identifier, funding_identifier=funding_identifier)

    def delete_license(self):
        """
        Function that deletes association between license and research object.
        :returns: response content from the API
        :rtype: dict
        """
        return rohub.ros_delete_license(identifier=self.identifier)

    def update(self):
        """
        Function for updating research object in the service.

        .. note::
            After executing update the research object will be updated in the service with accordance
            to the changes that were made to the python object in your local scope.

        :returns: response content from the API
        :rtype: dict
        """
        # validating attributes before making a call to the API
        self.research_areas = self._validate_research_areas(research_areas=self.research_areas)
        if self.access_mode:
            self.access_mode = self._validate_and_set_access_mode(access_mode=str(self.access_mode))
        if self.ros_type:
            self._validate_and_set_ros_type(ros_type=str(self.ros_type))
        if self.template:
            self._validate_type_matching(template=self.template)
            self._validate_and_set_template(template=str(self.template))
        if self.creation_mode:
            self._validate_and_set_creation_mode(creation_mode=str(self.creation_mode))
        # making a call
        self.update_response_content = rohub.ros_update(identifier=self.identifier,
                                                        title=self.title,
                                                        research_areas=self.research_areas,
                                                        description=self.description,
                                                        access_mode=self.access_mode,
                                                        ros_type=self.ros_type,
                                                        template=self.template,
                                                        owner=self.owner,
                                                        editors=self.editors,
                                                        readers=self.readers,
                                                        creation_mode=self.creation_mode)
        return self.update_response_content

    def update_funding(self, funding_identifier, grant_identifier=None, grant_name=None,
                       grant_title=None, funder_doi=None, funder_name=None):
        """
        Function that updates specific funding associated with research object.

        .. seealso::
            :func:`~list_fundings`

        :param funding_identifier: funding's identifier
        :type funding_identifier: str
        :param grant_identifier: grant's identifier, optional
        :type grant_identifier: str
        :param grant_name: grant's name, optional
        :type grant_name: str
        :param funder_name: funder's name, optional
        :type funder_name: str
        :param grant_title: grant's title, optional
        :type grant_title: str
        :param funder_doi: funder's doi, optional
        :type funder_doi: str
        :returns: response content from the API
        :rtype: dict
        """
        return rohub.ros_update_funding(identifier=self.identifier, funding_identifier=funding_identifier,
                                        grant_identifier=grant_identifier, grant_name=grant_name,
                                        grant_title=grant_title, funder_doi=funder_doi,
                                        funder_name=funder_name)

    def list_publications(self):
        """
        Function that lists publication details related to the research object.

        :return: set of selected information regarding each publication
        :rtype: list
        """
        self.show_publication_response_content = rohub.ros_list_publications(identifier=self.identifier)
        return self.show_publication_response_content

    def list_annotations(self):
        """
        Function that lists all annotations associated with the research object.

        :return: set of selected information regarding each annotation
        :rtype: list
        """
        data = rohub.ros_list_annotations(identifier=self.identifier)
        self.annotations = data
        return self.annotations

    def list_triples(self, identifier):
        """
        Function that lists all triples related to a specific annotation that is a part of research object.

        .. warning::
            If provided annotation is not a part of research object the error will be thrown!

        :param identifier: annotation's identifier
        :type identifier: str
        :return: set of selected information regarding each triple
        :rtype: list
        """
        if not self.annotations:
            self.list_annotations()
        # validating if annotations belongs to the current ros.
        validated_annotations = [result for result in self.annotations if result["identifier"] == identifier]
        if not validated_annotations:
            print(f"Annotation with given id {identifier} doesn't belong to the research object "
                  f"you are currently working with!")
        else:
            if len(validated_annotations) > 1:
                print("Unexpected behaviour, more than one annotation with the same id belongs to the"
                      " current Research Object! Please be aware of that.")
            data = rohub.ros_list_triples(identifier=identifier)
            return data

    def list_folders(self):
        """
        Function that lists folders associated with research object.

        :returns: table containing selected information about all associated folders
        :rtype: Panda's DataFrame
        """
        return rohub.ros_list_folders(identifier=self.identifier)

    def list_authors(self):
        """
        Function that lists authors associated with the research object.

        :returns: response containing authors details
        :rtype: dict
        """
        return rohub.ros_list_authors(identifier=self.identifier)

    def list_contributors(self):
        """
        Function that lists contributors associated with the research object.

        :returns: response containing contributors details
        :rtype: dict
        """
        return rohub.ros_list_contributors(identifier=self.identifier)

    def list_copyright(self):
        """
        Function that lists copyrights associated with the research object.

        :returns: response containing copyright details
        :rtype: dict
        """
        return rohub.ros_list_copyright(identifier=self.identifier)

    def list_fundings(self):
        """
        Function that lists fundings associated with the research object.

        :returns: response containing fundings details
        :rtype: dict
        """
        return rohub.ros_list_fundings(identifier=self.identifier)

    def list_license(self):
        """
        Function that lists license associated with the research object.

        :returns: response containing license details
        :rtype: dict
        """
        return rohub.ros_list_license(identifier=self.identifier)

    def export_to_rocrate(self, filename=None, path=None, use_format=settings.EXPORT_TO_ROCRATE_DEFAULT_FORMAT):
        """
        Function for downloading research object metadata as RO-crate.

        :param filename: plain filename without extension, optional - if not provided username will be used instead
        :type filename: str
        :param path: folder path to where file should be downloaded, optional - default is current working directory
        :type path: str
        :param use_format: format choice for acquired data - either json-ld or zip
        :type use_format: str
        :returns: None
        """
        rohub.ros_export_to_rocrate(identifier=self.identifier, filename=filename, path=path,
                                    use_format=use_format)

    ###############################################################################
    #              Required Attributes methods.                                   #
    ###############################################################################

    @staticmethod
    def _validate_research_areas(research_areas):
        """
        Semi private function that validates user's input for research areas.
        :param research_areas: list -> list of research areas provided by the user.
        :return: list -> list of valid research areas.
        """
        if isinstance(research_areas, list):
            valid_research_areas = set(rohub.list_valid_research_areas())
            validated = []
            for candidate in research_areas:
                validated.extend(utils.validate_against_different_formats(candidate, valid_research_areas))
            return validated
        else:
            msg = f"Aborting: research_areas parameter should be a list and not {type(research_areas)}!"
            raise SystemExit(msg)

    ###############################################################################
    #              Optional Attributes methods.                                   #
    ###############################################################################

    @staticmethod
    def _validate_and_set_access_mode(access_mode):
        """
        Semi-private function for validating and setting access mode attribute.
        :param access_mode: str -> access
        :return: str -> access mode value.
        """
        try:
            valid_access_modes = set(rohub.list_valid_access_modes())
            verified_access_mode = utils.validate_against_different_formats(input_value=access_mode,
                                                                            valid_value_set=valid_access_modes)
            # checking if set contains at least one element
            if len(verified_access_mode):
                # expected behaviour, only one value is correct
                return verified_access_mode[0]
            else:
                msg = f"Incorrect access mode. Must be one of: {valid_access_modes}"
                raise SystemExit(msg)
        except KeyError as e:
            print("Wasn't able to validate values for access_mode. Leaving it"
                  " empty as per default. Please try adjust this using generated"
                  " ResearchObject later.")
            print(e)
            return None

    @staticmethod
    def _validate_and_set_ros_type(ros_type):
        """
        Semi-private function for validating and setting ros type attribute.
        :param ros_type: str -> ros type.
        :return: str -> ros type value.
        """
        try:
            valid_ros_type = set(rohub.list_valid_ros_types())
            verified_ros_type = utils.validate_against_different_formats(input_value=ros_type,
                                                                         valid_value_set=valid_ros_type)
            # checking if set contains at least one element
            if len(verified_ros_type):
                # expected behaviour, only one value is correct
                return verified_ros_type[0]
            else:
                msg = f"Incorrect ros type. Must be one of: {valid_ros_type}"
                raise SystemExit(msg)
        except KeyError as e:
            print("Wasn't able to validate values for ros_type. Leaving it"
                  " empty as per default. Please try adjust this using generated"
                  " ResearchObject later.")
            print(e)
            return None

    @staticmethod
    def _validate_and_set_template(template):
        """
        Semi-private function for validating and setting template attribute.
        :param template: str -> template type.
        :return: str -> template value.
        """
        try:
            valid_templates = set(rohub.list_valid_templates())
            verified_templates = utils.validate_against_different_formats(input_value=template,
                                                                          valid_value_set=valid_templates)
            # checking if set contains at least one element
            if len(verified_templates):
                # expected behaviour, only one value is correct
                return verified_templates[0]
            else:
                msg = f"Incorrect template. Must be one of: {valid_templates}"
                raise SystemExit(msg)
        except KeyError as e:
            print("Wasn't able to validate values for template. Leaving it"
                  " empty as per default. Please try adjust this using generated"
                  " ResearchObject later.")
            print(e)
            return None

    @staticmethod
    def _validate_and_set_creation_mode(creation_mode):
        """
        Semi-private function for validating and setting template attribute.
        :param creation_mode: str -> creation mode.
        :return: str -> creation mode value.
        """
        try:
            valid_creation_modes = set(rohub.list_valid_creation_modes())
            verified_creation_modes = utils.validate_against_different_formats(input_value=creation_mode,
                                                                               valid_value_set=valid_creation_modes)
            # checking if set contains at least one element
            if len(verified_creation_modes):
                # expected behaviour, only one value is correct
                return verified_creation_modes[0]
            else:
                msg = f"Incorrect creation mode. Must be one of: {valid_creation_modes}"
                raise SystemExit(msg)
        except KeyError as e:
            print("Wasn't able to validate values for creation mode. Leaving it"
                  " empty as per default. Please try adjust this using generated"
                  " ResearchObject later.")
            print(e)
            return None

    def _validate_type_matching(self, template):
        """
        Function that validates if given template can be associated with given Research Object type.
        :param template: str -> template value.
        """
        if not self.ros_type:
            msg = "Research Object type has to be provided when assigning template!"
            raise SystemExit(msg)
        valid_matches = rohub.show_valid_type_matching_for_ros()
        if not valid_matches[self.ros_type]:
            msg = "There is no template associated with given Research Object type!" \
                  "Please remove template from the input, and try creating/updating ROS again."
            raise SystemExit(msg)
        if template not in valid_matches[self.ros_type]:
            msg = f"Illegal usage - template value has to match Research Object type." \
                  f"Valid values for the type that was provided {valid_matches[self.ros_type]}"
            raise SystemExit(msg)

    def _assign_template(self):
        """
        Semi-private helper functions for assigning a template to research object type.
        :return: str -> template value
        """
        if not self.ros_type:
            msg = "Aborting... ros type is mandatory when use_template=True. Please specify ro_type!"
            raise SystemExit(msg)
        valid_matches = rohub.show_valid_type_matching_for_ros()
        template_results = valid_matches[self.ros_type]
        if not template_results:
            msg = "Unfortunately there is no template associated with ros type that was chosen." \
                  " The research object will be created without any template!"
            print(msg)
            return None
        else:
            return template_results[0]
