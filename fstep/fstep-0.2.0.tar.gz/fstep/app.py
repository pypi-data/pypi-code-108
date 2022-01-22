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
    with open(fn) as fo:
        l = fstep.Lexer(fo)
        print(f"(",end=' ')
        while True:
            token = l.NextToken()
            if token != fstep.Token.End:
                if token == fstep.Token.Id:
                    print(f"(Id {l.id_val_})",end=' ')
                elif token == fstep.Token.Integer:
                    print(f"(Integer {l.int_val_})",end=' ')
                elif token == fstep.Token.Keyword:
                    print(f"(Keyword {l.key_val_})",end=' ')
                elif token == fstep.Token.Operator:
                    print(f"(Operator {l.op_val_})",end=' ')
                elif token == fstep.Token.Other:
                    print(f"(Other {l.other_val_})",end=' ')
            else:
                break
        print(f")")

def parser(fn):
    with open(fn) as fo:
        lexer = fstep.Lexer(fo)
        parser = fstep.Parser(lexer)
        ast_list = []
        while True:
            ast = parser.ParseNext()
            if not ast:
                break
            ast_list.append(ast)

    for ast in ast_list:
        print(ast)

def assembler(fn, out_fn=None):
    with open(fn) as fo:
        lexer = fstep.Lexer(fo)
        parser = fstep.Parser(lexer)
        gen = fstep.IRGenerator()

        while True:
            ast = parser.ParseNext()
            if not ast:
                break
            ast.GenerateIR(gen)

        if out_fn != None:
            with open(out_fn, 'w') as out_fo:
                gen.Dump(out_fo)

def main():
    usage = '''
    Usage: fstep -s [file] [options]
    Options:
        -h, --h         show help
        -s file         source file
        -l              lexer
        -p              parser
        -i              interpreter
        -a file         risc-v assembler
    Examples:
        fstep -h
        fstep -s source.fstep -i
    '''
    try:
        opts, argvs = getopt.getopt(sys.argv[1:], 's:lpa:hi', ['help'])
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
            out_fn = argv
            return assembler(fn, out_fn)
        elif opt == '-i':
            return interpreter(fn)

    print(usage)

if __name__ == '__main__':
    main()
