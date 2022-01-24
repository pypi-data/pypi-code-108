from __future__ import annotations
from os import getcwd
from unittest import TestCase
from tempfile import TemporaryDirectory
from pathlib import Path
from jsonclasses_cli.package import package


class TestPackageTs(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = TemporaryDirectory()
        cls.temp_path = Path(str(cls.temp_dir.name)) / "app_path"
        cls.cls_dir = Path(getcwd()) / 'tests' / 'classes'
        cls.data_dir = Path(getcwd()) / 'tests' / 'data_package_ts'
        cls.ts_path = cls.temp_path / 'packages' / 'ts'

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp_dir.cleanup()

    def test_package_create_all_files(self) -> None:
        package(self.temp_path, self.cls_dir / 'simple_song', 'ts', 'simple', True)
        gitignore_path = self.ts_path / '.gitignore'
        package_json_path = self.ts_path  / 'package.json'
        config_path = self.ts_path / 'tsconfig.json'
        api_path = self.ts_path  / 'src' / 'index.ts'
        self.assertTrue(gitignore_path.is_file(), gitignore_path.name)
        self.assertTrue(package_json_path.is_file(), package_json_path.name)
        self.assertTrue(config_path.is_file, config_path.name)
        self.assertTrue(api_path.is_file, api_path.name)

    def test_package_content_of_gitignore_packagejson_tsconfig(self) -> None:
        package(self.temp_path, self.cls_dir / 'simple_song', 'ts', 'simple', True)
        gitignore_path = self.ts_path / '.gitignore'
        test_gitignore_path = self.data_dir / '.gitignore'
        package_json_path =  self.ts_path  / 'package.json'
        test_package_json_path = self.data_dir / 'package.json'
        config_path =  self.ts_path / 'tsconfig.json'
        test_config_path = self.data_dir / 'tsconfig.json'
        self.assertEqual(gitignore_path.read_text(), test_gitignore_path.read_text())
        self.assertEqual(package_json_path.read_text(), test_package_json_path.read_text())
        self.assertEqual(config_path.read_text(), test_config_path.read_text())

    def test_package_create_without_link_and_session(self) -> None:
        package(self.temp_path, self.cls_dir / 'simple_song.py', 'ts', 'simple', True)
        result = self.ts_path / 'src' / 'index.ts'
        expect = self.data_dir / 'simple_song_api.ts'
        self.assertEqual(result.read_text(), expect.read_text())

    def test_package_create_with_session(self) -> None:
        package(self.temp_path, self.cls_dir / 'session.py', 'ts', 'session', True)
        result = self.ts_path / 'src' / 'index.ts'
        expect = self.data_dir / 'session_api.ts'
        self.assertEqual(result.read_text(), expect.read_text())

    def test_package_create_with_linkedthru_and_session(self) -> None:
        package(self.temp_path, self.cls_dir / 'linkedthru_session.py', 'ts', 'linkedthru_session', True)
        result = self.ts_path / 'src' / 'index.ts'
        expect = self.data_dir / 'linkedthru_session_api.ts'
        self.assertEqual(result.read_text(), expect.read_text())

    def test_package_create_with_linkedthru(self) -> None:
        package(self.temp_path, self.cls_dir / 'linkedthru.py', 'ts', 'linkedthru', True)
        result = self.ts_path / 'src' / 'index.ts'
        expect = self.data_dir / 'linkedthru_api.ts'
        self.assertEqual(result.read_text(), expect.read_text())

    def test_package_create_with_linkto_and_session(self) -> None:
        package(self.temp_path, self.cls_dir / 'linkto_session.py', 'ts', 'linkto_session', True)
        result = self.ts_path / 'src' / 'index.ts'
        expect = self.data_dir / 'linkto_session_api.ts'
        self.assertEqual(result.read_text(), expect.read_text())

    def test_package_create_with_linkto(self) -> None:
        package(self.temp_path, self.cls_dir / 'linkto.py', 'ts', 'linkto', True)
        result = self.ts_path / 'src' / 'index.ts'
        expect = self.data_dir / 'linkto_api.ts'
        self.assertEqual(result.read_text(), expect.read_text())
