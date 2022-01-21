import click


class MagicGroup(click.Group):
    def __init__(self, **attrs):
        super().__init__(**attrs)
        from magic.generate_commands import generate_commands

        generate_commands(self)

    def get_help(self, ctx):
        from magic.get_help import get_help

        return get_help(self, ctx)


@click.group(
    cls=MagicGroup,
    context_settings=dict(allow_extra_args=True, help_option_names=["-h", "--help"]),
)
def main():
    pass


@main.command(name="add")
def __add():
    """Add spell to spellbook"""
    from magic.add_spell import add_spell

    return add_spell()


@main.command(name="edit")
def __edit():
    """Open spellbook in editor"""
    from magic.edit_spellbook import edit_spellbook

    return edit_spellbook()
