class Population:

    def __init__(self):
        self.in_initial_population: bool = None
        self.in_denominator: bool = None
        self.in_numerator: bool = None

    def set_initial_population(self, flag: bool):
        self.in_initial_population = flag
        self.in_denominator = flag
        self.in_numerator = flag

    def set_denominator(self, flag: bool):
        self.in_denominator = flag
        self.in_numerator = flag

    def set_numerator(self, flag: bool):
        self.in_numerator = flag
