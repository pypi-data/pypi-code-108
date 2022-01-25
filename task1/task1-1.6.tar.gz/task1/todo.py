import pickle
import time
import win10toast
from os.path import abspath

file = abspath(__file__)[:-2] + 'data'


def addTodos(name, date, priority = "Low"):
    try:
        with open(file, 'rb') as f:
            todos = pickle.load(f)
    except FileNotFoundError:
        todos = {}

    finally:
        todos[name] = [date, priority]
        with open(file, 'wb') as f:
            pickle.dump(todos, f)


def getAllTodos():
    with open(file, 'rb') as f:
        todos = pickle.load(f)
    alltodosdata = []
    for key, value in todos.items():
        alltodosdata.append([key, value[0], value[1]])
    return alltodosdata


def deleteTODO(name):
    with open(file, 'rb+') as f:
        todos = pickle.load(f)
        del todos[name]
        f.seek(0)
        f.truncate(0)
        pickle.dump(todos, f)


class TODOHandler:
    def __init__(self):
        pass

    def start(self):
        def _start():
            todos = getAllTodos()
            print(todos)
            latestdate = min(int(i[1]) for i in todos)
            name = None
            for todo in todos:
                if int(todo[1]) == latestdate:
                    name = todo[0]

            if name is not None: deleteTODO(name)
            return name, latestdate

        print("Started TODO service")
        while True:
            # try:
            print("Trying to find TODO")
            name, latestdate = _start()
            if name is not None:
                print(f"Next todo is  {name} in  {latestdate}")
                time.sleep(latestdate)  # assume tht it is in seconds
                win10toast.ToastNotifier().show_toast("Elsa", name)
            else:
                print("No TODO found")
                time.sleep(10)


todohandler = TODOHandler()
if __name__ == "__main__":
    addTodos("test1", 2)
    addTodos("test2", 10)
    todohandler.start()
