import asyncio
import os
from enum import Enum
from datetime import datetime
import Config
import atexit
from io import TextIOWrapper

storage = []


class log_type(Enum):
    NORMAL = 0
    GAMEPLAY = 1
    WARNING = 2
    ERROR = 3


def log(string, l_type=log_type.NORMAL):
    storage.append((l_type, string))


async def loop():
    now = datetime.now()
    path = now.strftime('logs/%m.%d.%Y')
    if not os.path.exists('./%s/' % path):
        os.makedirs(path)
    try:
        with open('./%s/log %s.chlog' % (path, now.strftime("%H.%M.%S")), 'a') as f:
            while True:
                while len(storage) > 0:
                    string = "(%s)[DEBUG | %s]: %s" % (now.strftime("%H:%M:%S"),str(storage[0][0]).split('.')[1], storage[0][1])
                    if Config.PRINT_DEBUG_LOG:
                        print(string)
                    if Config.OUTPUT_LOG_TO_FILE:
                        f.write(string)
                        f.flush()
                    storage.pop(0)
                    await asyncio.sleep(.1)
                await asyncio.sleep(1)

    #   I AM SORRY ABOUT THE BARE EXCEPT, BUT I WANT THIS TO ATTEMPT TO RUN NO MATTER WHAT!
    #   This is most likely to occur due to insufficient file permissions, though!
    except Exception as e:
        log(str(e), log_type.ERROR)
        while True:
            while len(storage) > 0:
                string = "[DEBUG | %s]: %s" % (str(storage[0][0]).split('.')[1], storage[0][1])
                if Config.PRINT_DEBUG_LOG:
                    print(string)
                storage.pop(0)
                await asyncio.sleep(.1)
            await asyncio.sleep(1)


