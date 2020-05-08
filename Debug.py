import asyncio
import os
from datetime import datetime
import Config

"""
Purpose: Debug module

Item definitions:
*Top-level methods
    log - places given string in debug storage
    loop - async loop that manages live debugging functionality
*Top-level VIP variables
    storage - represents backlog of strings that need to be outputted by the debugger
"""
storage = []


def log(string):
    storage.append(string)


async def loop():
    now = datetime.now()
    path = now.strftime('logs/%d.%m.%Y')
    if not os.path.exists('./%s/' % path):
        os.makedirs(path)
    try:
        with open('./%s/log %s.chlog' % (path, now.strftime("%H.%M.%S")), 'w') as f:
            while True:
                if len(storage) > 0:
                    if Config.PRINT_DEBUG_LOG:
                        print("[DEBUG]: %s" % storage[0])
                    f.write(storage[0])
                    storage.pop(0)
                await asyncio.sleep(1)

    #   I AM SORRY ABOUT THE BARE EXCEPT, BUT I WANT THIS TO ATTEMPT TO RUN NO MATTER WHAT!
    except:
        while True:
            if len(storage) > 0:
                if Config.PRINT_DEBUG_LOG:
                    print("[DEBUG]: %s" % storage[0])
                storage.pop(0)
            await asyncio.sleep(1)
