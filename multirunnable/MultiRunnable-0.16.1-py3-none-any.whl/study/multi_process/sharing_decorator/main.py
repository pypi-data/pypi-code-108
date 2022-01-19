from multiprocessing import Pool, Process
import sys

# package_multirunnable_path = str(pathlib.Path(__file__).absolute().parent.parent)
package_multirunnable_path = "/Bryant-Python-Package/apache-multirunnable"
print(f"final_path: {package_multirunnable_path}")
sys.path.append(package_multirunnable_path)

from multirunnable.test.target import ACls, B
from multirunnable.test.impl import AACls



def run(a: ACls, b: B):
    print(f"a instance ID: {id(a)}")
    print(f"b instance ID: {id(b)}")
    a.fun_a()
    b.fun_b()



def run_new():
    a = ACls()
    # a = ACls
    # aa = a()
    b = B()
    # b = BNo()

    print(f"a class ID: {id(a)}")
    print(f"a class ID with 16 bit bytes: {convert_to_16(a)}")
    # print(f"a instance ID: {id(aa)}")
    # print(f"a instance ID with 16 bit bytes: {convert_to_16(aa)}")
    print(f"b instance ID: {id(b)}")
    print(f"b instance ID with 16 bit bytes: {convert_to_16(b)}")

    # aa.fun_a()
    a.fun_a()
    b.fun_b()


class TestCls:

    def __init__(self):
        self._temp_a_instance = None


    @property
    def temp_a(self) -> AACls:
        if self._temp_a_instance is None:
            print(f"[DEBUG] It doesn't have instance right now.")
            self._temp_a_instance = AACls()
        print(f"[DEBUG] TestCls._temp_a_instance: {self._temp_a_instance}.")
        return self._temp_a_instance


    def function(self):
        # a = ACls()

        # a = AACls()

        a = self.temp_a

        # a = ACls
        # aa = a()

        b = B()
        # b = BNo()

        print(f"a class ID: {id(a)}")
        print(f"a class ID with 16 bit bytes: {convert_to_16(a)}")
        # print(f"a instance ID: {id(aa)}")
        # print(f"a instance ID with 16 bit bytes: {convert_to_16(aa)}")
        print(f"b instance ID: {id(b)}")
        print(f"b instance ID with 16 bit bytes: {convert_to_16(b)}")

        # aa.fun_a()
        a.fun_a()
        b.fun_b()


def convert_to_16(obj):
    return hex(int(str(id(obj)), 10))



if __name__ == '__main__':

    # _a = AClsNo()
    # _b = BNo()
    # _a = ACls()
    # _b = B()
    # _namespace = Global_Manager.Namespace()
    # _namespace.ACls = _a
    # _namespace.B = _b

    print("Initial process ...")
    # print(f"Global_Namespace.ACls: {Global_Namespace.ACls}")
    # print(f"Global_Namespace.B: {Global_Namespace.B}")
    # processes = [Process(target=run, args=(_a, _b)) for _ in range(3)]
    # processes = [Process(target=run_new) for _ in range(3)]
    _tc = TestCls()
    processes = [Process(target=_tc.function) for _ in range(3)]

    print("Run process ")
    for _p in processes:
        _p.run()

    print("End process ")
    for _p in processes:
        # _p.join()
        _p.close()


    process_pool = Pool(processes=3)


