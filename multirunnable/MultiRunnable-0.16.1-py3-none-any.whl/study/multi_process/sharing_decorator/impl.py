from multirunnable.test.target import ACls



class AACls(ACls):

    def fun_a(self):
        print("This is function a.")
        print(f"ACls before Cls_Val: {self.Cls_Val}")
        self.Cls_Val += 1
        print(f"ACls after Cls_Val: {self.Cls_Val}")

