import discord
import Chess
import Debug
import Utility

import os
"""
Purpose: Essentially the "main" of the entire bot. This is where it all begins...

Item definitions:

*Top-level Classes
    Chesscord - the bot itself, containing all functionality of the program
        *Methods:
            on_message - runs every time a message is received
            
        *VIP variables:
            message_prefix - prefix utilized to initiate a command
            game - the actual game of Chess, which is stored in Chess.py
            challengers - used to store all challengers that have yet to receive a response
            command_set - set of possible commands that can be used
    
"""


class Chesscord(discord.Client):
    def __init__(self, message_prefix='!'):
        super().__init__()

        Debug.log("Bot started!")
        self.message_prefix = message_prefix
        self.games = []
        self.challengers = []
        self.command_set = ['display numerical', 'display lexical', 'display characterial', 'display locational',
                            'display image', 'display', 'secret', 'secret zimbabwe coronavirus millionaire',
                            'help', 'challenge', 'accept']
        #   Add Debugger's main loop to event loop
        self.loop.create_task(Debug.loop())

    async def on_message(self, message):
        content = message.content
        if content.startswith(self.message_prefix):
            #   Remove prefix from message for reading, then format with strip and lower
            content = content[1:].strip().lower().split(' ')
            #   Search command set for given command
            if content[0] in self.command_set:
                if 'display' in content:
                    found_game = False
                    for game in self.games:
                        if str(message.author.id) in str(game.player_white.id) or str(message.author.id) in str(
                                game.player_black.id):
                            found_game = True
                            if 'numerical' in content:
                                board = game.format_board_to_string(
                                    game.get_board_as_array(btype=Chess.BoardType.NUMERICAL))
                                await message.channel.send(board)
                            elif 'lexical' in content:
                                board = game.format_board_to_string(
                                    game.get_board_as_array(btype=Chess.BoardType.LEXICAL))
                                await message.channel.send(board)
                            elif 'characterial' in content:
                                board = game.format_board_to_string(
                                    game.get_board_as_array(btype=Chess.BoardType.CHARACTERIAL))
                                await message.channel.send(board)
                            elif 'locational' in content:
                                board = game.format_board_to_string(
                                    game.get_board_as_array(btype=Chess.BoardType.LOCATIONAL))
                                await message.channel.send(board)
                            else:
                                Utility.get_graphical_board(game.board).save("./rsc/temp/gb%s.png" % game.id)
                                board = discord.File("./rsc/temp/gb%s.png" % game.id)
                                await message.channel.send(file=board)
                                try:
                                    os.remove("./rsc/temp/gb%s.png" % game.id)
                                except PermissionError:
                                    Debug.log("Failed to remove image due to insufficient permissions")

                    if not found_game:
                        await message.channel.send("You haven't started a game yet!")
                elif 'help' in content:
                    await message.channel.send(Utility.get_help())

                elif 'stats' in content:
                    await message.channel.send()

                elif 'secret zimbabwe coronavirus millionaire' in content:
                    await message.channel.send(
                        'I have heard rumors that <@176998998459154432> is not actually a heterosexual...')

                elif 'secret' in content:
                    await message.channel.send('Enter !secret again, followed by the magic phrase...')

                elif 'challenge' in content:
                    self.challengers.append(message.author)
                    if len(message.mentions) > 0:
                        await message.mentions[0].send(
                            "Hey! %s has challenged you to a chess match in server: \"%s\"!\nTo accept, go to the"
                            " channel you were mentioned in and type: \n\"!accept @%s\"" % (
                                message.author.name, message.guild,
                                message.author.name + "#" + message.author.discriminator))
                    else:
                        await message.channel.send("Please specify who you are challenging by mentioning them!")

                elif 'accept' in content:
                    if len(message.mentions) > 0:
                        if message.mentions[0] in self.challengers:
                            self.games.append(Chess.ChessMatch(Utility.generate_id(self.games),
                                                               message.mentions[0], message.author))
                    else:
                        await message.channel.send(
                            "Please specify whose challenge you are accepting by mentioning them!")

                Debug.log("User %s activated the bot with %s" % (message.author.name, message.content))


if __name__ == "__main__":
    # Chess()
    cli = Chesscord()
    cli.run('NzA2MjcxNTE2OTAzMzQyMTM1.Xq31fw.b9Kp0-0mFM7S7CR1bYElNf9EwW8')
