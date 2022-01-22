class HelloWorld:
    def __init__(self, msg):
        self.msg = msg

    def say(self):
        print(self.msg)


if __name__ == "__main__":
    HelloWorld("Hi!").say()