# -*- coding: utf-8 -*-
"""Recherche Rquipe.
"""

import copy
import logging


class RechercheEquipe():
    """CLASS : RechercheEquipe."""

    def __init__(self, logger=None):
        """Constructor."""
        self.__logger__ = logger
        self.__result_points__ = 0
        self.__result_equipe__ = []

    @property
    def logger(self):
        """Get logger."""
        if self.__logger__ is None:
            self.__logger__ = logging.getLogger()
        return self.__logger__

    def reset(self):
        """Reset."""
        self.__result_points__ = 0
        self.__result_equipe__ = []

    def push_result(self, equipe, points):
        """Push Result."""
        if points > self.__result_points__:
            self.__result_points__ = points
            self.__result_equipe__ = [copy.deepcopy(equipe)]
            self.logger.debug('Equipe : %s -> %s pts', equipe, points)
        elif points == self.__result_points__:
            self.__result_equipe__ += [copy.deepcopy(equipe)]
            self.logger.debug('Equipe : %s -> %s pts', equipe, points)

    def check_before_search(self, nages, nageurs):
        """Check before search."""
        listnages = []
        for item in nageurs:
            listnages = list(set(listnages + item.get_list_nages_name()))

        has_all_nages = True
        for item in nages:
            if item not in listnages:
                self.logger.critical("La nage %s n'est nagée par aucun nageur/nageuse", item)
                has_all_nages = False
                break

        return has_all_nages

    def search(self, nages, nageurs, equipe, points, max_dames, max_messieurs):  # pylint: disable=too-many-arguments, too-many-locals
        """Search."""
        lnageurs = len(nageurs)

        # End loop nages
        if len(nages) == 0:
            self.push_result(equipe, points)
            return

        # End loop nageurs
        if lnageurs == 0:
            # self.push_result(equipe, points)
            return

        # debug
        nages_first = nages[0]
        nages_other = nages[1:]

        # if nages_first == '300 Bra.':
        #     print('ste')

        for inageur in range(lnageurs):
            # self.logger.debug('Nages: %s -> %s / %s', nages, inageur, lnageurs)
            # if self.logger.level == logging.DEBUG:
            #     debugres = []
            #     for item in nageurs:
            #         debugres += [item.name]
            #     self.logger.debug('Nageurs: %s', debugres)

            nageurs_first = nageurs[inageur]
            nageurs_other = nageurs[:inageur] + nageurs[inageur + 1:]

            skip = False
            if nageurs_first.sexe == 'F' and max_dames == 0:
                skip = True
            if nageurs_first.sexe == 'M' and max_messieurs == 0:
                skip = True

            if not skip:
                nage = nageurs_first.get_nage(nages_first)
                max_dames2 = max_dames
                max_messieurs2 = max_messieurs
                if nage is None:
                    points2 = points
                    equipe2 = copy.deepcopy(equipe)
                    self.search(nages, nageurs_other, equipe=equipe2, points=points2, max_dames=max_dames2, max_messieurs=max_messieurs2)
                else:
                    points2 = points + nage.points_i
                    equipe2 = copy.deepcopy(equipe) + [{nageurs_first.name: {'nage': nages_first, 'points': nage.points_i}}]
                    if nageurs_first.sexe == 'F':
                        max_dames2 = max_dames - 1
                    else:
                        max_messieurs2 = max_messieurs - 1

                    self.search(nages_other, nageurs_other, equipe=equipe2, points=points2, max_dames=max_dames2, max_messieurs=max_messieurs2)
