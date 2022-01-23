def CleanInput(inp, customRules=[], appendList=True):
    """
    Still not perfect, but gets rid of the common culprits (\, ', and zero-width space), and strip()s the text.
    Then, you can add a list as the second argument (optional) which allows you to add more stuff.
    Set appendList to False if you ONLY want to use the custom rules.
    For example, you might run:
    turbofunc.CleanInput("   This input is NOT CLEAN!sss\\", ["sss","!"], appendList=True)
    That will turn the string passed in from "   This input is NOT CLEAN!sss\\" to "This input is NOT CLEAN".
    Note that the custom rules are done before the defaults.
    """
    for i in customRules:
        inp = inp.replace(i,'')
    if appendList:
        return inp.replace('\u200b', '').replace('\\', '').replace('\'', '').strip()
    return inp
