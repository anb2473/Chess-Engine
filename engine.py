class Counter:
    def __init__(self):
        self.index = 0

    def incr(self):
        self.index += 1
        return self.index


class Piece:
    def __init__(self, piece_type, loc, board, value):
        self.piece_type = piece_type
        self.loc = loc
        self.board = board
        self.value = value
        self.is_black = loc[1] > 4

    # overrided by child class
    def enumerate_moves(self):
        pass

    def enumerate_raycast(self, offset):
        points = []
        pos = list(self.loc)
        open = True
        while open:
            pos[0] += offset[0]
            pos[1] += offset[1]
            if not self.board.is_valid_coord(pos):
                break
            if not self.board.is_empty(pos):
                open = False
                if self.board.is_black(pos) == self.is_black:
                    points.append(tuple(pos))
                break
            points.append(tuple(pos))
        return points

    def scan_by_offset_list(self, cx, cy):
        candidates = []
        for x, y in zip(cx, cy):
            new_pos = (self.loc[0] + x, self.loc[1] + y)
            if self.board.is_valid_coord(new_pos) and (self.board.is_empty(new_pos) or self.board.is_black(new_pos) != self.is_black):
                candidates.append(new_pos)
        return candidates


class Pawn(Piece):
    def __init__(self, loc=(0, 0), board=None):
        super().__init__("pawn", loc, board, 1)

    def enumerate_moves(self):
        candidates = []
        for loc in [(self.loc[0] - 1, self.loc[1] + 1), (self.loc[0] + 1, self.loc[1] + 1)]:
            if self.board.is_valid_coord(loc) and self.board.is_black(loc) != self.is_black:
                candidates.append(loc)
        
        if self.board.is_valid_coord((self.loc[0], self.loc[1] + 1)) and self.board.is_empty((self.loc[0], self.loc[1] + 1)):
            candidates.append((self.loc[0], self.loc[1] + 1))

        return candidates


class Rook(Piece):
    def __init__(self, loc=(0, 0), board=None):
        super().__init__("rook", loc, board, 6)

    def enumerate_moves(self):
        candidates = []
        candidates.extend(self.enumerate_raycast((0, 1)))
        candidates.extend(self.enumerate_raycast((1, 0)))
        candidates.extend(self.enumerate_raycast((0, -1)))
        candidates.extend(self.enumerate_raycast((-1, 0)))
        return candidates


class Bishop(Piece):
    def __init__(self, loc=(0, 0), board=None):
        super().__init__("bishop", loc, board, 3.75)

    def enumerate_moves(self):
        candidates = []
        candidates.extend(self.enumerate_raycast((1, 1)))
        candidates.extend(self.enumerate_raycast((1, -1)))
        candidates.extend(self.enumerate_raycast((-1, 1)))
        candidates.extend(self.enumerate_raycast((-1, -1)))
        return candidates


class King(Piece):
    def __init__(self, loc=(0, 0), board=None):
        super().__init__("king", loc, board, 1000000000)

    def enumerate_moves(self):
        candidates = self.scan_by_offset_list([-1, 0, 1, 1, 1, 0, -1, -1], [1, 1, 1, 0, -1, -1, -1, 0])
        return candidates


class Queen(Piece):
    def __init__(self, loc=(0, 0), board=None):
        super().__init__("queen", loc, board, 9)

    def enumerate_moves(self):
        candidates = []
        candidates.extend(self.enumerate_raycast((1, 1)))
        candidates.extend(self.enumerate_raycast((1, -1)))
        candidates.extend(self.enumerate_raycast((-1, 1)))
        candidates.extend(self.enumerate_raycast((-1, -1)))
        candidates.extend(self.enumerate_raycast((0, 1)))
        candidates.extend(self.enumerate_raycast((1, 0)))
        candidates.extend(self.enumerate_raycast((0, -1)))
        candidates.extend(self.enumerate_raycast((-1, 0)))
        return candidates


class Knight(Piece):
    def __init__(self, loc=(0, 0), board=None):
        super().__init__("knight", loc, board, 3)

    def enumerate_moves(self):
        candidates = self.scan_by_offset_list([1, 2, 2, 1, -1, -2, -2, -1], [2, 1, -1, -2, -2, -1, 1, 2])
        return candidates


class Controller:
    # board is ref to Board object
    def __init__(self, is_black=False, board=None):
        self.board = board
        self.is_black = is_black
        self.move_id = None
        self.move_location = None

    # Move formatted as
    def execute_move(self):
        if self.move_id is None:
            raise ValueError("Cannot move none type piece")
        if self.move_location is None:
            raise ValueError("Cannot move piece to none type location")
        self.board.move_piece(self.move_id, self.move_location, self.is_black)

    # child class overrides this
    def generate_move(self):
        pass

    def move(self, board):
        self.board = board
        self.generate_move()
        self.execute_move()


class Human(Controller):
    def render_board(self):
        white_emoji_map = {"pawn": "♟", "rook": "♜", "knight": "♞", "bishop": "♝", "queen": "♛", "king": "♚"}
        black_emoji_map = {"pawn": "♙", "rook": "♖", "knight": "♘", "bishop": "♗", "queen": "♕", "king": "♔"}
        row_num = 8
        for row in self.board.pos_board:
            print(row_num, end=" ")
            for piece_id in row:
                if piece_id is None:
                    print("    ", end=" ")
                else:
                    piece = self.board.id_board[0].get(piece_id)
                    if piece is None:
                        piece = self.board.id_board[1].get(piece_id)
                    if piece.is_black:
                        print(black_emoji_map.get(piece.piece_type) + " " + str(piece_id).zfill(2), end=" ")
                    else:
                        print(white_emoji_map.get(piece.piece_type) + " " + str(piece_id).zfill(2), end=" ")
            print()
            row_num -= 1
        print("   a    b    c    d    e    f    g    h")
 
    def generate_move(self):
        self.render_board()
        user_input = input(f"{"♔  Black" if self.is_black else "♚ White"}: ")
        self.move_id = int(user_input[0]) * 10 + int(user_input[1])
        x = ord(user_input[2].lower()) - ord('a') + 1 # x is a letter
        y = int(user_input[3]) - 1
        self.move_location = (x, y)


class Engine(Controller):
    def __init__(self, is_black=False, board=None):
        super().__init__(is_black, board)
        self.last_moves = []

    def index_moves(self, is_black):
        pieces = self.board.id_board[int(is_black)]
        candidates = self.list_candidates(pieces)
        return pieces, candidates

    def list_candidates(self, pieces):
        candidates = {}
        for piece in pieces.values():
            if not isinstance(piece, Piece):
                raise ValueError("Cannot evaluate non piece object as piece")
            for candidate in piece.enumerate_moves():
                candidates[(piece, candidate)] = True
        return candidates

    def count_occurances(self, obj, map):
        occurances = 0
        for item in map:
            if item == obj:
                occurances += 1
        return occurances

    def evaluate_move(self, pieces, piece, move_location):
        """
        Criteria:
        - is the piece safe (can it be taken with an unfair trade)
        - does it lose material (are there any pieces that can be taken if that move is played)
        - values of all controlled squares once the move is played (including opened sightlines from other pieces)
        - castling (castling should weigh higher than other moves which don't save material)
        - don't move pieces twice (that would incentivize shuffling around the bishop as that maximizes controlled squares)
        - can it be threatened on the next move (is there a possible move that can directly attack the piece)
        """
        score = 0.0
        enemy_pieces, enemy_moves = self.index_moves(not self.is_black)

        # is it safe (must be multiplied by 4 because the value of the back rank is 24, so if it is less
        #       you are incentivized to put a rook on the backrank even if it is in danger)
        if move_location in enemy_moves and self.count_occurances(move_location, pieces) > 1:
            score -= piece.value * 4

        # how often has it been moved
        harm = 5
        for move in self.last_moves:
            if move[0] == piece:
                score -= harm
                harm *= 2

        # how many squares does it control
        board_value = [[3, 3, 3, 3, 3, 3, 3, 3],
                       [1, 1, 1.65, 1.75, 1.75, 1.65, 1, 1],
                       [0.5, 0.5, 1.25, 1.5, 1.5, 1.25, 0.5, 0.5],
                       [0, 0, 1.75, 2, 2, 1.75, 0, 0],
                       [0, 0, 1.8, 2, 2, 1.8, 0, 0],
                       [0, 0, 0.8, 1, 1, 0.8, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0]]
        for piece in self.board.id_board[int(self.is_black)].values():
            board_value[piece.loc[1]][piece.loc[0]] = piece.value
        
        new_pieces = pieces.copy()
        new_piece = next((v for k, v in pieces.items() if v == piece), None)
        new_piece.loc = move_location
        new_candidates = self.list_candidates(new_pieces)
        control_value = 0.0
        controlled_defense_weight = 0.75
        controlled_offense_weight = 0.55
        for candidate in new_candidates:
            candidate_loc = candidate[1]
            control_value += board_value[candidate_loc[1]][candidate_loc[0]]
            control_value += 0.5
            controlled_id = self.board.pos_board[candidate_loc[1]][candidate_loc[0]]
            if controlled_id is not None:
                controlled_piece = self.board.id_board[int(self.is_black)][controlled_id]
                control_value += controlled_piece.value + controlled_defense_weight if controlled_piece.is_black == self.is_black else controlled_offense_weight

        return score

    def generate_move(self):
        pieces, candidates = self.index_moves(self.is_black)

        # This will be set when a move is selected
        if len(self.last_moves) > 3:
            self.last_moves = self.last_moves[-3:]

        best_score = float('-inf')
        best_candidate = None
        for candidate in candidates:
            score = self.evaluate_move(pieces, candidate[0], candidate[1])
            if score > best_score:
                best_score = score
                best_candidate = candidate
        self.move_id = next((k for k, v in pieces.items() if v == best_candidate[0]), None)
        self.move_location = best_candidate[1]


class Board:
    def __init__(self):
        self.count = Counter()
        self.id_board, self.pos_board = self.generate_board(([Rook((0, 0), self), Knight((1, 0), self), Bishop((2, 0), self), Queen((3, 0), self), King((4, 0), self), Bishop((5, 0), self), Knight((6, 0), self), Rook((7, 0), self), Pawn((0, 1), self), Pawn((1, 1), self), Pawn((2, 1), self), Pawn((3, 1), self), Pawn((4, 1), self), Pawn((5, 1), self), Pawn((6, 1), self), Pawn((7, 1), self)],
[Rook((0, 7), self), Knight((1, 7), self), Bishop((2, 7), self), Queen((3, 7), self), King((4, 7), self), Bishop((5, 7), self), Knight((6, 7), self), Rook((7, 7), self), Pawn((0, 6), self), Pawn((1, 6), self), Pawn((2, 6), self), Pawn((3, 6), self), Pawn((4, 6), self), Pawn((5, 6), self), Pawn((6, 6), self), Pawn((7, 6), self)]))
        # white controller is index 0, black controller is index 1
        self.controllers = [None, None]
        self.running = True

    def hash_side(self, side):
        side_dict = {}
        for item in side:
            side_dict[self.count.incr()] = item
        return side_dict

    def pos_side(self, side, pos_board):
        for piece_id, piece in side.items():
            pos_board[piece.loc[1]][piece.loc[0]] = piece_id

    # generate hashmap with id's for each piece, and a positional 2d array of the board
    def generate_board(self, board):
        white = self.hash_side(board[0])
        black = self.hash_side(board[1])
        pos_board = [[None for _ in range(8)] for _ in range(8)]
        self.pos_side(white, pos_board)
        self.pos_side(black, pos_board)
        return (white, black), pos_board
    
    def attach_controller(self, controller):
        if not isinstance(controller, Controller):
            raise ValueError("Cannot attach non controller object as controller")
        if self.controllers[int(controller.is_black)] is not None:
            raise ValueError("Cannot override controller")
        self.controllers[int(controller.is_black)] = controller

    def move_piece(self, id, loc, is_black):
        piece = self.id_board[int(is_black)][id]
        if not piece:
            raise ValueError("Piece with id does not exist")
        self.pos_board[loc[1]][loc[0]] = id
        self.pos_board[piece.loc[1]][piece.loc[0]] = None
        piece.loc = loc

    def is_empty(self, loc):
        return self.pos_board[loc[1]][loc[0]] is None
    
    def is_black(self, loc):
        piece_id = self.pos_board[loc[1]][loc[0]]
        if piece_id is None:
            return None
        # Check both white and black pieces
        for pieces in self.id_board:
            if piece_id in pieces:
                return pieces[piece_id].is_black
        return None

    def is_valid_coord(self, loc):
        return 0 <= loc[0] < 8 and 0 <= loc[1] < 8

    def run(self):
        if self.controllers[0] is None or self.controllers[1] is None:
            raise ValueError("Both controllers must be attached before running the game")
        
        is_black = False
        while self.running:
            self.controllers[int(is_black)].move(self)
            is_black = not is_black


if __name__ == "__main__":
    board = Board()
    white = Human(is_black=False, board=board)
    black = Engine(is_black=True, board=board)
    board.attach_controller(white)
    board.attach_controller(black)
    board.run()