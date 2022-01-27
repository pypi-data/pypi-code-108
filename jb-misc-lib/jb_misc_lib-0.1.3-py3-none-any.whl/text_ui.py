# 22/01/2021
# Jason Brown
# Python Text UI functions



lb = "\n"  # To be used in f"""These sorts of strings{lb}Useful in ternary operators"""


def menu(question, menu_list, question_header=0, repeat=False, disable_auto_exit=False, manual_repeating=False):
    """
    Menu list of format [[option_text_1, function_to_execute_1, function_1_args_list, function_1_kwargs_dict], ...]
    Passing _question as a lambda function will call it before each menu print - allows for dynamic question generation
    This also works for option texts
    Function args are optional
    If repeating it will stop if a function returns "break_menu" as first return value
    Exit is automatically supplied as first option if repeat is True, unless disable_auto_exit is True
    Returns all the return values of executed function, except the first return value if it's "break_menu" and was used to
    stop repeating the menu
    LEGACY FEATURE:
    Manual repeating should be used if texts of question or options need to dynamically change without exiting menu
        while menu(...) != "break_menu": pass
    NEW METHOD: Make question or option texts callable functions that return the desired text e.g.
        _question = lambda: f"This is a question with some variable information {variable_info}"
    """

    if (repeat or manual_repeating) and not disable_auto_exit:
        menu_list.insert(0, ["Exit", lambda: "break_menu"])

    while True:

        # Dynamic question generation support: Checks if question is a function to be called to dynamically generate question text
        _question = question() if callable(question) else question

        if question_header == 2:
            print(f"""============================================================
{_question}
------------------------------------------------------------
""")
        elif question_header == 1:
            print(f"""------------------------------------------------------------
{_question}
""")
        else:
            print(_question+"\n")

        for i, option in enumerate(menu_list):
            option_text = option[0]
            _option_text = option_text() if callable(option_text) else option_text
            print(f"{i}. {_option_text}")

        while True:
            user_choice = input()
            print()

            try:
                user_choice = int(user_choice)
            except ValueError:
                print("Input not an integer")
            else:
                if user_choice >= len(menu_list) or user_choice < 0:
                    print("Choice out of range")
                else:
                    break

        choice = menu_list[user_choice]

        if not choice[2:3] or isinstance(choice[2], dict):  # Checks for args and inserts empty list if none
            choice.insert(2, [])

        if not choice[3:4]:  # Checks for kwargs and inserts empty list if none
            choice.insert(3, dict())

        if not isinstance(choice[2], list):  # If single argument was passed we'll make a single item list of it
            choice[2] = [choice[2]]

        return_value = choice[1](*choice[2], **choice[3])  # Executes function giving args and kwargs

        break_menu = False

        # Determine whether to filter break_menu string from return text
        if not manual_repeating:
            if isinstance(return_value, str):
                if return_value == "break_menu":
                    return_value = None
                    break_menu = True

            elif isinstance(return_value, tuple):
                if return_value[0] == "break_menu":
                    return_value = return_value[1] if len(return_value) == 2 else return_value[1:]
                    break_menu = True

        if not repeat or break_menu is True:
            break

    return return_value


def prompt(question, ans_type=None, valid_options=None, valid_options_case_sensitive=True):
    """
    Asks the user a question via input() and will keep asking until an appropriate answer is given

    :param question: Question text to use
    :param ans_type: Type expected for the answer, if input does not convert to this type the question is asked again
    :param valid_options: Optionally provide a list of valid options for the user to enter. If using this consider if a
                            menu is more appropriate. If user input is not in this list question is asked again
    :param valid_options_case_sensitive: Whether or not to care about case when checking if the answer is a valid option
    :return: What the user inputted after they provide an answer conforming to the given constraints
    """
    while True:
        answer = input(f"{question} ")

        if ans_type is not None:
            try:
                answer = ans_type(answer)
            except ValueError:
                print(f"Error, incorrect type entered, expected {ans_type}")
                continue

        if isinstance(valid_options, list):
            if (answer not in valid_options) and (valid_options_case_sensitive or answer.lower() not in [option.lower() for option in valid_options]):
                print(f"Error, answer is not a valid option, valid options are: {', '.join(valid_options)}")
                continue

        break

    return answer


def yes_or_no(question):
    """
    Asks the user a yes or no question. Valid responses: Yes, No, y, n and all case variants of these.
    If an invalid response is given it loops until a valid one is provided

    :param question: The question to ask
    :return: A bool which is true if user replied yes and false if they said no
    """
    while True:
        answer = input(f"{question} y/n: ").lower()

        if answer == "y" or answer == "yes":
            return True
        elif answer == "n" or answer == "no":
            return False
        else:
            print("Invalid input, please enter yes, no, y or n")


def enter_to_continue():
    """
    Little function that allows for staggering what's being printed
    """
    input("\nPress enter to continue... ")


def print_info(info):
    """
    Prints and then waits for user to press enter to continue

    :param info: Thing to print
    """
    print(info)
    enter_to_continue()
