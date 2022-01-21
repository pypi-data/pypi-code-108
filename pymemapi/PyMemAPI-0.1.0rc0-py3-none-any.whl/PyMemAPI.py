import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Optional, Any, Dict, Tuple
from dataclasses import dataclass, field
from memrise import transUntilDone
from text2ipa import get_IPAs
from getpass import getpass
import requests
import json
import logging
import re
import tempfile
import sqlite3
from .schema import CourseList, LevelSchema, EditLevel, CourseSchema, LevelList
from .exception import (
    InvalidSeperateElement,
    LanguageError,
    LoginError,
    AddLevelError,
    AddBulkError,
    ConnectionError,
    JSONParseError,
    InputOutOfRange,
)
from .text2speech import (
    concat,
    external_generate_audio,
    generate_audio,
    choose_voices,
    generate_audio_except,
    CUSTOM,
)


# COURSE = "https://app.memrise.com/v1.17/courses/{course_id}/"
# LEVEL = "https://app.memrise.com/v1.17/courses/{course_id}/levels/"
# Constants
URL = "https://app.memrise.com"
UPLOAD_PATH = "/ajax/thing/cell/upload_file/"
DELETE_PATH = "/ajax/thing/column/delete_from/"

INSERT_STATEMENT = (
    """INSERT INTO "sentense" ("sentense", "meaning", "topic") VALUES (?, ?, ?);"""
)
SELECT_NULL_MEANING = """SELECT "sentense" FROM sentense WHERE meaning is NULL;"""
SELECT_NULL_IPA = """SELECT "sentense" FROM sentense WHERE ipa is NULL;"""
UPDATE_MEANING = """UPDATE sentense SET meaning = ? WHERE sentense = ? ;"""
UPDATE_IPA = """UPDATE sentense SET ipa = ? WHERE sentense = ? ;"""
TOPIC_LOCAL = """SELECT id, name FROM topic WHERE status = 'local';"""
TOPIC_STREAM = """SELECT id, name FROM topic WHERE status = 'stream';"""
SENS_IN_TOPIC = (
    """SELECT "sentense", "meaning", "ipa" FROM "sentense" WHERE topic_id = ? ;"""
)
UPDATE_STATUS = """UPDATE topic SET status = 'stream' WHERE id = ? ;"""


@dataclass
class Client:
    username: str = field(init=False)
    password: str = field(init=False)
    session: requests.Session = requests.Session()

    def login(self, username: Optional[str] = "", password: Optional[str] = "") -> bool:
        status: bool = False
        if username == "" or password == "":
            username = input("Enter username: ")
            password = getpass("Enter password: ")
        try:
            res = self.session.get(f"{URL}/login/", timeout=30)
        except requests.RequestException as e:
            raise LoginError(f"LoginError with message: {e}")

        payload = {
            "username": username,
            "password": password,
            "csrfmiddlewaretoken": res.cookies["csrftoken"],
        }

        try:
            response = self.session.post(
                f"{URL}/login/",
                data=payload,
                headers={"Referer": f"{URL}/login/"},
                timeout=30,
            )
        except requests.RequestException as e:
            print(e)
            exit()

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 403:
                raise LoginError(f"Authentication failed: {e}")
            else:
                raise LoginError(f"Unexpected response during login: {e}")
        else:
            status = True

        return status

    def courses(self):
        """Retrieve the courses to which the logged in user has edit permissions."""
        all_courses: List[Course] = []
        has_more_courses = True
        offset = 0
        while has_more_courses:
            data = self.get(
                "/ajax/courses/dashboard/",
                params={
                    "courses_filter": "teaching",
                    "get_review_count": "false",
                    "offset": offset,
                    "limit": 8,
                },
            )
            course_list = CourseList(**data)
            has_more_courses = course_list.has_more_courses
            offset += 9
            all_courses.extend(Course(self, schema) for schema in course_list.courses)
        return all_courses

    def get(self, path: str, params: Optional[Dict[str, Any]] = None):
        try:
            response = self.session.get(
                f"{URL}{path}",
                params=params,
                timeout=10,
            )
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Get request failed: {e}")

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            raise ConnectionError(f"Unexpected response for a GET request: {e}")

        try:
            data = response.json()
        except json.decoder.JSONDecodeError as e:
            raise JSONParseError(f"Invalid JSON response for a GET request: {e}")

        return data

    def post(
        self,
        path: str,
        payload: Dict[str, Any],
        headers: Dict[str, str],
        files: Optional[Dict[str, Tuple[str, bytes, str]]] = None,
    ) -> requests.Response:
        """Send POST request. Each POST request is NEED a CSRF TOKEN."""
        payload["csrfmiddlewaretoken"] = self.session.cookies["csrftoken"]
        try:
            response = self.session.post(
                f"{URL}{path}",
                files=files,
                headers=headers,
                data=payload,
                timeout=20,
            )
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"POST request failed': {e}")

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            print(response.content)
            raise ConnectionError(f"Unexpected response to a POST request': {e}")
            # pass

        return response


@dataclass
class Word:
    id: int
    text: str
    audio_col: int
    audio_count: int
    client: Client

    def upload_audio(self, audio: Any):
        if isinstance(audio, str):
            with open(audio, "rb") as fp:
                files = {"f": ("audio.mp3", fp.read(), "audio/mp3")}

            self.__upload_file(files)

        elif isinstance(audio, list):
            for file in audio:
                with open(file, "rb") as fp:
                    files = {"f": ("audio.mp3", fp.read(), "audio/mp3")}

                self.__upload_file(files)

        elif isinstance(audio, bytes):
            files = {"f": ("audio.mp3", audio, "audio/mp3")}

        else:
            raise TypeError(f"Expected 'str' or 'bytes', but {type(audio)}")

    def __upload_file(self, files):
        payload = {
            "thing_id": self.id,
            "cell_id": self.audio_col,
            "cell_type": "column",
        }

        self.client.post(
            path=UPLOAD_PATH,
            files=files,
            headers={"Referer": "https://app.memrise.com/course"},
            payload=payload,
        )

    def remove_audio(self) -> int:
        """Remove all audio from a learnable."""
        for file_id in range(1, self.audio_count + 1):
            payload = {
                "thing_id": self.id,
                "column_key": self.audio_col,
                "cell_type": "column",
                "file_id": file_id,
            }
            try:
                self.client.post(
                    path=DELETE_PATH,
                    headers={"Referer": "https://app.memrise.com/course"},
                    payload=payload,
                )
            except ConnectionError as e:
                print(f"Failed to remove audio audio file ID {file_id}: {e}")
                continue

            self.audio_count -= 1
        return self.audio_count


class Level:
    def __init__(self, client: Client, schema: LevelSchema):
        self.client = client
        self.schema = schema
        self.id = self.schema.id
        self.name = self.schema.title

    def get_words(self) -> List[Word]:
        """Retrieve learnables in a level."""
        data = self.client.get(f"/ajax/level/editing_html/?level_id={self.id}")
        return self.__parse_words(data)

    def __parse_words(self, data: Dict[str, Any]) -> List[Word]:
        """Parse learnables (words) from Memrise API response."""
        level: EditLevel = EditLevel(**data)
        learnables: List[Word] = []
        soup = BeautifulSoup(level.rendered, "html.parser")
        tags = soup("tr", {"class": "thing"})
        column_number = soup.find("th", {"class": "column audio"})["data-key"]
        for tag in tags:
            item = tag.get("data-thing-id")
            if item is not None:
                learnable_id = item
                learnable_text = tag.text.split("\n")[2].strip()
                numbers = re.findall("\\d+", tag.text)
                try:
                    audio_count = int(numbers[-1])
                except IndexError:
                    audio_count = 0
                    print(f"Word `{learnable_text}`: 0 audios")
                    pass
            # Using the others instead -----------
            learnables.append(
                Word(
                    client=self.client,
                    id=learnable_id,
                    text=learnable_text,
                    audio_col=column_number,
                    audio_count=audio_count,
                )
            )

        return learnables


class Course:
    def __init__(self, client: Client, schema: CourseSchema):
        self.client = client
        self.schema = schema
        self.id = schema.id
        self.name = schema.name
        self.source_lang = schema.source.language_code
        self.target_lang = schema.target.language_code

    def levels(self) -> List[Level]:
        """Retrieve course's levels."""
        data = self.client.get(f"/v1.17/courses/{self.id}/levels/")
        level_list = LevelList(**data)
        return [Level(self.client, schema) for schema in level_list.levels]

    def delete_all_level(self):
        levels: List[Level] = self.levels()
        success: bool = True
        for level in levels:
            success = success and self.delete_level(level.id)
        return success

    def delete_level(self, level_id) -> bool:
        status: bool = False
        payload: Dict[str, str] = {"level_id": f"{level_id}"}
        headers = {"Referer": f"https://app.memrise.com/course/{self.id}/edit/"}
        response = self.client.post(
            "/ajax/level/delete/", payload=payload, headers=headers
        )
        data = response.json()
        status = data["success"]
        return status

    def set_level_title(self, level_id: str, new_val: str) -> bool:
        headers: Dict[str, str] = {
            "Referer": f"https://app.memrise.com/course/{self.id}/edit/"
        }
        payload = {"level_id": f"{level_id}", "new_val": new_val}
        response = self.client.post(
            "/ajax/level/set_title/", payload=payload, headers=headers
        )
        # Validation status change name
        try:
            data = response.json()
        except json.decoder.JSONDecodeError as e:
            raise JSONParseError(f"Invalid JSON response for a GET request: {e}")
        else:
            status: bool = data["success"]
            if status is False:
                logging.warning(f"Failed to rename the level {level_id}")
        return status

    def add_bulk(
        self, level_id: str, bulk: str, sep: str, headers: Dict[str, str]
    ) -> bool:
        """Add bulk for the level."""

        payload = {
            "word_delimiter": sep,
            "data": bulk,
            "level_id": level_id,
        }
        response = self.client.post(
            "/ajax/level/add_things_in_bulk/", payload=payload, headers=headers
        )
        # Validation status:
        try:
            data = response.json()
        except json.decoder.JSONDecodeError as e:
            raise JSONParseError(f"Invalid JSON response for a GET request: {e}")
        else:
            status: bool = data["success"]
            if status is False:
                raise AddBulkError(id=level_id, message="Failed to Add Bulk.")
        return status

    def move_level(
        self, index: int, index_new: int, custom: Dict[str, str] = {}
    ) -> bool:
        status: bool
        levels: List[Level] = self.levels()
        orders: List[str] = [str(item.id) for item in levels]
        if custom != {}:
            for key, value in custom.items():
                orders.insert(int(key) - 1, value)

        level_id = orders[index - 1]
        orders.remove(level_id)
        orders.insert(index_new - 1, level_id)

        payload: Dict[str, str] = {
            "course_id": f"{self.id}",
            "level_ids": json.dumps(orders),
        }
        headers: Dict[str, str] = {
            "Referer": f"https://app.memrise.com/course/{self.id}/edit/"
        }
        try:
            response = self.client.post(
                "/ajax/course/reorder_levels/", payload=payload, headers=headers
            )
        except ConnectionError as e:
            logging.warning(f"Failed to move the level due to {e}")
            status = False
            return status

        # Validation status change name
        try:
            data = response.json()
        except (json.decoder.JSONDecodeError, UnboundLocalError) as e:
            raise JSONParseError(f"Invalid JSON response for a GET request: {e}")
        else:
            status = data["success"]
            if status is False:
                logging.warning(
                    f"Failed to move the level {level_id} from {index} to {index_new}"
                )
        return status

    def add_level(self) -> Tuple[str, Dict[str, str]]:
        """Add a new level in the course."""
        # Get the pool_id
        res = self.client.session.get(f"{URL}/course/{self.id}/any/edit/")
        soup = BeautifulSoup(res.content, "html.parser")
        tag = soup.find("div", {"class": "level collapsed"})
        data = {
            "course_id": f"{self.id}",
            "kind": "things",
            "pool_id": tag["data-pool-id"],
        }
        headers = {"Referer": f"{res.url}"}
        response = self.client.post("/ajax/level/add/", payload=data, headers=headers)

        try:
            data = response.json()
        except json.decoder.JSONDecodeError as e:
            raise AddLevelError(
                id=str(self.id),
                message=f"Invalid JSON response for a adding level request: {e}",
            )
        else:
            level_id = data["redirect_url"].split("_")[-1]

        return level_id, headers

    def add_level_with_bulk(self, name: str, bulk: str, sep: str) -> bool:
        """Add new level with bulk data."""
        # Validation for seperate parameter must be comma or tab
        if sep not in ["\t", ","]:
            raise InvalidSeperateElement(
                sep=sep, message="seperate paramater must be tab or comma."
            )
        else:
            word_delimiter = "tab" if sep == "\t" else "comma"
        # Part1: Add new level
        level_id, headers = self.add_level()

        # Part2: Rename the level title
        self.set_level_title(level_id, name)

        # Part3: Add bulk request
        try:
            status = self.add_bulk(level_id, bulk, word_delimiter, headers)
        except ConnectionError as e:
            status = False
            self.delete_level(level_id)
            logging.warning(f"Failed to add level with bulk {level_id}: {e}")
        return status

    def _update_audio_external(self, language):
        if language not in CUSTOM.keys():
            raise LanguageError(
                language=language,
                message="Not support. Please download the new packages.",
            )
        voices: List[str] = CUSTOM[language]
        naudios = len(voices)
        for voice in voices:
            levels = self.levels()
            for level in levels:
                print(f"Retriveing the level name `{level.name}`")
                words = level.get_words()
                for idx in range(len(words)):
                    if words[idx].audio_count < naudios:
                        filename = concat(words[idx].text)
                        vname = voice.replace(" ", "")
                        words[idx].upload_audio(f"./audio/{vname}/{filename}.mp3")

    def update_audio(self, language: str, speed: int = 170):
        levels = self.levels()
        tempFolder = tempfile.TemporaryDirectory()
        __voices__: List[str] = []
        for level_idx in range(len(levels)):
            words = levels[level_idx].get_words()
            for idx in range(len(words)):
                try:
                    files = generate_audio(
                        text=words[idx].text,
                        path=tempFolder.name,
                        language=language,
                        speed=speed,
                    )
                except LanguageError:
                    if len(__voices__) < 1:
                        __voices__ = choose_voices()
                    files = generate_audio_except(
                        text=words[idx].text,
                        path=tempFolder.name,
                        voices=__voices__,
                        speed=speed,
                    )
                words[idx].upload_audio(files)

    def sync_database(self, file: str):
        # Read the database find the new levels
        db = SQLite(file)

        # Select the local topics
        df_topic = db.select_local_topic()

        # Retrieval all topics to convert to bulk
        # And then connect to MEMRISE add bulk to new level for each topic
        for idx in range(df_topic.shape[0]):
            sep = "\t"
            # Get topic id & name
            topic_id = int(df_topic[0][idx])
            topic_name = df_topic[1][idx]
            # Streaming data
            bulk = db.topic_to_bulk(topic_id, sep)
            status = self.add_level_with_bulk(topic_name, bulk, sep)
            # Validate the status
            if status:
                logging.Logger(f"Successful to add level {topic_id}")
                db.switch_status(str(df_topic[0][idx]))
            else:
                logging.warning(f"Failed to add level {topic_id}")
        # Close the database
        db.close()

        # Update the audio for each levels
        self.update_audio("en")


@dataclass
class Memrise(Client):
    def select_course(self) -> Course:
        courses = self.courses()
        print("All courses: ")
        for indx in range(1, 1 + len(courses)):
            print(f"{indx}. {courses[indx-1].name}")
        choice = input("Make your choice: ")
        try:
            indx_choice = int(choice)
        except ValueError as e:
            raise ValueError(f"Input error with message: {e}")

        if indx_choice not in range(1, 1 + len(courses)):
            raise InputOutOfRange(
                indx_choice, f"Your choice out of range [1,{len(courses)}]"
            )
        retCourse: Course = courses[indx_choice - 1]
        return retCourse


@dataclass
class SQLite:
    filename: str
    conn: sqlite3.Connection = field(init=False)
    cur: sqlite3.Cursor = field(init=False)

    def __post_init__(self):
        self.conn = sqlite3.Connection(self.filename)
        self.cur = self.conn.cursor()

    def update_trans(self, src: str, dest: str):
        """Translation automatiacilly"""
        self.cur.execute(SELECT_NULL_MEANING)
        df = pd.DataFrame(self.cur.fetchall())
        bulk = transUntilDone(
            [item.lower() for item in list(df[0])], src=src, dest=dest, sep="\n\r"
        )

        for idx in range(len(bulk)):
            self.cur.execute(UPDATE_MEANING, (bulk[idx], df[0][idx]))

        self.conn.commit()

    def switch_status(self, topic_id: str):
        """Switch the status of the specific topic by id."""
        self.cur.execute(UPDATE_STATUS, (topic_id,))
        self.conn.commit()

    def update_ipas(self):
        """Convert and Update text to Internatioanl Phonetic Aplabets automaticially."""
        self.cur.execute(SELECT_NULL_IPA)
        df = pd.DataFrame(self.cur.fetchall())
        bulk = get_IPAs(list(df[0]), "am")

        for idx in range(len(bulk)):
            self.cur.execute(UPDATE_IPA, (bulk[idx], df[0][idx]))

        self.conn.commit()

    def select_local_topic(self) -> pd.DataFrame:
        """Select all local topics."""
        self.cur.execute(TOPIC_LOCAL)
        __df = pd.DataFrame(self.cur.fetchall())
        return __df

    def topic_to_bulk(
        self, topic_id: int, sep="\t", external: bool = False, language: str = ""
    ) -> str:
        """Convert the content of topic to bulk text."""
        bulk: str = ""
        df = self.__select_sentense_in_topic(topic_id)
        for idx in range(df.shape[0]):
            __learable: str = df[0][idx]
            __meaning: str = df[1][idx]
            __ipa: str = df[2][idx]
            if external:
                if language == "":
                    raise Exception("Missing language parameter.")
                external_generate_audio(language, __learable.lower())
            bulk += f"{__learable}{sep}{__meaning}{sep}{__ipa}\n"
        return bulk

    def __select_sentense_in_topic(self, topic_id: int) -> pd.DataFrame:
        """Local method: Select a specific topic by id."""
        self.cur.execute(SENS_IN_TOPIC, (topic_id,))
        __df = pd.DataFrame(self.cur.fetchall())
        return __df

    def close(self):
        """Close the database."""
        self.cur.close()
        self.conn.commit()
        self.conn.close()
