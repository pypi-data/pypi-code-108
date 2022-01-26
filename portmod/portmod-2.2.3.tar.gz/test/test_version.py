# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Tests the version comparison system
"""

from portmod.util import get_max_version
from portmodlib.atom import version_gt


def test_simple_version():
    """Tests extremely simple version comparison"""
    v_b = "2.0"
    v_a = "1.0"
    assert get_max_version([v_a, v_b]) == v_b


def gt(atom1, atom2):
    """Tests that atom1 is considered greater than atom2"""
    assert version_gt(atom1, atom2)
    assert not version_gt(atom2, atom1)
    assert get_max_version([atom1, atom2]) == atom1
    assert get_max_version([atom2, atom1]) == atom1


def test_suffix():
    """Tests that suffixed versions come before full versions"""
    assert (
        get_max_version(["2.0_alpha", "2.0_beta", "2.0_pre", "2.0_rc", "2.0"]) == "2.0"
    )


def test_suffix_p():
    """Tests that p suffixed versions come after full versions"""
    gt("2.0_p1", "2.0")
    gt("2.0_alpha_p1", "2.0_alpha")


def test_suffix_endings():
    """Tests that p suffixed versions with integer endings order correctly"""
    gt("2.0_p2", "2.0_p1")
    gt("2.0_alpha2", "2.0_alpha1")
    gt("2.0_beta1", "2.0_alpha2")
    gt("2.0_alpha1", "2.0_alpha")
    gt("2.0_alpha1_beta2", "2.0_alpha")
    gt("2.0_alpha", "2.0_alpha_beta2")


def test_letter():
    """
    Tests that letter versions come after non-letter versions, increase in order
    and take precedence over suffixes, but not numeric components
    """
    gt("2.0a", "2.0")
    gt("2.0b", "2.0a")
    gt("2.0b_alpha", "2.0a")
    gt("2.1a", "2.0b")


def test_revision():
    """
    Tests that revisions have the lowest precedence and increase in order
    """
    gt("2.0-r1", "2.0")
    gt("2.0-r2", "2.0-r1")
    gt("2.0a-r1", "2.0-r2")
    gt("2.0_beta-r1", "2.0_alpha-r2")


def test_different_version_lengths():
    """
    Tests that having more version components is considered a greater version if the numbers are otherwise equal
    """
    gt("2.0.1", "2.0")
    gt("2.1", "2.0.1")
    gt("2.0.1_alpha", "2.0_p1-r1")
