import paramiko
import threading
import re
import time


class ShaulMiko:
    """
    """

    # Make the connection
    def __init__(self, host, port, username, password, set_terminal_length=True, get_pty=True):
        """

        """
        # Creating SSH Client
        self.ssh = paramiko.SSHClient()
        # Adding auto key
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Authenticating for future ssh session
        self.ssh.connect(hostname=host, username=username, password=password, port=port)

        # Creating a session
        if get_pty:
            self.channel = self.ssh.get_transport().open_session()
            self.channel.get_pty()
            self.channel.invoke_shell()
        else:
            self.channel: paramiko.channel.Channel = self.ssh.invoke_shell()

        # Creating 'write' stream
        self.stdin = self.channel.makefile('wb')
        # Creating 'read' stream
        self.stdout = self.channel.makefile('r')

        # Will send the command 'terminal length 0' unless told otherwise
        if set_terminal_length:
            # Run the command
            self.channel.send("terminal length 0 \n")
        # Amount of seconds we wait before each read
        self.delay_factor = 1
        # Creating output parameter
        self._raw_output = ''
        # Amount of bytes to read per channel read
        self.buffer_size = 1024
        # Creating a stop event flag
        self._stop = False
        # Clearing buffer to get rid of banner
        self.clear_buffer()
        # When we want to clear the prompt we should keep a copy of it instead of finding it every time
        self._prompt = None

    # Close the connection
    def __del__(self):
        self.ssh.close()

    def read_until(self, read_until_string: str, timeout=None):
        """
        Reads all the output of the session until matching string/substring, or timeout. Whatever happens first
        :param timeout: Number of seconds before we stop reading the session content
        :param read_until_string: The string/substring we stop reading at
        :return: The output of the session
        """

        # Creating a thread that reads the output
        thread = threading.Thread(target=self._read_thread, args=(read_until_string,))
        thread.start()
        timeout_reached = False
        # Waiting until timeout passes
        thread.join(timeout=timeout)
        # Checking if thread is alive
        if thread.is_alive():
            self._stop = True
            time.sleep(self.delay_factor * 0.5)
            timeout_reached = True

        output = self._raw_output

        # If timeout was not reached and output was fully read until 'read_until_string'
        if not timeout_reached:
            # Slice output at read until line
            index = output.find(read_until_string)
            new_line_finder = self._normalize_linefeeds(output[index:])
            output = output[:index] + new_line_finder.split("\n")[0]

        return output

    def read_until_timeout(self, timeout: int):
        '''
        Reads all terminal output for 'timeout' seconds and returns the raw output
        :param timeout: Amount of seconds to wait before we stop reading
        :return: session output
        '''
        # Creating a thread that reads the output
        thread = threading.Thread(target=self._read_until_timeout_thread)
        thread.start()

        #  Waiting until timeout passes
        thread.join(timeout=timeout)
        # Checking if thread is alive
        if thread.is_alive():
            self._stop = True
            time.sleep(self.delay_factor * 0.5)

        output = self._raw_output

        return output

    def _read_until_timeout_thread(self):
        '''
        Thread that reads the output until it reaches a timeout
        :return: returns the output of the session
        '''

        # Clearing buffer
        output = ""
        # Constantly reading output
        while True:
            # Reading output
            last_output = self._strip_ansi_escape_codes(self._read_channel())
            output += last_output
            # If timeout was reached
            if self._stop:
                self._stop = False
                break
            # Waiting a bit
            time.sleep(self.delay_factor * 0.25)
        self._raw_output = output

    def write(self, command, no_newline=False):
        """
        Sends a command to the open connection
        :param no_newline: If the user wishes to send the command without the newline '\n' character
        :param command: The comand to send to the session
        :return:
        """
        if no_newline:
            self.channel.send(command)
        else:
            self.channel.send(command + '\n')

    def close_session(self):
        """
        Closes the ssh session
        :return: Nothing
        """
        self.ssh.close()

    def _read_thread(self, read_until_string):
        """
        Thread that reads the output until it reaches the 'read_until_string' string
        :param read_until_string: The string we stop reading the output at
        :return: returns the output of the command
        """
        # Clearing buffer
        output = ""
        # Constantly reading output
        while True:
            # Reading output
            last_output = self._strip_ansi_escape_codes(self._read_channel())
            output += last_output
            # If read until in output
            if read_until_string in last_output:
                break
            # If timeout was reached
            if self._stop:
                self._stop = False
                break
            # Waiting a bit
            time.sleep(self.delay_factor * 0.25)
        self._raw_output = output

    # Execute the commands with checking if it succeeded
    def execute(self, command: str, read_until_string=None, timeout=None, clean_prompt=False):
        """
        :param clean_prompt: Set to true to remove the prompt from the end of the output
        :param timeout: The amount of seconds until shaulmiko stops trying to read the output
        :param read_until_string: String that shaulmiko will stop reading the output at
        :param command: The command to be executed on the remote device
        :example: execute('ls')
                  execute('sudo su -')
                  execute(show interface description')
        """

        # If user didn't specify read_until_string, then read until device prompt (hostname)
        if not read_until_string:
            # Creating default prompt (will read until hostname is shown again)
            read_until_string = self.find_prompt()
        else:
            # Clearing session contents to make sure the next command doesn't have leftovers from the last command
            self.clear_buffer()

        # Run the command
        self.channel.send(command + "\n")

        # Creating a thread that reads the output
        thread = threading.Thread(target=self._read_thread, args=(read_until_string,))
        thread.start()
        timeout_reached = False
        # Waiting until timeout passes
        thread.join(timeout=timeout)
        # Checking if thread is alive
        if thread.is_alive():
            self._stop = True
            time.sleep(self.delay_factor * 0.5)
            timeout_reached = True

        # Clearing output of the command we sent
        output = self._raw_output.replace(command + '\r\n', '').replace(command + '\n', '')

        # If timeout was not reached and output was fully read until 'read_until_string'
        if not timeout_reached:
            # Slice output at read until line
            index = output.find(read_until_string)
            new_line_finder = self._normalize_linefeeds(output[index:])
            output = output[:index] + new_line_finder.split("\n")[0]

        # If clean_prompt is true remove the prompt from the output
        if clean_prompt:
            if self._prompt is None:
                self._prompt = self.find_prompt(self.delay_factor)
            output = output.replace(self._prompt, "")

        return output

    def clear_buffer(self):
        """
        Reads the output at max 10 times to make sure the next command doesn't have leftovers from the last command
        :return: Nothing
        """
        backoff_factor = 0.4
        # Going over it 10 times
        for i in range(1, 10):
            # Waiting before reading
            time.sleep(self.delay_factor * (backoff_factor * i * i))
            data = self._read_buffer()
            # If no data is returned, means the buffer is clear
            if not data:
                break

    def _read_buffer(self):
        """
        Reads max buffer size of info from the channel/stream
        :return:
        """

        output = ""

        # Verifying that channel is open
        if self.channel.recv_ready():
            # Reading the channel output
            outbuf = self.channel.recv(self.buffer_size)
            # If there is no channel output, then the channel has been closed
            if len(outbuf) == 0:
                raise EOFError("Channel stream closed by remote device.")
            # Appending output
            output += outbuf.decode()
        return output

    def _read_channel(self):
        """
        Calls read buffer until there is no more output, and creates a final output string
        :return: final output as string
        """

        output = ""

        # Continuously reading the output
        while True:
            # Reading new output
            new_output = self._read_buffer()
            output += new_output
            # If we are done reading the output
            if new_output == "":
                break
            # If the timeout was reached
            if self._stop:
                break
        return output

    def find_prompt(self, delay_factor=1):
        """Finds the current hostname of the device, last line only.
        :param delay_factor: See __init__: global_delay_factor
        :type delay_factor: int
        """

        # Clearing the output
        self.clear_buffer()
        # Sending 'Enter' to prompt output with hostname
        self.channel.send('\n')
        time.sleep(delay_factor * 0.1)

        # Initial attempt to get prompt
        prompt = self._read_channel()
        prompt = self._strip_ansi_escape_codes(prompt)

        # Checking if the only thing you received was a newline
        count = 0
        prompt = prompt.strip()
        while count <= 10 and not prompt:
            prompt = self._read_channel().strip()
            if prompt:
                prompt = self._strip_ansi_escape_codes(prompt).strip()
            else:
                self.channel.send('\n')
                time.sleep(delay_factor * 0.1)
            count += 1

        # Replacing all possible newline characters with \n
        prompt = self._normalize_linefeeds(prompt)
        # Splitting string based on newline character, if multiple lines in the output take the last line
        prompt = prompt.split('\n')[-1]
        prompt = prompt.strip()
        # If no prompt was found
        if not prompt:
            raise ValueError("Unable to  find prompt: {}".format(prompt))
        time.sleep(delay_factor * 0.1)
        return prompt

    def _normalize_linefeeds(self, a_string):
        """Convert `\r\r\n`,`\r\n`, `\n\r`, to `\n`.

        :param a_string: A string that may have non-normalized line feeds
            i.e. output returned from device, or a device prompt
        :type a_string: str
        """
        newline = re.compile("(\r\r\r\n|\r\r\n|\r\n|\n\r|\r)")
        a_string = newline.sub('\n', a_string)
        return a_string

    def _strip_ansi_escape_codes(self, string_buffer):
        """
        Remove any ANSI (VT100) ESC codes from the output

        http://en.wikipedia.org/wiki/ANSI_escape_code

        Note: this does not capture ALL possible ANSI Escape Codes only the ones
        I have encountered

        Current codes that are filtered:
        ESC = '\x1b' or chr(27)
        ESC = is the escape character [^ in hex ('\x1b')
        ESC[24;27H   Position cursor
        ESC[?25h     Show the cursor
        ESC[E        Next line (HP does ESC-E)
        ESC[K        Erase line from cursor to the end of line
        ESC[2K       Erase entire line
        ESC[1;24r    Enable scrolling from start to row end
        ESC[?6l      Reset mode screen with options 640 x 200 monochrome (graphics)
        ESC[?7l      Disable line wrapping
        ECS[2J       Code erase display
        ESC[00;32m   Coloer Green (30 to 37 are different colors) more general pattern is
                     ESC[\d\d;\d\dm and ESC[\d\d;\d\d;\d\dm
        ESC[6n       Get cursor position

        HP ProCurve and Cisco SG300 require this (possible others).

        :param string_buffer: The string to be processed to remove ANSI escape codes
        :type string_buffer: str
        """

        code_position_cursor = chr(27) + r"\[\d+;\d+H"
        code_show_cursor = chr(27) + r"\[\?25h"
        code_next_line = chr(27) + r"E"
        code_erase_line_end = chr(27) + r"\[K"
        code_erase_line = chr(27) + r"\[2K"
        code_erase_start_line = chr(27) + r"\[K"
        code_enable_scroll = chr(27) + r"\[\d+;\d+r"
        code_form_feed = chr(27) + r"\[1L"
        code_carriage_return = chr(27) + r"\[1M"
        code_disable_line_wrapping = chr(27) + r"\[\?7l"
        code_reset_mode_screen_options = chr(27) + r"\[\?\d+l"
        code_reset_graphics_mode = chr(27) + r"\[00m"
        code_erase_display = chr(27) + r"\[2J"
        code_graphics_mode = chr(27) + r"\[\d\d;\d\dm"
        code_graphics_mode2 = chr(27) + r"\[\d\d;\d\d;\d\dm"
        code_get_cursor_position = chr(27) + r"\[6n"
        code_cursor_position = chr(27) + r"\[m"
        code_erase_display = chr(27) + r"\[J"

        code_set = [
            code_position_cursor,
            code_show_cursor,
            code_erase_line,
            code_enable_scroll,
            code_erase_start_line,
            code_form_feed,
            code_carriage_return,
            code_disable_line_wrapping,
            code_erase_line_end,
            code_reset_mode_screen_options,
            code_reset_graphics_mode,
            code_erase_display,
            code_graphics_mode,
            code_graphics_mode2,
            code_get_cursor_position,
            code_cursor_position,
            code_erase_display
        ]

        output = string_buffer
        for ansi_esc_code in code_set:
            output = re.sub(ansi_esc_code, "", output)

        # CODE_NEXT_LINE must substitute with return
        output = re.sub(code_next_line, '\r\n', output)

        return output
