
import sys
import argparse
import trtpy
import subprocess
import os
import requests
from . import process_code_template

def get_trtpy_str_variables(prefix="trtpy."):
    trtpy_variables = []
    for item in dir(trtpy):
        if item.startswith("__") and item.endswith("__"):
            continue

        value = getattr(trtpy, item)
        if isinstance(value, str):
            trtpy_variables.append([prefix + item, value])
    return trtpy_variables

def do_get_env(args):
    trtpy.init(cuda_version=args.cuda, tensorrt_version=args.trt)
    print(f"Environment info: ")
    trtpy.print_pyc(trtpy.current_pyc)
    print("Done, Useage: 'import trtpy.init_default as trtpy'")

def do_info(args):
    if args.cuda is not None or args.trt is not None:
        trtpy.init(cuda_version=args.cuda, tensorrt_version=args.trt)

    print("Variables: ")
    for key, value in get_variable_template():
        print(f"  {key} = {value}")

    print(f"Current kernel module driver version: {trtpy.current_kernel_module_driver_version}")
    print(f"Support list: {len(trtpy.supported_pycs)} elements")
    for i, pyc in enumerate(trtpy.supported_pycs):
        trtpy.print_pyc(pyc, i)

def do_local_cpp_pkg(args):
    files = []
    if os.path.exists(trtpy.cpp_packages_root):
        files = os.listdir(trtpy.cpp_packages_root)

    found_package = []
    for file in files:
        path = os.path.join(trtpy.cpp_packages_root, file)
        if os.path.isdir(path):
            found_package.append([file, path])

    print(f"Found {len(found_package)} local cpp-packges")
    for i, (name, path) in enumerate(found_package):
        print(f"{i+1}. {name}          directory: {path}")

def do_get_cpp_env(args):
    name = args.name
    url = f"{trtpy.pypi_base_url}/cpp-packages/{name}.zip"
    from . import downloader

    file = os.path.join(downloader.CACHE_ROOT, "cpp-packages", f"{name}.zip")
    ok, md5 = downloader.download_and_verify_md5_saveto_file(url, file)
    if not ok:
        print(f"Failed to fetch cpp package {name}")
        return

    package_root = os.path.join(trtpy.cpp_packages_root, name)
    package_lib_root = os.path.join(package_root, "lib")
    if os.path.isdir(package_root):
        print(f"Remove old package files {package_root}")
        import shutil
        shutil.rmtree(package_root)

    print(f"Extract package {name} to {package_root}")
    downloader.extract_zip_to(file, trtpy.cpp_packages_root)
    if os.path.isdir(package_lib_root):
        print(f"Create symlink {package_lib_root}")
        trtpy.create_symlink_directory(package_lib_root, False)
    print("Done")

def do_if_exec():
    if not (len(sys.argv) > 1 and sys.argv[1] == "exec"):
        return

    args = sys.argv
    if len(args) > 2 and args[2] == "--help":
        return

    i = 2
    cuda_version = None
    trt_version = None
    trt_args = []
    while i < len(args):
        argv = args[i]
        if argv.startswith("--cuda"):
            if argv.startswith("--cuda="):
                cuda_version = argv[argv.find("=")+1:]
            elif i + 1 < len(args) and not args[i+1].startswith("-"):
                cuda_version = argv[i + 1]
                i += 1
        elif argv.startswith("--trt"):
            if argv.startswith("--trt="):
                trt_version = argv[argv.find("=")+1:]
            elif i + 1 < len(args) and not args[i+1].startswith("-"):
                trt_version = argv[i + 1]
                i += 1
        else:
            trt_args.append(argv)
        i += 1
    
    for i in range(len(trt_args)):
        if trt_args[i].find("~/") != -1:
            trt_args[i] = trt_args[i].replace("~/", os.path.expanduser("~") + "/")

    trtpy.init(cuda_version=cuda_version, tensorrt_version=trt_version)
    cmd = trtpy.trtexec_path + " " + " ".join(trt_args)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8", errors="replace")

    while True:
        realtime_output = p.stdout.readline()
        if realtime_output == "" and p.poll() is not None:
            break

        if realtime_output:
            print(realtime_output.strip(), flush=True)
    sys.exit(p.returncode)


def get_variable_template():
    variable_template = get_trtpy_str_variables("")
    variable_template.append(["CPP_PKG", f"{trtpy.cpp_packages_root}"])
    variable_template.append(["TRTPRO_INCLUDE", f"{trtpy.trtpy_root}/include"])
    variable_template.append(["SYS_LIB", f"{trtpy.trtpy_root}/lib"])
    variable_template.append(["PYTHON_LINK_NAME", f"{trtpy.pydll_link_name}"])
    variable_template.append(["PYTHON_LIB", f"{trtpy.pydll_path}"])
    
    if trtpy.inited:
        variable_template.append(["TRTPRO_LIB", f"{trtpy.libtrtpro_root}"])
        variable_template.append(["CUDA_HOME", f"{trtpy.nv_root}"])
        variable_template.append(["CUDA_INCLUDE", f"{trtpy.nv_root}/include/cuda"])
        variable_template.append(["CUDNN_INCLUDE", f"{trtpy.nv_root}/include/cudnn"])
        variable_template.append(["TENSORRT_INCLUDE", f"{trtpy.nv_root}/include/tensorRT"])
        variable_template.append(["PROTOBUF_INCLUDE", f"{trtpy.nv_root}/include/protobuf"])
        variable_template.append(["NVLIB64", f"{trtpy.nv_root}/lib64"])
    return variable_template


def do_get_templ(args):
    from . import downloader

    if args.saveto is None:
        args.saveto = args.template

    if os.path.isdir(args.saveto):
        while True:
            opt = input(f"{args.saveto} has exists, overwrite? (Y=yes, N=no): default [Y]:").lower()
            if opt == "": opt = "y"
            if opt != "y" and opt != "n":
                continue
                
            if opt == "n":
                print("Operation cancel.")
                return
            break

    if os.path.isfile(args.saveto):
        print(f"{args.saveto} is file")
        return

    trtpy.init(cuda_version=args.cuda, tensorrt_version=args.trt, load_lean_library=False)
    url = f"{trtpy.pypi_base_url}/code_template/{args.template}.zip"
    to = os.path.join(downloader.CACHE_ROOT, "code_template", f"{args.template}.zip")
    if not downloader.download_to_file(url, to):
        print(f"Template '{args.template}' not found")
        return

    print(f"Extract to {args.saveto} . ")
    namelist = downloader.extract_zip_to(to, args.saveto)
    os.remove(to)

    if not args.raw:
        print("Replace project variable")
        variable_template = get_variable_template()
        process_code_template.process_code_template(args.saveto, namelist, variable_template)
    print("Done!")


def do_templ_list(args):

    url = f"{trtpy.pypi_base_url}/code_template/list.txt"
    resp = requests.get(url)
    if resp.status_code != 200:
        print("Can not fetch template list")
        return

    list_info = resp.content.decode("utf-8").split("\n")
    list_info = [item.strip().split(";") for item in list_info if item.strip() != ""]

    print(f"Found {len(list_info)} items:")
    for i, line in enumerate(list_info):
        name = line[0] if len(line) > 0 else ""
        language = line[1] if len(line) > 1 else ""
        descript = line[2] if len(line) > 2 else ""
        print(f"-{i+1}. {name} [{language}] : {descript}")


def do_templ_search(args):
    url = f"{trtpy.pypi_base_url}/code_template/list.txt"
    resp = requests.get(url)
    if resp.status_code != 200:
        print("Can not fetch template list")
        return

    list_info = resp.content.decode("utf-8").split("\n")
    list_info = [item.strip().split(";") for item in list_info if item.strip() != ""]
    pattern = args.pattern
    def pattern_match(pattern, value : str):
        array = pattern.lower().split("%")
        value = value.lower()
        if len(array) == 0: return False
        i = 0
        p = 0
        while i < len(array):
            item = array[i]
            p = value.find(item, p)
            if p == -1: return False
            p += len(item)
            i += 1
        return True

    list_info = [item for item in list_info if pattern_match(pattern, item[0])]

    if len(list_info) == 0:
        print(f"Not found any items match for '{pattern}'")
        return

    print(f"Found {len(list_info)} items for '{pattern}':")
    for i, line in enumerate(list_info):
        name = line[0] if len(line) > 0 else ""
        language = line[1] if len(line) > 1 else ""
        descript = line[2] if len(line) > 2 else ""
        print(f"-{i+1}. {name} [{language}] : {descript}")

def do_mnist_test(args):
    trtpy.init(args.cuda, args.trt)
    trtpy.compile_onnx_to_file(1, trtpy.onnx_hub("mnist"), "mnist.trtmodel")
    os.remove("mnist.trtmodel")
    print("Done.")

def do_prep_vars(args):
    trtpy.init(args.cuda, args.trt)
    file_or_directory = args.file_or_directory
    if not os.path.exists(file_or_directory):
        print(f"No such file or directory, {file_or_directory}")
        return

    files = []
    if os.path.isdir(file_or_directory):
        for d, ds, fs in os.walk(file_or_directory):
            files.extend([os.path.join(d, f) for f in fs])
    else:
        files.append(file_or_directory)

    print("Replace project variable")
    variable_template = get_variable_template()
    process_code_template.process_code_template(None, files, variable_template)
    print("Done!")

if __name__ == "__main__":
    do_if_exec()
    parser = argparse.ArgumentParser()
    subp = parser.add_subparsers(dest="cmd")
    downloadp = subp.add_parser("get-env", help="download environment")
    downloadp.add_argument("--cuda", type=str, help="cuda version, 10.2, 11.2, 10, 11 etc.", default=None)
    downloadp.add_argument("--trt", type=str, help="trt version, 8.0, 8 etc.", default=None)
    
    execp = subp.add_parser("exec", help="same to ./trtexec")
    execp.add_argument("--cuda", type=str, help="cuda version, 10.2, 11.2, 10, 11 etc.", default=None)
    execp.add_argument("--trt", type=str, help="trt version, 8.0, 8 etc.", default=None)
    execp.add_argument("args", type=str, help="./trtexec args", default=None)

    subp.add_parser("list-templ", help="display all code template")
    templ_search_p = subp.add_parser("search-templ", help="search all code template")
    templ_search_p.add_argument("pattern", type=str, help="search name, yolo* etc.")

    p = subp.add_parser("get-templ", help="fetch code template")
    p.add_argument("template", type=str, help="template name: tensorrt-mnist cuda-sample")
    p.add_argument("saveto", type=str, help="save to directory, default[template name]", nargs="?")
    p.add_argument("--raw", action="store_true", help="do not replace variables")
    p.add_argument("--cuda", type=str, help="cuda version, 10.2, 11.2, 10, 11 etc.", default=None)
    p.add_argument("--trt", type=str, help="trt version, 8.0, 8 etc.", default=None)

    cpp_envp = subp.add_parser("get-cpp-pkg", help="download cpp package")
    cpp_envp.add_argument("name", type=str, help="package name")

    cpp_env_listp = subp.add_parser("local-cpp-pkg", help="display all installed local cpp package")

    p = subp.add_parser("info", help="display support list")
    p.add_argument("--cuda", type=str, help="cuda version, 10.2, 11.2, 10, 11 etc.", default=None)
    p.add_argument("--trt", type=str, help="trt version, 8.0, 8 etc.", default=None)

    p = subp.add_parser("prep-vars", help="replace local file variables")
    p.add_argument("file_or_directory", type=str, help=f"Project directory or file, file filter = {process_code_template.include_list}")
    p.add_argument("--cuda", type=str, help="cuda version, 10.2, 11.2, 10, 11 etc.", default=None)
    p.add_argument("--trt", type=str, help="trt version, 8.0, 8 etc.", default=None)

    p = subp.add_parser("mnist-test", help="test tensorrt with mnist")
    p.add_argument("--cuda", type=str, help="cuda version, 10.2, 11.2, 10, 11 etc.", default=None)
    p.add_argument("--trt", type=str, help="trt version, 8.0, 8 etc.", default=None)
    args = parser.parse_args()

    if args.cmd == "get-env":
        do_get_env(args)
    elif args.cmd == "info":
        do_info(args)
    elif args.cmd == "get-templ":
        do_get_templ(args)
    elif args.cmd == "list-templ":
        do_templ_list(args)
    elif args.cmd == "search-templ":
        do_templ_search(args)
    elif args.cmd == "get-cpp-pkg":
        do_get_cpp_env(args)
    elif args.cmd == "local-cpp-pkg":
        do_local_cpp_pkg(args)
    elif args.cmd == "mnist-test":
        do_mnist_test(args)
    elif args.cmd == "prep-vars":
        do_prep_vars(args)
    else:
        parser.print_help()