class Classroom:

    def __init__(self, year_of_creation, classroom_char, students):
        self.students = students
        self.classroom_char = classroom_char
        self.year_of_creation = year_of_creation


    def add_Student(self, student):
        self.students.append(student)

    def show_student(self):
        for x in self.students:
            print(x.fullname)

# studentsklA = [
#     student1,
#     student2,
#     student3
# ]
#
# studentsklB = [student4, student5, student6]
#
#
# classroomA = Classroom(
#     year_of_creation=2001,
#     classroom_char='A',
#     students=studentsklA
# )
#
# classroomB = Classroom(
#     year_of_creation=2000,
#     classroom_char='B',
#     students=studentsklB