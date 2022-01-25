from __future__ import annotations
import re
from os import getcwd
from unittest import TestCase
from tempfile import TemporaryDirectory
from pathlib import Path
from jsonclasses_cli.new import new


class TestNew(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = TemporaryDirectory()
        cls.data_path = Path(getcwd()) / 'tests' / 'data_new'

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp_dir.cleanup()

    def setUp(self) -> None:
        self.temp_path = Path(str(self.temp_dir.name)) / "new_app"


    def test_new_create_all_filed(self) -> None:
        new(self.temp_path, None, None, None, None, None, True)
        app = self.temp_path / 'app.py'
        requirements = self.temp_path / 'requirements.txt'
        config = self.temp_path / 'config.json'
        mypy = self.temp_path / 'mypy.ini'
        gitignore = self.temp_path / '.gitignore'
        read_me = self.temp_path / 'README.md'
        self.assertTrue(app.is_file(), app.name)
        self.assertTrue(requirements.is_file(), requirements.name)
        self.assertTrue(config.is_file(), config.name)
        self.assertTrue(mypy.is_file(), mypy.name)
        self.assertTrue(gitignore.is_file(), gitignore.name)
        self.assertTrue(read_me.is_file(), read_me.name)

    def test_new_app_content_without_admin_and_user(self) -> None:
        new(self.temp_path, None, None, None, None, None, True)
        result = self.temp_path / 'app.py'
        expect = self.data_path / 'app.py'
        self.assertEqual(result.read_text(), expect.read_text())

    def test_new_app_content_with_user(self) -> None:
        new(self.temp_path, None, True, None, None, None, True)
        result = self.temp_path / 'app.py'
        expect = self.data_path / 'app_with_u.py'
        self.assertEqual(result.read_text(), expect.read_text())

    def test_new_app_content_with_admin(self) -> None:
        new(self.temp_path, None, None, True, None, None, True)
        result = self.temp_path / 'app.py'
        expect = self.data_path / 'app_with_a.py'
        self.assertEqual(result.read_text(), expect.read_text())

    def test_new_app_content_with_user_and_admin(self) -> None:
        new(self.temp_path, None, True, True, None, None, True)
        result = self.temp_path / 'app.py'
        expect = self.data_path / 'app_with_ua.py'
        self.assertEqual(result.read_text(), expect.read_text())

    def test_new_genarate_content_of_config(self) -> None:
        new(self.temp_path, None, True, True, None, None, True)
        result = (self.temp_path / 'config.json').read_text()
        expect = (self.data_path / 'config.json').read_text()
        filter_result = re.sub(r'\"secretKey\": \".*\"', '', result)
        self.assertEqual(filter_result, expect)

    def test_new_genarate_content_of_requirements(self) -> None:
        new(self.temp_path, None, False, False, None, None, True)
        result = (self.temp_path / 'requirements.txt').read_text()
        expect = (self.data_path / 'requirements.txt').read_text()
        self.assertEqual(result, expect)

    def test_new_genarate_content_of_requirements_with_user_or_admin(self) -> None:
        new(self.temp_path, None, True, False, None, None, True)
        result = (self.temp_path / 'requirements.txt').read_text()
        expect = (self.data_path / 'requirements_with_ua.txt').read_text()
        self.assertEqual(result, expect)

    def test_new_genarate_content_of_mypy_gitignore_and_readme(self) -> None:
        new(self.temp_path, None, None, None, None, None, True)
        mypy = self.temp_path / 'mypy.ini'
        gitignore = self.temp_path / '.gitignore'
        read_me = self.temp_path / 'README.md'
        expect_mypy = self.data_path / 'mypy.ini'
        expect_gitignore = self.data_path / '.gitignore'
        expect_read_me = self.data_path / 'README.md'
        self.assertEqual(mypy.read_text(), expect_mypy.read_text())
        self.assertEqual(gitignore.read_text(), expect_gitignore.read_text())
        self.assertEqual(read_me.read_text(), expect_read_me.read_text())
