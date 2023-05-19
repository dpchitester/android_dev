"""
Problem: provide two-way communication with a subprocess in Python.

See also: 
- https://kevinmccarthy.org/2016/07/25/streaming-subprocess-stdin-and-stdout-with-asyncio-in-python/
- http://eli.thegreenplace.net/2017/interacting-with-a-long-running-child-process-in-python/
"""

import asyncio
import sys
import typing as T

async def enqueue(values: T.Iterable[bytes], stream: asyncio.StreamWriter):

    for line in values:
        stream.write(line)
        # Yield to the asyncio loop
        await stream.drain()

    # Once we've exhausted values, we need to close the async stream to signal to
    # the subprocess that it can exit
    stream.close()

async def dequeue(stream: asyncio.StreamReader, callback: T.Callable[[bytes], None]):

    while True:
        line = await stream.readline()
        if not line:
            break
        callback(line)

async def main():

    proc = await asyncio.subprocess.create_subprocess_exec(
        'sed', r's/o/o\n/g',
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )
    
    await asyncio.wait([
        asyncio.create_task(enqueue(sys.stdin.buffer, proc.stdin)),
        asyncio.create_task(dequeue(proc.stdout, sys.stdout.buffer.write)),
    ])

    # I'm not completely sure the call to `communicate` is necessary
    (stdout_data, stderr_data) = await proc.communicate()
    await proc.wait()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    rc = loop.run_until_complete(main())
    loop.close()