from rito.senders import migadu

def send_message(to_number, text):
    migadu.send_message(f"{to_number}@txt.att.net", text + " ")