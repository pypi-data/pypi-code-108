
import sys
import argparse
import trtpy
import subprocess
import os
import requests
from . import process_code_template
from . import downloader
import json
import shutil

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
    print("Done, Usage: 'import trtpy.init_default as trtpy'")
    return 0

def do_info(args):
    if args.init or args.cuda is not None or args.trt is not None:
        trtpy.init(cuda_version=args.cuda, tensorrt_version=args.trt, load_lean_library=args.tryload)

    print("Variables: ")
    for key, value in get_variable_template():
        print(f"  {key} = {value}")

    if trtpy.inited:
        print(f"Current kernel module driver version: {trtpy.current_kernel_module_driver_version}")
        print(f"Support list: {len(trtpy.supported_pycs)} elements")
        for i, pyc in enumerate(trtpy.supported_pycs):
            trtpy.print_pyc(pyc, i)
    return 0

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
    return 0

def do_get_cpp_pkg(args):
    name = args.name
    url = f"{trtpy.pypi_base_url}/cpp-packages/{name}.zip"

    file = os.path.join(downloader.CACHE_ROOT, "cpp-packages", f"{name}.zip")
    ok, md5 = downloader.download_and_verify_md5_saveto_file(url, file)
    if not ok:
        print(f"Failed to fetch cpp package {name}")
        return 1

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
    return 0

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
    variable_template.append(["PYTHON_INCLUDE", f"{sys.exec_prefix}/include/{trtpy.pydll_link_name}"])
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

def get_inv_variable_template():
    variable_template = []
    variable_template.append(["CPP_PKG", f"{trtpy.cpp_packages_root}"])
    variable_template.append(["TRTPRO_INCLUDE", f"{trtpy.trtpy_root}/include"])
    variable_template.append(["SYS_LIB", f"{trtpy.trtpy_root}/lib"])
    variable_template.append(["PYTHON_LINK_NAME", f"{trtpy.pydll_link_name}"])
    variable_template.append(["PYTHON_INCLUDE", f"{sys.exec_prefix}/include/{trtpy.pydll_link_name}"])
    variable_template.append(["PYTHON_LIB", f"{trtpy.pydll_path}"])
    
    if trtpy.inited:
        variable_template.append(["TRTPRO_LIB", f"{trtpy.libtrtpro_root}"])
        variable_template.append(["CUDA_HOME", f"{trtpy.nv_root}"])
        variable_template.append(["CUDA_INCLUDE", f"{trtpy.nv_root}/include/cuda"])
        variable_template.append(["CUDNN_INCLUDE", f"{trtpy.nv_root}/include/cudnn"])
        variable_template.append(["TENSORRT_INCLUDE", f"{trtpy.nv_root}/include/tensorRT"])
        variable_template.append(["PROTOBUF_INCLUDE", f"{trtpy.nv_root}/include/protobuf"])
        variable_template.append(["NVLIB64", f"{trtpy.nv_root}/lib64"])

    variable_template = sorted(variable_template, key=lambda x:len(x[1]), reverse=True)
    return variable_template

def do_get_templ(args):
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
                return 0
            break

    if os.path.isfile(args.saveto):
        print(f"{args.saveto} is file")
        return 1

    if not args.raw:
        trtpy.init(cuda_version=args.cuda, tensorrt_version=args.trt, load_lean_library=False)

    url = f"{trtpy.pypi_base_url}/code_template/{args.template}.zip"
    cache_zip = os.path.join(downloader.CACHE_ROOT, "code_template", f"{args.template}.zip")
    if not args.download and os.path.exists(cache_zip):
        print(f"Use cache {cache_zip}")
    elif not downloader.download_to_file(url, cache_zip):
        print(f"Template '{args.template}' not found")
        return 1

    print(f"Extract to {args.saveto} . ")
    namelist = downloader.extract_zip_to(cache_zip, args.saveto)

    if not args.raw:
        print("Replace project variable")
        variable_template = get_variable_template()
        process_code_template.process_code_template(args.saveto, namelist, variable_template)

    print("Done!")
    return 0

def remove_tree_keep_father(path):
    files = os.listdir(path)
    for file in files:
        full_path = os.path.join(path, file)
        print(f"Delete {full_path}")
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)

def extract_series_templ(meta, saveto, raw, download, cuda, trt):

    series_name = meta["name"]
    current_index = meta["current-index"]
    templ_list = meta["list-templ"]
    select_item = templ_list[current_index]
    item_name = select_item[0].strip()
    if item_name == "" or item_name == "." or item_name == ".." or item_name.find("/") != -1:
        print(f"Invalid series templ name [{item_name}]")
        return

    templ_name = f"{series_name}-{item_name}"
    templ_url = f"{trtpy.pypi_base_url}/code_template/{templ_name}.zip"
    templ_cache_local_zip = os.path.join(downloader.CACHE_ROOT, "code_template", f"{templ_name}.zip")
    if not download and os.path.exists(templ_cache_local_zip):
        print(f"Use cache {templ_cache_local_zip}")
    elif not downloader.download_to_file(templ_url, templ_cache_local_zip):
        print(f"Template '{templ_name}' not found")
        return 1

    if os.path.isdir(saveto):
        print(f"Remove old files")
        remove_tree_keep_father(saveto)

    print(f"Extract to {saveto} . ")
    namelist = downloader.extract_zip_to(templ_cache_local_zip, saveto)

    if not raw:
        print("Replace project variable")
        trtpy.init(cuda_version=cuda, tensorrt_version=trt, load_lean_library=False)
        variable_template = get_variable_template()
        process_code_template.process_code_template(saveto, namelist, variable_template)

    series_directory = os.path.join(saveto, ".series")
    os.makedirs(series_directory, exist_ok=True)
    local_config_json = os.path.join(series_directory, "config.json")

    print(f"Save to {local_config_json}")
    json.dump(meta, open(local_config_json, "w"), indent=4, ensure_ascii=False)
    print(f"Done! current template is {templ_name}, {select_item[1]}")
    return 0

def do_get_series(args):
    if args.saveto is None:
        args.saveto = args.name

    if os.path.isdir(args.saveto):
        while True:
            opt = input(f"{args.saveto} has exists, overwrite? (Y=yes, N=no): default [Y]:").lower()
            if opt == "": opt = "y"
            if opt != "y" and opt != "n":
                continue
                
            if opt == "n":
                print("Operation cancel.")
                return 0
            break

    if os.path.isfile(args.saveto):
        print(f"{args.saveto} is file")
        return 1

    meta_url = f"{trtpy.pypi_base_url}/code_template/{args.name}.series.json"
    meta_cache_local_file = os.path.join(downloader.CACHE_ROOT, "code_template", f"{args.name}.series.json")
    if not args.download and os.path.exists(meta_cache_local_file):
        print(f"Use cache {meta_cache_local_file}")
    elif not downloader.download_to_file(meta_url, meta_cache_local_file):
        print(f"Series '{args.name}' not found")
        return 1

    meta = json.load(open(meta_cache_local_file))
    templ_list = meta["list-templ"]

    current_index = 0
    meta["current-index"] = current_index
    if len(templ_list) == 0:
        print(f"Series list-templ is empty")
        return 0

    return extract_series_templ(meta, args.saveto, args.raw, args.download, args.cuda, args.trt)


def do_change_proj(args):

    current_dir = os.path.abspath(".")
    config_json_file = os.path.join(current_dir, ".series", "config.json")
    if not os.path.isfile(config_json_file):
        print(f"Current is not series folder")
        return 1

    meta = json.load(open(config_json_file, "r"))
    current_index = meta["current-index"]
    templ_list = meta["list-templ"]
    if len(templ_list) == 0:
        print(f"list templ is empty")
        return 1

    if args.index in ["next", "prev"]:
        if args.index == "next":
            current_index = max(0, current_index)
            current_index = (current_index + 1) % len(templ_list)
        elif args.index == "prev":
            current_index = max(0, current_index)
            current_index = (current_index - 1 + len(templ_list)) % len(templ_list)
        
        meta["current-index"] = current_index
        return extract_series_templ(meta, current_dir, args.raw, args.download)

    index_names_map = []
    for index, (templ_name, templ_descript) in enumerate(templ_list):
        p = templ_name.find("-")
        if p != -1:
            names = [templ_name[:p], templ_name[p+1:]]
        else:
            names = [templ_name]    
        
        names = [name for name in names if name.strip() != ""]
        index_names_map.append([index, names, templ_descript])

    if args.index != "":
        for index, names, templ_descript in index_names_map:
            if args.index in names:
                meta["current-index"] = index
                return extract_series_templ(meta, current_dir, args.raw, args.download, args.cuda, args.trt)
    
    print(f"List templ: ")
    for index, names, templ_descript in index_names_map:
        if len(names) > 0:
            if len(names) == 1:
                print(names[0])
            else:
                chapter = names[0]
                caption = names[1]
                print(f"chapter: {chapter}, caption: {caption}, description: {templ_descript}")
        
    if args.index != "":
        print(f"Unknow index [{args.index}]")
    return 1


def do_templ_list(args):

    url = f"{trtpy.pypi_base_url}/code_template/list.txt"
    resp = requests.get(url)
    if resp.status_code != 200:
        print("Can not fetch template list")
        return 1

    list_info = resp.content.decode("utf-8").split("\n")
    list_info = [item.strip().split(";") for item in list_info if item.strip() != ""]

    print(f"Found {len(list_info)} items:")
    for i, line in enumerate(list_info):
        name = line[0] if len(line) > 0 else ""
        language = line[1] if len(line) > 1 else ""
        descript = line[2] if len(line) > 2 else ""
        print(f"-{i+1}. {name} [{language}] : {descript}")
    return 0


def do_templ_search(args):
    url = f"{trtpy.pypi_base_url}/code_template/list.txt"
    resp = requests.get(url)
    if resp.status_code != 200:
        print("Can not fetch template list")
        return 1

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
        return 1

    print(f"Found {len(list_info)} items for '{pattern}':")
    for i, line in enumerate(list_info):
        name = line[0] if len(line) > 0 else ""
        language = line[1] if len(line) > 1 else ""
        descript = line[2] if len(line) > 2 else ""
        print(f"-{i+1}. {name} [{language}] : {descript}")
    return 0

def do_series_list(args):

    url = f"{trtpy.pypi_base_url}/code_template/list.series.txt"
    resp = requests.get(url)
    if resp.status_code != 200:
        print("Can not fetch series list")
        return 1

    list_info = resp.content.decode("utf-8").split("\n")
    list_info = [item.strip().split(";") for item in list_info if item.strip() != ""]

    print(f"Found {len(list_info)} items:")
    for i, line in enumerate(list_info):
        name = line[0] if len(line) > 0 else ""
        language = line[1] if len(line) > 1 else ""
        descript = line[2] if len(line) > 2 else ""
        print(f"-{i+1}. {name} [{language}] : {descript}")
    return 0


def do_series_search(args):
    url = f"{trtpy.pypi_base_url}/code_template/list.series.txt"
    resp = requests.get(url)
    if resp.status_code != 200:
        print("Can not fetch series list")
        return 1

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
        return 1

    print(f"Found {len(list_info)} items for '{pattern}':")
    for i, line in enumerate(list_info):
        name = line[0] if len(line) > 0 else ""
        language = line[1] if len(line) > 1 else ""
        descript = line[2] if len(line) > 2 else ""
        print(f"-{i+1}. {name} [{language}] : {descript}")
    return 0

def do_mnist_test(args):
    trtpy.init(args.cuda, args.trt)
    trtpy.compile_onnx_to_file(1, trtpy.onnx_hub("mnist"), "mnist.trtmodel")
    os.remove("mnist.trtmodel")
    print("Done.")
    return 0

def do_prep_vars(args):
    trtpy.init(args.cuda, args.trt)
    file_or_directory = args.file_or_directory
    if not os.path.exists(file_or_directory):
        print(f"No such file or directory, {file_or_directory}")
        return 1

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
    return 0

def do_compile(args):
    trtpy.init(args.cuda, args.trt)

    onnx = args.onnx
    if args.onnx_from_hub:
        onnx = trtpy.onnx_hub(onnx)
        if onnx is None:
            return 1

    if not os.path.exists(onnx):
        print(f"No such file {onnx}")
        return 1

    out = args.out
    if os.path.isdir(out):
        out = os.path.join(out, os.path.splitext(os.path.basename(onnx))[0] + ".trtmodel")

    mode = trtpy.Mode.FP32
    if args.fp16:
        mode = trtpy.Mode.FP16

    success = trtpy.compile_onnx_to_file(
        max_batch_size = args.max_batch_size, 
        file      = onnx, 
        saveto    = out, 
        mode      = mode, 
        device_id = args.device,
        max_workspace_size=args.max_workspace_size
    )

    if not success:
        print("Compile failed")
        return 1

    print(f"Compile successfully, save to {out}")
    return 0

def do_tryload(args):

    trtmodel = args.trtmodel
    if not os.path.exists(trtmodel):
        print(f"No such file {trtmodel}")
        return 1

    trtpy.init(args.cuda, args.trt)
    print(f"Load tensorRT engine {trtmodel} ...")
    trtpy.set_device(args.device)
    engine = trtpy.load_infer_file(trtmodel)
    if engine is None:
        print(f"Engine load failed {trtmodel}")
        return 1

    engine.print()
    print("Done!")
    return 0

def do_env_source(args):
    trtpy.init(args.cuda, args.trt)
    save = args.save
    template_file = os.path.join(trtpy.trtpy_root, "environment-template.sh")
    template_data = open(template_file, "r").read()
    variable_template = get_variable_template()
    template_data, _ = process_code_template.filter_content(template_data, variable_template)
    
    envbase_file = os.path.join(trtpy.nv_root, "env.sh")
    open(envbase_file, "w").write(template_data)

    if args.print:
        print(envbase_file, end="")
    else:
        open(save, "w").write(template_data)
        print(f"Save to {save}")

def do_invert_variable(args):

    trtpy.init(args.cuda, args.trt)
    file_or_directory = args.file_or_directory
    if not os.path.exists(file_or_directory):
        print(f"No such file or directory, {file_or_directory}")
        return 1

    files = []
    if os.path.isdir(file_or_directory):
        for d, ds, fs in os.walk(file_or_directory):
            files.extend([os.path.join(d, f) for f in fs])
    else:
        files.append(file_or_directory)

    print("Replace project value to variable")
    variable_template = get_inv_variable_template()
    process_code_template.process_code_template(None, files, variable_template, process_code_template.inv_filter_content)
    print("Done!")
    return 0

if __name__ == "__main__":
    do_if_exec()

    def new_parser_with_version(name, help):
        global subp
        p = subp.add_parser(name, help=help)
        p.add_argument("--cuda", type=str, help="cuda version, 10.2, 11.2, 10, 11 etc.", default=None)
        p.add_argument("--trt", type=str, help="trt version, 8.0, 8 etc.", default=None)
        return p

    parser = argparse.ArgumentParser()
    subp = parser.add_subparsers(dest="cmd")
    new_parser_with_version("get-env", help="download environment")
    p = new_parser_with_version("info", help="display support list")
    p.add_argument("--init", action="store_true", help="init after display")
    p.add_argument("--tryload", action="store_true", help="try to load dynamic library")
    new_parser_with_version("mnist-test", help="test tensorrt with mnist")
    
    p = new_parser_with_version("exec", help="same to ./trtexec")
    p.add_argument("args", type=str, help="./trtexec args", default=None)

    subp.add_parser("list-templ", help="display all code template")
    p = subp.add_parser("search-templ", help="search all code template")
    p.add_argument("pattern", type=str, help="search name, yolo* etc.")

    p = new_parser_with_version("get-templ", help="fetch code template")
    p.add_argument("template", type=str, help="template name: tensorrt-mnist cuda-sample")
    p.add_argument("saveto", type=str, help="save to directory, default[template name]", nargs="?")
    p.add_argument("--raw", action="store_true", help="do not replace variables")
    p.add_argument("--download", action="store_true", help="ignore cache and download template")

    subp.add_parser("list-series", help="display all series template")
    p = subp.add_parser("search-series", help="search all series template")
    p.add_argument("pattern", type=str, help="search name, yolo* etc.")

    p = new_parser_with_version("get-series", help="fetch series template")
    p.add_argument("name", type=str, help="series name")
    p.add_argument("saveto", type=str, help="save to directory, default[template name]", nargs="?")
    p.add_argument("--raw", action="store_true", help="do not replace variables")
    p.add_argument("--download", action="store_true", help="ignore cache and download template")

    p = new_parser_with_version("change-proj", help="change series proj")
    p.add_argument("index", type=str, default="", help="series proj index, 1.1/cuinit", nargs="?")
    p.add_argument("--raw", action="store_true", help="do not replace variables")
    p.add_argument("--download", action="store_true", help="ignore cache and download template")

    p = new_parser_with_version("prep-vars", help="replace local file variables")
    p.add_argument("file_or_directory", type=str, help=f"Project directory or file, file filter = {process_code_template.include_list}")

    p = new_parser_with_version("inv-vars", help="replace local file value invert to variables")
    p.add_argument("file_or_directory", type=str, help=f"Project directory or file, file filter = {process_code_template.include_list}")

    p = new_parser_with_version("compile", help="compile use trtpro")
    p.add_argument("onnx", type=str, help="onnx file")
    p.add_argument("--out", type=str, default=".", help="output file or directory")
    p.add_argument("--fp16", action="store_true", help="use fp16")
    p.add_argument("--device", type=str, default=0, help="device id")
    p.add_argument("--onnx-from-hub", action="store_true", default=0, help="use onnx hub file")
    p.add_argument("--max-batch-size", type=int, default=1, help="max batch size")
    p.add_argument("--max-workspace-size", type=int, default=1<<30, help="max workspace size")

    p = new_parser_with_version("tryload", help="try to load trtmodel file")
    p.add_argument("trtmodel", type=str, help="tensorRT engine file")
    p.add_argument("--device", type=int, default=0, help="device id")

    p = new_parser_with_version("env-source", help="get trtpy environment")
    p.add_argument("--save", type=str, default="trtpy-environment.sh", help="save to file")
    p.add_argument("--print", action="store_true", help="print env path")

    subp.add_parser("local-cpp-pkg", help="display all installed local cpp package")
    p = subp.add_parser("get-cpp-pkg", help="download cpp package")
    p.add_argument("name", type=str, help="package name")
    args = parser.parse_args()

    cmd_funcs = {
        "get-env":       do_get_env,
        "info":          do_info,
        "get-templ":     do_get_templ,
        "list-templ":    do_templ_list,
        "search-templ":  do_templ_search,
        "get-cpp-pkg":   do_get_cpp_pkg,
        "local-cpp-pkg": do_local_cpp_pkg,
        "mnist-test":    do_mnist_test,
        "prep-vars":     do_prep_vars,
        "compile":       do_compile,
        "tryload":       do_tryload,
        "env-source":    do_env_source,
        "inv-vars":      do_invert_variable,
        "get-series":    do_get_series,
        "list-series":   do_series_list,
        "search-series": do_series_search,
        "change-proj":   do_change_proj
    }

    if args.cmd in cmd_funcs:
        sys.exit(cmd_funcs[args.cmd](args))

    parser.print_help()