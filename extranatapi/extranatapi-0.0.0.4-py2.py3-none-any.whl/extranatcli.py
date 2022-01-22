# -*- coding: utf-8 -*-
"""Extranat."""

import logging
import math
import sys

from .base import ExtranatObjectCollection
from .cotation import Cotation
from .filetools import FileTools
from .nageur import Nageur
from .wrapper import Wrapper
from .rechercheequipe import RechercheEquipe


class Extranatcli():
    """Class : Extranatcli."""

    def __init__(self, logger=None):
        """Construtor."""
        if logger is None:
            self.__logger__ = logging.getLogger()
        else:
            self.__logger__ = logger

        self.__filetools__ = FileTools(self.__logger__)
        self.__output__ = sys.stdout
        self.__outputformat__ = 'column'
        self.__result_regions__ = None
        self.__result_departements__ = None
        self.__result_clubs__ = None

    @property
    def logger(self):
        """Get logger."""
        return self.__logger__

    @property
    def filetools(self):
        """Get filetools."""
        return self.__filetools__

    @property
    def output(self):
        """Get output."""
        return self.__output__

    @property
    def outputformat(self):
        """Get output format."""
        return self.__outputformat__

    def set_output(self, output, outputformat):
        """Set output."""
        self.__output__ = output
        self.__outputformat__ = outputformat

    def show_result(self, result):
        """Show result."""
        if self.outputformat == 'json':
            self.output.write(result.to_json())

        elif self.outputformat == 'csv':
            self.filetools.write_csv(
                array=result.to_array(startarray=[]),
                array_header=result.to_array_header(startarray=[]),
                output=self.output)

        elif self.outputformat == 'text':
            self.output.write(result.__str__())

        elif self.outputformat == 'xlsx':
            self.filetools.write_excel(
                filename=self.output,
                array=result.to_array(startarray=[]),
                array_header=result.to_array_header(startarray=[]))
        else:
            result.to_stdcolumn(self.output)

    # list-regions
    def run_list_regions(self):
        """Run list regions."""
        wrapper = Wrapper(showprogress=True)

        if self.__result_regions__ is None:
            self.__result_regions__ = wrapper.get_regions()
        self.show_result(self.__result_regions__)

    # list-departements
    def run_list_departements(self):
        """Run list departements."""
        wrapper = Wrapper(showprogress=True)

        if self.__result_departements__ is None:
            self.__result_departements__ = wrapper.get_departements()
        self.show_result(self.__result_departements__)

    # list-clubs
    def run_list_clubs(self):
        """Run list clubs."""
        wrapper = Wrapper(showprogress=True)

        if self.__result_clubs__ is None:
            self.__result_clubs__ = wrapper.get_clubs()
        self.show_result(self.__result_clubs__)

    # get saison
    def run_saison(self, idclub, annee):
        """Run saison."""

        wrapper = Wrapper(showprogress=True)
        result = wrapper.get_saison(idclub, annee)
        self.show_result(result)

    # get nageur
    def run_nageur_perf(self, iuf, allperf):
        """Run Perf Nageur."""

        wrapper = Wrapper(showprogress=True)
        if allperf:
            result = wrapper.get_nageur_all(iuf)
        else:
            result = wrapper.get_nageur_mpp(iuf)

        self.show_result(result.nages)

    # get nageurs
    def run_nageurs_perf(self, inputfile, allperf):
        """Run Perf NageurS."""
        results = ExtranatObjectCollection(Nageur())
        iufs = self.filetools.read_uif(inputfile)

        wrapper = Wrapper(showprogress=True)
        for iuf in iufs:

            if allperf:
                nageur = wrapper.get_nageur_all(iuf)
            else:
                nageur = wrapper.get_nageur_mpp(iuf)

            if nageur is not None:
                results.append(nageur)

        self.show_result(results)

    # get cotation
    def run_cotation(self, inputfile, coeff_enable=True):
        """Run cotation."""
        nageurs = self.filetools.read_nageurs(inputfile)
        cotation = Cotation()

        for nageur in nageurs:

            nageur.cotation(cotation=cotation, coeff_enable=coeff_enable)

        self.show_result(nageurs)

    # Recherche Equipe
    def run_recherche_equipe(self, nagesfile, nageursfile, sexe):
        """Recherche Equipe."""
        nageurs = self.filetools.read_equipe_nageurs(nageursfile)
        nages = self.filetools.read_equipe_nages(nagesfile)

        max_dames = len(nages)
        max_messieurs = max_dames

        if sexe is not None:
            if sexe == 'M':
                max_dames = 0
            elif sexe == 'F':
                max_messieurs = 0
            else:
                try:
                    min_sexe = int(sexe)
                    if min_sexe > math.ceil(max_dames / 2.0):
                        self.logger.critical('Trop de nageurs demandés par rapport au nombre de nage: %s vs %s/2', min_sexe, max_dames)
                        sys.exit(1)
                    max_dames = max_messieurs - min_sexe
                    max_messieurs = max_dames
                except ValueError:
                    self.logger.critical('Paramètre sur le sexe invalide: %s', sexe)
                    sys.exit(1)

        self.logger.debug('Max messieurs: %s', max_messieurs)
        self.logger.debug('Max dames: %s', max_dames)

        searchteam = RechercheEquipe(self.logger)

        if searchteam.check_before_search(nages, nageurs):
            searchteam.search(nages, nageurs, [], 0, max_dames, max_messieurs)

            print(f'Points: {searchteam.__result_points__}')
            for item in searchteam.__result_equipe__:
                print(item)

        # self.show_result(nageurs)
        # print(nages)
