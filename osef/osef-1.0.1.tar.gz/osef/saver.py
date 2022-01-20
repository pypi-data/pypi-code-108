"""Tools to save osef stream to a file."""
from osef import parser
from osef._logger import osef_logger


def pretty_size(size, precision=2):
    """get a pretty string of a size."""
    suffixes = ["B", "KB", "MB", "GB", "TB"]
    suffix_index = 0
    while size > 1024 and suffix_index < 4:
        suffix_index += 1  # increment the index of the suffix
        size = size / 1024.0  # apply the division
    return "%.*f%s" % (precision, size, suffixes[suffix_index])


def save_osef_from_tcp(
    tcp_input: str, output_filename: str, print_progress: bool = False
):
    """Save tcp stream to a file.

    :param tcp_input: tcp stream (ex: tcp://192.168.2.2:11120)
    :param output_filename: path to output file
    :param print_progress: print the saving progress osef_saver (1)
    :return: None
    """
    with open(output_filename, "wb") as output:
        with parser.OsefStream(tcp_input) as osef_stream:
            if not osef_stream:
                return None
            bytes_written = 0
            count = 0
            while True:
                try:
                    read = osef_stream.read()
                    if read is None or len(read) == 0:
                        break
                    output.write(read)
                    bytes_written += len(read)
                    count += 1
                    if print_progress and not count % 1000:
                        osef_logger.info(
                            f"Current file size: {pretty_size(bytes_written)}"
                        )
                except KeyboardInterrupt:
                    break
                except EOFError:
                    break
            return bytes_written
