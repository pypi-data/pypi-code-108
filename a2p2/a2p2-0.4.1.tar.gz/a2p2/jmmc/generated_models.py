from .models import _model

def punct( name, flux_weight=1.0, x=0.0, y=0.0,  output_mode=None):
    """ Returns the Fourier transform of a punctual object (Dirac function) at coordinates (X,Y)
(milliarcsecond).

FLUX_WEIGHT is the intensity coefficient. FLUX_WEIGHT=1 means total energy is 1. """

    return _model({"flux_weight" : flux_weight, "x" : x, "y" : y, "name":name, "type":"punct"}, output_mode)

def disk( name, flux_weight=1.0, x=0.0, y=0.0, diameter=0.0,  output_mode=None):
    """ Returns the Fourier transform of a normalized uniform disk of diameter DIAMETER
(milliarcsecond) and centered at coordinates (X,Y) (milliarcsecond).

FLUX_WEIGHT is the intensity coefficient. FLUX_WEIGHT=1 means total energy is 1.

The function returns an error if DIAMETER is negative. """

    return _model({"flux_weight" : flux_weight, "x" : x, "y" : y, "diameter" : diameter, "name":name, "type":"disk"}, output_mode)

def elong_disk( name, flux_weight=1.0, x=0.0, y=0.0, minor_axis_diameter=0.0, elong_ratio=1.0, major_axis_pos_angle=0.0,  output_mode=None):
    """ Returns the Fourier transform of a normalized ellipse centered at coordinates (X,Y)
(milliarcsecond) with a ratio ELONG_RATIO between the major diameter and the minor one
MINOR_AXIS_DIAMETER, turned from the positive vertical semi-axis (i.e. North direction)
with angle MAJOR_AXIS_POS_ANGLE, in degrees, towards to the positive horizontal semi-axis
(i.e. East direction). (the elongation is along the major_axis)

For avoiding degenerescence, the domain of variation of MAJOR_AXIS_POS_ANGLE is 180
degrees, for ex. from 0 to 180 degrees.

ELONG_RATIO = major_axis / minor_axis
FLUX_WEIGHT is the intensity coefficient. FLUX_WEIGHT=1 means total energy is 1.

The function returns an error if MINOR_AXIS_DIAMETER is negative or if ELONG_RATIO is
smaller than 1. """

    return _model({"flux_weight" : flux_weight, "x" : x, "y" : y, "minor_axis_diameter" : minor_axis_diameter, "elong_ratio" : elong_ratio, "major_axis_pos_angle" : major_axis_pos_angle, "name":name, "type":"elong_disk"}, output_mode)

def flatten_disk( name, flux_weight=1.0, x=0.0, y=0.0, major_axis_diameter=0.0, flatten_ratio=1.0, minor_axis_pos_angle=0.0,  output_mode=None):
    """ Returns the Fourier transform of a normalized ellipse centered at coordinates (X,Y)
(milliarcsecond) with a ratio FLATTEN_RATIO between the major diameter
MAJOR_AXIS_DIAMETER and the minor one, turned from the positive vertical semi-axis
(i.e. North direction) with angle MINOR_AXIS_POS_ANGLE, in degrees, towards to the
positive horizontal semi-axis (i.e. East direction). (the flattening is along the minor_axis)

For avoiding degenerescence, the domain of variation of MINOR_AXIS_POS_ANGLE is 180
degrees, for ex. from 0 to 180 degrees.

FLATTEN_RATIO = major_axis / minor_axis
FLUX_WEIGHT is the intensity coefficient. FLUX_WEIGHT=1 means total energy is 1.

The function returns an error if MAJOR_AXIS_DIAMETER is negative or if FLATTEN_RATIO
is smaller than 1. """

    return _model({"flux_weight" : flux_weight, "x" : x, "y" : y, "major_axis_diameter" : major_axis_diameter, "flatten_ratio" : flatten_ratio, "minor_axis_pos_angle" : minor_axis_pos_angle, "name":name, "type":"flatten_disk"}, output_mode)

def circle( name, flux_weight=1.0, x=0.0, y=0.0, diameter=0.0,  output_mode=None):
    """ Returns the Fourier transform of a normalized uniform circle of diameter DIAMETER
(milliarcsecond) and centered at coordinates (X,Y) (milliarcsecond).

FLUX_WEIGHT is the intensity coefficient. FLUX_WEIGHT=1 means total energy is 1.

The function returns an error if DIAMETER is negative. """

    return _model({"flux_weight" : flux_weight, "x" : x, "y" : y, "diameter" : diameter, "name":name, "type":"circle"}, output_mode)

def ring( name, flux_weight=1.0, x=0.0, y=0.0, diameter=0.0, width=0.0,  output_mode=None):
    """ Returns the Fourier transform of a normalized uniform ring with internal diameter
DIAMETER (milliarcsecond) and external diameter DIAMETER + WIDTH centered at coordinates
(X,Y) (milliarcsecond).

FLUX_WEIGHT is the intensity coefficient. FLUX_WEIGHT=1 means total energy is 1.

The function returns an error if DIAMETER or WIDTH are negative. """

    return _model({"flux_weight" : flux_weight, "x" : x, "y" : y, "diameter" : diameter, "width" : width, "name":name, "type":"ring"}, output_mode)

def elong_ring( name, flux_weight=1.0, x=0.0, y=0.0, minor_internal_diameter=0.0, elong_ratio=1.0, width=0.0, major_axis_pos_angle=0.0,  output_mode=None):
    """ Returns the Fourier transform of a normalized uniform elongated ring centered at
coordinates (X,Y) (milliarcsecond). The sizes of the function in two orthogonal directions
are given by the narrowest internal diameter (MINOR_INTERNAL_DIAMETER) and by the ratio
ELONG_RATIO between the widest internal diameter and MINOR_INTERNAL_DIAMETER,
in the same way as for an ellipse (the elongation is along the major_axis) :

ELONG_RATIO = MAJOR_INTERNAL_DIAMETER / MINOR_INTERNAL_DIAMETER.
In the direction of MINOR_INTERNAL_DIAMETER, the external diameter is
MINOR_INTERNAL_DIAMETER + WIDTH. In the direction of the widest internal diameter,
the width is magnified by the ratio ELONG_RATIO, so that the external diameter is
the elongated MAJOR_INTERNAL_DIAMETER + WIDTH * ELONG_RATIO.
MAJOR_AXIS_POS_ANGLE is measured in degrees, from the positive vertical semi-axis
(i.e. North direction) towards to the positive horizontal semi-axis (i.e. East direction).
For avoiding degenerescence, the domain of variation of MAJOR_AXIS_POS_ANGLE is 180
degrees, for ex. from 0 to 180 degrees.

FLUX_WEIGHT is the intensity coefficient. FLUX_WEIGHT=1 means total energy is 1.

The function returns an error if MINOR_INTERNAL_DIAMETER is negative or if ELONG_RATIO
is smaller than 1. """

    return _model({"flux_weight" : flux_weight, "x" : x, "y" : y, "minor_internal_diameter" : minor_internal_diameter, "elong_ratio" : elong_ratio, "width" : width, "major_axis_pos_angle" : major_axis_pos_angle, "name":name, "type":"elong_ring"}, output_mode)

def flatten_ring( name, flux_weight=1.0, x=0.0, y=0.0, major_internal_diameter=0.0, flatten_ratio=1.0, width=0.0, minor_axis_pos_angle=0.0,  output_mode=None):
    """ Returns the Fourier transform of a normalized uniform flattened ring centered at
coordinates (X,Y) (milliarcsecond). The sizes of the function in two orthogonal directions
are given by the widest internal diameter (MAJOR_INTERNAL_DIAMETER) and by the ratio
FLATTEN_RATIO between MAJOR_INTERNAL_DIAMETER and the narrowest internal diameter,
in the same way as for an ellipse (the flattening is along the minor axis) :

FLATTEN_RATIO = MAJOR_INTERNAL_DIAMETER / MINOR_INTERNAL_DIAMETER.
In the direction of MAJOR_INTERNAL_DIAMETER, the external diameter is
MAJOR_INTERNAL_DIAMETER + WIDTH. In the direction of the narrowest internal diameter,
the width is decreased by the ratio FLATTEN_RATIO, so that the external diameter is
the flattened MINOR_INTERNAL_DIAMETER + WIDTH / FLATTEN_RATIO.
MINOR_AXIS_POS_ANGLE is measured in degrees, from the positive vertical semi-axis
(i.e. North direction) towards to the positive horizontal semi-axis (i.e. East direction).
For avoiding degenerescence, the domain of variation of MINOR_AXIS_POS_ANGLE is 180
degrees, for ex. from 0 to 180 degrees.

FLUX_WEIGHT is the intensity coefficient. FLUX_WEIGHT=1 means total energy is 1.

The function returns an error if MAJOR_INTERNAL_DIAMETER is negative or if FLATTEN_RATIO
is smaller than 1. """

    return _model({"flux_weight" : flux_weight, "x" : x, "y" : y, "major_internal_diameter" : major_internal_diameter, "flatten_ratio" : flatten_ratio, "width" : width, "minor_axis_pos_angle" : minor_axis_pos_angle, "name":name, "type":"flatten_ring"}, output_mode)

def gaussian( name, flux_weight=1.0, x=0.0, y=0.0, fwhm=0.0,  output_mode=None):
    """ Returns the Fourier transform of a normalized gaussian with given FWHM (milliarcsecond)
centered at coordinates (X,Y) (milliarcsecond).

FLUX_WEIGHT is the intensity coefficient. FLUX_WEIGHT=1 means total energy is 1.

The function returns an error if FWHM is negative. """

    return _model({"flux_weight" : flux_weight, "x" : x, "y" : y, "fwhm" : fwhm, "name":name, "type":"gaussian"}, output_mode)

def elong_gaussian( name, flux_weight=1.0, x=0.0, y=0.0, minor_axis_fwhm=0.0, elong_ratio=1.0, major_axis_pos_angle=0.0,  output_mode=None):
    """ Returns the Fourier transform of a normalized elongated gaussian centered at coordinates
(X,Y) (milliarcsecond). The sizes of the function in two orthogonal directions are given by
the narrowest FWHM (MINOR_AXIS_FWHM) and by the ratio ELONG_RATIO between the largest
FWHM (MAJOR_AXIS_FWHM) and the MINOR_AXIS_FWHM, in the same way as for an ellipse
(the elongation is along the major_axis) :

ELONG_RATIO = MAJOR_AXIS_FWHM / MINOR_AXIS_FWHM.
MAJOR_AXIS_POS_ANGLE is measured in degrees, from the positive vertical semi-axis
(i.e. North direction) towards to the positive horizontal semi-axis (i.e. East direction).
For avoiding degenerescence, the domain of variation of MAJOR_AXIS_POS_ANGLE is 180
degrees, for ex. from 0 to 180 degrees.

FLUX_WEIGHT is the intensity coefficient. FLUX_WEIGHT=1 means total energy is 1.

The function returns an error if MINOR_AXIS_FWHM is negative or if ELONG_RATIO
is smaller than 1. """

    return _model({"flux_weight" : flux_weight, "x" : x, "y" : y, "minor_axis_fwhm" : minor_axis_fwhm, "elong_ratio" : elong_ratio, "major_axis_pos_angle" : major_axis_pos_angle, "name":name, "type":"elong_gaussian"}, output_mode)

def flatten_gaussian( name, flux_weight=1.0, x=0.0, y=0.0, major_axis_fwhm=0.0, flatten_ratio=1.0, minor_axis_pos_angle=0.0,  output_mode=None):
    """ Returns the Fourier transform of a normalized flattened gaussian centered at coordinates
(X,Y) (milliarcsecond). The sizes of the function in two orthogonal directions are given by
the largest FWHM (MAJOR_AXIS_FWHM) and by the ratio FLATTEN_RATIO between the largest
FWHM (MAJOR_AXIS_FWHM) and the MINOR_AXIS_FWHM, in the same way as for an ellipse
(the flattening is along the minor_axis) :

FLATTEN_RATIO = MAJOR_AXIS_FWHM / MINOR_AXIS_FWHM.
MINOR_AXIS_POS_ANGLE is measured in degrees, from the positive vertical semi-axis
(i.e. North direction) towards to the positive horizontal semi-axis (i.e. East direction).
For avoiding degenerescence, the domain of variation of MINOR_AXIS_POS_ANGLE is 180
degrees, for ex. from 0 to 180 degrees.

FLUX_WEIGHT is the intensity coefficient. FLUX_WEIGHT=1 means total energy is 1.

The function returns an error if MAJOR_AXIS_FWHM is negative or if FLATTEN_RATIO
is smaller than 1. """

    return _model({"flux_weight" : flux_weight, "x" : x, "y" : y, "major_axis_fwhm" : major_axis_fwhm, "flatten_ratio" : flatten_ratio, "minor_axis_pos_angle" : minor_axis_pos_angle, "name":name, "type":"flatten_gaussian"}, output_mode)

def limb_quadratic( name, flux_weight=1.0, x=0.0, y=0.0, diameter=0.0, a1_coeff=0.0, a2_coeff=0.0,  output_mode=None):
    """ Returns the Fourier transform of a center-to-limb darkened disk of diameter DIAMETER
(milliarcsecond) centered at coordinates (X,Y) (milliarcsecond).

The brightness distribution o, if expressed versus mu, the cosine of the azimuth of
a surface element of the star, follows a quadratic law of coefficients
A1_COEFF, A2_COEFF ([-1,1]), and is normalized for mu = 1 (center of the star).
o(mu) = 1 -A1_COEFF(1-mu) - A2_COEFF(1-mu)^2.

FLUX_WEIGHT is the intensity coefficient. FLUX_WEIGHT=1 means total energy is 1.

The function returns an error if DIAMETER is negative or if A1_COEFF or A2_coeff is
outside bounds [-1,1] """

    return _model({"flux_weight" : flux_weight, "x" : x, "y" : y, "diameter" : diameter, "a1_coeff" : a1_coeff, "a2_coeff" : a2_coeff, "name":name, "type":"limb_quadratic"}, output_mode)

