"""List available Finesse elements.

Originally used for #45.
"""

from finesse.element import ModelElement


def inheritors(klass):
    subclasses = set()
    work = [klass]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                work.append(child)
    return subclasses


MODEL_ELEMENT_CHILDREN = inheritors(ModelElement)


if __name__ == "__main__":
    for cls in sorted(
        MODEL_ELEMENT_CHILDREN, key=lambda cls: (cls.__module__, cls.__name__)
    ):
        print(f"* [ ] `{cls.__module__}.{cls.__name__}`")
