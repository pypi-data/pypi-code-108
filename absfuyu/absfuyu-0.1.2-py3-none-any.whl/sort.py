
#!/usr/bin/env python
# coding: utf-8



__all__ = [
    "selection_sort",
]

def selection_sort(lst, reverse=False):

    if reverse: # descending order
        for i in range(len(lst)):
            for j in range(i+1, len(lst)):
                if lst[i] < lst[j]:
                    lst[i], lst[j] = lst[j], lst[i]
        return lst
        
    else: # ascending order
        for i in range(len(lst)):
            for j in range(i+1, len(lst)):
                if lst[i] > lst[j]:
                    lst[i], lst[j] = lst[j], lst[i]
        return lst




def insertion_sort(lst):
    for i in range (1,len(lst)):
        key = lst[i]
        j = i-1
        while j>=0 and key < lst[j]:
            lst[j+1] = lst[j]
            j -= 1
        lst[j+1] = key
    return lst



# Make a dict that show the frequency of item name first character in list
def alphabetAppear(lst):
    al_char = [x[0] for x in selection_sort(lst)]
    times_appear = dict()
    for x in al_char:
        if x in times_appear:
            times_appear[x] += 1
        else:
            times_appear[x] = 1
    
    times_appear_increment = []
    total = 0
    for x in times_appear.values():
        total += x
        times_appear_increment.append(total)

    # first item is character frequency
    # second item is incremental index list
    return [times_appear,times_appear_increment]