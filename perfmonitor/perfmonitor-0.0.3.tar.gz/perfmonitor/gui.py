import os
import shutil
from time import time
from typing import Tuple

import termcolor


def color_perc_str(val: int, format_str: str = None, warning_val=50, critical_val=80):
    """
    Return a colored string representing the percentage of a value.
    """
    if format_str is None:
        format_str = "{}"
    s = f"{format_str.format(val)}"

    if float(val) < warning_val:
        return termcolor.colored(s, 'green')
    if float(val) < critical_val:
        return termcolor.colored(s, 'yellow')
    return termcolor.colored(s, 'red')


def perc_usage_bar(current_usage: float, length: int, max_usage: float, low_usage=0.5, mid_usage=0.8, ext=""):
    """
    Return progress bar showing the current PERCENTAGE of usage of a resource.
    """
    if current_usage >= max_usage or current_usage < 0:
        current_usage = max_usage
    p_str_len = 15
    usable_len = length - 2 - p_str_len

    usage_perc = current_usage / max_usage
    color = "green" if usage_perc < low_usage else "yellow" if usage_perc < mid_usage else "red"
    usage_str = "{:.1f}%".format(usage_perc * 100)

    s_internal = ("█" * round(usable_len * usage_perc)) + \
        ("-" * round(usable_len * (1 - usage_perc)))
    s_internal = termcolor.colored(s_internal[:round(len(s_internal) * low_usage)], "green") + \
        termcolor.colored(s_internal[round(len(s_internal) * low_usage):round(len(s_internal) * mid_usage)],
                          "yellow") + \
        termcolor.colored(
            s_internal[round(len(s_internal) * mid_usage):], "red")

    p_str = termcolor.colored(usage_str, color)  # type: str
    return "{} [{}]".format((p_str + ext).rjust(p_str_len), s_internal)


def raw_usage_bar(current_usage: float, length: int, max_usage: float, low_usage=0.5, mid_usage=0.8, ext="", pad_start=0):
    """
    Return progress bar showing the current usage of a resource. Units are raw (unformatted) values.
    """
    if current_usage >= max_usage or current_usage < 0:
        current_usage = max_usage
    p_len = 25
    usable_len = length - 2 - (p_len-pad_start)

    usage_perc = current_usage / max_usage
    color = "green" if usage_perc < low_usage else "yellow" if usage_perc < mid_usage else "red"
    usage_str = "{:.2f} / {:.2f}".format(current_usage, max_usage)

    s_internal = ("█" * int(usable_len * usage_perc)) + \
        ("-" * int(usable_len * (1 - usage_perc)))

    s_internal = termcolor.colored(s_internal[:round(len(s_internal) * low_usage)], "green") + \
        termcolor.colored(s_internal[round(len(s_internal) * low_usage):round(len(s_internal) * mid_usage)],
                          "yellow") + \
        termcolor.colored(
            s_internal[round(len(s_internal) * mid_usage):], "red")

    return "[{}] {}".format(s_internal, termcolor.colored(usage_str + ext, color).rjust(25))


def print_cpu_stats(data: dict, out_str: str, cols: int) -> Tuple[str, int]:
    """
    Pretty print CPU stats.
    Output: string to print and number of lines printed.
    """
    out_str += "CPU STATS\n"

    cpu_time = data["cpu_percs"]
    combined_info = " Total:   " + \
        perc_usage_bar(float(cpu_time['_Total']), cols // 2 - 9, 100)
    out_str += combined_info + "\n\n"
    cpu_usage = ""
    rows = 0
    for cpu_i in range(len(cpu_time.keys()) - 1):
        base_s = f" Core {cpu_i + 1}: ".ljust(10)
        s = perc_usage_bar(cpu_time[cpu_i], cols // 2 - 9, 100)

        cpu_usage += base_s + s
        if cpu_i % 2 == 1:
            cpu_usage += "\n"
            rows += 1
    return out_str + cpu_usage + "\n", 5 + rows


def print_mem_stats(data: dict, gpu_state: dict, out_str: str, cols: int, n_lines: int, disable_gpu_stat=False, net_stats: str = None) -> Tuple[str, int]:
    """
    Pretty print MEM stats.
    Output: string to print and number of lines printed.
    """
    mem_line_len = cols // 2
    mem_bar_len = mem_line_len - 7
    ram_unit = "GB" if data["byte_avail"] > 1024 else "MB"
    swap_unit = "GB" if data["v_bytes"] > 1024 else "MB"

    avail_ram = data["byte_avail"] / \
        1024 if data["byte_avail"] > 1024 else data["byte_avail"]
    tot_ram = data["mb_tot"] / \
        1024 if data["mb_tot"] > 1024 else data["mb_tot"]
    swap_mem = data["v_bytes"] / \
        1024 if data["v_bytes"] > 1024 else data["v_bytes"]

    tot_swap = data["v_bytes_limit"] if data["v_bytes_limit"] < 1024 else \
        data["v_bytes_limit"] / 1024 if data["v_bytes_limit"] < (1024 ** 2) else \
        data["v_bytes_limit"] / (1024 ** 2) if data["v_bytes_limit"] < (1024 ** 3) else \
        data["v_bytes_limit"] / (1024 ** 3)

    mem_str = ""
    mem_str += "MEM STATS\n"
    mem_str += " RAM:  " + raw_usage_bar(tot_ram - avail_ram, mem_bar_len, tot_ram, ext=" " + ram_unit) + \
               " <" + "{:.2f}".format(avail_ram).rjust(5) + \
        " {} available>".format(ram_unit) + "\n"
    mem_str += " SWAP: " + raw_usage_bar(swap_mem, mem_bar_len, tot_swap, ext=" " + swap_unit) + \
               " <" + "{:.2f}".format(tot_swap - swap_mem).rjust(5) + \
        " {} available>".format(swap_unit) + "\n"

    if not disable_gpu_stat and gpu_state is not None:
        mem_str += " GPU:  " + raw_usage_bar(float(gpu_state['used_mem'].split()[0])/1024, cols // 2 - 17, float(gpu_state['total_mem'].split(
        )[0])/1024, ext=" GB", pad_start=10) + " <" + "{:.2f}".format(float(gpu_state['free_mem'].split()[0])/1024).rjust(5) + " GB available>" + "\n"
        n_lines += 1

    if net_stats is not None:
        netlines = net_stats.splitlines()
        assert len(netlines) <= len(mem_str.splitlines())
        memlines = mem_str.splitlines()
        for r, l in enumerate(netlines):
            if r == 0:
                memlines[r] += ' '*(mem_line_len+3)
            memlines[r] = memlines[r].rstrip(
                '\n') + " "*2 + '|' + " "*2 + l.strip('\n') + "    \n"
        mem_str = ''.join(memlines)

    out_str += (mem_str+'\n')

    n_lines += 4

    return out_str, n_lines


terminal_size = None


def check_terminal_resize():
    """
    Check if the terminal has been resized. If so:
    - Update the global variable terminal_size
    - Clear screen
    """
    rows, cols = get_terminal_size()
    changed_size = False
    global terminal_size
    if terminal_size is None:
        terminal_size = rows, cols
    else:
        if terminal_size[0] != rows or terminal_size[1] != cols:
            terminal_size = rows, cols
            changed_size = True

    if changed_size:
        os.system("CLS")


def format_net_str(byte_value: int):
    """
    Format a byte value to a human readable string.
    """

    if byte_value < 1024:
        return "{:.2f} B/s".format(byte_value)
    elif byte_value < (1024 ** 2):
        return "{:.2f} KB/s".format(byte_value / 1024)
    elif byte_value < (1024 ** 3):
        return "{:.2f} MB/s".format(byte_value / (1024 ** 2))
    else:
        return "{:.2f} GB/s".format(byte_value / (1024 ** 3))


def get_net_str(net_counters: dict, pad=0, title_pad=0):
    net_sent_str = format_net_str(net_counters['bytes_sent'])
    net_recv_str = format_net_str(net_counters['bytes_recv'])

    return f"""{' '*title_pad}NET STATS\n{' '*pad}Received {net_recv_str}\n{' '*pad}Sent     {net_sent_str}"""


def print_gpu_stats(gpu_state: dict, out_str: str, cols: int, n_lines: int, disable_gpu_stat: bool) -> Tuple[str, int]:
    """
    Pretty print GPU stats.
    Output: string to print and number of lines printed.
    """
    if gpu_state is None or disable_gpu_stat:
        return out_str, n_lines

    gpu_cols = cols // 2
    gpu_bar_len = gpu_cols - 17

    out_str += "\nGPU STATS\n"
    out_str += " Compute engine: " + \
        perc_usage_bar(float(gpu_state['gpu_usage'].split()[
                       0]), gpu_bar_len, 100) + "\n"

    out_str += " Encoder:        " + \
        perc_usage_bar(float(gpu_state['encoder_usage'].split()[
                       0]), gpu_bar_len, 100) + "\n"
    out_str += " Decoder:        " + \
        perc_usage_bar(float(gpu_state['decoder_usage'].split()[
                       0]), gpu_bar_len, 100) + "\n"
    out_str += " Memory Bus:     " + \
        perc_usage_bar(float(gpu_state['memory_usage'].split()[
                       0]), gpu_bar_len, 100) + "\n"

    temp = float(gpu_state['temperature'].split()[0])
    max_temp = float(gpu_state['max_temp'].split()[0])
    slow_temp = float(gpu_state['slow_temp'].split()[0])

    temp_perc = temp / max_temp
    temp_color = "green" if temp_perc < 0.6 else "yellow" if temp_perc < 0.8 else "red"

    out_str += " Current temperature: " + termcolor.colored(f"{temp} C",
                                                            temp_color) + f" <Max: {max_temp} C | Slowing down at: {slow_temp} C>\n"

    return out_str, n_lines + 5


def pretty_print_data(data: dict, gpu_state: dict, loading_time: float, gpu_load_time: float,
                      start_time: float, min_rows: int, final_line='', disable_gpu_stat=False) -> None:
    """
    Pretty print loaded stats.

    :param data: CPU+MEM+NET stats.
    :param gpu_state: GPU stats.
    :param loading_time: Time to load the CPU+MEM stats.
    :param gpu_load_time: The time it took to load the GPU stats.
    :param start_time: Timestamp before stats loading.
    :param min_rows: Minimum number of rows to print.
    :param final_line: The final line to print.
    :param disable_gpu_stat: Disable GPU stats print.
    """
    global terminal_size
    check_terminal_resize()
    rows, cols = terminal_size

    if rows < min_rows:
        os.system("CLS")
        print(
            f"Terminal too small. Please resize it to at least {min_rows} rows (current: {rows})")
        return

    out_str = "\r"

    out_str, n_lines = print_cpu_stats(data, out_str, cols)
    out_str, n_lines = print_mem_stats(
        data, gpu_state, out_str, cols, n_lines, disable_gpu_stat, net_stats=get_net_str(data['net_io_counters'], pad=1))

    out_str, n_lines = print_gpu_stats(
        gpu_state, out_str, cols, n_lines, disable_gpu_stat)

    out_str += "\n" * (rows - n_lines - 2)

    if disable_gpu_stat:
        out_str += "System info loading time: {:.2f} ms | Processing time: {:5.2f} ms    \n".format(
            loading_time * 1000, ((time() - start_time) - loading_time) * 1000)
    elif gpu_load_time is not None:
        out_str += "System info loading time: {:.2f} ms | GPU info loading time: {:.2f} ms | Processing time: {:5.2f} ms    \n".format(
            loading_time * 1000, gpu_load_time * 1000, ((time() - start_time) - (loading_time + gpu_load_time)) * 1000)
    else:
        out_str += "System info loading time: {:.2f} ms | NO GPU DETECTED | Processing time: {:5.2f} ms    \n".format(
            loading_time * 1000, ((time() - start_time) - loading_time) * 1000)

    out_str += final_line

    print(out_str, end="")
    print("\033[F"*rows, end="")


def get_terminal_size():
    """Return the terminal size in rows and columns."""
    term_size = shutil.get_terminal_size()
    return int(term_size.lines), int(term_size.columns)
