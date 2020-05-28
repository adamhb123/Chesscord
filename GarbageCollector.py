import os
import asyncio
import Debug

GARBAGE = []


class QueueMember:
    def __init__(self, path):
        self.path = path


def queue(file) -> None:
    if os.path.exists(file):
        GARBAGE.append(QueueMember(file))
    else:
        Debug.log("Failed to add '%s' to the garbage queue...couldn't locate the file!" % file,
                  l_type=Debug.LogType.WARNING)


async def loop():
    while True:
        if len(GARBAGE) > 0:
            front = GARBAGE[0]
            try:
                os.remove(os.path.abspath(front.path))
                Debug.log("Successfully cleaned up file '%s'" % front.path)
                GARBAGE.pop(0)

            except Exception as e:
                Debug.log(str(e), Debug.LogType.WARNING)

            await asyncio.sleep(1)
        else:
            await asyncio.sleep(10)
