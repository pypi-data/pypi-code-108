import string
from unittest import TestCase

from django_keygen import KeyGen, SecurityWarning, SecurityException


class KeyGeneration(TestCase):
    """Tests for the generation of secret keys"""

    def test_returned_length(self) -> None:
        """Tet the returned key length matches the ``length`` argument"""

        for i in range(10, 25, 50):
            self.assertEqual(i, len(KeyGen().gen_secret_key(i, force=True)))

    def test_sequential_not_equal(self) -> None:
        """Test sequential keys do not match"""

        # This isn't really a true test for randomness - those are very involved
        # However, it will protect a developer who left behind a seed while debugging
        self.assertNotEqual(
            KeyGen().gen_secret_key(),
            KeyGen().gen_secret_key()
        )


class SecurityErrorsAndWarnings(TestCase):
    """Tests for security warnings and errors"""

    def test_error_on_non_positive_length(self) -> None:
        """Test for a ``ValueError`` on a non-positive key length"""

        with self.assertRaises(ValueError):
            KeyGen().gen_secret_key(length=0)

        with self.assertRaises(ValueError):
            KeyGen().gen_secret_key(length=-1)

    def test_warn_on_short_length(self) -> None:
        with self.assertRaises(SecurityException):
            KeyGen().gen_secret_key(length=29)

        with self.assertWarns(SecurityWarning):
            KeyGen().gen_secret_key(length=29, force=True)

    def test_warn_on_small_char_set(self) -> None:
        with self.assertRaises(SecurityException):
            KeyGen().gen_secret_key(chars='abcd')

        with self.assertWarns(SecurityWarning):
            KeyGen().gen_secret_key(chars='abcd', force=True)


class DefaultCharacterSet(TestCase):
    """Tests for the default character set used in key generation"""

    def assertSubsetChars(self, expected: str, actual: str) -> None:
        """Test if characters of the ``expected`` string are a subset of the ``actual`` string"""

        expected_set = set(expected)
        actual_set = set(actual)
        self.assertTrue(expected_set.issubset(actual_set))

    def test_contains_ascii_lower(self) -> None:
        """Test keys pull from lowercase letters"""

        self.assertSubsetChars(string.ascii_lowercase, KeyGen().default_chars)

    def test_contains_ascii_upper(self) -> None:
        """Test keys pull from uppercase letters"""

        self.assertSubsetChars(string.ascii_uppercase, KeyGen().default_chars)

    def test_contains_punctuation(self) -> None:
        """Test keys pull from punctuation"""

        self.assertSubsetChars(string.punctuation, KeyGen().default_chars)
