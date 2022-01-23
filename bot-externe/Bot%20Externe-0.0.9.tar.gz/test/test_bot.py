# -*- coding: utf-8 -*-
import unittest
from context import Bot, COMMAND_LIST, HELP_FILE, Request


class TestBot(unittest.TestCase):

    def setUp(self) -> None:
        self.true_command_list = COMMAND_LIST
        self.false_command_list_1 = ["/", "/help", "inutile", "/zarbi"]
        self.message_1 = Request("/help")
        self.message_2 = ["/cine", "namur"]

    def test_init(self):
        pass

    def test_get_help(self):
        self.assertEqual(len(Bot("/help").get_help(HELP_FILE)), 915)

    def test_process_request(self):

        self.assertEqual(
            len(Bot("/itinerary louvain-la-neuve ottignies").process_request(
                Request("/itinerary louvain-la-neuve ottignies").get_message(self.true_command_list))), 1201)
        self.assertEqual(len(Bot("/cine namur").process_request(
            Request("/cine namur").get_message(self.true_command_list))), 187)
        self.assertEqual(len(Bot("/news basket").process_request(
            Request("/news basket").get_message(self.true_command_list)).split("\n")), 10)
        self.assertEqual(len(Bot("/resto gembloux").process_request(
            Request("/resto gembloux").get_message(self.true_command_list))), 84)


if __name__ == "__main__":
    unittest.main()