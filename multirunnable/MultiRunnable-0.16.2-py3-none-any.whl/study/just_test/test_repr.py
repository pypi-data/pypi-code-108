
class OgCls:

    def test(self):
        print("This is test function in test class.")


class ACls:

    def __repr__(self):
        # return f"<object {self.__class__}>"
        return f"<object {self.__class__}>"


    def __str__(self):
        return f"This is str of class {self.__class__}"



class BCls(ACls):

    pass



if __name__ == '__main__':

    og_class = OgCls
    a_class = ACls
    b_class = BCls

    print("A class by print: ", a_class)
    print("B class by print: ", b_class)
    print("Og class by print: ", og_class)

    a_class_str = str(a_class)
    b_class_str = str(b_class)
    og_class_str = str(og_class)

    print(f"str class a: {a_class_str}")
    print(f"str class b: {b_class_str}")
    print(f"str class og: {og_class_str}")

    a_class_repr = repr(a_class)
    b_class_repr = repr(b_class)
    og_class_repr = repr(og_class)

    print(f"repr class a: {a_class_repr}")
    print(f"repr class b: {b_class_repr}")
    print(f"repr class og: {og_class_repr}")

    a_instance = a_class()
    b_instance = b_class()
    og_instance = og_class()

    print("A instance by print: ", a_instance)
    print("B instance by print: ", b_instance)
    print("Og instance by print: ", og_instance)

    a_instance_str = str(a_instance)
    b_instance_str = str(b_instance)
    og_instance_str = str(og_instance)

    print(f"str instance a: {a_instance_str}")
    print(f"str instance b: {b_instance_str}")
    print(f"str instance og: {og_instance_str}")

    a_instance_repr = repr(a_instance)
    b_instance_repr = repr(b_instance)
    og_instance_repr = repr(og_instance)

    print(f"repr instance a: {a_instance_repr}")
    print(f"repr instance b: {b_instance_repr}")
    print(f"repr instance og: {og_instance_repr}")
