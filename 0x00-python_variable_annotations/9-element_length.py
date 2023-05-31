#!/usr/bin/env python3
"""return values with the appropriate types.
"""
from typing import Iterable, List, Sequence, Tuple


def element_length(lst: Iterable[Sequence]) -> List[Tuple[Sequence, int]]:
    """gets length of a list of sequences.
    """
    return [(i, len(i)) for i in lst]
