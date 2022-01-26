

def urljoin(*args):
    """Join args into a url. Trailing but not leading slashes are removed."""
    args = [str(x).rstrip('/').lstrip('/') for x in args]
    return '/'.join(args)
