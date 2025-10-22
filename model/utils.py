import random

def shuffle_list(lst):
    temp = lst.copy()
    random.shuffle(temp)
    return temp

def flatten(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]
