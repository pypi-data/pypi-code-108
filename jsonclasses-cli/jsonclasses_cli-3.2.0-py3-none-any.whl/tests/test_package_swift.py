from __future__ import annotations
from os import getcwd
from unittest import TestCase
from tempfile import TemporaryDirectory
from pathlib import Path
from jsonclasses_cli.package import package


class TestPackageSwift(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = TemporaryDirectory()
        cls.temp_path = Path(str(cls.temp_dir.name)) / "swift_path"
        cls.cls_dir = Path(getcwd()) / 'tests' / 'classes'
        cls.data_path = Path(getcwd()) / 'tests' / 'data_package_swift'
        cls.swift_path = cls.temp_path / 'packages' / 'swift'

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp_dir.cleanup()

    def test_package_swift_create_all_files(self) -> None:
        package(self.temp_path, self.cls_dir / 'simple_song', 'swift', 'simple', True)
        gitignore = self.swift_path / '.gitignore'
        package_swift = self.swift_path  / 'Package.swift'
        read_me = self.swift_path  / 'README.md'
        api = self.swift_path  / 'Sources' / 'API' / 'API.swift'
        self.assertTrue(gitignore.is_file(), gitignore.name)
        self.assertTrue(package_swift.is_file(), package_swift.name)
        self.assertTrue(read_me.is_file(), read_me.name)
        self.assertTrue(api.is_file(), api.name)

    def test_package_swift_content_of_gitignore_package_and_readme(self) -> None:
        package(self.temp_path, self.cls_dir / 'simple_song', 'swift', 'simple', True)
        package_swift = self.swift_path / 'Package.swift'
        gitignore = self.swift_path / '.gitignore'
        read_me = self.swift_path / 'README.md'
        expect_package_swift = self.data_path / 'Package.swift'
        expect_gitignore = self.data_path / '.gitignore'
        expect_read_me = self.data_path / 'README.md'
        self.assertEqual(package_swift.read_text(), expect_package_swift.read_text())
        self.assertEqual(gitignore.read_text(), expect_gitignore.read_text())
        self.assertEqual(read_me.read_text(), expect_read_me.read_text())

    def test_package_create_without_link_and_session(self) -> None:
        package(self.temp_path, self.cls_dir / 'simple_song', 'swift', 'simple', True)
        result = self.swift_path / 'Sources' / 'API' / 'API.swift'
        expect = self.data_path / 'simple_api.swift'
        self.assertEqual(result.read_text(), expect.read_text())

    def test_package_create_with_session(self) -> None:
        package(self.temp_path, self.cls_dir / 'session.py', 'swift', 'session', True)
        result = self.swift_path / 'Sources' / 'API' / 'API.swift'
        expect = self.data_path / 'session_api.swift'
        self.assertEqual(result.read_text(), expect.read_text())

    def test_package_create_with_linkedthru_and_session(self) -> None:
        package(self.temp_path, self.cls_dir / 'linkedthru_session.py', 'swift', 'linkedthru_session', True)
        result = self.swift_path / 'Sources' / 'API' / 'API.swift'
        expect = self.data_path / 'linkedthru_session_api.swift'
        self.assertEqual(result.read_text(), expect.read_text())

    def test_package_create_with_linkedthru(self) -> None:
        package(self.temp_path, self.cls_dir / 'linkedthru.py', 'swift', 'linkedthru', True)
        result = self.swift_path / 'Sources' / 'API' / 'API.swift'
        expect = self.data_path / 'linkedthru_api.swift'
        self.assertEqual(result.read_text(), expect.read_text())

    def test_package_create_with_linkto_and_session(self) -> None:
        package(self.temp_path, self.cls_dir / 'linkto_session.py', 'swift', 'linkto_session', True)
        result = self.swift_path / 'Sources' / 'API' / 'API.swift'
        expect = self.data_path / 'linkto_session_api.swift'
        self.assertEqual(result.read_text(), expect.read_text())

    def test_package_create_with_linkto(self) -> None:
        package(self.temp_path, self.cls_dir / 'linkto.py', 'swift', 'linkto', True)
        result = self.swift_path / 'Sources' / 'API' / 'API.swift'
        expect = self.data_path / 'linkto_api.swift'
        self.assertEqual(result.read_text(), expect.read_text())
