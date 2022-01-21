def number_companies():
    try:
        first_name = str(input("Your first name: "))
        last_name = str(input("Your last name: "))
        p_id = int(input("Your ID: "))
        number = input("Your mobile number: ")
        if number[:2] == '571':
            with open('beeline.txt', 'w') as file:
                file.write(number)
        elif number[:2] == '577':
            with open('geocell.txt', 'w') as file:
                file.write(number)
        elif number[:2] == '598':
            with open('magti.txt', 'w') as file:
                file.write(number)
        return 'Number is written in file!'
    except ValueError:
        print("Enter correct types!")
