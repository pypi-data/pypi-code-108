"""
Spectral Line Data Structure
"""


class SpectralLine:
    def __init__(self, name: str, wavelength: float, wavemin: float, wavemax: float):
        self.name = name
        self.wavelength = wavelength
        self.wavemin = wavemin
        self.wavemax = wavemax
        if not (wavemin <= wavelength <= wavemax):
            raise ValueError(
                "SpectralLine.wavemin must be smaller than SpectralLine.wavelength, which must be smaller than SpectralLine.wavemax"
            )

    @property
    def linewidth(self) -> float:
        return self.wavemax - self.wavemin

    def __repr__(self):
        return f"SpectralLine: name={self.name}, wavelength={self.wavelength}, wavemin={self.wavemin}, wavemax={self.wavemax}"


def find_associated_line(wavelength: float, lines: [SpectralLine]) -> str:
    """
    Given a list of SpectralLine objects, find the one that contains the wavelength of the frame
    within its range, and return its name.
    """
    matching_lines = []
    for line in lines:
        if line.wavemin <= wavelength <= line.wavemax:
            matching_lines.append(line)
    if len(matching_lines) == 1:
        return matching_lines[0].name
    if len(matching_lines) > 1:
        raise ValueError(
            f"{len(matching_lines)} valid spectral lines were found for this frame: {matching_lines=}, {wavelength=}"
        )
    raise ValueError(f"No valid line found for wavelength {wavelength}")
