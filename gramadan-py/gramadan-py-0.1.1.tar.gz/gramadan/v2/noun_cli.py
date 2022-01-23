import sys
import os
from gramadan.noun import Noun
from gramadan.features import Gender, FormSg
from gramadan.v2.database import Database

from .noun import DeclensionInconsistentError, FormsMissingException, FormsAmbiguousException, NounDeclensionGuesser
from .noun_empirical import EmpiricalNounDeclensionGuesser
from .noun_nualeargais import NualeargaisNounDeclensionGuesser, NualeargaisFullNounDeclensionGuesser

if __name__ == "__main__":
    guesser: NounDeclensionGuesser
    if '--empirical' in sys.argv:
        guesser = EmpiricalNounDeclensionGuesser()
    elif '--nualeargais-full' in sys.argv:
        guesser = NualeargaisFullNounDeclensionGuesser()
    elif '--nualeargais' in sys.argv:
        guesser = NualeargaisNounDeclensionGuesser()
    else:
        guesser = NounDeclensionGuesser()

    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'output', 'data')

    dictionary = None
    print_result = False
    for n, arg in enumerate(sys.argv):
        if arg == '--word':
            lemma, gender, gen = sys.argv[n+1].split(',')
            noun = Noun(
                [FormSg(lemma, Gender(gender))],
                [FormSg(gen, Gender(gender))],
            )
            dictionary = {
                lemma: noun
            }
            print_result = True

    if not dictionary:
        database = Database(path)
        database.load()
        dictionary = database.dictionary.noun

    errors = []
    known = 0
    unknown = []
    for n, (lemma, noun) in enumerate(dictionary.items()):
        try:
            if noun.declension:
                known += 1
            dec = guesser.guess(noun)
            if noun.declension:
                if dec != noun.declension:
                    raise DeclensionInconsistentError(
                        f'Declension for {lemma}, expected {noun.declension}, got {dec}',
                        dec,
                        noun.declension
                    )
            else:
                noun.declension = dec
                if print_result and not dec:
                    unknown.append(noun)
        except FormsMissingException as e:
            if '--debug' in sys.argv:
                print('[', e, ']')
        except DeclensionInconsistentError as e:
            errors.append((noun, e))
            if '--debug' in sys.argv:
                print(e)

    if len(errors) < 20 or '--all' in sys.argv:
        import tabulate # type: ignore
        table = [
            {
                'Lemma': noun.getLemma(),
                'Gender': noun.getGender().value,
                'Genitive': noun.sgGen[0].value if len(noun.sgGen) else '',
                'Error': str(e)
            }
            for noun, e in errors
        ]
        print(tabulate.tabulate(table, headers='keys'))

    if print_result:
        import tabulate # type: ignore
        table = [
            {
                'Lemma': lemma,
                'Gender': noun.getGender().value,
                'Genitive': noun.sgGen[0].value if len(noun.sgGen) else '',
                'Declension': 'IRR.' if noun.declension == -1 else noun.declension
            }
            for lemma, noun in dictionary.items()
        ]
        print(tabulate.tabulate(table, headers='keys'))
        if unknown:
            print(f"{len(unknown)} could not be guessed: {', '.join([n.getLemma() for n in unknown])}")
    if known:
        print(f"Errors {len(errors)} in {known} known, {100 * (1 - len(errors) / known):.2f}% success")
