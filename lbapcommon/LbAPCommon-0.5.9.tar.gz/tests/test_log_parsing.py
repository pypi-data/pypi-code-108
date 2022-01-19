###############################################################################
# (c) Copyright 2020 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

from os.path import dirname, join

from LbAPCommon.validators import explain_log


def _load_log(filename):
    with open(join(dirname(__file__), "example-logs", filename), "rt") as fp:
        return fp.read()


def test_missing_shared_library():
    text = _load_log("error-missing-shared-library.log")
    explanations, suggestions, errors = explain_log(text)

    assert len(errors) == 1
    error_message, line_numbers = errors.pop()
    assert "HEP_OSlibs" in error_message
    assert line_numbers is None


def test_illegal_instruction():
    text = _load_log("error-illegal-instruction.log")
    explanations, suggestions, errors = explain_log(text)

    assert len(errors) == 1
    error_message, line_numbers = errors.pop()
    assert "compiled with instructions" in error_message
    assert line_numbers is None


def test_platform_unsupported():
    text = _load_log("error-platform-unsupported.log")
    explanations, suggestions, errors = explain_log(text)

    assert len(errors) == 1
    error_message, line_numbers = errors.pop()
    assert "lb-describe-platform" in error_message
    assert line_numbers is None


def test_related_info_missing():
    text = _load_log("error-related-info-missing.log")
    explanations, suggestions, errors = explain_log(text)

    # Errors
    (relinfo_error,) = sorted(errors)

    error_message, line_numbers = relinfo_error
    assert "RelatedInfo" in error_message
    assert len(line_numbers) == 54

    # Suggestions
    (cal_mc_suggest,) = sorted(suggestions)

    error_message, line_numbers = cal_mc_suggest
    assert "calorimeter MC-truth" in error_message
    assert len(line_numbers) == 9

    # Suggestions
    (histogram_not_set,) = sorted(explanations)

    error_message, line_numbers = histogram_not_set
    assert "Histograms are not being saved" in error_message
    assert "harmless" in error_message
    assert line_numbers == [4678]


def test_failed_to_read_file():
    text = _load_log("error-failed-to-read-file.log")
    explanations, suggestions, errors = explain_log(text)

    assert len(errors) == 1
    error_message, line_numbers = errors.pop()
    assert "error accessing the input" in error_message
    assert line_numbers == [1085]


def test_good_davinci_38():
    text = _load_log("good-DaVinci_00110296_00000038_1.log")
    explanations, suggestions, errors = explain_log(text)

    assert errors == []


def test_good_davinci_194():
    text = _load_log("good-DaVinci_00110296_00000194_1.log")
    explanations, suggestions, errors = explain_log(text)

    assert errors == []


def test_good_gauss_11():
    text = _load_log("good-Gauss_00104988_00000011_1.log")
    explanations, suggestions, errors = explain_log(text)

    assert errors == []
