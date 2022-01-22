

def elim_apostrophes(args):
    """ strip apostrphes form items in args, allows for user to enslose characters and phrases that cannot naturally
    be parsed, such as spaces, or items beginning in a hyphen like negative numbers"""
    for key in args.keys():
        if isinstance(args[key], list):
            for i in range(0, len(args[key])):
                args[key][i] = args[key][i].replace("'", '')
        elif isinstance(args[key], str):
            args[key] = args[key].replace("'", '')


def process_clause(args):
    w_params = []
    for cond in args['<w_conds>']:
        if cond.casefold() == 'eq'.casefold():
            w_params.append('=')
        if cond.casefold() == 'gt'.casefold():
            w_params.append('>=')
        if cond.casefold() == 'lt'.casefold():
            w_params.append('<=')
        if cond.casefold() == 'like'.casefold():
            w_params.append('LIKE')

    return w_params


def o_cond(args):
    o_cond = ""
    if args['--asc']:
        o_cond = 'ASC'
    elif args['--desc']:
        o_cond = 'DESC'

    return o_cond