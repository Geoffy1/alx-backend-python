#!/usr/bin/env python3
'''Task four
'''
import asyncio
from typing import List


task_wait_random = __import__('3-tasks').task_wait_random


async def task_wait_n(n: int, max_delay: int) -> List[float]:
    """
    run a number of  coroutines simultaneously with async
    """
    delays = []
    for _ in range(n):
        delay = await task_wait_random(max_delay)
        delays.append(delay)
        delays = sorted(delays)
    return delays
