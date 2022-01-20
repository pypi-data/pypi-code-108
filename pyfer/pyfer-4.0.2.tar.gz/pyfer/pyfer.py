"""
PYFER - Encrypt and Decrypt messages.
-------------------------------------

Module-Wide Functions
---------------------
generate_key: Generates a random key of specified length.


Classes
-------
Machine: encryption and decryption machine.
    
    Class Methods:
        init: creates a Pyfer Crypt Machine.
        -
        scramble: uses the Crypt Machine to encrypt a message.
        -
        unscramble: uses the Crypt Machine to decrypt a message.
"""

import numpy as np
import string
import itertools

# ------------------------------------------------------------------------


def generate_key(key_length):

    """
    Generates a random string of digits of the specified length.
    """

    if type(key_length) is int:
        n = key_length
    else:
        raise Exception(
            f"key_length argument must be an integer; {type(key_length)} given."
        )

    str_key = "".join(
        ["{}".format(np.random.randint(10)) for num in range(0, n)]
    )

    return str_key


# ------------------------------------------------------------------------


class Machine:

    """
    Class representing an encryption machine.

    Attributes
    ----------
    key (str): string of 30, 40, or 45 digits to serving as encryption
    key.
    -
    char_list (list) optional/dependent on init: list of characters used
    by the encryption machine.
    -
    char_grid (numpy-array) optional/dependent on init: unscrambled grid
    version of list of characters used by the encryption machine.
    -
    scramble_grid (numpy-array) optional/dependent on init: scrambled
    grid of characters to used for the encryption and decryption of
    messages.

    Methods
    -------
    init: constructs all the necessary attributes for the encryption
    machine.
    -
    scramble: encrypts a message.
    -
    unscramble: decrypts a message.
    """

    def __init__(self, key):

        """
        Constructs all the necessary attributes for the Crypt encryption
        machine.

        Arguments:
            key (str): string of 30, 40, or 45 digits to serving as
            encryption key.

        Returns:
            Crypt encryption machine.
        """

        lc_list = list(string.ascii_lowercase)
        uc_list = list(string.ascii_uppercase)
        d_list = list(string.digits)
        p_med = ["!", "?"]
        p_full = [
            "!",
            "?",
            ".",
            ",",
            ":",
            ";",
            ")",
            "(",
            "_",
            "+",
            "-",
            "=",
            "<",
            ">",
            "%",
            "*",
            "/",
            "$",
            "&",
        ]

        if type(key) is str:
            pass
        else:
            raise Exception(f"key must be a string; {type(key)} given.")

        if len(key) == 30:
            self.key = key
            self.char_list = [
                x
                for x in itertools.chain.from_iterable(
                    itertools.zip_longest(lc_list, d_list)
                )
                if x
            ]
        elif len(key) == 40:
            self.key = key
            self.char_list = [
                x
                for x in itertools.chain.from_iterable(
                    itertools.zip_longest(
                        lc_list, uc_list, d_list, p_med
                    )
                )
                if x
            ]
        elif len(key) == 45:
            self.key = key
            self.char_list = [
                x
                for x in itertools.chain.from_iterable(
                    itertools.zip_longest(
                        lc_list, uc_list, d_list, p_full
                    )
                )
                if x
            ]
        else:
            self.key = None
            self.char_list = None
            raise Exception(
                "Invalid key type: must be string of 30, 40, or 45 digits."
            )

        if self.key is not None:
            square = int(len(self.key) / 5)
            try:
                intkey = int(self.key)
            except:
                raise Exception(
                    "Invalid key type: must be string of 30, 40, or 45 digits."
                )
            finally:
                key_x_elements = []
                for i in self.key[0:square]:
                    key_x_elements.append(int(i))
                    x_key = np.argsort(np.array(key_x_elements))

                key_y_elements = []
                for i in self.key[square : (2 * square)]:
                    key_y_elements.append(int(i))
                    y_key = np.argsort(np.array(key_y_elements))

                key_x2_elements = []
                for i in self.key[(2 * square) : (3 * square)]:
                    key_x2_elements.append(int(i))
                    x2_key = np.argsort(np.array(key_x2_elements))

                key_y2_elements = []
                for i in self.key[(3 * square) : (4 * square)]:
                    key_y2_elements.append(int(i))
                    y2_key = np.argsort(np.array(key_y2_elements))

                key_z_elements = []
                for i in self.key[(-1 * square) :]:
                    key_z_elements.append(int(i))
                    z_key = np.argsort(np.array(key_z_elements))

        self.char_grid = np.asarray(self.char_list).reshape(
            square, square
        )

        reshuffle_1 = self.char_grid[:, x_key]
        if len(self.key) == 40:
            reshuffle_2 = reshuffle_1.reshape(
                4, int((square ** 2) / 4)
            ).transpose()
        else:
            reshuffle_2 = reshuffle_1.reshape(
                3, int((square ** 2) / 3)
            ).transpose()
        reshuffle_3 = reshuffle_2.reshape(square, square)
        reshuffle_4 = reshuffle_3[y_key, :]

        reshuffle_5 = reshuffle_4[:, x2_key]
        if len(self.key) == 40:
            reshuffle_6 = reshuffle_5.reshape(
                4, int((square ** 2) / 4)
            ).transpose()
        else:
            reshuffle_6 = reshuffle_5.reshape(
                3, int((square ** 2) / 3)
            ).transpose()
        reshuffle_7 = reshuffle_6.reshape(square, square)
        reshuffle_8 = reshuffle_7[y2_key, :]

        reshuffle_9 = reshuffle_8[:, z_key]
        if len(self.key) == 40:
            reshuffle_10 = reshuffle_9.reshape(
                4, int((square ** 2) / 4)
            ).transpose()
        else:
            reshuffle_10 = reshuffle_9.reshape(
                3, int((square ** 2) / 3)
            ).transpose()
        reshuffle_11 = reshuffle_10.reshape(square, square)
        reshuffle_12 = reshuffle_11[z_key, :]

        self.scramble_grid = reshuffle_12

    #     ----------

    def scramble(self, input_string):

        """
        Scramble the input message using the Crypt Machine.

        Arguments:
            input_string (str): message to encrypt.

        Returns:
            output_string (str): encrypted message.
        """

        if type(input_string) is str:
            if np.mod(len(input_string), 2) == 0:
                if len(input_string) > 1:
                    if all(i in self.char_list for i in input_string):
                        pass
                    else:
                        raise Exception(
                            "Disallowed characters in input string"
                        )
                else:
                    raise Exception(
                        "Input string must have length greater than 1."
                    )
            else:
                raise Exception(
                    f"Input string must have even number of characters; {len(input_string)} given."
                )
        else:
            raise Exception(
                "Input must be string of even length greater than 1."
            )

        in_indices = []
        for i in input_string:
            in_indices.append(np.argwhere(self.scramble_grid == i)[0])
        out_indices = np.reshape(
            np.transpose(np.array(in_indices)), (len(input_string), 2)
        )

        output_list = []
        for i in range(len(input_string)):
            output_list.append(
                self.scramble_grid[out_indices[i][0], out_indices[i][1]]
            )
        output_string = "".join(output_list)

        return output_string

    #     ----------

    def unscramble(self, input_string):

        """
        Unscramble the input message using the Crypt Machine.

        Arguments:
            input_string (str): message to decrypt.

        Returns:
            output_string (str): decrypted message.
        """

        if type(input_string) is str:
            if np.mod(len(input_string), 2) == 0:
                if len(input_string) > 1:
                    if all(i in self.char_list for i in input_string):
                        pass
                    else:
                        raise Exception(
                            "Disallowed characters in input string"
                        )
                else:
                    raise Exception(
                        "Input string must have length greater than 1."
                    )
            else:
                raise Exception(
                    "Input string must have even number of characters and have length greater than 1."
                )
        else:
            raise Exception(
                "Input must be string of even length greater than 1."
            )

        in_indices = []
        for i in input_string:
            in_indices.append(np.argwhere(self.scramble_grid == i)[0])
        out_indices = np.transpose(
            np.reshape(np.array(in_indices), (2, len(input_string)))
        )

        output_list = []
        for i in range(len(input_string)):
            output_list.append(
                self.scramble_grid[out_indices[i][0], out_indices[i][1]]
            )
        output_string = "".join(output_list)

        return output_string
