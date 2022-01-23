# -*- coding: utf-8 -*-
# pylint: disable=invalid-name, too-many-branches, too-many-statements
"""Extranat."""

import argparse
import logging
import math
import os.path
import sys

from .base import ExtranatObjectCollection, ItemsName
from .cotation import Cotation, COTATION_MESSIEURS, COTATION_DAMES
from .filetools import FileTools
from .nageur import Nageur
from .wrapper import Wrapper
from .rechercheequipe import RechercheEquipe


__version__ = '0.0.0.6'
__HELP__ = """Help"""
__OUTPUT_FORMAT__ = ['column', 'json', 'csv', 'text', 'xlsx']


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

    # list-nages
    def run_list_nages(self):
        """Run list nages."""
        results = ItemsName()

        results.appendlist(COTATION_MESSIEURS.values())
        results.appendlist(COTATION_DAMES.values())

        self.show_result(results)

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

    def run(self):
        """Run main."""
        # ------------------------------------------
        # commandLine
        # ------------------------------------------
        cmdparser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, epilog=__HELP__)
        cmdparser.add_argument('--version', action='version', version=__version__)
        cmdparser.add_argument('--debug', action='store_true')
        cmdparser.add_argument('--list-regions', action='store_true')
        cmdparser.add_argument('--list-departements', action='store_true')
        cmdparser.add_argument('--list-clubs', action='store_true')
        cmdparser.add_argument('--list-nages', action='store_true')
        cmdparser.add_argument('--saison', action='store_true')
        cmdparser.add_argument('--nageur', help='avec son code IUF')
        cmdparser.add_argument('--cotation', help='fichier csv/xlsx en entrée')
        cmdparser.add_argument('--master', action='store_false', help='Utilisation des coeff de rajeunissement master')
        cmdparser.add_argument('--idclub')
        cmdparser.add_argument('--annee')
        cmdparser.add_argument('--recherche_equipe', nargs='+')
        cmdparser.add_argument('--all', action='store_true')
        cmdparser.add_argument('--format', help='Formats spécifiques de sortie: column (defaut), json, csv, text, xlsx', default='column')
        cmdparser.add_argument('--file', help='Redirection de la sortie vers un fichier')

        # ------------------------------------------
        # Process
        # ------------------------------------------
        cmdargs = cmdparser.parse_args()

        # debug
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
        if cmdargs.debug:
            self.logger.setLevel(logging.DEBUG)

        # Check format
        outputformat = cmdargs.format
        if outputformat not in __OUTPUT_FORMAT__:
            self.logger.critical('Les formats de sortie disponibles sont: %s', ','.join(__OUTPUT_FORMAT__))
            sys.exit(1)

        # Output
        output = sys.stdout
        if outputformat == 'xlsx':
            if cmdargs.file is None:
                self.logger.critical("--file est obligatoire avec l'option --format xlsx")
                sys.exit(1)
            else:
                output = cmdargs.file
        else:
            if cmdargs.file is not None:
                output = open(cmdargs.file, 'w', encoding='utf-8')  # pylint: disable=consider-using-with
        self.set_output(output, outputformat)

        # action
        if cmdargs.list_regions:
            self.run_list_regions()
        elif cmdargs.list_departements:
            self.run_list_departements()
        elif cmdargs.list_clubs:
            self.run_list_clubs()
        elif cmdargs.list_nages:
            self.run_list_nages()
        elif cmdargs.saison:
            if cmdargs.idclub is None or cmdargs.annee is None:
                self.logger.critical('--idclub et --annee sont obligatoires')
                sys.exit(1)
            self.run_saison(idclub=cmdargs.idclub, annee=cmdargs.annee)
        elif cmdargs.nageur is not None:
            if os.path.isfile(cmdargs.nageur):
                self.run_nageurs_perf(inputfile=cmdargs.nageur, allperf=cmdargs.all)
            else:
                self.run_nageur_perf(iuf=cmdargs.nageur, allperf=cmdargs.all)
        elif cmdargs.cotation:
            if not os.path.isfile(cmdargs.cotation):
                self.logger.critical('Fichier non trouvé %s', cmdargs.cotation)
                sys.exit(1)
            self.run_cotation(inputfile=cmdargs.cotation, coeff_enable=cmdargs.master)
        elif cmdargs.recherche_equipe:
            if len(cmdargs.recherche_equipe) < 1:
                self.logger.critical('Fichier des nageurs manquant')
                sys.exit(1)
            if not os.path.isfile(cmdargs.recherche_equipe[0]):
                self.logger.critical('Fichier non trouvé %s', cmdargs.recherche_equipe[0])
                sys.exit(1)
            if not os.path.isfile(cmdargs.recherche_equipe[1]):
                self.logger.critical('Fichier non trouvé %s', cmdargs.recherche_equipe[1])
                sys.exit(1)

            sexe = None
            if len(cmdargs.recherche_equipe) >= 3:
                sexe = cmdargs.recherche_equipe[2]

            self.run_recherche_equipe(nagesfile=cmdargs.recherche_equipe[0], nageursfile=cmdargs.recherche_equipe[1], sexe=sexe)

        sys.exit(0)
