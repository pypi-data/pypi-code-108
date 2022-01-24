import math

from magnumapi.cadata.StrandDefinition import StrandDefinition

strand_def = StrandDefinition(name='STR01',
                              d_strand=1.065,
                              f_cu_nocu=1.6,
                              rrr=70,
                              temp_ref=1.9,
                              b_ref=10,
                              j_c_at_b_ref_t_ref=1433.3,
                              dj_c_over_db=500.34,
                              comment='MB INNER                      ')


def test_get_magnum_to_roxie_dct():
    # arrange
    # act
    magnum_to_roxie_dct = strand_def.get_magnum_to_roxie_dct()

    # assert
    magnum_to_roxie_dct_ref = {'name': 'Name', 'd_strand': 'diam.', 'f_cu_nocu': 'cu/sc', 'rrr': 'RRR',
                               'temp_ref': 'Tref', 'b_ref': 'Bref', 'j_c_at_b_ref_t_ref': 'Jc@BrTr',
                               'dj_c_over_db': 'dJc/dB', 'comment': 'Comment'}
    assert magnum_to_roxie_dct_ref == magnum_to_roxie_dct


def test_compute_surface_cu():
    # arrange
    # act
    surface_cu = strand_def.compute_surface_cu()

    # assert
    surface_ref = math.pi * strand_def.d_strand ** 2 / 4
    f_nocu_ref = strand_def.f_cu_nocu / (1 + strand_def.f_cu_nocu)

    assert abs(surface_cu - surface_ref * f_nocu_ref) < 1e-6


def test_compute_surface_nocu():
    # arrange
    # act
    surface_nocu = strand_def.compute_surface_nocu()

    # assert
    surface_ref = math.pi * strand_def.d_strand ** 2 / 4
    f_nocu_ref = 1 / (1 + strand_def.f_cu_nocu)

    assert abs(surface_nocu - surface_ref * f_nocu_ref) < 1e-6


def test_compute_f_nocu():
    # arrange
    # act
    f_nocu = strand_def.compute_f_nocu()

    # assert
    f_nocu_ref = 1 / (1 + strand_def.f_cu_nocu)

    assert abs(f_nocu_ref - f_nocu) < 1e-6


def test_compute_f_cu():
    # arrange
    # act
    f_cu = strand_def.compute_f_cu()

    # assert
    f_cu_ref = strand_def.f_cu_nocu / (1 + strand_def.f_cu_nocu)

    assert abs(f_cu_ref - f_cu) < 1e-6


def test_compute_f_cu_compute_f_nocu():
    # arrange
    # act
    f_cu = strand_def.compute_f_cu()
    f_nocu = strand_def.compute_f_nocu()

    # assert
    assert abs(1 - (f_cu + f_nocu)) < 1e-6


def test_compute_surface():
    # arrange
    # act
    surface = strand_def.compute_surface()

    # assert
    surface_ref = math.pi * strand_def.d_strand ** 2 / 4
    assert abs(surface_ref - surface) < 1e-9
