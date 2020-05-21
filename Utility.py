from PIL import Image
from random import randint
import Debug
from typing import Union

CURRENT_GAMES = []
IM_DB = {'Board': "./rsc/board.png",
         'White Bishop': "./rsc/pieces/white/white_bishop.png",
         'White King': "./rsc/pieces/white/white_king.png",
         'White Knight': "./rsc/pieces/white/white_knight.png",
         'White Pawn': "./rsc/pieces/white/white_pawn.png",
         'White Queen': "./rsc/pieces/white/white_queen.png",
         'White Rook': "./rsc/pieces/white/white_rook.png",
         'Black Bishop': "./rsc/pieces/black/black_bishop.png",
         'Black King': "./rsc/pieces/black/black_king.png",
         'Black Knight': "./rsc/pieces/black/black_knight.png",
         'Black Pawn': "./rsc/pieces/black/black_pawn.png",
         'Black Queen': "./rsc/pieces/black/black_queen.png",
         'Black Rook': "./rsc/pieces/black/black_rook.png",
         }


def get_graphical_board(board) -> Image.Image:
    """
    Returns an image representation of the given chess board.

    :param board: Board to represent (which is an array filled with Piece objects).
    :return: A PIL Image object of the board in its current state.
    :rtype: Image.Image
    """
    board_im = Image.open(IM_DB['Board']).convert("RGBA")
    b_w, b_h = board_im.size
    offset_x, offset_y = 25, 5

    for y in range(0, len(board)):
        for x in range(0, len(board[y])):
            piece = board[y][x]

            if piece != 0:
                piece_im = Image.open(IM_DB["%s %s" % (piece.player.color.capitalize(),
                                                       piece.name.capitalize())]).convert("RGBA")
                piece_size = piece_im.size
                board_im.paste(piece_im, box=(offset_x + (x * piece_size[0]), offset_y + (y * piece_size[1])),
                               mask=piece_im)

    return board_im


def check_position_input_valid(position_input) -> bool:
    """
    Checks whether or not the given positional input (ex: "A1") is a valid position or not.

    :param position_input: Given position, ex:"A1".
    :return: A boolean indicating whether or not the positional input is valid.
    :rtype: bool
    """
    return isinstance(position_input, str) and ('A' <= position_input[0] <= 'H') and (1 <= int(position_input[1]) <= 8)


def check_move_input_valid(move_input) -> bool:
    """
    Checks validity of move input. All this does is make sure that both parts of the input are properly

    :param move_input: Move input to check.
    :return: A boolean indicating whether or not the move input is valid
    :rtype: bool
    """
    try:
        splt = move_input.split(':')
        return check_position_input_valid(splt[0]) and check_position_input_valid(splt[1])
    except AttributeError as ae:
        Debug.log(ae)
        return False


def index_position_to_conventional(position) -> str:
    """
    Converts a given index position to its conventional equivalent, ex: (0,7) -> "A1"

    :param position: Position to convert, given in index format, ex (0,7)
    :return: The positional equivalent of the given indexical (if that is a word) position, in "A1" formatting
    :rtype: str
    """
    index_a = chr(position[0] + 65)
    index_b = 8 - position[1]
    return str(index_a) + str(index_b)


def conventional_position_to_index(position) -> tuple:
    """
    Converts a given conventional position to its index equivalent, ex: "A1" -> (0,7).

    :param position: Position to convert, given in conventional format, ex: "A1".
    :return: The indexical (if that is a word) equivalent of the given conventional position, in (x,y) formatting.
    """
    index_a = 8 - int(position[1])
    index_b = ord(position[0].upper()) - 65
    #   Return in (x,y) format
    return index_b, index_a


def divide_zero_error_ignore(n, d) -> float:
    """
    Used for division operations where division by zero errors must be ignored.

    :param n: The numerator.
    :param d: The divisor.
    :return: The result of the division, 0.0 is returned if division by zero occurs.
    :rtype: float
    """
    return n / d if d else 0.0


def generate_game_id() -> int:
    """
    Generates a unique game id intended for a Chess.ChessMatch instance

    :return: Returns the generated unique game id.
    :rtype: int
    """
    a = randint(0, 100000000)
    if len(CURRENT_GAMES) != 0:
        if a in CURRENT_GAMES:
            return generate_game_id()
    CURRENT_GAMES.append(a)
    return a


def get_help() -> str:
    """
    Returns the defined help string. This is solely for organizational purposes.

    :return: The help string.
    :rtype: str
    """
    helpstr = \
        '''```Chesscord is a CHESS bot for disCORD. Very unique name, I know.
        Commands:
            TOO MANY```'''

    return helpstr
