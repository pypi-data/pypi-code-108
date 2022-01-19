"""
Test for for loop with or syntax
"""

# test_list = ["element_1", "element_2", "element_3", "element_4"]
# test_list = None
test_list = []
for ele in (test_list or ["Original_List_Is_Empty"]):
    print(f"Element: {ele}")
