import numpy as np
from .double_flatfield import DoubleFlatField
from ..utils import check_shape
from ..cuda.utils import get_cuda_context, __has_pycuda__
from ..cuda.processing import CudaProcessing
from ..misc.unsharp_cuda import CudaUnsharpMask

if __has_pycuda__:
    import pycuda.gpuarray as garray
    import pycuda.cumath as cumath

class CudaDoubleFlatField(DoubleFlatField):

    def __init__(
        self,
        shape,
        result_url=None,
        sub_region=None,
        input_is_mlog=True,
        output_is_mlog=False,
        average_is_on_log=False,
        sigma_filter=None,
        filter_mode="reflect",
        cuda_options=None,
    ):
        """
        Init double flat field with Cuda backend.
        """
        self.cuda_processing = CudaProcessing(**(cuda_options or {}))
        super().__init__(
            shape,
            result_url=result_url,
            sub_region=sub_region,
            input_is_mlog=input_is_mlog,
            output_is_mlog=output_is_mlog,
            average_is_on_log=average_is_on_log,
            sigma_filter=sigma_filter,
            filter_mode=filter_mode
        )
        self._init_gaussian_filter()


    def _init_gaussian_filter(self):
        if self.sigma_filter is None:
            return
        self._unsharp_mask = CudaUnsharpMask(
            self.shape, self.sigma_filter, -1.,
            mode=self.filter_mode, method="log"
        )


    @staticmethod
    def _proc_copy(x, o):
        o[:] = x[:]
        return o

    @staticmethod
    def _proc_expm(x, o):
        o[:] = x[:]
        o[:] *= -1
        cumath.exp(o, out=o)
        return o

    @staticmethod
    def _proc_mlog(x, o, min_clip=None):
        if min_clip is not None:
            garray.maximum(x, min_clip, output=o)
            cumath.log(o, out=o)
        else:
            cumath.log(x, out=o)
        o *= -1
        return o


    def _init_processing(self, input_is_mlog, output_is_mlog, average_is_on_log, sigma_filter, filter_mode):
        self.input_is_mlog = input_is_mlog
        self.output_is_mlog = output_is_mlog
        self.average_is_on_log = average_is_on_log
        self.sigma_filter = sigma_filter
        if self.sigma_filter is not None and abs(float(self.sigma_filter)) < 1e-4:
            self.sigma_filter = None
        self.filter_mode = filter_mode
        # proc = lambda x,o: np.copyto(o, x)
        proc = self._proc_copy
        if self.input_is_mlog:
            if not self.average_is_on_log:
                # proc = lambda x,o: np.exp(-x, out=o)
                proc = self._proc_expm
        else:
            if self.average_is_on_log:
                # proc = lambda x,o: -np.log(x, out=o)
                proc = self._proc_mlog

        # postproc = lambda x: x
        postproc = self._proc_copy
        if self.output_is_mlog:
            if not self.average_is_on_log:
                # postproc = lambda x: -np.log(x)
                postproc = self._proc_mlog
        else:
            if self.average_is_on_log:
                # postproc = lambda x: np.exp(-x)
                postproc = self._proc_expm

        self.proc = proc
        self.postproc = postproc


    def compute_double_flatfield(self, radios, recompute=False):
        """
        Read the radios and generate the "double flat field" by averaging
        and possibly other processing.

        Parameters
        ----------
        radios: array
            Input radios chunk.
        recompute: bool, optional
            Whether to recompute the double flatfield if already computed.
        """
        if not(isinstance(radios, garray.GPUArray)):
            raise ValueError("Expected pycuda.gpuarray.GPUArray for radios")
        if self._computed:
            return self.doubleflatfield
        acc = garray.zeros(radios[0].shape, "f")
        tmpdat = garray.zeros(radios[0].shape, "f")
        for i in range(radios.shape[0]):
            self.proc(radios[i], tmpdat)
            acc += tmpdat

        acc /= radios.shape[0]

        if self.sigma_filter is not None:
            # acc = acc - gaussian_filter(acc, self.sigma_filter, mode=self.filter_mode)
            self._unsharp_mask.unsharp(acc, tmpdat)
            acc[:] = tmpdat[:]
        self.postproc(acc, tmpdat)
        self.doubleflatfield = tmpdat
        # Handle small values to avoid issues when dividing
        # self.doubleflatfield[np.abs(self.doubleflatfield) < self._small] = 1.
        cumath.fabs(self.doubleflatfield, out=acc)
        acc -= self._small # acc = abs(doubleflatfield) - _small
        garray.if_positive(
            acc,
            self.doubleflatfield,
            garray.zeros_like(acc) + self._small,
            out=self.doubleflatfield
        )

        if self.writer is not None:
            self.writer.write(self.doubleflatfield.get(), "double_flatfield")
        self._computed = True
        return self.doubleflatfield


    def get_double_flatfield(self, radios=None, compute=False):
        """
        Get the double flat field or a subregion of it.

        Parameters
        ----------
        radios: array, optional
            Input radios chunk
        compute: bool, optional
            Whether to compute the double flatfield anyway even if a dump file
            exists.
        """
        if self.reader is None:
            if radios is None:
                raise ValueError(
                    "result_url was not provided. Please provide 'radios' to this function"
                )
            return self.compute_double_flatfield(radios)

        if radios is not None and compute:
            res = self.compute_double_flatfield(radios)
        else:
            res = self._load_dff_dump()
            res = garray.to_gpu(res)
            self._computed = True
        return res


    def apply_double_flatfield(self, radios):
        """
        Apply the "double flatfield" filter on a chunk of radios.
        The processing is done in-place !
        """
        check_shape(radios.shape, self.radios_shape, "radios")
        dff = self.get_double_flatfield(radios=radios)
        for i in range(self.n_angles):
            radios[i] /= dff
        return radios
