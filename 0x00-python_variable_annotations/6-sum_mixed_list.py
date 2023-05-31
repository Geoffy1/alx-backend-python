#!/usr/bin/env python3
"""returns sum of list mxd_lst of integers and floats
"""

import typing


def sum_mixed_list(mxd_lst: typing.List[typing.Union[int, float]]) -> float:
    """the sum of the list as a float"""
    return float(sum(mxd_lst))
