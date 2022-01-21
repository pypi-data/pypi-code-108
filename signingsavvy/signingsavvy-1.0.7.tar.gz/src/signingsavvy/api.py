"""Module using quart to construct a restful api for use with signingsavvy."""

import logging
import re

from logging import basicConfig

import requests

from bs4 import BeautifulSoup as soup
from quart import Quart
from quart import request
from requests import session


app = Quart(__name__)


def payload() -> dict:
    """Function that retrieves request payload for headers.

    Quart is used to pull the headers from a request into the Python requests session.

    Returns:
        dict: Payload for SigningSavvy membership authentication.

    """

    return {
        "username": request.headers.get("user"),
        "password": request.headers.get("pass"),
        "login": 1,
        "remember": 1,
        "search": "",
        "find": 1,
    }


with session() as c:
    base: str = "https://www.signingsavvy.com"

    # Set up logging config
    basicConfig(
        filename="signingsavvy.log",
        format="[%(asctime)s] {%(pathname)s:%(lineno)d} \
    %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
        encoding="utf-8",
        level=logging.INFO,
    )

    def getHTML(uri: str) -> soup:
        """Generalized function for getting html from a uri.

        Args:
            uri (str): Uri to request from.

        Returns:
            soup: The parsed HTML from the response text.

        """

        logging.info(f"Getting HTML from {uri}")
        r: requests.Response = c.get(uri)

        return soup(r.text, "html.parser")

    def IdFromUri(uri: str) -> str:
        """Function to pull id from uri.

        Args:
            uri (str): Uri to pull id from.

        Returns:
            str: the regex matched id.

        """

        logging.info(f"Getting id from {uri}")
        return re.findall(r"\d+(?=\/)(?<!\/)", uri)[0]

    def fetchTabText(html: soup, classCSS: str) -> str:
        """Function get the text from inside a tab element.

        Args:
            html (soup): HTML data to fetch from.
            classCSS (str): CSS class to query the html.

        Returns:
            str: text returned from the tab.

        """

        logging.info(f"Getting text from a tab using {classCSS}")
        query = html.select_one(f".{classCSS} + div>p")
        return query.text if query else ""

    def formatSignName(text: str) -> str:
        """Function to pull the name of a word from the full text.

        Args:
            text (str): Full text from sign description.

        Returns:
            str: Sign name.

        """

        return formatSignNameClarification(text, r"[\w\s]+(?!\()")

    def formatSignClarification(text: str) -> str:
        """Function to pull the clarification of a word from the full text.

        Args:
            text (str): Full text from sign description.

        Returns:
            str: Sign clarification.

        """

        return formatSignNameClarification(text, r"(?<=as in \").+(?=\")")

    def formatSignNameClarification(text: str, regexExpr: str) -> str:
        """Function to pull either the clarification or name of
            a word from the full text.

        Args:
            text (str): Full text from sign description.
            regexExpr (str): Regex expression to match either a sign name or its clarification.

        Returns:
            str: Sign name or its clarification.

        """

        logging.info(f"Formatting {text}")
        regex: list(str) = re.findall(regexExpr, text)

        return "" if regex == [] else regex[0]

    def formatSignVideo(href: str) -> str:
        """Function to pull a fragment of the uri for a sign's video.

        Args:
            href (str): Href for a sign's video.

        Returns:
            str: Uri fragment of a sign's video.

        """

        logging.info(f"Formatting {href}")
        return re.findall(r"\d+\/\d+.mp4", href)[0]

    def fetchSignSynonyms(html: soup) -> list:
        """Function to pull synonyms for a sign.

        Args:
            html (soup): HTML data to fetch from.

        Returns:
            list: List containing synonyms of the given sign.

        """

        logging.info("Grabbing synonyms from current sign")
        synonyms = []

        for _ in html.select(".fa-tags + div>ul>li>a"):
            synonyms.append(
                {
                    "id": IdFromUri(_["href"]),
                    "name": formatSignName(_.text).title(),
                    "clarification": formatSignClarification(_.text),
                }
            )

        return synonyms

    def fetchSignUsage(html: soup) -> list:
        """Function to pull one or more usages from a sign.

        Args:
            html (soup): HTML data to fetch from.

        Returns:
            list: A list of responses containing English and ASL entries.

        """

        logging.info("Grabbing usage from current sign")
        text = html.select(".fa-film + div>div>p")

        if text == []:
            query = html.select_one(".fa-film + div>p")
            return query.text if query else ""

        english = []
        asl = []
        for i in range(len(text)):
            if i % 2 != 0:
                # regex substitution to remove tilted single quotes
                asl.append(re.sub("(\u2018|\u2019)", "'", text[i].text))
            else:
                # regex substitution to remove tilted single quotes
                english.append(re.sub("(\u2018|\u2019)", "'", text[i].text))

        return list(map(lambda e, a: {"english": e, "asl": a}, english, asl))

    def fetchSignVariants(html: soup, sign: str, _id: str) -> list:
        """Function to pull the variants of a sign.

        Args:
            html (soup): HTML data to fetch from.
            sign (str): The name of the sign.
            _id (str): The id of the sign.

        Returns:
            list: A list of responses containing variants for the given sign.

        """

        logging.info(f"Grabbing variants from {sign}/{_id}")
        variants = []

        variantLen = len(html.select(".fa-cubes + div>ul>li"))

        for i in range(variantLen):
            html = getHTML(f"{base}/sign/{sign}/{_id}/{i + 1}")
            _type = fetchTabText(html, "fa-hand-paper-o")
            desc = fetchTabText(html, "fa-info-circle")
            aid = fetchTabText(html, "icon-eyeglasses")
            usage = fetchSignUsage(html)
            video = formatSignVideo(html.select_one("video>source")["src"])

            variants.append(
                {
                    "type": _type,
                    "desc": desc,
                    "aid": aid,
                    "usage": usage,
                    "video": video,
                }
            )

        return variants

    def fetchGlossary(html: soup) -> list:
        """Function to pull the list of words that make up a sentence.

        Args:
            html (soup): HTML data to fetch from.

        Returns:
            list: List of responses containing the glossary for a sign.

        """

        logging.info("Grabbing glossary from current sign")
        glossary = []

        for sign in html.select(".fa-hand-paper-o + div>p>a"):
            glossary.append({"id": IdFromUri(sign["href"]), "name": sign.text})

        return glossary

    @app.route("/sentences/<category>/<sentence>")
    def fetchSentence(category: str, sentence: str) -> dict:
        """Function to pull a specific sentence.

        Note:
            @app.route("/sentence/<category>/<sentence>")

        Args:
            category (str): The category for the sentence.
            sentence (str): The sentence.

        Returns:
            dict: A response that contains information for the sentence.

        """

        logging.info(f"Grabbing sentence from {category}{sentence}")
        c.post(base, data=payload())

        html = getHTML(f"{base}/sentences/{category}/{sentence}")
        if not html.select_one(".wordlist-bar > a"):
            return {
                "value": "ASL Sentences are available only to full members."
            }

        category = html.select_one(".wordlist-bar > a")

        return {
            "id": sentence,
            "english": fetchTabText(html, "fa-pencil"),
            "asl": fetchTabText(html, "fa-hand-paper-o"),
            "category": category.text if category else "",
            "glossary": fetchGlossary(html),
            "video": formatSignVideo(html.select_one("video>source")["src"]),
        }

    @app.route("/sign/<sign>/<_id>")
    def fetchSign(sign: str, _id: str) -> dict:
        """Function to pull information for a given sign.

        Note:
            @app.route("/sign/<sign>/<_id>")

        Args:
            sign (str): The name of the sign.
            _id (str): The id of the sign.

        Returns:
            dict: A response that contains information for the sign.

        """

        logging.info(f"Grabbing sign from {sign}/{_id}")
        c.post(base, data=payload())

        html = getHTML(f"{base}/sign/{sign}/{_id}/1")

        response = {
            "id": _id,
            "name": sign.title(),
            "clarification": formatSignClarification(
                fetchTabText(html, "fa-pencil")
            ),
            "synonyms": fetchSignSynonyms(html),
            "variants": fetchSignVariants(html, sign, _id),
        }

        return response

    @app.route("/browse/<letter>")
    def browse(letter: str) -> dict:
        """Function to pull a list of signs by alphabetical letter.

        Note:
            @app.route("/browse/<letter>")

        Args:
            letter (str): The letter to pull signs for.

        Returns:
            dict: Response containing a list of signs from a given letter.

        """

        logging.info(f"Grabbing list of signs that start with {letter}")
        c.post(base, data=payload())

        html = getHTML(f"{base}/browse/{letter}")
        return {"signs": seekSign(html)}

    @app.route("/search/<sign>")
    def search(sign: str) -> dict:
        """Function to pull one or more signs through a search result.

        Note:
            @app.route("/search/<sign>")

        If only one sign is found, the information is returned directly.
        If more signs are found, a list of results are returned.

        Args:
            sign (str): The word/term to search for.

        Returns:
            dict: Response containing a response of matching signs or a response containing information from the sign in the event that only a single sign is found.

        """

        logging.info(f"Grabbing signs that match {sign}")
        c.post(base, data=payload())

        html = getHTML(f"{base}/sign/{sign}")
        return seekSign(html, sign)

    def seekSign(html: soup, sign: str = None) -> dict:
        """Function to search for signs.

        Args:
            html (soup): HTML data to fetch from.
            sign (str): The name of the sign.

        Returns:
            dict: Response containing a response of matching signs or a response containing information from the sign in the event that only a single sign is found.

        """

        logging.info("Looking for matching sign")
        signs = map(
            lambda tag: {
                "uri": re.sub(
                    r"\/\d$",
                    "",
                    tag.select_one("a")["href"].replace("sign/", ""),
                ),
                "word": re.sub(
                    r"\/\d$",
                    "",
                    tag.text.replace("&quot", "'").replace('"', "'"),
                ),
            },
            html.select(".search_results>ul>li"),
        )

        if len(html.select(".search_results")) == 0 and sign:
            logging.info("Found a single matching sign. Returning info")
            signId = html.select_one(".comment-button-reply")["id"]
            fSignId = re.findall(r"\d+", signId)[0]

            return fetchSign(sign, fSignId)

        else:
            logging.info("Found multiple matches and returning results")
            results = {"search_results": list(signs)}

            return results

    @app.route("/sentences")
    def sentenceCategories() -> dict:
        """Function to gather SigningSavvy categories for sentences

        Note:
            @app.route("/sentences")

        Returns:
            dict: Response containing all SigningSavvy categories.

        """

        logging.info("Pulling available sentence categories")
        c.post(base, data=payload())

        html = getHTML(f"{base}/sentences")
        categories = html.select(".phrase_list")[1].select("ul>li")
        return {"categories": list(map(lambda tag: tag.text, categories))}

    @app.route("/sentences/<category>")
    def sentenceCategoryEntries(category: str) -> dict:
        """Function to gather sentences from a category

        Note:
            @app.route("/sentences/<category>")

        Args:
            category (str): The desired category for a given sentence.

        Returns:
            dict: Response containing the given sentence as well as its uri.

        """

        logging.info("Pulling entries from sentence category")
        c.post(base, data=payload())

        html = getHTML(f"{base}/sentences/{category}")
        entries = html.select(".content_module>p>a")

        return {
            "categories": list(
                map(
                    lambda tag: {
                        "uri": tag["href"].replace("sentences/", ""),
                        "sentence": re.sub(
                            r"([\.?!,](?=\w))", r"\1 ", tag.text
                        ),
                    },
                    entries,
                )
            )
        }
