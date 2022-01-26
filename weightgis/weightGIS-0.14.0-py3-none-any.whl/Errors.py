class BaseNameNotFound(Exception):
    def __init__(self, base_name, shapefile_folder):
        super(BaseNameNotFound, self).__init__(
            f"\n\tFailed to find {base_name} within {shapefile_folder}"
        )


class NoSubUnitWeightIndex(Exception):
    def __init__(self):
        super(NoSubUnitWeightIndex, self).__init__(
            f"\n\tYou have specified you wish to use subunit weights, and have provided a valid file to do so, but not "
            f"provided the index of the weighting parameter within the attribute table of said shapefile"
        )
