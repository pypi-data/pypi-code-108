class WsLogger:
    def set_font(self, text, color='black', size=2, face='verdana'):
        return f'<font color="{color}" size="{size}" face="{face}">{text}</font>'

    def get_format_message(self, text, mode='debug'):
        if mode == 'debug':
            color = 'green'
        elif mode == 'error':
            color = 'red'
        elif mode == 'info':
            color = 'blue'
        elif mode == 'warning':
            color = 'orange'
        else:
            color = 'black'
        return f'<span><b>{self.set_font(mode.upper(), color)}</b>: {text}<span>'
