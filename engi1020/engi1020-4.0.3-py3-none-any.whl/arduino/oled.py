from . import command


# Cursor location
row = 0
col = 0


def clear():
    """Clear the OLED display."""

    global row, col

    command("Clearing OLED display", "oc", "OC-OK")
    row = 0
    col = 0


def print_message(message):
    """Print a message to the OLED display at the current cursor position."""

    global row, col

    message = str(message)
    
    while len(message) > 0:
        space = 16 - col

        next_chunk = message[:space]
        remainder = message[space:]

        while len(next_chunk) < 16:
            next_chunk += ' '

        encoded = next_chunk.encode('utf-8')

        command(f"Printing {next_chunk} at ({row}, {col})", "op", "OP-OK",
                bytes([row, col, len(encoded)]), encoded)

        row += 1
        col = 0
        message = remainder

def move_cursor(new_row, new_col):
    global row, col

    row = new_row
    col = new_col
    
