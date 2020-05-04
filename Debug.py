import asyncio

'''
Purpose: Debug module


'''
storage = []


def log(string):
    storage.append(string)


async def loop():
    while True:
        if len(storage) > 0:
            print("[DEBUG]: %s" % storage[0])
            storage.pop(0)
        await asyncio.sleep(.1)
