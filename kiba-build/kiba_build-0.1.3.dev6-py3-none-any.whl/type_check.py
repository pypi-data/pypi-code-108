import re
import os
import json
import dataclasses
import subprocess
from collections import defaultdict
from typing import List

import click
from pylint.reporters import CollectingReporter  # type: ignore
from simple_chalk import chalk  # type: ignore


@dataclasses.dataclass
class Message:
    path: str
    line: int
    column: int
    code: str
    message: str
    level: str

class KibaReporter(CollectingReporter):

    @staticmethod
    def parse_message(rawMessage: str) -> Message:
        match = re.match(r'(.*):(\d*):(\d*): (.*): (.*) \[(.*)\]', rawMessage)
        if match:
            return Message(path=match.group(1), line=int(match.group(2)), column=int(match.group(3)), code=match.group(6), message=match.group(5).strip(), level=match.group(4))
        return Message(path='', line=0, column=0, code='unparsed', message=rawMessage.strip(), level='error')

class GitHubAnnotationsReporter(KibaReporter):

    def create_output(self, messages: List[str]) -> str:
        annotations = []
        parsedMessages = [self.parse_message(rawMessage=rawMessage) for rawMessage in messages if rawMessage]
        for message in parsedMessages:
            annotation = {
                'path': os.path.relpath(message.path) if message.path else '<unknown>',
                'start_line': message.line,
                'end_line': message.line,
                'start_column': message.column,
                'end_column': message.column,
                'message': f'[{message.code}] {message.message}',
                'annotation_level': 'note' if message.level == 'note' else ('warning' if message.level == 'warning' else 'failure'),
            }
            annotations.append(annotation)
        return json.dumps(annotations)


class PrettyReporter(KibaReporter):

    @staticmethod
    def get_summary(errorCount: int, warningCount: int) -> str:
        summary = ''
        if errorCount:
            summary += chalk.red(f'{errorCount} errors')
        if warningCount:
            summary = f'{summary} and ' if summary else ''
            summary += chalk.yellow(f'{warningCount} warnings')
        return summary

    def create_output(self, messages: List[str]) -> str:
        parsedMessages = [self.parse_message(rawMessage=rawMessage) for rawMessage in messages if rawMessage]
        fileMessageMap = defaultdict(list)
        for message in parsedMessages:
            fileMessageMap[os.path.relpath(message.path) if message.path else '<unknown>'].append(message)
        totalErrorCount = 0
        totalWarningCount = 0
        outputs = []
        for (filePath, parsedMessages) in fileMessageMap.items():
            fileOutputs = []
            for message in parsedMessages:
                location = chalk.grey(f'{filePath}:{message.line}:{message.column}')
                color = chalk.yellow if message.level == 'warning' else chalk.red
                fileOutputs.append(f'{location} [{color(message.code)}] {message.message}')
            errorCount = sum(1 for message in parsedMessages if message.level != 'warning')
            totalErrorCount += errorCount
            warningCount = sum(1 for message in parsedMessages if message.level == 'warning')
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
    messages = []
    try:
        subprocess.check_output(f'mypy {targetDirectory} --config-file {currentDirectory}/mypy.ini --no-color-output --no-error-summary --show-column-numbers', stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as exception:
        messages = exception.output.decode().split('\n')
    output = reporter.create_output(messages=messages)  # type: ignore
    if outputFilename:
        with open(outputFilename, 'w') as outputFile:
            outputFile.write(output)
    else:
        print(output)

if __name__ == '__main__':
    run()  # pylint: disable=no-value-for-parameter
