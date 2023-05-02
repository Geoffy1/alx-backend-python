#!/usr/bin/env python3
'''Task zero
'''

import asyncio
import random


async def wait_random(max_delay: int = 10) -> float:
    """
    Wait for random delay of number 0 to 10
    with asynchronous coroutine
    """
    delay = random.uniform(0, max_delay)
    await asyncio.sleep(delay)
    return delay
