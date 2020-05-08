from enum import Enum
import Debug
import Config
import Utility
import asyncio

"""
Purpose: 
    The actual game of chess. Provides the internal game functionality of the Chesscord bot.

Item definitions:
    Too many...
"""

NUM_TO_WORD_DICT = {0: ' ', 1: 'Pawn', 2: 'Knight', 3: 'Bishop',
                    4: 'Rook', 5: 'Queen', 6: 'King'}
WORD_TO_NUM_DICT = {value: key for key, value in NUM_TO_WORD_DICT.items()}
NUM_TO_SYMBOL_DICT_BLACK = {0: ' ', 1: '♟', 2: '♞', 3: '♝',
                            4: '♜', 5: '♛', 6: '♚'}
NUM_TO_SYMBOL_DICT_WHITE = {0: ' ', 1: '♙', 2: '♘', 3: '♗',
                            4: '♖', 5: '♕', 6: '♔'}


class BoardType(Enum):
    NUMERICAL = 0
    LEXICAL = 1
    CHARACTERIAL = 2
    LOCATIONAL = 3


class Piece:
    def __init__(self, board, name, color, position):

        self.name = name
        self.board = board
        self.color = color

        #   Name refers to the piece type (Queen, Rook, etc)
        #   Color refers to the team the piece is on and is represented by "White" or "Black"
        #   Position is a tuple containing the position of the piece (x,y)
        #   Test position input:
        Utility.check_position_input_valid(position)
        self.location = (position[0], int(position[1]))
        # self.direction = -1

    def get_identity(self):
        return "%s %s at %s" % (self.color, self.name, self.get_formatted_location())

    def get_formatted_location(self):
        return self.location[0] + str(self.location[1])

    def move(self, to):
        if self.__move_valid(to): pass

    def __distance_to_point(self, point):
        vertical = abs(int(point[1]) - int(self.location[1]))
        horizontal = ord(point[0]) - ord(self.location[0])
        return horizontal, vertical

    def __move_valid(self, to):
        if "Pawn" in self.name:
            if self.__distance_to_point(to) == 1:
                pass

            elif self.__distance_to_point(to) == 2:
                pass

            else:
                return False


class Player:
    def __init__(self, name):
        #   Matches won will actually read from and save to a DB once I get things going
        self.matches_won = 0
        self.name = name


class ChessMatch:
    def __init__(self, id, player_white, player_black):
        self.board = [[4, 2, 3, 5, 6, 3, 2, 4],
                      [1, 1, 1, 1, 1, 1, 1, 1],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [1, 1, 1, 1, 1, 1, 1, 1],
                      [4, 2, 3, 5, 6, 3, 2, 4]]
        self.player_white, self.player_black = player_white, player_black
        self.turn_count = 0
        self.id = id
        self.current_player_turn = "White"
        self.__init_board()
        self.image = Utility.get_graphical_board(self.board)
    def __init_board(self):
        for y in range(0, len(self.board)):
            for x in range(0, len(self.board[y])):
                if self.board[y][x] != 0:
                    position = self.grid_position_to_conventional((x, y))
                    if y > 4:
                        self.board[y][x] = Piece(self.board, NUM_TO_WORD_DICT[self.board[y][x]], "White", position)
                    else:
                        self.board[y][x] = Piece(self.board, NUM_TO_WORD_DICT[self.board[y][x]], "Black", position)
        Debug.log("Board initialized")

    def start(self, player_white_id, player_black_id):
        self.player_white = Player(player_white_id)
        self.player_black = Player(player_black_id)
        Debug.log("Match started with players: White=%s\tBlack=%s" % (player_white_id, player_black_id))

    @staticmethod
    def conventional_position_to_grid(position):
        index_a = 8 - int(position[1])
        index_b = ord(position[0].upper()) - 65
        #   Return in (x,y) format
        return index_b, index_a

    @staticmethod
    def grid_position_to_conventional(position):
        index_a = chr(position[0] + 65)
        index_b = 8 - position[1]
        return str(index_a) + str(index_b)

    def format_board_to_string(self, board_as_array):
        a = "```[\t%s vs %s\t]\n\n" % (self.player_white.name, self.player_black.name)
        for row in board_as_array:
            a += '\t%s\n' % str(row)
        a += '```'
        return a

    def get_board_as_array(self, btype=BoardType.NUMERICAL):
        format_board = [[0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0]]
        if btype == BoardType.NUMERICAL:
            for y in range(0, len(self.board)):
                for x in range(0, len(self.board[y])):
                    if not self.board[y][x] == 0:
                        format_board[y][x] = WORD_TO_NUM_DICT[self.board[y][x].name]
                    else:
                        format_board[y][x] = 0
        elif btype == BoardType.LEXICAL:
            for y in range(0, len(self.board)):
                for x in range(0, len(self.board[y])):
                    if self.board[y][x] != 0:
                        format_board[y][x] = self.board[y][x].name
                    else:
                        format_board[y][x] = NUM_TO_WORD_DICT[0]

        elif btype == BoardType.CHARACTERIAL:
            for y in range(0, len(self.board)):
                for x in range(0, len(self.board[y])):
                    if self.board[y][x] != 0:
                        format_board[y][x] = self.board[y][x].name[0]
                    else:
                        format_board[y][x] = ' '

        elif btype == BoardType.LOCATIONAL:
            for y in range(0, len(self.board)):
                for x in range(0, len(self.board[y])):
                    if self.board[y][x] != 0:
                        format_board[y][x] = self.board[y][x].get_formatted_location()
                    else:
                        format_board[y][x] = '  '

        return format_board

    #   Get piece at a certain position
    def piece_at_position(self, position):
        x, y = self.conventional_position_to_grid(position)
        if self.board[y][x] != 0:
            return self.board[y][x]

        return None

    async def game_loop(self):
        while True:
            await asyncio.sleep(.01)

    def piece_on_path(self, point_a, point_b):
        print("ORD A:%s\nORD B%s" % (ord(point_a[0]), ord(point_b[0])))
        if not Utility.check_position_input_valid(point_a):
            Debug.log("Method 'piece_on_path' given bad value for argument 'point_a'")
            raise ValueError("Method 'piece_on_path' given bad value for argument 'point_a'")
        elif not Utility.check_position_input_valid(point_b):
            Debug.log("Method 'piece_on_path' given bad value for argument 'point_b'")
            raise ValueError("Method 'piece_on_path' given bad value for argument 'point_b'")

        #   If given path is just the same space
        if point_a[0] == point_b[0] and point_a[1] == point_b[1]:
            return True
        #   If given path is in same column
        elif point_a[0] == point_b[0]:
            for x in range(int(point_a[1]), int(point_b[1])):
                if self.piece_at_position((point_a[0], x)):
                    return True

        #   If given path is in same row
        elif point_a[1] == point_b[1]:
            for x in range(ord(point_a[0]), ord(point_b)):
                if self.piece_at_position((chr(x), point_a[1])):
                    return True

        return False


if __name__ == "__main__":
    # Chess()
    loop = asyncio.get_event_loop()
    loop.create_task(Debug.loop())
    chess = ChessMatch("Bingus#0421", "Dongus#4223")
    #print(chess.piece_on_path("B1", "D1"))
    Utility.get_graphical_board(chess.board).show()
    loop.run_forever()
