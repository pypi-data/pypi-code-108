import arrow
import click


def arrow_time_callback(_ctx, _param, value, arw_now=arrow.utcnow()) -> arrow.Arrow:
    try:
        return arw_now.dehumanize(value)
    except:
        pass
    try:
        return arrow.get(value)
    except:
        pass
    raise click.ClickException(f"cannot parse time {value}")
