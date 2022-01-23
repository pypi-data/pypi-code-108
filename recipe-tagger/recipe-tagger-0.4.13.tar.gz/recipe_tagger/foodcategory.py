"""
Module containg all the necessary class for the package.
FoodCategory is a Enum class representing the category of ingredient.
CategorySynset is a class representing the wordnet synset of a category.
"""

from enum import Enum

from nltk.corpus import wordnet


class FoodCategory(Enum):
    """
    Enum class used to represent the category of ingredients.
    """

    vegetable = 0
    fruit = 1
    legume = 2
    meat = 3
    egg = 4
    dairy = 5
    staple = 6
    condiment = 7
    nut = 8
    seafood = 9
    snack = 10
    mushroom = 11
    dessert = 12
    beverage = 13


class CategorySynset:
    """
    Class used to represent the Wordnet Synset of catagories.

    Attributes
    ----------
    categories: list
        a list containing all synset of the above categories
    """

    categories = [
        wordnet.synset(f"{FoodCategory.vegetable.name}.n.01"),
        wordnet.synset(f"{FoodCategory.fruit.name}.n.01"),
        wordnet.synset(f"{FoodCategory.legume.name}.n.01"),
        wordnet.synset(f"{FoodCategory.meat.name}.n.01"),
        wordnet.synset(f"{FoodCategory.egg.name}.n.01"),
        wordnet.synset(f"{FoodCategory.dairy.name}.n.01"),
        wordnet.synset(f"{FoodCategory.staple.name}.n.01"),
        wordnet.synset(f"{FoodCategory.condiment.name}.n.01"),
        wordnet.synset(f"{FoodCategory.nut.name}.n.01"),
        wordnet.synset(f"{FoodCategory.seafood.name}.n.01"),
        wordnet.synset(f"{FoodCategory.snack.name}.n.01"),
        wordnet.synset(f"{FoodCategory.mushroom.name}.n.01"),
        wordnet.synset(f"{FoodCategory.dessert.name}.n.01"),
        wordnet.synset(f"{FoodCategory.beverage.name}.n.01"),
    ]


class FoodCategoryWaterFootprint(Enum):
    """
    Enum class used to represent the default water footprint
    of category of ingredients.
    """

    vegetable = 354
    fruit = 962
    legume = 4055
    meat = 8623
    egg = 3265
    dairy = 3178
    staple = 1644
    condiment = 2364
    nut = 9063
    seafood = 2590
    snack = 2980
    mushroom = 322
    dessert = 3140
    beverage = 732
