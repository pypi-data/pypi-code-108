from cytoolz.curried import do, pipe, map
from .sinks import Sink, JsonlFileSink
from .sources import Source, JsonlFileSource
from genomoncology.parse.ensures import flatten
import glob
import os


def do_file_run_pipeline(processors, input, output):

    funcs, sinks = prep_funcs_sinks(processors, output)

    for _ in pipe(input, *funcs):
        pass

    for sink in sinks:
        sink.close()


def run_pipeline(processors, input, output, dir):
    if dir is not None:
        if dir == ".":
            dir = os.getcwd()
        input_file_pattern = os.path.join(dir, input)
        matching_files = glob.glob(input_file_pattern)
        for input_file in matching_files:
            head, tail = os.path.split(input_file)
            if output == "-":
                output_file = "-"
            else:
                output_file = os.path.join(
                    dir, output.replace("*", tail.split(".")[0])
                )
            if output_file == "-" or not os.path.isfile(output_file):
                do_file_run_pipeline(processors, input_file, output_file)
    else:
        do_file_run_pipeline(processors, input, output)


def prep_funcs_sinks(processors, output):
    processors = flatten(processors)

    if not processors or not Source.is_source_class(processors[0]):
        processors.insert(0, JsonlFileSource)

    sinks = []
    funcs = []

    def add_sink(cls):
        sink = cls(output)
        sinks.append(sink)
        funcs.append(map(do(sink.write)))

    for processor in processors:
        if Sink.is_sink_class(processor):
            add_sink(processor)

        else:
            funcs.append(processor)

    if not sinks:
        add_sink(JsonlFileSink)

    return funcs, sinks
