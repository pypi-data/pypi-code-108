import click
import numpy as np


@click.command()
@click.option("--src", help="File containing raw word list")
@click.option("--size", default=5, help="word length filter size")
def filter_word_list(src, size) -> None:

    # Get all words in english dictionary
    words = np.loadtxt(src, dtype="str")

    # Filter only words with length of 5
    words = words[np.where(np.array([len(word) for word in words]) == size)]

    # Filter only words with alphabetical characters
    words = words[np.where(np.array([word.isalpha() for word in words]) is True)]

    # Make all words lowercase
    words = np.array([word.lower() for word in words])

    # Store words
    np.savetxt(src.replace(".txt", "_filtered.txt"), words, fmt="%s")


if __name__ == "__main__":
    filter_word_list()
