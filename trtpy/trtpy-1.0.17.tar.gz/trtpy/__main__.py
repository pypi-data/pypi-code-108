
import sys
import argparse
import trtpy
import subprocess
import os

def download(args):
    trtpy.init(cuda_version=args.cuda, tensorrt_version=args.trt)
    print(f"Download info: ")
    trtpy.print_pyc(trtpy.current_pyc)
    print("Done, Useage: 'import trtpy.init_default as trtpy'")

def info(args):
    print(f"Current kernel module driver version: {trtpy.current_kernel_module_driver_version}")

    print(f"Support list: {len(trtpy.supported_pycs)} elements")
    for i, pyc in enumerate(trtpy.supported_pycs):
        trtpy.print_pyc(pyc, i)

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
        if argv.startswith("--cuda-version"):
            if argv.startswith("--cuda-version="):
                cuda_version = argv[argv.find("=")+1:]
            elif i + 1 < len(args) and not args[i+1].startswith("-"):
                cuda_version = argv[i + 1]
                i += 1
        elif argv.startswith("--trt-version"):
            if argv.startswith("--trt-version="):
                trt_version = argv[argv.find("=")+1:]
            elif i + 1 < len(args) and not args[i+1].startswith("-"):
                trt_version = argv[i + 1]
                i += 1
        else:
            trt_args.append(argv)
        i += 1

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


if __name__ == "__main__":

    do_if_exec()
    parser = argparse.ArgumentParser()
    subp = parser.add_subparsers(dest="cmd")
    downloadp = subp.add_parser("download", help="download environment")
    downloadp.add_argument("--cuda", type=str, help="cuda version, 10.2, 11.2, 10, 11 etc.", default=None)
    downloadp.add_argument("--trt", type=str, help="trt version, 8.0, 8 etc.", default=None)
    
    execp = subp.add_parser("exec", help="same to ./trtexec")
    execp.add_argument("--cuda-version", type=str, help="cuda version, 10.2, 11.2, 10, 11 etc.", default=None)
    execp.add_argument("--trt-version", type=str, help="trt version, 8.0, 8 etc.", default=None)
    execp.add_argument("args", type=str, help="./trtexec args", default=None)

    infop = subp.add_parser("info", help="display support list")
    args = parser.parse_args()

    if args.cmd == "download":
        download(args)
    elif args.cmd == "info":
        info(args)
    else:
        print(f"Unknow cmd cmd {args.cmd}")