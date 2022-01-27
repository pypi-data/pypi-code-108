from dkist_processing_common.models.spectral_line import SpectralLine

VBI_SPECTRAL_LINES = [
    SpectralLine(name="VBI-Blue Ca II K", wavelength=393.327, wavemin=393.276, wavemax=393.378),
    SpectralLine(name="VBI-Blue G-Band", wavelength=430.52, wavemin=430.301, wavemax=430.789),
    SpectralLine(name="VBI-Blue Continuum", wavelength=450.287, wavemin=450.084, wavemax=450.490),
    SpectralLine(name="VBI-Blue H-Beta", wavelength=486.139, wavemin=486.116, wavemax=486.162),
    SpectralLine(name="VBI-Red H-alpha", wavelength=656.282, wavemin=656.258, wavemax=656.306),
    SpectralLine(name="VBI-Red Continuum", wavelength=668.423, wavemin=668.202, wavemax=668.644),
    SpectralLine(name="VBI-Red Ti O", wavelength=705.839, wavemin=705.545, wavemax=706.133),
    SpectralLine(name="VBI-Red Fe IX", wavelength=789.186, wavemin=789.168, wavemax=789.204),
]
