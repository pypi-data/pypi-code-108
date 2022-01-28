from ..singleSeq.Predictor import MineSuite
from ..singleSeq import constants


class SingleSeq:
    """
    Stores the sequences, the filename where they were read from, tools to be executed and the result of the
    predicitons.

    Parameters:

            fileName (str): Path to the fasta file where the sequences of interest are located.
    """

    def __init__(self, fileName):
        """
        Constructor for the SingleSeq class. Reads the fasta file that contains the sequences, calls a function that
        reads the sequences and creates the structure to store all the information required to run and store the
        predicitons.

        Parameters:

            fileName (str): Path to the fasta file where the sequences of interest are located.


        """
        self.__mineSuite__ = MineSuite()
        self.__sequenceFileName__ = fileName
        self.__sequences__ = self.__mineSuite__.readFasta(fileName)
        self.__predictor_runners__ = {
            constants.TOOL_DYNAMINE: self.__mineSuite__.dynaMine,
            constants.TOOL_DISOMINE: self.__mineSuite__.disoMine,
            constants.TOOL_EFOLDMINE: self.__mineSuite__.eFoldMine,
            constants.TOOL_AGMATA: self.__mineSuite__.agmata,
        }

        self.__results__ = {}

    # This method has the responsibility of running the asked predictions in a smart way: it omits the tools that already have a result
    def predict(self, tools=[]):
        """
        This method has the responsibility of running the asked predictions in a smart way: it omits the tools that
        already have a result and runs the remaining.

        Parameters:

            tools (list[str]) : List of tools to be ran. Any combination of the following tools is accepted:
                - "dynamine"
                - "disomine"
                - "efoldmine"
                - "agmata"

        Returns:

            obj: self
        """

        for tool in tools:
            dependencies = constants.DEPENDENCIES[tool]

            if (len(dependencies) > 0):
                self.predict(tools=dependencies)

            if not self.__results__.get(tool):

                predictor_function = self.__predictor_runners__[tool]
                predictor_function.allPredictions = self._all_predictions()

                if tool == constants.TOOL_EFOLDMINE:
                    predictor_function.predictSeqs(self.__sequences__, dynaMinePreds=predictor_function.allPredictions)
                else:
                    predictor_function.predictSeqs(self.__sequences__)

                self.__results__[tool] = predictor_function.allPredictions
                print("executed {0}".format(tool))

        return self

    # Instead of using a list of tools as in predict method, this one uses flags to create a list of tools and call
    # the predict method:
    def semantic_predict(
            self,
            dynamics=False,
            aggregation=False,
            early_folding_propensity=False,
            disorder=False,
    ):
        """
        Instead of using a list of tools as in predict method, this one uses flags on the (high level) type of
        predictions desired to create a list of tools and call the predict method.

        Parameters:

            dynamics (bool, optional) : Whether or not dynamics predictions are to be ran
            aggregation (bool, optional) : Whether or not aggregation predictions are to be ran
            early_folding_propensity (bool, optional) : Whether or not early folding propensity predictions are to be ran
            disorder (bool, optional) : Whether or not disorder predictions are to be ran

        Returns:

            obj: self
        """
        tools_to_run = []

        if dynamics:
            tools_to_run.append(constants.TOOL_DYNAMINE)
        if aggregation:
            tools_to_run.append(constants.TOOL_AGMATA)
        if early_folding_propensity:
            tools_to_run.append(constants.TOOL_EFOLDMINE)
        if disorder:
            tools_to_run.append(constants.TOOL_DISOMINE)

        return self.predict(tools=tools_to_run)

    def explicit_definition_predictions(self, backbone_dynamics=False,
                                        sidechain_dynamics=False,
                                        propoline_II=False,
                                        disorder_propensity=False,
                                        coil=False,
                                        beta_sheet=False,
                                        alpha_helix=False,
                                        early_folding_propensity=False,
                                        aggregation_propensity=False):

        """

        Instead of using a list of tools as in predict method, this one uses flags on the (explicit) type of
        predictions desired to create a list of tools and call the predict method.

        Parameters:

            backbone_dynamics (bool, optional) : Whether or not backbone dynamics are to be predicted
            sidechain_dynamics (bool, optional) : Whether or not sidechain dynamics are to be predicted
            propoline_II (bool, optional) : Whether or not propoline II propensity is to be predicted
            disorder_propensity (bool, optional) : Whether or not disorder propensity is to be predicted
            coil (bool, optional) : Whether or not coil propensity is to be predicted
            beta_sheet (bool, optional) : Whether or not beta sheet propensity is to be predicted
            alpha_helix (bool, optional) : Whether or not alpha helix propensity is to be predicted
            early_folding_propensity (bool, optional) : Whether or early folding propensity is to be predicted
            aggregation_propensity (bool, optional) : Whether or aggregation propensity is to be predicted

        Returns:

            obj: self

        """

        tools_to_run = []

        if backbone_dynamics or sidechain_dynamics or coil or beta_sheet or alpha_helix or propoline_II:
            tools_to_run.append(constants.TOOL_DYNAMINE)
        if disorder_propensity:
            tools_to_run.append(constants.TOOL_DISOMINE)
        if early_folding_propensity:
            tools_to_run.append(constants.TOOL_EFOLDMINE)
        if aggregation_propensity:
            tools_to_run.append(constants.TOOL_AGMATA)

        return self.predict(tools=tools_to_run)

    def _all_predictions(self):
        result = {}

        for tool in self.__predictor_runners__:
            result.update(self.__predictor_runners__[tool].allPredictions)

        return result

    def get_all_predictions_json(self, identifier):
        """
        Outputs all available predictions in a JSON formatted string. This still needs to be written in the desired
        output channel by the user.

        Parameters:

            identifier (str) : Identifier used as the root key of the JSON output.

        Returns:

            str : JSON string with outputs
        """
        self.__mineSuite__.allPredictions = self._all_predictions()

        return self.__mineSuite__.getAllPredictionsJson(identifier=identifier)

    def get_all_predictions(self, sequence_key=None):
        """
        Returns the values in dictionary form. It also allows to select the outputs of a single sequence from the
        original fasta file instead of all of them at once.

        Parameters:

            sequence_key (str, optional) : Sequence identifier specified as the FASTA header in the input
        file. It allow the user to select the output of a single sequence.

        Returns:

            reorganized_results (dict) : Dictionary which contains the output of the predictions.

        """
        result = self._all_predictions()

        if sequence_key is not None:
            results_to_reorganize = {sequence_key: result[sequence_key]}
        else:
            results_to_reorganize = result

        reorganized_results = self._organize_predictions_in_dictionary(results_to_reorganize)

        return reorganized_results

    def _organize_predictions_in_dictionary(self, results):
        new_result = {}
        for sequence in results:
            new_keys = {}

            for i, predictions in enumerate(results[sequence]):
                if i == 0:
                    new_keys['seq'] = [position[0] for position in results[sequence][predictions]]
                new_keys[predictions] = [position[1] for position in results[sequence][predictions]]

            new_result[sequence] = new_keys

        return new_result
