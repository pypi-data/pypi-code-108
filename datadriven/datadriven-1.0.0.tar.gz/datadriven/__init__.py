import functools
import itertools
import inspect


def wrap_func(f, name, args):
    @functools.wraps(f)
    def func(*fargs):
        return f(*(fargs + args.args), **args.kwargs)

    func.__name__ = name
    return func


def datadriven(**testcases):
    """
    You should decorate tests with datadriven if you want to pass data to them
    (and have them called multiple times).
    For example, declaring a test method like this:
        @datadriven(
            dataA=Args(paramA="foo"),
            dataB=Args("hello", paramB="world")
        )
        def test_method(self, paramA, paramB=None):
            pass
    is equivalent to writing:
        def test_method_dataA(self):
            decorated_test_method("foo")
        def test_method_dataB(self):
            decorated_test_method("hello", "world")
    Note that test_method is removed from the class.
    Caveats:
     * The decorated test method is removed from the class (otherwise unittest would try to run it)
     * The decorated test method must begin with "test" since its name is used as a prefix
       in the generated test cases
    """

    def wrapper(f):
        frame_locals = inspect.currentframe().f_back.f_locals

        for test_name, args in testcases.items():
            name = f.__name__ + "_" + test_name
            frame_locals[name] = wrap_func(f, name, args)

        f.__test__ = False

    return wrapper


def matrix_datadriven(matrix):
    """
    You should decorate tests with matrix_datadriven if you want to pass data to a test, and
    the test should work for every combination of this data.
    So, declaring a test method like this:
        @matrix_datadriven([
            dict(student_a=Args("maria"), student_b=Args("jose")),
            dict(class_a=Args("literature"), class_b=Args("math")),
        ])
        def test_method(self, student, class):
            pass
    is equivalent to writing:
        def test_method_student_a_class_a(self):
            decorated_test_method("maria", "literature")
        def test_method_student_a_class_b(self):
            decorated_test_method("maria", "math")
        def test_method_student_b_class_a(self):
            decorated_test_method("jose", "literature")
        def test_method_student_b_class_b(self):
            decorated_test_method("jose", "math")
    Note that test_method is removed from the class.
    Caveats:
     * The decorated test method is removed from the class (otherwise unittest would try to run it)
     * The decorated test method must begin with "test" since its name is used as a prefix
       in the generated test cases
    *  You should be careful not to repeat keyword arguments between rows of the matrix.
       The program will fail badly if you do that.
    """

    def get_testcases():
        dimensions = [list(dimension.items()) for dimension in matrix]
        for combination in itertools.product(*dimensions):
            test_name = "_".join(name for name, _ in combination)
            test_args, test_kwargs = [], {}

            for _, args in combination:
                test_args.extend(args.args)
                test_kwargs.update(args.kwargs)

            yield test_name, Args(*test_args, **test_kwargs)

    return datadriven(**dict(get_testcases()))


class Args:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
