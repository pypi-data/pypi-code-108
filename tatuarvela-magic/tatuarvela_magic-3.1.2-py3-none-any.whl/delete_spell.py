from magic.shared.display import EMOJI_TRASH
from magic.shared.prompt import yes_or_no_prompt
from magic.shared.spellbook import delete_spell as _delete_spell
from magic.show_spell import show_spell


def delete_spell(magic_word):
    print(f"{EMOJI_TRASH} Deleting spell '{magic_word}'\n")

    show_spell(magic_word, spell_args=[], skip_arguments_provided=True)
    print("")

    confirm = yes_or_no_prompt(
        "This action cannot be undone. Are you sure you want to delete this spell, yes or NO?",
        default="no",
        color="red",
    )

    if confirm:
        _delete_spell(magic_word)
