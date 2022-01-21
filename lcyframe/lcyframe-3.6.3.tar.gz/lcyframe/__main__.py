import sys, os, shutil

def main():
    args = sys.argv
    cwd_path = os.getcwd()
    root_path = os.path.abspath(os.path.dirname(__file__))
    print(root_path)
    if len(args) == 1:
        file_name = args[0]
        file_path = cwd_path
    elif len(args) == 2:
        if os.path.isdir(args[1]):
            file_name = "demo"
            file_path = args[1]
        else:
            file_name = args[1]
            file_path = cwd_path
    elif len(args) == 3:
        file_name = args[1]
        file_path = args[2]
    else:
        file_name = "demo"
        file_path = cwd_path

    if not os.path.exists(file_path):
        print(" ")
        print("Error: No such file or directory '%s'" % file_path)
        print(" ")
        return

    if file_name == "demo" and os.path.exists(os.path.join(file_path, file_name)):
        file_name += "_lcyframe"

    if os.path.exists(os.path.join(file_path, file_name)):
        print(" ")
        print("Error: Directory already exists" + " '%s'" % os.path.join(file_path, file_name))
        print(" ")
        return

    shutil.copytree(os.path.join(root_path, 'demo'), os.path.join(file_path, file_name))

    if os.path.basename(cwd_path) == "lcyframe":
        pass
        # print("##################################################################################################")
        # print("#    Please run like this 'python -mlcyframe demo_name' in your directory to create a Demo !     #")
        # print("##################################################################################################")

    if os.path.exists(os.path.join(file_path, file_name)):
        print("##################################################################################################")
        print("#                                                                                                #")
        print("#     Created Successfully: '%s'" % os.path.join(file_path, file_name))
        print("#                                                                                                #")
        print("##################################################################################################")


if __name__ == '__main__':
    sys.exit(main())