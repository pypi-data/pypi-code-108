"""Tests for mode masks on detectors."""

import numpy as np
import pytest

from finesse import Model
from finesse.analysis.actions import Noxaxis
from finesse.utilities.homs import make_modes, remove_modes


@pytest.fixture
def fp_cavity_model():
    IFO = Model()
    IFO.parse(
        """
        l L0 P=1
        s s0 L0.p1 ITM.p1

        m ITM R=0.9 T=0.1 Rc=-2
        s sc ITM.p2 ETM.p1 L=1
        m ETM R=0.9 T=0.1 Rc=2

        pd P_total ETM.p2.o
        pd P_masked ETM.p2.o

        cav FP ITM.p2
        """
    )
    IFO.ITM.Rcy = IFO.ITM.Rcx.ref
    IFO.ETM.Rcy = IFO.ETM.Rcx.ref

    return IFO


def test_masked_tem00_gives_null(fp_cavity_model: Model):
    """Test that masking the 00 mode for a model with no mismatches nor misalignments
    gives zero response in the masked power detector."""
    IFO = fp_cavity_model

    IFO.modes("even", maxtem=4)

    # Mask the 00 mode
    IFO.P_masked.mask = ["00"]

    # Check the mask itself has been interpreted correctly
    assert np.all(IFO.P_masked.mask == [[0, 0]])

    out = IFO.run(Noxaxis())

    # No mismatches nor misalignments present so masking
    # HG00 should give a null response
    assert out["P_masked"] == 0
    # Impedance matched so total transmitted power should
    # equal input power
    assert out["P_total"] == pytest.approx(IFO.L0.P.value)


def test_masked_tem00_gives_null_ccd_image(fp_cavity_model: Model):
    """Test that masking the 00 mode for a model with no mismatches nor misalignments
    gives zero response in the masked CCD."""
    IFO = fp_cavity_model

    Npts = 100
    IFO.modes("even", maxtem=4)
    IFO.parse(f"ccd CCD ETM.p2.o xlim=5 ylim=5 npts={Npts}")

    # Mask the 00 mode
    IFO.CCD.mask = ["00"]

    # Check the mask itself has been interpreted correctly
    assert np.all(IFO.CCD.mask == [[0, 0]])

    out = IFO.run(Noxaxis())

    # No mismatches nor misalignments present so masking
    # HG00 should give an image of zeros
    assert np.all(out["CCD"] == np.zeros((Npts, Npts)))


def test_masked_tem00_gives_null_field_image(fp_cavity_model: Model):
    """Test that masking the 00 mode for a model with no mismatches nor misalignments
    gives zero response in the masked FieldCamera."""
    IFO = fp_cavity_model

    Npts = 100
    IFO.modes("even", maxtem=4)
    IFO.parse(f"fcam FCAM ETM.p2.o f=0 xlim=5 ylim=5 npts={Npts}")

    # Mask the 00 mode
    IFO.FCAM.mask = ["00"]

    # Check the mask itself has been interpreted correctly
    assert np.all(IFO.FCAM.mask == [[0, 0]])

    out = IFO.run(Noxaxis())

    # No mismatches nor misalignments present so masking
    # HG00 should give an image of complex zeros
    assert np.all(out["FCAM"] == np.zeros((Npts, Npts), dtype=np.complex128))


def test_masked_even_order_tem_mismatched_file_gives_null(fp_cavity_model: Model):
    """Test that masking all even-order modes for a mismatched model gives zero response
    in the masked power detector."""
    IFO = fp_cavity_model

    IFO.modes("even", maxtem=4)
    # Add another mode so that size of P_masked.mask is
    # not same as number of HOMs in the model
    IFO.include_modes("01")

    # Create mismatch originating at L0 of 5% in w0, 5% in z
    IFO.create_mismatch(IFO.L0.p1.o, w0_mm=5, z_mm=5)

    # Mask all even order modes
    IFO.P_masked.select_mask("even")

    assert np.all(IFO.P_masked.mask == make_modes("even", maxtem=4))

    out = IFO.run(Noxaxis())

    # Only mismatch present (no misalignment) so masking all
    # even order modes on P_masked should give a null response
    assert out["P_masked"] == 0


def test_masked_x_modes_itmyaw_file_gives_null(fp_cavity_model: Model):
    """Test that masking all x modes for a model with yawed mirror gives zero response
    in the masked power detector."""
    IFO = fp_cavity_model

    # Apply a yaw misalignment to ITM of 1% of the cavity divergence angle
    IFO.ITM.xbeta = IFO.FP.qx.divergence / 100

    IFO.modes("x", maxtem=4)
    # Add another mode so that size of P_masked.mask is
    # not same as number of HOMs in the model
    IFO.include_modes("02")

    # Mask all x order modes
    IFO.P_masked.select_mask("x")

    assert np.all(IFO.P_masked.mask == make_modes("x", maxtem=4))

    out = IFO.run(Noxaxis())

    # Only yaw misalignment present so masking all yaw modes
    # on P_masked should give a null response
    assert out["P_masked"] == 0


def test_masked_y_modes_itmpitch_file_gives_null(fp_cavity_model: Model):
    """Test that masking all x modes for a model with yawed mirror gives zero response
    in the masked power detector."""
    IFO = fp_cavity_model

    # Apply a pitch misalignment to ITM of 1% of the cavity divergence angle
    IFO.ITM.ybeta = IFO.FP.qx.divergence / 100

    IFO.modes("y", maxtem=4)
    # Add another mode so that size of P_masked.mask is
    # not same as number of HOMs in the model
    IFO.include_modes("20")

    # Mask all x order modes
    IFO.P_masked.select_mask("y")

    assert np.all(IFO.P_masked.mask == make_modes("y", maxtem=4))

    out = IFO.run(Noxaxis())

    # Only pitch misalignment present so masking all pitch modes
    # on P_masked should give a null response
    assert out["P_masked"] == 0


def test_masked_tem00_mismatched_file(fp_cavity_model: Model):
    """Test that masking the 00 mode for a mismatched model gives response equal to abs
    sum sqd of HOM field amplitudes."""
    IFO = fp_cavity_model

    IFO.modes("even", maxtem=4)
    for n, m in IFO.homs:
        IFO.parse(f"ad ad{n}{m} ETM.p2.o 0 n={n} m={m}")

    # Create mismatch originating at L0 of 5% in w0, 5% in z
    IFO.create_mismatch(IFO.L0.p1.o, w0_mm=5, z_mm=5)

    # Mask the 00 mode
    IFO.P_masked.mask = ["00"]
    IFO.ad00.mask = ["00"]

    assert np.all(IFO.P_masked.mask == [[0, 0]])
    assert np.all(IFO.ad00.mask == [[0, 0]])

    out = IFO.run(Noxaxis())
    hom_amp_sum = 0
    for n, m in IFO.homs:
        if not n and not m:
            continue

        hom_amp_sum += np.abs(out[f"ad{n}{m}"] ** 2)

    # Only mismatch present so masking 00 mode means
    # P_masked should equal abs sum sqd of HOm fields
    assert out["P_masked"] == pytest.approx(hom_amp_sum)

    # Masking the mode itself on an ad should always give zero
    assert out["ad00"] == 0 + 0j


def test_masked_even_modes_mismatched_file_detect_tem00(fp_cavity_model: Model):
    """Test that masking all modes but 00 for a mismatched model gives response equal to
    abs sqd of a00 field."""
    IFO = fp_cavity_model

    IFO.modes("even", maxtem=4)
    IFO.parse("ad ad00 ETM.p2.o 0 n=0 m=0")

    # Create mismatch originating at L0 of 5% in w0, 5% in z
    IFO.create_mismatch(IFO.L0.p1.o, w0_mm=5, z_mm=5)

    # Mask all but 00 mode
    IFO.P_masked.select_mask("even", exclude="00")

    mask = make_modes("even", maxtem=4)
    mask = remove_modes(mask, "00")
    assert np.all(IFO.P_masked.mask == mask)

    out = IFO.run(Noxaxis())

    # Only mismatch present so masking even modes means
    # P_masked should equal abs sqd of 00 field
    assert out["P_masked"] == pytest.approx(np.abs(out["ad00"]) ** 2)


def test_masking_all_modes_raises_exception(fp_cavity_model: Model):
    """Test that masking all modes on a detector raises a RuntimeError."""
    IFO = fp_cavity_model

    IFO.modes("even", maxtem=4)

    # Mask all modes...
    IFO.P_masked.select_mask("even")

    # ... and check that this raises an error
    with pytest.raises(RuntimeError):
        IFO.run(Noxaxis())


def test_masking_non_existent_mode_raises_exception(fp_cavity_model: Model):
    """Test that masking modes which are not present in the model raises a
    RuntimeError."""
    IFO = fp_cavity_model

    IFO.modes("even", maxtem=4)

    # Mask modes which aren't in the model...
    IFO.P_masked.select_mask(["01", "33"])

    # ... and check that this raises an error
    with pytest.raises(RuntimeError):
        IFO.run(Noxaxis())


def test_masking_ad_single_field_mode_logs_warning(fp_cavity_model: Model):
    """Test that applying mask to the mode that an amplitude detector is detecting logs
    a warning and outputs complex zero."""
    IFO = fp_cavity_model

    IFO.modes(maxtem=2)
    IFO.parse("ad ad00 ETM.p2.o f=0 n=0 m=0")

    IFO.ad00.mask = ["00"]

    with pytest.warns(
        UserWarning, match=r"This will always return values of complex zero"
    ):
        out = IFO.run(Noxaxis())

    assert out["ad00"] == complex(0, 0)


def test_masking_ad_single_field_mode_not_detected_logs_warning(fp_cavity_model: Model):
    """Test that applying mask to the mode that an amplitude detector is not detecting
    logs a warning."""
    IFO = fp_cavity_model

    IFO.modes(maxtem=2)
    IFO.parse("ad ad00 ETM.p2.o f=0 n=0 m=0")

    IFO.ad00.mask = ["01"]

    with pytest.warns(UserWarning, match=r"Mask applied to 'ad00' has no effect"):
        IFO.run(Noxaxis())


# TODO (sjr) Above covers masks on pd0, CCD, ad single field. Need to
#            add mode mask tests for:
#                - ad in multi-field mode (i.e. n=m=None)
#                - pd1 and pd2
