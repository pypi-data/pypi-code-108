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

from omfit_classes.omfit_namelist import OMFITnamelist
from omfit_classes.omfit_ascii import OMFITascii
import numpy as np
import fortranformat
from omfit_classes.utils_fusion import tokamak

__all__ = ['OMFITmhdin', 'OMFITdprobe', 'OMFITnstxMHD', 'get_mhdindat']


class OMFITmhdin(OMFITnamelist):
    scaleSizes = 50
    invalid = 99

    @dynaLoad
    def load(self, *args, **kw):
        r"""
        Load OMFITmhdin file

        :param \*args: arguments passed to OMFITnamelist.load()

        :param \**kw: keyword arguments passed to OMFITnamelist.load()
        """

        # load namelist
        self.outsideOfNamelistIsComment = True
        self.noSpaceIsComment = True
        super().load(*args, **kw)

        # out-of-namelist format (DIII-D)
        if 'RF' not in self['IN3']:
            fformat = {}
            fformat['FC'] = fortranformat.FortranRecordReader('(4f12.4,2A12)')
            fformat['OH'] = fortranformat.FortranRecordReader('(5f10.6)')
            fformat['VESSEL'] = fortranformat.FortranRecordReader('(4f12.4,2A12)')

            # get text past namelist
            comment_item = list(self.keys())[-1]
            if '__comment' not in comment_item:
                self.clear()
                self.dynaLoad = True
                raise ValueError('Not a valid mhdin.dat file')
            lines = str(self[comment_item])
            tmp = lines.split('comment')
            if len(tmp) > 1:
                lines, comment = tmp
            else:
                lines = tmp[0]
                comment = ''
            del self[comment_item]
            lines = lines.split('\n')
            lines = [line.expandtabs(12) for line in lines if len(line.strip()) and line.strip()[0] != '!']

            # number of elements per section
            nfc = len(self['IN3'].get('FCTURN', self['IN3'].get('TURNFC', None)))
            if self['IN3'].get('IECOIL', 0):
                nve = len(self['IN3']['RSISVS'])
                ntf = len(lines) - nfc - nve
            else:
                ntf = 0
                nve = len(lines) - nfc - ntf

            # poloidal field coils
            # R,Z,DR,DZ,skew_angle1,skew_angle2
            kk = 0
            self['FC'] = {}
            for k in range(nfc):
                lines[kk] += '%12d%12d' % (0, 0)
                data = fformat['FC'].read(lines[kk])
                data[4] = '0.0' if not data[4].strip() or float(data[4]) == 0 else data[4]
                data[5] = '90.0' if not data[5].strip() or float(data[5]) == 0 else data[5]
                data = np.array(list(map(float, data)))
                self['FC']['%d' % (k + 1)] = data
                kk += 1
            self['FC'] = np.array(self['FC'].values())

            # ohmic coils
            # R,Z,DR,DZ,block
            if not ntf:
                self['OH'] = np.array([])
            else:
                self['OH'] = {}
                for k in range(ntf):
                    data = fformat['OH'].read(lines[kk])
                    self['OH']['%d' % (k + 1)] = data
                    kk += 1
                self['OH'] = np.array(self['OH'].values())

            # conducting vessel segments
            # R,Z,DR,DZ,skew_angle1,skew_angle2
            if not nve:
                self['VESSEL'] = np.array([])
            else:
                self['VESSEL'] = {}
                for k in range(nve):
                    lines[kk] += '%12d%12d' % (0, 0)
                    data = fformat['VESSEL'].read(lines[kk])
                    data[4] = '0.0' if not data[4].strip() or float(data[4]) == 0 else data[4]
                    data[5] = '90.0' if not data[5].strip() or float(data[5]) == 0 else data[5]
                    data = np.array(list(map(float, data)))
                    data = np.array(data)
                    self['VESSEL']['%d' % (k + 1)] = data
                    kk += 1
                self['VESSEL'] = np.array(self['VESSEL'].values())

            # uncomment this to translate out-of-namelist format to in-namelist format
            if False:
                # create namelist elements
                self['IN3']['RF'] = self['FC'][:, 0]
                self['IN3']['ZF'] = self['FC'][:, 1]
                self['IN3']['WF'] = self['FC'][:, 2]
                self['IN3']['HF'] = self['FC'][:, 3]
                self['IN3']['AF'] = self['FC'][:, 4]
                self['IN3']['AF2'] = self['FC'][:, 5]

                self['IN3']['RVS'] = self['VESSEL'][:, 0]
                self['IN3']['ZVS'] = self['VESSEL'][:, 1]
                self['IN3']['WVS'] = self['VESSEL'][:, 2]
                self['IN3']['HVS'] = self['VESSEL'][:, 3]
                self['IN3']['AVS'] = self['VESSEL'][:, 5]
                self['IN3']['AVS2'] = self['VESSEL'][:, 5]

                self['IN3']['RE'] = self['OH'][:, 0]
                self['IN3']['ZE'] = self['OH'][:, 1]
                self['IN3']['WE'] = self['OH'][:, 2]
                self['IN3']['HE'] = self['OH'][:, 3]

            self['__trailing_comment__'] = 'comment' + comment

        # in-namelist format
        else:

            # initialize namelist
            for geom in ['R{element}', 'Z{element}', 'W{element}', 'H{element}', 'A{element}', 'A{element}2']:
                for element in ['E', 'F', 'VS']:
                    item = geom.format(element=element)
                    if item not in self['IN3'] and item not in ['AE', 'AE2']:
                        self['IN3'][item] = np.array([])

            # populate aggregated arrays
            self['FC'] = np.array(
                [
                    self['IN3']['RF'],
                    self['IN3']['ZF'],
                    self['IN3']['WF'],
                    self['IN3']['HF'],
                    self['IN3']['AF'],
                    self['IN3']['AF2'] + (self['IN3']['AF2'] == 0) * 90,
                ]
            ).T
            self['OH'] = np.array([self['IN3']['RE'], self['IN3']['ZE'], self['IN3']['WE'], self['IN3']['HE'], self['IN3']['HE'] * 0 + 1]).T
            self['VESSEL'] = np.array(
                [
                    self['IN3']['RVS'],
                    self['IN3']['ZVS'],
                    self['IN3']['WVS'],
                    self['IN3']['HVS'],
                    self['IN3']['AVS'],
                    self['IN3']['AVS2'] + (self['IN3']['AVS2'] == 0) * 90,
                ]
            ).T

    @dynaSave
    def save(self, *args, **kw):
        r"""
        Save OMFITmhdin file

        :param \*args: arguments passed to OMFITnamelist.save()

        :param \**kw: keyword arguments passed to OMFITnamelist.save()
        """
        fformat = {}
        fformat['FC'] = fortranformat.FortranRecordWriter('(4f12.4,2A12)')
        fformat['OH'] = fortranformat.FortranRecordWriter('(5f10.6)')
        fformat['VESSEL'] = fortranformat.FortranRecordWriter('(4f12.4,2A12)')

        mhdin_special = ['FC', 'OH', 'VESSEL', '__trailing_comment__']

        # remove non-namelist components
        tmp = {}
        for item in mhdin_special:
            if item in self:
                tmp[item] = self[item]
                del self[item]
        angle2_special = {}
        for item in ['AF2', 'AVS2']:
            if item not in self['IN3']:
                continue
            angle2_special[item] = self['IN3'][item].copy()
            self['IN3'][item][self['IN3'][item] == 90] = 0.0
        try:
            # save namelist section
            super().save(*args, **kw)

            # append non-namelist components
            txt = ''
            for system in mhdin_special:
                if system not in tmp:
                    continue
                if system in fformat:
                    for item in range(tmp[system].shape[0]):
                        data = tmp[system][item, :].tolist()
                        if len(data) == 6:
                            if data[4] == 0:
                                data[4] = ''
                            if data[5] == 90:
                                data[5] = ''
                        txt += fformat[system].write(data) + '\n'
                else:
                    txt += tmp[system]
            with open(self.filename, 'a') as f:
                f.write(txt)

        finally:
            # restore angles
            for item in angle2_special:
                self['IN3'][item] = angle2_special[item]
            # restore non-namelist components
            for item in mhdin_special:
                if item in tmp:
                    self[item] = tmp[item]

    @staticmethod
    def plot_coil(data, patch_facecolor='lightgray', patch_edgecolor='black', label=None, ax=None):
        """
        plot individual coil

        :param data: FC, OH, VESSEL data array row

        :param patch_facecolor: face color

        :param patch_edgecolor: edge color

        :param label: [True, False]

        :param ax: axis

        :return: matplotlib rectangle patch
        """
        import matplotlib.transforms as mtransforms
        from matplotlib import patches

        if ax is None:
            ax = pyplot.gca()

        rect = patches.Rectangle((0, 0), data[2], data[3], facecolor=patch_facecolor, edgecolor=patch_edgecolor)
        if len(data) == 6:
            angle1, angle2 = 90 - data[5], data[4]
            rect.set_transform(
                mtransforms.Affine2D().translate(-data[2] / 2.0, -data[3] / 2.0)
                + mtransforms.Affine2D().skew_deg(angle1, angle2)
                + mtransforms.Affine2D().translate(data[0], data[1])
                + ax.transData
            )
        else:
            rect.set_transform(
                mtransforms.Affine2D().translate(-data[2] / 2.0, -data[3] / 2.0)
                + mtransforms.Affine2D().translate(data[0], data[1])
                + ax.transData
            )
        ax.add_patch(rect)

        if label:
            ax.text(data[0], data[1], label, color='w', size=8, ha='center', va='center', zorder=1000, weight='bold', clip_on=True)
            ax.text(data[0], data[1], label, color='m', size=8, ha='center', va='center', zorder=1001, clip_on=True)
        return rect

    def plot_flux_loops(self, display=None, colors=None, label=False, ax=None):
        """
        plot the flux loops

        :param display: array used to turn on/off display individual flux loops

        :param colors: array used to set the color of individual flux loops

        :param label: [True, False]

        :param ax: axis
        """
        if 'ZSI' not in self['IN3'] or 'RSI' not in self['IN3']:
            return
        if ax is None:
            ax = pyplot.gca()
        x0 = np.squeeze(self['IN3']['RSI'])
        y0 = np.squeeze(self['IN3']['ZSI'])
        if colors is not None:
            c0 = np.squeeze(colors)[: len(x0)]
        if display is not None:
            s0 = np.squeeze((display != 0))[: len(x0)]
        else:
            s0 = np.ones(x0.shape)
        s0 *= self.scaleSizes

        # trim
        x0 = x0[: len(s0)]
        y0 = y0[: len(s0)]

        # disable plotting of dummy flux loops
        x0 = x0[np.where(y0 != -self.invalid)]
        y0 = y0[np.where(y0 != -self.invalid)]

        # plot
        if colors is not None:
            ax.scatter(x0, y0, s=s0, c=c0, vmin=0, vmax=vmax, marker='o', cmap=cm, alpha=0.75, zorder=100)
        else:
            ax.scatter(x0, y0, s=s0, color='b', marker='o', alpha=0.75, zorder=100)

        # labels
        if label:
            for k, name in enumerate(self['IN3']['LPNAME']):
                ax.text(x0[k], y0[k], '\n ' + name, ha='left', va='top', size=8, color='w', zorder=1000, weight='bold', clip_on=True)
                ax.text(x0[k], y0[k], '\n ' + name, ha='left', va='top', size=8, color='b', zorder=1001, clip_on=True)

    def plot_magnetic_probes(self, display=None, colors=None, label=False, ax=None):
        """
        plot the magnetic probes

        :param display: array used to turn on/off the display of individual magnetic probes

        :param colors: array used to set the color of individual magnetic probes

        :param label: [True, False]

        :param ax: axis
        """
        # The magnetic probes are characterized by:
        #  - XMP2 and
        #  - YMP2, cartesian coordinates of the center of the probe,
        #  - SMP2, size/length of the probe in meters (read below!),
        #  - AMP2, angle/orientation of the probe in degrees.
        #
        # the usual magnetic probe in EFIT is a partial rogowski coil,
        # yet beware! the EFIT D3D probe file also models saddle loops,
        # which extend in the toroidal direction and provide integrated
        # signals. such loops are characterized by a negative length.
        #
        # in order to plot non-rogowski coils correctly, a forced 90 deg
        # counter-clockwise rotation has to be applied on the probe's angle.
        #
        # the probes are plotted with different linestyles: rogowski coils
        # are plotted with a segment centered around a dot, whereas
        # saddle loops are plotted with a segment with dots on the endpoints.
        #
        # FURTHER REFERENCE as explained by T. Strait on 19-jul-2016
        #
        # - The angle AMP2 always indicates the direction of the magnetic field
        #   component that is being measured.
        #
        # - The length SMP2 indicates the length (in the R-Z plane) over which
        #   the magnetic field is averaged by the sensor.
        #
        # - SMP2 > 0 indicates that the averaging length is in the direction of AMP2.
        #   SMP2 < 0 indicates that the averaging length is perpendicular to AMP2.
        #
        # - In predicting the measurement of the sensor for purposes of fitting,
        #   only the length SMP2 is considered.  The width of the sensor in the
        #   direction perpendicular to SMP2 (in the R-Z plane) is small and is
        #   therefore neglected.
        #   Since the EFIT equilibrium is assumed to be axisymmetric, the width
        #   of the sensor in the toroidal direction is not relevant.
        #
        if 'XMP2' not in self['IN3'] or 'YMP2' not in self['IN3'] or 'SMP2' not in self['IN3'] or 'AMP2' not in self['IN3']:
            return
        if ax is None:
            ax = pyplot.gca()
        # first, get the arrays and make sure that their dimensions match
        x0 = np.squeeze(self['IN3']['XMP2'])
        y0 = np.squeeze(self['IN3']['YMP2'])
        l0 = np.squeeze(self['IN3']['SMP2'])
        a0 = np.squeeze(self['IN3']['AMP2'])
        if colors is not None:
            c0 = np.squeeze(colors)[: len(x0)]
        if display is not None:
            s0 = np.squeeze((display != 0))[: len(x0)]
        else:
            s0 = np.ones(x0.shape)
        s0 *= self.scaleSizes

        # trim
        x0 = x0[: len(s0)]
        y0 = y0[: len(s0)]
        l0 = l0[: len(s0)]
        a0 = a0[: len(s0)]

        # disable plotting of dummy probes
        l0 = l0[np.where(y0 != -self.invalid)]
        a0 = a0[np.where(y0 != -self.invalid)]
        x0 = x0[np.where(y0 != -self.invalid)]
        y0 = y0[np.where(y0 != -self.invalid)]

        def probe_endpoints(x0, y0, a0, l0):
            boo = (1 - np.sign(l0)) / 2.0
            cor = boo * np.pi / 2.0

            # then, compute the two-point arrays to build the partial rogowskis
            # as segments rather than single points, applying the correction
            px = x0 - l0 / 2.0 * np.cos(a0 * np.pi / 180.0 + cor)
            py = y0 - l0 / 2.0 * np.sin(a0 * np.pi / 180.0 + cor)
            qx = x0 + l0 / 2.0 * np.cos(a0 * np.pi / 180.0 + cor)
            qy = y0 + l0 / 2.0 * np.sin(a0 * np.pi / 180.0 + cor)

            segx = []
            segy = []
            for k in range(len(x0)):
                segx.append([px[k], qx[k]])
                segy.append([py[k], qy[k]])
            return segx, segy

        # finally, plot
        segx, segy = probe_endpoints(x0, y0, a0, l0)
        for k in range(len(x0)):
            if colors is None:
                col = 'r'
            else:
                col = cm(c0[k])
            if l0[k] > 0:
                ax.plot(segx[k], segy[k], '-', lw=2, color=col, zorder=100, alpha=0.75)
                ax.plot(x0[k], y0[k], '.', color=col, zorder=100, alpha=0.75, mec='none')
            else:
                ax.plot(segx[k], segy[k], '.-', lw=2, color=col, zorder=100, alpha=0.75, mec='none')

        # labels
        if label:
            for k, name in enumerate(self['IN3']['MPNAM2']):
                ax.text(x0[k], y0[k], '\n ' + name, ha='left', va='top', size=8, color='w', zorder=1000, weight='bold', clip_on=True)
                ax.text(x0[k], y0[k], '\n ' + name, ha='left', va='top', size=8, color='r', zorder=1001, clip_on=True)

    def plot_poloidal_field_coils(self, edgecolor='none', facecolor='orange', label=False, ax=None):
        """
        Plot poloidal field coils

        :param label: [True, False]

        :param ax: axis
        """
        if not self['FC'].size:
            return
        if ax is None:
            ax = pyplot.gca()
        return self.plot_system('FC', edgecolor=edgecolor, facecolor=facecolor, label=label, ax=ax)

    def plot_ohmic_coils(self, edgecolor='none', facecolor='none', label=False, ax=None):
        """
        Plot ohmic coils

        :param label: [True, False]

        :param ax: axis
        """
        if not self['OH'].size:
            return
        if ax is None:
            ax = pyplot.gca()
        return self.plot_system('OH', edgecolor=edgecolor, facecolor=facecolor, label=label, ax=ax)

    def plot_vessel(self, edgecolor='none', facecolor='gray', label=False, ax=None):
        """
        Plot vacuum vessel

        :param label: [True, False]

        :param ax: axis
        """
        if not self['VESSEL'].size:
            return
        if ax is None:
            ax = pyplot.gca()
        return self.plot_system('VESSEL', edgecolor=edgecolor, facecolor=facecolor, label=label, ax=ax)

    def plot_system(self, system, edgecolor, facecolor, label=False, ax=None):
        """
        Plot coil/vessel system

        :param system: ['FC', 'OH', 'VESSEL']

        :param edgecolor: color of patch edges

        :param facecolor: color of patch fill

        :param label: [True, False]

        :param ax: axis
        """
        if ax is None:
            ax = pyplot.gca()
        kw = {'ax': ax}
        kw['patch_facecolor'] = facecolor
        kw['patch_edgecolor'] = edgecolor
        if system == 'OH':
            n = int(max(self[system][:, -1]))
        for k in range(self[system].shape[0]):
            # disable plotting of dummy probes/loops
            if self[system][k, 1] == self.invalid:
                continue
            if system == 'OH' and facecolor == 'none':
                kw['patch_facecolor'] = pyplot.cm.viridis(np.linspace(0.0, 1.0, n))[int(self[system][k, -1]) - 1]
            if label:
                kw['label'] = '%d' % k
            self.plot_coil(self[system][k, :], **kw)
        ax.set_frame_on(False)
        ax.set_aspect('equal')
        ax.autoscale(tight=True)
        ax.set_xlim(ax.get_xlim() * np.array([0.98, 1.02]))
        ax.set_ylim(ax.get_ylim() * np.array([1.02, 1.02]))

    def plot_domain(self, ax=None):
        """
        plot EFUND computation domain

        :param ax: axis
        """
        if ax is None:
            ax = pyplot.gca()

        from matplotlib import patches

        rect = patches.Rectangle(
            (self['IN3']['RLEFT'], self['IN3']['ZBOTTO']),
            self['IN3']['RRIGHT'] - self['IN3']['RLEFT'],
            self['IN3']['ZTOP'] - self['IN3']['ZBOTTO'],
            facecolor='none',
            edgecolor='black',
            ls='--',
        )
        ax.add_patch(rect)

    def plot(self, label=False, plot_coils=True, plot_vessel=True, plot_measurements=True, plot_domain=True, ax=None):
        """
        Composite plot

        :param label: label coils and measurements

        :param plot_coils: plot poloidal field and oh coils

        :param plot_vessel: plot conducting vessel

        :param plot_measurements: plot flux loops and magnetic probes

        :param plot_domain: plot EFUND computing domain

        :param ax: axis
        """

        if ax is None:
            ax = pyplot.gca()
        if plot_coils:
            self.plot_poloidal_field_coils(label=label, ax=ax)
            self.plot_ohmic_coils(label=label, ax=ax)
        if plot_vessel:
            self.plot_vessel(label=label, ax=ax)
        if plot_measurements:
            self.plot_flux_loops(label=label, ax=ax)
            self.plot_magnetic_probes(label=label, ax=ax)
        if not isinstance(self, OMFITdprobe) and plot_domain:
            self.plot_domain(ax=ax)
        ax.autoscale(tight=True)

    def __call__(self, *args, **kw):
        r"""
        Done to override default OMFIT GUI behaviour for OMFITnamelist
        """
        return self.plotFigure(*args, **kw)

    def aggregate_oh_coils(self, index=None, group=None):
        """
        Aggregate selected OH coils into a single coil

        :param index of OH coils to aggregate

        :param group: group of OH coils to aggregate
        """
        if group is not None:
            index = np.where(self['OH'][:, 4] == group)[0]

        mx = np.min(self['OH'][index, 0] - self['OH'][index, 2] / 2.0)
        MX = np.max(self['OH'][index, 0] + self['OH'][index, 2] / 2.0)
        my = np.min(self['OH'][index, 1] - self['OH'][index, 3] / 2.0)
        MY = np.max(self['OH'][index, 1] + self['OH'][index, 3] / 2.0)
        group = self['OH'][index, 4][0]

        aggregated_coil = [(MX + mx) / 2.0, (MY + my) / 2.0, (MX - mx), (MY - my), group]

        index = np.array(sorted(list(set(list(range(self['OH'].shape[0]))).difference(list(index)))))
        self['OH'] = self['OH'][index, :]
        self['OH'] = np.vstack((self['OH'], aggregated_coil))

    def disable_oh_group(self, group):
        """
        remove OH group

        :param group: group of OH coils to disable
        """
        index = np.where(self['OH'][:, 4] != group)[0]
        self['OH'] = self['OH'][index, :]
        groups = np.unique(self['OH'][:, 4])
        groups_mapper = dict(zip(groups, range(1, len(groups) + 1)))
        for k in range(self['OH'].shape[0]):
            self['OH'][k, 4] = groups_mapper[self['OH'][k, 4]]

    def change_R(self, deltaR=0.0):
        """
        add or subtract a deltaR to coils, flux loops and magnetic
        probes radial location effectively changing the aspect ratio

        :param deltaR: radial shift in m
        """
        for system in ['FC', 'OH', 'VESSEL']:
            self[system][:, 0] += deltaR
        for item in self['IN3']:
            if item[0].upper() in ['R', 'X']:
                self['IN3'][item] += deltaR

    def change_Z(self, deltaZ=0.0):
        """
        add or subtract a deltaZ to coils, flux loops and magnetic
        probes radial location effectively changing the aspect ratio

        :param deltaR: radial shift in m
        """
        for system in ['FC', 'OH', 'VESSEL']:
            self[system][:, 1] += deltaZ
        for item in self['IN3']:
            if item[0].upper() in ['Z', 'Y']:
                self['IN3'][item] += deltaZ

    def scale_system(self, scale_factor=0.0):
        """
        scale coils, flux loops and magnetic
        probes radial location effectively changing the major radius
        holding aspect ratio fixed

        :param scale_factor: scaling factor to multiple system by
        """
        for system in ['FC', 'OH', 'VESSEL']:
            self[system][:, 0] *= scale_factor
            self[system][:, 1] *= scale_factor
        for item in self['IN3']:
            if item[0].upper() in ['R', 'X']:
                self['IN3'][item] *= scale_factor
            if item[0].upper() in ['Z', 'Y']:
                self['IN3'][item] *= scale_factor

    def fill_coils_from(self, mhdin):
        """
        Copy FC, OH, VESSEL from passed object into current object,
        without changing the number of elements in current object.

        This requires that the number of elements in the current object
        is greater or equal than the number of elements in the passed object.
        The extra elements in the current object will be placed at R=0, Z=0

        :param mhdin: other mhdin object
        """
        self['FC'][:, 0] = 0.01
        self['FC'][:, 1] = self.invalid
        self['FC'][:, 2] = 0.01
        self['FC'][:, 3] = 0.01
        self['FC'][:, 4] = 0.0
        self['FC'][:, 5] = 90.0

        self['OH'][:, 0] = 0.01
        self['OH'][:, 1] = self.invalid
        self['OH'][:, 2] = 0.01
        self['OH'][:, 3] = 0.01
        if len(mhdin['OH']):
            delta_shape = self['OH'].shape[0] - mhdin['OH'].shape[0]
            if delta_shape and max(mhdin['OH'][:, 4]) >= max(self['OH'][:, 4]):
                raise ValueError('OMFITmhdin.fill_coils_from() has no space for an extra `invalid` OH group')
            self['OH'][mhdin['OH'].shape[0] :, 4] = np.linspace(
                max(mhdin['OH'][:, 4]) + 1, max(self['OH'][:, 4]) + 0.9999, delta_shape
            ).astype(int)
            self['OH'][: mhdin['OH'].shape[0], 4] = 0.0

        self['VESSEL'][:, 0] = 0.01
        self['VESSEL'][:, 1] = self.invalid
        self['VESSEL'][:, 2] = 0.01
        self['VESSEL'][:, 3] = 0.01
        self['VESSEL'][:, 4] = 0.0
        self['VESSEL'][:, 5] = 90.0
        self['IN3']['VSNAME'] = ['DUMMY_%d' % k for k in range(self['VESSEL'].shape[0])]
        if len(mhdin['VESSEL']):
            self['IN3']['VSNAME'][: self['VESSEL'].shape[0]] = mhdin['IN3'].get('VSNAME', ['vessel'] * self['VESSEL'].shape[0])

        for system in ['FC', 'OH', 'VESSEL']:
            if len(mhdin[system]):
                self[system][: len(mhdin[system])] = mhdin[system]

    def modify_vessel_elements(self, index, action=['keep', 'delete'][0]):
        """
        Utility function to remove vessel elements

        :param index: index of the vessel elements to either keep or delete

        :param action: can be either 'keep' or 'delete'
        """
        keep_index = index
        if action == 'delete':
            keep_index = [k for k in range(len(self['IN3']['VSNAME'])) if k not in index]
        self['VESSEL'] = self['VESSEL'][keep_index]
        self['IN3']['VSNAME'] = np.array(self['IN3']['VSNAME'])[keep_index]

    def fill_probes_loops_from(self, mhdin):
        """
        Copy flux loops and magnetic probes from other object into current object,
        without changing the number of elements in current object

        This requires that the number of elements in the current object
        is greater or equal than the number of elements in the passed object.
        The extra elements in the current object will be placed at R=0, Z=0

        :param mhdin: other mhdin object
        """
        for system in [['XMP2', 'YMP2', 'SMP2', 'AMP2', 'MPNAM2'], ['RSI', 'ZSI', 'LPNAME']]:
            for item in system:
                if item in ['MPNAM2', 'LPNAME']:
                    self['IN3'][item] = ['DUMMY_%d' % k for k in range(len(self['IN3'][item]))]
                    self['IN3'][item][: len(mhdin['IN3'][item])] = mhdin['IN3'][item]
                else:
                    self['IN3'][item] *= 0
                    if item[0] in ['X', 'R']:
                        self['IN3'][item] += 0.01
                    elif item[0] in ['Y', 'Z']:
                        self['IN3'][item] += -self.invalid
                    elif item[0] in ['S']:
                        self['IN3'][item] += 0.01
                    self['IN3'][item][: len(mhdin['IN3'][item])] = mhdin['IN3'][item]

    def fill_scalars_from(self, mhdin):
        """
        copy scalar quantities in IN3 namelist
        without overwriting ['IFCOIL', 'IECOIL', 'IVESEL']

        :param mhdin: other mhdin object
        """
        for item in self['IN3']:
            if item in mhdin['IN3']:
                if isinstance(mhdin['IN3'][item], (int, float)):
                    if item not in ['IFCOIL', 'IECOIL', 'IVESEL']:
                        self['IN3'][item] = mhdin['IN3'][item]
                else:
                    self['IN3'][item] = np.array(self['IN3'][item])

    def pretty_print(self, default_tilt2=0):
        for item in ['FC', 'OH', 'VESSEL']:
            print('# ' + '=' * len(item))
            print('# ' + item)
            print('# ' + '=' * len(item))
            for row in range(self[item].shape[0]):
                start = ' '
                end = ','
                if row == 0:
                    start = '['
                if row == self[item].shape[0] - 1:
                    end = ']'
                tmp = self[item][row, :].copy()
                if len(tmp) == 6 and tmp[5] == 90:
                    tmp[5] = default_tilt2
                print(start + '[' + ', '.join(map(lambda x: repr(x), tmp)) + ']' + end)

        print('# ==========')
        print('# Flux loops')
        print('# ==========')
        print('R_flux_loop = ', end='')
        print(repr(self['IN3']['RSI']))
        print('Z_flux_loop = ', end='')
        print(repr(self['IN3']['ZSI']))
        print('name_flux_loop = ', end='')
        print(repr(self['IN3']['LPNAME']))

        print('# ===============')
        print('# Magnetic probes')
        print('# ===============')
        print('R_magnetic = ', end='')
        print(repr(self['IN3']['XMP2']))
        print('Z_magnetic = ', end='')
        print(repr(self['IN3']['YMP2']))
        print('A_magnetic = ', end='')
        print(repr(self['IN3']['AMP2']))
        print('S_magnetic = ', end='')
        print(repr(self['IN3']['SMP2']))
        print('name_magnetic = ', end='')
        print(repr(self['IN3']['MPNAM2']))

        return self

    def to_omas(self, ods=None, update=['oh', 'pf_active', 'flux_loop', 'b_field_pol_probe']):
        """
        Transfers data in EFIT mhdin.dat format to ODS

        WARNING: only rudimentary identifies are assigned for pf_active
        You should assign your own identifiers and only rely on this function to assign numerical geometry data.

        :param ods: ODS instance
            Data will be added in-place

        :param update: systems to populate
            ['oh', 'pf_active', 'flux_loop', 'b_field_pol_probe']
            ['magnetics'] will enable both ['flux_loop', 'b_field_pol_probe']
            NOTE that in IMAS the OH information goes under `pf_active`

        :return: ODS instance
        """

        from omas.omas_plot import geo_type_lookup
        from omas import omas_environment, ODS

        if ods is None:
            ods = ODS()

        # oh
        if 'oh' in update:
            coil_data = self['OH']
            turns = self['IN3']['ECTURN']
            elements_id = (self['IN3']['ECID'] - 1).astype(int)
            rect_code = geo_type_lookup('rectangle', 'pf_active', ods.imas_version, reverse=True)
            for i in range(len(coil_data)):
                c = elements_id[i]
                e = sum(elements_id[:i] == elements_id[i])
                ods['pf_active.coil'][c]['name'] = f'OH{c}'
                ods['pf_active.coil'][c]['identifier'] = f'OH{c}'
                ods['pf_active.coil'][c]['element'][e]['name'] = f'OH{c}_{e}'
                ods['pf_active.coil'][c]['element'][e]['identifier'] = f'OH{c}_{e}'
                ods['pf_active.coil'][c]['element'][e]['turns_with_sign'] = turns[i]
                rect = ods['pf_active.coil'][c]['element'][e]['geometry.rectangle']
                rect['r'] = coil_data[i, 0]
                rect['z'] = coil_data[i, 1]
                rect['width'] = coil_data[i, 2]
                rect['height'] = coil_data[i, 3]
                ods['pf_active.coil'][c]['element'][e]['geometry.geometry_type'] = rect_code

        # pf_active
        if 'pf_active' in update:
            coil_data = self['FC']
            turns = self['IN3']['FCTURN']
            elements_id = (self['IN3']['FCID'] - 1).astype(int)
            rect_code = geo_type_lookup('rectangle', 'pf_active', ods.imas_version, reverse=True)
            outline_code = geo_type_lookup('outline', 'pf_active', ods.imas_version, reverse=True)
            offset = len(ods['pf_active.coil'])
            for i in range(len(coil_data)):
                c = elements_id[i] + offset
                e = sum(elements_id[:i] == elements_id[i])
                ods['pf_active.coil'][c]['name'] = f'PF{c}'
                ods['pf_active.coil'][c]['identifier'] = f'PF{c}'
                ods['pf_active.coil'][c]['element'][e]['name'] = f'PF{c}_{e}'
                ods['pf_active.coil'][c]['element'][e]['identifier'] = f'PF{c}_{e}'
                ods['pf_active.coil'][c]['element'][e]['turns_with_sign'] = turns[i]
                if coil_data[i, 4] == 0 and coil_data[i, 5] == 0:
                    rect = ods['pf_active.coil'][c]['element'][e]['geometry.rectangle']
                    rect['r'] = coil_data[i, 0]
                    rect['z'] = coil_data[i, 1]
                    rect['width'] = coil_data[i, 2]
                    rect['height'] = coil_data[i, 3]
                    ods['pf_active.coil'][c]['element'][e]['geometry.geometry_type'] = rect_code
                else:
                    outline = ods['pf_active.coil'][c]['element'][e]['geometry.outline']
                    fdat = copy.deepcopy(coil_data[i])
                    fdat[4] = -coil_data[i, 4] * np.pi / 180.0
                    fdat[5] = -(coil_data[i, 5] * np.pi / 180.0 if coil_data[i, 5] != 0 else np.pi / 2)
                    outline['r'] = [
                        fdat[0] - fdat[2] / 2.0 - fdat[3] / 2.0 * np.tan((np.pi / 2.0 + fdat[5])),
                        fdat[0] - fdat[2] / 2.0 + fdat[3] / 2.0 * np.tan((np.pi / 2.0 + fdat[5])),
                        fdat[0] + fdat[2] / 2.0 + fdat[3] / 2.0 * np.tan((np.pi / 2.0 + fdat[5])),
                        fdat[0] + fdat[2] / 2.0 - fdat[3] / 2.0 * np.tan((np.pi / 2.0 + fdat[5])),
                    ]
                    outline['z'] = [
                        fdat[1] - fdat[3] / 2.0 - fdat[2] / 2.0 * np.tan(-fdat[4]),
                        fdat[1] + fdat[3] / 2.0 - fdat[2] / 2.0 * np.tan(-fdat[4]),
                        fdat[1] + fdat[3] / 2.0 + fdat[2] / 2.0 * np.tan(-fdat[4]),
                        fdat[1] - fdat[3] / 2.0 + fdat[2] / 2.0 * np.tan(-fdat[4]),
                    ]
                    ods['pf_active.coil'][c]['element'][e]['geometry.geometry_type'] = outline_code

        # flux_loop
        if 'magnetics' in update or 'flux_loop' in update:
            R_flux_loop = self['IN3']['RSI']
            Z_flux_loop = self['IN3']['ZSI']
            name_flux_loop = list(map(lambda x: x.strip(), self['IN3']['LPNAME']))
            with omas_environment(ods, cocosio=1):
                for k, (r, z, name) in enumerate(zip(R_flux_loop, Z_flux_loop, name_flux_loop)):
                    ods[f'magnetics.flux_loop.{k}.name'] = name
                    ods[f'magnetics.flux_loop.{k}.identifier'] = name
                    ods[f'magnetics.flux_loop.{k}.position[0].r'] = r
                    ods[f'magnetics.flux_loop.{k}.position[0].z'] = z
                    ods[f'magnetics.flux_loop.{k}.type.index'] = 1

        # b_field_pol_probe
        if 'magnetics' in update or 'b_field_pol_probe' in update:
            R_magnetic = self['IN3']['XMP2']
            Z_magnetic = self['IN3']['YMP2']
            A_magnetic = self['IN3']['AMP2']
            S_magnetic = self['IN3']['SMP2']
            name_magnetic = list(map(lambda x: x.strip(), self['IN3']['MPNAM2']))
            with omas_environment(ods, cocosio=1):
                for k, (r, z, a, s, name) in enumerate(zip(R_magnetic, Z_magnetic, A_magnetic, S_magnetic, name_magnetic)):
                    ods[f'magnetics.b_field_pol_probe.{k}.name'] = name
                    ods[f'magnetics.b_field_pol_probe.{k}.identifier'] = name
                    ods[f'magnetics.b_field_pol_probe.{k}.position.r'] = r
                    ods[f'magnetics.b_field_pol_probe.{k}.position.z'] = z
                    ods[f'magnetics.b_field_pol_probe.{k}.length'] = s
                    ods[f'magnetics.b_field_pol_probe.{k}.poloidal_angle'] = -a / 180 * np.pi
                    ods[f'magnetics.b_field_pol_probe.{k}.toroidal_angle'] = 0.0 / 180 * np.pi
                    ods[f'magnetics.b_field_pol_probe.{k}.type.index'] = 1
                    ods[f'magnetics.b_field_pol_probe.{k}.turns'] = 1

        return ods


class OMFITdprobe(OMFITmhdin):
    @dynaLoad
    def load(self, *args, **kw):
        super().load(*args, **kw)
        for item in list(self['IN3'].keys()):
            if item.upper() not in [
                'RSISVS',
                'TURNFC',
                'VSNAME',
                'LPNAME',
                'MPNAM2',
                'RSI',
                'ZSI',
                'XMP2',
                'YMP2',
                'AMP2',
                'SMP2',
                'PATMP2',
                'IECOIL',
                'IVESEL',
                'IFCOIL',
            ]:
                del self['IN3'][item]


class OMFITnstxMHD(SortedDict, OMFITascii):
    """
    OMFIT class to read NSTX MHD device files such as `device01152015.dat`, `diagSpec01152015.dat` and `signals_020916_PF4.dat`
    """

    def __init__(self, filename, use_leading_comma=None, **kw):
        r"""
        OMFIT class to parse NSTX MHD device files

        :param filename: filename

        :param \**kw: arguments passed to __init__ of OMFITascii
        """
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        self.clear()
        with open(self.filename, 'r') as f:
            lines = f.read().split('\n')
        lines = [line for line in lines if len(line.strip()) and not line.startswith(';')]
        self['all'] = {}
        for line in lines:
            line, description = (line + ';').split(';', 1)
            line = line.split()
            if line[1] not in self:
                self[line[1]] = {}
            piece = len(self[line[1]])
            # signals.dat
            if len(line) in [16, 17]:
                self.type = 'signals'
                self[line[1]][piece] = dict(
                    zip(
                        'name type map_var map_index mds_tree read_sig rel_error abs_error sig_thresh use_err scale pri fitwt t_index t_smooth mds_name'.split(),
                        line,
                    )
                )
            # diagspec.dat
            elif len(line) == 12:
                self.type = 'diagspec'
                self[line[1]][piece] = dict(zip('name type id rc zc wc hc ac ac2 turns div material'.split(), line))
            # device.dat
            elif len(line) == 8:
                self.type = 'device'
                self[line[1]][piece] = dict(zip('tag type units rc zc pol_ang tor_ang1 tor_ang2'.split(), line))
            else:
                raise ValueError(f'Format not recognized {len(line)}')
            self[line[1]][piece]['description'] = description.strip(';')
            for item in self[line[1]][piece]:
                try:
                    self[line[1]][piece][item] = ast.literal_eval(self[line[1]][piece][item])
                except (ValueError, SyntaxError):
                    pass
            self['all'][line[0]] = self[line[1]][piece]

        # postprocess
        if self.type == 'signals':
            mds_tree_map = {'o': 'operations', 'e': 'engineering', 'a': 'activespec', 'r': 'radiatiion', 'E2': 'efit02', '-': 'computed'}
            for group in self:
                if group not in ['all']:
                    for item in self[group]:
                        self[group][item]['mds_tree'] = mds_tree_map.get(self[group][item]['mds_tree'], self[group][item]['mds_tree'])
            # sort entries according to their `map` fields
            self['mappings'] = {}
            for group in self:
                for item in self[group]:
                    map_var = self[group][item].get('map_var', 'none')
                    self['mappings'].setdefault(map_var, {})
                    map_index = self[group][item].get('map_index', len(self['mappings'][map_var]))
                    self['mappings'][map_var][map_index] = value = self[group][item]
                    if 'mds_tree' in value:
                        if value['mds_tree'] == 'computed' and value['mds_name'] in self['all']:
                            value['mds_tree_resolved'] = self['all'][value['mds_name']]['mds_tree']
                            value['mds_name_resolved'] = self['all'][value['mds_name']]['mds_name'] + '/' + str(value['scale'])
                        else:
                            value['mds_tree_resolved'] = value['mds_tree']
                            value['mds_name_resolved'] = value['mds_name']
        return self

    def pretty_print(self):
        """
        Print data in file as arrays, as it is needed for a fortran namelist
        """
        for group in self:
            for item in self[group][0]:
                print(f"{group.lower()}_{item.split('(')[0].lower()} = ", end='')
                print([self[group][k][item] for k in self[group]])
        return self


def get_mhdindat(device, pulse=None):
    """
    :param device: name of the device to get the mhdin.dat file of

    :param pulse: for certain devices the mhdin.dat depends on the shot number

    :return: OMFITmhdin object
    """
    device = tokamak(device, 'OMAS', True, translation_dict={'nstx': 'nstxu'})

    if device == 'nstxu':
        from omas.machine_mappings.nstxu import nstx_filenames

        if pulse is None:
            pulse = 1e10
        mhdin_dat_filename = nstx_filenames('mhdin', pulse)

    else:
        from omas import omas_dir

        mhdin_dat_filename = os.sep.join([omas_dir, 'machine_mappings', 'support_files', device, 'mhdin.dat'])

    from omas.machine_mappings._common import get_support_file

    return get_support_file(OMFITmhdin, mhdin_dat_filename)


############################################
if '__main__' == __name__:
    from matplotlib import pyplot

    test_classes_main_header()
    for machine in ['nstx-u', 'diii-d']:
        tmp = OMFITmhdin(OMFITsrc + f'/../modules/EFUND/TEMPLATES/mhdin_{machine}.dat')
        tmp.load()
        tmp.pretty_print()
        tmp.plot(label=True)
        pyplot.show()
