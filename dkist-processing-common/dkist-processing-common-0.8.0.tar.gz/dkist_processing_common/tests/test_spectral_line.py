import pytest

from dkist_processing_common.models.spectral_line import find_associated_line
from dkist_processing_common.models.spectral_line import SpectralLine

line_a = SpectralLine(name="A", wavelength=10.0, wavemin=9.0, wavemax=11.0)
line_b = SpectralLine(name="B", wavelength=15.0, wavemin=14.5, wavemax=15.5)
line_c = SpectralLine(name="C", wavelength=17.0, wavemin=15.1, wavemax=20.0)


def test_spectral_line():
    """
    :Given: a valid SpectralLine object
    :When: examining its properties
    :Then: the properties have the expected values
    """
    assert line_a.name == "A"
    assert line_a.wavelength == 10.0
    assert line_a.wavemin == 9.0
    assert line_a.wavemax == 11.0
    assert line_a.linewidth == 2


def test_invalid_spectral_line():
    """
    :Given: an invalid SpectralLine object with wavemax < wavemin
    :When: instantiating the object
    :Then: an error is raised
    """
    with pytest.raises(ValueError):
        SpectralLine(name="name", wavelength=15.0, wavemin=14.0, wavemax=13.0)


def test_find_associated_line():
    """
    :Given: a collection of SpectralLines and a wavelength contained within one of them
    :When: searching for the associated line
    :Then: the correct line is found
    """
    associated_line = find_associated_line(wavelength=14.75, lines=[line_a, line_b])
    assert associated_line == "B"


def test_find_associated_line_too_many_matches():
    """
    :Given: a collection of SpectralLines and a wavelength contained within *TWO* of them
    :When: searching for the associated line
    :Then: an error is raised
    """
    with pytest.raises(ValueError):
        find_associated_line(wavelength=15.25, lines=[line_a, line_b, line_c])


def test_find_associated_line_no_matches():
    """
    :Given: a collection of SpectralLines and a wavelength contained within *NONE* of them
    :When: searching for the associated line
    :Then: an error is raised
    """
    with pytest.raises(ValueError):
        find_associated_line(wavelength=21.0, lines=[line_a, line_b, line_c])
