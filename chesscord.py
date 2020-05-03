import discord
from chess import Chess

class Chesscord(discord.Client):
    def __init__(self,message_prefix='!'):
        super().__init__()
        self.message_prefix = message_prefix
    async def on_read(self):
        print("Logged on as %s!" % self.user)

    async def on_message(self,message):
        content = message.content
        if content.startswith(message_prefix):
            #   Remove prefix from message for reading, then split into arg list
            content = content[1:].split(' ')
            
            
        
            
if __name__=="__main__":
    cli = Chesscord()
    cli.run('NzA2MjcxNTE2OTAzMzQyMTM1.Xq31fw.b9Kp0-0mFM7S7CR1bYElNf9EwW8')
