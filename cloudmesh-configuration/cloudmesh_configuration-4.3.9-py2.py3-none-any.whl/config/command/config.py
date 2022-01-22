import oyaml as yaml
from cloudmesh.common.FlatDict import flatten
from cloudmesh.common.Printer import Printer
from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.configuration.Config import Config
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command, map_parameters


class ConfigCommand(PluginCommand):

    # see https://github.com/cloudmesh/client/blob/main/cloudmesh_client/shell/plugins/KeyCommand.py
    # see https://github.com/cloudmesh/client/blob/main/cloudmesh_client/shell/plugins/AkeyCommand.py

    # noinspection PyUnusedLocal
    @command
    def do_config(self, args, arguments):
        """
        ::

           Usage:
             config  -h | --help
             config cat [less]
             config check
             config edit [ATTRIBUTE]
             config set ATTRIBUTE=VALUE
             config get ATTRIBUTE [--output=OUTPUT]
             config value ATTRIBUTE
             config cloud verify NAME [KIND]
             config cloud edit [NAME] [KIND]
             config cloud list NAME [KIND] [--secrets]
             config security add (--secret=REGEXP | --exception=REGEXP )
             config security rmv (--secret=REGEXP | --exception=REGEXP )
             config security list


           Arguments:
             ATTRIBUTE=VALUE  sets the attribute with . notation in the
                              configuration file.
             ATTRIBUTE        reads the attribute from the container and sets it
                              in the configuration file
                              If the attribute is a password, * is written instead
                              of the character included
             REGEXP           python regular expression

           Options:
              --name=KEYNAME        The name of a key
              --nopass              Indicates if private key is password protected
              --output=OUTPUT       The output format [default: yaml]

           Description:

             config check
                checks if the ssh key ~/.ssh/id_rsa has a password. Verifies it
                through entering the passphrase

             Key generation

                Keys can be generated with

                    cms key gen (ssh | pem)

                Key validity and password can be verified with

                    cms key verify (ssh | pem)

                key verify (ssh | pem) [--filename=FILENAME] [--pub]

                ssh-add

             Setting configuration


                config set ATTRIBUTE=VALUE

                    config set profile.name=Gregor

                In case the ATTRIBUTE is the name of a cloud defined under
                cloudmesh.cloud, the value will be written into the credentials
                attributes for that cloud this way you can safe a lot of
                typing. An example is

                    cms config set aws.AWS_TEST=Gregor

                which would write the AWS_TEST attribute in the credentials
                of the cloud aws. This can naturally be used to set for
                example username and password.


        """
        # d = Config()                #~/.cloudmesh/cloudmesh.yaml
        # d = Config(encryted=True)   # ~/.cloudmesh/cloudmesh.yaml.enc

        map_parameters(arguments,
                       "exception",
                       "keep",
                       "nopass",
                       "output",
                       "secrets")

        # source = arguments.SOURCE or path_expand("~/.cloudmesh/cloudmesh.yaml")
        # destination = source + ".enc"

        if arguments.cloud and arguments.edit and arguments.NAME is None:
            path = path_expand("~/.cloudmesh/cloudmesh.yaml")
            print(path)
            Shell.edit(path)
            return ""

        cloud = arguments.NAME
        kind = arguments.KIND
        if kind is None:
            kind = "cloud"

        configuration = Config()

        if arguments.cloud and arguments.verify:
            service = configuration[f"cloudmesh.{kind}.{cloud}"]

            result = {"cloudmesh": {"cloud": {cloud: service}}}

            action = "verify"
            banner(
                f"{action} cloudmesh.{kind}.{cloud} in ~/.cloudmesh/cloudmesh.yaml")

            print(yaml.dump(result))

            flat = flatten(service, sep=".")

            for attribute in flat:
                if "TBD" in str(flat[attribute]):
                    Console.error(
                        f"~/.cloudmesh.yaml: Attribute cloudmesh.{cloud}.{attribute} contains TBD")

        elif arguments.cloud and arguments.list:
            service = configuration[f"cloudmesh.{kind}.{cloud}"]
            result = {"cloudmesh": {"cloud": {cloud: service}}}

            action = "list"
            banner(
                f"{action} cloudmesh.{kind}.{cloud} in ~/.cloudmesh/cloudmesh.yaml")

            lines = yaml.dump(result).splitlines()
            secrets = not arguments.secrets
            result = Config.cat_lines(lines, mask_secrets=secrets)
            print(result)

        elif arguments.cloud and arguments.edit:

            #
            # there is a duplicated code in config.py for this
            #
            action = "edit"
            banner(
                f"{action} cloudmesh.{kind}.{cloud}.credentials in ~/.cloudmesh/cloudmesh.yaml")

            credentials = configuration[f"cloudmesh.{kind}.{cloud}.credentials"]

            print(yaml.dump(credentials))

            for attribute in credentials:
                if "TBD" in credentials[str(attribute)]:
                    value = credentials[attribute]
                    result = input(f"Please enter {attribute}[{value}]: ")
                    credentials[attribute] = result

            # configuration[f"cloudmesh.{kind}.{cloud}.credentials"] = credentials

            print(yaml.dump(
                configuration[f"cloudmesh.{kind}.{cloud}.credentials"]))

        elif arguments["edit"] and arguments["ATTRIBUTE"]:

            attribute = arguments.ATTRIBUTE

            config = Config()

            config.edit(attribute)

            config.save()

            return ""

        elif arguments.cat:

            content = Config.cat()

            import shutil
            columns, rows = shutil.get_terminal_size(fallback=(80, 24))

            lines = content.splitlines()

            counter = 1
            for line in lines:
                if arguments.less:
                    if counter % (rows - 2) == 0:
                        x = input()
                        if x != '' and 'q' in x.lower():
                            return ""
                print(line)
                counter += 1

            return ""

        elif arguments.check:

            Config.check()

        elif arguments.set:

            config = Config()
            clouds = config["cloudmesh.cloud"].keys()

            line = arguments["ATTRIBUTE=VALUE"]
            attribute, value = line.split("=", 1)

            cloud, field = attribute.split(".", 1)

            if cloud in clouds:
                attribute = f"cloudmesh.cloud.{cloud}.credentials.{field}"

            elif not attribute.startswith("cloudmesh."):
                attribute = f"cloudmesh.{attribute}"

            config[attribute] = value
            config.save()

        elif arguments.value:

            config = Config()

            attribute = arguments.ATTRIBUTE
            if not attribute.startswith("cloudmesh."):
                attribute = f"cloudmesh.{attribute}"

            try:
                value = config[attribute]
                if type(value) == dict:
                    raise Console.error("the variable is a dict")
                else:
                    print(f"{value}")

            except Exception as e:
                print(e)
                return ""

        elif arguments.get:

            print()

            config = Config()
            clouds = config["cloudmesh.cloud"].keys()

            attribute = arguments.ATTRIBUTE

            try:
                cloud, field = attribute.split(".", 1)
                field = f".{field}"
            except:
                cloud = attribute
                field = ""

            if cloud in clouds:
                attribute = f"cloudmesh.cloud.{cloud}{field}"
            elif not attribute.startswith("cloudmesh."):
                attribute = f"cloudmesh.{attribute}"

            try:
                value = config[attribute]
                if type(value) == dict:
                    print(Printer.write(value, output=arguments.output))
                else:
                    print(f"{attribute}={value}")

            except Exception as e:
                print(e)
                return ""

        return ""
