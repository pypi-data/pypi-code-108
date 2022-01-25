import os
import subprocess
import sys

from pycsp3.compiler import Compilation
from pycsp3.tools.utilities import BLUE, WHITE

path_home = os.sep + "home" + os.sep + "lecoutre" + os.sep
path_prefix = path_home + "workspacePy" + os.sep + "pycsp3" + os.sep + "problems" + os.sep
path_prefix_parsers = path_prefix + "data" + os.sep + "parsers" + os.sep
path_prefix_instances = path_home + "instances" + os.sep

path_csp_acad = path_prefix + "csp" + os.sep + "academic" + os.sep
path_csp_real = path_prefix + "csp" + os.sep + "complex" + os.sep
path_cop_acad = path_prefix + "cop" + os.sep + "academic" + os.sep
path_cop_real = path_prefix + "cop" + os.sep + "complex" + os.sep

cwd = os.getcwd()
seriesName = sys.argv[1].lower()


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


def series(name):
    os.chdir(cwd)
    if seriesName in ("all", name.lower()):
        if not os.path.isdir(name):
            os.mkdir(name)
        os.chdir(name)
        return True
    return False


def execute(model, *, variants=None, data=None, dataformat=None, dataparser=None, series=None, other_args=None):
    if series:
        curr_wd = os.getcwd()
        if not os.path.isdir(series):
            os.mkdir(series)
        os.chdir(series)
    data = None if data is None else "[" + ",".join(str(v) for v in data) + "]" if isinstance(data, (tuple, list)) else str(data)
    variants = variants if isinstance(variants, (tuple, list)) else [variants]

    for variant in variants:
        command = "python3 " + model + (" -variant=" + variant if variant else "") + (" -data=" + data if data else "")
        command += (" -dataformat=" + dataformat if dataformat else "") + (" -dataparser=" + dataparser if dataparser else "")
        command += " " + str(other_args) if other_args else ""
        print(BLUE + "Command:" + WHITE, command)
        subprocess.call(command.split())
    if series:
        os.chdir(curr_wd)


if series("AllInterval"):
    d = {"model": path_csp_acad + "AllInterval.py", "dataformat": "{:03d}"}

    for i in list(range(5, 21)) + list(range(25, 101, 5)):
        execute(**d, variants=[None, "aux"], data=i)

if series("Bibd"):
    d = {"model": path_csp_acad + "Bibd.py", "dataformat": "[{:02d},{:03d},{:02d},{:02d},{:02d}]"}

    # series from "Global constraints for lexicographic orderings"
    t = [(6, 50, 25, 3, 10), (6, 60, 30, 3, 12), (6, 70, 35, 3, 10), (10, 90, 27, 3, 6), (9, 108, 36, 3, 9), (15, 70, 14, 3, 2), (12, 88, 22, 3, 4),
         (9, 120, 40, 3, 10), (10, 120, 36, 3, 8), (13, 104, 24, 3, 4)]
    for v in t:
        execute(**d, variants=[None, "aux"], data=v, series="lex")

    # series from "solving strategies for highly symmetric CSPs"
    t = [(7, 7, 3, 3, 1), (6, 10, 5, 3, 2), (7, 14, 6, 3, 2), (9, 12, 4, 3, 1), (6, 20, 10, 3, 4), (7, 21, 9, 3, 3), (6, 30, 15, 3, 6), (7, 28, 12, 3, 4),
         (9, 24, 8, 3, 2), (6, 40, 20, 3, 8), (7, 35, 15, 3, 5), (7, 42, 18, 3, 6), (10, 30, 9, 3, 2), (6, 50, 25, 3, 10), (9, 36, 12, 3, 3), (13, 26, 6, 3, 1),
         (7, 49, 21, 3, 7), (6, 60, 30, 3, 12), (7, 56, 24, 3, 8), (6, 70, 35, 3, 14), (9, 48, 16, 3, 4), (7, 63, 27, 3, 9), (8, 56, 21, 3, 6),
         (6, 80, 40, 3, 6), (7, 70, 30, 3, 10), (15, 35, 7, 3, 1), (12, 44, 11, 3, 2), (7, 77, 33, 3, 11), (9, 60, 20, 3, 5), (7, 84, 26, 3, 12),
         (10, 60, 18, 3, 4), (11, 55, 15, 3, 3), (7, 91, 39, 3, 13), (9, 72, 24, 3, 6), (13, 52, 12, 3, 2), (9, 84, 28, 3, 7), (9, 36, 32, 3, 8),
         (10, 90, 27, 3, 6), (9, 108, 36, 3, 9), (13, 78, 18, 3, 3), (15, 70, 14, 3, 2), (12, 88, 22, 3, 4), (9, 120, 40, 3, 10), (19, 57, 9, 3, 1),
         (10, 120, 36, 3, 8), (11, 110, 30, 3, 6), (16, 80, 15, 3, 2), (13, 104, 24, 3, 4)]
    for v in t:
        execute(**d, variants=[None, "aux"], data=v, series="sym")

    # series from "Symmetry Breaking Using Stabilizer"
    t = [(v, 0, 0, k, l) for (v, k, l) in
         [(8, 4, 6), (7, 3, 10), (6, 3, 10), (6, 3, 12), (12, 6, 5), (13, 4, 2), (9, 3, 9), (9, 3, 10), (11, 5, 4), (16, 6, 3), (16, 4, 1), (10, 3, 6),
          (19, 9, 4), (12, 3, 4), (10, 3, 8), (13, 3, 4), (16, 6, 2), (15, 3, 1), (15, 3, 2), (15, 5, 2), (25, 9, 3), (25, 5, 1), (21, 5, 1), (22, 7, 2)]]
    for v in t:
        execute(**d, variants=[None, "aux"], data=v, series="stab1")
    t = [(v, 0, 0, k, l) for (v, k, l) in
         [(6, 3, 2), (7, 3, 1), (6, 3, 4), (9, 3, 1), (7, 3, 2), (8, 4, 3), (6, 3, 6), (11, 5, 2), (10, 4, 2), (7, 3, 3), (13, 4, 1), (6, 3, 8), (9, 4, 3),
          (16, 4, 1), (7, 3, 4), (6, 3, 10), (9, 3, 2), (16, 6, 2), (15, 5, 2), (13, 3, 1), (7, 3, 5), (15, 7, 3), (21, 5, 1), (25, 5, 1), (10, 5, 4),
          (7, 3, 6),
          (22, 7, 2), (7, 3, 7), (8, 4, 6), (19, 9, 4), (10, 3, 2), (31, 6, 1), (7, 3, 8), (9, 3, 3), (7, 3, 9), (15, 3, 1), (21, 6, 2), (13, 4, 2), (11, 5, 4),
          (12, 6, 5), (25, 9, 3), (16, 6, 3)]]
    for v in t:
        execute(**d, variants=[None, "aux"], data=v, series="stab2")

    # series from Minizinc in CSPLib
    t = [(v, 0, 0, k, l) for (v, k, l) in
         [(3, 3, 1), (4, 2, 1), (6, 3, 2), (7, 3, 1), (7, 3, 2), (8, 4, 3), (9, 3, 1), (11, 5, 2), (13, 3, 1), (13, 4, 1), (15, 3, 1), (15, 7, 3), (16, 4, 1),
          (19, 3, 1), (25, 5, 1), (28, 4, 1)]]
    for v in t:
        execute(**d, variants=[None, "aux"], data=v, series="mini")

    # open instances from http://www.csplib.org/Problems/prob028/results
    t = [(46, 69, 9, 6, 1), (51, 85, 10, 6, 1), (61, 122, 12, 6, 1), (22, 33, 12, 8, 4), (40, 52, 13, 10, 3), (46, 69, 15, 10, 3), (65, 80, 16, 13, 3),
         (81, 81, 16, 16, 3), (49, 98, 18, 9, 3), (55, 99, 18, 10, 3), (85, 102, 18, 15, 3), (39, 57, 19, 13, 6), (61, 122, 20, 10, 3), (46, 92, 20, 10, 4),
         (45, 75, 20, 12, 5), (57, 76, 20, 15, 5), (57, 133, 21, 9, 3), (40, 60, 21, 14, 7), (85, 105, 21, 17, 4), (45, 90, 22, 11, 5), (45, 66, 22, 15, 7),
         (55, 132, 24, 10, 4), (69, 92, 24, 18, 6), (51, 85, 25, 15, 7), (51, 75, 25, 17, 8), (55, 135, 27, 11, 5), (55, 99, 27, 15, 7), (57, 84, 28, 19, 9),
         (57, 76, 28, 21, 10), (85, 85, 28, 28, 9), (34, 85, 30, 12, 10), (58, 87, 30, 20, 10), (56, 88, 33, 21, 12), (78, 117, 33, 22, 9),
         (64, 96, 33, 22, 11), (97, 97, 33, 33, 11), (69, 102, 34, 23, 11), (46, 161, 35, 10, 7), (51, 85, 35, 21, 14), (64, 80, 35, 28, 15),
         (69, 138, 36, 18, 9), (52, 104, 36, 18, 12), (49, 84, 36, 21, 15), (55, 90, 36, 22, 14), (70, 105, 36, 24, 12), (85, 85, 36, 36, 15),
         (75, 111, 37, 25, 12), (58, 116, 38, 19, 12), (76, 114, 39, 26, 13), (66, 99, 39, 26, 15), (57, 152, 40, 15, 10), (65, 104, 40, 25, 15)]
    # difficult to generate: 97, 97, 33, 33, 11
    for v in t:
        execute(**d, variants=[None, "aux"], data=v, series="open")

if series("Blackhole"):
    d = {"model": path_csp_real + "Blackhole.py", "dataparser": path_prefix_parsers + "Blackhole_Random.py"}

    for i in range(20):
        execute(**d, other_args="13 3 " + str(i), series="s13")
        execute(**d, other_args="16 3 " + str(i), series="s16")
        execute(**d, other_args="19 3 " + str(i), series="s19")

if series("BoardColoration"):
    d = {"model": path_cop_acad + "BoardColoration.py", "dataformat": "[{:02d},{:02d}]"}

    for i in list(range(5, 21)) + list(range(25, 41, 5)):
        execute(**d, data=[i, i], series="s1")
        execute(**d, data=[i - 2, i], series="s2")

if series("ColouredQueens"):
    d = {"model": path_csp_acad + "ColouredQueens.py", "dataformat": "{:02d}"}

    for i in range(4, 26):
        execute(**d, data=i)

if series("QueenAttacking"):
    d = {"model": path_cop_acad + "QueenAttacking.py", "dataformat": "{:02d}"}

    for i in range(3, 21):
        execute(**d, variants=[None, "aux", "hybrid", "table"], data=i)

# New series
if series("CoinsGrid"):
    d = {"model": path_cop_acad + "CoinsGrid.py", "dataformat": "[{:02d},{:02d}]"}

    for p in [(v * 2 + 2, v) for v in range(5, 14)] + [(31, 14)]:
        execute(**d, data=p)

if series("HCPizza"):
    d = {"model": path_cop_real + "HCPizza.py", "dataparser": path_prefix_parsers + "HCPizza_Random.py"}

    for i in range(4):
        execute(**d, other_args="10 10 2 6 " + str(i))
        execute(**d, other_args="12 12 2 6 " + str(i))
        execute(**d, other_args="15 15 2 7 " + str(i))
        execute(**d, other_args="20 20 2 8 " + str(i))

if series("PrizeCollecting"):
    d = {"model": path_cop_real + "PrizeCollecting.py", "dataparser": path_prefix_parsers + "PrizeCollecting_ParserZ.py"}

    for f in listdir_fullpath(path_prefix_instances + "dataForSeries" + os.sep + "prizeCollectingZ"):
        execute(**d, data=f)

if series("League"):
    d = {"model": path_cop_real + "League.py"}

    for f in listdir_fullpath(path_prefix_instances + "dataForSeries" + os.sep + "leagueJ"):
        execute(**d, data=f)

if series("RoadConstruction"):
    d = {"model": path_cop_real + "RoadConstruction.py", "dataparser": path_prefix_parsers + "RoadConstruction_ParserZ.py"}

    for f in listdir_fullpath(path_prefix_instances + "dataForSeries" + os.sep + "roadZ"):
        execute(**d, data=f)

if series("LinearArrangement"):
    d = {"model": path_cop_real + "LinearArrangement.py", "dataparser": path_prefix_parsers + "LinearArrangement_Parser.py"}

    for f in listdir_fullpath(path_prefix_instances + "dataForSeries" + os.sep + "linearArrangement"):
        execute(**d, data=f)

if series("MultiKnapsack"):
    d = {"model": path_cop_real + "MultiKnapsack.py", "dataparser": path_prefix_parsers + "MultiKnapsack_Parser.py"}

    for f in listdir_fullpath(path_prefix_instances + "dataForSeries" + os.sep + "mknap"):
        execute(**d, data=f)

if series("AircraftLanding"):
    d = {"model": path_cop_real + "AircraftLanding.py", "dataparser": path_prefix_parsers + "AircraftLanding_Parser.py"}

    for f in listdir_fullpath(path_prefix_instances + "dataForSeries" + os.sep + "aircraftLanding"):
        execute(**d, variants=[None, "table"], data=f)

if series("amaze"):
    d = {"model": path_cop_real + "Amaze.py", "dataparser": path_prefix_parsers + "Amaze_ParserZ.py"}

    for f in listdir_fullpath(path_prefix_instances + "dataForSeries" + os.sep + "amazeZ"):
        execute(**d, data=f)

if series("sonet"):
    d = {"model": path_cop_real + "Sonet.py", "dataparser": path_prefix_parsers + "Sonet_Parser.py"}

    for f in listdir_fullpath(path_prefix_instances + "dataForSeries" + os.sep + "sonet"):
        execute(**d, data=f)


if series("TravelingTournament"):
    d = {"model": path_cop_real + "TravelingTournament.py", "dataparser": path_prefix_parsers + "TravelingTournament_Parser.py"}

    for f in listdir_fullpath(path_prefix_instances + "dataForSeries" + os.sep + "travelingTournament"):
        execute(**d, variants=["a2", "a3"], data=f)

if series("TravelingTournamentWithPredefinedVenues"):
    d = {"model": path_cop_real + "TravelingTournamentWithPredefinedVenues.py",
         "dataparser": path_prefix_parsers + "TravelingTournamentWithPredefinedVenues_ParserZ.py"}

    for f in listdir_fullpath(path_prefix_instances + "dataForSeries" + os.sep + "travelingTournamentWithPredefinedVenuesZ"):
        execute(**d, variants=["a2", "a3"], data=f)

if series("PP"):
    dp = path_prefix_parsers + "ProgressiveParty_Parser.py"  # adding nPeriods += 3 for example to generate rally-p3
    for f in listdir_fullpath(path_prefix_instances + "ProgressiveParty" + os.sep + "rally"):
        execute(path_cop_real + "ProgressiveParty.py", data=f, dataparser=dp)

# os.chdir(cwd)
# execute(path_csp_acad + "AllInterval.py", data="8")
# execute(path_csp_acad + "ColouredQueens.py", data="8")

Compilation.done = True
