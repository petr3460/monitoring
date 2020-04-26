import random
import time
import asyncio
from aiohttp import ClientSession

now = time.time()
yesterday = int(now) - 24*60*60


async def fetch(url, session, tstamp, hostname):
    print(url, tstamp, hostname)
    async with session.post(url, data={'hostname': hostname,
                                       'timestamp': tstamp,
                                       'is_online': True}) as response:
        print(response.status)
        return await response.read()


async def bound_fetch(sem, url, session, tstamp, hostname):
    async with sem:
        await fetch(url, session, tstamp, hostname)


async def run():
    url = "http://localhost:8000/event/"
    tasks = []
    sem = asyncio.Semaphore(100)
    async with ClientSession() as session:
        for i in range(1, 8):
            start_interval = yesterday + random.randint(0, 60*20)
            end_interval = start_interval + 60 * random.randint(4, 10)
            intervals_count = 2
            for _ in range(intervals_count):
                for tstamp in range(start_interval, end_interval, 60):
                    hostname = 'Host{}'.format(str(i))
                    task = asyncio.ensure_future(bound_fetch(sem, url, session, tstamp, hostname))
                    tasks.append(task)
                start_interval = end_interval + 60 * random.randint(40, 100)
                end_interval = start_interval + 60 * random.randint(3, 8)

        responses = asyncio.gather(*tasks)
        await responses


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run())
    loop.run_until_complete(future)
