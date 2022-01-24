import re
import typing
from textwrap import dedent

from momotor.bundles import RecipeBundle, ConfigBundle, BundleFormatError
from momotor.options.option import OptionDefinition, OptionNameDomain
from momotor.options.parser.placeholders import replace_placeholders
from momotor.options.providers import Providers
from momotor.options.task_id import task_number_from_id, StepTaskId
from momotor.options.types import StepTasksType
from ._domain import DOMAIN

TASKS_OPTION_NAME = OptionNameDomain('tasks', DOMAIN)
tasks_option = OptionDefinition(
    name=TASKS_OPTION_NAME,
    type='str',
    doc=dedent("""\
        Enable multiple tasks for this step. If not provided, a single task is generated for this step.

        This option can directly define the number of tasks, but the actual number of tasks can also be defined
        in the top-level options of the recipe or the options of the configuration bundle.

        The following table describes the various values that are valid for this option:

        ============ ============================
        Tasks option Recipe/config option allowed
        ============ ============================
        ``*``        Any dimensions allowed (e.g. ``2``, ``2.2`` etc)
        ``?``        A single dimension required (e.g. ``1``, ``2``)
        ``?.?``      Two dimensions required (e.g. ``1.1``, ``2.2``)
        ``?.?.?``    Three dimensions required (e.g. ``1.2.3``, ``2.2.2``)
        ``?.*``      At least two dimensions required (e.g. ``1.2``, ``1.2.3``)
        ``4.?``      Exactly two dimensions required, and the first must be ``4`` (e.g. ``4.1``, ``4.2``)
        ``4.*``      At least two dimensions required, and the first must be ``4`` (e.g. ``4.1``, ``4.2.3``)
        ``4.4``      A fixed dimension. Config option not required, but if provided, MUST equal ``4.4``
        ============ ============================

        There is no limit to the number of dimensions allowed.
    """),
    location=('config', 'recipe', 'step')
)


def get_scheduler_tasks_option(recipe: RecipeBundle, config: typing.Optional[ConfigBundle], step_id: str) \
        -> typing.Optional[StepTasksType]:
    """ Get the 'tasks' option for a single step

    This gets the value of the 'tasks' option in the 'scheduler' domain from the step, recipe or config.

    A step supporting sub-tasks must define the option in the recipe. The option definition in the recipe declares
    what is supported. The format for the definition is as follows:

    ============ ============================
    Tasks option Recipe/config option allowed
    ============ ============================
    ``*``        Any dimensions allowed (e.g. ``2``, ``2.2`` etc)
    ``?``        A single dimension required (e.g. ``1``, ``2``)
    ``?.?``      Two dimensions required (e.g. ``1.1``, ``2.2``)
    ``?.?.?``    Three dimensions required (e.g. ``1.2.3``, ``2.2.2``)
    ``?.*``      At least two dimensions required (e.g. ``1.2``, ``1.2.3``)
    ``4.?``      Exactly two dimensions required, and the first must be ``4`` (e.g. ``4.1``, ``4.2``)
    ``4.*``      At least two dimensions required, and the first must be ``4`` (e.g. ``4.1``, ``4.2.3``)
    ``4.4``      A fixed dimension. Config option not required, but if provided, MUST equal ``4.4``
    ============ ============================

    There is no limit to the number of dimensions allowed.

    Values in the config take priority over values in the recipe. If the option in the recipe contains dimension
    wildcards ``?`` or ``*``, the option in the config must fill in those values.

    :param recipe: the recipe bundle
    :param config: (optional) the config bundle
    :param step_id: the id of the step
    :return: the tasks option, parsed into a tuple of ints
    """
    value_def_providers = Providers(
        recipe=recipe,
        task_id=StepTaskId(step_id, None)
    )
    value_def = tasks_option.resolve(value_def_providers, False)
    value_def = replace_placeholders(value_def, value_def_providers)

    value_providers = Providers(
        recipe=recipe,
        config=config
    )
    value = tasks_option.resolve(
        value_providers, {
            'recipe': step_id,
            'config': step_id
        }
    )
    value = replace_placeholders(value, value_providers)

    if value_def is None:
        if value is None:
            return None
        else:
            raise BundleFormatError(f"Step {step_id!r}: {TASKS_OPTION_NAME} option not supported")

    if not TASKS_DEF_RE.match(value_def):
        raise BundleFormatError(f"Step {step_id!r}: invalid {TASKS_OPTION_NAME} option"
                                f" definition {value_def!r}")

    value_def_parts = value_def.split('.')
    if value_def_parts[-1] == '*':
        wildcard = True
        value_def_parts.pop()
    else:
        wildcard = False

    if not wildcard and '?' not in value_def_parts:
        # Fixed dimension -- value is optional but must be equal to value_def if provided
        if value and value != value_def:
            raise BundleFormatError(f"Step {step_id!r}: {TASKS_OPTION_NAME} option value {value!r} "
                                    f"does not match definition {value_def!r}")

        return task_number_from_id(value_def)

    elif not value:
        # Missing value option
        raise BundleFormatError(f"Step {step_id!r}: missing required {TASKS_OPTION_NAME} option")

    else:
        step_tasks = []
        try:
            for pos, part in enumerate(value.split('.')):
                try:
                    part_def = value_def_parts[pos]
                except IndexError:
                    if not wildcard:
                        raise ValueError
                    part_def = '?'

                if part_def not in {'?', part}:
                    raise ValueError

                step_tasks.append(int(part))

        except ValueError:
            raise BundleFormatError(f"Step {step_id!r}: {TASKS_OPTION_NAME} option value {value!r} "
                                    f"does not match definition {value_def!r}")

        return tuple(step_tasks)


TASKS_DEF_RE = re.compile(r'^((([1-9]\d*)|[?])\.)*(([1-9]\d*)|[?*])$')
