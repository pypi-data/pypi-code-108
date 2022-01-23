import json
import os

script_dir = os.path.dirname(os.path.realpath(__file__))

class NotFoundError(Exception):
    pass

class Database():
    def __init__(self, data):
        self._data = data

    def get_odrive_versions(self):
        """
        Returns all known ODrive board versions and their data as a collection
        of tuples.
        """
        print("TODO: deprecated")
        return self._data['odrives'].items()

    def get_products(self):
        """
        Returns all known ODrive Robotics product line and version combinations.
        The return type is a generator of tuples of the form
        (product_name, product_data).
        """
        return [
            ((('ODrive ' + k) if k.startswith('v3.') else ('ODrive Pro ' + k)), v)
            for k, v in self._data['odrives'].items()
        ]

    def get_odrive(self, board_version: str):
        """
        Loads data for a particular ODrive version.
        board_version: e.g. "v4.4" or "v4.4-58V"
        """
        print("TODO: get_odrive() IS DEPRECATED") # TODO: use get_product() instead
        return self._data['odrives'][board_version.partition('-')[0]]

    def get_product(self, product: str):
        """
        Loads data for a particular ODrive Robotics product.
        product: e.g. "ODrive v4.4" or "ODrive v4.4-58V"
        """
        if product.startswith("ODrive Pro "):
            board_version = product[len("ODrive Pro "):]
        elif product.startswith("ODrive "):
            board_version = product[len("ODrive "):]
        elif product.startswith("NODrive "):
            board_version = product[len("NODrive "):]
        else:
            raise NotFoundError(f"unknown product line: {product}")
        key = board_version.partition('-')[0]
        if not key in self._data['odrives']:
            raise NotFoundError(f"{key} not found in product database")
        return self._data['odrives'][key]

    def get_motor(self, name: str):
        """
        Loads data for a particular motor model.
        name: e.g. "D6374-150KV"
        """
        return self._data['motors'][name]

    def get_encoder(self, name: str):
        """
        Loads data for a particular encoder model.
        name: e.g. "AMT10x"
        """
        return self._data['encoders'][name]

    def get_encoders(self):
        return list(self._data['encoders'].keys())


def _process_motor(motor):
    if "kv" in motor:
        motor["torque_constant"] = 8.27 / motor["kv"]
    else:
        motor["kv"] = 8.27 / motor["torque_constant"]

def _process_nothing(x):
    pass


def load(path = None, validate = False):
    """
    path: Path of the database folder. If none, the path is detected automatically.
    validate: Validates all JSON files that are being loaded against their schema.
    If this feature is used jsonschema must be installed.
    """

    db_dir0 = os.path.join(script_dir, 'data') # When running from pip install
    db_dir1 = os.path.join(os.path.dirname(os.path.dirname(script_dir)), 'data') # When running from Git repo

    if path is None:
        if os.path.isdir(db_dir0):
            path = db_dir0
        elif os.path.isdir(db_dir1):
            path = db_dir1
        else:
            raise Exception("Database not found.")

    data = {
        'odrives': {},
        'drvs': {},
        'motors': {},
        'encoders': {}
    }

    loaders = {
        'odrive': [_process_nothing, None],
        'drv': [_process_nothing, None],
        'motor': [_process_motor, None],
        'encoder': [_process_nothing, None]
    }

    if validate:
        import jsonschema
        with open(os.path.join(path, "schema.json")) as fp:
            schema = json.load(fp)
        loaders['odrive'][1] = jsonschema.Draft4Validator({**schema, **{"$ref": "#/$defs/odrive"}})
        loaders['drv'][1] = jsonschema.Draft4Validator({**schema, **{"$ref": "#/$defs/drv"}})
        loaders['motor'][1] = jsonschema.Draft4Validator({**schema, **{"$ref": "#/$defs/motor"}})
        loaders['encoder'][1] = jsonschema.Draft4Validator({**schema, **{"$ref": "#/$defs/encoder"}})


    for file in os.listdir(path):
        name, ext = os.path.splitext(file)
        file = os.path.join(path, file)
        if os.path.isfile(file) and ext.lower() == '.json':
            for k, (processor, validator) in loaders.items():
                try:
                    if name.startswith(k + '-') and ext.lower() == '.json':
                        with open(file) as fp:
                            items = {name.partition(k + '-')[-1]: json.load(fp)}

                    elif name == k + 's':
                        with open(file) as fp:
                            items = json.load(fp)
                        assert(isinstance(items, dict))

                    else:
                        continue

                    if validate:
                        for item in items.values():
                            validator.validate(item)

                    for name, item in items.items():
                        processor(item)
                        data[k + 's'][name] = item

                except Exception as ex:
                    raise Exception("error while processing " + file) from ex

    # Postprocessing: load metadata of gate driver chip for each inverter
    for odrive in data['odrives'].values():
        for inv in odrive['inverters']:
            if len(inv['drv'].keys()) == 1 and '$ref' in inv['drv'].keys():
                inv['drv'] = data['drvs'][inv['drv']['$ref']]

    # Postprocessing: include inherited properties for each encoder
    for key, encoder in list(data['encoders'].items()):
        while 'inherits' in encoder:
            inherited_encoder = data['encoders'][encoder['inherits']]
            encoder.pop('inherits')
            encoder = {**inherited_encoder, **encoder}
        data['encoders'][key] = encoder

    return Database(data)

