# pgn_parser.py
import chess
import chess.pgn
from typing import Optional

class PGNTreeNode:
    def __init__(self, board: chess.Board, move: Optional[chess.Move] = None, move_san: Optional[str] = None,
                 from_square: Optional[str] = None, to_square: Optional[str] = None, piece_type: Optional[str] = None,
                 prev_eval: Optional[float] = None):
        self.board = board.copy()        # Board state after the move.
        self.move = move                 # Move that led to this state.
        self.move_san = move_san         # SAN notation for the move.
        self.from_square = from_square   # Starting square (e.g., "e2").
        self.to_square = to_square       # Ending square (e.g., "e4").
        self.piece_type = piece_type     # Piece type (e.g., "P", "N", "B", etc.).
        self.children = []               # For main line, a single-element list.
        self.annotation: Optional[str] = None  # Annotation text.
        self.headers = {}                # To store original PGN headers (set on the root)
        self.player_color = None         # Will be set on the root (True for White, False for Black)
        self.prev_eval = prev_eval       # Evaluation before this move was played
        self.current_eval: Optional[float] = None  # Current evaluation of the position

    def add_child(self, child_node: 'PGNTreeNode'):
        self.children.append(child_node)

def parse_pgn_to_tree(pgn_file_path: str) -> PGNTreeNode:
    """
    Parse a PGN file and return a linear tree (only the main line).
    Stores each move's SAN, starting/ending squares, piece type, and preserves the original PGN headers.
    Also stores the player's color (from the starting position) on the root.
    """
    with open(pgn_file_path) as pgn_file:
        game = chess.pgn.read_game(pgn_file)
        if game is None:
            raise ValueError("No game found in PGN file.")
    
    board = game.board()
    root = PGNTreeNode(board=board)
    root.headers = game.headers.copy()  # Preserve headers.
    # Store player's color from starting position.
    root.player_color = board.turn
    current_node = root
    prev_eval = 0.0  # Starting position is equal

    for move in game.mainline_moves():
        move_san = board.san(move)
        from_sq = chess.square_name(move.from_square)
        to_sq = chess.square_name(move.to_square)
        piece = board.piece_at(move.from_square)
        piece_str = piece.symbol() if piece is not None else "Unknown"
        if piece_str.lower() == "b":
            piece_str = "B"  # Force bishop uppercase.
        board.push(move)
        child_node = PGNTreeNode(
            board=board.copy(),
            move=move,
            move_san=move_san,
            from_square=from_sq,
            to_square=to_sq,
            piece_type=piece_str,
            prev_eval=prev_eval
        )
        current_node.add_child(child_node)
        current_node = child_node
        # In a real implementation, prev_eval would come from the PGN file
        # For now, we'll just use 0.0 as a placeholder
        prev_eval = 0.0
    
    return root

# For testing:
if __name__ == "__main__":
    tree = parse_pgn_to_tree("data/raw/mini.pgn")
    print("Player color (True=White, False=Black):", tree.player_color)
    current = tree
    while current.children:
        current = current.children[0]
        print(f"Move: {current.move_san}, from {current.from_square} to {current.to_square}, piece: {current.piece_type}")
