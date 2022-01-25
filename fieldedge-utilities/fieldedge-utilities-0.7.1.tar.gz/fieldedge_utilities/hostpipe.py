"""Operations for interacting with the hostpipe service."""
import os
import subprocess
from datetime import datetime
from logging import DEBUG, Logger
from time import sleep, time

TIMESTAMP_FMT = 'YYYY-mm-ddTHH:MM:SS.SSSZ'
# TIMESTAMP_FMT = os.getenv('HOSTPIPE_TIMESTAMP_FMT', 'YYYY-mm-ddTHH:MM:SS.SSSZ')
COMMAND_PREFIX = f'{TIMESTAMP_FMT},[INFO],command='
RESPONSE_PREFIX = f'{TIMESTAMP_FMT},[INFO],result='

DEFAULT_TIMEOUT = float(os.getenv('HOSTPIPE_TIMEOUT', 0.25))
MAX_FILE_SIZE = int(os.getenv('HOSTPIPE_LOGFILE_SIZE', 2)) * 1024 * 1024


def host_command(command: str,
                 noresponse: bool = False,
                 timeout: float = DEFAULT_TIMEOUT,
                 log: Logger = None,
                 pipelog: str = None,
                 test_mode: bool = False,
                 ) -> str:
    """Sends a host command to a pipe (from the Docker container).
    
    The response is read from the hostpipe.log file assuming the fieldedge-core
    script is in place to echo command and response into a log.
    Care should be taken to ensure the timeout is sufficient for the response,
    and the calling function must handle an empty string response.

    Args:
        command: The command to be executed on the host.
        noresponse: Flag if set don't look for a response.
        timeout: The time in seconds to wait for a response.
        log: An optional logger for debug purposes.
        pipelog: Override default hostpipe.log, typically used with test_mode.
        test_mode: Boolean to mock responses.
    
    Returns:
        A string with the command response, or empty if no response received.
    
    Raises:
        FileNotFoundError if the hostpipe log cannot be found.

    """
    command = _apply_preamble(command)
    command_time = time()
    if not test_mode:
        if isinstance(log, Logger):
            log.debug(f'Sending {command} to hostpipe via shell')
        subprocess.run(f'echo "{_escaped_command(command)}" > ./hostpipe/pipe',
                       shell=True)
    elif isinstance(log, Logger):
        log.info(f'test_mode received command: {command}')
    if noresponse:
        return f'{command} sent'
    if pipelog is None:
        pipelog = './logs/hostpipe.log'
    if not os.path.isfile(pipelog):
        raise FileNotFoundError(f'Could not find file {pipelog}')
    response_str = host_get_response(command,
                                     command_time=command_time,
                                     pipelog=pipelog,
                                     timeout=timeout,
                                     log=log,
                                     test_mode=test_mode,
                                     ).strip()
    deleted_count = _maintain_pipelog(pipelog)
    if isinstance(log, Logger) and deleted_count > 0:
        log.info(f'Removed {deleted_count} oldest lines from {pipelog}')
    if isinstance(log, Logger) and log.getEffectiveLevel() == DEBUG:
        if response_str == '':
            abv_response = '<no response>'
        elif len(response_str) < 25:
            abv_response = response_str.replace('\n', ';')
        else:
            abv_response = response_str[:20].replace("\n", ";") + '...'
        log.debug(f'Hostpipe: {command} -> {abv_response}')
    return response_str


def _apply_preamble(command: str) -> str:
    if '$HOME' in command:
        preamble = 'sudo runuser -u pi -- '
        if preamble in command:
            preamble = ''
        command = f'{preamble}{command.replace("$HOME", "/home/pi")}'
    return command


def _escaped_command(command: str) -> str:
    escaped_command = ''
    for c in command:
        if c == '"':
            escaped_command += r'\\\"'
        else:
            escaped_command += c
    return escaped_command


def _get_line_ts(line: str) -> float:
    iso_time = line[:len(TIMESTAMP_FMT)]
    utc_dt = datetime.strptime(iso_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    return (utc_dt - datetime(1970, 1, 1)).total_seconds()


def host_get_response(command: str,
                      command_time: float = None,
                      pipelog: str = None,
                      timeout: float = DEFAULT_TIMEOUT,
                      log: Logger = None,
                      test_mode: bool = False,
                      ) -> str:
    """Retrieves the response to the command from the host pipe log.
    
    Args:
        command: The host command sent previously.
        timeout: The maximum time in seconds to try for a response.
        log: Optional logging facility
    
    Returns:
        A string concatenating all the response lines following the command.

    Raises:
        FileNotFoundError if the hostpipe log cannot be found.

    """
    calltime = time()
    command = _apply_preamble(command)
    if pipelog is None:
        pipelog = './logs/hostpipe.log'
    if not os.path.isfile(pipelog):
        raise FileNotFoundError(f'Could not find file {pipelog}')
    if isinstance(log, Logger):
        log.debug(f'Searching {pipelog} for {command}')
    response = []
    filepass = 0
    while len(response) == 0:
        # test_mode assumes manual step through will usually violate timeout
        if not test_mode and time() > calltime + timeout:
            if isinstance(log, Logger):
                log.warning(f'Response to {command} timed out'
                    f' after {timeout} seconds')
            break
        filepass += 1
        if isinstance(log, Logger):
            log.debug(f'{pipelog} read iteration {filepass}')
        lines = open(pipelog, 'r').readlines()
        for line in reversed(lines):
            if (not test_mode and
                command_time is not None and
                _get_line_ts(line) < command_time):
                # older command, skip this pass
                sleep(0.1)
                break
            if ',command=' in line:
                logged_command = line.split(',command=')[1].strip()
                if isinstance(log, Logger):
                    log.debug(f'Found command {logged_command} in {pipelog}'
                        f'({line[:len(TIMESTAMP_FMT)]})'
                        f' with {len(response)} response lines')
                if logged_command != command:
                    # wrong command/response so dump parsed lines so far
                    cts = line[:len(TIMESTAMP_FMT)]
                    to_remove = []
                    for resline in response:
                        rts = resline[:len(TIMESTAMP_FMT)]
                        if rts == cts:
                            to_remove.append(resline)
                    if isinstance(log, Logger):
                        log.debug(f'Mismatch: {logged_command} != {command}'
                            f' -> dropping {len(to_remove)} response lines')
                    response = [l for l in response if l not in to_remove]
                else:
                    # we reached the original command so can stop parsing response
                    if isinstance(log, Logger):
                        log.debug(f'Found target {command}'
                            f' with {len(response)} response lines')
                    response = [l[len(RESPONSE_PREFIX):] for l in response]
                    break
            elif ',result=' in line:
                response.append(line)
        if not test_mode:
            sleep(timeout / 2)
    response.reverse()
    return ''.join(response)


def _maintain_pipelog(pipelog: str,
                      max_file_size: int = MAX_FILE_SIZE,
                      test_mode: bool = False,
                      ) -> int:
    """Deletes log entries if over a maximum size and returns the count deleted.

    Deletes both the command and its response.

    Returns the number of lines deleted.
    """
    # TODO: spin a thread to do this in background? or manage in bash/linux
    if not(os.path.isfile(pipelog)):
        raise FileNotFoundError(f'Could not find {pipelog}')
    to_delete = []
    if os.path.getsize(pipelog) > max_file_size:
        lines = open(pipelog, 'r').readlines()
        while os.path.getsize(pipelog) > max_file_size:
            for line in lines:
                if ',result=' in line:
                    to_delete.append(line)
                elif ',command=' in line:
                    if len(to_delete) == 0:
                        to_delete.append(line)
                    else:
                        break
            with open(pipelog, 'w') as f:
                for line in lines:
                    if line not in to_delete:
                        f.write(line)
        if len(to_delete) > 0 and test_mode:
            with open(pipelog, 'w') as f:
                f.writelines(lines)
    return len(to_delete)
