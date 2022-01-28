import click
from .util import (
    parse_path,
    input_file_argument,
    plot_option,
    trace_option,
    legacy_option,
    verbose_option,
    quiet_option,
    fancy_error_option,
    debug_option,
    log_display_level_option,
    log_exclude_option,
    network_type_argument,
    graph_layout_argument,
    graphviz_option,
    list_graph_layouts_option,
    plot_graph,
    KatState,
)


@click.command()
@input_file_argument
@plot_option
@trace_option
@legacy_option
@verbose_option
@quiet_option
@fancy_error_option
@debug_option
@log_display_level_option
@log_exclude_option
@click.pass_context
def run(
    ctx,
    input_file,
    plot,
    trace,
    legacy,
):
    """Run a Finesse script."""
    state = ctx.ensure_object(KatState)
    state.print_banner(input_file)

    model = parse_path(state, input_file, legacy=legacy)

    try:
        solution = model.run()
    except Exception as error:
        state.print_error(error, title="ANALYSIS ERROR:")

    if trace:
        try:
            trace_solution = model.beam_trace()
        except Exception as error:
            state.print_error(error, title="TRACE ERROR:")

        state.print("Trace:", fg="green", bold=True)
        state.print(trace_solution)

    if solution is not None:
        state.print("Solution:", fg="green", bold=True)
        state.print(solution, indent=1)

        if hasattr(solution, "plot") and plot:
            from .. import configure

            configure(plotting=True)
            solution.plot(show=plot)


@click.command()
@input_file_argument
@click.option(
    "--summary/--no-summary",
    is_flag=True,
    default=True,
    show_default=True,
    help="Show summary.",
)
@click.option("--graph/--no-graph", is_flag=True, default=False, help="Show graph.")
@network_type_argument
@graph_layout_argument
@graphviz_option
@list_graph_layouts_option
@legacy_option
@verbose_option
@quiet_option
@fancy_error_option
@debug_option
@log_display_level_option
@log_exclude_option
@click.pass_context
def info(ctx, input_file, summary, graph, network_type, layout, graphviz, legacy):
    """Print information about a model parsed from a script."""
    state = ctx.ensure_object(KatState)
    state.print_banner(input_file)

    model = parse_path(state, input_file, legacy=legacy)

    if summary:
        state.print("Summary:", fg="green", bold=True)
        state.print(model.info())

    if graph:
        try:
            plot_graph(
                state,
                network=model.get_network(network_type),
                layout=layout,
                graphviz=graphviz,
            )
        except Exception as e:
            state.print_error(e)


@click.command()
@input_file_argument
@click.option(
    "--from",
    "from_",
    help="Start node.",
)
@click.option(
    "--to",
    help="Stop node.",
)
@legacy_option
@verbose_option
@quiet_option
@fancy_error_option
@debug_option
@log_display_level_option
@log_exclude_option
@click.pass_context
def path(ctx, input_file, from_, to, legacy):
    """Print information about a path through the parsed model."""
    state = ctx.ensure_object(KatState)
    state.print_banner(input_file)

    model = parse_path(state, input_file, legacy=legacy)

    state.print(model.path(from_, to))


@click.command()
@input_file_argument
@click.option(
    "--direction",
    type=click.Choice(("x", "y")),
    help="Direction to compute mismatches in. If not specified, both 'x' and 'y' are computed.",
)
@legacy_option
@verbose_option
@quiet_option
@fancy_error_option
@debug_option
@log_display_level_option
@log_exclude_option
@click.pass_context
def mismatches(ctx, input_file, direction, legacy):
    """Mismatch tools."""
    state = ctx.ensure_object(KatState)
    state.print_banner(input_file)

    model = parse_path(state, input_file, legacy=legacy)

    try:
        model.print_cavity_mismatches(direction=direction)
    except Exception as error:
        state.print_error(error, title="TRACE ERROR:")


@click.command()
@input_file_argument
@click.option(
    "--from",
    "from_",
    help="Start node.",
)
@click.option(
    "--to",
    help="Stop node.",
)
@click.option(
    "--symbolic",
    is_flag=True,
    default=False,
    show_default=True,
    help="Perform symbolic trace computation.",
)
@click.option(
    "--print-distances",
    is_flag=True,
    default=False,
    show_default=True,
    help="Print component distances matrix.",
)
@click.option(
    "--plot/--no-plot",
    default=True,
    show_default=True,
    help="Display results as figure.",
)
@click.option(
    "--save-figure",
    type=click.File("wb", lazy=False),
    help="Save image of figure to file.",
)
@legacy_option
@verbose_option
@quiet_option
@fancy_error_option
@debug_option
@log_display_level_option
@log_exclude_option
@click.pass_context
def trace(
    ctx, input_file, from_, to, symbolic, print_distances, plot, save_figure, legacy
):
    """Tracing tools."""
    state = ctx.ensure_object(KatState)
    state.print_banner(input_file)

    model = parse_path(state, input_file, legacy=legacy)

    try:
        trace_solution = model.propagate_beam(from_, to, symbolic=symbolic)
    except Exception as error:
        state.print_error(error, title="TRACE ERROR:")

    state.print("Trace:", fg="green", bold=True)
    state.print(trace_solution)

    if print_distances:
        # FIXME: print using state.
        trace_solution.print_distances_matrix()

    if plot or save_figure:
        from finesse import configure

        configure(plotting=True)
        trace_solution.plot(show=plot, filename=save_figure)


@click.command()
@input_file_argument
@click.option(
    "--from",
    "from_",
    help="Start node.",
)
@click.option(
    "--to",
    help="Stop node.",
)
@click.option(
    "-p",
    "--parameter",
    "params",
    type=(str, click.Choice(("lin", "log")), float, float, int),
    multiple=True,
    help=(
        "Model parameter to animate in the form '<param> lin|log <start> <stop> <step>' (can be "
        "specified multiple times)."
    ),
)
@click.option(
    "--property",
    "props",
    type=click.Choice(("beamsize", "gouy", "curvature", "all")),
    multiple=True,
    help="Property to animate (can be specified multiple times).",
)
@click.option(
    "-i",
    "--interval",
    type=float,
    default=200,
    help="Delay between frames in milliseconds.",
)
@click.option(
    "--save-figure",
    type=click.Path(dir_okay=False, writable=True),
    help="Save image of figure to file.",
)
@legacy_option
@verbose_option
@quiet_option
@fancy_error_option
@debug_option
@log_display_level_option
@log_exclude_option
@click.pass_context
def trace_animation(
    ctx, input_file, from_, to, params, props, interval, save_figure, legacy
):
    """Animate a trace."""
    state = ctx.ensure_object(KatState)
    state.print_banner(input_file)

    model = parse_path(state, input_file, legacy=legacy)

    try:
        trace_solution = model.propagate_beam(from_, to, symbolic=True)
    except Exception as error:
        state.print_error(error, title="TRACE ERROR:")

    def parse_param_sweep(param, scale, start, stop, step):
        import numpy as np

        param = model.get(param)
        func = np.linspace if scale == "lin" else np.logspace
        return param, func(start, stop, step)

    parameters = dict(parse_param_sweep(*param) for param in params)
    trace_solution.animate(parameters, *props, interval=interval, filename=save_figure)


if __name__ == "__main__":

    @click.group()
    def entry_point():
        pass

    for command in (run, info, path, mismatches, trace, trace_animation):
        entry_point.add_command(command)

    entry_point()
