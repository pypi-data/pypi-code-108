from typing import Callable



class DecoratorCls:

    def retry_mechanism(function: Callable):
        def retry(self, *args, **kwargs):
            try:
                print("Run the function ...")
                function(self, *args, **kwargs)
            except Exception as e:
                print("Catch the exception!")
                print(e)
            else:
                print("Run successfully!")
            finally:
                print("Test done.")
        return retry


    def target_fun(self):
        print("This is a testing function.")
        # self.retry_mechanism(function=self.target_fun_with_retry)


    @retry_mechanism
    def target_fun_with_retry(self, *args, **kwargs):
        if args or kwargs:
            print("get args: ", args)
            print(" or ")
            print("get kwargs: ", kwargs)
        print("Is it raise exception?")
        raise Exception("Just for test")



if __name__ == '__main__':

    __dc = DecoratorCls()
    __dc.target_fun()
    __dc.target_fun_with_retry("arg1", "arg2")
    __dc.target_fun_with_retry(par1="par1", par2="par2")
