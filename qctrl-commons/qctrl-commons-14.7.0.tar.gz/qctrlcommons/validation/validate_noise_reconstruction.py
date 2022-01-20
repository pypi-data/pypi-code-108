"""
Validator for core__calculateNoiseReconstruction mutation.
"""
from typing import List

import numpy as np

from qctrlcommons.exceptions import QctrlFieldError
from qctrlcommons.validation.base import BaseMutationInputValidator
from qctrlcommons.validation.messages import Messages


class CalculateNoiseReconstructionValidator(BaseMutationInputValidator):
    """
    Validator for core__calculateNoiseReconstruction mutation.
    """

    def check_noises(self, input_):  # pylint:disable=no-self-use
        """
        Expects that the number of noises is equal to the number of filter functions
        in each measurement.

        Parameters
        ----------
        input_: dict
            the GraphQL input.

        Raises
        ------
        QctrlFieldError
            validation check failed
        """
        noises = input_.get("noises")
        measurements = input_.get("measurements")
        if noises is not None:
            noise_count = len(noises)
            for measurement in measurements:
                if len(measurement.get("filterFunctions")) != noise_count:
                    raise QctrlFieldError(
                        message="The number of filterFunctions per measurement "
                        "has to match the number of noises.",
                        fields=["noises"],
                    )

    def check_measurements(self, input_):  # pylint:disable=no-self-use
        """
        Expects the following:
        1. There is at least 1 measurement.
        2. Measurement's `infidelity` value needs to be >= 0.
        3. Measurement's `infidelity_uncertainty` value needs to be >=0 if present.
        4. There needs to be at least 1 filter function per measurement.
        4. The samples frequency at each index inside the `filter_function` is the same same
        across all the measurements.

        Parameters
        ----------
        input_: dict
            the GraphQL input.

        Raises
        ------
        QctrlFieldError
            validation check failed
        """
        measurements = input_.get("measurements")

        # check there is at least 1 measurement
        if len(measurements) < 1:
            raise QctrlFieldError(
                message=Messages(
                    field_name="measurements", min_length=0
                ).items_greater_than,
                fields=["measurements"],
            )

        noise_channel_count = len(measurements[0].get("filterFunctions"))
        if noise_channel_count < 1:
            raise QctrlFieldError(
                message="There needs to be at least 1 `filterFunctions` per measurement.",
                fields=["filterFunctions"],
            )
        noise_channel_frequencies = {}
        for measurement in measurements:

            # check infidelity is >= 0
            if measurement["infidelity"] < 0:
                raise QctrlFieldError(
                    message=Messages(field_name="infidelity", minimum=0).minimum,
                    fields=["infidelity"],
                )

            # check infidelity_uncertainty is >= 0
            infidelity_uncertainty = measurement.get("infidelityUncertainty")
            if infidelity_uncertainty and infidelity_uncertainty < 0:
                raise QctrlFieldError(
                    message=Messages(
                        field_name="infidelityUncertainty", minimum=0
                    ).minimum,
                    fields=["infidelityUncertainty"],
                )

            # validate filter_functions
            filter_functions = measurement.get("filterFunctions")
            if len(filter_functions) != noise_channel_count:
                raise QctrlFieldError(
                    message="The number of `filterFunctions` per measurement "
                    "must be the same across all measurements.",
                    fields=["filterFunctions"],
                )
            self._check_filter_functions(filter_functions)

            for channel in range(noise_channel_count):
                sample_frequencies = [
                    sample["frequency"]
                    for sample in measurement["filterFunctions"][channel]["samples"]
                ]
                if noise_channel_frequencies.get(channel) and (
                    len(noise_channel_frequencies[channel]) != len(sample_frequencies)
                    or not np.allclose(
                        noise_channel_frequencies[channel], sample_frequencies
                    )
                ):
                    raise QctrlFieldError(
                        message="The filter function sample frequencies "
                        "must be the same at each noise.",
                        fields=["frequency"],
                    )
                noise_channel_frequencies[channel] = sample_frequencies

    def _check_filter_functions(
        self, filter_functions: List[dict]
    ):  # pylint:disable=no-self-use
        """
        Expects the following:
        1. The `samples` are in increasing order of frequency
        2. The `inverse_power` in each sample is >= 0.

        Parameters
        ----------
        filter_functions: List[dict]
            The list of filter functions, each containing a ` frequency` and `inverse_power`.

        Raises
        ------
        QctrlFieldError
            validation check failed
        """
        for filter_function in filter_functions:
            for sample in filter_function["samples"]:
                if sample.get("inversePower") < 0:
                    raise QctrlFieldError(
                        message=Messages(field_name="inversePower", minimum=0).minimum,
                        fields=["inversePower"],
                    )
            prev_frequency = filter_function["samples"][0]["frequency"]
            for sample in filter_function["samples"][1:]:
                if sample["frequency"] <= prev_frequency:
                    raise QctrlFieldError(
                        message="Filter function samples need to be provided "
                        "in order of ascending frequency.",
                        fields=["frequency"],
                    )
                prev_frequency = sample["frequency"]

    def check_method(self, input_):  # pylint:disable=no-self-use, too-many-branches
        """
        Expects the following:
        1. Only one field in method is non null.
        2. When singularValueDecomposition and truncation is set:
            a. Only one field in singular_value_trunctation is non null
            b. roundingThreshold is <=1 but >= 0 if entropy is set.
            c. checks singularValueCount if fixedLength is set.
        3. When convexOptimization is non null.
            a. powerDensityLowerBound >=0
            b. powerDensityLowerBound < powerDensityUpperBound
            c. regularizationHyperparamete >= 0

        Parameters
        ----------
        input_: dict
            the GraphQL input.

        Raises
        ------
        QctrlFieldError
            validation check failed
        """
        # skip check if method is not set
        method = input_.get("method")
        if method is None:
            return

        if not method:
            raise QctrlFieldError(
                message="Both `singularValueDecomposition` and `convexOptimization`"
                " cannot be null. Either `singularValueDecomposition` or "
                "`convexOptimization` must be set.",
                fields=["singularValueDecomposition", "convexOptimization"],
            )

        singular_value_decomposition = method.get("singularValueDecomposition")
        convex_optimization = method.get("convexOptimization")

        if singular_value_decomposition is not None and convex_optimization is not None:
            raise QctrlFieldError(
                message="Both `singularValueDecomposition` and `convexOptimization`"
                " cannot be non null. Either `singularValueDecomposition` "
                "or `convexOptimization` must be set.",
                fields=["singularValueDecomposition", "convexOptimization"],
            )

        if singular_value_decomposition is not None:

            truncation = singular_value_decomposition.get("truncation")
            if truncation is not None:
                if not truncation:
                    raise QctrlFieldError(
                        message="Both `entropy` and `fixedLength` cannot be null."
                        " Either `entropy` or `fixedLength` must be set.",
                        fields=["entropy", "fixedLength"],
                    )

                entropy = truncation.get("entropy")
                fixed_length = truncation.get("fixedLength")

                if entropy is None and fixed_length is None:
                    raise QctrlFieldError(
                        message="Both `entropy` and `fixedLength` cannot be null."
                        " Either `entropy` or `fixedLength` must be set.",
                        fields=["entropy", "fixedLength"],
                    )

                if entropy is not None and fixed_length is not None:
                    raise QctrlFieldError(
                        message="Both `entropy` and `fixedLength` cannot be non null. "
                        "Either `entropy` or `fixedLength` must be set.",
                        fields=["entropy", "fixedLength"],
                    )

                if (
                    entropy is not None
                    and not 0 <= entropy.get("roundingThreshold") <= 1
                ):
                    raise QctrlFieldError(
                        message=Messages(
                            field_name="roundingThreshold", minimum=0, maximum=1
                        ).value_between,
                        fields=["roundingThreshold"],
                    )
                if (
                    fixed_length is not None
                    and fixed_length.get("singularValueCount") is not None
                ):
                    self._check_singular_value_count(
                        fixed_length.get("singularValueCount"),
                        input_.get("measurements"),
                    )

        if convex_optimization:

            if convex_optimization.get("powerDensityLowerBound") < 0:
                raise QctrlFieldError(
                    message=Messages(
                        field_name="powerDensityLowerBound", minimum=0
                    ).minimum,
                    fields=["powerDensityLowerBound"],
                )

            if convex_optimization.get(
                "powerDensityLowerBound"
            ) >= convex_optimization.get("powerDensityUpperBound"):
                raise QctrlFieldError(
                    message=Messages(
                        field_name="powerDensityUpperBound",
                        minimum="powerDensityLowerBound",
                    ).greater_than,
                    fields=["powerDensityUpperBound"],
                )

            if convex_optimization.get("regularizationHyperparameter") < 0:
                raise QctrlFieldError(
                    message=Messages(
                        field_name="regularizationHyperparameter", minimum=0
                    ).minimum,
                    fields=["regularizationHyperparameter"],
                )

    def _check_singular_value_count(
        self, singular_value_count, measurements
    ):  # pylint:disable=no-self-use
        """
        Expects the following:
        1. The `singular_value_count` is >= 1.
        2. The `singular_value_count` is <= the total number of measurements.
        3. The `singular_value_count` is <= The total number of sample frequencies in a single
        measurement.

        Parameters
        ----------
        singular_value_count: int
            The singular count value.
        measurements: dict
            The measurements associated with the noise reconstruction.

        Raises
        ------
        QctrlFieldError
            validation check failed
        """

        error_message = None
        if singular_value_count < 1:
            error_message = Messages(field_name="singularValueCount", minimum=1).minimum
            raise QctrlFieldError(message=error_message, fields=["singularValueCount"])

        number_of_measurements = len(measurements)
        total_sample_frequencies = sum(
            len(filter_function["samples"])
            for filter_function in measurements[0]["filterFunctions"]
        )

        if singular_value_count > number_of_measurements:
            error_message = Messages(
                field_name="singularValueCount",
                maximum="the total number of measurements",
            ).maximum

        elif singular_value_count > total_sample_frequencies:
            error_message = Messages(
                field_name="singularValueCount",
                maximum="the total number of sample frequencies in a single measurement",
            ).maximum

        if error_message:
            raise QctrlFieldError(message=error_message, fields=["singularValueCount"])
