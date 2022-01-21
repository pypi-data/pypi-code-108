import numpy as np


class UniversalLimit:
    """ """
    STRAIN_STRESS_VALUES = ["Strain", "Stress"]
    TENSION_COMPRESSION_VALUES = ["Overall", "Tension", "Compression", "vonMises"]


class ObjectCalcUtil:
    """ """
    def __init__(self):
        pass

    def _overall_function(self, integration_points, axis=1):
        """

        Args:
          integration_points: param axis:
          axis:  (Default value = 1)

        Returns:

        """

        abs_min = np.abs(np.min(integration_points, axis=axis))
        abs_max = np.abs(np.max(integration_points, axis=axis))
        return np.max([abs_min, abs_max], axis=0)

    def _von_mises(self, integration_points, axis=1):
        """

        Args:
          integration_points: 
          axis:  (Default value = 1)

        Returns:

        """

        xy = (integration_points[:, 0] - integration_points[:, 1])**2 + \
            (integration_points[:, 1] - integration_points[:, 2])**2 + \
            (integration_points[:, 2] - integration_points[:, 0])**2

        return np.sqrt(1/2 * xy)

    def retrieve_functions(self, selection_tension_compression, integration_point):
        """

        Args:
          selection_tension_compression: param integration_point:
          integration_point: 

        Returns:

        """

        integration_point_options = ["Max", "Mean", "Min"]

        # selected function for tension compression and overall calculation
        if selection_tension_compression == UniversalLimit.TENSION_COMPRESSION_VALUES[0]:  # Overall
            function_overall_tension_compression = self._overall_function
        elif selection_tension_compression == UniversalLimit.TENSION_COMPRESSION_VALUES[1]:  # Tension
            function_overall_tension_compression = np.max
        elif selection_tension_compression == UniversalLimit.TENSION_COMPRESSION_VALUES[2]:  # Compression
            function_overall_tension_compression = np.min
        elif selection_tension_compression == UniversalLimit.TENSION_COMPRESSION_VALUES[3]:  # Compression
            function_overall_tension_compression = self._von_mises
        else:
            assert False

        if integration_point == integration_point_options[0]:
            integration_point_function = np.max
        elif integration_point == integration_point_options[1]:
            integration_point_function = np.mean
        elif integration_point == integration_point_options[2]:
            integration_point_function = np.min
        else:
            assert False

        return function_overall_tension_compression, integration_point_function
