from statistics import stdev


class InferenceStatistics():
    """Provides inference statistics.
    """

    def __init__(self, metrics, power_events):
        self._fps = None
        self._powers = {}
        self._energy = None
        if "inference_start" in metrics.names:
            inf_start = metrics["inference_start"]
            inf_end = metrics["inference_end"]
            frames = metrics["inference_frames"]
            duration = (inf_end - inf_start) / 1000
            if duration > 0:
                self._fps = frames / duration
            if power_events:
                # get power events between inference start & end
                powers = []
                for event in power_events:
                    if event.ts >= inf_start and event.ts <= inf_end:
                        powers.append(event.power)
                num_powers = len(powers)
                if num_powers > 1:
                    # Remove first value
                    powers = powers[1:]
                    # get avg/min/max
                    self._powers["Avg"] = sum(powers) / len(powers)
                    self._powers["Min"] = min(powers)
                    self._powers["Max"] = max(powers)
                    if len(powers) > 1:
                        self._powers["Std"] = stdev(powers)
                    # evaluate the energy consumed by frame
                    # It is average power * duration / frame
                    self._energy = self._powers["Avg"] * duration / frames

    def __repr__(self):
        fps = "N/A" if self.fps is None else "%.2f" % self._fps
        data = "fps: " + fps
        if self._powers:
            data += ", powers: " + str(self._powers)
        if self._energy:
            data += ", energy: " + str(self._energy)
        return data

    def __str__(self):
        fps = "N/A" if self.fps is None else "%.2f" % self._fps + " fps"
        data = "Average framerate = " + fps
        if self._powers:
            data += "\nLast inference power range (mW): "
            num_powers = len(self._powers)
            for index, (key, value) in enumerate(self._powers.items()):
                data += " {} {:.2f} ".format(key, value)
                if index != num_powers - 1:
                    data += "/"
        if self._energy:
            data += "\nLast inference energy consumed (mJ/frame): {:.2f}".format(
                self._energy)
        return data

    @property
    def fps(self):
        """Returns the frames per seconds for the last inference batch.

        Returns:
            a float value in frames/s.
        """
        return self._fps

    @property
    def powers(self):
        """Returns the power ranges during the last inference batch.

        Note that the power measurements must be enabled for the device.

        Note also that the inference must last long enough to provide meaningful
        power measurements: try increasing the number of samples and/or batch
        size if power ranges are missing.

        Returns:
            a dictionary of float power values in mW indexed by name (where
            names are in ['Avg', 'Min', 'Max', 'Std']).
        """
        return self._powers

    @property
    def energy(self):
        """Returns the energy consumed during the last inference batch.

        This corresponds to the average amount of energy consumed to process one
        frame.

        Returns:
            a float value in mJ/frame.
        """
        return self._energy


class SequenceStatistics(InferenceStatistics):
    """Provides sequence layer statistics.
    """

    def __init__(self, sequence, power_events):
        self._sequence = sequence
        super().__init__(sequence.metrics, power_events)

    def __repr__(self):
        return f"{{sequence: {self._sequence.name}, {super().__repr__()}"

    def __str__(self):
        return f"Sequence {self._sequence.name}\n{super().__str__()}"


class Statistics:
    """Provides statistics for all Model layer sequences.
    """

    def __init__(self, model=None, device=None):
        self._stats = {}
        if model is not None:
            # Iterate through model layer sequences
            for sequence in model.sequences:
                self._stats[sequence.name] = SequenceStatistics(
                    sequence, model.power_events)
        elif device is not None:
            # Check if we have a soc device to get power events
            soc = device.soc
            power_events = device.inference_power_events if soc and soc.power_measurement_enabled else None
            self._stats[device.desc] = InferenceStatistics(
                device.metrics, power_events)

    def __str__(self):
        data = ""
        for _, stat in self._stats.items():
            if stat.fps is not None:
                data += "\n" + stat.__str__()
        if not data:
            data = "N/A"
        return data

    def __repr__(self):
        return self._stats.__repr__()

    def __getitem__(self, key):
        # Look first for a Sequence statistics
        if key in self._stats:
            return self._stats[key]
        raise KeyError

    def __len__(self):
        return len(self._stats)

    def __iter__(self):
        return iter(self._stats.items())

    def keys(self):
        return self._stats.keys()

    def items(self):
        return self._stats.items()
