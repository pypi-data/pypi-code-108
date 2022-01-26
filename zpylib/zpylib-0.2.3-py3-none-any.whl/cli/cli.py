# 使用方法: cli.py [-h] {run,build} ...

# 执行 Zpy 程序

# 可选项:
#   -h, --help   显示帮助信息

# Zpy:
#   {run,build}  Zpy 工具
#     run        运行 Zpy 程序
#     build      编译 Zpy 程序


import argparse
from zpylib import run, build

def main():
    parser = argparse.ArgumentParser(description='Execute Zpy program')
    subparser = parser.add_subparsers(title="Zpy", help="Zpy Toolkit")

    run_parser = subparser.add_parser('run', help='Build Zpy program')
    run_file = run_parser.add_argument('runFile', help='Taget file')

    build_parser = subparser.add_parser('build', help='Build Zpy program')
    build_file = build_parser.add_argument('buildFile', help='Taget file')
    to_py = build_parser.add_argument('-to', help='Build to Python file')
    
    args = parser.parse_args()

    try:
        args.runFile
    except Exception as e:
        file_exists = False
    else:
        file_exists = True

    try:
        args.buildFile
    except Exception as e:
        buildFile_exists = False
    else:
        buildFile_exists = True

    if buildFile_exists:
        build(args.buildFile, args.to)
    elif file_exists:
        run(args.runFile)
    else:
        print(args)
        raise Exception("Error: Could not execute or build")


if __name__ == "__main__":
    main()
