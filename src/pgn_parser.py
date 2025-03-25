# pgn_parser.py
import chess
import chess.pgn
from typing import Optional

class PGNTreeNode:
    def __init__(self, board: chess.Board, move: Optional[chess.Move] = None, move_san: Optional[str] = None):
        self.board = board.copy()        # Board state after the move.
        self.move = move                 # Move that led to this state.
        self.move_san = move_san         # SAN notation of the move (from parent's board).
        self.children = []               # For main line, this is a single-element list.
        self.annotation: Optional[str] = None  # Annotation text.

    def add_child(self, child_node: 'PGNTreeNode'):
        self.children.append(child_node)

def parse_pgn_to_tree(pgn_file_path: str) -> PGNTreeNode:
    """
    Parse a PGN file and return a linear tree (only the main line).
    Stores the SAN for each move at parse time.
    """
    with open(pgn_file_path) as pgn_file:
        game = chess.pgn.read_game(pgn_file)
        if game is None:
            raise ValueError("No game found in PGN file.")
    
    board = game.board()
    root = PGNTreeNode(board=board)
    current_node = root
    for move in game.mainline_moves():
        move_san = board.san(move)
        board.push(move)
        child_node = PGNTreeNode(board=board.copy(), move=move, move_san=move_san)
        current_node.add_child(child_node)
        current_node = child_node
    return root

# For testing:
if __name__ == "__main__":
    tree = parse_pgn_to_tree("data/raw/sample.pgn")
    print("Mainline PGN tree parsed successfully.")
    current = tree
    while current.children:
        current = current.children[0]
        print(current.move_san)
