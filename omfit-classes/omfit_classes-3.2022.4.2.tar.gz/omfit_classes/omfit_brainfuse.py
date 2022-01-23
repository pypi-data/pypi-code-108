try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise

try:
    from omfit_classes.brainfuse import brainfuse
    from omfit_classes.brainfuse import *
except ImportError:
    brainfuse = None
from omfit_classes.omfit_ascii import OMFITascii
from omfit_classes.utils_math import *

import random

if brainfuse is not None:

    class OMFITbrainfuse(brainfuse, OMFITascii):
        def __init__(self, filename, **kw):
            OMFITascii.__init__(self, filename, **kw)
            brainfuse.__init__(self, self.filename, **kw)

        def train_net(
            self,
            dB,
            inputNames=[],
            outputNames=[],
            max_iterations=100,
            hidden_layer=None,
            connection_rate=1.0,
            noise=0.0,
            fraction=0.5,
            norm_output={},
            output_mean_0=False,
            robust_stats=0.0,
            weight_decay=0.1,
            spring_decay=1.0,
            activation_function='SIGMOID_SYMMETRIC',
        ):

            """
            :param dB: dictionary of input/output arrays

            :param inputNames: train on these inputs (use all arrays not starting with `OUT_` if not specified)

            :param outputNames: train on these outputs (use all arrays starting with `OUT_` if not specified)

            :param max_iterations: >0 max number of iterations
                                   <0 max number of iterations without improvement

            :param hidden_layer: list of integers defining the NN hidden layer topology

            :param connection_rate: float from 0. to 1. defining the density of the synapses

            :param noise: add gaussian noise to training set

            :param fraction: fraction of data used for training (the rest being for validation)
                             fraction>0 fraction random splitting
                             -1<fraction<0 fraction sequential splitting
                             fraction>1 index sequential splitting

            :param norm_output: normalize outputs

            :param output_mean_0: force average of normalized outputs to have 0 mean

            :param robust_stats: 0<x<100 percentile of data to be considered
                                 =0 mean and std
                                 <0 median and mad

            :param weight_decay: exponential forget of the weight

            :param spring_decay: link training weight decay to the validation error

            :return: std_out of training process
            """

            def f(inv1, inv2):
                try:
                    return abs(np.sum(inv1 - inv2))
                except Exception:
                    return None, None, None

            forbidden = []
            for k1 in sorted(dB.keys()):
                if k1[0] == '_' or np.all(dB[k1] == dB[k1][0]):
                    forbidden.append(k1)
                for k2 in sorted(dB.keys()):
                    if k1 in forbidden or k2 in forbidden:
                        continue
                    v = f(dB[k1], dB[k2])
                    if k1 != k2 and v == 0:
                        forbidden.append(k2)

            if not len(inputNames):
                for k in sorted(dB.keys()):
                    if k not in forbidden and not k.startswith('OUT_') and k[0] != '_':
                        self.inputNames.append(k)
            else:
                self.inputNames = inputNames
            if not len(self.inputNames):
                raise OMFITexception('No inputs!')

            if not len(outputNames):
                for k in sorted(dB.keys()):
                    if k[0] != '_':
                        if np.std(dB[k] - np.mean(dB[k])) != 0:
                            if k.startswith('OUT_') and k[0] != '_':
                                self.outputNames.append(k)
            else:
                self.outputNames = outputNames
            if not len(self.outputNames):
                raise OMFITexception('No outputs!')

            inputs = []
            for k in self.inputNames:
                inputs.append(dB[k].astype(float))
            inputs = np.array(inputs).T

            outputs = []
            for k in self.outputNames:
                outputs.append(dB[k].astype(float))
            outputs = np.array(outputs).T

            def fann_mean(x, dim):
                if robust_stats > 0:
                    tmp = []
                    for k in range(x.shape[-1]):
                        i = np.where(
                            (x[:, k] > np.percentile(x[:, k], robust_stats)) & (x[:, k] < np.percentile(x[:, k], 100 - robust_stats))
                        )[0]
                        if len(i):
                            tmp.append(np.mean(x[i, k]))
                        else:
                            tmp.append(np.mean(x[:, k]))
                elif robust_stats == 0:
                    tmp = np.mean(x, 0)
                else:
                    tmp = np.median(x, 0)
                return tmp

            def fann_std(x, dim):
                if robust_stats > 0:
                    tmp = []
                    for k in range(x.shape[-1]):
                        i = np.where(
                            (x[:, k] > np.percentile(x[:, k], robust_stats)) & (x[:, k] < np.percentile(x[:, k], 100 - robust_stats))
                        )[0]
                        if len(i):
                            tmp.append(np.std(x[i, k]))
                        else:
                            tmp.append(np.std(x[:, k]))
                elif robust_stats == 0:
                    tmp = np.std(x, 0)
                else:
                    tmp = mad(x, 0)

                for k in range(x.shape[-1]):
                    if tmp[k] == 0:
                        tmp[k] = abs(np.mean(x[:, k]))
                    if tmp[k] == 0:
                        tmp[k] = 1.0

                return tmp

            inputs_ = inputs
            outputs_ = outputs

            # normalize
            self.norm_output = []
            for ko, itemo in enumerate(self.outputNames):
                self.norm_output.append([])
                if isinstance(norm_output, dict):
                    for ki, itemi in enumerate(self.inputNames):
                        n0 = 0.0
                        if itemo in norm_output and itemi in norm_output[itemo]:
                            n0 = norm_output[itemo][itemi]
                            print('normalize %s with %s' % (itemo, itemi))
                        self.norm_output[-1].append(n0)
                elif norm_output is True:
                    p, fitfunc = powerlaw_fit(inputs_.T, outputs_[:, ko])
                    print('normalize %s with %s' % (itemo, repr(p)))
                    self.norm_output[-1].extend(p[:-1])
                else:
                    self.norm_output[-1].extend([0.0] * len(self.inputNames))
            outputs_ = self.normOutputs(inputs_, outputs_)

            # scale inputs
            self.scale_mean_in = fann_mean(inputs_, 0)
            self.scale_deviation_in = fann_std(inputs_ - self.scale_mean_in, 0)
            inputs_ = (inputs_ - self.scale_mean_in) / self.scale_deviation_in

            # 0 output mean
            if not output_mean_0:
                self.scale_mean_out = fann_mean(outputs_, 0)
                self.scale_deviation_out = fann_std(outputs_ - self.scale_mean_out, 0)
            else:
                print('output mean 0')
                self.scale_mean_out = fann_mean(outputs_, 0) * 0
                self.scale_deviation_out = np.sqrt(fann_mean(abs(outputs_) ** 2, 0))
            outputs_ = (outputs_ - self.scale_mean_out) / self.scale_deviation_out

            if hidden_layer is None:
                hidden_layer = len(self.inputNames) * 2
            print([len(self.inputNames)] + tolist(hidden_layer) + [len(self.outputNames)])
            self.create_sparse_array(connection_rate, [len(self.inputNames)] + tolist(hidden_layer) + [len(self.outputNames)])
            self.set_activation_function_output(libfann.LINEAR)
            self.set_activation_function_hidden(getattr(libfann, activation_function))
            self.set_training_algorithm(libfann.TRAIN_RPROP)
            self.set_rprop_increase_factor(1.2)
            self.set_rprop_decrease_factor(0.5)
            self.set_train_error_function(libfann.ERRORFUNC_LINEAR)

            self.randomize_weights(-1.0, 1.0)

            if fraction > 0:
                i = np.array(rand(inputs_.shape[0]))
                t_tmpi = inputs_[np.where((i <= fraction))[0], :]
                t_tmpo = outputs_[np.where(i <= fraction)[0], :]
                v_tmpi = inputs_[np.where(i > fraction)[0], :]
                v_tmpo = outputs_[np.where(i > fraction)[0], :]
            elif fraction > -1 and fraction < 0:
                fraction = abs(fraction)
                n = inputs_.shape[0]
                t_tmpi = inputs_[: int(n * fraction), :]
                t_tmpo = outputs_[: int(n * fraction), :]
                v_tmpi = inputs_[int(n * fraction) :, :]
                v_tmpo = outputs_[int(n * fraction) :, :]
            elif abs(fraction) > 1:
                fraction = int(abs(fraction))
                t_tmpi = inputs_[:fraction, :]
                t_tmpo = outputs_[:fraction, :]
                v_tmpi = inputs_[fraction:, :]
                v_tmpo = outputs_[fraction:, :]
            print('training set size: %d' % t_tmpo.shape[0])
            print('validation set size: %d' % v_tmpo.shape[0])

            os.remove(self.filename)

            if noise:
                t_tmpi = t_tmpi * (1 + self.scale_deviation_in[np.newaxis, :] * noise * randn(*t_tmpi.shape))
                t_tmpo = t_tmpo * (1 + self.scale_deviation_out[np.newaxis, :] * noise * randn(*t_tmpo.shape))

            print('Writing train data file')
            txt = [' '.join(map(str, [t_tmpi.shape[0], t_tmpi.shape[1], t_tmpo.shape[1]]))]
            tmp = list(range(t_tmpi.shape[0]))
            random.shuffle(tmp)
            for k in tmp:
                txt.append(' '.join(['%6.6f' % x for x in t_tmpi[k, :]]))
                txt.append(' '.join(['%6.6f' % x for x in t_tmpo[k, :]]))
            trainData = OMFITascii('brainfuse.train', fromString='\n'.join(txt))

            print('Writing validation data file')
            txt = [' '.join(map(str, [v_tmpi.shape[0], v_tmpi.shape[1], v_tmpo.shape[1]]))]
            tmp = list(range(v_tmpi.shape[0]))
            random.shuffle(tmp)
            for k in tmp:
                txt.append(' '.join(['%6.6f' % x for x in v_tmpi[k, :]]))
                txt.append(' '.join(['%6.6f' % x for x in v_tmpo[k, :]]))
            validData = OMFITascii('brainfuse.valid', fromString='\n'.join(txt))

            t0 = time.time()
            self.save()
            inputNames = copy.deepcopy(self.inputNames)
            outputNames = copy.deepcopy(self.outputNames)
            import omfit_classes.OMFITx as OMFITx

            if 'BRAINFUSE_ROOT' not in os.environ:
                raise OMFITexception('Error! BRAINFUSE_ROOT environmental variable is not defined')
            std_out = []
            OMFITx.execute(
                os.environ['BRAINFUSE_ROOT']
                + '/brainfuse_train.exe %s %s %s %d %f %f'
                % (self.filename, trainData.filename, validData.filename, max_iterations, weight_decay, spring_decay),
                std_out=std_out,
            )
            self.load()
            self.inputNames = inputNames
            self.outputNames = outputNames

            data = libfann.training_data()
            data.set_train_data(inputs_, outputs_)
            self.MSE = self.test_data(data)
            data.destroy_train()
            print(self.MSE)

            self.save()

            print('Training timing:' + str(time.time() - t0))
            return std_out


else:
    # associate OMFITbrainfuse to OMFITascii to bring the
    # files along even if they cannot be parsed and used
    class OMFITbrainfuse(OMFITascii):
        pass

    brainfuse = None

    activateNets = None

    activateNetsFile = None

    activateMergeNets = None

__all__ = ['OMFITbrainfuse', 'brainfuse', 'activateNets', 'activateNetsFile', 'activateMergeNets']

############################################
if __name__ == '__main__':
    test_classes_main_header()

    if not os.path.exists('brainfuse.net'):
        print('Unable to test omfit_brainfuse')
        sys.exit()
    OMFITbrainfuse('brainfuse.net')
