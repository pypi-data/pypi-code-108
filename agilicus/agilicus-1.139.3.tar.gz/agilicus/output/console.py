from agilicus import context


def output_if_console(ctx, output: str):
    if context.output_console(ctx):
        print(output)
