
class TestLevel:

    print("Class level but not in __init__ and __new__ run init process.")

    def __new__(cls, *args, **kwargs):
        print("__new__ run inti process.")


    def __init__(self):
        print("__init__ run init process.")



if __name__ == '__main__':

    print("Just for set the object here.")
    tl = TestLevel

    print("Instanciate object.")
    tl_inst = tl()

