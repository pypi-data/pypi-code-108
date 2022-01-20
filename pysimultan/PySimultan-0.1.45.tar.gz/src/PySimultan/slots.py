from .ParameterStructure.Components import SimSlot, SimSlotBase, ComponentUtils
# from .ParameterStructure.Components.ComponentUtils import *

"""
Valid slots

COMP_SLOT_ABGABE = "Abgabe"
COMP_SLOT_AREAS = "Geometrische_Flächen"
COMP_SLOT_CALCULATION = "Berechnung"
COMP_SLOT_COMMUNICATION = "Kommunikation"
COMP_SLOT_COMPOSITE = "Aufbau"
COMP_SLOT_CONNECTED_TO = "Angeschlossen_an"
COMP_SLOT_COST = "Kosten"
COMP_SLOT_DELIMITER = "_0"
COMP_SLOT_ERZEUGER = "Erzeuger"
COMP_SLOT_IMPORT = "Import"
COMP_SLOT_ITEM = "Element"
COMP_SLOT_JOINT = "Anschluss"
COMP_SLOT_LAYER = "Schicht"
COMP_SLOT_LENGTHS = "Geometrische_Längen"
COMP_SLOT_LIST = "Liste"
COMP_SLOT_MATERIAL = "Material"
COMP_SLOT_OBJECT = "Geometrisches_Objekt"
COMP_SLOT_OPENING = "Öffnung"
COMP_SLOT_POSITION = "Verortung"
COMP_SLOT_REGULATION = "Anforderungen"
COMP_SLOT_SINGLE_ACOUSTICS = "Akustik"
COMP_SLOT_SINGLE_COOLING = "Kühlung"
COMP_SLOT_SINGLE_ELECTRICAL = "Elektro"
COMP_SLOT_SINGLE_FIRE_SAFETY = "Brandschutz"
COMP_SLOT_SINGLE_HEATIG = "Heizung"
COMP_SLOT_SINGLE_HUMIDITY = "Feuchte"
COMP_SLOT_SINGLE_LIGHT_ARTIF = "Kunstlicht"
COMP_SLOT_SINGLE_LIGHT_NATURAL = "Naturlicht"
COMP_SLOT_SINGLE_MSR = "MSR"
COMP_SLOT_SINGLE_WASTE = "Abwasser"
COMP_SLOT_SINGLE_WATER = "Wasser"
COMP_SLOT_SIZE = "Geometrische_Maße"
COMP_SLOT_SPECIFICATION = "Leistungsbeschr"
COMP_SLOT_SYSTEM = "System"
COMP_SLOT_TUPLE = "Tupel"
COMP_SLOT_UNDEFINED = "Undefined Slot"
COMP_SLOT_VERTEILER = "Verteiler"
COMP_SLOT_VERTEILER_PART = "Verteiler_Teil"
COMP_SLOT_VERTEILER_PIPE = "Verteiler_Kanal"
COMP_SLOT_VOLUMES = "Geometrische_Volumina
"""


def create_slot(slot_name, slot_extension):
    return SimSlot(SimSlotBase(slot_name), str(slot_extension))
