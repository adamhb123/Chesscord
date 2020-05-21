import discord
import Chess
import Debug
import Utility
import GarbageCollector


class Chesscord(discord.Client):
    def __init__(self, message_prefix='!'):
        """
        Object that represents the bot client itself.

        :param message_prefix:

        """
        super().__init__()

        Debug.log("Bot started!")
        self.message_prefix = message_prefix
        self.games = []
        self.challengers = []
        self.command_set = ['display', 'help', 'stats', 'challenge', 'accept', 'move',
                            'd', 'h', 's', 'c', 'a', 'm']

        #   Add Debugger's main loop to event loop
        self.loop.create_task(Debug.loop())

        #   Add GarbageCollector's main loop to event loop
        self.loop.create_task(GarbageCollector.loop())

    def get_game_given_user(self, uid):
        """
        Retrieves a game given a participating user's id

        :param uid:
        :return: Matching ChessMatch object given
        :rtype: Chess.ChessMatch
        """
        for game in self.games:
            if game.player_white.id == uid or game.player_black.id == uid:
                return game
        return None

    async def on_message(self, message):
        content = message.content

        if content.startswith(self.message_prefix):
            #   Remove prefix from message for reading, then format with strip and lower
            content = content[1:].strip().lower().split(' ')
            #   Search command set for given command
            if content[0] in self.command_set:
                game = self.get_game_given_user(message.author.id)
                if 'display' in content or content[0] == 'd':
                    if game is None:
                        await message.channel.send("You haven't started a game yet!")
                    else:
                        if 'numerical' in content:
                            board = game.format_board_to_string(
                                game.get_board_as_array(btype=Chess.BoardDisplayType.NUMERICAL))
                            await message.channel.send(board)
                        elif 'characterial' in content:
                            board = game.format_board_to_string(
                                game.get_board_as_array(btype=Chess.BoardDisplayType.CHARACTERIAL))
                            await message.channel.send(board)
                        elif 'color' in content:
                            board = game.format_board_to_string(
                                game.get_board_as_array(btype=Chess.BoardDisplayType.COLOR))
                            await message.channel.send(board)
                        else:
                            fp = "./rsc/temp/gb%s.png" % game.id
                            Utility.get_graphical_board(game.board).save(fp)
                            board = discord.File(fp)
                            await message.channel.send(file=board)
                            try:
                                GarbageCollector.queue("./rsc/temp/gb%s.png" % game.id)
                            except PermissionError:
                                Debug.log("Failed to remove image due to insufficient permissions")
                            except Exception as e:
                                Debug.log("Failed to remove image: %s" % str(e))

                elif 'help' in content or content[0] == 'h':
                    await message.channel.send(Utility.get_help())

                elif 'stats' in content or content[0] == 's':
                    await message.channel.send()

                elif 'challenge' in content or content[0] == 'c':
                    self.challengers.append(message.author)
                    if len(message.mentions) > 0:
                        await message.mentions[0].send(
                            "_______________________________________________________\n"
                            "Hey! %s has challenged you to a chess match in server: \"%s\"!\nTo accept, go to the"
                            " channel you were mentioned in and type: \n\"!accept @%s\"\n"
                            "_______________________________________________________\n" % (
                                message.author.name, message.guild,
                                message.author.name + "#" + message.author.discriminator))
                    else:
                        await message.channel.send("Please specify who you are challenging by mentioning them!")

                elif 'accept' in content or content[0] == 'a':
                    if len(message.mentions) > 0:
                        if message.mentions[0] in self.challengers:
                            self.games.append(Chess.ChessMatch(Utility.generate_game_id(),
                                                               init_message=message))
                            self.challengers.remove(message.mentions[0])
                    else:
                        await message.channel.send(
                            "Please specify whose challenge you are accepting by mentioning them!")

                elif 'move' in content or content[0] == 'm':
                    if self.get_game_given_user(message.author.id) is None:
                        await message.channel.send("You haven't started a game yet.")
                    else:
                        move = content[1].upper()
                        if Utility.check_move_input_valid(move):
                            move = move.split(':')
                            piece = game.piece_at_position(move[0])
                            Debug.log("MOVING PIECE OWNER: %s" % piece.player.id)
                            move = piece.move(move[1], message)
                            if move is False:
                                await message.channel.send("Invalid move!")
                            elif move == "WRONG PLAYER":
                                await message.channel.send("It is not your turn!")
                            elif move == "WRONG TEAM":
                                await message.channel.send("That isn't your piece!")
                            else:
                                fp = "./rsc/temp/gb%s.png" % game.id
                                Utility.get_graphical_board(game.board).save(fp)
                                board = discord.File(fp)
                                await message.channel.send(file=board)


                        else:
                            await message.channel.send("Move input incorrect! Example: \"!move D3:D4\"")

                Debug.log("User %s activated the bot with %s" % (message.author.name, message.content))


if __name__ == "__main__":
    # Chess()
    try:
        cli = Chesscord()
        cli.run('NzA2MjcxNTE2OTAzMzQyMTM1.XsWazg.EQX3N9MSe5uQJD4nKgxZ_le5hDg')
    except Exception as e:
        Debug.log(str(e))
