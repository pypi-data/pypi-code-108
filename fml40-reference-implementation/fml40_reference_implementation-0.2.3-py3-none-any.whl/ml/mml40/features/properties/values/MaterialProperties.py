from ml.ml40.features.properties.values.value import Value


class MaterialProperties(Value):
    def __init__(self, namespace="mml40", name="", identifier=""):
        super().__init__(namespace=namespace, name=name, identifier=identifier)
        self.__max_amount_load_change = None
        self.__material_type = None
        self.__yield_strength = None
        self.__young_modulus = None
        self.__json_out = dict()

    @property
    def maxAmountLoadChange(self):
        return self.__max_amount_load_change

    @maxAmountLoadChange.setter
    def maxAmountLoadChange(self, value):
        self.__max_amount_load_change = value

    @property
    def materialType(self):
        return self.__material_type

    @materialType.setter
    def materialType(self, value):
        self.__material_type = value

    @property
    def yieldStrength(self):
        return self.__yield_strength

    @yieldStrength.setter
    def yieldStrength(self, value):
        self.__yield_strength = value

    @property
    def youngModulus(self):
        return self.__young_modulus

    @youngModulus.setter
    def youngModulus(self, value):
        self.__young_modulus = value

    def to_json(self):
        self.__json_out = super().to_json()
        if self.maxAmountLoadChange is not None:
            self.__json_out["maxAmountLoadChange"] = self.maxAmountLoadChange

        if self.materialType is not None:
            self.__json_out["materialType"] = self.materialType

        if self.yieldStrength is not None:
            self.__json_out["yieldStrength"] = self.yieldStrength

        if self.youngModulus is not None:
            self.__json_out["youngModulus"] = self.youngModulus

        return self.__json_out
