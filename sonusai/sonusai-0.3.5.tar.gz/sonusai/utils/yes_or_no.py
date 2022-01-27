def yes_or_no(question: str) -> bool:
    while 'the answer is invalid':
        reply = str(input(question + ' (y/n)?: ')).lower().strip()
        if reply[:1] == 'y':
            return True
        if reply[:1] == 'n':
            return False
