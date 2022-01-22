import sys
import getopt
import fstep

def interpreter(fn):
    with open(fn) as fo:
        lexer = fstep.Lexer(fo)
        parser = fstep.Parser(lexer)
        intp = fstep.Interpreter()

        while True:
            ast = parser.ParseNext()
            if not ast:
                break
            intp.AddFunctionDef(ast)

        ret = intp.Eval()
        if ret != None:
            print(ret)
        exit(ret)

def lexer(fn):
    print('todo')

def parser(fn):
    print('todo')

def assembler(fn):
    print('todo')

def main():
    usage = '''
    Usage: fstep -s [file] [options]
    Options:
        -h, --h         show help
        -s file         import the source file, required!
        -l              lexer
        -p              parser
        -a              assembler, the assembler file is in the same path with compiler.py
        -i              interpreter
    Examples:
        fstep -h
        fstep -s source.fstep -i
    '''
    try:
        opts, argvs = getopt.getopt(sys.argv[1:], 's:lpahi', ['help'])
    except:
        print(usage)
        exit()

    if not opts or len(opts) == 0:
        print(usage)
        exit()

    for opt, argv in opts:
        if opt in ['-h', '--h', '--help']:
            print(usage)
            exit()
        elif opt == '-s':
            fn = argv
        elif opt == '-l':
            return lexer(fn)
        elif opt == '-p':
            return parser(fn)
        elif opt == '-a':
            return assembler(fn)
        elif opt == '-i':
            return interpreter(fn)

    print(usage)

if __name__ == '__main__':
    main()
