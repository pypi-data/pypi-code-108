"""List available Finesse element validators.

Originally used for #123.
"""

from list_elements import MODEL_ELEMENT_CHILDREN


def model_element_validators(klass):
    """Dict of parameter names to validator callables."""
    # Reverse param dict since it's defined in reverse.
    for pinfo in reversed(klass._param_dict[klass]):
        try:
            validator = klass._validators[klass][pinfo.name]
        except KeyError:
            validator = None

        yield name, validator


if __name__ == "__main__":
    for cls in sorted(
        MODEL_ELEMENT_CHILDREN, key=lambda cls: (cls.__module__, cls.__name__)
    ):
        print(f"### `{cls.__module__}.{cls.__name__}`")
        print()

        validators = dict(model_element_validators(cls))

        if validators:
            for parameter, validator in validators.items():
                status = f" --- **no validator**" if validator is None else ""
                print(f"* [ ] `{parameter}`{status}")
        else:
            print("*No model parameters.*")

        print()
