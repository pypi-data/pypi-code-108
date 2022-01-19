import argparse
import logging
import sys

from . import export_latex, export_pdf, load, render

logger = logging.getLogger('pyexam')

export_formats = {
    'latex': export_latex,
    'pdf': export_pdf,
}


def setup_logger(level: str):
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % level)
    logging.basicConfig(level=numeric_level)


def main():
    parser = argparse.ArgumentParser(prog='pyexam')
    parser.add_argument('-i', '--input-file', dest='file', required=True)
    parser.add_argument('-o', '--output-dir', dest='out', required=False)
    parser.add_argument('-t', '--template-dir',
                        dest='template', required=False)
    parser.add_argument('-s', '--solution', dest='solution',
                        action=argparse.BooleanOptionalAction)
    parser.add_argument('-f', '--format', dest='format',
                        default='latex', choices=export_formats.keys())
    parser.add_argument('-l', '--log-level', dest='level', default='error')
    options = parser.parse_args()

    try:
        setup_logger(options.level)
        exam = load(options.file)

        if not options.out:
            if options.format == 'pdf':
                raise ValueError('Output arg is required when format is pdf')
            print(render(exam, options.solution, options.template))
        else:
            export_formats[options.format](
                exam, options.out, options.solution, options.template)
            print(f'Exported exam to directory {options.out}')
    except Exception as e:
        if e.__cause__:
            logger.error(e.__cause__)
        logger.exception(e)
        sys.exit(f'pyexam error: {e}')


if __name__ == '__main__':
    main()
