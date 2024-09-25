import asyncio
import time
from functools import wraps


def retry(times=3, delay=1, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            attempt = 0
            while attempt < times:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    print(
                        f"Async Exception: {e}. Retrying {attempt}/{times} in {delay} seconds..."
                    )
                    if attempt >= times:
                        raise
                    await asyncio.sleep(delay)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            attempt = 0
            while attempt < times:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    print(
                        f"Sync Exception: {e}. Retrying {attempt}/{times} in {delay} seconds..."
                    )
                    if attempt >= times:
                        raise
                    time.sleep(delay)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
