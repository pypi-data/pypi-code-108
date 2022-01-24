"""
A module for instantiating clusters for use in ClusterGraph objects.
"""
# Standard imports
import uuid
import copy

# Local imports
from veroku._constants import DEFAULT_FACTOR_RTOL, DEFAULT_FACTOR_ATOL
FIX_NON_PSD_MATRICES = False

# TODO: add evidence observation functionality
#   (perhaps only important for non-linear gaussian and similar approximate transformation factors)

# pylint: disable=protected-access


class Cluster:
    """
    A class for instantiating clusters for use in ClusterGraph objects.
    """

    def __init__(self, factor, cluster_name_prefix=""):
        """
        Construct a cluster with an initial factor potential.

        :param Factor factor: The factor to use in the cluster
        :param str cluster_name_prefix: The name of the cluster.
        """
        self._factor = factor
        # self._cluster_id = name if name is not None else str(uuid.uuid1())
        # self._cluster_id = name if name is not None else str(factor.var_names)
        self._cluster_id = cluster_name_prefix + ",".join(factor.var_names)
        self._neighbour_sepsets = {}  # neighbour_id as key
        self._received_message_factors = {}  # neighbour_id as key
        self._neighbour_references = []
        self._outward_message_paths = []
        self._special_evidence = None

    def add_special_evidence(self, special_evidence):
        """
        Add special evidence to the cluster. This evidence will not be used to reduce the cluster potential, but will be
        used in the calculation of messages from the cluster. This is used for clusters with factors of which the joint
        distribution is approximated based on conditioning distributions (i.e the NonLinearGaussian factor).

        :param dict special_evidence: The special evidence (i.e {'a':0.3, 'b':2.0})
        """
        self._special_evidence = special_evidence

    def remove_all_neighbours(self):
        """
        Remove all neighbours.
        """
        self._neighbour_sepsets = {}  # neighbour_id as key

    def add_neighbour(self, other_cluster, sepset):
        """
        Add a neighbour to this cluster's list of neighbours.

        :param Cluster other_cluster: The cluster to add as a neighbour
        :param list sepset: The sepset between the neighbours (can be smaller than the scope intersection in order
                       to enforce the running intersection property)
        """
        # TODO: Add var_names check here (there should be a non-zero intersection)
        assert len(sepset) > 0, "Error: cant add neighbour with no overlapping variable scope."
        self._neighbour_references.append(other_cluster)
        self._neighbour_sepsets[other_cluster.cluster_id] = list(sepset)

    # TODO: merge this with add_neighbour
    def add_outward_message_path(self, outward_message_path):
        """
        Add an outward graph message path.

        :param outward_message_path: The graph message path to add.
        """
        self._outward_message_paths.append(outward_message_path)

    def make_message(self, neighbour_id):
        """
        Make a Message to send to the neighbour with a specified id.

        :param neighbour_id: The specified id corresponding to the neighbour cluster.
        :return: The Message
        :rtype: Message
        """
        sepset_vars = self._neighbour_sepsets[neighbour_id]
        message_factor = self._factor.copy()
        if self._special_evidence is not None:
            evidence_vrs = list(self._special_evidence.keys())
            evidence_values = list(self._special_evidence.values())
            message_factor = message_factor.reduce(evidence_vrs, evidence_values)
        message_factor = message_factor.marginalize(sepset_vars, keep=True)
        if neighbour_id in self._received_message_factors:
            prev_received_message_factor = self._received_message_factors[neighbour_id]
            message_factor = message_factor.cancel(prev_received_message_factor)
        # Normalising here can cause incorrect convergence with discrete distributions
        # TODO: investigate this.
        #message_factor = message_factor.normalize()

        message = Message(factor=message_factor, sender_id=self.cluster_id, receiver_id=neighbour_id)
        return message

    def receive_message(self, message):
        """
        Receive Message.

        :param Message message: The received Message
        """
        # Absorb message
        assert message.receiver_id == self.cluster_id, "Error: Message not meant for this Cluster."
        self._factor = self._factor.multiply(message.factor)

        # Cancel out any message previously received from sender cluster
        sender_id = message.sender_id
        if sender_id in self._received_message_factors:
            prev_received_message_factor = self._received_message_factors[sender_id]
            self._factor = self._factor.cancel(prev_received_message_factor)

        self._received_message_factors[message.sender_id] = message.factor.copy()

    def get_sepset(self, neighbour_id):
        """
        Get the sepset between this cluster and another.

        :param str neighbour_id: The id of the other cluster.
        :return: The sepset
        :rtype: list
        """
        sepset = self._neighbour_sepsets[neighbour_id].copy()
        return sepset

    @property
    def neighbour_ids(self):
        """
        Get a list of ids corresponding to the cluster's neigbours.
        """
        return list(self._neighbour_sepsets.keys())

    @property
    def var_names(self):
        """
        The variable names associated with the cluster factor.

        :return: the var_names
        """
        return self._factor.var_names

    @property
    def cluster_id(self):
        """
        The cluster's id.

        :return: The cluster_id
        """
        return self._cluster_id

    @property
    def factor(self):
        """
        The factor.

        :return: The factor.
        """
        return self._factor.copy()


class Message:

    """
    A class for instantiating Message objects.
    """

    def __init__(self, factor, sender_id, receiver_id):
        """
        The initializer.

        :param factor: The Message factor.
        :param sender_id:  The cluster_id of the sender cluster
        :param receiver_id: The cluster_id of the receiver cluster
        """
        self.uuid = str(uuid.uuid1())
        self._sender_id = sender_id
        self._receiver_id = receiver_id
        self._factor = factor

    def equals(self, other, rtol=DEFAULT_FACTOR_RTOL, atol=DEFAULT_FACTOR_ATOL):
        """
        Check if this message equals another message.

        :param other: The other message.
        :param float rtol: The relative tolerance to use for factor equality check.
        :param float atol: The absolute tolerance to use for factor equality check.
        :return: The result of the equality check.
        :rtype: bool
        """
        if self._sender_id != other.sender_id:
            return False
        if self._receiver_id != other._receiver_id:
            return False
        if not self._factor.equals(other._factor, rtol=rtol, atol=atol):
            return False
        return True

    def __repr__(self):
        """
        Get the string representation of the message.

        :return: The string.
        :rtype: str
        """
        repr_str = (
            "sender_id: "
            + self._sender_id
            + "\n"
            + "receiver_id: "
            + self._receiver_id
            + "\n"
            + "factor: \n"
            + self._factor.__repr__()
        )
        return repr_str

    @property
    def sender_id(self):
        """
        The Message's sender id

        :return: The sender_id
        """
        return self._sender_id

    @property
    def receiver_id(self):
        """
        The Message's receiver id

        :return: The receiver_id
        """
        return self._receiver_id

    @property
    def factor(self):
        """
        The Message's factor.

        :return: The factor
        """
        return self._factor.copy()

    def distance_from_vacuous(self):
        """
        Get the Kullback-Leibler (KL) divergence between the message factor and a vacuous (uniform) version of it.

        :return: The KL-divergence
        """
        return self.factor.distance_from_vacuous()

    def kl_divergence(self, message):
        """
        Get the KL-divergence D_KL(self.factor || message.factor) between a this message factor and another message
        factor.

        :param message: The other message of which the factor will be used to compare to this message's factor.
        :return: The KL-divergence
        """
        distance = self.factor.kl_divergence(message.factor)
        return distance

    @property
    def var_names(self):
        """
        The variable names associated with the cluster factor.

        :return: the var_names
        """
        return self._factor.var_names

    def copy(self):
        """
        Copy this Message.

        :return: The message copy.
        :rtype: Message
        """
        msg_copy = Message(self.factor.copy(), copy.deepcopy(self.sender_id), copy.deepcopy(self.receiver_id))
        return msg_copy
