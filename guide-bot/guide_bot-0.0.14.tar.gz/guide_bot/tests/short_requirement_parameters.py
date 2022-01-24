from guide_bot.requirements import requirement_parameters as rpars


class Thing:
    def __init__(self, first_par=1, second_par=3.0, total=None):
        self.parameters = rpars.Parameters()

        self.parameters.add("first_par", first_par)
        self.parameters.add("second_par", second_par)
        self.parameters.add("total", total)

    def __getitem__(self, item):
        return self.parameters[item]


thing1 = Thing(first_par=[1,2,3], total=[10, 12, 14])
thing1.parameters.lock_parameters("first_par", "total")
thing2 = Thing()
thing2.parameters.preface_names("test_")



scan = rpars.InputConfiguratonIterator(thing1, thing2)

scan.reset_configuration()
while scan.next_state():
    print("")
    print("thing1:")
    print("  ", thing1["first_par"])
    print("  ", thing1["second_par"])
    print("  ", thing1["total"])
    print("thing2:")
    print("  ", thing2["test_first_par"])
    print("  ", thing2["test_second_par"])
    print("  ", thing2["test_total"])
    print("")

