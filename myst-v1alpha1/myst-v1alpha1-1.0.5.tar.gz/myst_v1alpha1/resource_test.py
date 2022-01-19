import unittest

import google.auth.credentials
import responses

import myst_v1alpha1
from myst_v1alpha1.resource import Resource


class ExampleResource(Resource):
    """Example resource to use in tests."""

    RESOURCE_NAME = "example_resource"

    def __init__(self, title, **kwargs):
        super(ExampleResource, self).__init__(**kwargs)
        self.title = title


class OtherExampleResource(Resource):
    """Other example resource to use in tests."""

    RESOURCE_NAME = "other_example_resource"


class ResourceTest(unittest.TestCase):
    """Base resource test for all resource tests to inherit from."""

    _RESOURCE_CLS = ExampleResource
    _RESOURCE_KWARGS = dict(title="My Example Resource")
    _RESOURCE_GET_JSON = {
        "uuid": "868d2f74-f382-49ee-bed1-8ebee810ffb0",
        "object": "ExampleResource",
        "create_time": "2018-01-01T00:00:00Z",
        "update_time": None,
        "title": "My Example Resource",
    }
    _RESOURCE_LIST_JSON = {
        "data": [
            {
                "uuid": "ea2ba917-1178-4a5d-81b1-f25ffd4c4feb",
                "object": "ExampleResource",
                "create_time": "2018-01-01T00:00:00Z",
                "update_time": None,
                "title": "My Example Resource #1",
            },
            {
                "uuid": "8e67aec5-6580-4673-ae3d-1ffde3f13c08",
                "object": "ExampleResource",
                "create_time": "2018-01-01T00:00:00Z",
                "update_time": None,
                "title": "My Example Resource #2",
            },
        ]
    }

    def _generate_custom_resource(self, resource_cls, default_kwargs, **kwargs):
        """Generates a resource for use in tests.

        Args:
            resource_cls (type[myst_v1alpha1.resource.Resource]): type of resource to generate
            default_kwargs (dict): default keyword arguments
            **kwargs: additional keyword arguments to override or augment default keyword arguments with

        Returns:
            resource (myst_v1alpha1.resource.Resource): resource object
        """
        resource = resource_cls(**dict(default_kwargs, **kwargs))
        return resource

    def _generate_resource(self, **kwargs):
        example_resource = self._generate_custom_resource(
            resource_cls=self._RESOURCE_CLS, default_kwargs=self._RESOURCE_KWARGS, **kwargs
        )
        return example_resource

    def setUp(self):
        # Authenticate using anonymous credentials for testing.
        myst_v1alpha1.authenticate(credentials=google.auth.credentials.AnonymousCredentials())

    def test_resource(self):
        # Generate an example resource to test with.
        example_resource = self._generate_resource(uuid="868d2f74-f382-49ee-bed1-8ebee810ffb0")

        # Test example resource attributes.
        self.assertEqual(example_resource.uuid, "868d2f74-f382-49ee-bed1-8ebee810ffb0")

    def test_eq(self):
        # Generate a couple of example resources to test with.
        example_resource = self._generate_resource(uuid="868d2f74-f382-49ee-bed1-8ebee810ffb0")
        other_example_resource = self._generate_resource(uuid="868d2f74-f382-49ee-bed1-8ebee810ffb0")
        self.assertEqual(example_resource, other_example_resource)

        # Change an attribute and test that they are no longer equal.
        other_example_resource.title = "Other Example Resource"
        self.assertNotEqual(example_resource, other_example_resource)

        # Test that a resource of a different type is not equal.
        self.assertNotEqual(Resource(), OtherExampleResource())

    def test_repr(self):
        resource = self._generate_resource(uuid="868d2f74-f382-49ee-bed1-8ebee810ffb0")
        self.assertEqual(
            str(resource),
            "<{resource_class}: uuid=868d2f74-f382-49ee-bed1-8ebee810ffb0>".format(
                resource_class=self._RESOURCE_CLS.__name__
            ),
        )

    def test_class_url(self):
        self.assertEqual(ExampleResource.class_url(), "https://api.myst.ai/v1alpha1/example_resource")

    def test_instance_url(self):
        example_resource = self._generate_resource(uuid="868d2f74-f382-49ee-bed1-8ebee810ffb0")
        self.assertEqual(
            example_resource.instance_url(),
            "https://api.myst.ai/v1alpha1/example_resource/868d2f74-f382-49ee-bed1-8ebee810ffb0",
        )

    @responses.activate
    def test_resource_get(self):
        # Mock example resource response.
        responses.add(
            responses.GET,
            "https://api.myst.ai/v1alpha1/example_resource/868d2f74-f382-49ee-bed1-8ebee810ffb0",
            json=self._RESOURCE_GET_JSON,
        )
        example_resource = ExampleResource.get(uuid="868d2f74-f382-49ee-bed1-8ebee810ffb0")

        # Test that example resource attributes were updated as expected.
        self.assertEqual(example_resource.uuid, "868d2f74-f382-49ee-bed1-8ebee810ffb0")
        self.assertEqual(example_resource.object, "ExampleResource")
        self.assertEqual(example_resource.create_time, "2018-01-01T00:00:00Z")
        self.assertEqual(example_resource.update_time, None)
        self.assertEqual(example_resource.title, "My Example Resource")

    @responses.activate
    def test_resource_list(self):
        # Mock example resource response.
        responses.add(
            responses.GET,
            "https://api.myst.ai/v1alpha1/{resource_name}".format(resource_name=self._RESOURCE_CLS.RESOURCE_NAME),
            json=self._RESOURCE_LIST_JSON,
        )

        self.assertEqual(
            ExampleResource.list(),
            [
                ExampleResource(
                    uuid="ea2ba917-1178-4a5d-81b1-f25ffd4c4feb",
                    object="ExampleResource",
                    create_time="2018-01-01T00:00:00Z",
                    update_time=None,
                    title="My Example Resource #1",
                ),
                ExampleResource(
                    uuid="8e67aec5-6580-4673-ae3d-1ffde3f13c08",
                    object="ExampleResource",
                    create_time="2018-01-01T00:00:00Z",
                    update_time=None,
                    title="My Example Resource #2",
                ),
            ],
        )

    @responses.activate
    def test_resource_refresh(self):
        # Mock example resource response.
        responses.add(
            responses.GET,
            "https://api.myst.ai/v1alpha1/example_resource/868d2f74-f382-49ee-bed1-8ebee810ffb0",
            json=self._RESOURCE_GET_JSON,
        )

        # Generate an example resource to test with.
        example_resource = self._generate_resource(uuid="868d2f74-f382-49ee-bed1-8ebee810ffb0")

        example_resource.refresh()

        # Test that example resource attributes were updated as expected.
        self.assertEqual(example_resource.uuid, "868d2f74-f382-49ee-bed1-8ebee810ffb0")
        self.assertEqual(example_resource.object, "ExampleResource")
        self.assertEqual(example_resource.create_time, "2018-01-01T00:00:00Z")
        self.assertEqual(example_resource.update_time, None)
        self.assertEqual(example_resource.title, "My Example Resource")

    def test_resources_refresh_with(self):
        # Generate an example resource to test with.
        example_resource = self._generate_resource(uuid="036b8a5a-3ed0-4d9e-b6f7-9c4f44c4c0ca")

        # Test that example resource attributes were intialized as expected.
        self.assertEqual(example_resource.uuid, "036b8a5a-3ed0-4d9e-b6f7-9c4f44c4c0ca")
        self.assertEqual(example_resource.title, "My Example Resource")

        example_resource.refresh_with(self._RESOURCE_GET_JSON)

        # Test that example resource attributes were updated as expected.
        self.assertEqual(example_resource.uuid, "868d2f74-f382-49ee-bed1-8ebee810ffb0")
        self.assertEqual(example_resource.object, "ExampleResource")
        self.assertEqual(example_resource.create_time, "2018-01-01T00:00:00Z")
        self.assertEqual(example_resource.update_time, None)
        self.assertEqual(example_resource.title, "My Example Resource")
