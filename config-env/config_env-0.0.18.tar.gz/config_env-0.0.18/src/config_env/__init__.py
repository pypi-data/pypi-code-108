import os
import glob
import collections.abc
import sys
sys.path.append(os.getcwd())

class ConfigEnv:
    def __init__(self) -> None:
        self.python_env = os.getenv("PYTHON_ENV")
        self.__run()

    def __cleanNullTerms(self, d: dict) -> dict:
        clean = {}
        for k, v in d.items():
            if isinstance(v, dict):
                nested = self.__cleanNullTerms(v)
                if len(nested.keys()) > 0:
                    clean[k] = nested
            elif v is not None:
                clean[k] = v
        return clean

    def __update_dictionary(self, d, u):
        for k, v in u.items():
            if isinstance(v, collections.abc.Mapping):
                d[k] = self.__update_dictionary(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    def __evaluate_environment_variables(self, config: dict) -> dict:
        for key, value in config.items():
            if isinstance(value, dict):
                self.__evaluate_environment_variables(value)
            else:
                config.update({key: os.getenv(value)})
        return config
           
    def __get_path_files(self):
        result = []
        for path in sys.path:
            for root, dirs, files in os.walk(path, topdown=True):
                for dir in dirs:
                    if dir == "configenv":
                        os.chdir(os.path.join(root, dir))
                        for file in glob.glob("*.json"):
                            result.append(os.path.join(root, dir, file))
                        if len(result) > 0:
                            break
                if len(result) > 0:
                    break
            if len(result) > 0:
                break

        if not result:
            for path in sys.path:
                for root, dirs, files in os.walk(path, topdown=False):
                    for dir in dirs:
                        if dir == "configenv":
                            os.chdir(os.path.join(root, dir))
                            for file in glob.glob("*.json"):
                                result.append(os.path.join(root, dir, file))
                            if len(result) > 0:
                                break
                    if len(result) > 0:
                        break
                if len(result) > 0:
                    break
        return result     

    def __run(self):
        files_path = self.__get_path_files()
        files = [i.split('/')[-1] for i in files_path]
        self.config = {}
        filenames = []
        for file, file_path in zip(files, files_path) :
            if os.stat(file_path).st_size != 0:
                filename = file.split(".")[0].replace("-", "_") + "_config"
                filenames.append(filename)
                exec(filename + "= eval(open(file_path).read())")

        if self.python_env == None or "DEFAULT":
            if "default.json" in files:
                exec("self.config.update(default_config)")
            else:
                raise FileNotFoundError("Missing config file default.json")

        if self.python_env not in [None, "DEFAULT"]:
            if (self.python_env.lower().replace('-','_')+".json") in files:
                env_name = self.python_env.lower() + "_config"
                self.config = self.__update_dictionary(self.config, eval(env_name))
            else:
                raise FileNotFoundError("Missing config file"+ self.python_env.lower()+ ".json")

        if "custom_environment_variables.json" in files:
            custom_config = self.__evaluate_environment_variables(
                eval("custom_environment_variables_config")
            )
            custom_config_cleaned = self.__cleanNullTerms(custom_config)
            self.config = self.__update_dictionary(self.config, custom_config_cleaned)
        os.chdir("..")
        return self.config
    
    def get(self, values):
        values_list = values.split(".")
        if len(values_list) == 1 and not values_list[0]: 
            return self.config
        else:
            command = "self.config"
            for value in values_list:
                command+=".get('"+value+"')"
            try:
                return eval(command)
            except:
                return None
