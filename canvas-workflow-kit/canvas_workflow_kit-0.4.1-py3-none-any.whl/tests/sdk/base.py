from canvas_workflow_kit import settings

from canvas_workflow_kit.tests.base import SDKBaseTest


class SDKBaseTest(SDKBaseTest):

    def setUp(self):
        super().setUp()
        self.mocks_path = f'{settings.BASE_DIR}/tests/sdk/mock_data'
