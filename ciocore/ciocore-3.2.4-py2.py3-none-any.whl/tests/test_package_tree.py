""" test package_tree

   isort:skip_file
"""
import json
import os
import random
import sys
import unittest

from ciocore import package_tree as ptree
 
JSON_FILENAME = os.path.join(os.path.dirname(__file__) , "fixtures", "sw_packages.json")
with open(JSON_FILENAME, 'r') as content:
    packages_json = json.load(content)["data"]
 
SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)


class RemoveUnreachableTest(unittest.TestCase):

    def test_single_valid_tree_unchanged(self):
        paths = ["a", "a/b", "a/b/c"]
        results = ptree.remove_unreachable(paths)
        self.assertEqual(results, paths)

    def test_many_valid_trees_unchanged(self):
        paths = ["a", "a/b", "a/b/c", "b", "b/b", "b/b/c", "c", "c/b", "c/b/c"]
        results = ptree.remove_unreachable(paths)
        self.assertEqual(results, paths)

    def test_single_invalid_tree_culled_leaf(self):
        paths = ["a", "a/b", "b/b/c"]
        results = ptree.remove_unreachable(paths)
        self.assertEqual(results, ["a", "a/b"])

    def test_single_invalid_tree_culled_below(self):
        paths = ["a", "b/b", "a/b/c"]
        results = ptree.remove_unreachable(paths)
        self.assertEqual(results, ["a"])

    def test_multiple_invalid_tree_culled(self):
        paths = ["a", "a/b", "a/b/c", "b", "b/b", "b/b/c", "d", "c/b", "c/b/c"]
        results = ptree.remove_unreachable(paths)
        self.assertEqual(
            results, [
                "a", "a/b", "a/b/c", "b", "b/b", "b/b/c", "d"])

    def test_random_input_order(self):
        paths = ["a", "a/b", "a/b/c", "b", "b/b", "b/b/c", "d", "c/b", "c/b/c"]
        random.shuffle(paths)
        results = ptree.remove_unreachable(paths)
        self.assertEqual(
            results, [
                "a", "a/b", "a/b/c", "b", "b/b", "b/b/c", "d"])


class ToNameTest(unittest.TestCase):

    def test_major_only(self):
        pkg = {
            "product": "foo-bar",
            "major_version": "1",
            "minor_version": "",
            "release_version": "",
            "build_version": ""
        }
        expected = "foo-bar 1"
        self.assertEqual(ptree.to_name(pkg), expected)

    def test_major_minor(self):
        pkg = {
            "product": "foo-bar",
            "major_version": "1",
            "minor_version": "3",
            "release_version": "",
            "build_version": ""
        }
        expected = "foo-bar 1.3"
        self.assertEqual(ptree.to_name(pkg), expected)

    def test_major_minor_release(self):
        pkg = {
            "product": "foo-bar",
            "major_version": "1",
            "minor_version": "3",
            "release_version": "62",
            "build_version": ""
        }
        expected = "foo-bar 1.3.62"
        self.assertEqual(ptree.to_name(pkg), expected)

    def test_major_minor_release_build(self):
        pkg = {
            "product": "foo-bar",
            "major_version": "1",
            "minor_version": "3",
            "release_version": "62",
            "build_version": "876"
        }
        expected = "foo-bar 1.3.62.876"
        self.assertEqual(ptree.to_name(pkg), expected)


class SoftwareDataInitTest(unittest.TestCase):

    def test_smoke(self):
        pt = ptree.PackageTree([])
        self.assertIsInstance(pt, ptree.PackageTree)

    def test_init_with_product(self):
        pt = ptree.PackageTree(packages_json, product="houdini")
        self.assertEqual(len(pt.tree["children"]), 2)
        pt = ptree.PackageTree(packages_json, product="maya-io")
        self.assertEqual(len(pt.tree["children"]), 9)

    def test_init_with_no_product(self):
        pt = ptree.PackageTree(packages_json)
        self.assertEqual(len(pt.tree["children"]), 77)

    def test_init_with_sub_product(self):
        pt = ptree.PackageTree(
            packages_json,
            product="arnold-houdini")
        self.assertEqual(len(pt.tree["children"]), 4)


class SoftwareDataFindByKeysTest(unittest.TestCase):

    def setUp(self):
        self.pt = ptree.PackageTree(packages_json, product="houdini")

    def test_find_host_by_keys(self):
        keys = {
            'product': 'houdini',
            'major_version': '16',
            'minor_version': '5',
            'release_version': '323',
            'build_version': '',
            'plugin_host_product': '',
            'plugin_host_version': ''
        }
        pkg = self.pt.find_by_keys(**keys)
        self.assertEqual(pkg["product"], 'houdini')
        self.assertEqual(pkg["major_version"], '16')
        self.assertEqual(pkg["minor_version"], '5')
        self.assertEqual(pkg["release_version"], '323')

    def test_find_leaf_by_keys(self):
        keys = {
            'product': 'al-shaders',
            'major_version': '1',
            'minor_version': '1',
            'release_version': '',
            'build_version': '',
            'plugin_host_product': '',
            'plugin_host_version': ''
        }
        pkg = self.pt.find_by_keys(**keys)
        self.assertEqual(pkg["product"], 'al-shaders')
        self.assertEqual(pkg["major_version"], '1')
        self.assertEqual(pkg["minor_version"], '1')

    def test_find_nonexistent_package_returns_none(self):
        keys = {
            'product': 'arnold-houdini',
            'major_version': '7',
            'minor_version': '1',
            'release_version': '',
            'build_version': '',
            'plugin_host_product': '',
            'plugin_host_version': ''
        }
        pkg = self.pt.find_by_keys(**keys)
        self.assertEqual(pkg, None)


class SoftwareDataFindByPathTest(unittest.TestCase):

    def setUp(self):
        self.pt = ptree.PackageTree(packages_json, product="houdini")

    def test_find_root_path(self):
        path = "houdini 16.0.736"
        pkg = self.pt.find_by_path(path)
        self.assertEqual(ptree.to_name(pkg), path)

    def test_find_leaf_path(self):
        path = "houdini 16.0.736/arnold-houdini 2.0.2.2/al-shaders 1.0"
        pkg = self.pt.find_by_path(path)
        self.assertEqual(ptree.to_name(pkg), "al-shaders 1.0")

    def test_find_nonexistent_path_return_none(self):
        path = "houdini 16.0.736/arnold-houdini 9.0.2.2"
        pkg = self.pt.find_by_path(path)
        self.assertEqual(pkg, None)

    def test_find_empty_path_return_none(self):
        path = ""
        pkg = self.pt.find_by_path(path)
        self.assertEqual(pkg, None)

    def test_find_none_path_return_none(self):
        path = None
        pkg = self.pt.find_by_path(path)
        self.assertEqual(pkg, None)


class FindByNameTest(unittest.TestCase):
    def setUp(self):
        self.pt = ptree.PackageTree(packages_json, product="houdini")

    def test_find_root(self):
        name = 'houdini 16.5.323'
        result = self.pt.find_by_name(name)
        self.assertEqual(ptree.to_name(result), name)

    def test_find_root_when_limit_1(self):
        name = 'houdini 16.5.323'
        result = self.pt.find_by_name(name, 1)
        self.assertEqual(ptree.to_name(result), name)

    def test_find_plugin_level(self):
        name = "arnold-houdini 2.0.2.2"
        result = self.pt.find_by_name(name)
        self.assertEqual(ptree.to_name(result), name)

    def test_find_plugin_level_high_limit(self):
        name = "arnold-houdini 2.0.2.2"
        result = self.pt.find_by_name(name, 2)
        self.assertEqual(ptree.to_name(result), name)

    def test_dont_find_plugin_level_when_limited(self):
        name = "arnold-houdini 2.0.2.2"
        result = self.pt.find_by_name(name, 1)
        self.assertEqual(result, None)


class SoftwareDataGetAllPathsTest(unittest.TestCase):

    def setUp(self):
        self.pt = ptree.PackageTree(packages_json, product="houdini")

    def test_get_all_paths_to_root(self):

        keys = {
            'product': 'houdini',
            'major_version': '16',
            'minor_version': '5',
            'release_version': '323',
            'build_version': '',
            'plugin_host_product': '',
            'plugin_host_version': ''
        }
        paths = self.pt.get_all_paths_to(**keys)
        self.assertTrue(
            'houdini 16.5.323' in paths)
        self.assertEqual(len(paths), 1)

    def test_get_all_paths_to_leaf(self):

        keys = {
            'product': 'al-shaders',
            'major_version': '1',
            'minor_version': '0',
            'release_version': '',
            'build_version': '',
            'plugin_host_product': '',
            'plugin_host_version': ''
        }
        paths = self.pt.get_all_paths_to(**keys)
        self.assertTrue(
            'houdini 16.0.736/arnold-houdini 2.0.1/al-shaders 1.0' in paths)
        self.assertEqual(len(paths), 2)

    def test_get_all_paths_to_nonexistent(self):

        keys = {
            'product': 'foo',
            'major_version': '1',
            'minor_version': '0',
            'release_version': '',
            'build_version': '',
            'plugin_host_product': '',
            'plugin_host_version': ''
        }
        paths = self.pt.get_all_paths_to(**keys)
        self.assertEqual(paths, [])


# TODO Test PackageTree#get_environment()


if __name__ == '__main__':
    unittest.main()
