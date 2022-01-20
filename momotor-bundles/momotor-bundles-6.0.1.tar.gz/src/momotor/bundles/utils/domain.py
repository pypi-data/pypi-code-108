import typing

__all__ = ['split_domain', 'unsplit_domain', 'merge_domains', 'DOMAIN_SEP']


DOMAIN_SEP = '#'


def split_domain(domain: typing.Optional[str]) -> typing.Tuple[typing.Optional[str], typing.Optional[str]]:
    """ Split a domain name `<domain>[#<subdomain>]` into its parts.

    >>> split_domain(None)
    (None, None)

    >>> split_domain('')
    (None, None)

    >>> split_domain('#')
    (None, None)

    >>> split_domain('domain')
    ('domain', None)

    >>> split_domain('domain#')
    ('domain', None)

    >>> split_domain('#subdomain')
    (None, 'subdomain')

    >>> split_domain('domain#subdomain')
    ('domain', 'subdomain')

    :param domain: The domain
    :return: a two-tuple with the parts
    """
    assert domain is None or domain.count(DOMAIN_SEP) < 2

    if domain and DOMAIN_SEP in domain:
        domain, subdomain = tuple(domain.split(DOMAIN_SEP, 1))
        if not domain:
            domain = None
        if not subdomain:
            subdomain = None
    else:
        subdomain = None

    return domain or None, subdomain or None


def unsplit_domain(domain: typing.Optional[str], subdomain: typing.Optional[str]) -> typing.Optional[str]:
    """ Merge `<domain>` and `<subdomain>` parts into a `<domain>#<subdomain>` string, handling ``None`` values

    The reverse operation of :py:func:`split_domain`.

    >>> unsplit_domain(None, None) is None
    True

    >>> unsplit_domain('domain', None)
    'domain'

    >>> unsplit_domain('domain', '')
    'domain'

    >>> unsplit_domain(None, 'subdomain')
    '#subdomain'

    >>> unsplit_domain('domain', 'subdomain')
    'domain#subdomain'

    :param: domain: The domain part
    :param: subdomain: The subdomain part
    :return: the joined domain
    """
    assert domain is None or DOMAIN_SEP not in domain
    assert subdomain is None or DOMAIN_SEP not in subdomain

    if domain:
        return f'{domain}{DOMAIN_SEP}{subdomain}' if subdomain else domain
    elif subdomain:
        return f'{DOMAIN_SEP}{subdomain}'

    return None


def merge_domains(*domains: typing.Optional[str]) -> typing.Optional[str]:
    """ Merge domains of format `<domain>#<subdomain>`.

    For all domains, the first provided part is returned as part of the merged domain::

      abc#def | uvw#xyz = abc#def
      abc#def | uvw     = abc#def
      abc#def |    #xyz = abc#def
      abc     | uvw#xyz = abc#xyz
      abc     | uvw     = abc
      abc     |    #xyz = abc#xyz
         #def | uvw#xyz = uwv#def
         #def | uvw     = uwv#def
         #def |    #xyz =    #def

    >>> merge_domains() is None
    True

    >>> merge_domains(None) is None
    True

    >>> merge_domains('abc#def', 'uvw')
    'abc#def'

    >>> merge_domains('abc#def', '#xyz')
    'abc#def'

    >>> merge_domains('abc#def', 'uvw#xyz')
    'abc#def'

    >>> merge_domains('abc', 'uvw#xyz')
    'abc#xyz'

    >>> merge_domains('abc', 'uvw')
    'abc'

    >>> merge_domains('abc', '#xyz')
    'abc#xyz'

    >>> merge_domains('#def', 'uvw#xyz')
    'uvw#def'

    >>> merge_domains('#def', 'uvw')
    'uvw#def'

    >>> merge_domains('#def', '#xyz')
    '#def'

    """
    dom, sub = None, None
    for domain in domains:
        new_dom, new_sub = split_domain(domain)
        if dom is None:
            dom = new_dom
        if sub is None:
            sub = new_sub

        if dom and sub:
            break

    return unsplit_domain(dom, sub)
