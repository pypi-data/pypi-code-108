from typing import Dict
from pymongo import MongoClient
import os
import re
import json

from datetime import datetime


def process_val(val, item):
    if re.search(r"\d+", val):
        try:
            casted = int(re.search(r"\d+", val).group(0))
            return casted
        except Exception as e:
            print(f"[bold red] {e}")
            print("Not parsible id:" + str(item["_id"]))
    return None


def edit_value(collection, key, regex):
    result = collection.find({key: {"$regex": regex}})
    for item in result:
        val: str = item.get(key)
        if type(val) == list:
            for idx, value in enumerate(val):
                casted = process_val(value, item)
                if casted:
                    if idx == 0:
                        collection.update_one(
                            {"_id": item["_id"]}, {"$set": {key: [casted]}}
                        )
                    else:
                        collection.update_one(
                            {"_id": item["_id"]}, {"$set": {key: {"$push": casted}}}
                        )

        elif type(val) == str:
            casted = process_val(val, item)
            if casted:
                collection.update_one({"_id": item["_id"]}, {"$set": {key: casted}})

        # if type(item.get(key, None)) == list and item.get(key, None) and all([type(x) == str for x in item[key]]):
        #     collection.update_one({'_id': item['_id']}, {'$set': {key: ''.join(item[key])}})
        #     element = collection.find_one({'_id': item['_id']})
        #     process_amount(collection, item, key, r'^(.+?)\s*(\d+(\.\d+)?)\s*(-|\u2013)?(\s*\d+(\.\d+)?)?\s*(crores|million|billion)s?', 7)

        #     regex =r'^(Rs.|\$|.+?)?\s*(\d+(\.\d+)?)\s*(-)?(\s*\d+(\.\d+)?)?\s*'
        #     if type(element.get(key,None)) == str and element.get(key, None) and re.search(regex, element[key], re.IGNORECASE):
        #         match = re.search(regex, element[key], re.IGNORECASE)
        #         if len(match.groups()) != 6:
        #             continue
        #         (currency, low, x, _, high, y) = match.groups()
        #         if low and high:
        #         # range of gross income
        #             # collection.update_one({'_id': element['_id']}, {'$set': {key: {'minimum': {'value': float(low), 'currency': currency}, 'maximum': {'value': float(high), 'currency': currency}}}})
        #             collection.update_one({'_id': item['_id']}, {'$set': {key: '{0}{1}-{2}{3}'.format(currency, float(low)*mfactor, currency, float(high)*mfactor)}})

        #         if low and not high:
        #         # single value
        #             # collection.update_one({'_id': element['_id']}, {'$set': {key: {'value': float(low), 'currency': currency}}})
        #             collection.update_one({'_id': item['_id']}, {'$set': {key: '{0}{1}'.format(currency, float(low)*mfactor)}})


def string_amt_sanitize(collection, key):
    result = collection.find()
    for item in result:
        if (
            item.get(key, None)
            and type(item.get(key, None)) == str
            and re.search(r"(.+?)\s*(\d+(\.\d+)?)", item[key])
        ):
            matches = re.finditer(r"(.+?)\s*(\d+(\.\d+)?)", item[key])
            for match in matches:
                currency = match.group(1)
                amount = match.group(2)
                try:
                    collection.update_one(
                        {"_id": item["_id"]},
                        {"$set": {key: {"value": float(amount), "currency": currency}}},
                    )
                except ValueError:
                    continue


def normalize(collection, key):
    result = collection.find()
    for item in result:
        if item.get(key, None) and type(item[key]) == str:
            collection.update_one(
                {"_id": item["_id"]}, {"$set": {key: item[key].title()}}
            )


class DBWriter:
    """
    Handling Database operations for adding and cleaning of the
    data generated from the Wiki-Parser
    """

    def __init__(
        self,
        connection_str: str,
        host: str,
        port: str,
        user: str,
        passwrd: str,
        db: str,
        collection: str,
        auth_db: str = "admin",
    ) -> None:
        if connection_str:
            self.__mongo__ = MongoClient(connection_str)
        else:
            self.__mongo__ = MongoClient(
                host=host, username=user, password=passwrd, port=port
            )
        self.__db__ = self.__mongo__.get_database(db)
        self.__collection__ = self.__db__.get_collection(collection)

    def write(self, directory: str = "extracts"):
        dir_contents = os.listdir(directory)

        for content in dir_contents:
            if os.path.isfile(os.path.join(directory, content)):
                with open(os.path.join(directory, content), "r") as file:
                    jsonarray: Dict = json.loads(file.read())
                    self.__collection__.insert_many(jsonarray.values())

    def process_dates(self):
        """
        Convert the date string to ISODate type
        """
        result = self.__collection__.find()
        for item in result:
            if (
                item.get("released", None)
                and type(item["released"]) == list
                and type(item["released"][0]) == dict
            ):
                for idx, release in enumerate(item["released"]):
                    if (
                        type(release["date"]) == str
                        and release["date"]
                        and re.search(r"\d{4}\/\d{2}\/\d{2}", release["date"])
                    ):
                        try:
                            date = datetime.strptime(release["date"], "%Y/%m/%d")
                        except ValueError:
                            continue
                        self.__collection__.update_one(
                            {"_id": item["_id"]},
                            {"$set": {"released.{}.date".format(idx): date}},
                        )
                    if (
                        type(release["date"]) == str
                        and release["date"]
                        and release["date"].isdigit()
                    ):
                        self.__collection__.update_one(
                            {"_id": item["_id"]},
                            {
                                "$set": {
                                    "released.{}.date".format(idx): int(release["date"])
                                }
                            },
                        )
            if (
                item.get("released", None)
                and type(item["released"]) == str
                and item["released"].isdigit()
            ):
                self.__collection__.update_one(
                    {"_id": item["_id"]}, {"$set": {"released": int(item["released"])}}
                )
