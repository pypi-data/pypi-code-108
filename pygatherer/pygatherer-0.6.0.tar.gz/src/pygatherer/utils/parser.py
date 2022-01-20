from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from pathurl import URL, Query

from pygatherer.utils.constants import CARD_DETAILS_URL, CARD_URL, SUPERTYPES


@dataclass
class Cost:
    type: str
    value: Any = None
    colors: List[str] = None


@dataclass
class Card:
    name: str
    cost: List[Cost]
    color_indicator: List[str]
    subtypes: List[str]
    types: List[str]
    supertypes: List[str]
    expansion: str
    image_url: URL
    power: str
    loyalty: str
    toughness: str
    variation: str
    rules: List[str]
    multiverse_id: int


def parse_cost_image(cost_img: Tag) -> Cost:
    alt = cost_img["alt"]
    try:
        cost = int(alt)
    except ValueError:
        pass
    else:
        return Cost(type="Colorless", value=cost)

    if alt.startswith("Phyrexian"):
        _, color = alt.split()
        return Cost(type="Phyrexian", colors=[color])

    if " or " in alt:
        first, second = alt.split(" or ")
        if first == "Two":
            return Cost(type="Monocolored Hybrid", colors=[second])
        return Cost(type="Hybrid", colors=[first, second])

    return Cost(type="Colored", colors=[alt])


def parse_types(type_info: str) -> Tuple[List[str], List[str], List[str]]:
    main_types, *subtypes = type_info.split("—")
    supertypes = []
    types = []
    for main_type in main_types.split():
        main_type.strip()
        if main_type in SUPERTYPES:
            supertypes.append(main_type)
        else:
            types.append(main_type)

    if subtypes:
        subtype_info = subtypes[0]
        if "Plane" in types:
            subtypes = [subtype_info.strip()]
        else:
            subtypes = [subtype.strip() for subtype in subtype_info.split()]

    return supertypes, types, subtypes


def parse_cost(cost: Tag) -> List[Cost]:
    return [parse_cost_image(cost_img) for cost_img in cost.select("img")]


def parse_rules(rules: Tag) -> List[str]:
    return [rule.text for rule in rules.select("div.cardtextbox")]


def parse_pt(pt: str) -> Tuple[str, str]:
    power, toughness = pt.split("/")
    return power.strip(), toughness.strip()


def get_id_from_image_url(image_url: URL) -> str:
    return image_url.query.get("multiverseid")[0]


def parse_left_col(left_col: Tag) -> Dict[str, Any]:
    img = left_col.img
    image_url = CARD_URL.join(img["src"])
    multiverse_id = get_id_from_image_url(image_url)
    variation = None
    variations = [
        variation
        for variation in left_col.select_one("div.variations").select("a")
        if variation["id"] == multiverse_id
    ]

    if variations:
        variation = int(variations[0].text)

    return {
        "image_url": image_url.string,
        "multiverse_id": int(multiverse_id),
        "variation": variation,
    }


def parse_right_col(right_col: Tag) -> Dict[str, Any]:
    rows = {
        row.select_one(".label").text.strip(): row.select_one(".value")
        for row in right_col.select("div.row")
    }
    supertypes, types, subtypes = parse_types(rows["Types:"].text.strip())
    cost = color_indicator = loyalty = rules = power = toughness = None

    if "Mana Cost:" in rows:
        cost = parse_cost(rows["Mana Cost:"])

    if "Color Indicator:" in rows:
        color_indicator = [
            indication.strip()
            for indication in rows["Color Indicator:"].text.split(",")
        ]

    if "Loyalty:" in rows:
        loyalty = rows["Loyalty:"].text.strip()

    if "Card Text:" in rows:
        rules = parse_rules(rows["Card Text:"])

    if "P/T:" in rows:
        power, toughness = parse_pt(rows["P/T:"].text.strip())

    return {
        "name": rows["Card Name:"].text.strip(),
        "expansion": rows["Expansion:"].select("a")[1].text.strip(),
        "supertypes": supertypes,
        "types": types,
        "subtypes": subtypes,
        "cost": cost,
        "color_indicator": color_indicator,
        "loyalty": loyalty,
        "rules": rules,
        "power": power,
        "toughness": toughness,
    }


def parse_gatherer_content(content: bytes, gatherer_url: URL) -> Card:
    soup = BeautifulSoup(content, "lxml")
    multiverse_id = int(get_id_from_image_url(gatherer_url))
    faces_table = soup.select_one("table.cardComponentTable")
    faces = faces_table.select("table.cardDetails")
    for face in faces:
        right_col = face.select_one("td.rightCol")
        left_col = face.select_one("td.leftCol")
        if left_col is None:
            left_col = face.select_one("td.plane")

        card_info = {**parse_left_col(left_col), **parse_right_col(right_col)}
        if card_info["multiverse_id"] == multiverse_id:
            return Card(**card_info)

    raise RuntimeError("No race is having the multiverse id.")


def get_card_by_id(multiverse_id: int) -> Card:
    gatherer_url = CARD_DETAILS_URL.replace(
        query=Query(f"multiverseid={multiverse_id}")
    )

    response = requests.get(gatherer_url.string, allow_redirects=False)
    if response.status_code >= 300:
        raise ValueError(f"No card with multiverse_id {multiverse_id} exists")
    return parse_gatherer_content(response.content, gatherer_url)
