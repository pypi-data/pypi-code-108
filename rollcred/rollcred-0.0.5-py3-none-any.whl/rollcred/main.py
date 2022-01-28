import xerox
import os
import click


class BadClipboardContentsError(Exception):
    pass


def get_clip_input():
    split_input = []
    clip_input = xerox.paste(xsel=True)

    split_input = clip_input.splitlines()

    if len(split_input) == 4:
        clip_input = split_input
        return clip_input
    else:
        raise BadClipboardContentsError("Bad clipboard contents, try copy again")


def replace_lines_in_awscreds(file_input, clip_input):
    try:
        cred_idx = file_input.index(clip_input[0])
        for idx in range(cred_idx + 1, cred_idx + 4):
            file_input[idx] = clip_input[idx - cred_idx]
        with open(os.path.expanduser("~/.aws/credentials"), "wt") as filehandle:
            filehandle.write("\n".join(file_input))
        return "Success"
    except ValueError as err:
        print(err)
        print("Appending clipped credentials to creds file.")
        file_input.extend(clip_input)
        with open(os.path.expanduser("~/.aws/credentials"), "wt") as filehandle:
            filehandle.write("\n".join(file_input))
        return "Success"


@click.command()
def cli():
    try:
        with open(os.path.expanduser("~/.aws/credentials"), "r") as opened_file:
            creds = opened_file.read()
    except FileNotFoundError as err:
        print("Creds file not found at ~/.aws/credentials. Creating file.")
        with open(os.path.expanduser("~/.aws/credentials"), "a+") as opened_file:
            creds = opened_file.read()
    file_input = creds.split("\n")

    try:
        clip_input = get_clip_input()
        result = replace_lines_in_awscreds(file_input, clip_input)
        print(result)
    except BadClipboardContentsError as err:
        print(err)


if __name__ == "__main__":
    replace_aws_creds()
