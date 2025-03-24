# pgn_parser.py
import chess
import chess.pgn
from typing import Optional

class PGNTreeNode:
    def __init__(self, board: chess.Board, move: Optional[chess.Move] = None):
        self.board = board.copy()         # Current board state (FEN)
        self.move = move                  # The move that led to this state (None for root)
        self.children = []                # Only one child per node (main line only)
        self.annotation = None            # Annotation text

    def add_child(self, child_node: 'PGNTreeNode'):
        self.children.append(child_node)

def parse_pgn_to_tree(pgn_file_path: str) -> PGNTreeNode:
    """
    Parse a PGN file and return a linear tree (only main line moves).
    """
    with open(pgn_file_path) as pgn_file:
        game = chess.pgn.read_game(pgn_file)
        if game is None:
            raise ValueError("No game found in PGN file.")
    
    board = game.board()
    root = PGNTreeNode(board=board)
    current_node = root
    
    # Only iterate through the main line moves
    for move in game.mainline_moves():
        board.push(move)
        child_node = PGNTreeNode(board=board.copy(), move=move)
        current_node.add_child(child_node)
        current_node = child_node  # Move along the main line
    
    return root

# For testing:
if __name__ == "__main__":
    tree = parse_pgn_to_tree("data/raw/sample.pgn")
    print("Mainline PGN tree parsed successfully.")
