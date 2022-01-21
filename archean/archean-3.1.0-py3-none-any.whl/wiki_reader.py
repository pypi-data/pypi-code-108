import mwparserfromhell
import xml.sax
import os
import gc
import re
import json
from rich.progress import Progress, TaskID
from bz2 import BZ2File
from .cleanup import (
    MonetaryCleanup,
    TimeCleanup,
    normalize_date,
    normalize_str,
    str_to_list,
    extract_template_money,
)
from rich import print

money_cleaner = MonetaryCleanup()
time_cleanup = TimeCleanup()


def process_article(title, text, timestamp, template="Infobox film"):
    """Process a wikipedia article looking for template"""

    # Create a parsing object
    wikicode = mwparserfromhell.parse(text)

    # Search through templates for the template
    matches = wikicode.filter_templates(matches=template)

    # Filter out errant matches
    matches = [
        x for x in matches if x.name.strip_code().strip().lower() == template.lower()
    ]

    if len(matches) >= 1:
        # template_name = matches[0].name.strip_code().strip()
        properties = {}
        # Extract information from infobox
        for param in matches[0].params:
            # based on
            exp_match = re.search(
                r"{{based on.*" "(.*)" ".*}}", str(param.value), flags=re.I
            )
            if exp_match:
                source_name, creator_name, val = None, None, None
                based_on_phrases = re.search(
                    r"''(.*?)''.*(?=\|)\|(.*)}}", str(param.value), flags=re.I
                )
                if based_on_phrases:
                    source_name = based_on_phrases.group(1)
                    creator_name = based_on_phrases.group(2).split("|")
                    source_name = normalize_str(source_name)
                    names = []
                    for name in creator_name:
                        names.append(normalize_str(name))

                if source_name and names:
                    val = "{0} by {1}".format(source_name, ", ".join(names))

                properties[param.name.strip_code().strip()] = val or ""

            # Releases
            exp_match = re.search(
                r"{{film date\s?\|(df=.*?\|)?(.*?)}}",
                normalize_str(str(param.value)),
                flags=re.I,
            )
            if exp_match:
                film_date = exp_match.group(2)
                date = ""
                releases = re.findall(r"\d{4}\|\d{1,2}\|\d{1,2}", film_date)
                properties[param.name.strip_code().strip()] = []
                y, m, d, loc = "", "", "", ""
                if len(releases) > 1:
                    # regex to match 2002|09|12|
                    # [[Toronto International Film Festival|Toronto]]
                    # |2002|09|12|Toronto International Film Festival|Toronto
                    release_dates = re.findall(
                        r"(\d{4})\|(\d{1,2})\|(\d{1,2})", film_date
                    )
                    locs = re.findall(r"(?<!\d)[a-zA-Z\s\\|<>\/&]+(?!\d)", film_date)

                    for release_date, loc in list(zip(release_dates, locs)):
                        date = normalize_date(release_date)
                        properties[param.name.strip_code().strip()].append(
                            {"date": date, "location": normalize_str(loc)}
                        )

                else:
                    try:
                        release_date = re.findall(
                            r"(\d{4})\|(\d{1,2})\|(\d{1,2})|(\d{4})", film_date
                        )[0]
                    except Exception:
                        print("[bold red] An error occured")
                        continue
                    loc = re.findall(r"(?<!\d)[a-zA-Z\s\\|<>\/&]+(?!\d)", film_date)
                    if len([k for k in release_date if k]) == 1:
                        y = release_date[3]
                        if len(loc) == 0:
                            loc = ""
                    elif len(release_date) > 3:
                        y, m, d, loc = release_date
                    else:
                        y, m, d = release_date

                    if len(m) == 1:
                        m = "0" + m
                    if len(d) == 1:
                        d = "0" + d
                    date = "{0}/{1}/{2}".format(y, m, d)
                    if date.endswith("//"):
                        date = date[:-2]
                    properties[param.name.strip_code().strip()].append(
                        {"date": date, "location": normalize_str(loc)}
                    )

            # Screenplay/Story/Dialogue

            exp_match = re.findall(
                r"([\w\s\]]+?)\((?=screenplay|story|dialogue)(\w+)\)",
                str(param.value),
                flags=re.I,
            )
            exp_match_2 = re.search(
                r"Screenplay:\s,\s+([\w\s]+)|Dialogues?:\s,\s+([\w\s]+)",
                str(param.value),
                flags=re.I,
            )
            if exp_match or exp_match_2:
                # has story or screenplay  or dialogue in the value
                exp_match = re.findall(
                    r"([\w\s\]]+?)\((?=screenplay|story|dialogue)(\w+)\)",
                    str(param.value),
                    flags=re.I,
                )
                if len(exp_match) > 0:
                    for match in exp_match:
                        person, label = match
                        properties[normalize_str(label)] = normalize_str(person)

                else:
                    exp_match = re.search(
                        r"Screenplay:\s,\s+([\w\s]+)|Dialogues?:\s,\s+([\w\s]+)",
                        str(param.value),
                        flags=re.I,
                    )
                    if exp_match:
                        screenplay = exp_match.group(1)
                        dialogue = exp_match.group(2)
                        if screenplay:
                            properties["screenplay"] = normalize_str(screenplay)
                        if dialogue:
                            properties["dialogue"] = normalize_str(dialogue)

            # Gross collection / Budget

            key = normalize_str(param.name.strip_code().strip())
            if key == "gross" or key == "budget":
                try:
                    value = extract_template_money(param.value)
                    value = value.replace(",", "")
                    # if "-" in value:
                    #     print(f'name: {properties["name"]} , original: {value}')
                    value = money_cleaner.remove_equivalent_amt(value)
                    value = money_cleaner.large_num_names(value)
                    value = money_cleaner.extract_series_collection(value)
                    value = money_cleaner.extract_estimated_amount(value)
                    value = money_cleaner.money(value)

                    properties[key] = normalize_str(value)
                except Exception as e:
                    print(f"[bold red] {e}")

            elif key == "runtime":
                try:
                    value: str = param.value.strip_code().strip()
                    value = normalize_str(value)
                    runtime_in_minutes = time_cleanup.to_numeric(value)
                    properties[key] = runtime_in_minutes
                except Exception as e:
                    print(f"[bold red] {e}")

            # default config
            else:
                if param.value.strip_code().strip():
                    value: str = param.value.strip_code().strip()
                    value = normalize_str(value)
                    key = normalize_str(param.name.strip_code().strip())
                    if "." in key:
                        key = key.replace(".", "")
                    if "," in value and (
                        key != "name" or key != "gross" or key != "budget"
                    ):
                        properties[key] = str_to_list(value)

                    else:
                        properties[key] = value
        # Infobox params sometimes dont contain 'name'
        if not properties.get("name", None):
            properties["name"] = title
        return {title: properties}


class WikiXmlHandler(xml.sax.handler.ContentHandler):
    """Parse through XML data using SAX"""

    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
        self._buffer = None
        self._values = {}
        self._current_tag = None
        self._films = {}
        self._article_count = 0
        self._non_matches = []

    def characters(self, content):
        """Characters between opening and closing tags"""
        if self._current_tag:
            self._buffer.append(content)

    def startElement(self, name, attrs):
        """Opening tag of element"""
        if name in ("title", "text", "timestamp"):
            self._current_tag = name
            self._buffer = []

    def endElement(self, name):
        """Closing tag of element"""
        if name == self._current_tag:
            self._values[name] = " ".join(self._buffer)

        if name == "page":
            self._article_count += 1
            # Search through the page to see if the page is a book
            film = process_article(**self._values, template="Infobox film")
            # Append to the list of books
            if film:
                self._films.update(film)


processed = 0


def find_films(
    data_path, extraction_dir, task_id: TaskID, progress: Progress, save=True
):
    """Find all the film articles from a compressed wikipedia XML dump.
    If save, films are saved to partition directory based on file name"""

    # Object for handling xml
    handler = WikiXmlHandler()
    global processed

    # Parsing object
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)

    # Iterate through compressed file
    # print(f"Working with {data_path}")
    try:
        # Split operations for brevity
        # Works exactly the same
        with BZ2File(data_path) as file:
            progress.start_task(task_id)
            line = file.readline()
            while line != b"":
                parser.feed(line)
                line = file.readline()
                progress.update(task_id=task_id, advance=len(line))

        if save:
            processed += 1
            # Create file name based on partition name
            JSON_filename = os.path.splitext(os.path.basename(data_path))[0]
            output_file = os.path.join(extraction_dir, f"{JSON_filename}.json")

            # Create extraction directory if not exist
            if not os.path.isdir(extraction_dir):
                os.mkdir(extraction_dir)
            # Open the file
            with open(output_file, "w") as fout:
                # Write as json
                fout.write(json.dumps(handler._films) + "\n")

    except StopIteration:
        return
    except xml.sax.SAXParseException:
        print(
            f"[bold red] Encountered Parse exception in {os.path.basename(data_path)}"
        )
        return
    except Exception as e:
        print("[bold red] An error occured")
        print(f"[bold red] {e}")

    print(f"[blue]Found {len(handler._films.keys())} items in {JSON_filename}.bz2")
    # Memory management
    del handler
    del parser
    gc.collect()
    return None
