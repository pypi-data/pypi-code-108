import argparse

from sumoappclient.pkggenerator.aws import AWSPkgGen
from sumoappclient.pkggenerator.onprem import OnPremPkgGen
from sumoappclient.pkggenerator.setupgen import SetupGen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", '--env', dest='env', choices=["onprem", "aws", "gcp", "azure"],
                        default="onprem", help='Select the environment on which the package is deployed.')

    parser.add_argument("-d", '--deploy', dest='deploy', choices=["prod", "test", "local"],
                         default=False, help='To deploy the package (default: False)')

    parser.add_argument("-c", '--config', dest='configpath', help='Path of the metadata file')

    parser.add_argument("-pc", '--python-cmd', required=False, dest='python_cmd', default="python", help='Python cmd python or python3')
    parser.add_argument("-g", '--generate', required=False, dest='target_folder', default=None, help='Path of the metadata file')
    args = parser.parse_args()

    if args.target_folder:
        SetupGen(args.target_folder, args.configpath, args.python_cmd).generate_setup_files()
    else:
        if args.env == "onprem":
            OnPremPkgGen(args.configpath, args.python_cmd).build_and_deploy(args.deploy)
        elif args.env == "aws":
            AWSPkgGen(args.configpath, args.python_cmd).build_and_deploy(args.deploy)
        else:
            print("%s environment is currently not supported" % args.env)


if __name__ == '__main__':
    main()
