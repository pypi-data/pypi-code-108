from pspipe import settings


def test_validate(tmp_path):
    s = settings.Settings.get_defaults()

    f = (tmp_path / 'f')
    f.touch()

    s.vis_to_sph.pre_flag = str(f)
    s.combine.pre_flag = str(f)
    s.power_spectra.eor_bin_list = str(f)
    s.power_spectra.ps_config = str(f)
    s.power_spectra.flagger = str(f)
    s.gpr.config_i = str(f)
    s.gpr.config_v = str(f)

    for m in s.keys():
        if hasattr(s, f'validate_{m}'):
            assert s.validate(m), m

    s.gpr.config_v = 'kks'
    assert not s.validate('gpr')

    s.vis_cube.win_fct = 'hann'
    assert s.validate('vis_cube')

    s.vis_cube.win_fct = 'aksks'
    assert not s.validate('vis_cube')

    s.image.lst_bins = [0, 4, 1]
    assert s.validate('image')
