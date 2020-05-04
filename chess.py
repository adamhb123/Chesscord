from pprint import pprint
from enum import Enum
from threading import Thread
import Tests
import Config
import asyncio
import Debug

'''
What's working:
    - 

What isn't:

'''

class BoardType(Enum):
    NUMERICAL = 0
    LEXICAL = 1
    CHARACTERIAL = 2
    STANDARD_IDENTIFIERS = 3
    OBJECTS = 4
    UNICODE_SYMBOLS = 5


class Color(Enum):
    WHITE = 0
    BLACK = 1


class Piece():
    def __init__(self, name, color, position):
        #   Name refers to the piece type (Queen, Rook, etc)
        #   Color refers to the team the piece is on and is represented by Color.WHITE or Color.BLACK
        #   Position is a tuple containing the position of the piece (x,y)
        self.name = name
        self.color = color
        self.position = position
        self.direction = -1
        if self.color == Color.BLACK:
            self.direction = 1


class Chess():
    #   Can set event_loop to init some of the Asyncio stuff
    def __init__(self, event_loop=None):
        self.num_to_word_dict = {0: 'Empty', 1: 'Pawn', 2: 'Knight', 3: 'Bishop',
                                 4: 'Rook', 5: 'Queen', 6: 'King'}

        self.num_to_symbol_dict_black = {0: ' ', 1: '♟', 2: '♞', 3: '♝',
                                         4: '♜', 5: '♛', 6: '♚'}
        self.num_to_symbol_dict_white = {0: ' ', 1: '♙', 2: '♘', 3: '♗',
                                         4: '♖', 5: '♕', 6: '♔'}

        self.board = [[4, 2, 3, 5, 6, 3, 2, 4],
                      [1, 1, 1, 1, 1, 1, 1, 1],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [1, 1, 1, 1, 1, 1, 1, 1],
                      [4, 2, 3, 5, 6, 3, 2, 4]]
        self.turn_count = 0
        self.current_player_turn = "White"
        self.__init_board()

    def __init_board(self):
        for y in range(0,len(self.board)):
            for x in range(0,len(self.board[y])):
                if self.board[y][x] is not 0:
                    if y > 4:
                        self.board[y][x] = Piece(self.num_to_word_dict[self.board[y][x]], "White", (x, y))
                    else:
                        self.board[y][x] = Piece(self.num_to_word_dict[self.board[y][x]], "Black", (x, y))

    async def get_board(self, btype=BoardType.NUMERICAL):
        if btype == BoardType.NUMERICAL:
            return self.board

        else:
            format_board = []
            if btype == BoardType.LEXICAL:
                for y in range(0, len(self.board)):
                    for x in range(0, len(self.board[y])):
                        format_board[y][x] = self.num_to_word_dict[self.board[y][x]]
                        await asyncio.sleep(0.01)

            elif btype == BoardType.CHARACTERIAL:
                for y in range(0, len(self.board)):
                    for x in range(0, len(self.board[y])):
                        format_board[y][x] = self.board[y][x][0]
                        await asyncio.sleep(0.01)
            elif btype == BoardType.STANDARD_IDENTIFIERS:
                for y in range(0, len(self.board)):
                    for x in range(0, len(self.board[y])):
                        if self.board[y][x] is not 0:
                            format_board[y][x] = chr(65 + x) + str(8 - y)

                        await asyncio.sleep(0.01)

            elif btype == BoardType.OBJECTS:
                for y in range(0, len(self.board)):
                    for x in range(0,len(self.board[y])):
                        if self.board[y][x] is not 0:
                            format_board[y][x] = self.board[y][x]

            elif btype == BoardType.UNICODE_SYMBOLS:
                for y in range(0, len(self.board)):
                    for x in range(0, self.board[y]):
                        piece = self.board[y][x]
                        if piece != 0:
                            if piece.color == Color.WHITE:
                                format_board[y][x] = self.num_to_symbol_dict_white[piece]
                            elif piece.color == Color.BLACK:
                                format_board[y][x] = self.num_to_symbol_dict_black[piece]
                        else:
                            format_board[y][x] = ' '

                    await asyncio.sleep(0.01)

            return format_board

    #   Get piece at a certain position 
    def piece_at_pos(self, pos):
        return self.board[pos[1]][pos[0]]

    def move(self, _from, to):
        piece = self.piece_at_pos(_from)
        if piece.name == "Pawn":
            #   Check if move is possible





    def game_loop():
        while True:
            asyncio.sleep(.01)


if __name__ == "__main__":
    # Chess()
    loop = asyncio.get_event_loop()
    chess = Chess()
