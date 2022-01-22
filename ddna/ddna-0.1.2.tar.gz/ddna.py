"""
Program that encodes and decodes string to DNA sequence
It's like base64 but for DNA and worse :D
"""
import re

from helpers.utils import arguments, banner, convert_to_bits, convert_to_string


class DDNA:
    """
    Main class that runs the program, it's a bit messy but it works
    Works both as a standalone program and as a module
    ie: import DDNA  [in python file]
    or DDNA --help [in terminal]
    """

    def __init__(self):
        self.bases = {
            "00": "A",
            "01": "C",
            "10": "G",
            "11": "T"
        }
        self.bases_rev = {
            "A": "00",
            "C": "01",
            "G": "10",
            "T": "11"
        }

    # pylint: disable=no-self-use
    def check_validity(self, string):
        """
        Check if string is a valid dna sequence using regex
        """
        return re.match("^[ACGT]*$", string)

    def encode(self, string):
        """"
        Encodes String to DNA bases
        Parameters:
            String (sentences, words)

        Returns:
            DNA sequence ACTG ATAT...
        """

        bits = convert_to_bits(string)

        encoded_bits = ""
        for i in range(0, len(bits), 2):
            encoded_bits += self.bases[bits[i:i+2]]
        return encoded_bits

    def decode(self, string):
        """"
        Decodes DNA bases to String
        Parameters:
            DNA sequence ACTG ATAT...

        Returns:
            String (sentences, words)
        """
        if not self.check_validity(string):
            raise ValueError("Invalid DNA sequence")

        bits = ""
        for char in string:
            bits += self.bases_rev[char]

        return convert_to_string(bits)

    def main(self):
        """
        Main function that runs the program if called as a standalone program
        """
        args = arguments()
        if args.encode:
            print(self.encode(args.encode))
        elif args.decode:
            print(self.decode(args.decode))
        else:
            banner()
            print("Usage:")
            print("\tddna -e <string>")
            print("\tddna -d <string>")
            print("\tddna --help")


if __name__ == "__main__":
    DDNA().main()
