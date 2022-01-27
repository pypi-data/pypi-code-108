import click
import xnat

from .utils import unpack_context

@click.group(name="rest")
@click.pass_context
def rest(ctx):
    """
    Perform various REST requests to the target XNAT.
    """

@rest.command()
@click.argument('path')
@click.option('--query', multiple=True, help="The values to be added to the query string in the URI.")
@click.option('--headers', multiple=True, help="HTTP headers to include.")
@click.pass_context
def get(ctx, path, query, headers):
    """Perform GET request to the target XNAT."""
    ctx = unpack_context(ctx)
    
    if query:
        query = {arg[0]:arg[1] for arg in map(lambda x: x.split("="), query)}

    if headers:
        headers = {arg[0]:arg[1] for arg in map(lambda x: x.split("="), headers)}
    
    with xnat.connect(ctx.host, user=ctx.user, netrc_file=ctx.netrc, jsession=ctx.jsession,
                      cli=True, no_parse_model=True, loglevel=ctx.loglevel) as session:
        result = session.get(path, query=query, timeout=ctx.timeout)
        click.echo('Result: {text}'.format(text=result.text))
        click.echo('Path {path} {user}'.format(path=path, user=ctx.user))


@rest.command()
@click.argument('path')
@click.option('--query', multiple=True, help="The values to be added to the query string in the URI.")
@click.option('--headers', multiple=True, help="HTTP headers to include.")
@click.pass_context
def head(ctx, path, query, headers):
    """Perform HEAD request to the target XNAT."""
    ctx = unpack_context(ctx)

    if query:
        query = {arg[0]:arg[1] for arg in map(lambda x: x.split("="), query)}

    if headers:
        headers = {arg[0]:arg[1] for arg in map(lambda x: x.split("="), headers)}
    
    with xnat.connect(ctx.host, user=ctx.user, netrc_file=ctx.netrc, jsession=ctx.jsession,
                      cli=True, no_parse_model=True, loglevel=ctx.loglevel) as session:
        result = session.head(path, timeout=ctx.timeout, query=query, headers=headers)
        click.echo('Result: {text}'.format(text=result.text))
        click.echo('Path {path} {user}'.format(path=path, user=ctx.user))


@rest.command()
@click.argument('path')
@click.option('--jsonpath', '-j', help="JSON payload file location.")
@click.option('--datapath', '-d', help="Data payload file location.")
@click.option('--query', multiple=True, help="The values to be added to the query string in the URI.")
@click.option('--headers', multiple=True, help="HTTP headers to include.")
@click.pass_context
def post(ctx, path, jsonpath, datapath, query, headers):
    """Perform POST request to the target XNAT."""
    ctx = unpack_context(ctx)
    
    if jsonpath is not None:
        with open(jsonpath, 'r') as json_file:
            json_payload = json_file.read()
    else:
        json_payload = None
    
    if datapath is not None:
        with open(datapath, 'r') as data_file:
            data_payload = data_file.read()
    else:
        data_payload = None

    if query:
        query = {arg[0]:arg[1] for arg in map(lambda x: x.split("="), query)}
    
    if headers:
        headers = {arg[0]:arg[1] for arg in map(lambda x: x.split("="), headers)}

    with xnat.connect(ctx.host, user=ctx.user, netrc_file=ctx.netrc, jsession=ctx.jsession,
                      cli=True, no_parse_model=True, loglevel=ctx.loglevel) as session:
        result = session.post(path, json=json_payload, data=data_payload, query=query, timeout=ctx.timeout, headers=headers)
        click.echo('Result: {text}'.format(text=result.text))
        click.echo('Path {path} {user}'.format(path=path, user=ctx.user))


@rest.command()
@click.argument('path')
@click.option('--jsonpath', '-j', help="JSON payload file location.")
@click.option('--datapath', '-d', help="Data payload file location.")
@click.option('--query', multiple=True, help="The values to be added to the query string in the URI.")
@click.option('--headers', multiple=True, help="HTTP headers to include.")
@click.pass_context
def put(ctx, path, jsonpath, datapath, query, headers):
    """Perform PUT request to the target XNAT."""
    ctx = unpack_context(ctx)
    
    if jsonpath is not None:
        with open(jsonpath, 'r') as json_file:
            json_payload = json_file.read()
    else:
        json_payload = None
    
    if datapath is not None:
        with open(datapath, 'r') as data_file:
            data_payload = data_file.read()
    else:
        data_payload = None
    
    if query:
        query = {arg[0]:arg[1] for arg in map(lambda x: x.split("="), query)}

    if headers:
        headers = {arg[0]:arg[1] for arg in map(lambda x: x.split("="), headers)} 

    with xnat.connect(ctx.host, user=ctx.user, netrc_file=ctx.netrc, jsession=ctx.jsession,
                      cli=True, no_parse_model=True, loglevel=ctx.loglevel) as session:
        result = session.put(path, json=json_payload, data=data_payload, query=query, timeout=ctx.timeout, headers=headers)
        click.echo('Result: {text}'.format(text=result.text))
        click.echo('Path {path} {user}'.format(path=path, user=ctx.user))


@rest.command()
@click.argument('path')
@click.option('--query', multiple=True, help="The values to be added to the query string in the URI.")
@click.option('--headers', multiple=True, help="HTTP headers to include.")
@click.pass_context
def delete(ctx, path, query, headers):
    """Perform DELETE request to the target XNAT."""
    ctx = unpack_context(ctx)

    if query:
        query = {arg[0]:arg[1] for arg in map(lambda x: x.split("="), query)}

    if headers:
        headers = {arg[0]:arg[1] for arg in map(lambda x: x.split("="), headers)} 

    with xnat.connect(ctx.host, user=ctx.user, netrc_file=ctx.netrc, jsession=ctx.jsession,
                      cli=True, no_parse_model=True, loglevel=ctx.loglevel) as session:
        result = session.delete(path, timeout=ctx.timeout, query=query, headers=headers)
        click.echo('Result: {text}'.format(text=result.text))
        click.echo('Path {path} {user}'.format(path=path, user=ctx.user))
