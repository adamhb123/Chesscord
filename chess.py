from enum import Enum
import Debug
import discord
import Utility
import asyncio
import Database
from typing import NewType, Union

#   Define all necessary dictionaries

NUM_TO_WORD_DICT = {0: ' ', 1: 'Pawn', 2: 'Knight', 3: 'Bishop',
                    4: 'Rook', 5: 'Queen', 6: 'King'}
WORD_TO_NUM_DICT = {value: key for key, value in NUM_TO_WORD_DICT.items()}


class BoardDisplayType(Enum):
    """
    Enum for the various board display types.
    """
    NUMERICAL = 0
    LEXICAL = 1
    CHARACTERIAL = 2
    LOCATIONAL = 3
    COLOR = 4

class HistoricalMove:
    def __init__(self, piece: 'Piece', pre_loc: str, post_loc: str):
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

class Player:
    def __init__(self, uid: int, color: str):
        """
        Holds all necessary player information

        :param uid: The user's unique identifier.
        :param color: The player's color (either "White" or "Black")
        """
        self.matches_won = 0
        self.color = color
        self.id = uid
        # self.wins, self.losses, self.stalemates = Database.get_player_stats(self)
        self.captures = []


class ChessMatch:
    def __init__(self, gid: int, init_message: discord.Message):
        """
        Represents a singular game of chess.

        :param gid: The game's given unique id, generated by the utility method "generate_game_id".
        :param init_message: The message used to confirm and initialize the game.
        """
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
        self._init_board()
        self.image = Utility.get_graphical_board(self.board)

    def _init_board(self) -> None:
        """
        Initializes the board, preparing it for gameplay.

        :return: Nothing.
        """
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

    def format_board_to_string(self, board_as_array: list) -> str:
        """
        Formats the game board (given as an array) into string formatting.
        Useful for the various display modes (excluding image display).

        :param board_as_array:
        :return: The game board formatted as a string.
        :rtype: str
        """
        a = "```[\t%s vs %s\t]\n\n" % (self.player_white.id, self.player_black.id)
        for row in board_as_array:
            a += '\t%s\n' % str(row)
        a += '```'
        return a

    def get_board_as_array(self, btype: BoardDisplayType = BoardDisplayType.NUMERICAL) -> list:
        """
        Retrieves the board as an array, the representation of pieces on the board varies as a result of the given
        display mode.

        :param btype: The given BoardDisplayType, determines how the pieces are represented in the array.
        :return: The board as an array, formatted in the given BoardDisplayType.
        """
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
    def piece_at_position(self, position: str) -> Union['Piece', None]:
        """
        Gets a piece at a certain position.

        :param position: The position at which the piece is (supposedly) located.
        :return: Either
        """
        x, y = Utility.conventional_position_to_index(position)
        if type(self.board[y][x]) is Piece:
            return self.board[y][x]

        return None

    def piece_on_path(self, point_a: str, point_b: str, return_list=False) -> Union[bool,tuple]:
        """


        :param point_a:
        :param point_b:
        :param return_list:
        :return:
        """
        result = False
        piece_list = []
        point_a_index = Utility.conventional_position_to_index(point_a)
        point_b_index = Utility.conventional_position_to_index(point_b)
        #   Should be totally functional...does not identify the piece on point_a
        if not Utility.check_position_input_valid(point_a):
            Debug.log("Method 'piece_on_path' given bad value for argument 'point_a'")
            # raise ValueError("Method 'piece_on_path' given bad value for argument 'point_a'")
        elif not Utility.check_position_input_valid(point_b):
            Debug.log("Method 'piece_on_path' given bad value for argument 'point_b'")
            # raise ValueError("Method 'piece_on_path' given bad value for argument 'point_b'")

        #   If given path is just the same space
        if point_a[0] == point_b[0] and point_a[1] == point_b[1]:
            result = True
            if return_list: piece_list.append(self.piece_at_position(point_a))


        #   If given path is in same column
        elif point_a_index[0] == point_b_index[0]:
            cursor_y = point_a_index[1]
            if point_a_index[1] > point_b_index[1]:

                cursor_y -= 1

        #   If given path is in same row
        elif point_a_index[1] == point_b_index[1]:
            cursor_x, cursor_y = point_a_index[0], point_a_index[1]
            if point_a_index[0] > point_b_index[0]:
                while cursor_x > point_b_index[0]:
                    piece = self.piece_at_position(Utility.index_position_to_conventional((cursor_x, cursor_y)))
                    if piece is not None:
                        result = True
                        if return_list: piece_list.append(piece)
                    cursor_x -= 1
            elif point_a_index[0] < point_b_index[0]:
                while cursor_x < point_b_index[0]:
                    piece = self.piece_at_position(Utility.index_position_to_conventional((cursor_x, cursor_y)))
                    if piece is not None:
                        result = True
                        if return_list: piece_list.append(piece)
                    cursor_x += 1

        #   For diagonal pathing, check if column/row ratio is 1

        elif abs(Utility.divide_zero_error_ignore((point_b_index[1]-point_a_index[1]),
                                                  point_b_index[0]-point_a_index[0])) == 1:
            Debug.log("diagonal")
            cursor_x, cursor_y = point_a_index[0], point_a_index[1]

            #   point_b is up and left of point_a
            if point_a_index[0] > point_b_index[0] and point_a_index[1] > point_b_index[1]:
                while cursor_x > point_b_index[0]:
                    piece = self.piece_at_position(Utility.index_position_to_conventional((cursor_x, cursor_y)))
                    if piece is not None:
                        result = True
                        if return_list: piece_list.append(piece)
                    cursor_x -= 1
                    cursor_y -= 1
            #   point_b is down and left of point_a
            elif point_a_index[0] > point_b_index[0] and point_a_index[1] < point_b_index[1]:
                while cursor_x > point_b_index[0]:
                    piece = self.piece_at_position(Utility.index_position_to_conventional((cursor_x, cursor_y)))
                    if piece is not None:
                        result = True
                        if return_list: piece_list.append(piece)
                    cursor_x -= 1
                    cursor_y += 1
            #   point_b is up and right of point_a
            elif point_a_index[0] < point_b_index[0] and point_a_index[1] > point_b_index[1]:
                while cursor_x < point_b_index[0]:
                    piece = self.piece_at_position(Utility.index_position_to_conventional((cursor_x, cursor_y)))
                    if piece is not None:
                        result = True
                        if return_list: piece_list.append(piece)
                    cursor_x += 1
                    cursor_y -= 1
            #   point_b is down and right of point_a
            elif point_a_index[0] < point_b_index[0] and point_a_index[1] < point_b_index[1]:
                while cursor_x < point_b_index[0]:
                    piece = self.piece_at_position(Utility.index_position_to_conventional((cursor_x, cursor_y)))
                    if piece is not None:
                        result = True
                        if return_list: piece_list.append(piece)
                    cursor_x += 1
                    cursor_y += 1

        if return_list:
            return result, piece_list

        return result


class Piece:
    def __init__(self, game: ChessMatch, name: str, player: Player, location: str):
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

    def get_identity(self) -> str:
        """
        Returns a string representative of the identity of the piece.

        :return: A string representative of the identity of the piece.
        :rtype: str
        """
        return "%s %s at %s" % (self.player.color, self.name, self.location)

    def location_as_index(self) -> tuple:
        """
        Converts the location (in conventional format) of the piece into index format.

        :return: The location (in conventional format) of the piece in index format.
        :rtype: tuple
        """
        return Utility.conventional_position_to_index(self.location)

    def _get_other_player(self) -> Player:
        """
        Returns the player that the piece DOESN'T belong to.

        :return: The player that the piece doesn't belong to.
        """
        if self.player == self.game.player_white:
            return self.game.player_black

        return self.game.player_white

    def _en_passant_conditions_met(self, player_index: tuple, to_index: tuple) -> Union['Piece', bool]:
        """
        Checks whether certain en passant conditions have been met. The conditions checked
        include:
            a) Enemy piece positioning
            b) Movement history

        :param piece_index: Index of the piece attempting a possible en passant.
        :param to_index: Index of the location the piece is attempting to go to.
        :return: The piece that will be en passanted, if it exists. Otherwise, None.
        :rtype: Union['Piece', None]
        """
        Debug.log("Testing en_passant")

        if self.player.color == "White":
            supposed_enemy_piece = self.game.piece_at_position(
                Utility.index_position_to_conventional((to_index[0], to_index[1]+1)))
        elif self.player.color == "Black":
            supposed_enemy_piece = self.game.piece_at_position(
                Utility.index_position_to_conventional((to_index[0], to_index[1]-1)))

        Debug.log(supposed_enemy_piece)

        enemy_piece_check = supposed_enemy_piece is not None and supposed_enemy_piece.player.color != self.player.color

        move_history_check = self.game.move_history[-1].piece == supposed_enemy_piece and abs(
            self.game.move_history[-1].index_pre_loc[1] -
            self.game.move_history[-1].index_post_loc[1]) == 2

        Debug.log("En passant checks:\n enemy_piece_check of %s %s: %s\nmove_history_check: %s" %
                  (supposed_enemy_piece.player.color, supposed_enemy_piece.name, enemy_piece_check,move_history_check))

        if move_history_check and enemy_piece_check:
            Debug.log("En_passant tests passed")
            Debug.log(supposed_enemy_piece, l_type=Debug.LogType.WARNING)
            if "Pawn" in supposed_enemy_piece.name:
                return supposed_enemy_piece
            return False
        return False

    def _pawn_capture_conditions(self, player_index: tuple, to_index: tuple) -> bool:
        """
        Checks if the pawn can capture a piece at position to_index.

        :param player_index: Player's positioning in index format.
        :param to_index:  Desired move location in index format.
        :return: A boolean describing whether or not the pawn can capture a piece at given position to_index.
        :rtype: bool
        """
        if self.game.piece_at_position(Utility.index_position_to_conventional(to_index)) is None:
            return False

        if self.player.color == "White":
            return abs(to_index[0] - player_index[0]) == 1 and to_index[1] + 1 == player_index[1]
        elif self.player.color == "Black":
            return (to_index[0] - 1 == player_index[0] or to_index[0] + 1 == player_index[0]) and \
                   to_index[1] - 1 == player_index[1]

    def _perform_move_operations(self, player_index: tuple, to_index: tuple) -> bool:
        """
        Performs the various necessary move operations. Very descriptive, I know.

        :param player_index: The position of the player in index format.
        :param to_index: The position that the player is moving to in index format.
        """
        to = Utility.index_position_to_conventional(to_index)
        player_position = Utility.index_position_to_conventional(player_index)
        to_position = Utility.index_position_to_conventional(to_index)
        self.game.move_history.append(
            HistoricalMove(self, player_position, to_position))
        self.game.board[to_index[1]][to_index[0]] = self
        self.location = to
        self.game.board[player_index[1]][player_index[0]] = 0
        self.game.current_player_turn = self._get_other_player()
        return True

    def _pawn_capture(self, player_index: tuple, to_index: tuple, cap_piece: 'Piece') -> Union[bool, None]:
        """
        Highest level pawn capturing method, activates all necessary pawn capturing operations.
        To answer a question you probably have: "Why does this need to_index AND cap_piece? Why not just get the
        piece_at_position of to_index?"

        It is necessary to have both to_index and cap_piece b/c of en passant (since the position of the captured
        piece is not equal to the position the player's pawn is moving to).

        This is activated AFTER other move check operations, so if this method is being ran, then the move itself
        is guaranteed to be legitimate UNLESS en passant is involved.

        :param player_index: Index of player's pawn that is being moved.
        :param to_index: Index of the position the pawn is moving to.
        :param cap_piece: Piece being captured by the player.
        :return: Either a boolean or None depending on the given conditions. None is returned when the move is valid,
        but does not involve the capture of any piece. False is returned when the requested move is supposed to be
        en passant, but the conditions aren't right for en passant to take place.
        """
        #   If piece below left or below right
        if self._pawn_capture_conditions(player_index, to_index):
            Debug.log("%s captures %s" % (self.get_identity(), cap_piece.get_identity()),
                      Debug.LogType.GAMEPLAY)
            self.player.captures.append(cap_piece)
            self._perform_move_operations(player_index, to_index)
            return True
        elif self._en_passant_conditions_met(player_index,to_index):
            self.player.captures.append(cap_piece)
            cpi = cap_piece.location_as_index()
            self.game.board[cpi[1]][cpi[0]] = 0
            self._perform_move_operations(player_index, to_index)
            return True
        return False

    def _path_is_straight_to_piece(self, point_a: str, to_piece: 'Piece') -> bool:
        """
        Checks whether or not the path from point_a to point_b goes straight to a piece with no pieces in between.
        Essentially this means that there is a piece at point_b, but no pieces on the path from point_a to point_b
        except said piece at point_b. This only works for actual direct routes, diagonals DO NOT WORK. Use
        _path_is_directly_diagonal_to_piece for that.

        :param point_a: Starting path point.
        :param to_piece: Piece that we are pathing to.
        :return: A tuple (A,B) containing A: whether or not the path leads straight to the piece
        """
        result, pieces = self.game.piece_on_path(point_a,to_piece.location,return_list=True)
        if len(pieces) == 1 and pieces[0] == to_piece:
            return True
        else:
            return False

    def _path_is_directly_diagonal_to_piece(self, point_a: str, to_piece: 'Piece') -> bool:
        """
        Checks whether or not the path from point_a to point_b goes straight to a piece diagonally with no pieces in between.
        Essentially this means that there is a piece at point_b, but no pieces on the path from point_a to point_b
        except said piece at point_b. Main use case for this is checking check.

        :param point_a: Starting path point.
        :param to_piece: Piece that we are pathing to.
        :return: A tuple (A,B) containing A: whether or not the path leads straight diagonally to the piece.
        """
        point_index = Utility.conventional_position_to_index(point_a)

        #   Go to bottom right diagonal
        cursor_x, cursor_y = point_index[0], point_index[1]
        while cursor_x < 7 and cursor_y < 7:
            piece_chk = self.game.piece_at_position(Utility.index_position_to_conventional((cursor_x,cursor_y)))
            if type(piece_chk) is Piece:
                if to_piece == piece_chk:
                    return True
                else:
                    break
            cursor_x += 1
            cursor_y += 1

        #   Go to bottom left diagonal
        cursor_x, cursor_y = point_index[0], point_index[1]
        while cursor_x > 0 and cursor_y < 7:
            piece_chk = self.game.piece_at_position(Utility.index_position_to_conventional((cursor_x, cursor_y)))
            if type(piece_chk) is Piece:
                if to_piece == piece_chk:
                    return True
                else:
                    break
            cursor_x -= 1
            cursor_y += 1

        #   Go to top right diagonal
        cursor_x, cursor_y = point_index[0], point_index[1]
        while cursor_x < 7 and cursor_y > 0:
            piece_chk = self.game.piece_at_position(Utility.index_position_to_conventional((cursor_x, cursor_y)))
            if type(piece_chk) is Piece:
                if to_piece == piece_chk:
                    return True
                else:
                    break
            cursor_x += 1
            cursor_y -= 1
        #   Go to top left diagonal
        cursor_x, cursor_y = point_index[0], point_index[1]
        while cursor_x > 0 and cursor_y > 0:
            piece_chk = self.game.piece_at_position(Utility.index_position_to_conventional((cursor_x, cursor_y)))
            if type(piece_chk) is Piece:
                if to_piece == piece_chk:
                    return True
                else:
                    break
            cursor_x -= 1
            cursor_y -= 1
        return False


    #def _check_stalemate(self):
        #self.game.board

    def _check_check(self, player_color: str, opposing_king_position: str):
        """
        Checks whether or not a player is in check.

        :param opposing_king_position: The opposing king's position in conventional formatting (string).
        :param player: The player who may be checking (the checker). Don't know how else to work it.
        :return: A boolean revealing whether or not the opposing player is in check.
        """
        if "King" not in self.game.piece_at_position(opposing_king_position).name:
            return False

        opposing_king_position_index = Utility.conventional_position_to_index(opposing_king_position)

        dbg = None

        #   SNAG ALL PIECES
        player_pieces = []
        for row in self.game.board:
            for piece in row:
                if type(piece) is Piece:
                    if player_color == piece.player.color:
                        player_pieces.append(piece)
        #   END SNAGGING

        for piece in player_pieces:
            if "Pawn" in piece.name:
                #   In hindsight I could have used the same function I used for the bishop here
                if player_color == "White":
                    top_left = self.game.piece_at_position(
                        Utility.index_position_to_conventional((opposing_king_position_index[0]-1,
                                                                opposing_king_position_index[1]-1)))
                    top_right = self.game.piece_at_position(
                        Utility.index_position_to_conventional((opposing_king_position_index[0]+1,
                                                                opposing_king_position_index[1]-1)))
                    if type(top_left) is Piece and "King" in top_left.name and top_left.player.color != player_color:
                        Debug.log("CHKCHK TRUE: %s pieceatpos %s" % (piece.name, top_left.name))
                        return True

                    elif type(top_right) is Piece and "King" in top_right.name and \
                            top_right.player.color != player_color:
                        Debug.log("CHKCHK TRUE: %s pieceatpos %s" % (piece.name, top_right.name))
                        return True

                elif player_color == "Black":
                    bottom_left = Utility.index_position_to_conventional((opposing_king_position_index[0]-1,
                                                                          opposing_king_position_index[1]+1))
                    bottom_right = Utility.index_position_to_conventional((opposing_king_position_index[0] + 1,
                                                                          opposing_king_position_index[1] + 1))
                    if self.game.piece_at_position(bottom_left) is not None or \
                            self.game.piece_at_position(bottom_right) is not None:
                        Debug.log("CHKCHK TRUE: %s" % piece.name)
                        return True

            elif "Rook" in piece.name:
                if self._path_is_straight_to_piece(opposing_king_position,piece):
                    Debug.log("CHKCHK TRUE: %s" % piece.name)
                    return True

            elif "Knight" in piece.name:
                piece_index = piece.location_as_index()
                distance_to_point = (opposing_king_position_index[0]-piece_index[0],
                                     opposing_king_position_index[1]-piece_index[1])
                #   We can use the knight movement evaluation here to check this whole deal because
                #   There is no chance of another piece being in the way due to the way lil' horsie moves
                if self._knight_movement_evaluation(distance_to_point):
                    Debug.log("CHKCHK TRUE: %s" % piece.name)
                    return True

            elif "Bishop" in piece.name:
                if self._path_is_directly_diagonal_to_piece(opposing_king_position, piece):
                    Debug.log("CHKCHK TRUE: %s" % piece.name)
                    return True

            elif "Queen" in piece.name:
                queen_chk_cond = self._path_is_directly_diagonal_to_piece(opposing_king_position, piece) or \
                self._path_is_straight_to_piece(opposing_king_position, piece)
                Debug.log("Queen chk cond: %s" % queen_chk_cond)

                if queen_chk_cond:
                    Debug.log("CHKCHK TRUE: %s" % piece.name)
                    return True

            elif "King" in piece.name:
                piece_index = piece.location_as_index()
                distance_to_point = (abs(opposing_king_position_index[0] - piece_index[0]),
                                     abs(opposing_king_position_index[1] - piece_index[1]))
                if distance_to_point[0] < 2 and distance_to_point[1] < 2:
                    Debug.log("CHKCHK TRUE: %s" % piece.name)
                    return True

            return False

    #def _check_checkmate(self):


    def move(self, to: str, message: discord.Message) -> Union[str, bool]:
        """
        :param to: Conventional location (ex: "A4") that the piece is moving to.
        :param message: Message that is requesting the piece be moved.
        :return: A boolean indicating whether the move is successful or not.
        :rtype: bool
        """
        result = None
        user_conditional = self.game.current_player_turn.id == self.player.id == message.author.id
        Debug.log("%s==%s==%s: %s" % (self.game.current_player_turn.id, self.player.id, message.author.id,
                                      user_conditional))
        #   user_conditional tests whether or not the user who activated the move command is actually meant to move.
        if user_conditional is True:
            player_index = Utility.conventional_position_to_index(self.location)
            to_index = Utility.conventional_position_to_index(to)
            move_valid = self._move_valid(to)
            print("Move_valid: %s" % move_valid)
            if move_valid:
                cap_piece = self.game.board[to_index[1]][to_index[0]]
                #   Runs if there is a piece at to_index and the piece does not belong to the player
                if cap_piece != 0 and cap_piece.player is not self.player:
                    print("CAP PIECE PLAYER: %s VS PLAYER: %s" % (cap_piece.player.color, self.player.color))
                    if "Pawn" in self.name:
                        result = self._pawn_capture(player_index, to_index, cap_piece)

                    result = self._perform_move_operations(player_index, to_index)

                #   Runs if there is no capturable piece at to_index and the piece belongs to the player
                elif cap_piece != 0 and cap_piece.player is self.player:
                    result = "OWN PIECE"

                #   Runs when there is no capturing (unless en passant happens) involved, but just basic movement
                else:
                    #   Special basic movement principals for pawns
                    if "Pawn" in self.name:
                        #   Only vertical movement is allowed for normal pawn movement that doesn't involve capturing
                        if player_index[0] - to_index[0] == 0:
                            result = self._perform_move_operations(player_index, to_index)

                        else:
                            possible_en_passant_piece = self._en_passant_conditions_met(player_index, to_index)
                            if type(possible_en_passant_piece) is Piece:
                                Debug.log("En passant (aka huge pain in the ass move that noone uses but I have to add "
                                          "anyways) activated!")
                                result = self._pawn_capture(player_index, to_index, possible_en_passant_piece)

                    #   Normal movement for all other pieces
                    else:
                        result = self._perform_move_operations(player_index, to_index)
            else:
                result = False

        elif self.game.current_player_turn.id == message.author.id:
            result = "WRONG TEAM"

        else:
            result = "WRONG PLAYER"

        #   Was the action successful?
        if result is not None and type(result) != str:
            #   The action was successful, check stalemate/checkmate/check conditions
            #   Grab opponent's king
            for row in self.game.board:
                for piece in row:
                    if type(piece) is Piece:
                        if "King" in piece.name and piece.player != self.player:
                            king = piece
            chkchk = self._check_check(self.player.color, king.location)
            Debug.log("CHKHK: %s" % chkchk)



        return result

    def _distance_to_point(self, point: str) -> tuple:
        """
        Get's the horizontal and vertical distance from this piece to a given point.

        :param point: The point to get the distance to, in conventional (ex: "A1") formatting.
        :return: A tuple that contains the horizontal and vertical distance from this piece to the given point.
        :rtype: tuple
        """
        vertical = abs(int(point[1]) - int(self.location[1]))
        horizontal = ord(point[0]) - ord(self.location[0])
        return horizontal, vertical

    def _move_valid_initial_conditionals(self, to: str) -> bool:
        """
        Verifies that a move to the given location 'to' is possible for this piece.
        Performs the following checks:
            a) It is the player's turn.
            b) There is no piece on the movement path (unless the piece is a Knight).

        :param to: Location to which the piece wants to move.
        :return: A boolean indicating whether or not the move is valid.
        """
        return self.player.color == self.game.current_player_turn.color and \
               ((not self.game.piece_on_path(self.location, to)) or "Knight" in self.name)

    @staticmethod
    def _queen_movement_evaluation(distance_to_point: tuple) -> bool:
        """
        Verifies that a move matches the queen piece's movement patterns.

        :param distance_to_point: Distance to the desired move location as a tuple: (horizontal, vertical).
        :return: A boolean indicating whether or not the move is valid.
        """
        #   Ensure only vertical/horizontal/diagonal movement
        return (abs(Utility.divide_zero_error_ignore(distance_to_point[0], distance_to_point[1])) == 1 or abs(
            Utility.divide_zero_error_ignore(distance_to_point[1], distance_to_point[0])) == 1) or (
                       distance_to_point[0] == 0 or distance_to_point[1] == 0)

    @staticmethod
    def _king_movement_evaluation(distance_to_point: tuple) -> bool:
        """
        Verifies that a move matches the king piece's movement patterns.

        :param distance_to_point: Distance to the desired move location as a tuple: (horizontal, vertical).
        :return: A boolean indicating whether or not the move is valid.
        """
        #   Ensure only single spaced vertical/horizontal/diagonal movement
        return (abs(distance_to_point[0]) <= 1 and abs(distance_to_point[1]) <= 1) and (
                (abs(Utility.divide_zero_error_ignore(distance_to_point[0], distance_to_point[1])) == 1 or abs(
                    Utility.divide_zero_error_ignore(distance_to_point[1], distance_to_point[0])) == 1) or (
                        distance_to_point[0] == 0 or distance_to_point[1] == 0))

    @staticmethod
    def _rook_movement_evaluation(distance_to_point: tuple) -> bool:
        """
        Verifies that a move matches the rook piece's movement patterns.

        :param distance_to_point: Distance to the desired move location as a tuple: (horizontal, vertical).
        :return: A boolean indicating whether or not the move is valid.
        """
        #   Ensure only vertical/horizontal movement
        return distance_to_point[0] == 0 or distance_to_point[1] == 0

    @staticmethod
    def _bishop_movement_evaluation(distance_to_point: tuple) -> bool:
        """
        Verifies that a move matches the bishop piece's movement patterns.

        :param distance_to_point: Distance to the desired move location as a tuple: (horizontal, vertical).
        :return: A boolean indicating whether or not the move is valid.
        """
        #   Ensure only diagonal movement
        return abs(Utility.divide_zero_error_ignore(distance_to_point[0], distance_to_point[1])) == 1 or abs(
            Utility.divide_zero_error_ignore(distance_to_point[1], distance_to_point[0])) == 1

    @staticmethod
    def _knight_movement_evaluation(distance_to_point: tuple) -> bool:
        """
        Verifies that a move matches the knight piece's movement patterns.

        :param distance_to_point: Distance to the desired move location as a tuple: (horizontal, vertical).
        :return: A boolean indicating whether or not the move is valid.
        """
        #   Ensure knight pattern movement
        return (abs(distance_to_point[0]) == 1 and abs(distance_to_point[1]) == 2) or (
                abs(distance_to_point[0]) == 2 and abs(distance_to_point[1]) == 1)

    def _pawn_movement_evaluation(self, distance_to_point: tuple) -> bool:
        """
        Verifies that a move matches the pawn piece's movement patterns.

        :param distance_to_point: Distance to the desired move location as a tuple: (horizontal, vertical).
        :return: A boolean indicating whether or not the move is valid.
        """
        location_as_index = self.location_as_index()

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

    def _move_valid(self, to: str) -> bool:
        """
        Checks whether a certain move is valid given the position it is moving to. Accounts for movement patterns

        :param to: Proposed location to move to.
        :return: A boolean that describes whether or not the given move is valid.
        """
        if self._move_valid_initial_conditionals(to):
            distance_to_point = self._distance_to_point(to)
            if "Pawn" in self.name:
                return self._pawn_movement_evaluation(distance_to_point)

            elif "Rook" in self.name:
                return self._rook_movement_evaluation(distance_to_point)

            elif "Bishop" in self.name:
                return self._bishop_movement_evaluation(distance_to_point)

            elif "Knight" in self.name:
                return self._knight_movement_evaluation(distance_to_point)

            elif "Queen" in self.name:
                return self._queen_movement_evaluation(distance_to_point)

            elif "King" in self.name:
                return self._king_movement_evaluation(distance_to_point)





class _MessageDummy:
    """
    A little Message dummy for testing without running the bot itself.
    I don't even think it works.
    """

    class UserDummy:
        def __init__(self, uid):
            self.id = uid

    def __init__(self):
        self.mentions = [self.UserDummy(222)]
        self.author = self.UserDummy(15)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(Debug.loop())
    player = Player(251261532095119361, "White")
    Database.queue_instruction(player.id, Database.InstructionType.ADD_PLAYER)
    loop.create_task(Database.update_loop())
    loop.run_forever()
