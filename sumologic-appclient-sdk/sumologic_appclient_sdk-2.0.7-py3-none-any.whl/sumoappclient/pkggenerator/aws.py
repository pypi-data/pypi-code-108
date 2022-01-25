# -*- coding: future_fstrings -*-
import os
import sys
import shutil
import yaml
import zipfile
import json

from sumoappclient.configmanager.base import BaseConfigHandler

if __name__ == "__main__":
    cur_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, cur_dir)

from sumoappclient.pkggenerator.base import PkgGenerator
from sumoappclient.pkggenerator.utils import upload_code_in_S3, copytree
from sumoappclient.common.utils import create_dir, read_yaml_file, read_first_file


class AWSPkgGen(PkgGenerator):

    sumo_content_account_id = 956882708938
    app_sdk_package_name = "sumologic-appclient-sdk"

    def __init__(self, configpath, *args, **kwargs):
        super(AWSPkgGen, self).__init__(configpath, *args, **kwargs)
        self.deploy_type = "local"

    def setup_env(self):
        self.remove_unwanted_files(self.project_dir)
        target_dir = os.path.join(self.project_dir, "target")
        create_dir(target_dir)
        self.aws_target_dir = os.path.join(target_dir, "aws")
        self.log.info(f"creating aws target directory {self.aws_target_dir}")
        create_dir(self.aws_target_dir)
        self.is_layer_enabled = self.deploy_config["ENABLE_LAYER"]

    def get_param_name(self, s):
        return s.title().replace("_", "")

    def _get_template_params(self):
        template_params = set()
        for section, section_cfg in self.base_config.items():
            for k, v in section_cfg.items():
                if v is None:
                    param_name = self.get_param_name(k)
                    template_params.add(param_name)

        return template_params

    def get_function_name(self):
        return "%sFunction" % self.deploy_config["APPNAME_SINGLE"]

    def create_parameters(self, sam_template_path, secret_params, secret_exist):
        self.log.debug(f"adding parameters {sam_template_path}")
        sam_config = read_yaml_file(sam_template_path)
        function_name = self.get_function_name()
        vars = sam_config["Resources"][function_name]["Properties"]['Environment']["Variables"]
        sam_config["Parameters"] = params = sam_config["Parameters"] or {}
        for section, section_cfg in self.base_config.items():
            for k, v in section_cfg.items():
                if v is None:
                    param_name = self.get_param_name(k)
                    params[param_name] = {"Type": "String"}
                    if k in secret_params:
                        vars[k] = {"Fn::If": ["create_secret", secret_params[k], {"Ref": param_name}]}
                    else:
                        vars[k] = {"Ref": param_name}
        if secret_exist:
            vars["DECRYPT_KEYS"] = {"Fn::If": ["create_secret", 'true', 'false']}
        with open(sam_template_path, "w") as f:
            f.write(yaml.dump(sam_config, default_flow_style=False))

    def generate_template(self):
        template_path = os.path.join(self.project_dir, "template.yaml")
        if not os.path.isfile(template_path):
            secret_exist, secret_params, env_var = self.get_secrets()
            base_sam_template_path = os.path.join(self.RESOURCE_FOLDER, "aws", self.get_template_name(secret_exist))
            target_filepath = os.path.join(self.aws_target_dir, "samtemplate.yaml")
            self.log.info(f"generating_template {target_filepath}")
            env = {**self.deploy_config, **env_var} if secret_exist else self.deploy_config
            self.generate_file(base_sam_template_path, env, target_filepath)
            self.create_parameters(target_filepath, secret_params, secret_exist)
            shutil.copy(target_filepath, template_path)
        return template_path

    # This method should be updated in case more secret type are added to the SDK for AWS.
    @staticmethod
    def get_template_name(secret_exist):
        if secret_exist:
            return "basesamwithkms.yaml"
        else:
            return "basesamtemplate.yaml"

    def get_secrets(self):
        secret_exist = False
        env_var = {}
        keys = {}
        if "Secrets" in self.base_config:
            secret_section = self.base_config["Secrets"]
            if "KEYS" in secret_section:
                secret_exist = True
                keys, secret_strings = self.get_secret_string(secret_section["KEYS"])
                env_var["ENCRYPT_KEYS"] = ", ".join(keys.keys())
                env_var["SECRET_STRING"] = json.dumps(secret_strings["AwsSecretManager"])
        return secret_exist, keys, env_var

    # This method should be updated in case of new Decryption methods
    def get_secret_string(self, secret_keys):
        secret_string = {"AwsSecretManager": {}, }
        keys = {}
        for key, value in secret_keys.items():
            if value == "AwsSecretManager":
                secret_string[value][key] = "${" + self.get_param_name(key) + "}"
                keys[key] = {"Ref": "SumoLogicSecret"}
        return keys, secret_string

    def deploy_package(self, packaged_template_path, aws_region):
        # Todo create layer, create and publish SAM
        # sam package --template-file MongoDBAtlas.yaml --s3-bucket $SAM_S3_BUCKET  --output-template-file packaged_MongoDBAtlas.yaml

        self.log.info(f"deploying template in {os.getenv('AWS_PROFILE')} Region: {aws_region}")
        env_vars = []
        template_params = self._get_template_params()
        cfg_locations = BaseConfigHandler.get_file_locations('', self.deploy_config['COLLECTION_CONFIG'])
        user_cfg, path = read_first_file(cfg_locations)
        for section, section_cfg in user_cfg.items():
            for k, v in section_cfg.items():
                param_name = self.get_param_name(k)
                if param_name in template_params:
                    env_vars.append(f"{param_name}={v}")

        cmd = ["sam", "deploy", "--template-file", packaged_template_path, "--stack-name", f"testing{self.deploy_config['APPNAME_SINGLE']}", "--capabilities", "CAPABILITY_IAM", "--region", aws_region]
        if env_vars:
            cmd.extend(["--parameter-overrides", *env_vars])
        resp = self.run_command(cmd)
        self.log.debug(f"deploying template resp: {resp}")

    def copy_requirement_file(self, build_folder):
        requirement_filepath = os.path.join(self.project_dir, "requirements.txt")
        shutil.copy(requirement_filepath, build_folder)

    def install_deps(self, build_folder):
        # Todo add support for aws_requirements.txt for dependencies only for aws environment
        os.chdir(build_folder)
        self.log.debug(f"changing to build dir: {os.getcwd()}")
        install_cmd_args = ["install"]
        if self.deploy_type == "test":
            install_cmd_args.extend(["--extra-index-url", "https://test.pypi.org/simple/"])
        if self.is_layer_enabled:
            if build_folder == self.get_layer_folder():
                # excluding app sdk from layers folder because of https://github.com/asottile/future-fstrings/issues/49
                self.copy_requirement_file(build_folder)
                resp = self.run_command(["grep", "-ivE", self.app_sdk_package_name, "requirements.txt"])
                dependencies = resp.stdout.decode().split()
                self.log.info(f"installing dependencies {dependencies}")
                self.run_command([self.PIP_CMD, *install_cmd_args, *dependencies, "-t", "."])
            else:
                # installing app sdk in source folder
                requirement_filepath = os.path.join(self.project_dir, "requirements.txt")
                resp = self.run_command(["grep", "-iE", self.app_sdk_package_name, requirement_filepath])
                app_sdk_package_name_with_version = resp.stdout.strip(b'"\n').decode()
                self.run_command([self.PIP_CMD, *install_cmd_args, app_sdk_package_name_with_version, "-t", "."])
        else:
            self.copy_requirement_file(build_folder)
            self.log.info(f"installing all dependencies")
            self.run_command([self.PIP_CMD, *install_cmd_args, "-r", "requirements.txt", "-t", "."])

        for filename in ["concurrent", "futures-3.1.1.dist-info"]:
            filepath = os.path.join(build_folder, filename)
            if os.path.isdir(filepath):
                shutil.rmtree(filepath)

    def add_layer_arn(self, layer_name, layer_version, template_file_path):

        if os.path.isfile(template_file_path) and self.is_layer_enabled:
            layer_arn = f'''arn:aws:lambda:${{AWS::Region}}:{self.sumo_content_account_id}:layer:{layer_name}:{layer_version}'''
            self.log.debug(f"adding layer arn {layer_arn} in {template_file_path}")
            sam_config = read_yaml_file(template_file_path)
            function_name = self.get_function_name()
            sam_config["Resources"][function_name]["Properties"]['Layers'] = [{"Fn::Sub": layer_arn}]

            with open(template_file_path, "w") as f:
                f.write(yaml.dump(sam_config, default_flow_style=False))

        return template_file_path

    def remove_layer_arn_if_exists(self, template_file_path):
        layer_name = self.get_layer_name()
        if os.path.isfile(template_file_path):
            self.log.debug(f"removing layer arn in {template_file_path}")
            sam_config = read_yaml_file(template_file_path)
            function_name = self.get_function_name()
            if 'Layers' in sam_config["Resources"][function_name]["Properties"]:
                del sam_config["Resources"][function_name]["Properties"]['Layers']

            with open(template_file_path, "w") as f:
                f.write(yaml.dump(sam_config, default_flow_style=False))

        return template_file_path

    def get_next_layer_version(self, layer_version):
        layer_version = str(int(layer_version)+1)
        return layer_version

    def get_layer_version(self, layer_name, region="us-east-1"):
        layer_arn_cmd_response = self.run_command(["aws", "lambda", "list-layer-versions", "--layer-name",layer_name ,"--region", region, "--query", "LayerVersions[0].LayerVersionArn"])

        layer_arn_output = layer_arn_cmd_response.stdout.strip(b'"\n').decode()
        if layer_arn_output == "null":
            layer_version = "0"
        else:
            layer_version = layer_arn_output.rsplit(":")[-1]

        return layer_version

    def get_layer_name(self):
        return self.deploy_config["APPNAME_SINGLE"]+"-deps"

    def get_layer_folder(self):
        return os.path.join(self.aws_target_dir, "layer_build")

    def get_aws_regions(self):
        # Todo make below list dynamic
        return ("us-east-2", "us-east-1", "us-west-1", "us-west-2", "ap-south-1", "ap-northeast-2", "ap-southeast-1", "ap-southeast-2", "ap-northeast-1", "ca-central-1", "eu-central-1", "eu-west-1", "eu-west-2", "eu-west-3", "sa-east-1")

    def create_layer(self, template_file_path):
        layer_build_folder = self.get_layer_folder()
        create_dir(layer_build_folder)
        os.chdir(layer_build_folder)
        self.install_deps(layer_build_folder)
        layer_name = self.get_layer_name()
        layer_file_name = layer_name+".zip"
        layer_zip_filepath = self.create_zip(layer_build_folder, layer_file_name)
        layer_version = self.get_layer_version(layer_name)
        deploy_new_layer = input("Press y for deploying new layer %s %s > " % (layer_name, layer_version))
        if deploy_new_layer and deploy_new_layer.lower() == "y":
            layer_version = self.get_next_layer_version(layer_version)
            self.log.info("Creating layer %s %s" % (layer_name, layer_version))
            regions = self.get_aws_regions()
            for region in regions:
                self.log.debug(f"Deploying layer in ${region}")
                bucket_name = f"appdevzipfiles-{region}"
                upload_code_in_S3(layer_zip_filepath, bucket_name, region)
                publish_cmd_response = self.run_command(["aws", "lambda", "publish-layer-version", "--layer-name", layer_name, "--description", f"contains {self.deploy_config['APPNAME_SINGLE']} solution dependencies", "--license-info", "MIT", "--content", f"S3Bucket={bucket_name},S3Key={layer_file_name}", "--compatible-runtimes", "python3.7", "python3.6", "--region", region])

                publish_cmd_output = json.loads(publish_cmd_response.stdout.decode())
                self.log.debug("Created Layer: %s" % publish_cmd_output.get("LayerVersionArn"))
                perm_cmd_response = self.run_command(["aws", "lambda", "add-layer-version-permission", "--layer-name", layer_name,  "--statement-id", layer_name, "--version-number", layer_version, "--principal", "*", "--action", "lambda:GetLayerVersion", "--region", region])
            self.add_layer_arn(layer_name, layer_version, template_file_path)
        return layer_name, layer_version

    def create_build(self):
        # Todo convert pip/zip to non command based
        aws_build_folder = os.path.join(self.aws_target_dir, "build")
        create_dir(aws_build_folder)
        os.chdir(aws_build_folder)
        self.install_deps(aws_build_folder)
        src_dir = os.path.join(self.project_dir, self.deploy_config['SRC_FOLDER_NAME'])
        self.log.debug(f"copying src {src_dir}")
        copytree(src_dir, aws_build_folder)

        return aws_build_folder

    def create_zip(self, build_folder, zip_file_name):
        os.chdir(build_folder)
        self.log.debug(f"changing to build dir: {os.getcwd()}")
        zip_file_path = os.path.join(self.aws_target_dir, zip_file_name)
        self.log.info(f"creating zip file {zip_file_path}")
        # subprocess.run(["zip", "-r", zip_file_path, "."])
        zipf = zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk("."):
            for file in files:
                zipf.write(os.path.join(root, file))

        zipf.close()
        return zip_file_path

    def generate_packaged_template(self, template_file_path, SAM_S3_BUCKET):
        os.chdir(self.project_dir)
        packaged_template_path = os.path.join(self.project_dir, "packaged.yaml")
        sam_config = read_yaml_file(template_file_path)
        sam_version = sam_config['Metadata']['AWS::ServerlessRepo::Application']['SemanticVersion']
        s3prefix = f'''{self.deploy_config["APPNAME_SINGLE"]}/v{sam_version}'''
        self.run_command(["sam", "package", "--template-file", template_file_path, "--output-template-file", packaged_template_path,  "--s3-bucket", SAM_S3_BUCKET, "--s3-prefix", s3prefix])
        return packaged_template_path

    def publish_package(self, packaged_template_path, AWS_REGION):
        os.chdir(self.project_dir)
        publish_cmd_response = self.run_command(["sam", "publish", "--template", packaged_template_path, "--region", AWS_REGION])
        self.log.info("Publishing package %s" % publish_cmd_response)

    def build_and_deploy(self, deploy=False):
        self.deploy_type = deploy
        template_file_path = self.generate_template()
        aws_build_folder = self.create_build()
        if self.is_layer_enabled:
            layer_file_name, layer_version = self.create_layer(template_file_path)
        else:
            self.remove_layer_arn_if_exists(template_file_path)

        if deploy:
            AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
            if deploy == "prod":
                SAM_S3_BUCKET = "appdevstore"
                packaged_template_path = self.generate_packaged_template(template_file_path, SAM_S3_BUCKET)
                self.publish_package(packaged_template_path, AWS_REGION)
            elif deploy == "test":
                self.log.info("Use SAM_S3_BUCKET,AWS_REGION env variable to set your custom bucket other wise it uses appdevstore-test bucket in us-east-1 region of sumocontent aws account.")
                SAM_S3_BUCKET = os.getenv("SAM_S3_BUCKET", "appdevstore-test")
                with open(template_file_path, "r+") as f:
                    data = f.read()
                    data = data.replace("appdevstore", SAM_S3_BUCKET)
                    f.seek(0)
                    f.write(data)
                    f.truncate()
                packaged_template_path = self.generate_packaged_template(template_file_path, SAM_S3_BUCKET)
                self.deploy_package(packaged_template_path, AWS_REGION)
            else:
                SAM_S3_BUCKET = "appdevstore"
                packaged_template_path = self.generate_packaged_template(template_file_path, SAM_S3_BUCKET)


if __name__ == "__main__":
    deploy = False
    if len(sys.argv) > 1:
        configpath = sys.argv[1]
        if len(sys.argv) > 2:
            deploy = sys.argv[2]
    else:
        raise Exception("pass collection config path as param")
    AWSPkgGen(configpath).build_and_deploy(deploy)


