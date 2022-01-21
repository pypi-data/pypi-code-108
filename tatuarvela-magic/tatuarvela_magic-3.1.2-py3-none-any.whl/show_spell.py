import click

from magic.shared.spellbook import read_spell


def show_spell(magic_word, spell_args, skip_arguments_provided=False):
    spell = read_spell(magic_word)
    color = "cyan"

    if not spell:
        raise Exception(f"Spell not found for magic word '{magic_word}'")

    print(f'{click.style("Description:", fg=color)} {spell["description"]}')
    print(f'{click.style("Magic words:", fg=color)} {", ".join(spell["magicWords"])}')
    print(click.style("Commands:", fg=color))
    for command in spell["commands"]:
        print(f"  {command}")

    argument_count = spell.get("argumentCount")
    if argument_count is None:
        print(f'{click.style("Arguments required:", fg=color)} None')
    else:
        print(f'{click.style("Arguments required:", fg=color)} {argument_count}')

    if skip_arguments_provided:
        return

    print(f'{click.style("Arguments provided:", fg=color)} {len(spell_args)}')
    for idx, arg in enumerate(spell_args):
        print(f"  $a{idx}: {arg}")
