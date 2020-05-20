from PIL import Image
from random import randint
import Debug

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


def get_graphical_board(board, scale=1):
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


def check_move_input_valid(move_input):
    splt = move_input.split(':')
    if check_position_input_valid(splt[0]) and check_position_input_valid(splt[1]):
        return True
    else:
        return False


def conventional_position_to_index(position):
    index_a = 8 - int(position[1])
    index_b = ord(position[0].upper()) - 65
    #   Return in (x,y) format
    return index_b, index_a


def divide_zero_error_ignore(n, d):
    return n / d if d else 0


def index_position_to_conventional(position):
    index_a = chr(position[0] + 65)
    index_b = 8 - position[1]
    return str(index_a) + str(index_b)


def generate_game_id():
    a = randint(0, 100000000)
    if len(CURRENT_GAMES) != 0:
        if a in CURRENT_GAMES:
            return generate_game_id()
    CURRENT_GAMES.append(a)
    return a


def get_help():
    helpstr = \
        '''```Chesscord is a CHESS bot for disCORD. Very unique name, I know.
        Commands:
            !display (mode): displays board given a mode, if no mode is given then it defaults to 'image'
            --- modes are as follows: 'numerical', 'lexical', 'characterial', 'locational', 'image'```'''

    return helpstr


def check_position_input_valid(position):
    #   TEST ONE: Is the argument a string?
    #   Given conventional notation
    if isinstance(position, str):
        #   TEST TWO: Is the argument value valid?
        #   A: Does the letter describe a valid column?
        #   B: Does the number describe a valid row?

        if ('A' <= position[0] <= 'H') and (1 <= int(position[1]) <= 8):
            return True

    return False
