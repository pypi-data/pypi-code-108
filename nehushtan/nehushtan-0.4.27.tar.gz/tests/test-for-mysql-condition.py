from nehushtan.mysql.MySQLCondition import MySQLCondition

# Static Type Checking for Python, especially in PyCharm, is not so smart.
# If you mix a correct one into list, even others are wrong, the whole is right.

result = MySQLCondition.make_and(
    [
        2,
        MySQLCondition.make_equal('A', 1.5),
        MySQLCondition.make_in_array('B', ('1', '2')),
        1,
    ]
).organize_to_sql()
print(result)
