from copy import deepcopy
from typing import List


def print_matrix(matrix: List[List[bool]]) -> None:
    """
    Prints a 2D matrix with proper rows and columns formatting.
    """
    for row in matrix:
        print(" ".join(["{:>10}".format(str(cell)) for cell in row]))

def print_inlines(inlines, words):
    inlines_copy = deepcopy(inlines)
    for idx, i in enumerate(inlines_copy):
        inlines_copy[idx] = [words[idx]] + inlines_copy[idx]
    inlines_copy = [[' '] + words] + inlines_copy
    print(inlines_copy)
    print_matrix(inlines_copy)
