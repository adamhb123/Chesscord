from pprint import pprint
from enum import Enum
class BoardType(Enum):
    NUMERICAL=0
    LEXICAL=1
    CHARACTERIAL=2

class Chess():
    def __init__(self):
        self.piece_to_word_dict = {0:'Empty',1:'Pawn',2:'Knight',3:'Bishop',
                           4:'Rook',5:'Queen',6:'King'}
        self.board = [[0,0,0,0,0,0,0,0],
                      [0,0,0,0,0,0,0,0],
                      [0,0,0,0,0,0,0,0],
                      [0,0,0,0,0,0,0,0],
                      [0,0,0,0,0,0,0,0],
                      [0,0,0,0,0,0,0,0],
                      [0,0,0,0,0,0,0,0],
                      [0,0,0,0,0,0,0,0]]
        
    def get_board(btype=BoardType.NUMERICAL):
        if btype == BoardType.NUMERICAL:
            

if __name__=="__main__":
