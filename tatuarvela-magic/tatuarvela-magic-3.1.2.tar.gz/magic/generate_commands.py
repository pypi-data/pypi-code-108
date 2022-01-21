import click

from magic.cast_spell import cast_spell
from magic.delete_spell import delete_spell
from magic.shared.spellbook import read_spells
from magic.show_spell import show_spell


def generate_commands(group):
    for magic_word, spell in read_spells().items():
        description = click.style(spell.get("description"), fg='blue')
        group.command(
            name=magic_word,
            help=description,
            short_help=description,
            context_settings=dict(allow_extra_args=True, ignore_unknown_options=True),
        )(__create_command(magic_word))


def __create_command(magic_word):
    @click.pass_context
    @click.option("-d", "--delete", is_flag=True, help="Delete this spell.")
    @click.option("-s", "--show", is_flag=True, help="Show details of this spell.")
    def command(ctx, delete, show):
        if delete:
            return delete_spell(magic_word)
        if show:
            return show_spell(magic_word=magic_word, spell_args=ctx.args)
        return cast_spell(magic_word=magic_word, arguments=ctx.args)

    return command
