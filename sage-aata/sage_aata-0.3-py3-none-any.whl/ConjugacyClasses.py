

def conjugacy_class(element , group):
    # define a set to hold all the conjugates of the element
    conjugates = set(())
    # for each item in the group, calculate the conjugate and add
    # it to the set defined in the line above.
    for i in group.list():
        conjugates.add((i^(-1))*element*i)
    # return the final set of all conjugates of the element.
    return conjugates


def all_conjugacy_classes(group):
    # define a list that will hold all the conjugacy classes of the group.
    conjugacy_classes = []
    # for each element in the group, 
    for i in group.list():
        # define a new set that will be the conjugacy class of that element
        conjugates = set(())
        # for each element of the group, add j^{-1}*i*j (remember that Sage 
        # takes this from right to left) to the conjugacy class
        for j in group.list():
            conjugates.add((j^(-1))*i*j)
        # if that conjugate class is not already in the list, add it.
        if conjugates not in conjugacy_classes:
            conjugacy_classes.append(conjugates)
    
    # return the final list of conjugacy classes.
    return conjugacy_classes


def conjugacy_class_gens(group):
    # define the dictionary that will hold all the conjugacy classes,
    # as well as which elements generate those classes.
    conjugacy_classes = {}
    # for each element in the group, 
    for i in group.list():
        # create a new set, that will be the conjugacy class of that element.
        conjugates = set(())
        for j in group.list():
            conjugates.add((j^(-1))*i*j)
        # sort that conjugacy class
        conjugates = sorted(conjugates)
        # if the conjugacy class is already found among the keys of the 
        # dictionary defined above, add the element to it's list, if not,
        # create a new entry with that conjugacy class.
        if str(conjugates) not in conjugacy_classes.keys():
            conjugacy_classes[str(conjugates)] = [i]
        else:
            conjugacy_classes[str(conjugates)].append(i)
    # return the final dictionary with all conjugacy classes and generators.
    return conjugacy_classes


