# -*- coding: utf-8 -*-
# pylint: disable=invalid-name, too-many-branches, too-many-statements
"""Extranat."""

import argparse
import logging
import os.path
import sys

import extranatapi
from extranatapi import Extranatcli


__HELP__ = """Help"""
__OUTPUT_FORMAT__ = ['column', 'json', 'csv', 'text', 'xlsx']


def main():
    """Run main."""
    # ------------------------------------------
    # commandLine
    # ------------------------------------------
    cmdparser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, epilog=__HELP__)
    cmdparser.add_argument('--version', action='version', version=extranatapi.__version__)
    cmdparser.add_argument('--debug', action='store_true')
    cmdparser.add_argument('--list-regions', action='store_true')
    cmdparser.add_argument('--list-departements', action='store_true')
    cmdparser.add_argument('--list-clubs', action='store_true')
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
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    if cmdargs.debug:
        logger.setLevel(logging.DEBUG)

    # Extranat CLI
    extranatcli = Extranatcli(logger)

    # Check format
    outputformat = cmdargs.format
    if outputformat not in __OUTPUT_FORMAT__:
        logger.critical('Les formats de sortie disponibles sont: %s', ','.join(__OUTPUT_FORMAT__))
        sys.exit(1)

    # Output
    output = sys.stdout
    if outputformat == 'xlsx':
        if cmdargs.file is None:
            logger.critical("--file est obligatoire avec l'option --format xlsx")
            sys.exit(1)
        else:
            output = cmdargs.file
    else:
        if cmdargs.file is not None:
            output = open(cmdargs.file, 'w', encoding='utf-8')  # pylint: disable=consider-using-with
    extranatcli.set_output(output, outputformat)

    # action
    if cmdargs.list_regions:
        extranatcli.run_list_regions()
    elif cmdargs.list_departements:
        extranatcli.run_list_departements()
    elif cmdargs.list_clubs:
        extranatcli.run_list_clubs()
    elif cmdargs.saison:
        if cmdargs.idclub is None or cmdargs.annee is None:
            logger.critical('--idclub et --annee sont obligatoires')
            sys.exit(1)
        extranatcli.run_saison(idclub=cmdargs.idclub, annee=cmdargs.annee)
    elif cmdargs.nageur is not None:
        if os.path.isfile(cmdargs.nageur):
            extranatcli.run_nageurs_perf(inputfile=cmdargs.nageur, allperf=cmdargs.all)
        else:
            extranatcli.run_nageur_perf(iuf=cmdargs.nageur, allperf=cmdargs.all)
    elif cmdargs.cotation:
        if not os.path.isfile(cmdargs.cotation):
            logger.critical('Fichier non trouvé %s', cmdargs.cotation)
            sys.exit(1)
        extranatcli.run_cotation(inputfile=cmdargs.cotation, coeff_enable=cmdargs.master)
    elif cmdargs.recherche_equipe:
        if len(cmdargs.recherche_equipe) < 1:
            logger.critical('Fichier des nageurs manquant')
            sys.exit(1)
        if not os.path.isfile(cmdargs.recherche_equipe[0]):
            logger.critical('Fichier non trouvé %s', cmdargs.recherche_equipe[0])
            sys.exit(1)
        if not os.path.isfile(cmdargs.recherche_equipe[1]):
            logger.critical('Fichier non trouvé %s', cmdargs.recherche_equipe[1])
            sys.exit(1)

        sexe = None
        if len(cmdargs.recherche_equipe) >= 3:
            sexe = cmdargs.recherche_equipe[2]

        extranatcli.run_recherche_equipe(nagesfile=cmdargs.recherche_equipe[0], nageursfile=cmdargs.recherche_equipe[1], sexe=sexe)

    sys.exit(0)


if __name__ == "__main__":

    main()
