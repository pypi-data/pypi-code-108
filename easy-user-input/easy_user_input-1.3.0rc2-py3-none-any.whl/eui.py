
#misc functions that help with user input
#formerly known as easy_user_input.easy_user_input (or easy_user_input.py)
from typing import Tuple


#Prompts the user to select either yes or no (y or n)
#returns a boolean representing their response (True for yes, False for no)
#continues to prompt user for valid input until recieved
#promptText will be printed as the prompt (along with a set of options)
#if a default is specified, it will be displayed in the prompt
#and will be used if user input is empty
def inputYesNo(promptText: str = "Choose yes or no", default: bool = None):

    #initialize default letter
    defaultLetter = None

    #create the full text of the prompt
    if default == None:
        fullPromptText = f"{promptText} (y/n): "
    else:
        #determine the default letter if default is set
        if default:
            defaultLetter = "y"
        else:
            defaultLetter = "n"
        
        #include the default in the prompt if set
        fullPromptText = f"{promptText} (y/n, default '{defaultLetter}'): "
    
    userChoice = None
    while userChoice == None:
        uInput = input(fullPromptText).lower()
        if uInput == 'y' or uInput == 'yes':
            userChoice = True
        elif uInput == 'n' or uInput == 'no':
            userChoice = False
        elif uInput == "" and default != None:
            userChoice = default
            print(f"No response; defaulting to '{defaultLetter}'")
            
        else:
            print(f'Invalid input: "{uInput}". Please choose (y)es or (n)o.')

    return userChoice


#prompts the user to select one option out of a tuple/list (the choices param)
#returns their selection as the index in the choices tuple
#each entry in choices can be a 2-tuple; in this case the second value is
#used as an extended description for the option
#promptText will be printed as a prompt, along with the available options
#if a default is specified, it will be displayed in the prompt
#and will be used if user input is empty
def inputChoice(
    choices:Tuple[str or Tuple[str, str]], 
    promptText:str = "Please select an option", 
    default: int = None
    ) -> int:

    #initialize default selection 
    defaultSelection = None

    #create the full text of the prompt
    fullPromptText = ""
    for index, choice in enumerate(choices):
        #use description if one is present
        if (isinstance(choice, tuple) or isinstance(choice, list)): 
            if len(choice) > 1:
                fullPromptText += f"{index + 1}: {choice[0]} - {choice[1]}\n"
            else:
                fullPromptText += f"{index + 1}: {choice[0]}\n"
        else:
            fullPromptText += f"{index + 1}: {choice}\n"

    #add a blank line to indicate end of choices
    fullPromptText += "\n"

    if default == None:
        fullPromptText += f"{promptText} (number from 1 to {len(choices)}): "
    else:
        #determine the default selection if default is set
        
        defaultChoice = choices[default]
        if (isinstance(defaultChoice, tuple) or isinstance(defaultChoice, list)): 
            defaultSelection = f"'{default+1}' - {defaultChoice[0]}"
        else:
            defaultSelection = f"'{default+1}' - {defaultChoice}"
        
        #include the default in the prompt if set
        #default + 1 is used because prompt is one indexed whereas lists are zero indexed
        fullPromptText += f"{promptText} (number from 1 to {len(choices)}, default {defaultSelection}): "

    #loop until valid input, which is returned when encountered,
    #thus breaking this loop
    while True:
        uInput = input(fullPromptText)
        
        #select default if provided and no input was given
        if uInput == "" and default != None:
            print(f"No response; defaulting to {defaultSelection}")
            return default

        #try to convert user input to an integer
        try:
            uInput = int(uInput)
            if uInput < 1 or uInput > len(choices):
                raise ValueError
        except ValueError:
            #print message and retry if input couldn't be converted
            #or if user input is out of bounds
            print(f'Invalid input: "{uInput}". Please choose a number from 1 to {len(choices)}.')
            continue

        else:
            userChoice = choices[uInput - 1]
            #print back the user's choice
            if (isinstance(userChoice, tuple) or isinstance(userChoice, list)): 
                print(f"Selected '{uInput}' - {userChoice[0]}")
            else:
                print(f"Selected '{uInput}' - {userChoice}")
            return (uInput - 1)

#Prompts the user to input a string; input is rejected unless it contains
#only charachters in the provided 'allowedChars' string (default shown below)
def inputStrictString(promptText: str, allowedChars: str = None, default: str or None = None) -> str:
    if allowedChars == None:
        import string
        allowedChars = string.digits + string.ascii_uppercase + string.ascii_lowercase + "_ "

    strictInput = None
    while strictInput == None:
        if default == None:
            uInput = input(f"{promptText}: ")
        else:
            uInput = input(f"{promptText} (default '{default}'): ")

        if uInput == "" and default != None:
            print(f"No response; defaulting to '{default}'")
            strictInput = default
        else:
            #check if input was valid
            inputValid = True
            for char in uInput:
                if char not in allowedChars:
                    inputValid = False
                    print(f"Invalid input: {repr(uInput)}")
                    break
            if inputValid:
                strictInput =  uInput

    return strictInput

#Prompts the user to input a file path; input is rejected unless the path is valid
#'existsBehavior' param is a string and must be one of the following:
# 'reject' - rejects existing paths
# 'warn' - accepts existing paths after accepting a warning
# 'accept' - accepts existing paths with no warning
# 'require' - only accepts paths to existing files
# 'directory' - only accepts paths to existing directories
#raises a ValueError if existsBehavior is anything else
def inputPath(
        promptText: str = "Please input a valid path",
        existsBehavior: str = "reject",
        default: str or None = None
    ) -> str:
    from os import path

    #construct full prompt

    if default != None:
        promptText += f" (default '{default}')"
        

    if existsBehavior == "reject":
        fullPromptText = f"{promptText} (new file): "
    elif existsBehavior == "warn" or existsBehavior == "accept" or existsBehavior == "require":
        fullPromptText = f"{promptText} (file): "
    elif existsBehavior == "directory":
        fullPromptText = f"{promptText} (directory): "
    else:
        raise ValueError(f"Invalid existsBehavior: {existsBehavior}")

    
    #get path from the user
    userPath = None
    while userPath == None:
        uInput = input(fullPromptText)

        if uInput == "" and default != None:
            print(f"No response; defaulting to '{default}'")
            return default

        #expand the ~ char into the user's home directory if needed
        if "~" in uInput:
            uInput = path.expanduser(uInput)

        #convert the path into an absolute path
        uInput = path.abspath(uInput)

        #test path validity based on existsBehavior
        if existsBehavior == "accept":
            #accept means path is always valid
            userPath = uInput
        
        elif existsBehavior == "warn":
            #accept if path doesn't exist or if user chooses to overwrite
            if path.exists(uInput):
                if inputYesNo(f"\"{uInput}\" already exists.\nOverwrite?", False):
                    userPath = uInput
            else:
                userPath = uInput
        
        elif existsBehavior == "reject":
            #accept only if path doesn't exist
            if path.exists(uInput):
                print(f"Cannot use path \"{uInput}\" because it already exists!")
            else:
                userPath = uInput

        elif existsBehavior == "require":
            #accept only if path exists and is a file
            if path.exists(uInput) and path.isfile(uInput):
                userPath = uInput
            else:
                if path.isdir(uInput):
                     print(f"Cannot use path \"{uInput}\" because it is a directory!")
                else:
                    print(f"Cannot use path \"{uInput}\" because it doesn't exist!")

        elif existsBehavior == "directory":
            #accept only if path exists and is a directory
            if path.exists(uInput) and path.isdir(uInput):
                userPath = uInput
            else:
                print(f"Cannot use path \"{uInput}\" because it is not a directory!")
        
    return userPath

#returns a message; mostly for testing
def getMsg() -> str:
    return "Easy User Input module - misc functions that help with user input"

if __name__ == "__main__":
    print(getMsg())