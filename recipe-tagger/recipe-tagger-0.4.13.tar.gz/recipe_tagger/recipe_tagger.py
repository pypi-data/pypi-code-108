"""
Module containg all the main methods of the package. 
"""


import re
from collections import Counter

import wikipediaapi
from nltk.corpus import wordnet
from PyDictionary import PyDictionary
from pyfood.utils import Shelf
from textblob import Word

from recipe_tagger import util

from .foodcategory import CategorySynset, FoodCategory
from .util import get_embedding, process_ingredients

food_embedding_paths = {
    "en": "data/ingredient_embedding_en.npy",
    "it": "data/ingredient_embedding_it.npy",
}


def is_ingredient_vegan(ingredient):
    """
    Check if the provided ingredient is vegan or not.

    :param ingredient: the name of the ingredient.
    :return: a bool indicating whether the ingredient is vegan or not.
    """
    ingredient = ingredient.strip()
    shelf = Shelf("Milan", month_id=0)
    results = shelf.process_ingredients([ingredient])
    return results["labels"]["vegan"]


def is_recipe_vegan(ingredients):
    """
    Check if the provided ingredients contained in a recipe ar vegan or not.
    If only one element is not vegan the recipe is not vegan.

    :param ingredients: the list of the ingredients.
    :return: a bool indicating wheter the recipe is vegan or not.
    """
    shelf = Shelf("Milan", month_id=0)
    results = shelf.process_ingredients(ingredients)
    return results["labels"]["vegan"]


def add_ingredient(ingredient, tag, language="en"):
    """
    Map the provided ingredient and the tag into the embedding dataset.
    Tag must be one the following FoodCategory:
    vegetable, fruit, meat, legume, diary, egg, staple,
    condiment, nut, seafood, dessert.

    :param ingredient: the name of the ingredient.
    :param tag: the class of the ingredient. Must be one of the listed above.
    :param language: the language of the ingredient.
    :return: a bool indicating if the operation has succeded or not.
    """
    embedding = get_embedding(food_embedding_paths[language])
    ingredient = ingredient.strip()
    tag = tag.strip()
    if ingredient in embedding:
        return False

    embedding[ingredient] = FoodCategory[tag].value
    return True


def search_ingredient_hypernyms(ingredient):
    """
    Predict the class of the provided ingredient based on the Wu & Palmer’s
    similarity between ingredient, his hypernyms and the 11 FoodCategory.
    The FoodCategory is choosen based on the maximum similarity value between
    the ingredient, its hypernym and the various categories. If the predicted
    category is different between ingredient and hypernym the category is
    choosen based on the avarege of both.

    :param ingredient: the name of the ingredient.
    :return: the class of the ingredient.
    """
    if " " in ingredient:
        ingredient = ingredient.split(" ")[-1]

    synsets = wordnet.synsets(ingredient)
    if not synsets:
        return

    ingredient = synsets[0]
    hypernym = ingredient.hypernyms()[0] if ingredient.hypernyms() else None
    categories = CategorySynset.categories

    sim = []
    hypernym_sim = []
    for cat in categories:
        sim.append(ingredient.wup_similarity(cat))
        if hypernym:
            hypernym_sim.append(hypernym.wup_similarity(cat))

    best_sim = sim.index(max(sim))
    best_hyp = hypernym_sim.index(max(hypernym_sim)) if hypernym else None

    if not hypernym or best_sim == best_hyp:
        return FoodCategory(best_sim).name
    else:
        sum = [(x + y) / 2 for x, y in zip(sim, hypernym_sim)]
        return FoodCategory(sum.index(max(sum))).name


def search_ingredient_class(ingredient, online_search=True, language="en"):
    """
    Search on wikipedia and english dictionary the class of
    the provided ingredient.
    Returns the most occurrences of a single FoodCategory class based on
    the two research.

    :param ingredient: the name of the ingredient.
    :param ingredient: allows to disable wikipedia search.
    :return: the class of the ingredient.
    """
    if " " in ingredient:
        ingredient = ingredient.split(" ")[-1]

    categories = []
    dictionary = PyDictionary()
    wiki = wikipediaapi.Wikipedia(language) if online_search else None

    try:
        page = wiki.page(ingredient) if online_search else None
        meaning = (
            dictionary.meaning(ingredient, disable_errors=True)["Noun"]
            if dictionary.meaning(ingredient, disable_errors=True)
            else None
        )
        ontology = ", ".join(meaning) if meaning else ""

        for category in FoodCategory:
            if page and re.search(r"\b({0})\b".format(category.name), page.summary):
                categories.append(category.name)
            if ontology and re.search(r"\b({0})\b".format(category.name), ontology):
                categories.append(category.name)
    except:
        pass
    return max(categories, key=categories.count) if categories else None


def get_ingredient_class(ingredient, online_search=True, language="en"):
    """
    Predict the class of the provided ingredient based on the embeddings.
    If the ingredient cannot be found in the dictionary it will be
    searched on wikipedia pages or hypernyms.

    :param ingredient: the name of the ingredient.
    :praram online_search: allows to disable wikipedia search
    :param language: the language of the ingredient.
    :return: the class of the ingredient.
    """
    embedding = get_embedding(food_embedding_paths[language])
    cleaned_ing = process_ingredients(ingredient, language=language)
    if cleaned_ing in embedding:
        return FoodCategory(embedding[cleaned_ing]).name
    elif " " in cleaned_ing:
        ings = [ing for ing in cleaned_ing.split()]
        classes = [
            get_ingredient_class(ing, online_search=online_search, language=language)
            for ing in ings
        ]
        classes = [cl for cl in classes if cl]
        return classes[0] if classes else None
    else:
        web_class = search_ingredient_class(
            ingredient, online_search=online_search, language=language
        )
        web_class = web_class if web_class else search_ingredient_hypernyms(cleaned_ing)
        return web_class


def get_recipe_class_percentage(ingredients, online_search=True, language="en"):
    """
    Classify a recipe in tags based on its ingredient.
    Returns the percentages of ingredient class in the recipe provided.

    :param ingredients: list of ingredients in the recipe.
    :param online_search: allows to disable wikipedia search
    :return: list of tuples containg classes and percentages.
    """
    tags = [
        get_ingredient_class(ingredient, online_search=online_search, language=language)
        for ingredient in ingredients
    ]
    c = Counter(tags)
    return [(i, str(round(c[i] / len(tags) * 100.0, 2)) + "%") for i in c]


def get_recipe_tags(ingredients, online_search=True, language="en"):
    """
    Classify a recipe in tags based on its ingredient.
    Tag could be: Vegetable, Fruit, Meat, Legume, Diary,
    Egg, Staple, Condiment, Nut, Seafood

    :param ingredients: list of ingredients in the recipe.
    :param online_search: allows to disable wikipedia search
    :return: set of tags for the recipe.
    """
    tags = [
        get_ingredient_class(ingredient, online_search=online_search, language=language)
        for ingredient in ingredients
    ]
    if None in tags:
        tags.remove(None)
    if len(tags) >= 2 and FoodCategory.condiment.name in tags:
        tags.remove(FoodCategory.condiment.name)
    return list(set(tags)) if len(tags) else tags
