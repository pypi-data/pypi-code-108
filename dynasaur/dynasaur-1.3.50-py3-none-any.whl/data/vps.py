import h5py
import numpy as np
from ..data.dynasaur_definitions import DynasaurDefinitions
from ..utils.logger import ConsoleLogger
from ..utils.constants import VPSDataConstant, DataChannelTypesNodout, DataChannelTypesSecforc, DataChannelTypesContact, \
    DataChannelTypesGlobalEnergy, DataChannelTypesRbdout, DataChannelTypesSbtout


class VPSData:
    """ """

    def __init__(self, vps_file_path):

        self.file_data = {}  # should be wrapped to binout data.

        self._vps_file_path = vps_file_path
        self._d = dict()
        self._ids = dict()

        with h5py.File(self._vps_file_path, 'r') as f:
            f['CSMEXPL/multistate'].visititems(self._get_available_data_types_dict)

        logger = ConsoleLogger()
        self.dynasaur_definitions = DynasaurDefinitions(logger)

    def _get_available_data_types_dict(self, name, node):
        """

        Args:
          name: 
          node: 

        Returns:

        """
        if isinstance(node, h5py.Dataset):
            if node.name.split("/")[-1] == 'res':  # result of data
                print(node.name)

                if node.parent.name.split("/")[5] in [VPSDataConstant.NODE]:
                    self._set_node_elements(node)

                elif node.parent.name.split("/")[5] in [VPSDataConstant.SECTION]:
                    self._set_section_elements(node)

                elif node.parent.name.split("/")[5] in [VPSDataConstant.JOINT]:
                    self._set_joint_elements(node)

                elif node.parent.name.split("/")[5] in [VPSDataConstant.SLIPRING]:
                    self._set_sbtout_elements(node)

                elif node.parent.name.split("/")[5] in [VPSDataConstant.CONTACT]:
                    self._set_contact_elements(node)

                elif node.parent.name.split("/")[5] in [VPSDataConstant.ENERGY_GLOBAL]:
                    self._set_global_energy_elements(node)

                elif node.parent.name.split("/")[5] in [VPSDataConstant.ENERGY_PART]:
                    self._set_part_energy_elements(node)

    def _args_to_data(self, args):
        """

        Args:
          args: 

        Returns:

        """
        data_type = ""
        data_channel = ""

        if args[1] == "time":
            with h5py.File(self._vps_file_path, 'r') as f:
                path = "/CSMEXPL/multistate/TIMESERIES1/multientityresults/MODEL/TIME/ZONE1_set1/erfblock/res"
                return (f[path][()][:, 0, 0])

        elif args[1] == "legend":
            with h5py.File(self._vps_file_path, 'r') as f:

                if args[0] == VPSDataConstant.SECFORC:
                    legend = f["/CSMEXPL/constant/attributes/SECTION/erfblock/title"][()]

                elif args[0] == VPSDataConstant.NODOUT:
                    legend = f["/CSMEXPL/constant/attributes/NODE/erfblock/title"][()]

                elif args[0] == VPSDataConstant.RCFORC:
                    legend = f["/CSMEXPL/constant/attributes/CONTACT/erfblock/title"][()]

                elif args[0] == VPSDataConstant.MATSUM:
                    legend = f["/CSMEXPL/constant/attributes/PART/erfblock/title"][()]

                elif args[0] == VPSDataConstant.RIGID_BODY:
                    legend = f["/CSMEXPL/constant/attributes/JOINT/erfblock/title"][()]

                elif args[0] == VPSDataConstant.SBTOUT:
                    legend = f["/CSMEXPL/constant/attributes/SLIPRING/erfblock/title"][()]

                else:
                    assert False

                assert (all([len(i) <= 80 for i in legend]))
                leg = "".join([i.decode("utf-8").ljust(80) for i in legend])
                return leg

        elif args[1] == "ids" or args[0] == VPSDataConstant.SBTOUT and args[1] == "slipring_ids":

            # check if data has been cached
            if args[0] in self._ids:
                return self._ids[args[0]]

            with h5py.File(self._vps_file_path, 'r') as f:
                if args[0] == VPSDataConstant.SECFORC:
                    # entids = f["/CSMEXPL/multistate/TIMESERIES1/multientityresults/" + VPSDataConstant.SECTION + "/Section_Force/ZONE1_set1/erfblock/entid"][()]
                    entids = f["/CSMEXPL/constant/attributes/SECTION/erfblock/entid"][()]
                    entid_translation = f["/CSMEXPL/constant/identifiers/SECTION/erfblock/entid"][()]
                    uids = f["/CSMEXPL/constant/identifiers/" + VPSDataConstant.SECTION + "/erfblock/uid"][()]

                elif args[0] == VPSDataConstant.RCFORC:
                    # entids = f["/CSMEXPL/multistate/TIMESERIES1/multientityresults/" + VPSDataConstant.CONTACT + "/Contact_Force/ZONE1_set1/erfblock/entid"][()]
                    entids = f["/CSMEXPL/constant/attributes/CONTACT/erfblock/entid"][()]
                    entid_translation = f["/CSMEXPL/constant/identifiers/CONTACT/erfblock/entid"][()]
                    uids = f["/CSMEXPL/constant/identifiers/CONTACT/erfblock/uid"][()]

                elif args[0] == VPSDataConstant.NODOUT:
                    entids = f["/CSMEXPL/constant/attributes/NODE/erfblock/entid"][()]
                    entid_translation = f["/CSMEXPL/constant/identifiers/NODE/erfblock/entid"][()]
                    uids = f["/CSMEXPL/constant/identifiers/NODE/erfblock/uid"][()]

                elif args[0] == VPSDataConstant.RIGID_BODY:
                    entids = f["/CSMEXPL/constant/attributes/JOINT/erfblock/entid"][()]
                    entid_translation = f["/CSMEXPL/constant/identifiers/JOINT/erfblock/entid"][()]
                    uids = f["/CSMEXPL/constant/identifiers/JOINT/erfblock/uid"][()]

                elif args[0] == VPSDataConstant.SBTOUT:
                    entids = f["/CSMEXPL/constant/attributes/"  + VPSDataConstant.SLIPRING + "/erfblock/entid"][()]
                    entid_translation = f["/CSMEXPL/constant/identifiers/" + VPSDataConstant.SLIPRING + "/erfblock/entid"][()]
                    uids = f["/CSMEXPL/constant/identifiers/"+ VPSDataConstant.SLIPRING + "/erfblock/uid"][()]

                elif args[0] == VPSDataConstant.MATSUM:
                    entids = f["/CSMEXPL/constant/attributes/PART/erfblock/entid"][()]
                    entid_translation = f["/CSMEXPL/constant/identifiers/PART/erfblock/entid"][()]
                    uids = f["/CSMEXPL/constant/identifiers/" + VPSDataConstant.ENERGY_PART + "/erfblock/uid"][()]

                elif args[0] == VPSDataConstant.GLSTAT:
                    return [0]

                else:
                    assert False

                assert len(entid_translation) == len(uids[:, 0])

                # TODO
                #  Guess that could be done more efficiently
                # entids is a list with length of the defined outputs (from the user)
                #    entid_translation maps the entids with the uids. For each entid
                #    we have to find the indices correct index in the entid_translation.
                #    With the index we are able to extract the correct ids of the channels written out
                #
                output_uids_idx = [list(entid_translation).index(i) for i in entids if i in list(entid_translation)]

                ids = uids[output_uids_idx][:, 0]
                self._ids[args[0]] = ids
                return ids

        if args[0] == VPSDataConstant.GLSTAT:
            data_type = VPSDataConstant.ENERGY_GLOBAL
            idx, data_channel = self._get_global_energy_index_and_data_channel(args[1])
            axis = 1

            search_string = "/CSMEXPL/multistate/TIMESERIES1/multientityresults/" + data_type + "/" + data_channel + "/ZONE1_set1/erfblock/res"

            with h5py.File(self._vps_file_path, 'r') as f:
                return np.linalg.norm(f[search_string][:, :, idx], axis=axis)

        if args[0] == VPSDataConstant.NODOUT:
            data_type = VPSDataConstant.NODE
            idx, data_channel = self._get_node_index_and_data_channel(args[1])

        elif args[0] == VPSDataConstant.SECFORC:
            data_type = VPSDataConstant.SECTION
            idx, data_channel = self._get_secforc_index_and_data_channel(args[1])

        elif args[0] == VPSDataConstant.RCFORC:
            data_type = VPSDataConstant.CONTACT
            idx, data_channel = self._get_contact_index_and_data_channel(args[1])

        elif args[0] == VPSDataConstant.RIGID_BODY:
            data_type = VPSDataConstant.JOINT
            idx, data_channel = self._get_rbdout_index_and_data_channel(args[1])

        elif args[0] == VPSDataConstant.SBTOUT:
            data_type = VPSDataConstant.SLIPRING
            idx, data_channel = self._get_sbtout_index_and_data_channel(args[1])

        elif args[0] == VPSDataConstant.MATSUM:
            data_type = VPSDataConstant.ENERGY_PART
            idx, data_channel = self._get_part_energy_index_and_data_channel(args[1])

        else:
            assert False

        search_string = "/CSMEXPL/multistate/TIMESERIES1/multientityresults/" + data_type + "/" + data_channel + "/ZONE1_set1/erfblock/res"

        if isinstance(idx, list):
            # list is returned, for resultant forces etc.
            with h5py.File(self._vps_file_path, 'r') as f:
                return np.linalg.norm(f[search_string][:, :, idx], axis=2)
        else:
            with h5py.File(self._vps_file_path, 'r') as f:
                return f[search_string][:, :, idx]

    def read(self, *argv):
        """

        Args:
          *argv: 

        Returns:

        """
        read_argv = []

        # 4 cases
        # TODO
        #
        #
        for i in argv:
            read_argv.append(i)
        assert 0 <= len(read_argv) <= 4

        if len(read_argv) == 0:
            return self._d.keys()

        if len(read_argv) == 1:
            if read_argv[0] in self._d.keys():
                return self._d[read_argv[0]]
            else:
                return []

        if len(read_argv) == 2:
            if read_argv[0] in self._d.keys():
                if read_argv[1] in self._d[read_argv[0]]:
                    # return data
                    return self._args_to_data(read_argv)
                else:
                    return []
            else:
                return []

    def _get_node_index_and_data_channel(self, arg):
        """

        Args:
          arg: 

        Returns:

        """
        # NODE
        if arg == DataChannelTypesNodout.X_COORDINATE or \
                arg == DataChannelTypesNodout.Y_COORDINATE or arg == DataChannelTypesNodout.Z_COORDINATE:
            idx = 0 if arg.startswith("x") else (1 if arg.startswith("y") else 2)
            data_channel = VPSDataConstant.COORDINATE

        elif arg == DataChannelTypesNodout.X_DISPLACEMENT or \
                arg == DataChannelTypesNodout.Y_DISPLACEMENT or arg == DataChannelTypesNodout.Z_DISPLACEMENT:
            idx = 0 if arg.startswith("x") else (1 if arg.startswith("y") else 2)
            data_channel = VPSDataConstant.TRANSLATION_DISPLACEMENT

        elif arg == DataChannelTypesNodout.X_VELOCITY or \
                arg == DataChannelTypesNodout.Y_VELOCITY or arg == DataChannelTypesNodout.Z_VELOCITY:
            idx = 0 if arg.startswith("x") else (1 if arg.startswith("y") else 2)
            data_channel = VPSDataConstant.VELOCITY

        elif arg == DataChannelTypesNodout.X_ACCELERATION or \
                arg == DataChannelTypesNodout.Y_ACCELERATION or arg == DataChannelTypesNodout.Z_ACCELERATION:
            idx = 0 if arg.startswith("x") else (1 if arg.startswith("y") else 2)
            data_channel = VPSDataConstant.ACCELERATION

        elif arg == DataChannelTypesNodout.RX_DISPLACEMENT or \
                arg == DataChannelTypesNodout.RY_DISPLACEMENT or arg == DataChannelTypesNodout.RZ_DISPLACEMENT:
            idx = 0 if arg.startswith("rx") else (1 if arg.startswith("ry") else 2)
            data_channel = VPSDataConstant.ROTATION_ANGLE

        elif arg == DataChannelTypesNodout.RX_VELOCITY or \
                arg == DataChannelTypesNodout.RY_VELOCITY or arg == DataChannelTypesNodout.RZ_VELOCITY:
            idx = 0 if arg.startswith("rx") else (1 if arg.startswith("ry") else 2)
            data_channel = VPSDataConstant.ROTATION_VELOCITY

        elif arg == DataChannelTypesNodout.RX_ACCELERATION or \
                arg == DataChannelTypesNodout.RY_ACCELERATION or arg == DataChannelTypesNodout.RZ_ACCELERATION:
            idx = 0 if arg.startswith("rx") else (1 if arg.startswith("ry") else 2)
            data_channel = VPSDataConstant.ROTATION_ACCELERATION

        else:
            # TODO: add console logger
            print("ID FAIL")
            return

        return idx, data_channel

    def _get_part_energy_index_and_data_channel(self, arg):
        """

        Args:
          arg: 

        Returns:

        """
        # MATSUM
        if arg == "hourglass_energy":
            idx = 0
            data_channel = "MHGL"
        elif arg == "internal_energy":
            idx = 0
            data_channel = "MINT"
        elif arg == "kinetic_energy":
            idx = 0
            data_channel = "MKIN"
        elif arg == "added_mass":
            idx = 0
            data_channel = "DMSC"
        else:
            # TODO: add console logger
            print("ID FAIL")
            return

        return idx, data_channel

    def _get_global_energy_index_and_data_channel(self, arg):
        """

        Args:
          arg: 

        Returns:

        """
        # GLSTAT
        if arg == DataChannelTypesGlobalEnergy.EXTERNAL_WORK:
            idx = 0
            data_channel = VPSDataConstant.ENERGY_GLOBAL_EXTERNAL

        elif arg == DataChannelTypesGlobalEnergy.INTERNAL_ENERGY or \
                arg == DataChannelTypesGlobalEnergy.TOTAL_ENERGY or arg == DataChannelTypesGlobalEnergy.KINETIC_ENERGY:
            idx = 0 if arg.startswith("kinetic") else (1 if arg.startswith("internal") else 2)
            data_channel = VPSDataConstant.ENERGY_GLOBAL_ENKIT

        elif arg == "time_step":
            idx = 0
            data_channel = "STEP"

        elif arg == "sliding_interface_energy":
            idx = 0
            data_channel = "TCNT"

        elif arg == "hourglass_energy":
            idx = 0
            data_channel = "THGL"

        elif arg == "added_mass":
            idx = 0
            data_channel = "DMAS"

        else:
            print("ID FAIL")
            return

        return idx, data_channel

    def _get_secforc_index_and_data_channel(self, arg):
        """

        Args:
          arg: 

        Returns:

        """
        # SECTION
        if arg == DataChannelTypesSecforc.X_CENTROID or \
                arg == DataChannelTypesSecforc.Y_CENTROID or arg == DataChannelTypesSecforc.Z_CENTROID:
            idx = 0 if arg.startswith("x") else (1 if arg.startswith("y") else 2)
            data_channel = VPSDataConstant.SECTION_CENTRE_POSITION

        elif arg == DataChannelTypesSecforc.X_FORCE or \
                arg == DataChannelTypesSecforc.Y_FORCE or arg == DataChannelTypesSecforc.Z_FORCE:
            idx = 0 if arg.startswith("x") else (1 if arg.startswith("y") else 2)
            data_channel = VPSDataConstant.SECTION_FORCE

        elif arg == DataChannelTypesSecforc.TOTAL_FORCE:
            idx = [0, 1, 2]
            data_channel = VPSDataConstant.SECTION_FORCE

        elif arg == DataChannelTypesSecforc.X_MOMENT or \
                arg == DataChannelTypesSecforc.Y_MOMENT or arg == DataChannelTypesSecforc.Z_MOMENT:
            idx = 0 if arg.startswith("x") else (1 if arg.startswith("y") else 2)
            data_channel = VPSDataConstant.SECTION_MOMENT

        elif arg == DataChannelTypesSecforc.TOTAL_MOMENT:
            idx = [0, 1, 2]
            data_channel = VPSDataConstant.SECTION_MOMENT

        else:
            # TODO: add console logger
            print("ID FAIL")
            return

        return idx, data_channel

    def _get_part_index_and_data_channel(self, arg):
        """

        Args:
          arg: 

        Returns:

        """
        if arg is None:
            idx = 0
            data_channel = "abc"
        else:
            # TODO: add console logger
            print("ID FAIL")
            return

        return idx, data_channel

    def _get_contact_index_and_data_channel(self, arg):
        """

        Args:
          arg: 

        Returns:

        """
        if arg == DataChannelTypesContact.X_FORCE or \
                arg == DataChannelTypesContact.Y_FORCE or arg == DataChannelTypesSecforc.Z_FORCE:
            idx = 0 if arg.startswith("x") else (1 if arg.startswith("y") else 2)
            data_channel = VPSDataConstant.CONTACT_FORCE

        elif arg == DataChannelTypesSecforc.TOTAL_FORCE:
            idx = [0, 1, 2]
            data_channel = VPSDataConstant.CONTACT_FORCE
        else:
            # TODO: add console logger
            print("ID FAIL")
            return

        return idx, data_channel

    def _get_sbtout_index_and_data_channel(self, arg):

        if arg == DataChannelTypesSbtout.RING_SLIP:
            idx = 0
            data_channel = VPSDataConstant.SLIPRING_VARIABLES

        else:
            # TODO: add console logger
            print("ID FAIL")
            return

        return idx, data_channel

    def _get_rbdout_index_and_data_channel(self, arg):
        """

        :param arg:
        :return:
        """
        print(arg)
        # TODO
        if arg == DataChannelTypesRbdout.LOCAL_RDZ:
            idx = 0
            data_channel = VPSDataConstant.JOINT_RELATIVE_ROTATION_R

        # if arg == DataChannelTypesRbdout.LOCAL_RDY:
        #     idx= 0
        #     data_channel = VPSDataConstant.JOINT_RELATIVE_ROTATION_S_I
        #
        # if arg == DataChannelTypesRbdout.LOCAL_RDZ:
        #     idx = 0
        #     data_channel = VPSDataConstant.JOINT_RELATIVE_ROTATION_T_II


        else:
            # TODO: add console logger
            print(f"{arg} for ID FAIL")
            return

        return idx, data_channel


    def _set_node_elements(self, node):
        """

        Args:
          node: 

        Returns:

        """
        if VPSDataConstant.NODOUT not in self._d.keys():
            self._d[VPSDataConstant.NODOUT] = ["ids", "time", "legend"]
        idx_of_data = node.parent.name.split("/").index(node.parent.name.split("/")[5]) + 1
        # TODO
        if node.parent.name.split("/")[idx_of_data] == VPSDataConstant.COORDINATE:
            self._d[VPSDataConstant.NODOUT].extend([DataChannelTypesNodout.X_COORDINATE,
                                                    DataChannelTypesNodout.Y_COORDINATE,
                                                    DataChannelTypesNodout.Z_COORDINATE])
        elif node.parent.name.split("/")[idx_of_data] == VPSDataConstant.TRANSLATION_DISPLACEMENT:
            self._d[VPSDataConstant.NODOUT].extend([DataChannelTypesNodout.X_DISPLACEMENT,
                                                    DataChannelTypesNodout.Y_DISPLACEMENT,
                                                    DataChannelTypesNodout.Z_DISPLACEMENT])
        elif node.parent.name.split("/")[idx_of_data] == VPSDataConstant.VELOCITY:
            self._d[VPSDataConstant.NODOUT].extend([DataChannelTypesNodout.X_VELOCITY,
                                                    DataChannelTypesNodout.Y_VELOCITY,
                                                    DataChannelTypesNodout.Z_VELOCITY])
        elif node.parent.name.split("/")[idx_of_data] == VPSDataConstant.ACCELERATION:
            self._d[VPSDataConstant.NODOUT].extend([DataChannelTypesNodout.X_ACCELERATION,
                                                    DataChannelTypesNodout.Y_ACCELERATION,
                                                    DataChannelTypesNodout.Z_ACCELERATION])
        elif node.parent.name.split("/")[idx_of_data] == VPSDataConstant.ROTATION_ANGLE:
            self._d[VPSDataConstant.NODOUT].extend([DataChannelTypesNodout.RX_DISPLACEMENT,
                                                    DataChannelTypesNodout.RY_DISPLACEMENT,
                                                    DataChannelTypesNodout.RZ_DISPLACEMENT])
        elif node.parent.name.split("/")[idx_of_data] == VPSDataConstant.ROTATION_VELOCITY:
            self._d[VPSDataConstant.NODOUT].extend([DataChannelTypesNodout.RX_VELOCITY,
                                                    DataChannelTypesNodout.RY_VELOCITY,
                                                    DataChannelTypesNodout.RZ_VELOCITY])
        elif node.parent.name.split("/")[idx_of_data] == VPSDataConstant.ROTATION_ACCELERATION:
            self._d[VPSDataConstant.NODOUT].extend([DataChannelTypesNodout.RX_ACCELERATION,
                                                    DataChannelTypesNodout.RY_ACCELERATION,
                                                    DataChannelTypesNodout.RZ_ACCELERATION])

    def _set_contact_elements(self, node):
        """

        Args:
          node: 

        Returns:

        """
        if VPSDataConstant.RCFORC not in self._d.keys():
            self._d[VPSDataConstant.RCFORC] = ["ids", "time", "legend"]
        idx_of_data = node.parent.name.split("/").index(node.parent.name.split("/")[5]) + 1

        if node.parent.name.split("/")[idx_of_data] == VPSDataConstant.CONTACT_FORCE:
            self._d[VPSDataConstant.RCFORC].extend([DataChannelTypesContact.X_FORCE,
                                                    DataChannelTypesContact.Y_FORCE,
                                                    DataChannelTypesContact.Z_FORCE])

    def _set_global_energy_elements(self, node):
        """

        Args:
          node: 

        Returns:

        """
        if VPSDataConstant.GLSTAT not in self._d.keys():
            self._d[VPSDataConstant.GLSTAT] = ["ids", "time"]
        idx_of_data = node.parent.name.split("/").index(node.parent.name.split("/")[5]) + 1

        if node.parent.name.split("/")[idx_of_data] == VPSDataConstant.ENERGY_GLOBAL_EXTERNAL:
            self._d[VPSDataConstant.GLSTAT].extend([DataChannelTypesGlobalEnergy.EXTERNAL_WORK])

        elif node.parent.name.split("/")[idx_of_data] == VPSDataConstant.ENERGY_GLOBAL_ENKIT:
            self._d[VPSDataConstant.GLSTAT].extend([DataChannelTypesGlobalEnergy.KINETIC_ENERGY,
                                                    DataChannelTypesGlobalEnergy.INTERNAL_ENERGY,
                                                    DataChannelTypesGlobalEnergy.TOTAL_ENERGY])

        elif node.parent.name.split("/")[idx_of_data] == "STEP":
            self._d[VPSDataConstant.GLSTAT].extend(["time_step"])

        elif node.parent.name.split("/")[idx_of_data] == "TCNT":
            self._d[VPSDataConstant.GLSTAT].extend(["sliding_interface_energy"])

        elif node.parent.name.split("/")[idx_of_data] == "THGL":
            self._d[VPSDataConstant.GLSTAT].extend(["hourglass_energy"])

        elif node.parent.name.split("/")[idx_of_data] == "DMAS":
            self._d[VPSDataConstant.GLSTAT].extend(["added_mass"])

    def _set_part_energy_elements(self, node):
        """

        Args:
          node: 

        Returns:

        """
        if VPSDataConstant.MATSUM not in self._d.keys():
            self._d[VPSDataConstant.MATSUM] = ["ids", "time", "legend"]

        idx_of_data = node.parent.name.split("/").index(node.parent.name.split("/")[5]) + 1

        if node.parent.name.split("/")[idx_of_data] == "DMSC":
            self._d[VPSDataConstant.MATSUM].extend(["added_mass"])

        elif node.parent.name.split("/")[idx_of_data] == "MHGL":
            self._d[VPSDataConstant.MATSUM].extend(["hourglass_energy"])

        elif node.parent.name.split("/")[idx_of_data] == "MINT":
            self._d[VPSDataConstant.MATSUM].extend(["internal_energy"])

        elif node.parent.name.split("/")[idx_of_data] == "MKIN":
            self._d[VPSDataConstant.MATSUM].extend(["kinetic_energy"])

        # idx_of_data = node.parent.name.split("/").index(node.parent.name.split("/")[5]) + 1


    def _set_sbtout_elements(self, node):
        """

        Args:
          node:

        Returns:

        """
        if node.parent.name.split("/")[5] == VPSDataConstant.SLIPRING:
            if VPSDataConstant.SBTOUT not in self._d.keys():
                self._d[VPSDataConstant.SBTOUT] = ["slipring_ids", "time", "legend"]
            idx_of_data = node.parent.name.split("/").index(node.parent.name.split("/")[5]) + 1
            #         # TODO
            #         print("*******************************************")
            #         print(node.parent.name.split("/")[idx_of_data])
            #         print("-------------------------------------------")

            if node.parent.name.split("/")[idx_of_data] == VPSDataConstant.SLIPRING_VARIABLES:
                self._d[VPSDataConstant.SBTOUT].extend([DataChannelTypesSbtout.RING_SLIP])

    def _set_joint_elements(self, node):
        """

        Args:
          node:

        Returns:

        """
        if node.parent.name.split("/")[5] == VPSDataConstant.JOINT:
            if VPSDataConstant.RIGID_BODY not in self._d.keys():
                self._d[VPSDataConstant.RIGID_BODY] = ["ids", "time", "legend"]
            idx_of_data = node.parent.name.split("/").index(node.parent.name.split("/")[5]) + 1
            #         # TODO
            #         print("*******************************************")
            #         print(node.parent.name.split("/")[idx_of_data])
            #         print("-------------------------------------------")

            if node.parent.name.split("/")[idx_of_data] == VPSDataConstant.JOINT_RELATIVE_ROTATION_R:
                self._d[VPSDataConstant.RIGID_BODY].extend([DataChannelTypesRbdout.LOCAL_RDZ])


    def _set_section_elements(self, node):
        """

        Args:
          node: 

        Returns:

        """
        if node.parent.name.split("/")[5] == VPSDataConstant.SECTION:
            if VPSDataConstant.SECFORC not in self._d.keys():
                self._d[VPSDataConstant.SECFORC] = ["ids", "time", "legend"]
            idx_of_data = node.parent.name.split("/").index(node.parent.name.split("/")[5]) + 1
            # #         # TODO
            #         print("*******************************************")
            #         print(node.parent.name.split("/")[idx_of_data])
            #         print("-------------------------------------------")

            if node.parent.name.split("/")[idx_of_data] == VPSDataConstant.SECTION_CENTRE_POSITION:
                self._d[VPSDataConstant.SECFORC].extend([DataChannelTypesSecforc.X_CENTROID,
                                                         DataChannelTypesSecforc.Y_CENTROID,
                                                         DataChannelTypesSecforc.Z_CENTROID])
            elif node.parent.name.split("/")[idx_of_data] == VPSDataConstant.SECTION_FORCE:
                self._d[VPSDataConstant.SECFORC].extend([DataChannelTypesSecforc.X_FORCE,
                                                         DataChannelTypesSecforc.Y_FORCE,
                                                         DataChannelTypesSecforc.Z_FORCE,
                                                         DataChannelTypesSecforc.TOTAL_FORCE])
            elif node.parent.name.split("/")[idx_of_data] == VPSDataConstant.SECTION_MOMENT:
                self._d[VPSDataConstant.SECFORC].extend([DataChannelTypesSecforc.X_MOMENT,
                                                         DataChannelTypesSecforc.Y_MOMENT,
                                                         DataChannelTypesSecforc.Z_MOMENT,
                                                         DataChannelTypesSecforc.TOTAL_MOMENT])
