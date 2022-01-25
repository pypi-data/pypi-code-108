"""test_file_catalog.py module."""

# standard library imports
from pathlib import Path
import pytest
from typing import Any, cast, Dict

# third party imports

# local imports
import scottbrian_utils.file_catalog as cat

# build case list for tests
# first tuple item is the file name and second tuple item is the
# full file path
file_specs_list = [{'file1': Path('/run/media/file1.csv')},
                   {'file1': Path('/run/media/file1.csv'),
                    'file2': Path('/run/media/file2.csv')},
                   {'file1': Path('/run/media/file1.csv'),
                    'file2': Path('/run/media/file2.csv'),
                    'file3': Path('/run/media/file3.csv')},
                   {'file1': Path('/run/media/file1.csv'),
                    'file2': Path('/run/media/file2.csv'),
                    'file3': Path('/run/media/file3.csv'),
                    'file4': Path('/run/media/file4.csv')},
                   {'file1': Path('/run/media/file1.csv'),
                    'file2': Path('/run/media/file2.csv'),
                    'file3': Path('/run/media/file3.csv'),
                    'file4': Path('/run/media/file4.csv'),
                    'file5': Path('/run/media/file5.csv')}
                   ]


@pytest.fixture(params=file_specs_list)  # type: ignore
def file_specs(request: Any) -> Dict[str, Path]:
    """Pytest fixture for different file_specs args.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(Dict[str, Path], request.param)


class TestFileCatalog:
    """TestFileCatalog class."""

    def test_file_catalog_with_no_file_specs(self,
                                             capsys: Any) -> None:
        """test_file_catalog with no file_specs not in list.

        Args:
            capsys: instance of the capture sys fixture

        """
        a_catalog = cat.FileCatalog()

        assert len(a_catalog) == 0

        with pytest.raises(cat.FileNameNotFound):
            _ = a_catalog.get_path('file1')

        print(a_catalog)  # test of __repr__
        captured = capsys.readouterr().out

        expected = "FileCatalog()\n"

        assert captured == expected

    def test_file_catalog_with_empty_file_specs(self) -> None:
        """test_file_catalog with empty file_specs."""
        with pytest.raises(cat.FileSpecIncorrect):
            _ = cat.FileCatalog([()])  # type: ignore

        with pytest.raises(cat.FileSpecIncorrect):
            _ = cat.FileCatalog('file1')  # type: ignore

        with pytest.raises(cat.FileSpecIncorrect):
            _ = cat.FileCatalog(('file1'))  # type: ignore

        with pytest.raises(cat.FileSpecIncorrect):
            _ = cat.FileCatalog(('file1', Path('path1')))  # type: ignore

        with pytest.raises(cat.FileSpecIncorrect):
            _ = cat.FileCatalog(['file1'])  # type: ignore

        with pytest.raises(cat.FileSpecIncorrect):
            _ = cat.FileCatalog([('file1')])  # type: ignore

        with pytest.raises(cat.FileSpecIncorrect):
            _ = cat.FileCatalog([('file1',)])  # type: ignore

        with pytest.raises(cat.FileSpecIncorrect):
            _ = cat.FileCatalog([(42)])  # type: ignore

        with pytest.raises(cat.FileSpecIncorrect):
            _ = cat.FileCatalog([(42, 24)])  # type: ignore

        with pytest.raises(cat.FileSpecIncorrect):
            _ = cat.FileCatalog({42: 24})  # type: ignore

        with pytest.raises(cat.FileSpecIncorrect):
            _ = cat.FileCatalog([(42, 'path1')])  # type: ignore

        with pytest.raises(cat.FileSpecIncorrect):
            _ = cat.FileCatalog({42: 'path1'})  # type: ignore

        with pytest.raises(cat.FileSpecIncorrect):
            _ = cat.FileCatalog([('file1', 42)])  # type: ignore

        with pytest.raises(cat.FileSpecIncorrect):
            _ = cat.FileCatalog({'file1': 42})  # type: ignore

        with pytest.raises(cat.FileSpecIncorrect):
            _ = cat.FileCatalog([[('file1', 'path1')]])  # type: ignore

        with pytest.raises(cat.FileSpecIncorrect):
            _ = cat.FileCatalog({'file1': 'path1'})  # type: ignore

        with pytest.raises(cat.FileSpecIncorrect):
            _ = cat.FileCatalog(({'file1': 'path1'}))  # type: ignore

        with pytest.raises(cat.FileSpecIncorrect):
            _ = cat.FileCatalog([(('file1', 'path1'),)])  # type: ignore

    def test_file_catalog_with_single_file_specs(self,
                                                 capsys: Any) -> None:
        """test_file_catalog with single file_specs not in list.

        Args:
            capsys: instance of the capture sys fixture

        """
        file_1 = 'file1'
        path_1 = Path('/run/media/file1.csv')

        for i in range(4):
            if i == 0:
                a_catalog = cat.FileCatalog({'file1':
                                             Path('/run/media/file1.csv')})
            elif i == 1:
                a_catalog = cat.FileCatalog({file_1: path_1})

            elif i == 2:
                file_spec2 = {'file1': Path('/run/media/file1.csv')}
                a_catalog = cat.FileCatalog(file_spec2)

            else:  # i == 3:
                file_spec3 = {file_1: path_1}
                a_catalog = cat.FileCatalog(file_spec3)

            assert len(a_catalog) == 1

            assert a_catalog.get_path('file1') == Path('/run/media/file1.csv')

            with pytest.raises(cat.FileNameNotFound):
                _ = a_catalog.get_path('file2')

            print(a_catalog)  # test of __repr__
            captured = capsys.readouterr().out

            expected = ("FileCatalog("
                        "{'file1': Path('/run/media/file1.csv')})\n")

            assert captured == expected

    def test_catalog_with_list_of_file_specs(self,
                                             capsys: Any,
                                             file_specs: cat.FileSpecs
                                             ) -> None:
        """test_file_catalog with lists of file_specs.

        Args:
            capsys: instance of the capture sys fixture
            file_specs: the list of file names and paths to use

        """
        for j in range(3):
            if j == 0:
                a_catalog = cat.FileCatalog(file_specs)
            elif j == 1:
                a_catalog = cat.FileCatalog()
                assert len(a_catalog) == 0
                a_catalog.add_paths(file_specs)
            else:
                a_catalog = cat.FileCatalog()
                assert len(a_catalog) == 0

                for k, (file_name, path) in enumerate(file_specs.items()):
                    expected_len = len(a_catalog) + 1

                    with pytest.raises(cat.FileNameNotFound):
                        _ = a_catalog.get_path(file_name)

                    a_catalog.add_paths({file_name: path})
                    assert a_catalog.get_path(file_name) == path
                    assert len(a_catalog) == expected_len

            assert len(a_catalog) == len(file_specs)

            num_indent_spaces = len('FileCatalog') + len('([')
            indent_spaces = ''
            parms = ''

            if isinstance(file_specs, list):
                a_file_specs = file_specs
            else:
                a_file_specs = list(file_specs.items())
            for i, (name, path) in enumerate(a_file_specs):
                assert a_catalog.get_path(name) == path
                if (len(file_specs) <= 4) or\
                        (i < 2) or (i == len(a_file_specs)-1):  # first 2 or
                    # last
                    parms = parms + indent_spaces + "'" + name + "': " + \
                            "Path('" + str(path.as_posix()) + "'),\n"
                if len(file_specs) > 4:
                    if (i == 2) and (i != len(a_file_specs)-1):  # middle,
                        # not last
                        parms = parms + indent_spaces + '...\n'
                indent_spaces = ' ' * num_indent_spaces

            parms = '{' + parms[:-2] + '}'  # remove final comma and new_line

            expected = 'FileCatalog(' + parms + ')\n'
            print(a_catalog)  # test of __repr__
            captured = capsys.readouterr().out
            assert captured == expected

    def test_file_catalog_add_paths_exceptions(
            self,
            capsys: Any,
            file_specs: cat.FileSpecs) -> None:
        """test_file_catalog add_paths exceptions.

        Args:
            capsys: instance of the capture sys fixture
            file_specs: the list of file names and paths to use

        """
        # instantiate a catalog
        a_catalog = cat.FileCatalog(file_specs)
        assert len(a_catalog) == len(file_specs)

        # try to add the file_specs again - should be OK
        a_catalog.add_paths(file_specs)
        assert len(a_catalog) == len(file_specs)

        for (file_name, path) in file_specs.items():
            # the number of entries should remain the same throughout
            # tests
            assert len(a_catalog) == len(file_specs)

            # we should always find the entries we added earlier
            assert a_catalog.get_path(file_name) == path

            # try to add same entry again
            a_catalog.add_paths({file_name: path})
            assert len(a_catalog) == len(file_specs)
            assert a_catalog.get_path(file_name) == path

            diff_path = Path('different/path')

            # should get the exception with same file name but different
            # path

            with pytest.raises(cat.IllegalAddAttempt):
                a_catalog.add_paths({file_name: diff_path})

            with pytest.raises(cat.IllegalAddAttempt):
                a_catalog.add_paths({file_name: diff_path})

            # ensure we still have expected results
            assert len(a_catalog) == len(file_specs)
            assert a_catalog.get_path(file_name) == path

            # try adding two entries, one good and one bad
            new_file_name = 'newFile1'
            new_file_path = Path('newFilePath1')

            with pytest.raises(cat.IllegalAddAttempt):
                a_catalog.add_paths({new_file_name: new_file_path,
                                     file_name: diff_path})

            with pytest.raises(cat.IllegalAddAttempt):
                a_catalog.add_paths({new_file_name: new_file_path,
                                     file_name: diff_path})

            # ensure we still have expected results
            with pytest.raises(cat.FileNameNotFound):
                _ = a_catalog.get_path(new_file_name)
            assert len(a_catalog) == len(file_specs)
            assert a_catalog.get_path(file_name) == path

    def test_file_catalog_del_paths_with_list_of_file_specs(
            self,
            capsys: Any,
            file_specs: cat.FileSpecs) -> None:
        """test_file_catalog delete paths with lists of file_specs.

        Args:
            capsys: instance of the capture sys fixture
            file_specs: the list of file names and paths to use

        """
        # all cases will expect zero entries
        expected = 'FileCatalog()\n'

        a_catalog = cat.FileCatalog()  # start with empty catalog
        assert len(a_catalog) == 0
        print(a_catalog)
        assert capsys.readouterr().out == expected

        # attempt to delete paths from empty catalog - should be ok
        a_catalog.del_paths(file_specs)
        assert len(a_catalog) == 0
        print(a_catalog)
        assert capsys.readouterr().out == expected

        # add all paths to catalog
        a_catalog.add_paths(file_specs)
        assert len(a_catalog) == len(file_specs)
        print(a_catalog)
        # should not be empty
        assert capsys.readouterr().out != expected

        # delete all paths
        a_catalog.del_paths(file_specs)
        assert len(a_catalog) == 0
        print(a_catalog)
        assert capsys.readouterr().out == expected

        # try doing partial deletes
        a_catalog = cat.FileCatalog()

        for (file_name, path) in file_specs.items():
            # verify each loop has empty catalog
            assert len(a_catalog) == 0

            a_file_spec = {file_name: path}

            for i in range(2):
                a_catalog.add_paths(a_file_spec)
                assert a_catalog.get_path(file_name) == path
                assert len(a_catalog) == 1

                if i == 0:
                    # delete specific path
                    a_catalog.del_paths(a_file_spec)
                else:
                    # delete them all
                    a_catalog.del_paths(file_specs)

                assert len(a_catalog) == 0
                with pytest.raises(cat.FileNameNotFound):
                    _ = a_catalog.get_path(file_name)

            for i in range(2):
                a_catalog.add_paths(file_specs)
                assert a_catalog.get_path(file_name) == path
                assert len(a_catalog) == len(file_specs)

                if i == 0:
                    # delete specific path
                    a_catalog.del_paths(a_file_spec)
                    assert len(a_catalog) == len(file_specs) - 1
                    with pytest.raises(cat.FileNameNotFound):
                        _ = a_catalog.get_path(file_name)
                else:
                    # delete them all
                    a_catalog.del_paths(file_specs)
                    assert len(a_catalog) == 0
                    with pytest.raises(cat.FileNameNotFound):
                        _ = a_catalog.get_path(file_name)

    def test_file_catalog_del_paths_exceptions(
            self,
            capsys: Any,
            file_specs: cat.FileSpecs) -> None:
        """test_file_catalog add_paths exceptions.

        Args:
            capsys: instance of the capture sys fixture
            file_specs: the list of file names and paths to use

        """
        # instantiate a catalog
        a_catalog = cat.FileCatalog(file_specs)
        assert len(a_catalog) == len(file_specs)

        # try to delete with non-dict
        delete_list_of_tuples = list(file_specs.items())
        with pytest.raises(cat.FileSpecIncorrect):
            a_catalog.del_paths(delete_list_of_tuples)  # type: ignore

        # try to delete with non-str file name
        with pytest.raises(cat.FileSpecIncorrect):
            a_catalog.del_paths({42: Path('path_dir/path1')})  # type: ignore

        # try to delete with non-path path
        with pytest.raises(cat.FileSpecIncorrect):
            a_catalog.del_paths({'file1': 'path_dir/path1'})  # type: ignore

        for (file_name, path) in file_specs.items():
            # the number of entries should remain the same throughout
            # tests
            assert len(a_catalog) == len(file_specs)

            # we should always find the entries we added earlier
            assert a_catalog.get_path(file_name) == path

            file_name2 = 'filename2'
            diff_path = Path('different/path')

            # should get del exception with same file name but different
            # path

            with pytest.raises(cat.IllegalDelAttempt):
                a_catalog.del_paths({file_name: diff_path})

            # ensure we still have expected results
            assert len(a_catalog) == len(file_specs)
            assert a_catalog.get_path(file_name) == path

            # try deleting two entries, one good and one bad

            with pytest.raises(cat.IllegalDelAttempt):
                a_catalog.del_paths({file_name2: path,
                                     file_name: diff_path})

            # ensure we still have expected results
            assert len(a_catalog) == len(file_specs)
            assert a_catalog.get_path(file_name) == path

    def test_save_and_load_file_catalog(
            self,
            tmp_path: Path,
            capsys: Any,
            file_specs: cat.FileSpecs) -> None:
        """test_file_catalog add_paths exceptions.

        Args:
            tmp_path: instance of the temporary path fixture
            capsys: instance of the capture sys fixture
            file_specs: the list of file names and paths to use

        """
        catalog = cat.FileCatalog(file_specs)
        assert len(catalog) == len(file_specs)
        for file_name, path in file_specs.items():
            assert catalog.get_path(file_name) == path

        # set up temp file
        temp_cat_dir = tmp_path / 'sub'
        temp_cat_dir.mkdir()
        saved_cat_path = temp_cat_dir / 'saved_cat.csv'

        # save catalog to temp file
        catalog.save_catalog(saved_cat_path)

        # load catalog from temp file
        loaded_catalog = cat.FileCatalog.load_catalog(saved_cat_path)
        assert len(loaded_catalog) == len(file_specs)
        for file_name, path in file_specs.items():
            assert loaded_catalog.get_path(file_name) == path
