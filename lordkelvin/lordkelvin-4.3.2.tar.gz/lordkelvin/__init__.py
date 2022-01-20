#!/usr/bin/env python3
'''
High level python EVM interface

Usage:
  lk ( b | balance ) <address>
  lk ( s | save    ) <contract>           [--as <name>] <address>
  lk ( d | deploy  ) <contract> [options] [--as <name>] [--] [<args>...]
  lk ( x | execute ) <contract> [options] ( <function>  [--] [<args>...] | -a | -b )
  lk -h | --help
  lk --version
  lk --path

Options:
  -q                 quiet mode
  -v                 verbose mode
  --J                JSON pretty-print mode on
  -J                 JSON mode on
  -j                 JSON mode off
  -a                 get address
  -b                 get balance
  <contract>         name of the contract
  <function>         name of the function
  -A --as <name>     name to save contract under
  -s --send <value>  value to send
  -S --salt <salt>   salt, for create2
  -P --profile       profile call
  -h --help          show this screen.
  --version          show version.
'''
import os, sys, json, time, functools as F
w3, __version__ = None, '4.3.2'
def get_balance(address=None):
    return w3.eth.get_balance(address or w3.eth.default_account)
def w3_connect(default_account, onion=None):
    global w3 ; from web3.auto import w3 as _w3 ; w3 = _w3
    if default_account is not None:
        w3.eth.default_account = w3.eth.accounts[int(default_account)]
        return w3
    from web3.middleware import construct_sign_and_send_raw_middleware
    from eth_account import Account
    w3.eth.default_account = os.getenv('PUBLIC')
    acct = Account.from_key( os.getenv('PRIVATE',''))
    #acct = Account.create('KEYSMASH FJAFJKLDSKF7JKFDJ 1530')
    w3.middleware_onion.add(construct_sign_and_send_raw_middleware(acct))
    return w3
def   load_abi(name):
    return json.load(open(f'out/{name}.abi'))
def   load_bytecode(name):
    return           open(f'out/{name}.bin').read()
def   load_address(name):
    return           open(f'out/{name}.cta').read()
def   save_address(name, address):
    if 1:            open(f'out/{name}.cta','w').write(address)
    return address
def        cta(name):
    return load_address(name)
def   save_cta(name, address):
    return save_address(name, address)
def __link_contract(old_name, new_name, ext, msg):
    ofn, nfn = f"./{old_name}.{ext}", f"out/{new_name}.{ext}"
    try:   os.unlink(nfn)
    except FileNotFoundError: pass
    return os.symlink(ofn, nfn)
def   link_contract(old_name, new_name):
    __link_contract(old_name, new_name, "abi", "ABI ERR")
    __link_contract(old_name, new_name, "bin", "BIN ERR")
    pass
def   load_contract(name, address=None):
    if address is None:
        address = load_address(name)
        pass
    return w3.eth.contract(abi=load_abi(name), address=address)
def     tx_wait(tx_hash):
    return w3.eth.wait_for_transaction_receipt(tx_hash)
def    new_contract(name):
    return w3.eth.contract(abi=load_abi(name),
                           bytecode=load_bytecode(name))
def   wrap_contract(*a, **kw):
    return WrapContract(load_contract(*a, **kw))
def   ctor_contract(name):
    return new_contract(name).constructor
def mk_exec_contract(name):
    with open(f'out/{name}', 'w') as f:
        print('cd `dirname $0`/..', file=f)
        print('exec lk x `basename $0` "$@"', file=f)
        pass
    assert(os.system(f'chmod +x out/{name}') == 0)
    return name
def deploy_contract(name, *args, **kw):
    tx_receipt = _wcall(ctor_contract(name), *args, **kw)
    mk_exec_contract(name)
    return save_address(name, tx_receipt.contractAddress)
def deploy_contract_verbose(name, *args, **kw):
    tx_receipt = _wcall(ctor_contract(name), *args, **kw)
    mk_exec_contract(name)
    save_address(name, tx_receipt.contractAddress)
    return tx_receipt
def _rcall(func, *args, **kw):
    return func(*args).call(kw)
class X(Exception): pass
def _wcall(func, *args, _from=None, tries=0, **kw):
    if _from: kw['from'] = _from
    if 'gasPrice' not in kw: kw['gasPrice'] = w3.eth.gas_price
    error = False
    ee = None
    while 1:
        try:
            return tx_wait(func(*args).transact(kw))
        except ValueError as e:
            if type(e.args[0])==str:
                error = True
                ee = e
                break
            tries -= 1
            if not tries or e.args[0]['code'] != -32010:
                raise
            print("SOME ERROR2", e)
            print(e.args[0]['message'])
            if    e.args[0]['message'].startswith('Insufficient funds. '):
                break
                raise exit(3)
            print("retry...")
            time.sleep(0.1)
            pass
        pass
    import web3
    raise web3.exceptions.ContractLogicError(*ee.args)
class WrapMixin:
    def get_balance(_, address=None):
        return get_balance(address or _.address)
    pass 
class WrapContract(WrapMixin):
    @property
    def address(_): return _.contract.address
    @property
    def  events(_): return _.contract.events
    def __init__(_, contract):
        _.ras, _.was, _.contract = [], [], contract
        for f in contract.functions._functions:
            b = f['stateMutability'] in ['view','pure']
            if b: _.ras.append(f['name'])
            else: _.was.append(f['name'])
            pass
        pass
    def __getattr__(_, key): return _.get2(key)[1]
    def __getitem__(_, key): return _.get2(key)[1]
    def        get (_, key): return _.get2(key)[1]
    def        get2(_, key):
        func = _.contract.functions.__dict__[key]        
        if key in _.ras: return False, F.partial(_rcall, func)
        if key in _.was: return True,  F.partial(_wcall, func)
        raise KeyError(key)
    pass
class WrapAccount(WrapMixin):
    def transfer(_, **kw): # to, value
        try:
            _ = w3.eth.default_account
            w3.eth.default_account = _.address
            tx_hash = w3.eth.send_transaction(kw)
            return w3.eth.wait_for_transaction_receipt(tx_hash)
        finally:
            w3.eth.default_account = _
            pass
        pass
    def __init__(_, address):
        if type(address) == int:
            address = w3.eth.accounts[address]
            pass
        _.address = address
        pass
    def __repr__(_): return repr(_.address)
    def  __str__(_): return  str(_.address)
    pass
def _f(x):
    if x == '-':
        return _f(input())
    if x == 'true':
        return True
    if x == 'false':
        return False
    if x == 'null':
        return None
    if x.startswith('@@'):
        return _f(open(f'out/{x[2:]}.cta').read().strip())
    if x.startswith('@'):
        return _f(open(       x[1:]      ).read().strip())
    if x.startswith('~'):
        try:    return   -int(x[1:])
        except: pass
        try:    return -float(x[1:])
        except: pass
        pass
    try:    return   int(x)
    except: pass
    try:    return float(x)
    except: pass
    return x
def println(result, _json, quiet=False, profile=False):
    from web3.datastructures import AttributeDict
    if profile:
        if quiet:
            return print(result['gasUsed'])
        result = dict(gasUsed=result['gasUsed'])
        if _json:
            return print(json.dumps(result))
        return print(result)
    if quiet:
        return
    if not _json:
        return print(result)
    if type(result)==AttributeDict:
        result = dict(result)
    if type(result).__name__=="bytes":
        return print(result.hex())
    if type(result).__name__=="HexBytes":
        return print(result.hex())
    if type(result)==type("") and result.startswith("0x"):
        return print(result)
    if type(result)==type([]):
        result = [f"0x{x.hex()}" if type(x)==bytes else x for x in result]
        return print(json.dumps(result))
    if type(result)!=type({}):
        return print(json.dumps(result))
    d = dict(result)
    for k, v in d.items():
        if k == "logsBloom":
            d[k] = 'logsBloom'
        elif k == "logs":
            d[k] = 'logs'
        elif type(v).__name__=="HexBytes":
            d[k] = v.hex()
            pass
        pass
    if _json==2:
        return print(json.dumps(d, indent=1))
    return print(json.dumps(d))
def main():
    import docopt, re
    A = docopt.docopt(__doc__, version=__version__)
    v, q, j = A['-v'], A['-q'], A['-J']
    nname   = A['--as']
    name    = A['<contract>']
    func    = A['<function>']
    value   = A['--send'] or 0
    unit    = 'wei'
    if not A['-j'] and not A['-J']: j = True
    if A['--J']: j = 2
    if A['--path']:
        exit(print(os.path.split(__file__)[0]))
    if value and type(value)==type(""):
        m = re.match(r'([0-9]+)(.*)$', value)
        value = int(m.group(1))
        if m.group(2): unit = m.group(2)
        pass
    w3 = w3_connect(os.getenv('WALLET'))
    if not w3.isConnected():
        print('no connection')
        raise exit(1)
    if nname:
        link_contract(name, nname)
        name = nname
        pass
    def execf(f, j, q, p=None):
        return println(f(*[_f(x) for x in A['<args>']],
                         value = w3.toWei(value,unit)), j, q, p)
    profile = A['--profile']
    if   A['execute'] or A['x']:
        if A['-b']:
            return println(get_balance(cta(A['<contract>'])), j)
        if A['-a']:
            return println(cta(name), j, q)            
        writable, func = wrap_contract(name).get2(func)
        execf(func, j, not v if writable else q, profile)
    elif  A['deploy'] or A['d']:
        if v: execf(F.partial(deploy_contract_verbose, name), j, q)
        else: execf(F.partial(deploy_contract,         name), j, q)
    elif    A['save'] or A['s']:
        save_cta(mk_exec_contract(name), _f(A['<address>']))
    elif A['balance'] or A['b']:
        println(get_balance(_f(A['<address>'])), j)
    else:
        print('dunno what to do', A)
        raise exit(1)
    pass
def main2():
    sys.argv.insert(1, sys.argv[0].split('/')[-1])
    return main()
if __name__=='__main__': main()
