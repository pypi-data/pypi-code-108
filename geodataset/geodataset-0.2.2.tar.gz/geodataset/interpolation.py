
class Interpolator:

    def __init__(self, source_area, target_area, method, **kwargs):
        self.source_area = source_area
        self.target_area = target_area
        self.method = method
        self.resampler = self.method(self.source_area, self.target_area, **kwargs)


class GridGridInterpolator(Interpolator): #(pyresample)

    def __call__(self, variable):
        return self.resampler.resample(variable)


class GridMeshInterpolator(Interpolator):#(griddata or else)
    pass
    def __call__(self):
        pass


class MeshGridInterpolator(Interpolator):#(Bamg)
    pass
    def __call__(self):
        pass
