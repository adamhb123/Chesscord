from enum import Enum
import Debug
import discord
import Config
import Utility
import asyncio
import math

NUM_TO_WORD_DICT = {0: ' ', 1: 'Pawn', 2: 'Knight', 3: 'Bishop',
                    4: 'Rook', 5: 'Queen', 6: 'King'}
WORD_TO_NUM_DICT = {value: key for key, value in NUM_TO_WORD_DICT.items()}


class HistoricalMove:
    def __init__(self, piece, pre_loc, post_loc):
        """
        Represents a past move in game history.
        :param piece: Piece that made the move.
        :param pre_loc: Location (in conventional format) before the move was made.
        :param post_loc: Location (in conventional format) after the move was made.
        """
        self.piece = piece
        self.pre_loc = pre_loc
        self.post_loc = post_loc
        self.index_pre_loc = Utility.conventional_position_to_index(self.pre_loc)
        self.index_post_loc = Utility.conventional_position_to_index(self.post_loc)


class BoardDisplayType(Enum):
    """
    Enum for the various board display types.
    """
    NUMERICAL = 0
    LEXICAL = 1
    CHARACTERIAL = 2
    LOCATIONAL = 3
    COLOR = 4


class Piece:
    def __init__(self, game, name, player, location):
        """
        Object that is representative of a game piece.

        :param game: ChessMatch (Object) that the piece belongs to.
        :param name: Name of the piece, ie "Rook" or "Queen".
        :param player: Player (Object) that the piece belongs to.
        :param location: Initial location (in conventional format) of the piece.
        """
        self.name = name
        self.game = game
        self.player = player
        #   Name refers to the piece type (Queen, Rook, etc)
        #   Color refers to the team the piece is on and is represented by "White" or "Black"
        #   Position is a tuple containing the position of the piece (x,y)
        #   Test position input:
        Utility.check_position_input_valid(location)
        self.location = str(location[0]) + str(location[1])

    def get_identity(self):
        """
        Returns a string representative of the identity of the piece.

        :return: A string representative of the identity of the piece.
        :rtype: str
        """
        return "%s %s at %s" % (self.player.color, self.name, self.location)

    def __location_as_index(self):
        """
        Converts the location (in conventional format) of the piece into index format.

        :return: The location (in conventional format) of the piece in index format.
        :rtype: tuple
        """
        return Utility.conventional_position_to_index(self.location)

    def __get_other_player(self):
        """
        Returns the player that the piece DOESN'T belong to.

        :return: The player that the piece doesn't belong to.
        :rtype: Player
        """
        if self.player == self.game.player_white:
            return self.game.player_black
        else:
            return self.game.player_white

    def __en_passant_conditions_met(self, piece_index, to_index):
        """
        Returns whether certain en passant conditions have been met. The conditions checked
        include:
            a) Piece positioning
            b) Movement history
            c)

        :param piece_index: Index of the piece attempting a possible en passant.
        :param to_index: Index of the location the piece is attempting to go to.
        :return: A boolean indicating whether en passant is possible.
        :rtype: bool
        """
        return piece_index[1] == to_index[1] and abs(piece_index[0] - to_index[0]) == 1 and \
               self.game.move_history[-1].piece == self.game.piece_at_position(
            Utility.index_position_to_conventional(to_index)) and abs(
            self.game.move_history[-1].pre_loc_index[1] -
            self.game.move_history[-1].post_loc_index[1]) == 2

    def move(self, to, message):
        """
        :param to: Conventional location (ex: "A4") that the piece is moving to.
        :param message: Message that is requesting the piece be moved.
        :return: A boolean indicating whether the move is successful or not.
        :rtype: bool
        """
        user_conditional = self.game.current_player_turn.id == self.player.id == message.author.id
        Debug.log("%s==%s==%s: %s" % (self.game.current_player_turn, self.player.id, message.author.id,
                                      user_conditional))
        if user_conditional is True:
            player_index = Utility.conventional_position_to_index(self.location)
            to_index = Utility.conventional_position_to_index(to)
            move_valid = self.__move_valid(to)
            print("Move_valid: %s" % move_valid)
            if move_valid:
                cap_piece = self.game.board[to_index[1]][to_index[0]]
                if cap_piece != 0:
                    if "Pawn" in self.name:
                        if self.player.color == "White":
                            #   If piece above left or above right
                            if abs(to_index[0] - player_index[0]) == 1 and to_index[1] + 1 == player_index[1]:
                                Debug.log("%s captures %s" % (self.get_identity(), cap_piece.get_identity()))

                            #   En passant
                            elif self.__en_passant_conditions_met(player_index, to_index):
                                Debug.log("%s captures %s EN PASSANT" % (self.get_identity(), cap_piece.get_identity()))
                            else:
                                return False
                        elif self.player.color == "Black":
                            #   If piece below left or below right
                            if (to_index[0] - 1 == player_index[0] or to_index[0] + 1 == player_index[0]) and to_index[
                                1] - 1 == \
                                    player_index[1]:
                                Debug.log("%s captures %s" % (self.get_identity(), cap_piece.get_identity()),
                                          Debug.log_type.GAMEPLAY)
                            #   En passant
                            elif self.__en_passant_conditions_met(player_index, to_index):
                                Debug.log("%s captures %s EN PASSANT" % (self.get_identity(), cap_piece.get_identity()))
                            else:
                                return False

                    self.player.captures.append(cap_piece)

                player_position = Utility.index_position_to_conventional(player_index)
                to_position = Utility.index_position_to_conventional(to_index)
                self.game.move_history.append(
                    HistoricalMove(self, player_position, to_position))
                self.game.board[to_index[1]][to_index[0]] = self
                self.location = to
                self.game.board[player_index[1]][player_index[0]] = 0
                self.game.current_player_turn = self.__get_other_player()

                return True
            else:
                return False

        elif self.game.current_player_turn.id == message.author.id:
            return "WRONG TEAM"

        else:
            return "WRONG PLAYER"

    def __distance_to_point(self, point):
        vertical = abs(int(point[1]) - int(self.location[1]))
        horizontal = ord(point[0]) - ord(self.location[0])
        return horizontal, vertical

    def __move_valid_initial_conditionals(self, to):
        return (self.player.color == self.game.current_player_turn.color) and (
            not (self.game.piece_on_path(self.location, to) and not self.game.piece_on_path(to, to)))

    @staticmethod
    def __queen_movement_evaluation(distance_to_point):
        #   Ensure only vertical/horizontal/diagonal movement
        return (abs(Utility.divide_zero_error_ignore(distance_to_point[0], distance_to_point[1])) == 1 or abs(
            Utility.divide_zero_error_ignore(distance_to_point[1], distance_to_point[0])) == 1) or (
                       distance_to_point[0] == 0 or distance_to_point[1] == 0)

    @staticmethod
    def __king_movement_evaluation(distance_to_point):
        #   Ensure only single spaced vertical/horizontal/diagonal movement
        return (abs(distance_to_point[0]) <= 1 and abs(distance_to_point[1]) <= 1) and (
                (abs(Utility.divide_zero_error_ignore(distance_to_point[0], distance_to_point[1])) == 1 or abs(
                    Utility.divide_zero_error_ignore(distance_to_point[1], distance_to_point[0])) == 1) or (
                        distance_to_point[0] == 0 or distance_to_point[1] == 0))

    @staticmethod
    def __rook_movement_evaluation(distance_to_point):
        #   Ensure only vertical/horizontal movement
        return distance_to_point[0] == 0 or distance_to_point[1] == 0

    @staticmethod
    def __bishop_movement_evaluation(distance_to_point):
        #   Ensure only diagonal movement
        return abs(Utility.divide_zero_error_ignore(distance_to_point[0], distance_to_point[1])) == 1 or abs(
            Utility.divide_zero_error_ignore(distance_to_point[1], distance_to_point[0])) == 1

    @staticmethod
    def __knight_movement_evaluation(distance_to_point):
        #   Ensure knight pattern movement
        return (abs(distance_to_point[0]) == 1 and abs(distance_to_point[1]) == 2) or (
                abs(distance_to_point[0]) == 2 and abs(distance_to_point[1]) == 1)

    def __pawn_movement_evaluation(self, distance_to_point):
        location_as_index = self.__location_as_index()
        #   Pawn is being moved 1 space
        if distance_to_point[1] == 1:
            if self.player.color == "White":
                piece_in_front = self.game.piece_at_position(Utility.index_position_to_conventional(
                    (location_as_index[0], location_as_index[1] - 1)))
            else:
                piece_in_front = self.game.piece_at_position(Utility.index_position_to_conventional(
                    (location_as_index[0], location_as_index[1] + 1)))

            if piece_in_front is None or piece_in_front.player.color != self.player.color:
                return True

        #   Pawn is being moved 2 spaces
        elif distance_to_point[1] == 2:
            if self.player.color == "White":
                piece_in_front = self.game.piece_at_position(Utility.index_position_to_conventional(
                    (location_as_index[0], location_as_index[1] - 2)))
            else:
                piece_in_front = self.game.piece_at_position(Utility.index_position_to_conventional(
                    (location_as_index[0], location_as_index[1] + 2)))

            #   Piece is its relative second rank
            if ((self.player.color == "White" and location_as_index[1] == 6) or
                    (self.player.color == "Black" and location_as_index[1] == 1)):

                if piece_in_front is None or piece_in_front.player.color != self.player.color:
                    return True

        return False

    def __move_valid(self, to):
        #   Check if there is a piece in the way
        print("Piece color: %s || Player color: %s" % (self.player.color, self.game.current_player_turn.color))

        if self.__move_valid_initial_conditionals(to):
            distance_to_point = self.__distance_to_point(to)

            if "Pawn" in self.name:
                return self.__pawn_movement_evaluation(distance_to_point)

            elif "Rook" in self.name:
                return self.__rook_movement_evaluation(distance_to_point)

            elif "Bishop" in self.name:
                return self.__bishop_movement_evaluation(distance_to_point)

            elif "Knight" in self.name:
                return self.__knight_movement_evaluation(distance_to_point)

            elif "Queen" in self.name:
                return self.__queen_movement_evaluation(distance_to_point)

            elif "King" in self.name:
                return self.__king_movement_evaluation(distance_to_point)


class Player:
    def __init__(self, uid, color):
        #   Matches won will actually read from and save to a DB once I get things going
        self.matches_won = 0
        self.color = color
        self.id = uid
        self.captures = []


class ChessMatch:
    def __init__(self, gid, init_message):
        self.board = [[4, 2, 3, 5, 6, 3, 2, 4],
                      [1, 1, 1, 1, 1, 1, 1, 1],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [1, 1, 1, 1, 1, 1, 1, 1],
                      [4, 2, 3, 5, 6, 3, 2, 4]]
        self.player_white, self.player_black = (Player(init_message.mentions[0].id, "White"),
                                                Player(init_message.author.id, "Black"))
        self.turn_count = 0
        self.init_message = init_message
        self.id = gid
        self.move_history = []
        self.current_player_turn = self.player_white
        self.__init_board()
        self.image = Utility.get_graphical_board(self.board)

    def __init_board(self):
        for y in range(0, len(self.board)):
            for x in range(0, len(self.board[y])):
                if self.board[y][x] != 0:
                    position = Utility.index_position_to_conventional((x, y))
                    if y > 4:
                        self.board[y][x] = Piece(self, NUM_TO_WORD_DICT[self.board[y][x]], self.player_white,
                                                 position)
                    else:
                        self.board[y][x] = Piece(self, NUM_TO_WORD_DICT[self.board[y][x]], self.player_black,
                                                 position)
        Debug.log("Board initialized")

    def format_board_to_string(self, board_as_array):
        a = "```[\t%s vs %s\t]\n\n" % (self.player_white.id, self.player_black.id)
        for row in board_as_array:
            a += '\t%s\n' % str(row)
        a += '```'
        return a

    def get_board_as_array(self, btype=BoardDisplayType.NUMERICAL):
        format_board = [[0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0]]
        if btype == BoardDisplayType.NUMERICAL:
            for y in range(0, len(self.board)):
                for x in range(0, len(self.board[y])):
                    if not self.board[y][x] == 0:
                        format_board[y][x] = WORD_TO_NUM_DICT[self.board[y][x].name]
                    else:
                        format_board[y][x] = 0

        elif btype == BoardDisplayType.CHARACTERIAL:
            for y in range(0, len(self.board)):
                for x in range(0, len(self.board[y])):
                    if self.board[y][x] != 0:
                        if "Knight" in self.board[y][x].name:
                            format_board[y][x] = "N"
                        else:
                            format_board[y][x] = self.board[y][x].name[0]
                    else:
                        format_board[y][x] = ' '

        elif btype == BoardDisplayType.COLOR:
            for y in range(0, len(self.board)):
                for x in range(0, len(self.board[y])):
                    if self.board[y][x] != 0:
                        format_board[y][x] = self.board[y][x].player.color[0]
                    else:
                        format_board[y][x] = ' '

        return format_board

    #   Get piece at a certain position
    def piece_at_position(self, position):
        x, y = Utility.conventional_position_to_index(position)
        if self.board[y][x] != 0:
            return self.board[y][x]

        return None

    def piece_on_path(self, point_a, point_b):
        #   Should be totally functional...does not identify the piece on point_a
        if not Utility.check_position_input_valid(point_a):
            Debug.log("Method 'piece_on_path' given bad value for argument 'point_a'")
            # raise ValueError("Method 'piece_on_path' given bad value for argument 'point_a'")
        elif not Utility.check_position_input_valid(point_b):
            Debug.log("Method 'piece_on_path' given bad value for argument 'point_b'")
            # raise ValueError("Method 'piece_on_path' given bad value for argument 'point_b'")

        #   If given path is just the same space
        if point_a[0] == point_b[0] and point_a[1] == point_b[1]:
            return True
        #   If given path is in same column
        elif point_a[0] == point_b[0]:
            for x in range(int(point_a[1]) + 1, int(point_b[1])):
                if self.piece_at_position(point_a[0] + str(x)):
                    return True

        #   If given path is in same row
        elif point_a[1] == point_b[1]:
            for x in range(ord(point_a[0]) + 1, ord(point_b[0])):
                if self.piece_at_position((chr(x), point_a[1])):
                    return True

        #   For horizontal pathing, check if column/row ratio is 1
        elif (int(point_b[1]) - int(point_a[1])) / (ord(point_b[0]) - ord(point_a[0])) == 1:
            print("Horizontal")
            for x in range(int(point_a[1]) + 1, int(point_b[1])):
                if self.piece_at_position((chr(x + 97), x)):
                    return True

        return False


class __MessageDummy:
    class UserDummy:
        def __init__(self, uid):
            self.id = uid

    def __init__(self):
        self.mentions = [self.UserDummy(222)]
        self.author = self.UserDummy(15)


if __name__ == "__main__":
    # Chess()
    loop = asyncio.get_event_loop()
    loop.create_task(Debug.loop())
    init_message_dummy = __MessageDummy()
    match = ChessMatch(431531, init_message_dummy)
    pawn_w, pawn_b = match.piece_at_position("D2"), match.piece_at_position("D7")
    queen_w, queen_b = match.piece_at_position("D1"), match.piece_at_position("D8")

    print(queen_w.player.captures)
    print(queen_b.player.captures)
    pawn_w.move("D4", init_message_dummy)
    queen_w.move("D8", init_message_dummy)
    Utility.get_graphical_board(match.board).show()
    loop.run_forever()
