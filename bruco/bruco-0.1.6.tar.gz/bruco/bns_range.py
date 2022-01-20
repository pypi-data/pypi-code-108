from gwpy.astro import inspiral_range
from gwpy.frequencyseries import FrequencySeries

def bns_range(fr, asd):
    """
    Compute the BNS range, integrating from from 10 Hz

    Input: 
       fr, asd = frequency vector and amplitude spectral density of strain
    Output:
       range: in Mpc
    """

    from gwpy.frequencyseries import FrequencySeries
    from gwpy.astro import inspiral_range
    s1 = FrequencySeries(frequencies=fr, data=asd**2)
    return inspiral_range(s1, fmin=10).value


