

def parse_args(args, flag_start='-'):
    ret = {}
    cur_flag = 'positional'
    for i in args:
        if(i.startswith(flag_start)):
            cur_flag = i[len(flag_start):]
            ret[cur_flag] = True
        else:
            if((cur_flag in ret) and (ret[cur_flag] is True)):
                ret[cur_flag] = [i]
            elif(cur_flag in ret):
                ret[cur_flag].append(i)
            else:
                ret[cur_flag]=[i]
    return ret


if(__name__ == '__main__'):   # for test only
    print(parse_args(["foo","-b","bar","--meow","oof"]))
    import sys
    print(parse_args(sys.argv))