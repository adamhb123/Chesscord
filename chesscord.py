import discord, Debug, asyncio
from Chess import Chess


class Chesscord(discord.Client):
    def __init__(self, message_prefix='!'):
        super().__init__()
        self.message_prefix = message_prefix

    async def on_read(self):
        print("Logged on as %s!" % self.user)

    async def on_message(self, message):
        content = message.content
        if content.startswith(self.message_prefix):
            #   Remove prefix from message for reading, then split into arg list
            content = content[1:].split(' ')


if __name__ == "__main__":
    # Chess()
    loop = asyncio.get_event_loop()
    chess = Chess()
    if Config.DEBUG_MODE:
        loop.create_task(Debug.loop())

if __name__ == "__main__":
    cli = Chesscord()
    cli.run('NzA2MjcxNTE2OTAzMzQyMTM1.Xq31fw.b9Kp0-0mFM7S7CR1bYElNf9EwW8')
