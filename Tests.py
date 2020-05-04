import Debug
import asyncio
'''
Purpose:
    - For testing all parts of the program (duh)

'''

async def debug_check_loop():
    n = 0
    while True:
        n += 1
        Debug.log(n)
        await asyncio.sleep(.01)


def create_debug_check():
    loop = asyncio.get_event_loop()
    loop.create_task(Debug.loop())
    loop.create_task(debug_check_loop())
    loop.run_forever()


def run_all_tests():
    create_debug_check()


if __name__ == "__main__":
    run_all_tests()
