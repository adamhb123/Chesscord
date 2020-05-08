from PIL import Image
from random import randint

"""
Purpose: Contains (generally) static functions for general ease-of-use

Item definitions:
*Methods
    get_graphical_board - returns the graphical version of a board given that board as an array
    get_help - returns the help string
    check_position_input_valid - checks if the given position is actually within the constraints of the board
"""
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


def get_graphical_board(board, scale=1):
    board_im = Image.open(IM_DB['Board']).convert("RGBA")
    b_w, b_h = board_im.size
    offset_x, offset_y = 5, 5

    for y in range(0, len(board)):
        for x in range(0, len(board[y])):
            piece = board[y][x]

            if piece != 0:
                piece_im = Image.open(IM_DB["%s %s" % (piece.color.capitalize(),
                                                       piece.name.capitalize())]).convert("RGBA")
                piece_size = piece_im.size
                board_im.paste(piece_im, box=(offset_x + (x * piece_size[0]), offset_y + (y * piece_size[1])),
                               mask=piece_im)

    return board_im


def generate_id(games):
    found = False
    a = randint(0, 100000000)
    if len(games) != 0:
        for game in games:
            if game.id == a:
                return generate_id(games)
    return a


def get_help():
    helpstr = \
        '''```Chesscord is a CHESS bot for disCORD. Very unique name, I know.
        Commands:
            !display (mode): displays board given a mode, if no mode is given then it defaults to 'image'
            --- modes are as follows: 'numerical', 'lexical', 'characterial', 'locational', 'image'```'''

    return helpstr


def check_position_input_valid(position):
    #   TEST ONE: Is the argument one of two valid types?
    #   Given conventional notation
    if isinstance(position, str):
        #   TEST TWO: Is the argument value valid?
        #   A: Does the letter describe a valid column?
        #   B: Does the number describe a valid row?
        if not ('A' <= position[0] <= 'H') or not (1 <= int(position[1]) <= 8):
            raise ValueError("Position outside of the constraints of the board")
        else:
            return True
    else:
        raise TypeError("Position of invalid type")
