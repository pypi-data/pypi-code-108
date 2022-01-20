
class TSSampling:
    r"""
    Examples:
        >>> from ailever.forecast import TSA
        >>> ...
        >>> trendAR=[]; trendMA=[]
        >>> seasonAR=[]; seasonMA=[]
        >>> TSA.sarima((1,1,2), (2,0,1,4), trendAR=trendAR, trendMA=trendMA, seasonAR=seasonAR, seasonMA=seasonMA, n_samples=300)
    """

    @staticmethod
    def sarima(trendparams:tuple=(0,0,0), seasonalparams:tuple=(0,0,0,1), trendAR=None, trendMA=None, seasonAR=None, seasonMA=None, n_samples=300):
        Process(trendparams, seasonalparams, trendAR, trendMA, seasonAR, seasonMA, n_samples)



