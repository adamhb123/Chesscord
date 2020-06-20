import discord
import Chess
import Debug
import Utility
import GarbageCollector
import Database
from typing import Union


class Chesscord(discord.Client):
    def __init__(self, message_prefix: str = '!'):
        """
        Object that represents the bot client itself.

        :param message_prefix: The prefix required to access the bot (ex: the bang in '!help').
        """
        super().__init__()

        Debug.log("Bot started!")
        self.message_prefix = message_prefix
        self.games = []

        self.challengers = []
        self.command_set = ['display', 'help', 'stats', 'challenge', 'accept', 'move', 'resign',
                            'd', 'h', 's', 'c', 'a', 'm', 'r']

        self.loop.create_task(Debug.loop())
        self.loop.create_task(GarbageCollector.loop())
        self.loop.create_task(Database.update_loop())

    def get_game_given_uid(self, uid: int) -> Union[Chess.ChessMatch, None]:
        """
        Retrieves a game given a participating user's ID.

        :param uid: User's ID.
        :return: Matching ChessMatch object given.
        :rtype: Chess.ChessMatch
        """
        for game in self.games:
            if game.player_white.id == uid or game.player_black.id == uid:
                return game
        return None

    def get_player_obj_given_uid(self, uid) -> Union[Chess.Player, None]:
        """
        Retrieves a Chess.Player object given user's ID.

        :param uid: User's ID.
        :return: Either a Chess.Player object or None
        """
        game = self.get_game_given_uid(uid)
        if game is not None:
            if game.player_white.id == uid:
                return game.player_white
            elif game.player_black.id == uid:
                return game.player_black
        else:
            return None

    def __resignation(self, message: discord.Message) -> Union[str, bool, None]:
        """
        Contains all necessary operations for resignation.

        :param message: The message that triggered the event.
        :return: None if the user isn't playing a game, True if the resignation succeeds.
        """
        game = self.get_game_given_uid(message.author.id)
        if game is None:
            return None
        else:
            self.games.remove(game)
            return True

    async def on_message(self, message: discord.Message):
        """
        Inherited method from discord.Client. Runs upon any certain message received. IT IS RIDICULOUSLY UGLY.

        :param message: The message that triggered the event.
        """
        content = message.content

        if content.startswith(self.message_prefix):
            #   Remove prefix from message for reading, then format with strip and lower
            content = content[1:].strip().lower().split(' ')
            #   Search command set for given command
            if content[0] in self.command_set:
                game = self.get_game_given_uid(message.author.id)
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
                            "\nHey! %s has challenged you to a chess match in server: \"%s\"!\nTo accept, go to the"
                            " channel you were mentioned in and type: \n\"!accept @%s\"\n" % (
                                message.author.name, message.guild,
                                message.author.name + "#" + message.author.discriminator))
                    else:
                        await message.channel.send("Please specify who you are challenging by mentioning them!")

                elif 'accept' in content or content[0] == 'a':
                    if len(message.mentions) > 0:
                        if message.mentions[0] in self.challengers:
                            self.games.append(Chess.ChessMatch(Utility.generate_game_id(self.games),
                                                               init_message=message))

                            Database.queue_instruction(message.mentions[0].id, Database.InstructionType.ADD_PLAYER)
                            self.challengers.remove(message.mentions[0])
                    else:
                        await message.channel.send(
                            "Please specify whose challenge you are accepting by mentioning them!")

                elif 'resign' in content:
                    res = self.__resignation(message)
                    if res is None:
                        await message.channel.send("You haven't started a game yet.")
                    elif res is True:
                        await message.channel.send("<@%s> has resigned." % message.author.id)

                elif 'move' in content or content[0] == 'm':
                    if self.get_game_given_uid(message.author.id) is None:
                        await message.channel.send("You haven't started a game yet.")
                    else:
                        move = content[1].upper()
                        Debug.log("MOVE: %s" % move)
                        if Utility.check_move_input_valid(game, move):
                            move = move.split(':')
                            piece = game.piece_at_position(move[0])
                            move = piece.move(move[1], message)
                            if move is False:
                                await message.channel.send("Invalid move!")
                            elif move == "WRONG PLAYER":
                                await message.channel.send("It is not your turn!")
                            elif move == "WRONG TEAM":
                                await message.channel.send("That isn't your piece!")
                            elif move == "OWN PIECE":
                                await message.channel.send("You can't capture your own piece!")

                            else:
                                fp = "./rsc/temp/gb%s.png" % game.id
                                Utility.get_graphical_board(game.board).save(fp)
                                board = discord.File(fp)
                                await message.channel.send(file=board)

                        else:
                            await message.channel.send("Move input incorrect! Example: \"!move D3:D4\"")



if __name__ == "__main__":
    try:
        print("Project current total lines of code: %s" % Utility.get_project_lines_of_code())
        cli = Chesscord()
        cli.run(Utility.get_token_from_file('private_config.txt'))
    except Exception as e:
        Debug.log(str(e))
