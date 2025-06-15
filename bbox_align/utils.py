from copy import deepcopy
from typing import List, TypeVar, Optional, Union, Any


T = TypeVar('T')


def subarray(array: List[List[T]], indices: List[int]) -> List[List[T]]:

    return [[array[row][col] for col in indices] for row in indices]

def get_augmented_matrix(
    matrix: List[List[Any]],
    words: List[str],
    idxs: Optional[List[int]] = None
) -> List[List[Any]]:

    if idxs:
        _matrix = subarray(matrix, idxs)
        _words = [words[idx] for idx in idxs]
    else:
        _matrix = deepcopy(matrix)
        _words = words

    # Prepend each word to the corresponding row
    for idx, row in enumerate(_matrix):
        _matrix[idx] = [_words[idx]] + row

    # Add a header row with words
    _matrix = [[' '] + _words] + _matrix

    return _matrix

def pprint_matrix(
    matrix: List[List[T]],
    words: List[str],
    idxs: Optional[List[int]] = None
):

    aug_matrix = get_augmented_matrix(matrix, words, idxs)

    maxl = max(
        len(str(val))
        for row in aug_matrix
        for val in row
    )

    for row in aug_matrix:
        print(" ".join([f"{str(cell):>{maxl + 2}}" for cell in row]))
