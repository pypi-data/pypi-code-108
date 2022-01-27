## Added by Brian Blaylock
## September 29, 2021

# ! Experimental
# This is a special case for model data that is stored on your local machine.
# Index files are assumed to be in the same directory as the file with .idx appended to the file name.
# * For the moment, you can only have one "local" template.
# Since Herbie now accepts kwargs and passes them to self, you can template with any parameter,
# just remember to pass that parameter to the Herbie class 😋


class coamps:
    def template(self):
        self.DESCRIPTION = "Local GRIB Files"
        self.DETAILS = {
            "local": "These GRIB2 files are concatenated from Brian's Cylc suite experiments."
        }
        self.PRODUCTS = {
            "sfc": "2D surface level fields",
            "pre": "3D pressure level fields",
        }
        self.SOURCES = {
            "local": f"$CENTER/save/{self.project}/gribfiles/{self.date:%Y%m%d%H}/nest{self.nest}/coamps.t{self.date:%H}z.{self.product}.f{self.fxx:02d}.grib2",
        }
        self.LOCALFILE = f"{self.get_remoteFileName}"
