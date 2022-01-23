from . import encode, decode, encode_file, decode_file, encode_string, decode_string
from prompt_toolkit.shortcuts import button_dialog, input_dialog, message_dialog
def main():
    if button_dialog(title='Action Chooser', text='What action would you like to preform?', buttons=[('Encode', True), ('Decode', False)]).run():
        # Encode
        encode_type = button_dialog(title='Encode Type', text='What type of encode would you like to preform?', buttons=[('Hex', 0), ('File', 1), ('String', 2)]).run()
        if encode_type == 0:
            # Hex
            message_dialog(title='Encoded String', text=encode(input_dialog(title='Hex Value', text='What hex value would you like to encode?').run())).run()
        elif encode_type == 1:
            # File
            message_dialog(title='Encoded String', text=encode_file(input_dialog(title='File Path', text='What file would you like to encode?').run())).run()
        elif encode_type == 2:
            # String
            message_dialog(title='Encoded String', text=encode_string(input_dialog(title='String', text='What string would you like to encode?').run())).run()
    else:
        # Decode
        decode_type = button_dialog(title='Decode Type', text='What type of decode would you like to preform?', buttons=[('Hex', 0), ('File', 1), ('String', 2)]).run()
        if decode_type == 0:
            # Hex
            message_dialog(title='Decoded Hex', text=decode(input_dialog(title='Encoded String', text='What encoded string would you like to decode?').run())).run()
        elif decode_type == 1:
            # File
            message_dialog(title='Decoded Hex', text=decode_file(input_dialog(title='Encoded String', text='What encoded string would you like to decode?').run(), input_dialog(title='File Path', text='What file would you like to decode to?').run())).run()
        elif decode_type == 2:
            # String
            message_dialog(title='Decoded String', text=decode_string(input_dialog(title='Encoded String', text='What encoded string would you like to decode?').run())).run()
if __name__ == '__main__':
    main()
# EOF
