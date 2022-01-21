from mdpeditor.mdpblocks.parameternotseterror import ParameterNotSetError


def not_set_or_empty(dictionary, key):
    """ Returns true if a key is not set or empty """
    return (key not in dictionary.keys() or not dictionary[key].strip())


def process(parameters, block_name):
    """ Set density guided simulation parameters from processing input

        Consume parameters that are not mdp options, but rather used to
        calculate these.

        Sets

            density-guided-simulation-gaussian-transform-spreading-width
            density-guided-simulation-reference-density-filename

        parameters : the full set of parameters, including non-mdp options
        block_name : allows error reporting.
    """
    pixel_size_key = "pixel-size-in-nm"

    errors = ParameterNotSetError()

    # set spreading width from pixel size if its not defined or empty
    width_key = "density-guided-simulation-gaussian-transform-spreading-width"
    if not_set_or_empty(parameters, width_key):
        try:
            parameters[width_key] = str(0.85 *
                                        float(parameters[pixel_size_key]))
            del parameters[pixel_size_key]
        except ValueError:
            errors.add(
                block_name, width_key,
                f" cannot convert \"{pixel_size_key}\"" +
                f"={parameters[pixel_size_key]} "
                "to a spreading width")
        except KeyError:
            errors.add(
                block_name, width_key, " not set in input, use --set " +
                f"{pixel_size_key}=YOURVALUE")
    else:
        if pixel_size_key in parameters:
            errors.add(
                block_name, width_key,
                "you have set a pixel size to determine the spreading width," +
                f" but {width_key} is already set to " +
                f"{parameters[width_key]}")

    # handle the reference density file name
    reference_file_key = "density-guided-simulation-reference-density-filename"
    reference_file_key_short = "reference-density-filename"

    if not_set_or_empty(parameters, reference_file_key):
        try:
            parameters[reference_file_key] = parameters[
                reference_file_key_short]
        except KeyError:
            errors.add(
                block_name, reference_file_key,
                "the reference density file name is not set" +
                ", use the shorthand --set " +
                f"{reference_file_key_short}=FILENAME")

    if errors.have_been_added:
        raise errors
