import os
import json
from collections import defaultdict

import click
from pylint.lint import Run as run_pylint  # type: ignore
from pylint.reporters import CollectingReporter  # type: ignore
from simple_chalk import chalk  # type: ignore

class GitHubAnnotationsReporter(CollectingReporter):

    def create_output(self) -> str:
        annotations = []
        for message in self.messages:
            annotation = {
                'path': os.path.relpath(message.abspath),
                'start_line': message.line,
                'end_line': message.line,
                'message': f'[{message.symbol}] {message.msg or ""}',
                'annotation_level': 'warning' if message.category == 'warning' else 'failure',
            }
            if annotation['start_line'] == ['annotation.end_line']:
                annotation['start_column'] = message.column + 1
                annotation['end_column'] = message.column + 1
            annotations.append(annotation)
        return json.dumps(annotations)


class PrettyReporter(CollectingReporter):

    @staticmethod
    def get_summary(errorCount: int, warningCount: int) -> str:
        summary = ''
        if errorCount:
            summary += chalk.red(f'{errorCount} errors')
        if warningCount:
            summary = f'{summary} and ' if summary else ''
            summary += chalk.yellow(f'{warningCount} warnings')
        return summary

    def create_output(self) -> str:
        fileMessageMap = defaultdict(list)
        for message in self.messages:
            fileMessageMap[os.path.relpath(message.abspath)].append(message)
        totalErrorCount = 0
        totalWarningCount = 0
        outputs = []
        for (filePath, messages) in fileMessageMap.items():
            fileOutputs = []
            for message in messages:
                location = chalk.grey(f'{filePath}:{message.line}:{message.column + 1}')
                color = chalk.yellow if message.category == 'warning' else chalk.red
                fileOutputs.append(f'{location} [{color(message.symbol)}] {message.msg}')
            errorCount = sum(1 for message in messages if message.category != 'warning')
            totalErrorCount += errorCount
            warningCount = sum(1 for message in messages if message.category == 'warning')
            totalWarningCount += warningCount
            fileOutputString = '\n'.join(fileOutputs)
            outputs.append(f'{self.get_summary(errorCount, warningCount)} in {filePath}\n{fileOutputString}\n')
        output = '\n'.join(outputs)
        output += f'\nFailed due to {self.get_summary(totalErrorCount, totalWarningCount)}.' if (totalErrorCount or totalWarningCount) else chalk.green('Passed.')
        return output


@click.command()
@click.option('-d', '--directory', 'directory', required=False, type=str)
@click.option('-o', '--output-file', 'outputFilename', required=False, type=str)
@click.option('-f', '--output-format', 'outputFormat', required=False, type=str, default='pretty')
def run(directory: str, outputFilename: str, outputFormat: str) -> None:
    currentDirectory = os.path.dirname(os.path.realpath(__file__))
    targetDirectory = os.path.abspath(directory or os.getcwd())
    reporter = GitHubAnnotationsReporter() if outputFormat == 'annotations' else PrettyReporter()
    run_pylint([f'--rcfile={currentDirectory}/pylintrc', targetDirectory], reporter=reporter, exit=False)
    output = reporter.create_output()  # type: ignore
    if outputFilename:
        with open(outputFilename, 'w') as outputFile:
            outputFile.write(output)
    else:
        print(output)

if __name__ == '__main__':
    run()  # pylint: disable=no-value-for-parameter
