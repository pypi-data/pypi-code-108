# -*- coding: utf-8 -*-
import unittest
import pytest
from context import Opinion, MongoConnector

# Commande de connexion à la base de doonnées mongosh 
# "mongodb+srv://cluster0.5i6qo.gcp.mongodb.net/ephecom-2TM2?authSource=%24external&authMechanism=MONGODB-X509" --tls
# --tlsCertificateKeyFile ./db_key.pem 


class TestOpinion(unittest.TestCase, MongoConnector):
    def setUp(self):
        try:
            with MongoConnector() as connector:
                self.collection = connector.db["users"]
                res = self.collection.findOne()
                print(res)
        except Exception as e:
            print(e)

        self.id = 0
        for elem in self.collection.find():
            self.id = elem["_id"]

        self.rep1 = {'_id': self.id + 1, 'opinion': 4,
                     'message': "c'est trop bien"}
        self.rep2 = {'_id': self.id + 2, 'opinion': 5, 'message': ""}
        self.rep3 = {'_id': self.id + 3, 'opinion': 1, 'message': "nul"}

    def test_init(self):
        """
        Tester l'instanciation de la connexion a la base de données
        """
        pass

    def test_set_opinion(self):
        self.assertEqual(Opinion(is_positif=12).set_opinion(),
                         "Choisissez plutôt un nombre entre 0 et 5 svp.")

        self.assertEqual(Opinion(is_positif=4, message="c'est trop bien").set_opinion(),
                         "Votre avis a bien été envoyé. Nous en tiendrons compte !")
        self.elem = self.collection.find().limit(1).sort([("$natural", -1)])
        self.assertEqual(self.elem[0], self.rep1)

        self.assertEqual(Opinion(is_positif=5).set_opinion(),
                         "Votre avis a bien été envoyé. Nous en tiendrons compte !")
        self.elem = self.collection.find().limit(1).sort([("$natural", -1)])
        self.assertEqual(self.elem[0], self.rep2)

        self.assertEqual(Opinion(is_positif=1, message="nul").set_opinion(),
                         "Votre avis a bien été envoyé. Nous en tiendrons compte !")
        self.elem = self.collection.find().limit(1).sort([("$natural", -1)])
        self.assertEqual(self.elem[0], self.rep3)

        self.collection.delete_one(self.rep1)
        self.collection.delete_one(self.rep2)
        self.collection.delete_one(self.rep3)


if __name__ == '__main__':
    pytest.main()
