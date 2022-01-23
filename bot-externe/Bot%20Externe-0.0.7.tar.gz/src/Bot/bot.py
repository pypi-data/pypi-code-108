
# -*- coding: utf-8 -*-
from .request import Request
from .weather import Weather
from .itinerary import Itinerary
from .news import News
from .cine import Cine
from .resto import Resto
from .config import HELP_FILE, COMMAND_LIST
from .opinion import Opinion


class ParameterException(Exception):
    pass


class Bot:
    # Mettre le chemin du fichier dans un fichier de configuration

    def __init__(self, message, command_list=COMMAND_LIST, help_file=HELP_FILE):
        self.__help = help_file

        self.__message = Request(message).get_message(command_list)
        self.error = "Mauvaise syntaxe veuillez entrez /help pour plus de précision!"

    def __str__(self):
        if isinstance(self.__message, list):

            return self.process_request(self.__message)
        else:
            return self.__message

    @property
    def _help(self):
        return self.__help

    def get_help(self, _help):
        """
        Renvoie toutes les commandes possibles et leur description

        PRE : Un fichier contenant les commandes et leur description
        POST : Chaines de caractère des commandes utilisables et leur description
        RAISES : Exception : si pas de réponse à la requete

        """
        try:
            with open(_help) as help_:
                return help_.read()
        except FileNotFoundError:
            return self.error

    def process_request(self, message):
        """
        Evalue la requête de l'utilisateur et appelle la classe correspondante

        PRE : liste contenant la commande et les paramètres
        POST : les réponses adéquates en fonction des modules appelés
        RAISES : Exception : si pas de réponse à la requete
        """

        # message est une liste contenant la commande et les paramètres que l'utilisateur a introduit

        if isinstance(message, list):
            if message[0] == "/help":
                return self.get_help(self._help)

            elif message[0] == "/weather":
                if len(message) == 1:
                    return Weather().get_weather()
                if len(message) == 2:
                    return Weather(message[0]).get_weather()

                if len(message) > 2:
                    return self.error

            elif message[0] == "/itinerary":
                # si on a plus que 2 paramètres , erreur
                if len(message) > 3 or len(message) <= 1:
                    return self.error
                if len(message) == 2:
                    return Itinerary(destination_address=message[1]).get_itinerary()
                if len(message) == 3:
                    return Itinerary(message[1], message[2]).get_itinerary()

            elif message[0] == "/news":
                if len(message) > 2 or len(message) <= 0:
                    return self.error
                if len(message) == 2:
                    return News(message[1]).get_news()
                if len(message) == 1:
                    return News().get_news()

            elif message[0] == "/cine":
                if len(message) > 2:
                    return self.error
                if len(message) == 2:
                    return Cine(message[1]).get_cine()
                if len(message) == 1:
                    return Cine().get_cine()

            elif message[0] == "/resto":
                if len(message) > 2:
                    return self.error
                if len(message) == 2:
                    return Resto(message[1]).get_resto()
                if len(message) == 1:
                    return Resto().get_resto()

            elif message[0] == "/opinion":

                if len(message) < 2:
                    return self.error
                if len(message) == 2:
                    return Opinion(message[1]).set_opinion()
                if len(message) > 2:
                    commentaire = ""
                    for i in range(2, len(message)):
                        commentaire += message[i] + " "
                    commentaire = commentaire[:-1]
                    return Opinion(message[1], commentaire).set_opinion()
        elif isinstance(message, str):
            return message
