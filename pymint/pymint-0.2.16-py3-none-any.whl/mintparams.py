from parchmint.params import Params


class MINTParams(Params):
    """Params class that abstracts Parchmint Params with
    MINT compatible options

    """

    def __init__(self, pairs: dict) -> None:
        """Creates a MINTParams object

        Args:
            pairs (dict): [description]
        """
        super(MINTParams, self).__init__(None)
        for key in pairs.keys():
            self.data[key] = pairs[key]

    def to_MINT(self) -> str:
        """Returns the MINT string for the set params, it skips the connection/constriant/position params

        Returns:
            str: MINT string
        """
        skip_list = ["paths", "wayPoints", "position"]
        ret = ""
        for key in self.data.keys():
            if key in skip_list:
                continue
            ret += "{}={} ".format(key, self.data[key])
        return ret
