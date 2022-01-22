# -*- coding: utf-8 -*-
import unittest
from context import Request, COMMAND_LIST


class TestRequest(unittest.TestCase):
    def setUp(self) -> None:
        self.request1 = Request("/news fr")
        self.request2 = Request("/autreCommande qqChose")
        self.request3 = Request("J'ai pas compris comment fonctionne le bot")
        self.command_list = COMMAND_LIST

    def test__init__(self):
        self.assertEqual(self.request1.message, "/news fr")
        self.assertEqual(self.request2.message, "/autreCommande qqChose")
        self.assertEqual(self.request3.message, "J'ai pas compris comment fonctionne le bot")

    def test_get_message(self):
        self.assertEqual(self.request1.get_message(self.command_list), self.request1.message.split())
        self.assertEqual(self.request2.get_message(self.command_list),
                         "Commande introuvable! Entrez /help pour voir la liste des commandes")
        self.assertEqual(self.request3.get_message(self.command_list),
                         "Commande introuvable! Entrez /help pour voir la liste des commandes")


if __name__ == '__main__':
    unittest.main()
