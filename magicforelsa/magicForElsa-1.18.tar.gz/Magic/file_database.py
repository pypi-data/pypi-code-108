"""This module deals with adding and verifying usernames"""
import json
import os

# Get the path of users.elsa
userpth = os.getcwd() + "/resources/ users.elsa"


def check_user_from_file(username: str) -> str:
    """This extension is used to check if the user is valid or not """
    try:
        with open(userpth, "r") as file:
            return json.load(file).get(username, None)
    except Exception as e: print("It seems that some error has happened", e)


def write_to_file(username: str, password: str) -> int:
    """Writes the username and password to users.elsa file"""
    try:
        with open(userpth, "r") as file:
            data = json.load(file)
        if username.lower().strip() not in {
            '', "initial", "cache", "users", "user", "theme", "indexer", "resources", "dummy", "indexerpaths", "indexerfolder"}:
            with open(userpth, "w") as file:
                data[username] = password
                json.dump(data, file, indent = 4)
            print(f"Added user {username} ")
            # returns state = 1 so that program knows that writing was successful
            return 1
        else:
            print("User already exists or the username is reserved")
            # return state = -1 to know that user was not added mainly due to username repetitions or reserved words
            return -1
    except Exception as e: print(e, "Try again")
