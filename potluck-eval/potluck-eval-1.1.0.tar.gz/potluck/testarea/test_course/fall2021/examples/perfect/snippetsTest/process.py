"""
Data processing.

process.py

Peter Mawhorter 2021-8-19
"""

DATA = [
    {
        "name": "A",
        "order": 3
    },
    {
        "name": "B",
        "order": 2
    },
    {
        "name": "C",
        "order": 3
    },
    {
        "name": "D",
        "order": 1
    },
    {
        "name": "E",
        "order": 4
    }
]


def processData(data, number):
    """
    Returns the names of a limited number of items in order of their
    "order" values with ties broken by name alphabetically.
    """
    ordered = sorted(
        data,
        key=lambda it: (it["order"], it["name"])
    )
    return list(map(lambda item: item["name"], ordered))[:number]


ab = input("A or B? ")
if ab == "A":
    print(', '.join(processData(DATA, 1)))
else:
    print(', '.join(processData(DATA, 2)))

ab = input("A or B? ")
if ab == "A":
    print(', '.join(processData(DATA, 2)))
else:
    print(', '.join(processData(DATA, 3)))
