from decimal import Decimal
from functools import reduce
from itertools import chain
from uuid import UUID

from bitfield import BitHandler , Bit
from django.db.models import ForeignKey
from isc_common import setAttr


def del_last_zero( value ) :
    if isinstance( value , str ) :
        return value

    res = str( value )
    # res.split('.')
    cel = res.split( '.' )[ 0 ]
    float = res.split( '.' )[ 1 :4 ][ 0 ].rstrip( '0' )
    float = StrToNumber( float )
    if isinstance( float , int ) and float > 0 :
        return f'{cel}.{float}'
    return cel


def DecimalToStr( value , noneId_0=False ) :
    if value is None :
        return ''

    try :
        if value == 0 and noneId_0 is True :
            return None

        res = del_last_zero( value=value )
        return res
    except IndexError :
        return value


def StrToNumber( s1 , default_blank=0 ) :
    if s1 is None :
        return None

    if s1 == '' :
        return default_blank

    if not isinstance( s1 , str ) :
        raise Exception( f'{s1} is not str type.' )

    s = s1.replace( ',' , '.' )

    if not isinstance( s , str ) :
        raise Exception( f'{s} is not str type.' )
    try :
        return int( s )
    except ValueError :
        try :
            return float( s )
        except ValueError as ex :
            return None


def IntToNumber( s ) :
    if s is None :
        return None

    if not isinstance( s , int ) :
        raise Exception( f'{s} is not int type.' )

    return float( s )


def IntToStr( value ) :
    if value is None :
        return None

    if not isinstance( value , str ) :
        return value

    if not isinstance( value , int ) :
        return del_last_zero( value=value )

    raise Exception( f'{value}  must be int' )


def ToStr( s ) :
    if s is None or s == 'null' :
        return None

    if isinstance( s , str ) :
        return s

    if isinstance( s , Decimal ) :
        return DecimalToStr( s )

    if isinstance( s , int ) :
        return IntToStr(s)

    if isinstance( s , UUID ) :
        return str( s ).replace( '-' , '_' )

    return s


def ToNumber( s ) :
    if s is None :
        return 0

    if isinstance( s , int ) :
        return IntToNumber( s )
    elif isinstance( s , str ) :
        return StrToNumber( s )
    elif isinstance( s , float ) :
        return s
    elif isinstance( s , Decimal ) :
        return float( s )
    else :
        raise Exception( f'{s} unknown type.' )


def ToInt( s ) :
    if s is None :
        return None

    if isinstance( s , int ) :
        return s
    elif isinstance( s , str ) :
        return StrToNumber( s )
    elif isinstance( s , float ) :
        return int( s )
    elif isinstance( s , Decimal ) :
        return int( s )
    else :
        raise Exception( f'{s} unknown type.' )


def ToBoolYesNone( value ) :
    if not isinstance( value , int ) :
        return '--'
    if value == 0 :
        return 'Нет'
    elif value == 1 :
        return 'Да'
    else :
        return '--'


def GetListFromStringCortege( stingCortege ) :
    if stingCortege is None :
        return [ None , None ]
    return list( map( lambda x : TryToInt( x ) , stingCortege.replace( '(' , '' ).replace( ')' , '' ).split( ',' ) ) )


def TryToInt( s ) :
    if s is None :
        return None

    try :
        if isinstance( s , int ) :
            return s
        elif isinstance( s , str ) :
            res = StrToNumber( s )
            return res if res is not None else s
        elif isinstance( s , float ) :
            return int( s )
        elif isinstance( s , Decimal ) :
            return int( s )
    except ValueError as ex :
        return s


def ToDecimal( s ) :
    if s is None :
        return 0

    if isinstance( s , int ) :
        return Decimal( s )
    elif isinstance( s , str ) :
        if len( s ) == 0 :
            return 0
        return Decimal( s )
    elif isinstance( s , float ) :
        return Decimal( s )
    elif isinstance( s , Decimal ) :
        return s
    else :
        raise Exception( f'{s} unknown type.' )


def IntToDecimal( s ) :
    if s is None :
        return None

    if not isinstance( s , int ) :
        raise Exception( f'{s} is not int type.' )

    return Decimal( s )


def IntToBool( s ) :
    if s is None :
        return False

    if not isinstance( s , int ) :
        raise Exception( f'{s} is not int type.' )

    if s > 0 :
        return True
    return False


def StrToInt( s ) :
    if s is None :
        return None
    try :
        return int( s )
    except ValueError as ex :
        return None


def DelProps( value ) :
    if isinstance( value , dict ) :
        for key , _value in value.items() :
            if isinstance( _value , BitHandler ) :
                setAttr( value , key , _value._value )
            elif isinstance( _value , Bit ) :
                setAttr( value , key , _value.is_set )
        return value
    else :
        value


def GetPropsInt( value ) :
    if isinstance( value , BitHandler ) :
        return value._value
    else :
        value


def model_2_dict( instance , fields=None , exclude=None ) :
    """
    Return a dict containing the data in ``instance`` suitable for passing as
    a Form's ``initial`` keyword argument.

    ``fields`` is an optional list of field names. If provided, return only the
    named.

    ``exclude`` is an optional list of field names. If provided, exclude the
    named from the returned dict, even if they are listed in the ``fields``
    argument.
    """
    opts = instance._meta
    data = { }
    for f in chain( opts.concrete_fields , opts.private_fields , opts.many_to_many ) :
        if not getattr( f , 'editable' , False ) :
            continue
        if fields is not None and f.name not in fields :
            continue
        if exclude and f.name in exclude :
            continue
        if isinstance( f , ForeignKey ) :
            data[ f'{f.name}_id' ] = f.value_from_object( instance )
        else :
            data[ f.name ] = f.value_from_object( instance )
    return data


def compare_2_dict( dict1 , dict2 ) :
    if not isinstance( dict1 , dict ) :
        raise Exception( f'dict1 must be dict' )

    if not isinstance( dict2 , dict ) :
        raise Exception( f'dict2 must be dict' )

    messages = [ ]

    for x_values , y_values in zip( dict1.items() , dict2.items() ) :
        if x_values != y_values :
            messages.append( f'{x_values} != {y_values}' )
    return messages


def flen( iterable ) :
    return reduce( lambda sum , element : sum + 1 , iterable , 0 )


class Set :
    _lst = [ ]
    _set = set()

    def __init__( self , lst=set() ) :
        if isinstance( lst , set ) :
            self._set.clear()
            for l in list( lst ) :
                self._set.add( l )

        if isinstance( lst , list ) :
            self._lst = lst

    def __str__( self ) :
        if self._set is not None :
            _lst = list( self._set )
            _lst = [ str( l ) for l in _lst ]

            _str = ' , '.join( _lst )
            return f'''({_str})'''
        elif self._lst is not None :
            _lst = [ str( l ) for l in self._lst ]
            _str = ' , '.join( _lst )
            return f'''({_str})'''
        else :
            return '()'

    def is_exists( self , element ) :
        _len = len( self._set )
        self._set.add( element )
        return _len == len( self._set )

    @property
    def get_set_sorted_as_original( self ) :
        if self._lst is not None :
            return sorted( set( self._lst ) , key=self._lst.index )
        elif self._set is not None :
            return list( self._set )
        else :
            return [ ]
