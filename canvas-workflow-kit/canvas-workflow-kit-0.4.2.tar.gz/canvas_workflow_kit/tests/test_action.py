from .base import SDKBaseTest
from canvas_workflow_kit.action import Coding, Action


class CodingTest(SDKBaseTest):

    def test___init__(self):
        # placeholder test
        tested = Coding()
        self.assertIsInstance(tested, Coding)


class ActionTest(SDKBaseTest):

    def test___init__(self):
        tested = Action('Title', 'Type', 'This is some content')
        self.assertIsInstance(tested, Action)
        self.assertEqual('Title', tested.title)
        self.assertEqual('Type', tested.type)
        self.assertEqual('This is some content', tested.content)

    def test_to_json(self):
        # placeholder test
        tested = Action('Title', 'Type', 'This is some content')
        self.assertIsInstance(tested, Action)
        result = tested.to_json()
        self.assertIsNone(result)
