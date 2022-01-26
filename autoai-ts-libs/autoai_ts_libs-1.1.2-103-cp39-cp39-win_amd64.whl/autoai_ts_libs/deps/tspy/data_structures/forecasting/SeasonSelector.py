#  /************** Begin Copyright - Do not add comments here **************
#   * Licensed Materials - Property of IBM
#   *
#   *   OCO Source Materials
#   *
#   *   (C) Copyright IBM Corp. 2020, All Rights Reserved
#   *
#   * The source code for this program is not published or other-
#   * wise divested of its trade secrets, irrespective of what has
#   * been deposited with the U.S. Copyright Office.
#   ***************************** End Copyright ****************************/

class SeasonSelector:
    """
    utility which determines a single season length when enough data has been collected
    """
    def __init__(self, tsc, j_season_selector):
        self._tsc = tsc
        self._j_season_selector = j_season_selector

    def get_season_length(self, y):
        """
        Determines the strongest season length for the given number of samples

        Parameters
        ----------
        y : list
            new regularly spaced values series data values

        Returns
        -------
        int
            a positive integer representing the computed season length when enough data has been provided and the season
            can be computed. If not enough data is provided, return -1
        """
        arr_size = len(y)
        j_arr = self._tsc._gateway.new_array(self._tsc._jvm.double, arr_size)
        for i in range(0, arr_size):
            j_arr[i] = y[i]
        return int(self._j_season_selector.getSeasonLength(j_arr))

    def get_multi_season_length(self, num_seasons, y):
        """
        gets a maximum of N strongest signals (i.e resonances as determined by FFT) present in the given data.

        Parameters
        ----------
        num_seasons : int
            the maximum number of signal periods
        y : list
            the data to search for resonant frequencies

        Returns
        -------
        int
            The season length(s) determined from the given samples.  The number may be smaller than the given maxSeason
            value if the strength of the signal is too small
        """
        arr_size = len(y)
        j_arr = self._tsc._gateway.new_array(self._tsc._jvm.double, arr_size)
        for i in range(0, arr_size):
            j_arr[i] = y[i]

        j_arr_result = self._j_season_selector.getMultiSeasonLength(num_seasons, j_arr)
        return [j_arr_result[i] for i in range(0, len(j_arr_result))]
