__all__ = ['encrypt']

# Don't look below, you will not understand this Python code :) I don't.

from js2py.pyjs import *
# setting scope
var = Scope( JS_BUILTINS )
set_global_object(var)

# Code follows:
var.registers(['encryptAES', '_gas', '_ep', '_chars_len', '_rds', 'CryptoJS', '$_chars'])
@Js
def PyJsHoisted__gas_(data, key0, iv0, this, arguments, var=var):
    var = Scope({'data':data, 'key0':key0, 'iv0':iv0, 'this':this, 'arguments':arguments}, var)
    var.registers(['iv0', 'key0', 'encrypted', 'data', 'key', 'iv'])
    var.put('key0', var.get('key0').callprop('replace', JsRegExp('/(^\\s+)|(\\s+$)/g'), Js('')))
    var.put('key', var.get('CryptoJS').get('enc').get('Utf8').callprop('parse', var.get('key0')))
    var.put('iv', var.get('CryptoJS').get('enc').get('Utf8').callprop('parse', var.get('iv0')))
    var.put('encrypted', var.get('CryptoJS').get('AES').callprop('encrypt', var.get('data'), var.get('key'), Js({'iv':var.get('iv'),'mode':var.get('CryptoJS').get('mode').get('CBC'),'padding':var.get('CryptoJS').get('pad').get('Pkcs7')})))
    return var.get('encrypted').callprop('toString')
PyJsHoisted__gas_.func_name = '_gas'
var.put('_gas', PyJsHoisted__gas_)
@Js
def PyJsHoisted_encryptAES_(data, _p1, this, arguments, var=var):
    var = Scope({'data':data, '_p1':_p1, 'this':this, 'arguments':arguments}, var)
    var.registers(['encrypted', 'data', '_p1'])
    if var.get('_p1').neg():
        return var.get('data')
    var.put('encrypted', var.get('_gas')((var.get('_rds')(Js(64.0))+var.get('data')), var.get('_p1'), var.get('_rds')(Js(16.0))))
    return var.get('encrypted')
PyJsHoisted_encryptAES_.func_name = 'encryptAES'
var.put('encryptAES', PyJsHoisted_encryptAES_)
@Js
def PyJsHoisted__ep_(p0, p1, this, arguments, var=var):
    var = Scope({'p0':p0, 'p1':p1, 'this':this, 'arguments':arguments}, var)
    var.registers(['p0', 'p1'])
    try:
        return var.get('encryptAES')(var.get('p0'), var.get('p1'))
    except PyJsException as PyJsTempException:
        PyJsHolder_65_96638274 = var.own.get('e')
        var.force_own_put('e', PyExceptionToJs(PyJsTempException))
        try:
            pass
        finally:
            if PyJsHolder_65_96638274 is not None:
                var.own['e'] = PyJsHolder_65_96638274
            else:
                del var.own['e']
            del PyJsHolder_65_96638274
    return var.get('p0')
PyJsHoisted__ep_.func_name = '_ep'
var.put('_ep', PyJsHoisted__ep_)
@Js
def PyJsHoisted__rds_(len, this, arguments, var=var):
    var = Scope({'len':len, 'this':this, 'arguments':arguments}, var)
    var.registers(['len', 'retStr'])
    var.put('retStr', Js(''))
    #for JS loop
    var.put('i', Js(0.0))
    while (var.get('i')<var.get('len')):
        try:
            var.put('retStr', var.get('$_chars').callprop('charAt', var.get('Math').callprop('floor', (var.get('Math').callprop('random')*var.get('_chars_len')))), '+')
        finally:
                (var.put('i',Js(var.get('i').to_number())+Js(1))-Js(1))
    return var.get('retStr')
PyJsHoisted__rds_.func_name = '_rds'
var.put('_rds', PyJsHoisted__rds_)
@Js
def PyJs_anonymous_0_(u, p, this, arguments, var=var):
    var = Scope({'u':u, 'p':p, 'this':this, 'arguments':arguments}, var)
    var.registers(['w', 'd', 'b', 'x', 'p', 's', 'v', 'r', 't', 'u', 'q', 'l', 'n'])
    var.put('d', Js({}))
    var.put('l', var.get('d').put('lib', Js({})))
    @Js
    def PyJs_anonymous_1_(this, arguments, var=var):
        var = Scope({'this':this, 'arguments':arguments}, var)
        var.registers([])
        pass
    PyJs_anonymous_1_._set_name('anonymous')
    var.put('s', PyJs_anonymous_1_)
    @Js
    def PyJs_anonymous_2_(a, this, arguments, var=var):
        var = Scope({'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['c', 'a'])
        var.get('s').put('prototype', var.get(u"this"))
        var.put('c', var.get('s').create())
        (var.get('a') and var.get('c').callprop('mixIn', var.get('a')))
        @Js
        def PyJs_anonymous_3_(this, arguments, var=var):
            var = Scope({'this':this, 'arguments':arguments}, var)
            var.registers([])
            var.get('c').get('$super').get('init').callprop('apply', var.get(u"this"), var.get('arguments'))
        PyJs_anonymous_3_._set_name('anonymous')
        (var.get('c').callprop('hasOwnProperty', Js('init')) or var.get('c').put('init', PyJs_anonymous_3_))
        var.get('c').get('init').put('prototype', var.get('c'))
        var.get('c').put('$super', var.get(u"this"))
        return var.get('c')
    PyJs_anonymous_2_._set_name('anonymous')
    @Js
    def PyJs_anonymous_4_(this, arguments, var=var):
        var = Scope({'this':this, 'arguments':arguments}, var)
        var.registers(['a'])
        var.put('a', var.get(u"this").callprop('extend'))
        var.get('a').get('init').callprop('apply', var.get('a'), var.get('arguments'))
        return var.get('a')
    PyJs_anonymous_4_._set_name('anonymous')
    @Js
    def PyJs_anonymous_5_(this, arguments, var=var):
        var = Scope({'this':this, 'arguments':arguments}, var)
        var.registers([])
        pass
    PyJs_anonymous_5_._set_name('anonymous')
    @Js
    def PyJs_anonymous_6_(a, this, arguments, var=var):
        var = Scope({'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['c', 'a'])
        for PyJsTemp in var.get('a'):
            var.put('c', PyJsTemp)
            (var.get('a').callprop('hasOwnProperty', var.get('c')) and var.get(u"this").put(var.get('c'), var.get('a').get(var.get('c'))))
        (var.get('a').callprop('hasOwnProperty', Js('toString')) and var.get(u"this").put('toString', var.get('a').get('toString')))
    PyJs_anonymous_6_._set_name('anonymous')
    @Js
    def PyJs_anonymous_7_(this, arguments, var=var):
        var = Scope({'this':this, 'arguments':arguments}, var)
        var.registers([])
        return var.get(u"this").get('init').get('prototype').callprop('extend', var.get(u"this"))
    PyJs_anonymous_7_._set_name('anonymous')
    var.put('t', var.get('l').put('Base', Js({'extend':PyJs_anonymous_2_,'create':PyJs_anonymous_4_,'init':PyJs_anonymous_5_,'mixIn':PyJs_anonymous_6_,'clone':PyJs_anonymous_7_})))
    @Js
    def PyJs_anonymous_8_(a, c, this, arguments, var=var):
        var = Scope({'a':a, 'c':c, 'this':this, 'arguments':arguments}, var)
        var.registers(['c', 'a'])
        var.put('a', var.get(u"this").put('words', (var.get('a') or Js([]))))
        var.get(u"this").put('sigBytes', (var.get('c') if (var.get('c')!=var.get('p')) else (Js(4.0)*var.get('a').get('length'))))
    PyJs_anonymous_8_._set_name('anonymous')
    @Js
    def PyJs_anonymous_9_(a, this, arguments, var=var):
        var = Scope({'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['a'])
        return (var.get('a') or var.get('v')).callprop('stringify', var.get(u"this"))
    PyJs_anonymous_9_._set_name('anonymous')
    @Js
    def PyJs_anonymous_10_(a, this, arguments, var=var):
        var = Scope({'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['a', 'k', 'e', 'j', 'c'])
        var.put('c', var.get(u"this").get('words'))
        var.put('e', var.get('a').get('words'))
        var.put('j', var.get(u"this").get('sigBytes'))
        var.put('a', var.get('a').get('sigBytes'))
        var.get(u"this").callprop('clamp')
        if (var.get('j')%Js(4.0)):
            #for JS loop
            var.put('k', Js(0.0))
            while (var.get('k')<var.get('a')):
                try:
                    var.get('c').put(PyJsBshift((var.get('j')+var.get('k')),Js(2.0)), ((PyJsBshift(var.get('e').get(PyJsBshift(var.get('k'),Js(2.0))),(Js(24.0)-(Js(8.0)*(var.get('k')%Js(4.0)))))&Js(255.0))<<(Js(24.0)-(Js(8.0)*((var.get('j')+var.get('k'))%Js(4.0))))), '|')
                finally:
                        (var.put('k',Js(var.get('k').to_number())+Js(1))-Js(1))
        else:
            if (Js(65535.0)<var.get('e').get('length')):
                #for JS loop
                var.put('k', Js(0.0))
                while (var.get('k')<var.get('a')):
                    try:
                        var.get('c').put(PyJsBshift((var.get('j')+var.get('k')),Js(2.0)), var.get('e').get(PyJsBshift(var.get('k'),Js(2.0))))
                    finally:
                            var.put('k', Js(4.0), '+')
            else:
                var.get('c').get('push').callprop('apply', var.get('c'), var.get('e'))
        var.get(u"this").put('sigBytes', var.get('a'), '+')
        return var.get(u"this")
    PyJs_anonymous_10_._set_name('anonymous')
    @Js
    def PyJs_anonymous_11_(this, arguments, var=var):
        var = Scope({'this':this, 'arguments':arguments}, var)
        var.registers(['c', 'a'])
        var.put('a', var.get(u"this").get('words'))
        var.put('c', var.get(u"this").get('sigBytes'))
        var.get('a').put(PyJsBshift(var.get('c'),Js(2.0)), (Js(4294967295.0)<<(Js(32.0)-(Js(8.0)*(var.get('c')%Js(4.0))))), '&')
        var.get('a').put('length', var.get('u').callprop('ceil', (var.get('c')/Js(4.0))))
    PyJs_anonymous_11_._set_name('anonymous')
    @Js
    def PyJs_anonymous_12_(this, arguments, var=var):
        var = Scope({'this':this, 'arguments':arguments}, var)
        var.registers(['a'])
        var.put('a', var.get('t').get('clone').callprop('call', var.get(u"this")))
        var.get('a').put('words', var.get(u"this").get('words').callprop('slice', Js(0.0)))
        return var.get('a')
    PyJs_anonymous_12_._set_name('anonymous')
    @Js
    def PyJs_anonymous_13_(a, this, arguments, var=var):
        var = Scope({'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['c', 'e', 'a'])
        #for JS loop
        var.put('c', Js([]))
        var.put('e', Js(0.0))
        while (var.get('e')<var.get('a')):
            try:
                var.get('c').callprop('push', ((Js(4294967296.0)*var.get('u').callprop('random'))|Js(0.0)))
            finally:
                    var.put('e', Js(4.0), '+')
        return var.get('r').get('init').create(var.get('c'), var.get('a'))
    PyJs_anonymous_13_._set_name('anonymous')
    var.put('r', var.get('l').put('WordArray', var.get('t').callprop('extend', Js({'init':PyJs_anonymous_8_,'toString':PyJs_anonymous_9_,'concat':PyJs_anonymous_10_,'clamp':PyJs_anonymous_11_,'clone':PyJs_anonymous_12_,'random':PyJs_anonymous_13_}))))
    var.put('w', var.get('d').put('enc', Js({})))
    @Js
    def PyJs_anonymous_14_(a, this, arguments, var=var):
        var = Scope({'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['a', 'k', 'e', 'j', 'c'])
        var.put('c', var.get('a').get('words'))
        var.put('a', var.get('a').get('sigBytes'))
        #for JS loop
        var.put('e', Js([]))
        var.put('j', Js(0.0))
        while (var.get('j')<var.get('a')):
            try:
                var.put('k', (PyJsBshift(var.get('c').get(PyJsBshift(var.get('j'),Js(2.0))),(Js(24.0)-(Js(8.0)*(var.get('j')%Js(4.0)))))&Js(255.0)))
                var.get('e').callprop('push', PyJsBshift(var.get('k'),Js(4.0)).callprop('toString', Js(16.0)))
                var.get('e').callprop('push', (var.get('k')&Js(15.0)).callprop('toString', Js(16.0)))
            finally:
                    (var.put('j',Js(var.get('j').to_number())+Js(1))-Js(1))
        return var.get('e').callprop('join', Js(''))
    PyJs_anonymous_14_._set_name('anonymous')
    @Js
    def PyJs_anonymous_15_(a, this, arguments, var=var):
        var = Scope({'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['c', 'e', 'j', 'a'])
        #for JS loop
        var.put('c', var.get('a').get('length'))
        var.put('e', Js([]))
        var.put('j', Js(0.0))
        while (var.get('j')<var.get('c')):
            try:
                var.get('e').put(PyJsBshift(var.get('j'),Js(3.0)), (var.get('parseInt')(var.get('a').callprop('substr', var.get('j'), Js(2.0)), Js(16.0))<<(Js(24.0)-(Js(4.0)*(var.get('j')%Js(8.0))))), '|')
            finally:
                    var.put('j', Js(2.0), '+')
        return var.get('r').get('init').create(var.get('e'), (var.get('c')/Js(2.0)))
    PyJs_anonymous_15_._set_name('anonymous')
    var.put('v', var.get('w').put('Hex', Js({'stringify':PyJs_anonymous_14_,'parse':PyJs_anonymous_15_})))
    @Js
    def PyJs_anonymous_16_(a, this, arguments, var=var):
        var = Scope({'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['c', 'e', 'j', 'a'])
        var.put('c', var.get('a').get('words'))
        var.put('a', var.get('a').get('sigBytes'))
        #for JS loop
        var.put('e', Js([]))
        var.put('j', Js(0.0))
        while (var.get('j')<var.get('a')):
            try:
                var.get('e').callprop('push', var.get('String').callprop('fromCharCode', (PyJsBshift(var.get('c').get(PyJsBshift(var.get('j'),Js(2.0))),(Js(24.0)-(Js(8.0)*(var.get('j')%Js(4.0)))))&Js(255.0))))
            finally:
                    (var.put('j',Js(var.get('j').to_number())+Js(1))-Js(1))
        return var.get('e').callprop('join', Js(''))
    PyJs_anonymous_16_._set_name('anonymous')
    @Js
    def PyJs_anonymous_17_(a, this, arguments, var=var):
        var = Scope({'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['c', 'e', 'j', 'a'])
        #for JS loop
        var.put('c', var.get('a').get('length'))
        var.put('e', Js([]))
        var.put('j', Js(0.0))
        while (var.get('j')<var.get('c')):
            try:
                var.get('e').put(PyJsBshift(var.get('j'),Js(2.0)), ((var.get('a').callprop('charCodeAt', var.get('j'))&Js(255.0))<<(Js(24.0)-(Js(8.0)*(var.get('j')%Js(4.0))))), '|')
            finally:
                    (var.put('j',Js(var.get('j').to_number())+Js(1))-Js(1))
        return var.get('r').get('init').create(var.get('e'), var.get('c'))
    PyJs_anonymous_17_._set_name('anonymous')
    var.put('b', var.get('w').put('Latin1', Js({'stringify':PyJs_anonymous_16_,'parse':PyJs_anonymous_17_})))
    @Js
    def PyJs_anonymous_18_(a, this, arguments, var=var):
        var = Scope({'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['a'])
        try:
            return var.get('decodeURIComponent')(var.get('escape')(var.get('b').callprop('stringify', var.get('a'))))
        except PyJsException as PyJsTempException:
            PyJsHolder_63_58589189 = var.own.get('c')
            var.force_own_put('c', PyExceptionToJs(PyJsTempException))
            try:
                PyJsTempException = JsToPyException(var.get('Error')(Js('Malformed UTF-8 data')))
                raise PyJsTempException
            finally:
                if PyJsHolder_63_58589189 is not None:
                    var.own['c'] = PyJsHolder_63_58589189
                else:
                    del var.own['c']
                del PyJsHolder_63_58589189
    PyJs_anonymous_18_._set_name('anonymous')
    @Js
    def PyJs_anonymous_19_(a, this, arguments, var=var):
        var = Scope({'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['a'])
        return var.get('b').callprop('parse', var.get('unescape')(var.get('encodeURIComponent')(var.get('a'))))
    PyJs_anonymous_19_._set_name('anonymous')
    var.put('x', var.get('w').put('Utf8', Js({'stringify':PyJs_anonymous_18_,'parse':PyJs_anonymous_19_})))
    @Js
    def PyJs_anonymous_20_(this, arguments, var=var):
        var = Scope({'this':this, 'arguments':arguments}, var)
        var.registers([])
        var.get(u"this").put('_data', var.get('r').get('init').create())
        var.get(u"this").put('_nDataBytes', Js(0.0))
    PyJs_anonymous_20_._set_name('anonymous')
    @Js
    def PyJs_anonymous_21_(a, this, arguments, var=var):
        var = Scope({'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['a'])
        ((Js('string')==var.get('a',throw=False).typeof()) and var.put('a', var.get('x').callprop('parse', var.get('a'))))
        var.get(u"this").get('_data').callprop('concat', var.get('a'))
        var.get(u"this").put('_nDataBytes', var.get('a').get('sigBytes'), '+')
    PyJs_anonymous_21_._set_name('anonymous')
    @Js
    def PyJs_anonymous_22_(a, this, arguments, var=var):
        var = Scope({'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['a', 'b', 'k', 'e', 'j', 'q', 'c'])
        var.put('c', var.get(u"this").get('_data'))
        var.put('e', var.get('c').get('words'))
        var.put('j', var.get('c').get('sigBytes'))
        var.put('k', var.get(u"this").get('blockSize'))
        var.put('b', (var.get('j')/(Js(4.0)*var.get('k'))))
        var.put('b', (var.get('u').callprop('ceil', var.get('b')) if var.get('a') else var.get('u').callprop('max', ((var.get('b')|Js(0.0))-var.get(u"this").get('_minBufferSize')), Js(0.0))))
        var.put('a', (var.get('b')*var.get('k')))
        var.put('j', var.get('u').callprop('min', (Js(4.0)*var.get('a')), var.get('j')))
        if var.get('a'):
            #for JS loop
            var.put('q', Js(0.0))
            while (var.get('q')<var.get('a')):
                try:
                    var.get(u"this").callprop('_doProcessBlock', var.get('e'), var.get('q'))
                finally:
                        var.put('q', var.get('k'), '+')
            var.put('q', var.get('e').callprop('splice', Js(0.0), var.get('a')))
            var.get('c').put('sigBytes', var.get('j'), '-')
        return var.get('r').get('init').create(var.get('q'), var.get('j'))
    PyJs_anonymous_22_._set_name('anonymous')
    @Js
    def PyJs_anonymous_23_(this, arguments, var=var):
        var = Scope({'this':this, 'arguments':arguments}, var)
        var.registers(['a'])
        var.put('a', var.get('t').get('clone').callprop('call', var.get(u"this")))
        var.get('a').put('_data', var.get(u"this").get('_data').callprop('clone'))
        return var.get('a')
    PyJs_anonymous_23_._set_name('anonymous')
    var.put('q', var.get('l').put('BufferedBlockAlgorithm', var.get('t').callprop('extend', Js({'reset':PyJs_anonymous_20_,'_append':PyJs_anonymous_21_,'_process':PyJs_anonymous_22_,'clone':PyJs_anonymous_23_,'_minBufferSize':Js(0.0)}))))
    @Js
    def PyJs_anonymous_24_(a, this, arguments, var=var):
        var = Scope({'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['a'])
        var.get(u"this").put('cfg', var.get(u"this").get('cfg').callprop('extend', var.get('a')))
        var.get(u"this").callprop('reset')
    PyJs_anonymous_24_._set_name('anonymous')
    @Js
    def PyJs_anonymous_25_(this, arguments, var=var):
        var = Scope({'this':this, 'arguments':arguments}, var)
        var.registers([])
        var.get('q').get('reset').callprop('call', var.get(u"this"))
        var.get(u"this").callprop('_doReset')
    PyJs_anonymous_25_._set_name('anonymous')
    @Js
    def PyJs_anonymous_26_(a, this, arguments, var=var):
        var = Scope({'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['a'])
        var.get(u"this").callprop('_append', var.get('a'))
        var.get(u"this").callprop('_process')
        return var.get(u"this")
    PyJs_anonymous_26_._set_name('anonymous')
    @Js
    def PyJs_anonymous_27_(a, this, arguments, var=var):
        var = Scope({'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['a'])
        (var.get('a') and var.get(u"this").callprop('_append', var.get('a')))
        return var.get(u"this").callprop('_doFinalize')
    PyJs_anonymous_27_._set_name('anonymous')
    @Js
    def PyJs_anonymous_28_(a, this, arguments, var=var):
        var = Scope({'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['a'])
        @Js
        def PyJs_anonymous_29_(b, e, this, arguments, var=var):
            var = Scope({'b':b, 'e':e, 'this':this, 'arguments':arguments}, var)
            var.registers(['b', 'e'])
            return var.get('a').get('init').create(var.get('e')).callprop('finalize', var.get('b'))
        PyJs_anonymous_29_._set_name('anonymous')
        return PyJs_anonymous_29_
    PyJs_anonymous_28_._set_name('anonymous')
    @Js
    def PyJs_anonymous_30_(a, this, arguments, var=var):
        var = Scope({'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['a'])
        @Js
        def PyJs_anonymous_31_(b, e, this, arguments, var=var):
            var = Scope({'b':b, 'e':e, 'this':this, 'arguments':arguments}, var)
            var.registers(['b', 'e'])
            return var.get('n').get('HMAC').get('init').create(var.get('a'), var.get('e')).callprop('finalize', var.get('b'))
        PyJs_anonymous_31_._set_name('anonymous')
        return PyJs_anonymous_31_
    PyJs_anonymous_30_._set_name('anonymous')
    var.get('l').put('Hasher', var.get('q').callprop('extend', Js({'cfg':var.get('t').callprop('extend'),'init':PyJs_anonymous_24_,'reset':PyJs_anonymous_25_,'update':PyJs_anonymous_26_,'finalize':PyJs_anonymous_27_,'blockSize':Js(16.0),'_createHelper':PyJs_anonymous_28_,'_createHmacHelper':PyJs_anonymous_30_})))
    var.put('n', var.get('d').put('algo', Js({})))
    return var.get('d')
PyJs_anonymous_0_._set_name('anonymous')
var.put('CryptoJS', (var.get('CryptoJS') or PyJs_anonymous_0_(var.get('Math'))))
@Js
def PyJs_anonymous_32_(this, arguments, var=var):
    var = Scope({'this':this, 'arguments':arguments}, var)
    var.registers(['p', 'u'])
    var.put('u', var.get('CryptoJS'))
    var.put('p', var.get('u').get('lib').get('WordArray'))
    @Js
    def PyJs_anonymous_33_(d, this, arguments, var=var):
        var = Scope({'d':d, 'this':this, 'arguments':arguments}, var)
        var.registers(['w', 'd', 'p', 'v', 'r', 't', 'l'])
        var.put('l', var.get('d').get('words'))
        var.put('p', var.get('d').get('sigBytes'))
        var.put('t', var.get(u"this").get('_map'))
        var.get('d').callprop('clamp')
        var.put('d', Js([]))
        #for JS loop
        var.put('r', Js(0.0))
        while (var.get('r')<var.get('p')):
            try:
                #for JS loop
                def PyJs_LONG_34_(var=var):
                    return ((((PyJsBshift(var.get('l').get(PyJsBshift(var.get('r'),Js(2.0))),(Js(24.0)-(Js(8.0)*(var.get('r')%Js(4.0)))))&Js(255.0))<<Js(16.0))|((PyJsBshift(var.get('l').get(PyJsBshift((var.get('r')+Js(1.0)),Js(2.0))),(Js(24.0)-(Js(8.0)*((var.get('r')+Js(1.0))%Js(4.0)))))&Js(255.0))<<Js(8.0)))|(PyJsBshift(var.get('l').get(PyJsBshift((var.get('r')+Js(2.0)),Js(2.0))),(Js(24.0)-(Js(8.0)*((var.get('r')+Js(2.0))%Js(4.0)))))&Js(255.0)))
                var.put('w', PyJs_LONG_34_())
                var.put('v', Js(0.0))
                while ((Js(4.0)>var.get('v')) and ((var.get('r')+(Js(0.75)*var.get('v')))<var.get('p'))):
                    try:
                        var.get('d').callprop('push', var.get('t').callprop('charAt', (PyJsBshift(var.get('w'),(Js(6.0)*(Js(3.0)-var.get('v'))))&Js(63.0))))
                    finally:
                            (var.put('v',Js(var.get('v').to_number())+Js(1))-Js(1))
            finally:
                    var.put('r', Js(3.0), '+')
        if var.put('l', var.get('t').callprop('charAt', Js(64.0))):
            #for JS loop
            
            while (var.get('d').get('length')%Js(4.0)):
                var.get('d').callprop('push', var.get('l'))
            
        return var.get('d').callprop('join', Js(''))
    PyJs_anonymous_33_._set_name('anonymous')
    @Js
    def PyJs_anonymous_35_(d, this, arguments, var=var):
        var = Scope({'d':d, 'this':this, 'arguments':arguments}, var)
        var.registers(['w', 'd', 'b', 's', 'v', 'r', 't', 'l'])
        var.put('l', var.get('d').get('length'))
        var.put('s', var.get(u"this").get('_map'))
        var.put('t', var.get('s').callprop('charAt', Js(64.0)))
        (var.get('t') and PyJsComma(var.put('t', var.get('d').callprop('indexOf', var.get('t'))),(((-Js(1.0))!=var.get('t')) and var.put('l', var.get('t')))))
        #for JS loop
        var.put('t', Js([]))
        var.put('r', Js(0.0))
        var.put('w', Js(0.0))
        while (var.get('w')<var.get('l')):
            try:
                if (var.get('w')%Js(4.0)):
                    var.put('v', (var.get('s').callprop('indexOf', var.get('d').callprop('charAt', (var.get('w')-Js(1.0))))<<(Js(2.0)*(var.get('w')%Js(4.0)))))
                    var.put('b', PyJsBshift(var.get('s').callprop('indexOf', var.get('d').callprop('charAt', var.get('w'))),(Js(6.0)-(Js(2.0)*(var.get('w')%Js(4.0))))))
                    var.get('t').put(PyJsBshift(var.get('r'),Js(2.0)), ((var.get('v')|var.get('b'))<<(Js(24.0)-(Js(8.0)*(var.get('r')%Js(4.0))))), '|')
                    (var.put('r',Js(var.get('r').to_number())+Js(1))-Js(1))
            finally:
                    (var.put('w',Js(var.get('w').to_number())+Js(1))-Js(1))
        return var.get('p').callprop('create', var.get('t'), var.get('r'))
    PyJs_anonymous_35_._set_name('anonymous')
    var.get('u').get('enc').put('Base64', Js({'stringify':PyJs_anonymous_33_,'parse':PyJs_anonymous_35_,'_map':Js('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')}))
PyJs_anonymous_32_._set_name('anonymous')
PyJs_anonymous_32_()
@Js
def PyJs_anonymous_36_(u, this, arguments, var=var):
    var = Scope({'u':u, 'this':this, 'arguments':arguments}, var)
    var.registers(['w', 'd', 'p', 'b', 'x', 's', 'v', 't', 'r', 'u', 'l'])
    @Js
    def PyJsHoisted_p_(b, n, a, c, e, j, k, this, arguments, var=var):
        var = Scope({'b':b, 'n':n, 'a':a, 'c':c, 'e':e, 'j':j, 'k':k, 'this':this, 'arguments':arguments}, var)
        var.registers(['a', 'b', 'k', 'e', 'j', 'c', 'n'])
        var.put('b', (((var.get('b')+((var.get('n')&var.get('a'))|((~var.get('n'))&var.get('c'))))+var.get('e'))+var.get('k')))
        return (((var.get('b')<<var.get('j'))|PyJsBshift(var.get('b'),(Js(32.0)-var.get('j'))))+var.get('n'))
    PyJsHoisted_p_.func_name = 'p'
    var.put('p', PyJsHoisted_p_)
    @Js
    def PyJsHoisted_d_(b, n, a, c, e, j, k, this, arguments, var=var):
        var = Scope({'b':b, 'n':n, 'a':a, 'c':c, 'e':e, 'j':j, 'k':k, 'this':this, 'arguments':arguments}, var)
        var.registers(['a', 'b', 'k', 'e', 'j', 'c', 'n'])
        var.put('b', (((var.get('b')+((var.get('n')&var.get('c'))|(var.get('a')&(~var.get('c')))))+var.get('e'))+var.get('k')))
        return (((var.get('b')<<var.get('j'))|PyJsBshift(var.get('b'),(Js(32.0)-var.get('j'))))+var.get('n'))
    PyJsHoisted_d_.func_name = 'd'
    var.put('d', PyJsHoisted_d_)
    @Js
    def PyJsHoisted_l_(b, n, a, c, e, j, k, this, arguments, var=var):
        var = Scope({'b':b, 'n':n, 'a':a, 'c':c, 'e':e, 'j':j, 'k':k, 'this':this, 'arguments':arguments}, var)
        var.registers(['a', 'b', 'k', 'e', 'j', 'c', 'n'])
        var.put('b', (((var.get('b')+((var.get('n')^var.get('a'))^var.get('c')))+var.get('e'))+var.get('k')))
        return (((var.get('b')<<var.get('j'))|PyJsBshift(var.get('b'),(Js(32.0)-var.get('j'))))+var.get('n'))
    PyJsHoisted_l_.func_name = 'l'
    var.put('l', PyJsHoisted_l_)
    @Js
    def PyJsHoisted_s_(b, n, a, c, e, j, k, this, arguments, var=var):
        var = Scope({'b':b, 'n':n, 'a':a, 'c':c, 'e':e, 'j':j, 'k':k, 'this':this, 'arguments':arguments}, var)
        var.registers(['a', 'b', 'k', 'e', 'j', 'c', 'n'])
        var.put('b', (((var.get('b')+(var.get('a')^(var.get('n')|(~var.get('c')))))+var.get('e'))+var.get('k')))
        return (((var.get('b')<<var.get('j'))|PyJsBshift(var.get('b'),(Js(32.0)-var.get('j'))))+var.get('n'))
    PyJsHoisted_s_.func_name = 's'
    var.put('s', PyJsHoisted_s_)
    pass
    pass
    pass
    pass
    #for JS loop
    var.put('t', var.get('CryptoJS'))
    var.put('r', var.get('t').get('lib'))
    var.put('w', var.get('r').get('WordArray'))
    var.put('v', var.get('r').get('Hasher'))
    var.put('r', var.get('t').get('algo'))
    var.put('b', Js([]))
    var.put('x', Js(0.0))
    while (Js(64.0)>var.get('x')):
        try:
            var.get('b').put(var.get('x'), ((Js(4294967296.0)*var.get('u').callprop('abs', var.get('u').callprop('sin', (var.get('x')+Js(1.0)))))|Js(0.0)))
        finally:
                (var.put('x',Js(var.get('x').to_number())+Js(1))-Js(1))
    @Js
    def PyJs_anonymous_37_(this, arguments, var=var):
        var = Scope({'this':this, 'arguments':arguments}, var)
        var.registers([])
        var.get(u"this").put('_hash', var.get('w').get('init').create(Js([Js(1732584193.0), Js(4023233417.0), Js(2562383102.0), Js(271733878.0)])))
    PyJs_anonymous_37_._set_name('anonymous')
    @Js
    def PyJs_anonymous_38_(q, n, this, arguments, var=var):
        var = Scope({'q':q, 'n':n, 'this':this, 'arguments':arguments}, var)
        var.registers(['a', 'c', 'n', 'f', 'e', 'u', 'D', 'g', 'm', 'x', 'k', 'h', 'B', 'r', 'q', 'w', 'C', 'v', 'j', 't', 'A', 'E', 'z'])
        #for JS loop
        var.put('a', Js(0.0))
        while (Js(16.0)>var.get('a')):
            try:
                var.put('c', (var.get('n')+var.get('a')))
                var.put('e', var.get('q').get(var.get('c')))
                var.get('q').put(var.get('c'), ((((var.get('e')<<Js(8.0))|PyJsBshift(var.get('e'),Js(24.0)))&Js(16711935.0))|(((var.get('e')<<Js(24.0))|PyJsBshift(var.get('e'),Js(8.0)))&Js(4278255360.0))))
            finally:
                    (var.put('a',Js(var.get('a').to_number())+Js(1))-Js(1))
        var.put('a', var.get(u"this").get('_hash').get('words'))
        var.put('c', var.get('q').get((var.get('n')+Js(0.0))))
        var.put('e', var.get('q').get((var.get('n')+Js(1.0))))
        var.put('j', var.get('q').get((var.get('n')+Js(2.0))))
        var.put('k', var.get('q').get((var.get('n')+Js(3.0))))
        var.put('z', var.get('q').get((var.get('n')+Js(4.0))))
        var.put('r', var.get('q').get((var.get('n')+Js(5.0))))
        var.put('t', var.get('q').get((var.get('n')+Js(6.0))))
        var.put('w', var.get('q').get((var.get('n')+Js(7.0))))
        var.put('v', var.get('q').get((var.get('n')+Js(8.0))))
        var.put('A', var.get('q').get((var.get('n')+Js(9.0))))
        var.put('B', var.get('q').get((var.get('n')+Js(10.0))))
        var.put('C', var.get('q').get((var.get('n')+Js(11.0))))
        var.put('u', var.get('q').get((var.get('n')+Js(12.0))))
        var.put('D', var.get('q').get((var.get('n')+Js(13.0))))
        var.put('E', var.get('q').get((var.get('n')+Js(14.0))))
        var.put('x', var.get('q').get((var.get('n')+Js(15.0))))
        var.put('f', var.get('a').get('0'))
        var.put('m', var.get('a').get('1'))
        var.put('g', var.get('a').get('2'))
        var.put('h', var.get('a').get('3'))
        var.put('f', var.get('p')(var.get('f'), var.get('m'), var.get('g'), var.get('h'), var.get('c'), Js(7.0), var.get('b').get('0')))
        var.put('h', var.get('p')(var.get('h'), var.get('f'), var.get('m'), var.get('g'), var.get('e'), Js(12.0), var.get('b').get('1')))
        var.put('g', var.get('p')(var.get('g'), var.get('h'), var.get('f'), var.get('m'), var.get('j'), Js(17.0), var.get('b').get('2')))
        var.put('m', var.get('p')(var.get('m'), var.get('g'), var.get('h'), var.get('f'), var.get('k'), Js(22.0), var.get('b').get('3')))
        var.put('f', var.get('p')(var.get('f'), var.get('m'), var.get('g'), var.get('h'), var.get('z'), Js(7.0), var.get('b').get('4')))
        var.put('h', var.get('p')(var.get('h'), var.get('f'), var.get('m'), var.get('g'), var.get('r'), Js(12.0), var.get('b').get('5')))
        var.put('g', var.get('p')(var.get('g'), var.get('h'), var.get('f'), var.get('m'), var.get('t'), Js(17.0), var.get('b').get('6')))
        var.put('m', var.get('p')(var.get('m'), var.get('g'), var.get('h'), var.get('f'), var.get('w'), Js(22.0), var.get('b').get('7')))
        var.put('f', var.get('p')(var.get('f'), var.get('m'), var.get('g'), var.get('h'), var.get('v'), Js(7.0), var.get('b').get('8')))
        var.put('h', var.get('p')(var.get('h'), var.get('f'), var.get('m'), var.get('g'), var.get('A'), Js(12.0), var.get('b').get('9')))
        var.put('g', var.get('p')(var.get('g'), var.get('h'), var.get('f'), var.get('m'), var.get('B'), Js(17.0), var.get('b').get('10')))
        var.put('m', var.get('p')(var.get('m'), var.get('g'), var.get('h'), var.get('f'), var.get('C'), Js(22.0), var.get('b').get('11')))
        var.put('f', var.get('p')(var.get('f'), var.get('m'), var.get('g'), var.get('h'), var.get('u'), Js(7.0), var.get('b').get('12')))
        var.put('h', var.get('p')(var.get('h'), var.get('f'), var.get('m'), var.get('g'), var.get('D'), Js(12.0), var.get('b').get('13')))
        var.put('g', var.get('p')(var.get('g'), var.get('h'), var.get('f'), var.get('m'), var.get('E'), Js(17.0), var.get('b').get('14')))
        var.put('m', var.get('p')(var.get('m'), var.get('g'), var.get('h'), var.get('f'), var.get('x'), Js(22.0), var.get('b').get('15')))
        var.put('f', var.get('d')(var.get('f'), var.get('m'), var.get('g'), var.get('h'), var.get('e'), Js(5.0), var.get('b').get('16')))
        var.put('h', var.get('d')(var.get('h'), var.get('f'), var.get('m'), var.get('g'), var.get('t'), Js(9.0), var.get('b').get('17')))
        var.put('g', var.get('d')(var.get('g'), var.get('h'), var.get('f'), var.get('m'), var.get('C'), Js(14.0), var.get('b').get('18')))
        var.put('m', var.get('d')(var.get('m'), var.get('g'), var.get('h'), var.get('f'), var.get('c'), Js(20.0), var.get('b').get('19')))
        var.put('f', var.get('d')(var.get('f'), var.get('m'), var.get('g'), var.get('h'), var.get('r'), Js(5.0), var.get('b').get('20')))
        var.put('h', var.get('d')(var.get('h'), var.get('f'), var.get('m'), var.get('g'), var.get('B'), Js(9.0), var.get('b').get('21')))
        var.put('g', var.get('d')(var.get('g'), var.get('h'), var.get('f'), var.get('m'), var.get('x'), Js(14.0), var.get('b').get('22')))
        var.put('m', var.get('d')(var.get('m'), var.get('g'), var.get('h'), var.get('f'), var.get('z'), Js(20.0), var.get('b').get('23')))
        var.put('f', var.get('d')(var.get('f'), var.get('m'), var.get('g'), var.get('h'), var.get('A'), Js(5.0), var.get('b').get('24')))
        var.put('h', var.get('d')(var.get('h'), var.get('f'), var.get('m'), var.get('g'), var.get('E'), Js(9.0), var.get('b').get('25')))
        var.put('g', var.get('d')(var.get('g'), var.get('h'), var.get('f'), var.get('m'), var.get('k'), Js(14.0), var.get('b').get('26')))
        var.put('m', var.get('d')(var.get('m'), var.get('g'), var.get('h'), var.get('f'), var.get('v'), Js(20.0), var.get('b').get('27')))
        var.put('f', var.get('d')(var.get('f'), var.get('m'), var.get('g'), var.get('h'), var.get('D'), Js(5.0), var.get('b').get('28')))
        var.put('h', var.get('d')(var.get('h'), var.get('f'), var.get('m'), var.get('g'), var.get('j'), Js(9.0), var.get('b').get('29')))
        var.put('g', var.get('d')(var.get('g'), var.get('h'), var.get('f'), var.get('m'), var.get('w'), Js(14.0), var.get('b').get('30')))
        var.put('m', var.get('d')(var.get('m'), var.get('g'), var.get('h'), var.get('f'), var.get('u'), Js(20.0), var.get('b').get('31')))
        var.put('f', var.get('l')(var.get('f'), var.get('m'), var.get('g'), var.get('h'), var.get('r'), Js(4.0), var.get('b').get('32')))
        var.put('h', var.get('l')(var.get('h'), var.get('f'), var.get('m'), var.get('g'), var.get('v'), Js(11.0), var.get('b').get('33')))
        var.put('g', var.get('l')(var.get('g'), var.get('h'), var.get('f'), var.get('m'), var.get('C'), Js(16.0), var.get('b').get('34')))
        var.put('m', var.get('l')(var.get('m'), var.get('g'), var.get('h'), var.get('f'), var.get('E'), Js(23.0), var.get('b').get('35')))
        var.put('f', var.get('l')(var.get('f'), var.get('m'), var.get('g'), var.get('h'), var.get('e'), Js(4.0), var.get('b').get('36')))
        var.put('h', var.get('l')(var.get('h'), var.get('f'), var.get('m'), var.get('g'), var.get('z'), Js(11.0), var.get('b').get('37')))
        var.put('g', var.get('l')(var.get('g'), var.get('h'), var.get('f'), var.get('m'), var.get('w'), Js(16.0), var.get('b').get('38')))
        var.put('m', var.get('l')(var.get('m'), var.get('g'), var.get('h'), var.get('f'), var.get('B'), Js(23.0), var.get('b').get('39')))
        var.put('f', var.get('l')(var.get('f'), var.get('m'), var.get('g'), var.get('h'), var.get('D'), Js(4.0), var.get('b').get('40')))
        var.put('h', var.get('l')(var.get('h'), var.get('f'), var.get('m'), var.get('g'), var.get('c'), Js(11.0), var.get('b').get('41')))
        var.put('g', var.get('l')(var.get('g'), var.get('h'), var.get('f'), var.get('m'), var.get('k'), Js(16.0), var.get('b').get('42')))
        var.put('m', var.get('l')(var.get('m'), var.get('g'), var.get('h'), var.get('f'), var.get('t'), Js(23.0), var.get('b').get('43')))
        var.put('f', var.get('l')(var.get('f'), var.get('m'), var.get('g'), var.get('h'), var.get('A'), Js(4.0), var.get('b').get('44')))
        var.put('h', var.get('l')(var.get('h'), var.get('f'), var.get('m'), var.get('g'), var.get('u'), Js(11.0), var.get('b').get('45')))
        var.put('g', var.get('l')(var.get('g'), var.get('h'), var.get('f'), var.get('m'), var.get('x'), Js(16.0), var.get('b').get('46')))
        var.put('m', var.get('l')(var.get('m'), var.get('g'), var.get('h'), var.get('f'), var.get('j'), Js(23.0), var.get('b').get('47')))
        var.put('f', var.get('s')(var.get('f'), var.get('m'), var.get('g'), var.get('h'), var.get('c'), Js(6.0), var.get('b').get('48')))
        var.put('h', var.get('s')(var.get('h'), var.get('f'), var.get('m'), var.get('g'), var.get('w'), Js(10.0), var.get('b').get('49')))
        var.put('g', var.get('s')(var.get('g'), var.get('h'), var.get('f'), var.get('m'), var.get('E'), Js(15.0), var.get('b').get('50')))
        var.put('m', var.get('s')(var.get('m'), var.get('g'), var.get('h'), var.get('f'), var.get('r'), Js(21.0), var.get('b').get('51')))
        var.put('f', var.get('s')(var.get('f'), var.get('m'), var.get('g'), var.get('h'), var.get('u'), Js(6.0), var.get('b').get('52')))
        var.put('h', var.get('s')(var.get('h'), var.get('f'), var.get('m'), var.get('g'), var.get('k'), Js(10.0), var.get('b').get('53')))
        var.put('g', var.get('s')(var.get('g'), var.get('h'), var.get('f'), var.get('m'), var.get('B'), Js(15.0), var.get('b').get('54')))
        var.put('m', var.get('s')(var.get('m'), var.get('g'), var.get('h'), var.get('f'), var.get('e'), Js(21.0), var.get('b').get('55')))
        var.put('f', var.get('s')(var.get('f'), var.get('m'), var.get('g'), var.get('h'), var.get('v'), Js(6.0), var.get('b').get('56')))
        var.put('h', var.get('s')(var.get('h'), var.get('f'), var.get('m'), var.get('g'), var.get('x'), Js(10.0), var.get('b').get('57')))
        var.put('g', var.get('s')(var.get('g'), var.get('h'), var.get('f'), var.get('m'), var.get('t'), Js(15.0), var.get('b').get('58')))
        var.put('m', var.get('s')(var.get('m'), var.get('g'), var.get('h'), var.get('f'), var.get('D'), Js(21.0), var.get('b').get('59')))
        var.put('f', var.get('s')(var.get('f'), var.get('m'), var.get('g'), var.get('h'), var.get('z'), Js(6.0), var.get('b').get('60')))
        var.put('h', var.get('s')(var.get('h'), var.get('f'), var.get('m'), var.get('g'), var.get('C'), Js(10.0), var.get('b').get('61')))
        var.put('g', var.get('s')(var.get('g'), var.get('h'), var.get('f'), var.get('m'), var.get('j'), Js(15.0), var.get('b').get('62')))
        var.put('m', var.get('s')(var.get('m'), var.get('g'), var.get('h'), var.get('f'), var.get('A'), Js(21.0), var.get('b').get('63')))
        var.get('a').put('0', ((var.get('a').get('0')+var.get('f'))|Js(0.0)))
        var.get('a').put('1', ((var.get('a').get('1')+var.get('m'))|Js(0.0)))
        var.get('a').put('2', ((var.get('a').get('2')+var.get('g'))|Js(0.0)))
        var.get('a').put('3', ((var.get('a').get('3')+var.get('h'))|Js(0.0)))
    PyJs_anonymous_38_._set_name('anonymous')
    @Js
    def PyJs_anonymous_39_(this, arguments, var=var):
        var = Scope({'this':this, 'arguments':arguments}, var)
        var.registers(['a', 'b', 'e', 'c', 'n'])
        var.put('b', var.get(u"this").get('_data'))
        var.put('n', var.get('b').get('words'))
        var.put('a', (Js(8.0)*var.get(u"this").get('_nDataBytes')))
        var.put('c', (Js(8.0)*var.get('b').get('sigBytes')))
        var.get('n').put(PyJsBshift(var.get('c'),Js(5.0)), (Js(128.0)<<(Js(24.0)-(var.get('c')%Js(32.0)))), '|')
        var.put('e', var.get('u').callprop('floor', (var.get('a')/Js(4294967296.0))))
        var.get('n').put(((PyJsBshift((var.get('c')+Js(64.0)),Js(9.0))<<Js(4.0))+Js(15.0)), ((((var.get('e')<<Js(8.0))|PyJsBshift(var.get('e'),Js(24.0)))&Js(16711935.0))|(((var.get('e')<<Js(24.0))|PyJsBshift(var.get('e'),Js(8.0)))&Js(4278255360.0))))
        var.get('n').put(((PyJsBshift((var.get('c')+Js(64.0)),Js(9.0))<<Js(4.0))+Js(14.0)), ((((var.get('a')<<Js(8.0))|PyJsBshift(var.get('a'),Js(24.0)))&Js(16711935.0))|(((var.get('a')<<Js(24.0))|PyJsBshift(var.get('a'),Js(8.0)))&Js(4278255360.0))))
        var.get('b').put('sigBytes', (Js(4.0)*(var.get('n').get('length')+Js(1.0))))
        var.get(u"this").callprop('_process')
        var.put('b', var.get(u"this").get('_hash'))
        var.put('n', var.get('b').get('words'))
        #for JS loop
        var.put('a', Js(0.0))
        while (Js(4.0)>var.get('a')):
            try:
                PyJsComma(var.put('c', var.get('n').get(var.get('a'))),var.get('n').put(var.get('a'), ((((var.get('c')<<Js(8.0))|PyJsBshift(var.get('c'),Js(24.0)))&Js(16711935.0))|(((var.get('c')<<Js(24.0))|PyJsBshift(var.get('c'),Js(8.0)))&Js(4278255360.0)))))
            finally:
                    (var.put('a',Js(var.get('a').to_number())+Js(1))-Js(1))
        return var.get('b')
    PyJs_anonymous_39_._set_name('anonymous')
    @Js
    def PyJs_anonymous_40_(this, arguments, var=var):
        var = Scope({'this':this, 'arguments':arguments}, var)
        var.registers(['b'])
        var.put('b', var.get('v').get('clone').callprop('call', var.get(u"this")))
        var.get('b').put('_hash', var.get(u"this").get('_hash').callprop('clone'))
        return var.get('b')
    PyJs_anonymous_40_._set_name('anonymous')
    var.put('r', var.get('r').put('MD5', var.get('v').callprop('extend', Js({'_doReset':PyJs_anonymous_37_,'_doProcessBlock':PyJs_anonymous_38_,'_doFinalize':PyJs_anonymous_39_,'clone':PyJs_anonymous_40_}))))
    var.get('t').put('MD5', var.get('v').callprop('_createHelper', var.get('r')))
    var.get('t').put('HmacMD5', var.get('v').callprop('_createHmacHelper', var.get('r')))
PyJs_anonymous_36_._set_name('anonymous')
PyJs_anonymous_36_(var.get('Math'))
@Js
def PyJs_anonymous_41_(this, arguments, var=var):
    var = Scope({'this':this, 'arguments':arguments}, var)
    var.registers(['d', 'p', 's', 'u', 'l'])
    var.put('u', var.get('CryptoJS'))
    var.put('p', var.get('u').get('lib'))
    var.put('d', var.get('p').get('Base'))
    var.put('l', var.get('p').get('WordArray'))
    var.put('p', var.get('u').get('algo'))
    @Js
    def PyJs_anonymous_42_(d, this, arguments, var=var):
        var = Scope({'d':d, 'this':this, 'arguments':arguments}, var)
        var.registers(['d'])
        var.get(u"this").put('cfg', var.get(u"this").get('cfg').callprop('extend', var.get('d')))
    PyJs_anonymous_42_._set_name('anonymous')
    @Js
    def PyJs_anonymous_43_(d, r, this, arguments, var=var):
        var = Scope({'d':d, 'r':r, 'this':this, 'arguments':arguments}, var)
        var.registers(['a', 'd', 'p', 'b', 's', 'r', 'u', 'q', 'n'])
        #for JS loop
        var.put('p', var.get(u"this").get('cfg'))
        var.put('s', var.get('p').get('hasher').callprop('create'))
        var.put('b', var.get('l').callprop('create'))
        var.put('u', var.get('b').get('words'))
        var.put('q', var.get('p').get('keySize'))
        var.put('p', var.get('p').get('iterations'))
        while (var.get('u').get('length')<var.get('q')):
            (var.get('n') and var.get('s').callprop('update', var.get('n')))
            var.put('n', var.get('s').callprop('update', var.get('d')).callprop('finalize', var.get('r')))
            var.get('s').callprop('reset')
            #for JS loop
            var.put('a', Js(1.0))
            while (var.get('a')<var.get('p')):
                try:
                    PyJsComma(var.put('n', var.get('s').callprop('finalize', var.get('n'))),var.get('s').callprop('reset'))
                finally:
                        (var.put('a',Js(var.get('a').to_number())+Js(1))-Js(1))
            var.get('b').callprop('concat', var.get('n'))
        
        var.get('b').put('sigBytes', (Js(4.0)*var.get('q')))
        return var.get('b')
    PyJs_anonymous_43_._set_name('anonymous')
    var.put('s', var.get('p').put('EvpKDF', var.get('d').callprop('extend', Js({'cfg':var.get('d').callprop('extend', Js({'keySize':Js(4.0),'hasher':var.get('p').get('MD5'),'iterations':Js(1.0)})),'init':PyJs_anonymous_42_,'compute':PyJs_anonymous_43_}))))
    @Js
    def PyJs_anonymous_44_(d, l, p, this, arguments, var=var):
        var = Scope({'d':d, 'l':l, 'p':p, 'this':this, 'arguments':arguments}, var)
        var.registers(['p', 'l', 'd'])
        return var.get('s').callprop('create', var.get('p')).callprop('compute', var.get('d'), var.get('l'))
    PyJs_anonymous_44_._set_name('anonymous')
    var.get('u').put('EvpKDF', PyJs_anonymous_44_)
PyJs_anonymous_41_._set_name('anonymous')
PyJs_anonymous_41_()
@Js
def PyJs_anonymous_45_(u, this, arguments, var=var):
    var = Scope({'u':u, 'this':this, 'arguments':arguments}, var)
    var.registers(['a', 'w', 'd', 'p', 'b', 'x', 's', 'v', 't', 'r', 'u', 'q', 'c', 'l', 'n'])
    var.put('p', var.get('CryptoJS'))
    var.put('d', var.get('p').get('lib'))
    var.put('l', var.get('d').get('Base'))
    var.put('s', var.get('d').get('WordArray'))
    var.put('t', var.get('d').get('BufferedBlockAlgorithm'))
    var.put('r', var.get('p').get('enc').get('Base64'))
    var.put('w', var.get('p').get('algo').get('EvpKDF'))
    def PyJs_LONG_55_(var=var):
        @Js
        def PyJs_anonymous_46_(e, a, this, arguments, var=var):
            var = Scope({'e':e, 'a':a, 'this':this, 'arguments':arguments}, var)
            var.registers(['e', 'a'])
            return var.get(u"this").callprop('create', var.get(u"this").get('_ENC_XFORM_MODE'), var.get('e'), var.get('a'))
        PyJs_anonymous_46_._set_name('anonymous')
        @Js
        def PyJs_anonymous_47_(e, a, this, arguments, var=var):
            var = Scope({'e':e, 'a':a, 'this':this, 'arguments':arguments}, var)
            var.registers(['e', 'a'])
            return var.get(u"this").callprop('create', var.get(u"this").get('_DEC_XFORM_MODE'), var.get('e'), var.get('a'))
        PyJs_anonymous_47_._set_name('anonymous')
        @Js
        def PyJs_anonymous_48_(e, a, b, this, arguments, var=var):
            var = Scope({'e':e, 'a':a, 'b':b, 'this':this, 'arguments':arguments}, var)
            var.registers(['b', 'e', 'a'])
            var.get(u"this").put('cfg', var.get(u"this").get('cfg').callprop('extend', var.get('b')))
            var.get(u"this").put('_xformMode', var.get('e'))
            var.get(u"this").put('_key', var.get('a'))
            var.get(u"this").callprop('reset')
        PyJs_anonymous_48_._set_name('anonymous')
        @Js
        def PyJs_anonymous_49_(this, arguments, var=var):
            var = Scope({'this':this, 'arguments':arguments}, var)
            var.registers([])
            var.get('t').get('reset').callprop('call', var.get(u"this"))
            var.get(u"this").callprop('_doReset')
        PyJs_anonymous_49_._set_name('anonymous')
        @Js
        def PyJs_anonymous_50_(e, this, arguments, var=var):
            var = Scope({'e':e, 'this':this, 'arguments':arguments}, var)
            var.registers(['e'])
            var.get(u"this").callprop('_append', var.get('e'))
            return var.get(u"this").callprop('_process')
        PyJs_anonymous_50_._set_name('anonymous')
        @Js
        def PyJs_anonymous_51_(e, this, arguments, var=var):
            var = Scope({'e':e, 'this':this, 'arguments':arguments}, var)
            var.registers(['e'])
            (var.get('e') and var.get(u"this").callprop('_append', var.get('e')))
            return var.get(u"this").callprop('_doFinalize')
        PyJs_anonymous_51_._set_name('anonymous')
        @Js
        def PyJs_anonymous_52_(e, this, arguments, var=var):
            var = Scope({'e':e, 'this':this, 'arguments':arguments}, var)
            var.registers(['e'])
            @Js
            def PyJs_anonymous_53_(b, k, d, this, arguments, var=var):
                var = Scope({'b':b, 'k':k, 'd':d, 'this':this, 'arguments':arguments}, var)
                var.registers(['b', 'k', 'd'])
                return (var.get('c') if (Js('string')==var.get('k',throw=False).typeof()) else var.get('a')).callprop('encrypt', var.get('e'), var.get('b'), var.get('k'), var.get('d'))
            PyJs_anonymous_53_._set_name('anonymous')
            @Js
            def PyJs_anonymous_54_(b, k, d, this, arguments, var=var):
                var = Scope({'b':b, 'k':k, 'd':d, 'this':this, 'arguments':arguments}, var)
                var.registers(['b', 'k', 'd'])
                return (var.get('c') if (Js('string')==var.get('k',throw=False).typeof()) else var.get('a')).callprop('decrypt', var.get('e'), var.get('b'), var.get('k'), var.get('d'))
            PyJs_anonymous_54_._set_name('anonymous')
            return Js({'encrypt':PyJs_anonymous_53_,'decrypt':PyJs_anonymous_54_})
        PyJs_anonymous_52_._set_name('anonymous')
        return var.get('d').put('Cipher', var.get('t').callprop('extend', Js({'cfg':var.get('l').callprop('extend'),'createEncryptor':PyJs_anonymous_46_,'createDecryptor':PyJs_anonymous_47_,'init':PyJs_anonymous_48_,'reset':PyJs_anonymous_49_,'process':PyJs_anonymous_50_,'finalize':PyJs_anonymous_51_,'keySize':Js(4.0),'ivSize':Js(4.0),'_ENC_XFORM_MODE':Js(1.0),'_DEC_XFORM_MODE':Js(2.0),'_createHelper':PyJs_anonymous_52_})))
    var.put('v', PyJs_LONG_55_())
    @Js
    def PyJs_anonymous_56_(this, arguments, var=var):
        var = Scope({'this':this, 'arguments':arguments}, var)
        var.registers([])
        return var.get(u"this").callprop('_process', Js(0.0).neg())
    PyJs_anonymous_56_._set_name('anonymous')
    var.get('d').put('StreamCipher', var.get('v').callprop('extend', Js({'_doFinalize':PyJs_anonymous_56_,'blockSize':Js(1.0)})))
    var.put('b', var.get('p').put('mode', Js({})))
    @Js
    def PyJs_anonymous_57_(e, a, b, this, arguments, var=var):
        var = Scope({'e':e, 'a':a, 'b':b, 'this':this, 'arguments':arguments}, var)
        var.registers(['a', 'd', 'b', 'e', 'c'])
        var.put('c', var.get(u"this").get('_iv'))
        (var.get(u"this").put('_iv', var.get('u')) if var.get('c') else var.put('c', var.get(u"this").get('_prevBlock')))
        #for JS loop
        var.put('d', Js(0.0))
        while (var.get('d')<var.get('b')):
            try:
                var.get('e').put((var.get('a')+var.get('d')), var.get('c').get(var.get('d')), '^')
            finally:
                    (var.put('d',Js(var.get('d').to_number())+Js(1))-Js(1))
    PyJs_anonymous_57_._set_name('anonymous')
    var.put('x', PyJs_anonymous_57_)
    @Js
    def PyJs_anonymous_58_(e, a, this, arguments, var=var):
        var = Scope({'e':e, 'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['e', 'a'])
        return var.get(u"this").get('Encryptor').callprop('create', var.get('e'), var.get('a'))
    PyJs_anonymous_58_._set_name('anonymous')
    @Js
    def PyJs_anonymous_59_(e, a, this, arguments, var=var):
        var = Scope({'e':e, 'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['e', 'a'])
        return var.get(u"this").get('Decryptor').callprop('create', var.get('e'), var.get('a'))
    PyJs_anonymous_59_._set_name('anonymous')
    @Js
    def PyJs_anonymous_60_(e, a, this, arguments, var=var):
        var = Scope({'e':e, 'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['e', 'a'])
        var.get(u"this").put('_cipher', var.get('e'))
        var.get(u"this").put('_iv', var.get('a'))
    PyJs_anonymous_60_._set_name('anonymous')
    var.put('q', var.get('d').put('BlockCipherMode', var.get('l').callprop('extend', Js({'createEncryptor':PyJs_anonymous_58_,'createDecryptor':PyJs_anonymous_59_,'init':PyJs_anonymous_60_}))).callprop('extend'))
    @Js
    def PyJs_anonymous_61_(e, a, this, arguments, var=var):
        var = Scope({'e':e, 'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['b', 'c', 'e', 'a'])
        var.put('b', var.get(u"this").get('_cipher'))
        var.put('c', var.get('b').get('blockSize'))
        var.get('x').callprop('call', var.get(u"this"), var.get('e'), var.get('a'), var.get('c'))
        var.get('b').callprop('encryptBlock', var.get('e'), var.get('a'))
        var.get(u"this").put('_prevBlock', var.get('e').callprop('slice', var.get('a'), (var.get('a')+var.get('c'))))
    PyJs_anonymous_61_._set_name('anonymous')
    var.get('q').put('Encryptor', var.get('q').callprop('extend', Js({'processBlock':PyJs_anonymous_61_})))
    @Js
    def PyJs_anonymous_62_(e, a, this, arguments, var=var):
        var = Scope({'e':e, 'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['a', 'd', 'b', 'e', 'c'])
        var.put('b', var.get(u"this").get('_cipher'))
        var.put('c', var.get('b').get('blockSize'))
        var.put('d', var.get('e').callprop('slice', var.get('a'), (var.get('a')+var.get('c'))))
        var.get('b').callprop('decryptBlock', var.get('e'), var.get('a'))
        var.get('x').callprop('call', var.get(u"this"), var.get('e'), var.get('a'), var.get('c'))
        var.get(u"this").put('_prevBlock', var.get('d'))
    PyJs_anonymous_62_._set_name('anonymous')
    var.get('q').put('Decryptor', var.get('q').callprop('extend', Js({'processBlock':PyJs_anonymous_62_})))
    var.put('b', var.get('b').put('CBC', var.get('q')))
    @Js
    def PyJs_anonymous_63_(a, b, this, arguments, var=var):
        var = Scope({'a':a, 'b':b, 'this':this, 'arguments':arguments}, var)
        var.registers(['a', 'd', 'b', 'c', 'l', 'n'])
        #for JS loop
        var.put('c', (Js(4.0)*var.get('b')))
        var.put('c', (var.get('c')-(var.get('a').get('sigBytes')%var.get('c'))))
        var.put('d', ((((var.get('c')<<Js(24.0))|(var.get('c')<<Js(16.0)))|(var.get('c')<<Js(8.0)))|var.get('c')))
        var.put('l', Js([]))
        var.put('n', Js(0.0))
        while (var.get('n')<var.get('c')):
            try:
                var.get('l').callprop('push', var.get('d'))
            finally:
                    var.put('n', Js(4.0), '+')
        var.put('c', var.get('s').callprop('create', var.get('l'), var.get('c')))
        var.get('a').callprop('concat', var.get('c'))
    PyJs_anonymous_63_._set_name('anonymous')
    @Js
    def PyJs_anonymous_64_(a, this, arguments, var=var):
        var = Scope({'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['a'])
        var.get('a').put('sigBytes', (var.get('a').get('words').get(PyJsBshift((var.get('a').get('sigBytes')-Js(1.0)),Js(2.0)))&Js(255.0)), '-')
    PyJs_anonymous_64_._set_name('anonymous')
    var.put('q', var.get('p').put('pad', Js({})).put('Pkcs7', Js({'pad':PyJs_anonymous_63_,'unpad':PyJs_anonymous_64_})))
    @Js
    def PyJs_anonymous_65_(this, arguments, var=var):
        var = Scope({'this':this, 'arguments':arguments}, var)
        var.registers(['b', 'c', 'a'])
        var.get('v').get('reset').callprop('call', var.get(u"this"))
        var.put('a', var.get(u"this").get('cfg'))
        var.put('b', var.get('a').get('iv'))
        var.put('a', var.get('a').get('mode'))
        if (var.get(u"this").get('_xformMode')==var.get(u"this").get('_ENC_XFORM_MODE')):
            var.put('c', var.get('a').get('createEncryptor'))
        else:
            PyJsComma(var.put('c', var.get('a').get('createDecryptor')),var.get(u"this").put('_minBufferSize', Js(1.0)))
        var.get(u"this").put('_mode', var.get('c').callprop('call', var.get('a'), var.get(u"this"), (var.get('b') and var.get('b').get('words'))))
    PyJs_anonymous_65_._set_name('anonymous')
    @Js
    def PyJs_anonymous_66_(a, b, this, arguments, var=var):
        var = Scope({'a':a, 'b':b, 'this':this, 'arguments':arguments}, var)
        var.registers(['b', 'a'])
        var.get(u"this").get('_mode').callprop('processBlock', var.get('a'), var.get('b'))
    PyJs_anonymous_66_._set_name('anonymous')
    @Js
    def PyJs_anonymous_67_(this, arguments, var=var):
        var = Scope({'this':this, 'arguments':arguments}, var)
        var.registers(['b', 'a'])
        var.put('a', var.get(u"this").get('cfg').get('padding'))
        if (var.get(u"this").get('_xformMode')==var.get(u"this").get('_ENC_XFORM_MODE')):
            var.get('a').callprop('pad', var.get(u"this").get('_data'), var.get(u"this").get('blockSize'))
            var.put('b', var.get(u"this").callprop('_process', Js(0.0).neg()))
        else:
            PyJsComma(var.put('b', var.get(u"this").callprop('_process', Js(0.0).neg())),var.get('a').callprop('unpad', var.get('b')))
        return var.get('b')
    PyJs_anonymous_67_._set_name('anonymous')
    var.get('d').put('BlockCipher', var.get('v').callprop('extend', Js({'cfg':var.get('v').get('cfg').callprop('extend', Js({'mode':var.get('b'),'padding':var.get('q')})),'reset':PyJs_anonymous_65_,'_doProcessBlock':PyJs_anonymous_66_,'_doFinalize':PyJs_anonymous_67_,'blockSize':Js(4.0)})))
    @Js
    def PyJs_anonymous_68_(a, this, arguments, var=var):
        var = Scope({'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['a'])
        var.get(u"this").callprop('mixIn', var.get('a'))
    PyJs_anonymous_68_._set_name('anonymous')
    @Js
    def PyJs_anonymous_69_(a, this, arguments, var=var):
        var = Scope({'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['a'])
        return (var.get('a') or var.get(u"this").get('formatter')).callprop('stringify', var.get(u"this"))
    PyJs_anonymous_69_._set_name('anonymous')
    var.put('n', var.get('d').put('CipherParams', var.get('l').callprop('extend', Js({'init':PyJs_anonymous_68_,'toString':PyJs_anonymous_69_}))))
    @Js
    def PyJs_anonymous_70_(a, this, arguments, var=var):
        var = Scope({'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['b', 'a'])
        var.put('b', var.get('a').get('ciphertext'))
        var.put('a', var.get('a').get('salt'))
        return (var.get('s').callprop('create', Js([Js(1398893684.0), Js(1701076831.0)])).callprop('concat', var.get('a')).callprop('concat', var.get('b')) if var.get('a') else var.get('b')).callprop('toString', var.get('r'))
    PyJs_anonymous_70_._set_name('anonymous')
    @Js
    def PyJs_anonymous_71_(a, this, arguments, var=var):
        var = Scope({'a':a, 'this':this, 'arguments':arguments}, var)
        var.registers(['b', 'c', 'a'])
        var.put('a', var.get('r').callprop('parse', var.get('a')))
        var.put('b', var.get('a').get('words'))
        if ((Js(1398893684.0)==var.get('b').get('0')) and (Js(1701076831.0)==var.get('b').get('1'))):
            var.put('c', var.get('s').callprop('create', var.get('b').callprop('slice', Js(2.0), Js(4.0))))
            var.get('b').callprop('splice', Js(0.0), Js(4.0))
            var.get('a').put('sigBytes', Js(16.0), '-')
        return var.get('n').callprop('create', Js({'ciphertext':var.get('a'),'salt':var.get('c')}))
    PyJs_anonymous_71_._set_name('anonymous')
    var.put('b', var.get('p').put('format', Js({})).put('OpenSSL', Js({'stringify':PyJs_anonymous_70_,'parse':PyJs_anonymous_71_})))
    @Js
    def PyJs_anonymous_72_(a, b, c, d, this, arguments, var=var):
        var = Scope({'a':a, 'b':b, 'c':c, 'd':d, 'this':this, 'arguments':arguments}, var)
        var.registers(['a', 'd', 'b', 'c', 'l'])
        var.put('d', var.get(u"this").get('cfg').callprop('extend', var.get('d')))
        var.put('l', var.get('a').callprop('createEncryptor', var.get('c'), var.get('d')))
        var.put('b', var.get('l').callprop('finalize', var.get('b')))
        var.put('l', var.get('l').get('cfg'))
        return var.get('n').callprop('create', Js({'ciphertext':var.get('b'),'key':var.get('c'),'iv':var.get('l').get('iv'),'algorithm':var.get('a'),'mode':var.get('l').get('mode'),'padding':var.get('l').get('padding'),'blockSize':var.get('a').get('blockSize'),'formatter':var.get('d').get('format')}))
    PyJs_anonymous_72_._set_name('anonymous')
    @Js
    def PyJs_anonymous_73_(a, b, c, d, this, arguments, var=var):
        var = Scope({'a':a, 'b':b, 'c':c, 'd':d, 'this':this, 'arguments':arguments}, var)
        var.registers(['b', 'c', 'a', 'd'])
        var.put('d', var.get(u"this").get('cfg').callprop('extend', var.get('d')))
        var.put('b', var.get(u"this").callprop('_parse', var.get('b'), var.get('d').get('format')))
        return var.get('a').callprop('createDecryptor', var.get('c'), var.get('d')).callprop('finalize', var.get('b').get('ciphertext'))
    PyJs_anonymous_73_._set_name('anonymous')
    @Js
    def PyJs_anonymous_74_(a, b, this, arguments, var=var):
        var = Scope({'a':a, 'b':b, 'this':this, 'arguments':arguments}, var)
        var.registers(['b', 'a'])
        return (var.get('b').callprop('parse', var.get('a'), var.get(u"this")) if (Js('string')==var.get('a',throw=False).typeof()) else var.get('a'))
    PyJs_anonymous_74_._set_name('anonymous')
    var.put('a', var.get('d').put('SerializableCipher', var.get('l').callprop('extend', Js({'cfg':var.get('l').callprop('extend', Js({'format':var.get('b')})),'encrypt':PyJs_anonymous_72_,'decrypt':PyJs_anonymous_73_,'_parse':PyJs_anonymous_74_}))))
    @Js
    def PyJs_anonymous_75_(a, b, c, d, this, arguments, var=var):
        var = Scope({'a':a, 'b':b, 'c':c, 'd':d, 'this':this, 'arguments':arguments}, var)
        var.registers(['b', 'c', 'a', 'd'])
        (var.get('d') or var.put('d', var.get('s').callprop('random', Js(8.0))))
        var.put('a', var.get('w').callprop('create', Js({'keySize':(var.get('b')+var.get('c'))})).callprop('compute', var.get('a'), var.get('d')))
        var.put('c', var.get('s').callprop('create', var.get('a').get('words').callprop('slice', var.get('b')), (Js(4.0)*var.get('c'))))
        var.get('a').put('sigBytes', (Js(4.0)*var.get('b')))
        return var.get('n').callprop('create', Js({'key':var.get('a'),'iv':var.get('c'),'salt':var.get('d')}))
    PyJs_anonymous_75_._set_name('anonymous')
    var.put('p', var.get('p').put('kdf', Js({})).put('OpenSSL', Js({'execute':PyJs_anonymous_75_})))
    @Js
    def PyJs_anonymous_76_(b, c, d, l, this, arguments, var=var):
        var = Scope({'b':b, 'c':c, 'd':d, 'l':l, 'this':this, 'arguments':arguments}, var)
        var.registers(['b', 'c', 'l', 'd'])
        var.put('l', var.get(u"this").get('cfg').callprop('extend', var.get('l')))
        var.put('d', var.get('l').get('kdf').callprop('execute', var.get('d'), var.get('b').get('keySize'), var.get('b').get('ivSize')))
        var.get('l').put('iv', var.get('d').get('iv'))
        var.put('b', var.get('a').get('encrypt').callprop('call', var.get(u"this"), var.get('b'), var.get('c'), var.get('d').get('key'), var.get('l')))
        var.get('b').callprop('mixIn', var.get('d'))
        return var.get('b')
    PyJs_anonymous_76_._set_name('anonymous')
    @Js
    def PyJs_anonymous_77_(b, c, d, l, this, arguments, var=var):
        var = Scope({'b':b, 'c':c, 'd':d, 'l':l, 'this':this, 'arguments':arguments}, var)
        var.registers(['b', 'c', 'l', 'd'])
        var.put('l', var.get(u"this").get('cfg').callprop('extend', var.get('l')))
        var.put('c', var.get(u"this").callprop('_parse', var.get('c'), var.get('l').get('format')))
        var.put('d', var.get('l').get('kdf').callprop('execute', var.get('d'), var.get('b').get('keySize'), var.get('b').get('ivSize'), var.get('c').get('salt')))
        var.get('l').put('iv', var.get('d').get('iv'))
        return var.get('a').get('decrypt').callprop('call', var.get(u"this"), var.get('b'), var.get('c'), var.get('d').get('key'), var.get('l'))
    PyJs_anonymous_77_._set_name('anonymous')
    var.put('c', var.get('d').put('PasswordBasedCipher', var.get('a').callprop('extend', Js({'cfg':var.get('a').get('cfg').callprop('extend', Js({'kdf':var.get('p')})),'encrypt':PyJs_anonymous_76_,'decrypt':PyJs_anonymous_77_}))))
PyJs_anonymous_45_._set_name('anonymous')
(var.get('CryptoJS').get('lib').get('Cipher') or PyJs_anonymous_45_())
@Js
def PyJs_anonymous_78_(this, arguments, var=var):
    var = Scope({'this':this, 'arguments':arguments}, var)
    var.registers(['a', 'd', 'b', 'F', 's', 'c', 'n', 'e', 'u', 'p', 'x', 'y', 'k', 'r', 'q', 'l', 'w', 'v', 'G', 't', 'j', 'H', 'z'])
    #for JS loop
    var.put('u', var.get('CryptoJS'))
    var.put('p', var.get('u').get('lib').get('BlockCipher'))
    var.put('d', var.get('u').get('algo'))
    var.put('l', Js([]))
    var.put('s', Js([]))
    var.put('t', Js([]))
    var.put('r', Js([]))
    var.put('w', Js([]))
    var.put('v', Js([]))
    var.put('b', Js([]))
    var.put('x', Js([]))
    var.put('q', Js([]))
    var.put('n', Js([]))
    var.put('a', Js([]))
    var.put('c', Js(0.0))
    while (Js(256.0)>var.get('c')):
        try:
            var.get('a').put(var.get('c'), ((var.get('c')<<Js(1.0)) if (Js(128.0)>var.get('c')) else ((var.get('c')<<Js(1.0))^Js(283.0))))
        finally:
                (var.put('c',Js(var.get('c').to_number())+Js(1))-Js(1))
    #for JS loop
    var.put('e', Js(0.0))
    var.put('j', Js(0.0))
    var.put('c', Js(0.0))
    while (Js(256.0)>var.get('c')):
        try:
            var.put('k', ((((var.get('j')^(var.get('j')<<Js(1.0)))^(var.get('j')<<Js(2.0)))^(var.get('j')<<Js(3.0)))^(var.get('j')<<Js(4.0))))
            var.put('k', ((PyJsBshift(var.get('k'),Js(8.0))^(var.get('k')&Js(255.0)))^Js(99.0)))
            var.get('l').put(var.get('e'), var.get('k'))
            var.get('s').put(var.get('k'), var.get('e'))
            var.put('z', var.get('a').get(var.get('e')))
            var.put('F', var.get('a').get(var.get('z')))
            var.put('G', var.get('a').get(var.get('F')))
            var.put('y', ((Js(257.0)*var.get('a').get(var.get('k')))^(Js(16843008.0)*var.get('k'))))
            var.get('t').put(var.get('e'), ((var.get('y')<<Js(24.0))|PyJsBshift(var.get('y'),Js(8.0))))
            var.get('r').put(var.get('e'), ((var.get('y')<<Js(16.0))|PyJsBshift(var.get('y'),Js(16.0))))
            var.get('w').put(var.get('e'), ((var.get('y')<<Js(8.0))|PyJsBshift(var.get('y'),Js(24.0))))
            var.get('v').put(var.get('e'), var.get('y'))
            var.put('y', ((((Js(16843009.0)*var.get('G'))^(Js(65537.0)*var.get('F')))^(Js(257.0)*var.get('z')))^(Js(16843008.0)*var.get('e'))))
            var.get('b').put(var.get('k'), ((var.get('y')<<Js(24.0))|PyJsBshift(var.get('y'),Js(8.0))))
            var.get('x').put(var.get('k'), ((var.get('y')<<Js(16.0))|PyJsBshift(var.get('y'),Js(16.0))))
            var.get('q').put(var.get('k'), ((var.get('y')<<Js(8.0))|PyJsBshift(var.get('y'),Js(24.0))))
            var.get('n').put(var.get('k'), var.get('y'))
            (PyJsComma(var.put('e', (var.get('z')^var.get('a').get(var.get('a').get(var.get('a').get((var.get('G')^var.get('z'))))))),var.put('j', var.get('a').get(var.get('a').get(var.get('j'))), '^')) if var.get('e') else var.put('e', var.put('j', Js(1.0))))
        finally:
                (var.put('c',Js(var.get('c').to_number())+Js(1))-Js(1))
    var.put('H', Js([Js(0.0), Js(1.0), Js(2.0), Js(4.0), Js(8.0), Js(16.0), Js(32.0), Js(64.0), Js(128.0), Js(27.0), Js(54.0)]))
    @Js
    def PyJs_anonymous_79_(this, arguments, var=var):
        var = Scope({'this':this, 'arguments':arguments}, var)
        var.registers(['a', 'd', 'k', 'e', 'j', 'c'])
        #for JS loop
        var.put('a', var.get(u"this").get('_key'))
        var.put('c', var.get('a').get('words'))
        var.put('d', (var.get('a').get('sigBytes')/Js(4.0)))
        var.put('a', (Js(4.0)*(var.get(u"this").put('_nRounds', (var.get('d')+Js(6.0)))+Js(1.0))))
        var.put('e', var.get(u"this").put('_keySchedule', Js([])))
        var.put('j', Js(0.0))
        while (var.get('j')<var.get('a')):
            try:
                if (var.get('j')<var.get('d')):
                    var.get('e').put(var.get('j'), var.get('c').get(var.get('j')))
                else:
                    var.put('k', var.get('e').get((var.get('j')-Js(1.0))))
                    def PyJs_LONG_81_(var=var):
                        def PyJs_LONG_80_(var=var):
                            return PyJsComma(PyJsComma(var.put('k', ((var.get('k')<<Js(8.0))|PyJsBshift(var.get('k'),Js(24.0)))),var.put('k', ((((var.get('l').get(PyJsBshift(var.get('k'),Js(24.0)))<<Js(24.0))|(var.get('l').get((PyJsBshift(var.get('k'),Js(16.0))&Js(255.0)))<<Js(16.0)))|(var.get('l').get((PyJsBshift(var.get('k'),Js(8.0))&Js(255.0)))<<Js(8.0)))|var.get('l').get((var.get('k')&Js(255.0)))))),var.put('k', (var.get('H').get(((var.get('j')/var.get('d'))|Js(0.0)))<<Js(24.0)), '^'))
                        return ((((Js(6.0)<var.get('d')) and (Js(4.0)==(var.get('j')%var.get('d')))) and var.put('k', ((((var.get('l').get(PyJsBshift(var.get('k'),Js(24.0)))<<Js(24.0))|(var.get('l').get((PyJsBshift(var.get('k'),Js(16.0))&Js(255.0)))<<Js(16.0)))|(var.get('l').get((PyJsBshift(var.get('k'),Js(8.0))&Js(255.0)))<<Js(8.0)))|var.get('l').get((var.get('k')&Js(255.0)))))) if (var.get('j')%var.get('d')) else PyJs_LONG_80_())
                    PyJs_LONG_81_()
                    var.get('e').put(var.get('j'), (var.get('e').get((var.get('j')-var.get('d')))^var.get('k')))
            finally:
                    (var.put('j',Js(var.get('j').to_number())+Js(1))-Js(1))
        var.put('c', var.get(u"this").put('_invKeySchedule', Js([])))
        #for JS loop
        var.put('d', Js(0.0))
        while (var.get('d')<var.get('a')):
            try:
                def PyJs_LONG_82_(var=var):
                    return var.get('c').put(var.get('d'), (var.get('k') if ((Js(4.0)>var.get('d')) or (Js(4.0)>=var.get('j'))) else (((var.get('b').get(var.get('l').get(PyJsBshift(var.get('k'),Js(24.0))))^var.get('x').get(var.get('l').get((PyJsBshift(var.get('k'),Js(16.0))&Js(255.0)))))^var.get('q').get(var.get('l').get((PyJsBshift(var.get('k'),Js(8.0))&Js(255.0)))))^var.get('n').get(var.get('l').get((var.get('k')&Js(255.0)))))))
                PyJsComma(PyJsComma(var.put('j', (var.get('a')-var.get('d'))),var.put('k', (var.get('e').get(var.get('j')) if (var.get('d')%Js(4.0)) else var.get('e').get((var.get('j')-Js(4.0)))))),PyJs_LONG_82_())
            finally:
                    (var.put('d',Js(var.get('d').to_number())+Js(1))-Js(1))
    PyJs_anonymous_79_._set_name('anonymous')
    @Js
    def PyJs_anonymous_83_(a, b, this, arguments, var=var):
        var = Scope({'a':a, 'b':b, 'this':this, 'arguments':arguments}, var)
        var.registers(['b', 'a'])
        var.get(u"this").callprop('_doCryptBlock', var.get('a'), var.get('b'), var.get(u"this").get('_keySchedule'), var.get('t'), var.get('r'), var.get('w'), var.get('v'), var.get('l'))
    PyJs_anonymous_83_._set_name('anonymous')
    @Js
    def PyJs_anonymous_84_(a, c, this, arguments, var=var):
        var = Scope({'a':a, 'c':c, 'this':this, 'arguments':arguments}, var)
        var.registers(['c', 'a', 'd'])
        var.put('d', var.get('a').get((var.get('c')+Js(1.0))))
        var.get('a').put((var.get('c')+Js(1.0)), var.get('a').get((var.get('c')+Js(3.0))))
        var.get('a').put((var.get('c')+Js(3.0)), var.get('d'))
        var.get(u"this").callprop('_doCryptBlock', var.get('a'), var.get('c'), var.get(u"this").get('_invKeySchedule'), var.get('b'), var.get('x'), var.get('q'), var.get('n'), var.get('s'))
        var.put('d', var.get('a').get((var.get('c')+Js(1.0))))
        var.get('a').put((var.get('c')+Js(1.0)), var.get('a').get((var.get('c')+Js(3.0))))
        var.get('a').put((var.get('c')+Js(3.0)), var.get('d'))
    PyJs_anonymous_84_._set_name('anonymous')
    @Js
    def PyJs_anonymous_85_(a, b, c, d, e, j, l, f, this, arguments, var=var):
        var = Scope({'a':a, 'b':b, 'c':c, 'd':d, 'e':e, 'j':j, 'l':l, 'f':f, 'this':this, 'arguments':arguments}, var)
        var.registers(['f', 'm', 'a', 'd', 'p', 'b', 'k', 'h', 's', 'r', 't', 'e', 'j', 'q', 'c', 'g', 'l', 'n'])
        #for JS loop
        var.put('m', var.get(u"this").get('_nRounds'))
        var.put('g', (var.get('a').get(var.get('b'))^var.get('c').get('0')))
        var.put('h', (var.get('a').get((var.get('b')+Js(1.0)))^var.get('c').get('1')))
        var.put('k', (var.get('a').get((var.get('b')+Js(2.0)))^var.get('c').get('2')))
        var.put('n', (var.get('a').get((var.get('b')+Js(3.0)))^var.get('c').get('3')))
        var.put('p', Js(4.0))
        var.put('r', Js(1.0))
        while (var.get('r')<var.get('m')):
            try:
                var.put('q', ((((var.get('d').get(PyJsBshift(var.get('g'),Js(24.0)))^var.get('e').get((PyJsBshift(var.get('h'),Js(16.0))&Js(255.0))))^var.get('j').get((PyJsBshift(var.get('k'),Js(8.0))&Js(255.0))))^var.get('l').get((var.get('n')&Js(255.0))))^var.get('c').get((var.put('p',Js(var.get('p').to_number())+Js(1))-Js(1)))))
                var.put('s', ((((var.get('d').get(PyJsBshift(var.get('h'),Js(24.0)))^var.get('e').get((PyJsBshift(var.get('k'),Js(16.0))&Js(255.0))))^var.get('j').get((PyJsBshift(var.get('n'),Js(8.0))&Js(255.0))))^var.get('l').get((var.get('g')&Js(255.0))))^var.get('c').get((var.put('p',Js(var.get('p').to_number())+Js(1))-Js(1)))))
                var.put('t', ((((var.get('d').get(PyJsBshift(var.get('k'),Js(24.0)))^var.get('e').get((PyJsBshift(var.get('n'),Js(16.0))&Js(255.0))))^var.get('j').get((PyJsBshift(var.get('g'),Js(8.0))&Js(255.0))))^var.get('l').get((var.get('h')&Js(255.0))))^var.get('c').get((var.put('p',Js(var.get('p').to_number())+Js(1))-Js(1)))))
                var.put('n', ((((var.get('d').get(PyJsBshift(var.get('n'),Js(24.0)))^var.get('e').get((PyJsBshift(var.get('g'),Js(16.0))&Js(255.0))))^var.get('j').get((PyJsBshift(var.get('h'),Js(8.0))&Js(255.0))))^var.get('l').get((var.get('k')&Js(255.0))))^var.get('c').get((var.put('p',Js(var.get('p').to_number())+Js(1))-Js(1)))))
                var.put('g', var.get('q'))
                var.put('h', var.get('s'))
                var.put('k', var.get('t'))
            finally:
                    (var.put('r',Js(var.get('r').to_number())+Js(1))-Js(1))
        var.put('q', (((((var.get('f').get(PyJsBshift(var.get('g'),Js(24.0)))<<Js(24.0))|(var.get('f').get((PyJsBshift(var.get('h'),Js(16.0))&Js(255.0)))<<Js(16.0)))|(var.get('f').get((PyJsBshift(var.get('k'),Js(8.0))&Js(255.0)))<<Js(8.0)))|var.get('f').get((var.get('n')&Js(255.0))))^var.get('c').get((var.put('p',Js(var.get('p').to_number())+Js(1))-Js(1)))))
        var.put('s', (((((var.get('f').get(PyJsBshift(var.get('h'),Js(24.0)))<<Js(24.0))|(var.get('f').get((PyJsBshift(var.get('k'),Js(16.0))&Js(255.0)))<<Js(16.0)))|(var.get('f').get((PyJsBshift(var.get('n'),Js(8.0))&Js(255.0)))<<Js(8.0)))|var.get('f').get((var.get('g')&Js(255.0))))^var.get('c').get((var.put('p',Js(var.get('p').to_number())+Js(1))-Js(1)))))
        var.put('t', (((((var.get('f').get(PyJsBshift(var.get('k'),Js(24.0)))<<Js(24.0))|(var.get('f').get((PyJsBshift(var.get('n'),Js(16.0))&Js(255.0)))<<Js(16.0)))|(var.get('f').get((PyJsBshift(var.get('g'),Js(8.0))&Js(255.0)))<<Js(8.0)))|var.get('f').get((var.get('h')&Js(255.0))))^var.get('c').get((var.put('p',Js(var.get('p').to_number())+Js(1))-Js(1)))))
        var.put('n', (((((var.get('f').get(PyJsBshift(var.get('n'),Js(24.0)))<<Js(24.0))|(var.get('f').get((PyJsBshift(var.get('g'),Js(16.0))&Js(255.0)))<<Js(16.0)))|(var.get('f').get((PyJsBshift(var.get('h'),Js(8.0))&Js(255.0)))<<Js(8.0)))|var.get('f').get((var.get('k')&Js(255.0))))^var.get('c').get((var.put('p',Js(var.get('p').to_number())+Js(1))-Js(1)))))
        var.get('a').put(var.get('b'), var.get('q'))
        var.get('a').put((var.get('b')+Js(1.0)), var.get('s'))
        var.get('a').put((var.get('b')+Js(2.0)), var.get('t'))
        var.get('a').put((var.get('b')+Js(3.0)), var.get('n'))
    PyJs_anonymous_85_._set_name('anonymous')
    var.put('d', var.get('d').put('AES', var.get('p').callprop('extend', Js({'_doReset':PyJs_anonymous_79_,'encryptBlock':PyJs_anonymous_83_,'decryptBlock':PyJs_anonymous_84_,'_doCryptBlock':PyJs_anonymous_85_,'keySize':Js(8.0)}))))
    var.get('u').put('AES', var.get('p').callprop('_createHelper', var.get('d')))
PyJs_anonymous_78_._set_name('anonymous')
PyJs_anonymous_78_()
pass
pass
pass
var.put('$_chars', Js('ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'))
var.put('_chars_len', var.get('$_chars').get('length'))
pass
pass


# Add lib to the module scope
encrypt = var.to_python()