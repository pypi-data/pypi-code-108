#######################
#   Lainupcomputer    #
#   ez_config v1.0    #
#######################
import json


def save(file_path, file):  # Save data to settings
    with open(file_path, "w") as f:
        json.dump(file, f, indent=2)


def read_file(file_path):  # Read all settings to process
    with open(file_path, "r") as f:
        file = json.load(f)
    return file


class ez_config:

    file_path = ""
    separator = ""
    debug = False

    def send_debug(self, message):
        if self.debug:
            print(message)

    def initialise(self, file_path, separator="#", debug=False):
        self.file_path = file_path
        self.separator = separator
        self.debug = debug
        there = True

        while there:
            if self.file_path != "":
                try:
                    with open(self.file_path, "r"):
                        self.send_debug("[*] Data found...")
                        break

                except FileNotFoundError:
                    with open(self.file_path, "w") as f:
                        f.write("{\n\n}")
                        self.send_debug("[*] Data created...")
            else:
                print("Insert: file_path!")

    def get(self, cfg="Configuration", data=""):  # get data from settings
        try:
            file = read_file(self.file_path)
            value = file[str(cfg)][data]
            self.send_debug(f"got {value} from {cfg}>{data}")
            return value

        except KeyError:
            self.send_debug(f"{cfg}>{data} Not Found")

    def edit(self, cfg="Configuration", data="", value=None):  # edit in settings
        try:
            file = read_file(self.file_path)
            file[str(cfg)][data] = value
            save(self.file_path, file)
            self.send_debug(f"edited {value} from {cfg}>{data}")
        except KeyError:
            self.send_debug(f"{value} for {cfg}>{data} Not Found")

    def add(self, cfg="Configuration", data=""):  # Add Data to settings
        file = read_file(self.file_path)
        file[str(cfg)] = {}

        for entry in data.split(self.separator):
            split_value = entry.split(":")
            file[str(cfg)][str(split_value[0])] = split_value[1]

        save(self.file_path, file)
        self.send_debug(f"added {cfg}>{data}")


