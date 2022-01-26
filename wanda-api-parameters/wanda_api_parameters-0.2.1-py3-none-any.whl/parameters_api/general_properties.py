import os

# Figure sizes
figtable = {"A4":[8.3, 11.7], "A3":[11.7, 16.5]}

# GLOBAL properties
ROOT_DIR = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
ROOT_DATA = os.path.join(ROOT_DIR, "data")
#ROOT_DATA = r"c:\Users\meerkerk\OneDrive - Stichting Deltares\TemporaryProjects\11207338 - Jubail\data"
ROOT_CHARACTERISTIC = os.path.join(ROOT_DATA, 'characteristics')
ROOT_CHARACTERISTIC_VALVE = os.path.join(ROOT_CHARACTERISTIC, 'valves')
ROOT_CHARACTERISTIC_PUMP = os.path.join(ROOT_CHARACTERISTIC, 'pumps')
ROOT_MSP = os.path.join(ROOT_DATA, "msp_boundaries")
ROOT_MODELS = os.path.join(ROOT_DATA, 'models')
ROOT_EXPORT = os.path.join(ROOT_DIR, 'export')
ROOT_CSV_EXISTING = os.path.join(ROOT_MODELS, "Existing_Network_CSV")
ROOT_CSV_FUTURE = os.path.join(ROOT_MODELS, "Future_Network_CSV")
ROOT_MATERIAL = os.path.join(ROOT_DATA, "material_data")
ROOT_EXAMPLE = os.path.join(ROOT_DIR, "example")
WBIN = r'C:\Program Files (x86)\Deltares\Wanda 4.6\Bin\\'

# Convert csv to epanet
MATERIAL = "Material"
EMODULUS = "Emodulus"
ROUGHNESS = "Roughness"
WAVESPEED = "Wave speed"
WALLTHICKNESS = "Wall thickness"
LOCAL_LOSS = "Minor Loss Coefficient (Derived)"
ID = 'Label'
DIAMETER = "Diameter (mm)"
DIAMETER_EXPORT = "Diameter"

# Wanda keys
WKEY_ADD_LOSS = "Additional losses"
WKEY_LOCAL_LOSS = "Local losses coeff"
WKEY_ROUGHNESS = "Wall roughness"
WKEY_FRICTION = "Friction model"
WKEY_YOUNGS = r"Young's modulus"
WKEY_VAL = "Value"
WKEY_PROP = "Property"
WKEY_WAVE_TYPE = "Wave speed mode"
WKEY_WAVE_SPEED = "Specified wave speed"
WKEY_DIAMETER = "Inner diameter"
WKEY_PROFILE = 'Profile'
WKEY_XDIST = "X-distance"
WKEY_HEIGHT = "Height"
WKEY_SDIST = "S-distance"
WKEY_GEOM_IN = "Geometry input"
WKEY_LH = "l-h"
WKEY_VALVE_CHAR = "Characteristic type"
WKEY_VALVE_KV = "Kv"
WKEY_VALVE_KVCHAR = "Kv Characteristic"
WKEY_VALVE_standard = "Standard"
WKEY_STANDARD_TYPE = "Standard type"
WKEY_KEYWORD = "Keywords"
WKEY_THICKNESS = "Wall thickness"
# Options to set in the pipes
PIPE_DICT = {WKEY_FRICTION: {WKEY_VAL: "D-W k", WKEY_PROP: True},
             WKEY_ROUGHNESS: {WKEY_VAL: ROUGHNESS, WKEY_PROP: False},
             WKEY_ADD_LOSS: {WKEY_VAL: "Xi", WKEY_PROP: True},
             WKEY_LOCAL_LOSS: {WKEY_VAL: LOCAL_LOSS, WKEY_PROP: False},
             WKEY_YOUNGS: {WKEY_VAL: EMODULUS, WKEY_PROP: False},
             WKEY_WAVE_TYPE: {WKEY_VAL: "Physical", WKEY_PROP: True},
             WKEY_THICKNESS: {WKEY_VAL: WALLTHICKNESS, WKEY_PROP: False},
             WKEY_DIAMETER: {WKEY_VAL: DIAMETER_EXPORT, WKEY_PROP: False},
             }

# Options to set in the valves
CSV_VALVE_DIAMETER = "Diameter (m)"
CSV_VALVE_TYPE = "Type"
CSV_VAVLE_ID = "ID"
CSV_VALVE_NAME = "Name"
CSV_STANDARD_VALVE_TYPE = "Valve type"
CSV_VALVE_CHARACTERISTIC = "Valve characteristic"

VALVE_DICT = {WKEY_VALVE_CHAR: {WKEY_VAL: WKEY_VALVE_standard, WKEY_PROP:True},
              WKEY_STANDARD_TYPE: {WKEY_VAL: CSV_STANDARD_VALVE_TYPE, WKEY_PROP:False},
              WKEY_DIAMETER: {WKEY_VAL: CSV_VALVE_DIAMETER, WKEY_PROP: False},
              WKEY_KEYWORD: {WKEY_VAL: "Valve", WKEY_PROP: False}
              }