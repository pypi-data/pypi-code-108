import click
from aiconfig import build


class KeyValuePairs(click.ParamType):
    """Convert to key value pairs"""
    name = "key-value-pairs"

    def convert(self, value, param, ctx):
        """
        Convert to key value pairs

        :param value: value
        :param param: parameter
        :param ctx: context
        """
        if not value.strip():
            return {}
        try:
            my_dict = dict([x.split('=') for x in value.split(',')])
            for k, val in my_dict.items():
                if val.isnumeric():
                    my_dict[k] = eval(val)
                elif val in {'true', 'True', 'false', 'False'}:
                    my_dict[k] = val.lower == 'true'
                elif '+' in val:
                    val = val.split('+')
                    val = [x for x in val if x]
                    val = [eval(x) if x.isnumeric() else x for x in val]
                    my_dict[k] = val
            return my_dict
        except TypeError:
            self.fail(
                "expected string for key-value-pairs() conversion, got "
                f"{value!r} of type {type(value).__name__}",
                param,
                ctx,
            )
        except ValueError as e:
            self.fail(f"{value!r} is not a valid key-value-pair: {e}", param, ctx)


@click.command(help='CLI tool for aiconfig')
@click.option('-c', '--config', help='path to base config for build')
@click.option('-t', '--target', default=None, help='target other than root node in build')
@click.option('-p', '--parameters', default=None, help='parameters/options to add to build',
              type=KeyValuePairs())
@click.option('--dry-run/--no-dry-run', default=False, help='key-value pairs to add to build')
def build(config, target, kwargs, dry_run):
    if kwargs is None:
        _build(config, target, strict=True, dry_run=dry_run)
    else:
        _build(config, target, **kwargs, strict=True, dry_run=dry_run)


if __name__ == '__main__':
    build()
