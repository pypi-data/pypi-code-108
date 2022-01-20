def bmi_index():
    try:
        first_name = str(input("Your First Name: "))
        last_name = str(input("Your Last Name: "))
        weight = float(input("Your Weight: "))
        height = float(input("Your Height in metres: "))
        bmi = weight / (height ** 2)
        if 16 <= bmi <= 25:
            print("Your weight is normal!")
        elif 30 <= bmi <= 35:
            print("It's the 1st degree of obesity!")
        elif 35 <= bmi <= 40:
            print("It's the 2nd degree of obesity!")
    except ValueError:
        print("Enter the right type!")
        bmi_index()

bmi_index()