from typing import Callable



def retry_mechanism(function: Callable):
    def retry():
        try:
            print("Run the function ...")
            function()
        except Exception as e:
            print("Catch the exception!")
            print(e)
        else:
            print("Run successfully!")
        finally:
            print("Test done.")
    return retry


def target_fun():
    print("This is a testing function.")


@retry_mechanism
def target_fun_with_retry():
    print("Is it raise exception?")
    raise Exception("Just for test")



if __name__ == '__main__':

    target_fun()
    target_fun_with_retry()
