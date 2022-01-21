from pint import UnitRegistry

class Units:

    def __init__(self, length="m",
                 time="s",
                 mass="kg",
                 angle="rad",
                 temperature="K",
                 luminosity="cd",
                 current="A",
                 substance="mol"):
        self.ureg = UnitRegistry()

        self._validate_unit(length, "[length]")
        self.length = self.ureg(length)

        self._validate_unit(time, "[time]")
        self.time = self.ureg(time)

        self._validate_unit(mass, "[mass]")
        self.mass = self.ureg(mass)

        self._validate_unit(angle, "dimensionless")
        self.angle = self.ureg(angle)

        self._validate_unit(temperature, "[temperature]")
        self.temperature = self.ureg(temperature)

        self._validate_unit(luminosity, "[luminosity]")
        self.luminosity = self.ureg(luminosity)

        self._validate_unit(current, "[current]")
        self.current = self.ureg(current)

        self._validate_unit(substance, "[substance]")
        self.substance = self.ureg(substance)

        self.dimensionless = self.ureg("dimensionless")

    def _validate_unit(self, unit, label):
        unit = self.ureg(unit)

        if str(unit.dimensionality) != label:
            raise ValueError(f"Expected dimensionality {label}, got {unit.dimensionality} instead!")
